"""C37 source-original factorial isolation of FIT-learned effect vs observed loop veto.

No native R3 source changes. Same prior C35 original FIT (279 genuine two-action
interventions) for every arm; 24 disjoint prospective original development worlds.
"""
from __future__ import annotations
import argparse,copy,hashlib,json,os,subprocess,sys,time
from pathlib import Path
try:
 import resource
except ImportError:
 resource=None
from research.native.itd02.r1.native_policy import PublicGrid,canonical
from research.native.itd02.r3.navigator import Navigator
from research.mass_r7c36.run import CausalOptions,read_C35_fit,make_nav,source_front,P as P_C36

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
P=json.loads((HERE/"PREREG.json").read_text())
SCHEMA=P["schema"]
ARMS=tuple(P["arms"])
PUBLIC_FIELDS={"x","y","direction","goal_x","goal_y","front_blocked"}

def sha(x):return hashlib.sha256(canonical(x)).hexdigest()

def prereg():
 if(SCHEMA!="itd02.c37.frozen-new-world-factorial-loop-veto-identifiability-v1"
    or P["parentC36"]!="e1a8465128debff54ed8f07597396df759187ed0"
    or P["FIT_only"]["actualPairCount"]!=279
    or len(ARMS)!=8
    or sum(len(x) for x in P["new_original_public_development_worlds"].values())!=24
    or P["contrast"]["sameC36ThresholdsAndOptionLogic"] is not True
    or P["governance"]["neverScientificProtectedFirstUse"] is not True):
  raise ValueError("C37_ORIGINAL_FIT_SOURCE_FIRST_PROTOCOL_DRIFT")

def predictor_mode(arm):
 if arm in ("native_veto","native_no_veto"):return "causal_two_step"
 if arm in ("shuffled_veto","shuffled_no_veto"):return "shuffled_effect_control"
 if arm in ("ridge_veto","ridge_no_veto"):return "trained_conventional_ridge_two_step"
 if arm=="FIT_motor_goal_heuristic_veto":return "motor_heuristic"
 if arm=="original_r3":return "original"
 raise ValueError("C37_UNREGISTERED_ACTOR")

def has_veto(arm):
 return arm in ("native_veto","shuffled_veto","ridge_veto",
                "FIT_motor_goal_heuristic_veto")

def motor_progress(model,s,turn):
 # Calibrated using the same actually selected forward actions in original C35 FIT.
 future_heading=(s.direction + (1 if turn==1 else -1))%4
 fitted=model.motors[str(future_heading)]
 if not fitted:return 0.
 steps=sorted(((int(cnt),key) for key,cnt in fitted.items()),reverse=True)
 _,axis=steps[0]
 dx,dy=[int(z) for z in axis.split(",")]
 before=abs(s.goal_x-s.x)+abs(s.goal_y-s.y)
 after=abs(s.goal_x-s.x-dx)+abs(s.goal_y-s.y-dy)
 return float(before-after)

def choose_action(nav,model,fam,s,arm,last_action,last_pose,pending):
 if type(nav) is not Navigator or set(s.__dict__)!=PUBLIC_FIELDS:
  raise ValueError("C37_CANNOT_USE_PRIVATE_SOURCE_MAP")
 source_front(nav,s)
 r3=nav.choose(s)
 if r3 not in (0,1,2):raise ValueError("C37_INVALID_ORIGINAL_R3")
 if pending and not s.front_blocked:
  return r3,2,False,True
 if arm=="original_r3" or r3==2:return r3,r3,False,False
 other=1-r3
 if has_veto(arm) and last_pose==(s.x,s.y) and last_action==r3:
  return r3,r3,False,False
 mode=predictor_mode(arm)
 if mode=="motor_heuristic":
  baseline=motor_progress(model,s,r3)
  alternative=motor_progress(model,s,other)
  n=2
 else:
  baseline,_=model.predict(fam,s.__dict__,(r3,2),mode)
  alternative,n=model.predict(fam,s.__dict__,(other,2),mode)
 if (n<P_C36["mechanism"]["requireAtLeastFITContextCount"] or
     alternative-baseline<P_C36["mechanism"]["minimumPredictedAdvantageOverR3Option"] or
     alternative<P_C36["mechanism"]["minimumPredictedGoalProgressToCommit"]):
  return r3,r3,False,False
 return r3,other,True,False

def cold_check(nav,model,fam,pub,arm,last_action,last_pose,pending):
 tmp=copy.deepcopy(nav)
 expected=choose_action(tmp,model,fam,pub,arm,last_action,last_pose,pending)[:2]
 snapshot=nav.snapshot()
 trained=model.snapshot()
 payload={"r3":snapshot.decode(),"fitted":trained,
    "fam":fam,"pub":pub.__dict__,"arm":arm,
    "last_action":last_action,"last_pose":last_pose,
    "pending":pending,"expected":expected}
 script="""import json,sys
from research.native.itd02.r1.native_policy import PublicGrid
from research.native.itd02.r3.navigator import Navigator
from research.mass_r7c36.run import CausalOptions
from research.mass_r7c37.run import choose_action
p=json.loads(sys.stdin.read())
nav=Navigator.restore(p['r3'].encode())
model=CausalOptions.from_snapshot(p['fitted'])
s=PublicGrid(**p['pub'])
assert list(choose_action(nav,model,p['fam'],s,p['arm'],p['last_action'],
             tuple(p['last_pose']) if p['last_pose'] is not None else None,
             p['pending'])[:2])==p['expected']
print('C37_INDEPENDENT_OS_ACTUAL_SOURCE_POLICY_STATE=PASS')
"""
 r=subprocess.run([sys.executable,"-B","-c",script],input=json.dumps(payload),
    capture_output=True,text=True,cwd=ROOT,timeout=35,
    env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1","OPENBLAS_NUM_THREADS":"1"})
 if r.returncode or "C37_INDEPENDENT_OS_ACTUAL_SOURCE_POLICY_STATE=PASS" not in r.stdout:
  raise ValueError("C37_AUTHENTIC_ACTUAL_EPISODE_COLD_PARITY:"+r.stderr[-900:])
 return {"cold_OS_source_policy_parity":True,"R3_snapshot_bytes":len(snapshot),
  "fitted_model_bytes":len(canonical(trained))}

def episode(fam,seed,arm,model):
 from research.mass_r7c20 import run as c20
 from research.mass_r7c22 import run as c22
 env=c20.env_make(fam)
 try:
  obs,_=env.reset(seed=seed)
  goal=c20.goal_from(obs)
  nav=make_nav(model.motors,tuple(int(x) for x in obs["image"].shape[:2]))
  history=[];last_action=None;last_pose=None;pending=False;cold=None
  overrides=0;starts=0
  for tick in range(P["maxActualSourceActionsPerEpisode"]):
   before=c22.public_dynamic(obs,goal)
   r3,chosen,commit,pending_executed=choose_action(nav,model,fam,before,arm,
       last_action,last_pose,pending)
   if (chosen not in (0,1,2) or
      (chosen!=r3 and not (r3 in (0,1) or pending_executed))):
    raise ValueError("C37_ILLEGAL_SOURCE_SELECTED_ACTION")
   new,reward,terminal,truncated,_=env.step(chosen)
   after=c22.public_dynamic(new,goal)
   nav.observe(before,chosen,after,float(reward),bool(terminal),False)
   if chosen!=r3:overrides+=1
   if commit:starts+=1
   history.append({"t":tick,"public_before":before.__dict__.copy(),
      "unchanged_R3_proposal":r3,"original_selected_action":chosen,
      "public_after":after.__dict__.copy(),"source_reward":float(reward),
      "terminated":bool(terminal),"truncated":bool(truncated),
      "actual_two_step_option_started":commit,
      "original_source_pending_forward_executed":pending_executed})
   last_pose=(before.x,before.y);last_action=chosen
   pending=bool(commit and not(terminal or truncated))
   if pending_executed:pending=False
   obs=new
   if tick==2 and not (terminal or truncated):
    cold=cold_check(nav,model,fam,after,arm,last_action,last_pose,pending)
   if terminal or truncated:break
  if cold is None:
   cold=cold_check(nav,model,fam,c22.public_dynamic(obs,goal),arm,
         last_action,last_pose,pending)
  if not history:raise ValueError("C37_ZERO_TRUE_ORIGINAL_ACTIONS")
  final=history[-1]
  inverse=0
  for a,b in zip(history,history[1:]):
   if(a["original_selected_action"] in (0,1) and
      b["original_selected_action"]==1-a["original_selected_action"] and
      (a["public_before"]["x"],a["public_before"]["y"])==
      (b["public_before"]["x"],b["public_before"]["y"])):
    inverse+=1
  return {"family":fam,"seed":seed,"arm":arm,
   "true_original_action_count":len(history),
   "true_source_goal":bool(final["terminated"] and final["source_reward"]>0),
   "true_source_collision_terminal":bool(final["terminated"] and final["source_reward"]<0),
   "true_source_horizon":bool(final["truncated"]),
   "actual_original_reward_sum":sum(x["source_reward"] for x in history),
   "real_inverted_turn_pairs_at_same_pose":inverse,
   "original_physical_turn_overrides":overrides,
   "actual_two_step_option_starts":starts,
   "full_original_public_source_action_trajectory":history,
   "original_trace_sha256":sha(history),
   "last_original_R3_graph_sha256":hashlib.sha256(nav.snapshot()).hexdigest(),
   "real_step3_process_cold":cold}
 finally:
  env.close()

def summarize(rows):
 result={}
 for arm in ARMS:
  filtered=[r for r in rows if r["arm"]==arm]
  result[arm]={"worlds":len(filtered),
   "goals":sum(int(r["true_source_goal"]) for r in filtered),
   "collisions":sum(int(r["true_source_collision_terminal"]) for r in filtered),
   "horizons":sum(int(r["true_source_horizon"]) for r in filtered),
   "mean_real_reward":sum(r["actual_original_reward_sum"] for r in filtered)/len(filtered),
   "true_actions":sum(r["true_original_action_count"] for r in filtered),
   "actual_overrides":sum(r["original_physical_turn_overrides"] for r in filtered),
   "actual_inverse_turn_pairs":sum(r["real_inverted_turn_pairs_at_same_pose"] for r in filtered),
   "by_family":{}}
  for fam in P["new_original_public_development_worlds"]:
   items=[r for r in filtered if r["family"]==fam]
   result[arm]["by_family"][fam]={
      "worlds":len(items),"goals":sum(r["true_source_goal"] for r in items),
      "mean_real_reward":sum(r["actual_original_reward_sum"] for r in items)/len(items),
      "actual_turn_loops":sum(r["real_inverted_turn_pairs_at_same_pose"] for r in items),
      "actually_executed_options":sum(r["actual_two_step_option_starts"] for r in items)}
 return result

def evaluate(fitdir):
 prereg()
 from research.mass_r7c20 import run as c20
 c20.check_source()
 FIT,motors=read_C35_fit(fitdir)
 model=CausalOptions(FIT,motors)
 records=[episode(fam,seed,arm,model)
  for arm in ARMS
  for fam,seeds in P["new_original_public_development_worlds"].items()
  for seed in seeds]
 summary=summarize(records)
 native=summary["native_veto"];r3=summary["original_r3"]
 shuffle=summary["shuffled_veto"];no=summary["native_no_veto"]
 strong=max((summary[k] for k in ("ridge_veto","ridge_no_veto",
     "FIT_motor_goal_heuristic_veto")),key=lambda x:(x["mean_real_reward"],x["goals"]))
 different=sum(
   next(x for x in records if x["arm"]=="native_veto" and x["family"]==fam and x["seed"]==seed)["original_trace_sha256"]!=
   next(x for x in records if x["arm"]=="shuffled_veto" and x["family"]==fam and x["seed"]==seed)["original_trace_sha256"]
   for fam,seeds in P["new_original_public_development_worlds"].items() for seed in seeds)
 c=P["preregAccept"]
 check={
  "same_24_original_worlds_per_arm":all(v["worlds"]==24 for v in summary.values()),
  "native_real_options_executed":native["actual_overrides"]>=c["nativeActuallyOverridesAtLeast"],
  "family_specific_native_goal_nonregression":all(native["by_family"][fam]["goals"]>=r3["by_family"][fam]["goals"] for fam in P["new_original_public_development_worlds"]),
  "native_mean_return_vs_original_R3":native["mean_real_reward"]-r3["mean_real_reward"]>=c["nativeMeanRealRewardVsR3AtLeast"],
  "native_mean_return_vs_shuffled":native["mean_real_reward"]-shuffle["mean_real_reward"]>=c["nativeMeanRealRewardVsShuffledVetoAtLeast"],
  "native_mean_return_vs_strongest_conventional":native["mean_real_reward"]-strong["mean_real_reward"]>=c["nativeMeanRealRewardVsStrongestConventionalAtLeast"],
  "actual_loop_veto_contribution":native["mean_real_reward"]-no["mean_real_reward"]>=c["nativeMeanRealRewardVsNativeNoVetoAtLeast"],
  "source_trajectory_distinction_vs_shuffle":different>=c["atLeastFourNativeVsShuffledPhysicallyDistinctEpisodeTrajectories"],
  "native_collision_nonregression":native["collisions"]<=r3["collisions"],
  "cold_independent_OS_after_real_step3":all(r["real_step3_process_cold"]["cold_OS_source_policy_parity"] for r in records)
 }
 return {"schema":SCHEMA,
  "scientific_result":c["positive"] if all(check.values()) else c["noGo"],
  "criteria":check,"factorial_source_actor_summaries":summary,
  "actual_native_vs_shuffled_source_trajectory_differences":different,
  "original_source_true_physical_actor_episodes":records,
  "FIT_trained_two_action_original_forks":model.fitted,
  "original_FIT_model_sha256":model.model_sha,
  "precommitted_protocol_sha256":hashlib.sha256((HERE/"PREREG.json").read_bytes()).hexdigest(),
  "original_R3_source_modified":False,
  "first_use":False,"scientific_accepted":False}

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--c35-fit-dir",type=Path,required=True)
 p.add_argument("--output",type=Path,required=True)
 a=p.parse_args()
 if a.output.exists() or not a.output.parent.is_dir():
  raise ValueError("C37_ORIGINAL_SOURCE_OUTPUT_MUST_BE_FRESH")
 start=time.perf_counter();cpu=time.process_time()
 r=evaluate(a.c35_fit_dir)
 r["resource_observation"]={"whole_source_wall_seconds":time.perf_counter()-start,
  "parent_python_CPU_seconds":time.process_time()-cpu,
  "parent_RSS_peak_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss if resource else None,
  "child_cold_process_total_CPU_not_covered":True,"energy_measured":False}
 a.output.write_bytes(canonical(r)+b"\n")
 print("C37_ORIGINAL_SOURCE_FACTORIAL_RESULT="+r["scientific_result"])
 print("C37_ACTUAL_FACTORIAL_PUBLIC_WORLDS="+json.dumps(r["factorial_source_actor_summaries"],sort_keys=True))
 print("C37_PREREGISTERED_CAUSAL_GATES="+json.dumps(r["criteria"],sort_keys=True))
if __name__=="__main__":main()
