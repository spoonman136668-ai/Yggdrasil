"""Y-F13: train a genuine per-state continuation decision.

This development study holds the F10 typed recurrent reasoning core FROZEN.
A separate learned controller sees only the prefix computation's model state
statistics, not oracle labels, graph-family IDs, or future recurrent states at
inference. Training-only targets use counterfactual final correctness. Compare
fixed-budget, pre-calibrated simple confidence, and hindsight-oracle controls.
F3 is unchanged/unadmitted. No claim of independent sealed science.
"""
from __future__ import annotations
import importlib.util,json,time
from pathlib import Path
import torch
from torch import nn

ROOT=Path(__file__).resolve().parent
src=ROOT.parent/"20261014-y-f11"/"execute.py"
spec=importlib.util.spec_from_file_location("y_f11_role_core",src)
assert spec and spec.loader
f11=importlib.util.module_from_spec(spec);spec.loader.exec_module(f11)
f10=f11.f10
torch.set_num_threads(1)
torch.manual_seed(1263)
TRAIN_FAMILIES=(60,61,62,63)
VALID_FAMILIES=(64,65,66,67)
TRAIN_SEEDS=range(58300,58312)
VALID_SEEDS=range(58800,58812)
TRAIN_DEPTHS=(4,5,6)
VALID_DEPTHS=(7,8)

def make_case(seed,fam,k,shift):
  assert k in TRAIN_DEPTHS+VALID_DEPTHS
  role=lambda j:(seed*3+fam*7+3*j+shift)%4
  edges=[(j,j+1) for j in range(k)]
  if fam%4==0: extra=[(0,min(3,k-1))]
  elif fam%4==1: extra=[(min(2,k-1),0)]
  elif fam%4==2: extra=[(k-1,1)]
  else: extra=[(k,0)]
  extra += [(k+10+j,k+11+j) for j in range(12-k-len(extra))]
  edges+=extra
  assert len(edges)==12 and len(set(edges))==12
  roles=[role(j) for j in range(12)]
  renamed=[(f10.f1.relabel(a,seed,2),f10.f1.relabel(b,seed,2)) for a,b in edges]
  pattern=tuple(roles[:k])
  # Alternative negative has a damaged necessary role in the actual graph;
  # a second negative requests identical role-bag in wrong order.
  modified=roles.copy()
  damaged=max(1,min(k-2,((seed+fam)%max(2,k-2))+1))
  modified[damaged]=(modified[damaged]+1)%4
  order=list(pattern)
  a,b=0,1
  assert order[a]!=order[b]
  order[a],order[b]=order[b],order[a]
  for i in range(11,0,-1):
    j=(seed*11+fam*17+k*23+shift*7+i*13)%(i+1)
    renamed[i],renamed[j]=renamed[j],renamed[i]
    roles[i],roles[j]=roles[j],roles[i]
    modified[i],modified[j]=modified[j],modified[i]
  query=(f10.f1.relabel(0,seed,2),f10.f1.relabel(k,seed,2))
  oracle=lambda rs,pattern:f10.typed_exact(renamed,rs,*query,pattern)
  assert oracle(roles,pattern) and not oracle(modified,pattern)
  assert not oracle(roles,order)
  return {"seed":seed,"family":fam,"depth":k,"role_shift":shift,
          "edges":renamed,"query":query,"roles":roles,
          "changed_roles":modified,"valid_sequence":pattern,
          "wrong_order_sequence":tuple(order)}

def gather_cases(seeds,fams,depths,shifts):
  return [make_case(seed,fam,k,shift)
          for seed in seeds for fam in fams for k in depths for shift in shifts]

def all_states(cases):
  # Each case provides one positive, two distinct hard negatives.
  facts=[];roles=[];query=[];patterns=[];truth=[];keys=[]
  for row in cases:
    for i,(rs,pattern,label) in enumerate(((row["roles"],row["valid_sequence"],1),
       (row["changed_roles"],row["valid_sequence"],0),
       (row["roles"],row["wrong_order_sequence"],0))):
      facts.append(row["edges"]);roles.append(rs)
      query.append(row["query"]);patterns.append(pattern)
      truth.append(label);keys.append((row["seed"],row["family"],row["depth"],row["role_shift"],i))
  return facts,roles,query,patterns,truth,keys

def trace_one(model,facts,roles,query,pattern):
  # No future states or hidden oracle are available to the policy.
  fact=torch.tensor([facts],dtype=torch.int32)
  erole=torch.tensor([roles],dtype=torch.int64)
  q=torch.tensor([query],dtype=torch.int32)
  state=model.encode(fact,erole)
  assert tuple(state.shape)==(1,144) and state.element_size()==4
  packed=state[:,:12].contiguous().view(torch.int32).long()
  src=(packed>>16)&65535;dst=packed&65535
  rel=state[:,12:24].long()
  link=model.core.similarity(dst[:,:,None],src[:,None,:])
  link=link*f10.f6.f4.MASK.to(link)
  active=model.core.similarity(q[:,0,None],src)
  terminal=model.core.similarity(dst,q[:,1,None])
  prev_probability=0.
  features=[];decisions=[]
  with torch.no_grad():
    for step,want in enumerate(pattern):
      gate=torch.sigmoid(model.role_logits[rel,torch.tensor([[want]])])
      if step:
        msg=torch.bmm(active.unsqueeze(1),link).squeeze(1)
        active=torch.sigmoid(model.core.message_gain*msg+
            model.core.recurrent_gain*active+model.core.activation_bias)
      active=active*gate
      prediction=float(torch.sigmoid(model.core.output_gain*(active*terminal).sum(-1)
                          +model.core.output_bias).item())
      # All seven features are emitted by THIS prefix alone; no future
      # requested role symbols, final task truth, or future rollouts.
      max_act=float(active.max().item())
      mean_act=float(active.mean().item())
      std_act=float(active.std(unbiased=False).item())
      step_frac=(step+1)/len(pattern)
      feat=[prediction,prediction-prev_probability,max_act,mean_act,
           std_act,step_frac,1.-step_frac]
      features.append(feat);decisions.append(prediction>=.5)
      prev_probability=prediction
  return features,decisions

def traces_for(rows,model):
  facts,roles,q,seq,truth,keys=all_states(rows)
  traces=[]
  for a,b,c,d,y,key in zip(facts,roles,q,seq,truth,keys):
    feats,pred=trace_one(model,a,b,c,d)
    traces.append({"key":key,"truth":bool(y),"features":feats,"prefix_preds":pred,
                   "depth":len(d)})
  return traces

class StopPolicy(nn.Module):
  def __init__(self):
    super().__init__()
    self.mlp=nn.Sequential(nn.Linear(7,8),nn.Tanh(),nn.Linear(8,1))
  def forward(self,x):
    return self.mlp(x).squeeze(-1)

def policy_run(record,policy=None,threshold=None,force=False,oracle=False):
  n=record["depth"]
  preds=record["prefix_preds"]
  actions=[]
  for i in range(n):
    # Oracle is an *upper bound* computed after original model rollout.
    if oracle:
      stop=(preds[i]==record["truth"] and
            all(pred==record["truth"] for pred in preds[i:]))
    elif force:
      stop=False
    elif threshold is not None:
      stop=record["features"][i][0]<=threshold
    else:
      assert policy is not None
      with torch.no_grad():
        f=torch.tensor([record["features"][i]],dtype=torch.float32)
        stop=bool(torch.sigmoid(policy(f))[0]>=.5)
    actions.append(stop)
    if stop or i==n-1:
      return {"answer":bool(preds[i]),"steps":i+1,
              "halt":bool(stop and i<n-1)}
  raise AssertionError("unreachable")

def aggregate(traces,policy=None,threshold=None,force=False,oracle=False):
  results=[policy_run(x,policy,threshold,force,oracle) for x in traces]
  correct=sum(int(a["answer"]==b["truth"]) for a,b in zip(results,traces))
  steps=sum(a["steps"] for a in results)
  full=sum(x["depth"] for x in traces)
  negatives=[(a,b) for a,b in zip(results,traces) if not b["truth"]]
  fpr=sum(a["answer"] for a,b in negatives)/len(negatives)
  return {"correct":correct,"accuracy":correct/len(traces),
    "false_positive_rate":fpr,
    "mean_steps":steps/len(traces),"full_steps":full,
    "actual_steps":steps,"compute_saved_fraction":1-steps/full,
    "utility":correct/len(traces)-.15*(steps/full),
    "details":results}

def evaluate():
  begun=time.perf_counter()
  frozen=f11.model()
  train_cases=gather_cases(TRAIN_SEEDS,TRAIN_FAMILIES,TRAIN_DEPTHS,(0,1))
  assert len(train_cases)==288
  train_trace=traces_for(train_cases,frozen)
  feats=[];target=[];weights=[]
  for rec in train_trace:
    for i,(x,pred) in enumerate(zip(rec["features"][:-1],rec["prefix_preds"][:-1])):
      # The training label uses development-only final task truth; inference
      # cannot access it. This is supervised expected-benefit approximation.
      safe=(pred==rec["truth"] and
            all(future==rec["truth"] for future in rec["prefix_preds"][i:]))
      feats.append(x);target.append(float(safe));weights.append(1.)
  x=torch.tensor(feats,dtype=torch.float32)
  y=torch.tensor(target,dtype=torch.float32)
  model=StopPolicy()
  opt=torch.optim.Adam(model.parameters(),lr=.035)
  train_start=time.perf_counter()
  for epoch in range(160):
    opt.zero_grad()
    logits=model(x)
    loss=nn.functional.binary_cross_entropy_with_logits(logits,y)
    loss.backward()
    opt.step()
  train_ms=round((time.perf_counter()-train_start)*1000)
  # Grid threshold controls are selected ONLY on the development TRAIN split;
  # no validation access before final control choices are frozen.
  grid=(.000001,.00001,.0001,.001,.01,.05,.1,.25,.49)
  scored={str(t):aggregate(train_trace,threshold=t) for t in grid}
  best=min(grid,key=lambda t:(-scored[str(t)]["utility"],t))
  baseline=aggregate(train_trace,threshold=best)
  train_policy=aggregate(train_trace,policy=model)
  validation=gather_cases(VALID_SEEDS,VALID_FAMILIES,VALID_DEPTHS,(0,1))
  assert len(validation)==192
  val_trace=traces_for(validation,frozen)
  decisions={
    "learned_expected_benefit_stop":aggregate(val_trace,policy=model),
    "fixed_complete_reasoning":aggregate(val_trace,force=True),
    "train_selected_confidence_threshold":aggregate(val_trace,threshold=best),
    "hindsight_oracle_upper":aggregate(val_trace,oracle=True)}
  learned=decisions["learned_expected_benefit_stop"]
  fixed=decisions["fixed_complete_reasoning"]
  simple=decisions["train_selected_confidence_threshold"]
  passed=(learned["accuracy"]>=.95 and learned["false_positive_rate"]<=.05 and
     learned["compute_saved_fraction"]>=.15 and
     learned["accuracy"]>=fixed["accuracy"]-.03 and
     learned["utility"]>=simple["utility"]+.01)
  rows=[]
  for i,rec in enumerate(val_trace):
    rows.append({"seed":rec["key"][0],"family":rec["key"][1],
      "depth":rec["depth"],"role_shift":rec["key"][3],
      "variant":rec["key"][4],"truth":rec["truth"],
      "prefix_features":rec["features"],"prefix_predictions":rec["prefix_preds"],
      "choices":{name:d["details"][i] for name,d in decisions.items()}})
  for value in decisions.values(): del value["details"]
  for value in (baseline,train_policy):value.pop("details",None)
  return {"schema":"yggdrasil.f13.learned-value-of-computation-development.v1",
    "stage":"DEVELOPMENT_ONLY",
    "parent_F12_sha":"fbe0269a4b32c42c497aa22b856720d39733c521",
    "train_families":list(TRAIN_FAMILIES),"val_families":list(VALID_FAMILIES),
    "train_depths":list(TRAIN_DEPTHS),"val_depths":list(VALID_DEPTHS),
    "train_graph_triplets":len(train_cases),"val_graph_triplets":len(validation),
    "train_question_count":len(train_trace),"val_question_count":len(val_trace),
    "policy_parameters":sum(p.numel() for p in model.parameters()),
    "frozen_core_parameters":38,"native_state_bytes":576,
    "train_policy_epochs":160,"training_wall_ms":train_ms,
    "train_ce":float(loss.detach()),"train_positive_stop_label_rate":float(y.mean()),
    "stop_feature_names":["prefix_prob","delta_prob","max_active","mean_active",
                          "std_active","prefix_fraction","remaining_fraction"],
    "train_selected_simple_threshold":best,
    "train_policy_score":train_policy,"train_heuristic_score":baseline,
    "policy_weights":{k:v.detach().tolist() for k,v in model.state_dict().items()},
    "scores":decisions,"rows":rows,
    "verdict":"DEVELOPMENT_LEARNED_COMPUTATION_CONTROL_TRANSFER" if passed
              else "DEVELOPMENT_NO_LEARNED_COMPUTATION_CONTROL_TRANSFER",
    "policy_inference_sees_future":False,
    "training_labels_use_train_oracle_future":True,
    "bounded_forced_terminal_at_query_end":True,
    "candidate_halts_early_from_learned_decision":True,
    "query_length_as_max_budget":True,"first_use_sealed":False,
    "independent_source_birth":False,"accepted_ref_mutation":False,
    "external_api_calls":0,"wall_ms":round((time.perf_counter()-begun)*1000)}
if __name__=="__main__":
  print(json.dumps(evaluate(),sort_keys=True,indent=2))
