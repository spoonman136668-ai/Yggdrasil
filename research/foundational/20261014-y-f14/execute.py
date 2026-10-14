"""Y-F14: learn a risk-constrained NEGATIVE-stop policy using local evidence.

Previous Y-F13 halted valid positive paths while prefix prediction remained
negative. Here continuation is default. A new risk head may stop negatively
only if a training-calibrated risk cap is met, using current prefix statistics
and cheap current edge-role availability. Validation uses new family/seed
identities and unseen 7-8 hop chains. No F3 source or future-oracle inference.
Development only; saving is in recurrent steps, NOT validated runtime time.
"""
from __future__ import annotations
import importlib.util,json,time
from pathlib import Path
import torch
from torch import nn
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("y_f13_frozen",P.parent/"20261014-y-f13"/"execute.py")
assert spec and spec.loader
f13=importlib.util.module_from_spec(spec);spec.loader.exec_module(f13)
torch.set_num_threads(1)
torch.manual_seed(1435)
TRAIN_FAMS=(68,69,70,71)
VALID_FAMS=(72,73,74,75)
TRAIN_SEEDS=range(60100,60112)
VALID_SEEDS=range(60600,60612)

def records(cases,model):
 facts,roles,queries,seq,truth,keys=f13.all_states(cases)
 recs=[]
 for fact,role,query,request,y,key in zip(facts,roles,queries,seq,truth,keys):
  feats,preds=f13.trace_one(model,fact,role,query,request)
  # Static current graph metadata only. Per-prefix feature is max learned
  # compatibility of the NEXT requested role with any available edge.
  # This is O(12) role lookups, not multi-hop oracle or future recurrence.
  with torch.no_grad():
   stored=model.encode(torch.tensor([fact],dtype=torch.int32),
                       torch.tensor([role],dtype=torch.int64))
   edge_types=stored[0,12:24].long()
   nextmax=[]
   for t in range(len(request)):
    if t+1<len(request):
     logits=model.role_logits[edge_types,request[t+1]]
     nextmax.append(float(torch.sigmoid(logits).max()))
    else:nextmax.append(0.)
  features=[base+[nextmax[i]] for i,base in enumerate(feats)]
  recs.append({"key":key,"depth":len(request),"truth":bool(y),
               "features":features,"prefix_preds":preds})
 return recs

class RiskHead(nn.Module):
 def __init__(self):
  super().__init__()
  self.m=nn.Sequential(nn.Linear(8,12),nn.Tanh(),nn.Linear(12,1))
 def forward(self,feat):return self.m(feat).squeeze(-1)

def train(rows):
 X=[];Y=[]
 for row in rows:
  for i in range(row["depth"]-1):
   # Training-only oracle supervision. Positives are UNSAFE to stop
   # negatively even when their early prefix score is near zero.
   safe=(not row["truth"] and not row["prefix_preds"][i]
       and not any(row["prefix_preds"][i:]))
   X.append(row["features"][i]);Y.append(int(safe))
 x=torch.tensor(X,dtype=torch.float32)
 y=torch.tensor(Y,dtype=torch.float32)
 head=RiskHead()
 optim=torch.optim.Adam(head.parameters(),lr=.025)
 for _ in range(180):
  optim.zero_grad()
  z=head(x)
  # False safe decisions are penalized 25 times more than missed savings.
  loss=nn.functional.binary_cross_entropy_with_logits(
      z,y,weight=torch.where(y>.5,1.,25.))
  loss.backward()
  optim.step()
 return head,float(loss.detach()),float(y.mean())

def simulate(rows,mode,head=None,threshold=1.):
 out=[]
 for row in rows:
  step=row["depth"]
  for i in range(row["depth"]):
   if mode=="full":stop=False
   elif mode=="old_stop":stop=not row["prefix_preds"][i]
   elif mode=="prefix_threshold":stop=(not row["prefix_preds"][i] and
                                       row["features"][i][0]<threshold)
   elif mode=="risk":
    with torch.no_grad():
     prob=float(torch.sigmoid(head(torch.tensor(
        [row["features"][i]],dtype=torch.float32)))[0])
    stop=(not row["prefix_preds"][i]) and prob>=threshold
   elif mode=="oracle":
    stop=(not row["prefix_preds"][i] and not row["truth"] and
          all(not a for a in row["prefix_preds"][i:]))
   else:raise ValueError(mode)
   if stop or i==row["depth"]-1:
    step=i+1;break
  out.append({"answer":bool(row["prefix_preds"][step-1]),"steps":step,
              "early_halt":step<row["depth"]})
 return out

def metrics(rows,out):
 total=len(rows)
 correct=sum(a["answer"]==r["truth"] for a,r in zip(out,rows))
 steps=sum(a["steps"] for a in out)
 full=sum(r["depth"] for r in rows)
 pos=[(a,r) for a,r in zip(out,rows) if r["truth"]]
 neg=[(a,r) for a,r in zip(out,rows) if not r["truth"]]
 fn=sum(not a["answer"] for a,r in pos)
 fp=sum(a["answer"] for a,r in neg)
 accuracy=correct/total
 return {"correct":correct,"accuracy":accuracy,"false_negatives":fn,
  "false_negative_rate":fn/len(pos),
  "false_positives":fp,"false_positive_rate":fp/len(neg),
  "actual_recurrence_steps":steps,"full_recurrence_steps":full,
  "recurrent_step_saving":1-steps/full,
  "utility_proxy":accuracy-.15*steps/full}

def choose_threshold(trainrows,head):
 # All calibration and selection occurs before the VALID source is opened.
 grid=(.5,.6,.7,.8,.9,.95,.98,.99,.995,.999)
 evaluated=[]
 for v in grid:
  m=metrics(trainrows,simulate(trainrows,"risk",head,v))
  eligible=m["accuracy"]>=.995 and m["false_negative_rate"]<=.005
  evaluated.append((v,m,eligible))
 eligible=[x for x in evaluated if x[2]]
 if not eligible:return 1.,evaluated
 selected=max(eligible,key=lambda x:(x[1]["recurrent_step_saving"],x[0]))
 return selected[0],evaluated

def evaluate():
 started=time.perf_counter()
 core=f13.f11.model()
 traincases=f13.gather_cases(TRAIN_SEEDS,TRAIN_FAMS,(4,5,6),(0,1))
 assert len(traincases)==288
 trainrows=records(traincases,core)
 head,loss,pos_rate=train(trainrows)
 limit,grid=choose_threshold(trainrows,head)
 # Confidence baseline calibrated independently on TRAIN alone with same
 # safety budget, allowing no-stop fallback.
 simplegrid=(.0000001,.000001,.00001,.0001,.001,.01,.05,.1,.25)
 simple=[]
 for c in simplegrid:
  metric=metrics(trainrows,simulate(trainrows,"prefix_threshold",threshold=c))
  simple.append((c,metric,metric["accuracy"]>=.995 and metric["false_negative_rate"]<=.005))
 eligible=[x for x in simple if x[2]]
 simplebest=max(eligible,key=lambda x:(x[1]["recurrent_step_saving"],x[0]))[0] if eligible else 0.
 validation=f13.gather_cases(VALID_SEEDS,VALID_FAMS,(7,8),(0,1))
 assert len(validation)==192
 valrows=records(validation,core)
 variants={"learned_asymmetric_risk":simulate(valrows,"risk",head,limit),
    "train_safe_confidence":simulate(valrows,"prefix_threshold",threshold=simplebest),
    "fixed_full":simulate(valrows,"full"),
    "old_early_negative":simulate(valrows,"old_stop"),
    "hindsight_oracle_upper":simulate(valrows,"oracle")}
 scores={k:metrics(valrows,v) for k,v in variants.items()}
 learned=scores["learned_asymmetric_risk"]
 fixed=scores["fixed_full"]
 simple=scores["train_safe_confidence"]
 passed=(learned["accuracy"]>=.95 and learned["false_negative_rate"]<=.05
     and learned["false_positive_rate"]<=.05
     and learned["recurrent_step_saving"]>=.15
     and learned["accuracy"]>=fixed["accuracy"]-.03
     and learned["utility_proxy"]>=simple["utility_proxy"]+.01)
 rows=[{"seed":rec["key"][0],"family":rec["key"][1],
   "depth":rec["depth"],"role_shift":rec["key"][3],
   "variant":rec["key"][4],"truth":rec["truth"],
   "prefix_features":rec["features"],"prefix_predictions":rec["prefix_preds"],
   "decisions":{name:v[i] for name,v in variants.items()}}
     for i,rec in enumerate(valrows)]
 return {"schema":"yggdrasil.f14.risk-constrained-continuation-development.v1",
  "stage":"DEVELOPMENT_ONLY","parent_F13_sha":"58b60c5f5e1293ad0485b1e3abe5b5662287cf67",
  "train_families":list(TRAIN_FAMS),"validation_families":list(VALID_FAMS),
  "train_seed_bounds":[60100,60112],"validation_seed_bounds":[60600,60612],
  "train_graph_triplets":len(traincases),"validation_graph_triplets":len(validation),
  "train_questions":len(trainrows),"validation_questions":len(valrows),
  "policy_parameters":sum(v.numel() for v in head.parameters()),
  "native_state_bytes":576,"policy_input_features":8,
  "training_epochs":180,"train_loss":loss,
  "train_safe_label_rate":pos_rate,"training_negative_stop_misclassification_weight":25,
  "train_selected_risk_threshold":limit,"train_selected_simple_threshold":simplebest,
  "calibration_grid":[{"threshold":v,"train":m,"eligible":ok} for v,m,ok in grid],
  "scores":scores,"rows":rows,
  "verdict":"DEVELOPMENT_RISK_AWARE_STOPPING_TRANSFER" if passed
       else "DEVELOPMENT_NO_RISK_AWARE_STOPPING_TRANSFER",
  "learned_policy_only_stops_negative":True,
  "calibration_only_training":True,
  "policy_inference_sees_future_oracle":False,
  "training_labels_use_train_only_future":True,
  "feature_next_role_compatibility_from_static_graph":True,
  "computation_savings_only_recurrent_step_proxy":True,
  "feature_collection_cost_excluded_from_saving":True,
  "query_max_depth_programmed":True,
  "independent_source_birth":False,"sealed_first_use":False,
  "accepted_ref_mutation":False,"external_model_calls":0,
  "original_wall_ms":round((time.perf_counter()-started)*1000)}
if __name__=="__main__":print(json.dumps(evaluate(),sort_keys=True,indent=2))
