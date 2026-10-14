"""Y-F2: task-learned transition matching over structured public ID bits.

Unlike F1/F1B, the transition probability has no coded equality indicator.
The binary ID representation, public query anchors, and four-hop traversal ARE
coded, so success is limited to learning this comparator, not general identity.
Development only; NO sealed first-use claim.
"""
from __future__ import annotations
import importlib.util,json,time
from pathlib import Path
import torch
from torch import nn

HERE=Path(__file__).resolve().parent
parent=HERE.parent/"20261014-y-f1b"/"execute.py"
spec=importlib.util.spec_from_file_location("yf1b_source",parent)
assert spec and spec.loader
f1b=importlib.util.module_from_spec(spec);spec.loader.exec_module(f1b)
f1=f1b.f1
torch.set_num_threads(1)
SHIFT=torch.arange(16,dtype=torch.int64)
TRAIN_SEEDS=range(41000,41024)
VALID_SEEDS=range(41200,41212)

class BitComparator(nn.Module):
 def __init__(self):
  super().__init__()
  self.raw_weight=nn.Parameter(torch.full((16,),-1.))
  self.bias=nn.Parameter(torch.tensor(0.))
 def make_state(self,facts):
  src=facts[:,:,0].long()
  dst=facts[:,:,1].long()
  sb=((src.unsqueeze(-1)>>SHIFT)&1).float()
  db=((dst.unsqueeze(-1)>>SHIFT)&1).float()
  mismatches=(db[:,:,None,:]-sb[:,None,:,:]).abs()
  # No direct equality, no oracle graph edges, no query labels inside state.
  logits=self.bias-torch.einsum("bijd,d->bij",mismatches,
                                      torch.nn.functional.softplus(self.raw_weight))
  p=torch.sigmoid(logits)
  p=p*(~torch.eye(12,dtype=torch.bool)).to(p)
  packed=((facts[:,:,0]<<16)|facts[:,:,1]).to(torch.int32).view(torch.float32)
  result=torch.cat((packed,p[:,f1.MASK]),dim=-1)
  assert result.shape[-1]==144 and result.element_size()==4
  return result

def cohort(seeds,families,table):
 facts,questions,labels,keys=[],[],[],[]
 for seed in seeds:
  for family in families:
   for ca in (False,True):
    for cb in (False,True):
     _,stress,qs,truth,aliases=f1b.probe(seed,family,ca,cb,1,table)
     facts.append(stress);questions.append(qs);labels.append(truth)
     keys.append((seed,family,ca,cb,len(aliases)))
 return (torch.tensor(facts,dtype=torch.int32),
         torch.tensor(questions,dtype=torch.int32),
         torch.tensor(labels,dtype=torch.float32),keys)

def infer(model,facts,questions):
 with torch.no_grad():
  return (f1.answer(model.make_state(facts),questions)>=.5)

def qualify():
 torch.manual_seed(612)
 started=time.perf_counter()
 table=f1b.hash_public_feature_dictionary()
 train=cohort(TRAIN_SEEDS,(0,1,2),table)
 valid=cohort(VALID_SEEDS,(4,5,6,7),table)
 assert train[0].shape==(288,12,2) and valid[0].shape==(192,12,2)
 model=BitComparator()
 before=infer(model,valid[0],valid[1])
 opt=torch.optim.Adam(model.parameters(),lr=.08)
 start_train=time.perf_counter()
 for epoch in range(120):
  opt.zero_grad()
  p=f1.answer(model.make_state(train[0]),train[1]).clamp(.00001,.99999)
  loss=torch.nn.functional.binary_cross_entropy(p,train[2])
  loss.backward()
  torch.nn.utils.clip_grad_norm_(model.parameters(),max_norm=10.)
  opt.step()
 train_ms=round((time.perf_counter()-start_train)*1000)
 learned=infer(model,valid[0],valid[1])
 exact=(f1.fixed_exact(valid[0],valid[1])>=.5)
 sim=f1.Gate("identity_similarity")
 with torch.no_grad():
  sim.weights.copy_(torch.tensor(f1b.FROZEN["identity_similarity"],dtype=torch.float32))
 frozen_similarity=infer(sim,valid[0],valid[1])
 labels=valid[2].bool()
 records=[]
 for idx,(seed,family,ca,cb,alias_count) in enumerate(valid[3]):
  records.append({"seed":seed,"family":family,"cut_a":ca,"cut_b":cb,
    "alias_count":alias_count,"truth":labels[idx].tolist(),
    "predictions":{"initialized_bit_comparator":before[idx].tolist(),
        "task_trained_bit_comparator":learned[idx].tolist(),
        "frozen_sinusoid_similarity":frozen_similarity[idx].tolist(),
        "fixed_coded_exact_control":exact[idx].tolist()}})
 score={}
 for name,pred in (("initialized_bit_comparator",before),
                   ("task_trained_bit_comparator",learned),
                   ("frozen_sinusoid_similarity",frozen_similarity),
                   ("fixed_coded_exact_control",exact)):
  accuracy=float((pred==labels).float().mean())
  neg=~labels
  fp=float((pred&neg).sum().item()/neg.sum().item())
  score[name]={"accuracy":accuracy,"false_positive_rate":fp,
      "correct":int((pred==labels).sum().item()),"false_positives":int((pred&neg).sum().item())}
 assertion=(score["task_trained_bit_comparator"]["accuracy"]>=.90 and
            score["task_trained_bit_comparator"]["false_positive_rate"]<=.10 and
            score["task_trained_bit_comparator"]["accuracy"]-score["initialized_bit_comparator"]["accuracy"]>=.15 and
            score["task_trained_bit_comparator"]["accuracy"]-score["frozen_sinusoid_similarity"]["accuracy"]>=.15)
 verdict=("DEVELOPMENT_TASK_LEARNED_BIT_COMPARATOR_OBSERVED" if assertion
          else "DEVELOPMENT_NO_NEW_BIT_COMPARATOR_GENERALIZATION")
 assert len(records)==192 and sum(not t for row in records for t in row["truth"])==192
 assert all(len(row["truth"])==2 for row in records)
 return {"schema":"yggdrasil.foundation.f2.learned-bit-transition-dev.v1",
   "stage":"DEVELOPMENT_ONLY","source_parent":"f65cb1c41a6fee7074d4ade89ecadd3b0e482da7",
   "train_seed_bounds":[41000,41024],"validation_seed_bounds":[41200,41212],
   "train_states":288,"validation_states":192,"validation_questions":384,
   "negative_questions":192,"native_state_bytes":576,
   "model_parameter_count":17,"model_parameter_bytes_fp32":68,
   "candidate_scores":score,"records":records,"registered_verdict":verdict,
   "train_steps":120,"trained_weights":[float(v) for v in model.raw_weight.detach()],
   "trained_bias":float(model.bias.detach()),"train_bce":float(loss.detach()),
   "training_wall_ms":train_ms,"total_wall_ms":round((time.perf_counter()-started)*1000),
   "no_direct_coded_transition_equality_in_learned_comparator":True,
   "public_binary_id_bits_programmed":True,"query_anchors_coded":True,
   "four_hop_traversal_coded":True,"learned_general_variable_identity":False,
   "first_use_sealed":False,"accepted_ref_mutation":False,"external_llm_calls":0}
if __name__=="__main__":
 print(json.dumps(qualify(),sort_keys=True,indent=2))
