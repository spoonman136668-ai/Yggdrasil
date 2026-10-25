"""C36 -- FIT-frozen genuine two-action causal options on real original worlds.

No native R3 edits. Every policy has a separately reset original source world.
The learned controller never observes future truth or a privileged source map.
"""
import argparse,collections,hashlib,json,math,os,subprocess,sys,time,zipfile
from pathlib import Path
try:
 import resource
except ImportError:
 resource=None
import numpy as np
from research.native.itd02.r1.native_policy import canonical
from research.native.itd02.r3.navigator import Navigator

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
P=json.loads((HERE/"PREREG.json").read_text())
ARMS=P["arms"]
PAIRS=((0,2),(1,2),(2,2))
SCHEMA=P["schema"]
FIT_ROLE="source_original_fit_real_two_action_forks"
FULL_FIELDS={"x","y","direction","goal_x","goal_y","front_blocked"}

def sha(x):return hashlib.sha256(canonical(x)).hexdigest()

def prereg():
 if (SCHEMA!="itd02.c36.actual-source-fit-two-step-commit-policy-v1"
    or P["parentC35"]!="cc2f53e507e62f3095fb09e04399e7e7d335a6bd"
    or P["trainOnly"]["expectedTruePairActions"]!=279
    or P["mechanism"]["minimumPredictedAdvantageOverR3Option"]!=.5
    or P["mechanism"]["minimumPredictedGoalProgressToCommit"]!=.5
    or P["mechanism"]["requireAtLeastFITContextCount"]!=2
    or P["limitations"]["notProtectedFirstUse"] is not True):
  raise ValueError("C36_FROZEN_SOURCE_POLICY_DRIFT")

def read_C35_fit(folder):
 prereg()
 path=Path(folder)
 a=json.loads((path/"process-a.json").read_bytes())
 b=json.loads((path/"process-b.json").read_bytes())
 for r in (a,b):r.pop("resources",None)
 if canonical(a)!=canonical(b):
  raise ValueError("C36_AUTHENTIC_FIT_ORIGINAL_PRODUCERS_DISAGREE")
 if (a["schema"]!="itd02.c35.prospective-real-two-action-source-effect-v1"
    or a["result"]!="NO_C35_TWO_STEP_CAUSAL_SOURCE_EFFECT_PREDICTIVE_ADVANTAGE"
    or len(a[FIT_ROLE])!=31
    or a["FIT_source_original_fitted_intervention_pairs"]!=279):
  raise ValueError("C36_UNQUALIFIED_ORIGINAL_C35_DATA")
 rows=a[FIT_ROLE]
 motors=collections.defaultdict(collections.Counter)
 for row in rows:
  for pair in row["all_nine_original_physical_pairs"].values():
   if not pair["completed_two_original_actions"]:
    raise ValueError("C36_UNEXECUTED_SOURCE_PAIR_USED_AS_FIT")
   for event in pair["actual_selected_source_actions"]:
    s=event["before"];n=event["after"]
    if set(s)!=FULL_FIELDS or set(n)!=FULL_FIELDS:
     raise ValueError("C36_PRIVATE_FIT_GRID_EXPOSED")
    if event["action"]==2:
     dx=n["x"]-s["x"];dy=n["y"]-s["y"]
     if abs(dx)+abs(dy)==1:motors[s["direction"]][(dx,dy)]+=1
 if set(motors)!=set(range(4)):
  raise ValueError("C36_SOURCE_LEARNED_MOTOR_INCOMPLETE")
 return rows,{str(d):{f"{dx},{dy}":n for (dx,dy),n in motors[d].items()} for d in range(4)}

def feature(row,pair):
 s=row["public_initial"]
 if set(s)!=FULL_FIELDS:raise ValueError("C36_PRIVATE_MODEL_INPUT")
 vals=[1.,float(row["family"]=="MiniGrid-Dynamic-Obstacles-8x8-v0"),
   s["x"]/20.,s["y"]/20.,
   max(-8,min(8,s["goal_x"]-s["x"]))/8.,
   max(-8,min(8,s["goal_y"]-s["y"]))/8.]
 vals.extend(float(s["direction"]==d) for d in range(4))
 vals.append(float(s["front_blocked"]))
 vals.extend(float(pair==x) for x in PAIRS)
 return vals

class CausalOptions:
 def __init__(self,fit,motors):
  prior=collections.defaultdict(lambda:[0.,0])
  conditional=collections.defaultdict(lambda:[0.,0])
  self.motors=motors
  x=[];y=[]
  for row in fit:
   fam=row["family"];pub=row["public_initial"]
   if set(row["all_nine_original_physical_pairs"])!={f"{a}{b}" for a in range(3) for b in range(3)}:
    raise ValueError("C36_INCOMPLETE_FIT_SOURCE_PAIRS")
   for pair in PAIRS:
    e=row["all_nine_original_physical_pairs"][str(pair[0])+str(pair[1])]
    if not e["completed_two_original_actions"] or [v["action"] for v in e["actual_selected_source_actions"]]!=list(pair):
     raise ValueError("C36_IMPUTED_SOURCE_OPTION")
    gain=e["real_two_step_goal_distance_improvement"]
    if not math.isfinite(gain) or abs(gain)>100:
     raise ValueError("C36_ILLEGAL_SOURCE_CAUSAL_PROGRESS")
    z=prior[(fam,*pair)];z[0]+=gain;z[1]+=1
    k=(fam,pub["direction"],int(pub["front_blocked"]),*pair)
    zz=conditional[k];zz[0]+=gain;zz[1]+=1
    x.append(feature(row,pair));y.append(gain)
  self.prior=dict(prior);self.conditional=dict(conditional)
  X=np.array(x);Y=np.array(y)
  reg=np.eye(X.shape[1])*P["mechanism"]["frozenRidgePenalty"]
  reg[0,0]=0
  self.ridge=np.linalg.solve(X.T@X+reg,X.T@Y).tolist()
  self.fitted=len(y)
  self.model_sha=sha({"prior":[[list(k),v] for k,v in sorted(self.prior.items())],
     "condition":[[list(k),v] for k,v in sorted(self.conditional.items())],"ridge":self.ridge,"motors":motors})

 def snapshot(self):
  return {"prior":[[list(k),v] for k,v in sorted(self.prior.items())],
   "condition":[[list(k),v] for k,v in sorted(self.conditional.items())],
   "ridge":self.ridge,"motors":self.motors,"fitted":self.fitted,"model_sha":self.model_sha}

 @classmethod
 def from_snapshot(cls,data):
  if not isinstance(data,dict) or set(data)!={"prior","condition","ridge","motors","fitted","model_sha"}:
   raise ValueError("C36_COLD_MODEL_SCHEMA")
  out=cls.__new__(cls)
  out.prior={tuple(k):v for k,v in data["prior"]}
  out.conditional={tuple(k):v for k,v in data["condition"]}
  out.ridge=data["ridge"];out.motors=data["motors"];out.fitted=data["fitted"];out.model_sha=data["model_sha"]
  if sha({k:v for k,v in data.items() if k!="model_sha"})!=data["model_sha"]:
   # original hash omits fitted count; recompute exactly as in constructor
   got=sha({"prior":data["prior"],"condition":data["condition"],"ridge":data["ridge"],"motors":data["motors"]})
   if got!=data["model_sha"]:raise ValueError("C36_TAMPERED_CAUSAL_MODEL")
  return out

 def predict(self,fam,pub,pair,mode):
  if set(pub)!=FULL_FIELDS or pair not in PAIRS:
   raise ValueError("C36_NONPUBLIC_OPTION")
  row={"family":fam,"public_initial":pub}
  pr=self.prior.get((fam,*pair),[0.,0])
  if pr[1]==0:raise ValueError("C36_UNTRAINED_OPTION")
  p0=pr[0]/pr[1]
  if mode=="trained_conventional_ridge_two_step":
   return sum(v*w for v,w in zip(feature(row,pair),self.ridge)),pr[1]
  if mode=="shuffled_effect_control":
   pair=((pair[0]+1)%3,pair[1])
  local=self.conditional.get((fam,pub["direction"],int(pub["front_blocked"]),*pair),[0.,0])
  smooth=P["mechanism"]["shrinkageSourceObservations"]
  return (local[0]+smooth*p0)/(local[1]+smooth),local[1]

def make_nav(motors,dims):
 nav=Navigator()
 nav.motor={str(d):dict(motors[str(d)]) for d in range(4)}
 nav.reset_episode(*dims)
 return nav

def source_front(nav,s):
 if s.front_blocked:
  nav.blocked.add((s.x,s.y,s.direction))
  nav.open_edges.discard((s.x,s.y,s.direction))
 else:
  nav.blocked.discard((s.x,s.y,s.direction))

def choose_action(nav,model,fam,s,arm,last_action,last_pose,pending):
 source_front(nav,s)
 r3=nav.choose(s)
 if r3 not in (0,1,2):raise ValueError("C36_INVALID_R3")
 if pending and not s.front_blocked:
  return r3,2,False,True
 if arm=="original_r3" or r3==2:
  return r3,r3,False,False
 original,_=model.predict(fam,s.__dict__,(r3,2),arm)
 other=1-r3
 alternative,n=model.predict(fam,s.__dict__,(other,2),arm)
 if n<P["mechanism"]["requireAtLeastFITContextCount"]:
  return r3,r3,False,False
 if (arm!="no_memory_ablation" and last_pose==(s.x,s.y) and
     last_action==1-other):
  return r3,r3,False,False
 if (alternative-original>=P["mechanism"]["minimumPredictedAdvantageOverR3Option"] and
     alternative>=P["mechanism"]["minimumPredictedGoalProgressToCommit"]):
  return r3,other,True,False
 return r3,r3,False,False

def cold_validate(nav,model,fam,pub,arm,last_action,last_pose,pending):
 import copy
 tmp=copy.deepcopy(nav)
 predicted=choose_action(tmp,model,fam,pub,arm,last_action,last_pose,pending)[:2]
 payload={"nav":nav.snapshot().decode(),"model":model.snapshot(),
     "pub":pub.__dict__,"fam":fam,"arm":arm,
     "last_action":last_action,"last_pose":last_pose,"pending":pending,
     "predicted":predicted}
 child="""import json,sys
from research.native.itd02.r1.native_policy import PublicGrid
from research.native.itd02.r3.navigator import Navigator
from research.mass_r7c36.run import CausalOptions,choose_action
x=json.loads(sys.stdin.read())
n=Navigator.restore(x['nav'].encode())
m=CausalOptions.from_snapshot(x['model'])
p=PublicGrid(**x['pub'])
assert list(choose_action(n,m,x['fam'],p,x['arm'],x['last_action'],tuple(x['last_pose']) if x['last_pose'] is not None else None,x['pending'])[:2])==x['predicted']
print('C36_TRUE_EPISODE_FRESH_OS_CAUSAL_CHECKPOINT=PASS')
"""
 z=subprocess.run([sys.executable,"-B","-c",child],
      input=json.dumps(payload),capture_output=True,text=True,cwd=ROOT,
      env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1","OPENBLAS_NUM_THREADS":"1"},timeout=30)
 if z.returncode or "C36_TRUE_EPISODE_FRESH_OS_CAUSAL_CHECKPOINT=PASS" not in z.stdout:
  raise ValueError("C36_COLD_ORIGINAL_NAV_AND_CAUSAL_OPTION_NOT_RESTORED:"+z.stderr[-600:])
 return {"fresh_os":True,"R3_bytes":len(payload["nav"]),"causal_model_bytes":len(canonical(payload["model"]))}

def episode(fam,seed,arm,model):
 from research.mass_r7c20 import run as c20
 from research.mass_r7c22 import run as c22
 env=c20.env_make(fam)
 try:
  obs,_=env.reset(seed=seed);goal=c20.goal_from(obs)
  dims=tuple(int(x) for x in obs["image"].shape[:2])
  nav=make_nav(model.motors,dims)
  steps=[];last_action=None;last_pose=None;pending=False;changed=0;cold=None
  for tick in range(P["maxSourceActions"]):
   s=c22.public_dynamic(obs,goal)
   baseline,action,commit,executed_pending=choose_action(nav,model,fam,s,arm,last_action,last_pose,pending)
   if action not in (0,1,2):raise ValueError("C36_INVALID_SOURCE_SELECTED_ACTION")
   before=s.__dict__.copy()
   nxt,reward,terminal,trunc,_=env.step(action)
   after=c22.public_dynamic(nxt,goal)
   nav.observe(s,action,after,float(reward),bool(terminal),False)
   if action!=baseline:changed+=1
   steps.append({"t":tick,"before":before,"R3_proposed":baseline,
      "real_selected":action,"real_after":after.__dict__.copy(),
      "reward":float(reward),"terminal":bool(terminal),"trunc":bool(trunc),
      "two_step_option_started":commit,"option_second_action":executed_pending})
   last_action=action;last_pose=(s.x,s.y)
   pending=bool(commit and not (terminal or trunc))
   if executed_pending:pending=False
   obs=nxt
   if tick==2 and not (terminal or trunc):
    cold=cold_validate(nav,model,fam,after,arm,last_action,last_pose,pending)
   if terminal or trunc:break
  if cold is None:
   cold=cold_validate(nav,model,fam,c22.public_dynamic(obs,goal),arm,last_action,last_pose,pending)
  done=steps[-1]
  return {"family":fam,"seed":seed,"arm":arm,"actual_source_steps":len(steps),
     "real_goal":bool(done["terminal"] and done["reward"]>0),
     "real_collision":bool(done["terminal"] and done["reward"]<0),
     "real_horizon":bool(done["trunc"]),
     "real_reward":sum(v["reward"] for v in steps),
     "actually_executed_overrides":changed,
     "real_true_source_actions":steps,"trace_sha256":sha(steps),
     "R3_checkpoint_sha256":hashlib.sha256(nav.snapshot()).hexdigest(),
     "checkpoint_cold":cold}
 finally:env.close()

def evaluate(folder):
 prereg()
 from research.mass_r7c20 import run as c20
 c20.check_source()
 rows,motors=read_C35_fit(folder)
 model=CausalOptions(rows,motors)
 result=[]
 for arm in ARMS:
  for fam,seeds in P["freshPublicEpisodeEvaluation"].items():
   for seed in seeds:
    result.append(episode(fam,seed,arm,model))
 by={}
 for arm in ARMS:
  r=[e for e in result if e["arm"]==arm]
  by[arm]={"episodes":len(r),"real_goals":sum(e["real_goal"] for e in r),
    "real_collisions":sum(e["real_collision"] for e in r),
    "real_horizons":sum(e["real_horizon"] for e in r),
    "real_source_actions":sum(e["actual_source_steps"] for e in r),
    "real_average_reward":sum(e["real_reward"] for e in r)/len(r),
    "real_overrides":sum(e["actually_executed_overrides"] for e in r)}
 native=by["causal_two_step"];r3=by["original_r3"];other=by["trained_conventional_ridge_two_step"]
 c=P["criteria"]
 checks={"episodes_equal_by_arm":all(v["episodes"]==8 for v in by.values()),
  "native_executed_real_options":native["real_overrides"]>=c["minPhysicallyExecutedNativeTurnOptionOverrides"],
  "native_goals_not_worse_than_r3":native["real_goals"]>=r3["real_goals"]+c["minNativeGoalsOverOriginalR3"],
  "native_goals_not_worse_than_conventional":native["real_goals"]>=other["real_goals"]+c["minNativeGoalsOverBestConventional"],
  "native_source_reward_gain_over_R3":native["real_average_reward"]-r3["real_average_reward"]>=c["minNativeActualMeanSourceRewardGainOverR3"],
  "native_source_reward_gain_over_conventional":native["real_average_reward"]-other["real_average_reward"]>=c["minNativeActualMeanSourceRewardGainOverBestConventional"],
  "no_more_native_collision_terminals":native["real_collisions"]<=r3["real_collisions"],
  "all_real_episodes_cold_restored":all(e["checkpoint_cold"]["fresh_os"] for e in result)}
 return {"schema":SCHEMA,"gate":"ITD02-C36",
    "result":c["positive"] if all(checks.values()) else c["noGo"],
    "criteria":checks,"actual_source_actor_summary":by,
    "genuine_original_source_episode_trajectories":result,
    "original_source_C35_FIT_fork_count":model.fitted,
    "FIT_only_model_sha256":model.model_sha,
    "source_prereg_sha256":hashlib.sha256((HERE/"PREREG.json").read_bytes()).hexdigest(),
    "fully_executed_true_actions":True,"native_R3_original_unchanged":True,
    "first_use":False,"science_accepted":False}
def main():
 pa=argparse.ArgumentParser()
 pa.add_argument("--c35-fit-dir",required=True)
 pa.add_argument("--output",type=Path,required=True)
 x=pa.parse_args()
 if x.output.exists() or not x.output.parent.is_dir():
  raise ValueError("C36_NONFRESH_RESULT")
 start=time.perf_counter();cpu=time.process_time()
 v=evaluate(x.c35_fit_dir)
 v["resources"]={"python_parent_CPU_seconds":time.process_time()-cpu,
  "source_wall_seconds":time.perf_counter()-start,
  "parent_peak_RSS_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss if resource else None,
  "fresh_OS_child_cpu_not_measured":True,"energy_measured":False}
 x.output.write_bytes(canonical(v)+b"\n")
 print("C36_REAL_ORIGINAL_SOURCE_POLICY="+v["result"],flush=True)
 print("C36_ALL_ACTUAL_SOURCE_ARM_RESULTS="+json.dumps(v["actual_source_actor_summary"],sort_keys=True),flush=True)
 print("C36_FROZEN_POLICY_GATES="+json.dumps(v["criteria"],sort_keys=True),flush=True)
if __name__=="__main__":main()
