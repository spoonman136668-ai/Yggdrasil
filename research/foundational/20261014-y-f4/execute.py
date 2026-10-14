"""Y-F4: task-learned recurrent relation composition, DEVELOPMENT ONLY.

A bounded 576-byte native state stores public endpoints and learned link scores.
The query is processed by a trainable recurrent message passing readout.
No explicit equality comparisons, fixed OR-path traversal or oracle joins occur
in the learned candidate's inference. Input bits and three message-passing rounds
are deliberately engineered and documented as remaining inductive biases.
"""
from __future__ import annotations
import importlib.util, json, time
from pathlib import Path
import torch
from torch import nn

HERE=Path(__file__).resolve().parent
f2path=HERE.parent/"20261014-y-f2"/"execute.py"
spec=importlib.util.spec_from_file_location("y_f2_dev",f2path)
assert spec and spec.loader
f2=importlib.util.module_from_spec(spec);spec.loader.exec_module(f2)
f1=f2.f1
torch.set_num_threads(1)
TRAIN=range(42200,42224)
VALID=range(42500,42512)
MASK=~torch.eye(12,dtype=torch.bool)
SHIFT=torch.arange(16,dtype=torch.int64)

def id_bits(ids):
 return ((ids.long().unsqueeze(-1)>>SHIFT)&1).float()

class RecurrentComposer(nn.Module):
 def __init__(self):
  super().__init__()
  self.raw_weights=nn.Parameter(torch.full((16,),-1.))
  self.identity_bias=nn.Parameter(torch.tensor(0.))
  self.message_gain=nn.Parameter(torch.tensor(1.5))
  self.recurrent_gain=nn.Parameter(torch.tensor(-1.5))
  self.activation_bias=nn.Parameter(torch.tensor(-1.0))
  self.output_gain=nn.Parameter(torch.tensor(3.))
  self.output_bias=nn.Parameter(torch.tensor(-3.))
 def similarity(self,a,b):
  mismatch=(id_bits(a)-id_bits(b)).abs()
  penalty=torch.einsum("...d,d->...",mismatch,
       torch.nn.functional.softplus(self.raw_weights))
  return torch.sigmoid(self.identity_bias-penalty)
 def make_state(self,facts):
  # No direct Boolean equality: all transition scores use trained parameters.
  a=facts[:,:,1,None]
  b=facts[:,None,:,0]
  matches=self.similarity(a,b)
  matches=matches*MASK.to(matches)
  packed=((facts[:,:,0]<<16)|facts[:,:,1]).to(torch.int32).view(torch.float32)
  out=torch.cat((packed,matches[:,MASK]),dim=-1)
  assert out.shape==(facts.shape[0],144)
  return out
 def answer(self,state,questions):
  packed=state[:,:12].contiguous().view(torch.int32).long()
  src=(packed>>16)&65535
  dst=packed&65535
  links=torch.zeros((state.shape[0],12,12),dtype=torch.float32)
  links[:,MASK]=state[:,12:]
  predictions=[]
  for q in range(2):
   start=questions[:,q,0,None]
   end=questions[:,q,1,None]
   active=self.similarity(start,src)
   terminal=self.similarity(dst,end)
   # Trainable three-round recurrent aggregation: no coded OR or equalities.
   for _ in range(3):
    message=torch.bmm(active.unsqueeze(1),links).squeeze(1)
    active=torch.sigmoid(self.message_gain*message+
                         self.recurrent_gain*active+self.activation_bias)
   output=torch.sigmoid(self.output_gain*(active*terminal).sum(-1)+
                        self.output_bias)
   predictions.append(output)
  return torch.stack(predictions,dim=1)

def evaluate():
 torch.manual_seed(642)
 begun=time.perf_counter()
 feature_table=f2.f1b.hash_public_feature_dictionary()
 train=f2.cohort(TRAIN,(0,1,2),feature_table)
 valid=f2.cohort(VALID,(4,5,6,7),feature_table)
 assert train[0].shape==(288,12,2) and valid[0].shape==(192,12,2)
 model=RecurrentComposer()
 with torch.no_grad():
  initial=(model.answer(model.make_state(valid[0]),valid[1])>=.5)
 opt=torch.optim.Adam(model.parameters(),lr=.055)
 t0=time.perf_counter()
 for epoch in range(150):
  opt.zero_grad()
  prob=model.answer(model.make_state(train[0]),train[1]).clamp(.00001,.99999)
  loss=nn.functional.binary_cross_entropy(prob,train[2])
  loss.backward()
  torch.nn.utils.clip_grad_norm_(model.parameters(),10.)
  opt.step()
 train_ms=round((time.perf_counter()-t0)*1000)
 with torch.no_grad():
  learned=(model.answer(model.make_state(valid[0]),valid[1])>=.5)
  frozen=f2.BitComparator()
  frozen.raw_weight.copy_(torch.tensor([1.2161805629730225,
      .8829572796821594,1.2392035722732544,2.430713415145874,
      3.4044041633605957,1.525221586227417,2.416123390472412,
      1.9606653451919556,2.2651169300079346,1.659049153327942,
      1.053269624710083,2.638160467147827,2.233046293258667,
      3.9128310680389404,-1.,-1.]))
  frozen.bias.copy_(torch.tensor(4.553725719451904))
  fixed_fourhop=(f1.answer(frozen.make_state(valid[0]),valid[1])>=.5)
  fixed_exact=(f1.fixed_exact(valid[0],valid[1])>=.5)
 labels=valid[2].bool()
 scores={}
 rows=[]
 preds={"learned_recurrent_composition":learned,
        "initialized_recurrent_composition":initial,
        "frozen_f2_coded_fourhop_control":fixed_fourhop,
        "fixed_exact_equality_oracle_control":fixed_exact}
 for name,answer in preds.items():
  negatives=~labels
  scores[name]={
   "accuracy":float((answer==labels).float().mean()),
   "false_positive_rate":float((answer&negatives).sum().item()/negatives.sum().item()),
   "correct":int((answer==labels).sum()),
   "false_positives":int((answer&negatives).sum())}
 for i,(seed,family,ca,cb,alias_count) in enumerate(valid[3]):
  rows.append({"seed":seed,"family":family,"cut_a":ca,"cut_b":cb,
   "alias_count":alias_count,"truth":labels[i].tolist(),
   "predictions":{k:v[i].tolist() for k,v in preds.items()}})
 assert len(rows)==192 and sum(not t for row in rows for t in row["truth"])==192
 p=scores["learned_recurrent_composition"]
 baseline=scores["initialized_recurrent_composition"]
 control=scores["frozen_f2_coded_fourhop_control"]
 passed=(p["accuracy"]>=.85 and p["false_positive_rate"]<=.15
     and p["accuracy"]-baseline["accuracy"]>=.15
     and control["accuracy"]-p["accuracy"]<=.15)
 return {"schema":"yggdrasil.foundation.f4.learned-composition-dev.v1",
   "stage":"DEVELOPMENT_ONLY","parent_f3_sha":"bf86d1405001cefba0ff70d99e407cd924cce249",
   "train_bounds":[42200,42224],"validation_bounds":[42500,42512],
   "train_states":288,"validation_states":192,
   "questions":384,"negative_questions":192,
   "resident_state_bytes":576,"candidate_parameter_count":sum(p.numel() for p in model.parameters()),
   "train_steps":150,"resource_training_ms":train_ms,
   "resource_total_ms":round((time.perf_counter()-begun)*1000),
   "scores":scores,"raw_rows":rows,
   "selected_weights":{"bit_weight":[float(z) for z in model.raw_weights.detach()],
    "identity_bias":float(model.identity_bias.detach()),
    "message_gain":float(model.message_gain.detach()),
    "recurrent_gain":float(model.recurrent_gain.detach()),
    "activation_bias":float(model.activation_bias.detach()),
    "output_gain":float(model.output_gain.detach()),
    "output_bias":float(model.output_bias.detach())},
   "verdict":"DEVELOPMENT_LEARNED_RECURRENCE_TRANSFER_OBSERVED" if passed else
     "DEVELOPMENT_NO_RECURRENT_COMPOSITION_TRANSFER",
   "coded_equality_in_candidate":False,"coded_or_traversal_in_candidate":False,
   "engineered_binary_input_features":True,
   "programmed_three_message_rounds":True,
   "query_used_only_during_readout":True,
   "sealed_first_use":False,"scientifically_accepted":False,
   "accepted_ref_mutation":False,"external_llm_calls":0}
if __name__=="__main__":
 print(json.dumps(evaluate(),sort_keys=True,indent=2))
