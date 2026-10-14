"""Y-F6: trained graph-reachability trace supervision; heldout novel motifs.

Training-only edge-reachability witnesses provide intermediate task guidance,
but the trained candidate's inference uses only learned entity matching and
recurrent message passing. No programmed equality or OR propagation in inference.
The new family split is disjoint from Y-F1 through Y-F5; this is DEVELOPMENT
ONLY and MUST NOT consume the independently admitted F3 first-use source.
"""
from __future__ import annotations
import importlib.util,json,time
from pathlib import Path
import torch
from torch import nn

HERE=Path(__file__).resolve().parent
src=HERE.parent/"20261014-y-f4"/"execute.py"
spec=importlib.util.spec_from_file_location("yf4_parent",src)
assert spec and spec.loader
f4=importlib.util.module_from_spec(spec);spec.loader.exec_module(f4)
f1=f4.f1
torch.set_num_threads(1)
TRAIN=range(47900,47924)
VALID=range(48200,48212)
MOTIFS={
20:((0,1),(1,2),(2,3),(3,4),(0,9),(9,10),(10,11),(11,12),(5,6),(6,7),(7,8),(8,13)),
21:((0,1),(1,2),(2,3),(3,4),(2,5),(5,6),(6,2),(1,7),(7,8),(8,7),(9,10),(10,11)),
22:((0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,3),(1,7),(7,8),(8,9),(9,10),(11,12)),
23:((0,1),(1,2),(2,3),(3,4),(3,0),(0,5),(5,1),(2,6),(6,7),(7,8),(8,9),(10,11)),
24:((0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,2),(1,7),(7,3),(4,8),(8,9),(10,11)),
25:((0,1),(1,2),(2,3),(3,4),(1,0),(1,5),(5,6),(6,7),(7,2),(3,8),(8,9),(10,11)),
26:((0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),(8,1),(2,9),(9,10),(11,12)),
27:((0,1),(1,2),(2,3),(3,4),(2,5),(5,2),(1,6),(6,7),(7,3),(4,8),(8,9),(9,10)),
}
TRAIN_FAMILIES=(20,21,22,23)
VALID_FAMILIES=(24,25,26,27)
def reach(edges,source,target,length):
 active={source}
 for _ in range(length):
  active={b for a,b in edges if a in active}
 return target in active
def fixture(seed,family,variant,perm):
 assert family in MOTIFS
 ordered=[(f1.relabel(a,seed,variant),f1.relabel(b,seed,variant))
          for a,b in MOTIFS[family]]
 for i in range(11,0,-1):
  k=(seed*37+i*11+family*23+perm*13)%(i+1)
  ordered[i],ordered[k]=ordered[k],ordered[i]
 assert len(ordered)==12 and len(set(ordered))==12
 source,target=(f1.relabel(0,seed,variant),f1.relabel(4,seed,variant))
 assert reach(ordered,source,target,4)
 seen={v for edge in ordered for v in edge}
 hard_negative=sorted(x for x in seen
                      if x!=target and not reach(ordered,source,x,4))
 assert hard_negative
 negative=hard_negative[(seed+family+perm)%len(hard_negative)]
 if (seed+family+perm)%2:
  questions=((source,negative),(source,target))
  labels=(False,True)
 else:
  questions=((source,target),(source,negative))
  labels=(True,False)
 assert [reach(ordered,a,b,4) for a,b in questions]==list(labels)
 return ordered,questions,labels

def cohort(seeds,families,variant,permutations):
 edges,questions,labels,keys=[],[],[],[]
 for seed in seeds:
  for fam in families:
   for perm in range(permutations):
    e,q,t=fixture(seed,fam,variant,perm)
    edges.append(e);questions.append(q);labels.append(t)
    keys.append((seed,fam,perm))
 return (torch.tensor(edges,dtype=torch.int32),
         torch.tensor(questions,dtype=torch.int32),
         torch.tensor(labels,dtype=torch.float32),keys)

def training_reachability_traces(facts,questions):
 # Used only for TRAINING auxiliary loss. Not called on VALID data.
 src=facts[:,:,0]
 dst=facts[:,:,1]
 link=(dst[:,:,None]==src[:,None,:])&f4.MASK
 outputs=[]
 for q in range(2):
  reached=(src==questions[:,q,0,None])
  states=[reached.float()]
  for _ in range(3):
   reached=(reached.unsqueeze(-1)&link).any(dim=1)
   states.append(reached.float())
  outputs.append(torch.stack(states,dim=1))
 return torch.stack(outputs,dim=1)

def model_forward(model,facts,questions):
 state=model.make_state(facts)
 packed=state[:,:12].contiguous().view(torch.int32).long()
 src=(packed>>16)&65535
 dst=packed&65535
 links=torch.zeros((state.shape[0],12,12),dtype=torch.float32)
 links[:,f4.MASK]=state[:,12:]
 preds=[];traces=[]
 for q in range(2):
  begin=questions[:,q,0,None]
  end=questions[:,q,1,None]
  active=model.similarity(begin,src)
  terminal=model.similarity(dst,end)
  snapshots=[active]
  for _ in range(3):
   message=torch.bmm(active.unsqueeze(1),links).squeeze(1)
   active=torch.sigmoid(model.message_gain*message+
                        model.recurrent_gain*active+model.activation_bias)
   snapshots.append(active)
  outcome=torch.sigmoid(model.output_gain*(active*terminal).sum(-1)+
                        model.output_bias)
  preds.append(outcome);traces.append(torch.stack(snapshots,dim=1))
 return torch.stack(preds,dim=1),torch.stack(traces,dim=1)

def fit(model,train_data,extra_trace):
 optim=torch.optim.Adam(model.parameters(),lr=.055)
 train_truth=train_data[2]
 trace_truth=training_reachability_traces(train_data[0],train_data[1]) if extra_trace else None
 started=time.perf_counter()
 for _ in range(160):
  optim.zero_grad()
  out,traces=model_forward(model,train_data[0],train_data[1])
  task_loss=nn.functional.binary_cross_entropy(out.clamp(.00001,.99999),train_truth)
  if extra_trace:
   trace_weight=torch.where(trace_truth>.5,3.,1.)
   trace_loss=nn.functional.binary_cross_entropy(traces.clamp(.00001,.99999),
            trace_truth,weight=trace_weight)
   loss=task_loss+.6*trace_loss
  else:
   loss=task_loss
  loss.backward()
  nn.utils.clip_grad_norm_(model.parameters(),10.)
  optim.step()
 return float(loss.detach()),round((time.perf_counter()-started)*1000)

def evaluate():
 torch.manual_seed(729)
 started=time.perf_counter()
 train=cohort(TRAIN,TRAIN_FAMILIES,0,3)
 valid=cohort(VALID,VALID_FAMILIES,2,4)
 assert train[0].shape==(288,12,2) and valid[0].shape==(192,12,2)
 teacher=f4.RecurrentComposer()
 plain=f4.RecurrentComposer()
 with torch.no_grad():
  init=(model_forward(teacher,valid[0],valid[1])[0]>=.5)
 # Same architecture and initial weights; different TRAIN-ONLY objective.
 plain.load_state_dict(teacher.state_dict())
 task_bce,task_ms=fit(plain,train,False)
 guided_bce,guided_ms=fit(teacher,train,True)
 with torch.no_grad():
  candidate=(model_forward(teacher,valid[0],valid[1])[0]>=.5)
  task_only=(model_forward(plain,valid[0],valid[1])[0]>=.5)
  coded=(f1.fixed_exact(valid[0],valid[1])>=.5)
 truth=valid[2].bool()
 pred={"training_trace_guided_recurrence":candidate,
       "task_only_matched_recurrence":task_only,
       "initialized_architecture":init,
       "coded_exact_upper_control":coded}
 stats={}
 for name,answer in pred.items():
  neg=~truth
  stats[name]={"correct":int((answer==truth).sum()),
       "accuracy":float((answer==truth).float().mean()),
       "false_positives":int((answer&neg).sum()),
       "negative_fp_rate":float((answer&neg).sum().item()/neg.sum().item())}
 rows=[]
 for i,(seed,family,perm) in enumerate(valid[3]):
  rows.append({"seed":seed,"family":family,"permutation":perm,
               "truth":truth[i].tolist(),
               "predictions":{name:a[i].tolist() for name,a in pred.items()}})
 assert len(rows)==192 and sum(not x for row in rows for x in row["truth"])==192
 guided=stats["training_trace_guided_recurrence"]
 plain_stats=stats["task_only_matched_recurrence"]
 initialized=stats["initialized_architecture"]
 upper=stats["coded_exact_upper_control"]
 passed=(guided["accuracy"]>=.85 and guided["negative_fp_rate"]<=.15
   and guided["accuracy"]-plain_stats["accuracy"]>=.10
   and guided["accuracy"]-initialized["accuracy"]>=.15
   and upper["accuracy"]-guided["accuracy"]<=.15)
 return {"schema":"yggdrasil.foundation.f6.path-trace-guided-transfer-dev.v1",
  "stage":"DEVELOPMENT_ONLY","source_F5_sha":"94dcd297302144dbef8132dc15fe44899da9f249",
  "train_seed_bounds":[47900,47924],"validation_seed_bounds":[48200,48212],
  "train_families":list(TRAIN_FAMILIES),"validation_families":list(VALID_FAMILIES),
  "training_states":len(train[3]),"validation_states":len(rows),
  "question_count":384,"negative_questions":192,
  "native_state_bytes":576,"model_parameters_each":sum(p.numel() for p in teacher.parameters()),
  "training_steps_each":160,"trace_weight":.6,"positive_trace_weight":3.0,
  "training_only_intermediate_oracle_labels":True,"validation_oracle_trace_opened":False,
  "trained_without_code_equality_at_inference":True,"coded_or_at_inference":False,
  "engineered_id_bits_and_fixed_rounds":True,
  "training_losses":{"guided":guided_bce,"task_only":task_bce},
  "training_wall_ms":{"guided":guided_ms,"task_only":task_ms},
  "scores":stats,"rows":rows,
  "guided_frozen_weights":{name:val.detach().tolist() for name,val in teacher.state_dict().items()},
  "registered_verdict":"DEVELOPMENT_TRAIN_ONLY_PATH_WITNESSES_IMPROVE_TRANSFER" if passed else
      "DEVELOPMENT_NO_TRAIN_ONLY_PATH_WITNESS_TRANSFER",
  "source_birth_independently_witnessed":False,"sealed_first_use":False,
  "accepted_ref_mutation":False,"external_llm_calls":0,
  "original_wall_ms":round((time.perf_counter()-started)*1000)}
if __name__=="__main__":
 print(json.dumps(evaluate(),sort_keys=True,indent=2))
