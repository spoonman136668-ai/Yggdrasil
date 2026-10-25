"""C35: nine genuinely executed TWO-action interventions at source-matched public states.

Every branch independently resets the immutable original MiniGrid and replays
identical selected prefix actions. FIT scoring uses distinct frozen source seeds.
No original R3 edit, protected first use or unperformed-action label.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import resource
import time
import traceback
import numpy as np

from research.native.itd02.r1.native_policy import canonical
from research.mass_r7c20 import run as c20
from research.mass_r7c22 import run as c22

HERE=Path(__file__).resolve().parent
P=json.loads((HERE/"PREREG.json").read_text())
FIELDS=set(P["protocol"]["independentSourcePublicObservationFields"]) if "independentSourcePublicObservationFields" in P["protocol"] else {"x","y","goal_x","goal_y","direction","front_blocked"}
PAIRS=tuple(tuple(x) for x in P["protocol"]["sourcePhysicalActionPairs"])
TICKS=tuple(P["protocol"]["sourcePrefixTicks"])
PREFIX=P["protocol"]["publicPrefixActionsRepeated"]
SCHEMA=P["schema"]

def fp(x):
 return hashlib.sha256(canonical(x)).hexdigest()
def validate():
 if (SCHEMA!="itd02.c35.prospective-real-two-action-source-effect-v1"
     or P["parentC34"]!="b81a7085afb7ccfba6e9fec0a303c83d731ae6f7"
     or P["source"]["external"]!="Farama-Foundation/Minigrid@7f5853792ea7f04f75614661006d87fcf949f26d"
     or len(PAIRS)!=9 or set(PAIRS)!={(a,b) for a in range(3) for b in range(3)}
     or TICKS!=(0,3,6) or PREFIX!=[2,0,2,1,2,0]
     or P["limits"]["sourceRoleNotProtectedScientificFirstUse"] is not True
     or P["prediction"]["smoothingPseudoObservations"]!=16
     or P["prediction"]["linearRidgePenalty"]!=10):
  raise ValueError("C35_ORIGINAL_FROZEN_SOURCE_IDENTITY_DRIFT")
 return P

def public(obs,goal):
 s=c22.public_dynamic(obs,goal).__dict__.copy()
 if(set(s)!=FIELDS or
     not all(type(s[k]) is int for k in ("x","y","goal_x","goal_y","direction")) or
     type(s["front_blocked"]) is not bool or s["direction"] not in range(4)):
  raise ValueError("C35_PRIVILEGED_OR_INVALID_PUBLIC_FIELDS")
 return s

def source_sha(obs,goal):
 # Source grid is used ONLY for strict branch replay custody, never as feature.
 return hashlib.sha256(obs["image"].tobytes()+
       canonical([int(obs["direction"]),list(goal)])).hexdigest()

def anchor(family,seed,tick):
 env=c20.env_make(family)
 try:
  obs,_=env.reset(seed=seed);goal=c20.goal_from(obs)
  initial=source_sha(obs,goal)
  prefix=[]
  for t in range(tick):
   chosen=PREFIX[t%len(PREFIX)]
   before=public(obs,goal);bsha=source_sha(obs,goal)
   nxt,reward,term,trunc,_=env.step(chosen)
   after=public(nxt,goal)
   prefix.append({"step":t,"action":chosen,"before":before,"after":after,
      "before_sha":bsha,"after_sha":source_sha(nxt,goal),
      "reward":float(reward),"term":bool(term),"trunc":bool(trunc)})
   obs=nxt
   if term or trunc:return None
  return {"family":family,"seed":seed,"tick":tick,
      "initial_source_sha256":initial,
      "anchor_source_sha256":source_sha(obs,goal),
      "public_initial":public(obs,goal),"original_source_prefix":prefix}
 finally:env.close()

def physically_execute_pair(anchor,pair):
 fam,seed=anchor["family"],anchor["seed"]
 env=c20.env_make(fam)
 try:
  obs,_=env.reset(seed=seed);goal=c20.goal_from(obs)
  if source_sha(obs,goal)!=anchor["initial_source_sha256"]:
   raise ValueError("C35_ORIGINAL_RESET_NOT_IDENTICAL")
  for p in anchor["original_source_prefix"]:
   if public(obs,goal)!=p["before"] or source_sha(obs,goal)!=p["before_sha"]:
    raise ValueError("C35_BEFORE_PREFIX_IDENTITY")
   nxt,reward,term,trunc,_=env.step(p["action"])
   if (public(nxt,goal)!=p["after"] or
      source_sha(nxt,goal)!=p["after_sha"] or
      float(reward)!=p["reward"] or bool(term)!=p["term"] or
      bool(trunc)!=p["trunc"] or term or trunc):
    raise ValueError("C35_ORIGINAL_PREFIX_REPLAY_MISMATCH")
   obs=nxt
  if (source_sha(obs,goal)!=anchor["anchor_source_sha256"] or
       public(obs,goal)!=anchor["public_initial"]):
    raise ValueError("C35_DIFFERENT_PHYSICAL_ANCHOR")
  results=[];start=public(obs,goal);initial_dist=abs(start["x"]-start["goal_x"])+abs(start["y"]-start["goal_y"])
  for ordinal,act in enumerate(pair):
   before=public(obs,goal)
   nxt,reward,term,trunc,_=env.step(act)
   after=public(nxt,goal)
   if not math.isfinite(float(reward)):
    raise ValueError("C35_NONFINITE_ORIGINAL_REWARD")
   results.append({"action":act,"before":before,"after":after,
       "reward":float(reward),"term":bool(term),"trunc":bool(trunc)})
   obs=nxt
   if (term or trunc) and ordinal==0:
    return {"pair":list(pair),"actual_first_only":results,
       "completed_two_original_actions":False}
   if term or trunc:break
  after=results[-1]["after"]
  distance=abs(after["x"]-after["goal_x"])+abs(after["y"]-after["goal_y"])
  return {"pair":list(pair),"actual_selected_source_actions":results,
    "completed_two_original_actions":len(results)==2,
    "actually_observed_next_front_blocked":bool(after["front_blocked"]),
    "real_two_step_goal_distance_improvement":initial_dist-distance,
    "actual_source_reward_sum":sum(x["reward"] for x in results),
    "actual_agent_translation":abs(after["x"]-start["x"])+abs(after["y"]-start["y"]),
    "physical_trace_sha256":fp(results)}
 finally:env.close()

def collect(phase):
 out=[];audit=[]
 for family,cohorts in P["worlds"].items():
  seeds=cohorts[phase]
  for seed in seeds:
   for tick in TICKS:
    a=anchor(family,seed,tick)
    if a is None:
     audit.append({"family":family,"seed":seed,"tick":tick,"excluded":"terminal_before_anchor"})
     continue
    observed={str(x[0])+str(x[1]):physically_execute_pair(a,x) for x in PAIRS}
    if any(not trial["completed_two_original_actions"] for trial in observed.values()):
     audit.append({"family":family,"seed":seed,"tick":tick,
       "excluded":"source_terminal_during_pair_no_training_or_scoring"})
     continue
    a["all_nine_original_physical_pairs"]=observed
    out.append(a)
 return out,audit

def features(row,pair):
 s=row["public_initial"];a,b=pair
 if set(s)!=FIELDS:raise ValueError("C35_BAD_TRAIN_PUBLIC_FEATURES")
 dx=max(-8,min(8,s["goal_x"]-s["x"]))/8
 dy=max(-8,min(8,s["goal_y"]-s["y"]))/8
 family=float(row["family"]=="MiniGrid-Dynamic-Obstacles-8x8-v0")
 return [1.,family,s["x"]/20.,s["y"]/20.,dx,dy,
   *[float(s["direction"]==d) for d in range(4)],float(s["front_blocked"]),
   *[float(pair==(i,j)) for i in range(3) for j in range(3)]]

class Models:
 def __init__(self,train):
  self.prior=defaultdict(lambda:[0,0])
  self.local=defaultdict(lambda:[0,0])
  X=[];Y=[]
  for row in train:
   family=row["family"];s=row["public_initial"]
   if set(row["all_nine_original_physical_pairs"])!={str(a)+str(b) for a,b in PAIRS}:
    raise ValueError("C35_MISSING_PHYSICAL_INTERVENTION")
   for a,b in PAIRS:
    t=row["all_nine_original_physical_pairs"][str(a)+str(b)]
    if(not t["completed_two_original_actions"] or
      [q["action"] for q in t["actual_selected_source_actions"]] !=[a,b]):
      raise ValueError("C35_FABRICATED_SOURCE_ACTION_PAIR")
    y=int(t["actually_observed_next_front_blocked"])
    k=(family,a,b);z=self.prior[k];z[0]+=y;z[1]+=1
    k2=(family,s["direction"],int(s["front_blocked"]),a,b)
    z2=self.local[k2];z2[0]+=y;z2[1]+=1
    X.append(features(row,(a,b)));Y.append(y)
  if len(self.prior)!=18:raise ValueError("C35_NOT_ALL_ACTIONS_AND_FAMILIES_TRAINED")
  arr=np.asarray(X,dtype=np.float64);yy=np.asarray(Y,dtype=np.float64)
  reg=np.eye(arr.shape[1])*P["prediction"]["linearRidgePenalty"]
  reg[0,0]=0.
  self.w=np.linalg.solve(arr.T@arr+reg,arr.T@yy).tolist()
  self.n=len(Y);self.weights_sha256=fp(self.w)

 def score(self,row,pair):
  fam=row["family"];s=row["public_initial"];a,b=pair
  prior=self.prior[fam,a,b]
  if prior[1]==0:raise ValueError("C35_NO_ACTUAL_PAIR_TRAINING")
  p0=(prior[0]+1)/(prior[1]+2)
  local=self.local.get((fam,s["direction"],int(s["front_blocked"]),a,b),(0,0))
  k=P["prediction"]["smoothingPseudoObservations"]
  candidate=(local[0]+k*p0)/(local[1]+k)
  linear=sum(x*w for x,w in zip(features(row,pair),self.w))
  return {"two_step_source_conditional":min(.99,max(.01,candidate)),
     "equal_source_pair_prior":min(.99,max(.01,p0)),
     "strong_independent_full_public_linear":min(.99,max(.01,linear)),
     "observed_context_FIT_count":local[1]}

def metrics(rows):
 n=len(rows)
 if n==0:return {"n":0,"brier":None,"logloss":None}
 return {"n":n,
   "brier":sum((p-y)**2 for p,y in rows)/n,
   "logloss":-sum(y*math.log(p)+(1-y)*math.log(1-p) for p,y in rows)/n}

def evaluate():
 validate()
 train,fit_audit=collect("FIT")
 model=Models(train)
 check,check_audit=collect("FIT_CHECK")
 predicted=[]
 for row in check:
  scores={}
  for pair in PAIRS:
   key=str(pair[0])+str(pair[1])
   actual=row["all_nine_original_physical_pairs"][key]
   models=model.score(row,pair)
   scores[key]=models
   predicted.append({"family":row["family"],"seed":row["seed"],"tick":row["tick"],
       "pair":list(pair),"truth":int(actual["actually_observed_next_front_blocked"]),
       "models":models})
  row["frozen_FIT_trained_predictions"]=scores
 grouped={}
 for mode in ("two_step_source_conditional","equal_source_pair_prior","strong_independent_full_public_linear"):
  grouped[mode]={"all":metrics([(r["models"][mode],r["truth"]) for r in predicted]),
     "by_family":{fam:metrics([(r["models"][mode],r["truth"])
         for r in predicted if r["family"]==fam]) for fam in P["worlds"]}}
 qualified=P["acceptance"]
 conditions={
   "FIT_fully_executed_source_anchor_count":len(train)>=qualified["minimumOriginalFITFullyPairedAnchors"],
   "FIT_CHECK_new_source_anchor_count":len(check)>=qualified["minimumFITCHECKFullyPairedAnchors"],
   "FIT_CHECK_true_action_pair_trials":len(predicted)>=qualified["minimumRealSourceFITCHECKPairTrials"],
   "all_nine_physical_pairs_per_family":all(sum(row["family"]==fam for row in train)>0
      for fam in P["worlds"]),
   "conditional_prediction_better_than_equal_source_pair_prior":
       grouped["equal_source_pair_prior"]["all"]["brier"]-
       grouped["two_step_source_conditional"]["all"]["brier"]>=qualified["minimumConditionalBrierGainVsSourcePairPrior"],
   "conditional_prediction_better_than_independently_fitted_full_public_linear":
       grouped["strong_independent_full_public_linear"]["all"]["brier"]-
       grouped["two_step_source_conditional"]["all"]["brier"]>=qualified["minimumConditionalBrierGainVsIndependentLinear"]}
 verdict=qualified["positive"] if all(conditions.values()) else qualified["noGo"]
 return {"schema":SCHEMA,"result":verdict,"criteria":conditions,
    "source_original_fit_real_two_action_forks":train,
    "source_independent_internal_fit_check_real_forks":check,
    "FIT_original_anchor_exclusions":fit_audit,
    "FIT_CHECK_original_anchor_exclusions":check_audit,
    "FIT_source_original_fitted_intervention_pairs":model.n,
    "fitted_conventional_full_public_weights_sha256":model.weights_sha256,
    "frozen_test_source_metrics":grouped,
    "genuine_original_source_observation_action_pair_trials":predicted,
    "two_independent_real_original_source_actions_per_fork":True,
    "original_environment_source":P["source"]["external"],
    "source_protocol_sha256":hashlib.sha256((HERE/"PREREG.json").read_bytes()).hexdigest(),
    "new_protected_or_unknown_source_episodes":0,
    "science_accepted":False,"original_R3_modified":False}

def main():
 pa=argparse.ArgumentParser();pa.add_argument("--output",type=Path,required=True)
 args=pa.parse_args()
 if args.output.exists() or not args.output.parent.is_dir():
  raise ValueError("C35_NONFRESH_SOURCE_OUTPUT")
 start=time.perf_counter();cpu=time.process_time()
 try:r=evaluate()
 except Exception as e:
  r={"schema":SCHEMA,"result":"ORIGINAL_SOURCE_OR_INFRASTRUCTURE_BLOCKED",
   "error_type":type(e).__name__,"error":str(e),
   "traceback_tail":traceback.format_exc().splitlines()[-15:],
   "science_accepted":False,"original_R3_modified":False}
 r["resources"]={"python_CPU_seconds":time.process_time()-cpu,
    "whole_source_wall_seconds":time.perf_counter()-start,
    "peak_self_RSS_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    "energy_measured":False,"no_native_subprocesses":True}
 args.output.write_bytes(canonical(r)+b"\n")
 print("C35_TWO_STEP_ORIGINAL_SOURCE_RESULT="+r["result"])
 if "frozen_test_source_metrics" in r:
  print("C35_TRUE_PHYSICAL_TWO_ACTION_SCORES="+json.dumps(r["frozen_test_source_metrics"],sort_keys=True))
  print("C35_FIXED_CRITERIA="+json.dumps(r["criteria"],sort_keys=True))
 if r["result"]=="ORIGINAL_SOURCE_OR_INFRASTRUCTURE_BLOCKED":raise SystemExit(1)
if __name__=="__main__":main()
