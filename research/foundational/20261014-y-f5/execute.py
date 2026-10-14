"""Y-F5: test learned competitive/normalized message passing after F4 false positives.

All arms use new development-only cohorts, equal optimizer steps and the same
576-byte native memory. The prior F4 study is NOT rerun on its old validation.
"""
from __future__ import annotations
import importlib.util,json,time
from pathlib import Path
import torch
from torch import nn
HERE=Path(__file__).resolve().parent
p=HERE.parent/"20261014-y-f4"/"execute.py"
spec=importlib.util.spec_from_file_location("y_f4_arch",p)
assert spec and spec.loader
f4=importlib.util.module_from_spec(spec);spec.loader.exec_module(f4)
f2=f4.f2
f1=f2.f1
torch.set_num_threads(1)
TRAIN=range(44900,44924)
VALID=range(45200,45212)

class CompetitiveComposer(f4.RecurrentComposer):
 def __init__(self):
  super().__init__()
  self.attention_temperature=nn.Parameter(torch.tensor(2.))
 def answer(self,state,questions):
  packed=state[:,:12].contiguous().view(torch.int32).long()
  src=(packed>>16)&65535
  dst=packed&65535
  links=torch.zeros((state.shape[0],12,12),dtype=torch.float32)
  links[:,f4.MASK]=state[:,12:]
  outputs=[]
  for q in range(2):
   source=questions[:,q,0,None]
   target=questions[:,q,1,None]
   active=self.similarity(source,src)
   terminal=self.similarity(dst,target)
   for step in range(3):
    attention=torch.softmax(self.attention_temperature*active,dim=-1)
    message=torch.bmm(attention.unsqueeze(1),links).squeeze(1)
    active=torch.sigmoid(self.message_gain*message+
                         self.recurrent_gain*active+self.activation_bias)
   outputs.append(torch.sigmoid(self.output_gain*(active*terminal).sum(-1)+
                                self.output_bias))
  return torch.stack(outputs,dim=1)

def train(model,cohort):
 optimizer=torch.optim.Adam(model.parameters(),lr=.055)
 start=time.perf_counter()
 for epoch in range(150):
  optimizer.zero_grad()
  scores=model.answer(model.make_state(cohort[0]),cohort[1]).clamp(.00001,.99999)
  loss=nn.functional.binary_cross_entropy(scores,cohort[2])
  loss.backward()
  torch.nn.utils.clip_grad_norm_(model.parameters(),10.)
  optimizer.step()
 return round((time.perf_counter()-start)*1000),float(loss.detach())

def predict(model,cohort):
 with torch.no_grad():
  return (model.answer(model.make_state(cohort[0]),cohort[1])>=.5)

def evaluate():
 torch.manual_seed(668)
 start=time.perf_counter()
 table=f2.f1b.hash_public_feature_dictionary()
 train_data=f2.cohort(TRAIN,(0,1,2),table)
 valid_data=f2.cohort(VALID,(4,5,6,7),table)
 assert train_data[0].shape==(288,12,2) and valid_data[0].shape==(192,12,2)
 control=f4.RecurrentComposer()
 candidate=CompetitiveComposer()
 initialized=predict(candidate,valid_data)
 # Matched train budget; no F4 original validation consumed.
 control_ms,control_loss=train(control,train_data)
 candidate_ms,candidate_loss=train(candidate,train_data)
 learned=predict(candidate,valid_data)
 matched_f4=predict(control,valid_data)
 exact=(f1.fixed_exact(valid_data[0],valid_data[1])>=.5)
 truth=valid_data[2].bool()
 predicted={
  "normalized_competitive_recurrence":learned,
  "same_arch_untrained":initialized,
  "matched_unnormalized_F4_retrained":matched_f4,
  "fixed_coded_exact_control":exact}
 scores={}
 for name,a in predicted.items():
  neg=~truth
  scores[name]={"correct":int((a==truth).sum()),
               "accuracy":float((a==truth).float().mean()),
               "false_positives":int((a&neg).sum()),
               "negative_false_positive_rate":float((a&neg).sum().item()/neg.sum().item())}
 rows=[]
 for i,(seed,family,ca,cb,alias_count) in enumerate(valid_data[3]):
  rows.append({"seed":seed,"family":family,"cut_a":ca,"cut_b":cb,
   "alias_count":alias_count,"truth":truth[i].tolist(),
   "predictions":{name:pred[i].tolist() for name,pred in predicted.items()}})
 assert len(rows)==192 and sum(not t for r in rows for t in r["truth"])==192
 trained=scores["normalized_competitive_recurrence"]
 init=scores["same_arch_untrained"]
 old=scores["matched_unnormalized_F4_retrained"]
 upper=scores["fixed_coded_exact_control"]
 positive=(trained["accuracy"]>=.85 and
           trained["negative_false_positive_rate"]<=.15 and
           trained["accuracy"]-init["accuracy"]>=.15 and
           trained["accuracy"]-old["accuracy"]>=.15 and
           upper["accuracy"]-trained["accuracy"]<=.15)
 return {"schema":"yggdrasil.foundation.f5.competitive-recurrence-development.v1",
  "stage":"DEVELOPMENT_ONLY","source_F4_sha":"55dfadce4ac75eb1be06797e7a688621ff0e7fdc",
  "train_bounds":[44900,44924],"valid_bounds":[45200,45212],
  "train_states":288,"validation_states":192,"questions":384,"negative_questions":192,
  "native_state_bytes":576,
  "normalized_model_parameters":sum(p.numel() for p in candidate.parameters()),
  "matched_unnormalized_parameters":sum(p.numel() for p in control.parameters()),
  "optimizer_steps_each":150,"candidate_train_ms":candidate_ms,
  "matched_control_train_ms":control_ms,
  "candidate_training_loss":candidate_loss,"control_training_loss":control_loss,
  "candidate_weights":{key:val.detach().tolist() for key,val in candidate.state_dict().items()},
  "scores":scores,"rows":rows,
  "verdict":"DEVELOPMENT_COMPETITIVE_COMPOSITION_GAIN" if positive else
    "DEVELOPMENT_NO_COMPETITIVE_COMPOSITION_GAIN",
  "candidate_direct_coded_equality":False,
  "candidate_fixed_or_traversal":False,
  "engineered_public_binary_features":True,
  "programmed_three_message_rounds":True,
  "sealed_first_use":False,"scientific_acceptance":False,
  "accepted_ref_mutation":False,"external_llm_calls":0,
  "total_development_wall_ms":round((time.perf_counter()-start)*1000)}
if __name__=="__main__":
 print(json.dumps(evaluate(),sort_keys=True,indent=2))
