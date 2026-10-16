"""F67 prospective teacher, synthetic-only pre-registered public training.

Teacher may examine later public TRAIN arrivals offline only. Frozen online
durable policy never receives later events, future questions or private tags.
"""
from __future__ import annotations
import hashlib,importlib.util,json,math,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes();return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert blob(P/"prereg-teacher.json")=="5d0fdf772b8e7db6a1166174b624cac8a9a8215e"
assert blob(P/"durable_policy.py")=="21f2f3fc90a3d00d09029f39e4958e09a33908cc"
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
POLICY=load("f67_frozen_durable_online",P/"durable_policy.py")
CONTRACT=json.loads((P/"prereg-teacher.json").read_text())
CO=CONTRACT["teacher_coefficients"]
def choices(memory,event,index):
 offered=POLICY.BASE.actions(memory,event,index,POLICY.PACK)
 candidates=[]
 seen=set()
 for j,(action,_old,_drop,after,_old_features) in enumerate(offered):
  options=[after]
  options.extend(after[:k]+after[k+1:] for k,r in enumerate(after) if len(r[2])<4)
  for k,outcome in enumerate(options):
   if not POLICY.is_admissible(memory,outcome) or outcome in seen:continue
   seen.add(outcome)
   candidates.append((action,outcome,POLICY.features(memory,event,action,outcome,index)))
 if not candidates:
  assert POLICY.is_admissible(memory,memory)
  candidates=[("reject",memory,POLICY.features(memory,event,"reject",memory,index))]
 return candidates
def offline_teacher_utility(after,later):
 inc={}
 for a,_role,b in later:
  inc[a]=inc.get(a,0)+1
  inc[b]=inc.get(b,0)+1
 endpoints={n for rec in after for n in rec[:2]}
 strong=sum(len(rec[2])**2 for rec in after)/36
 long=sum(len(rec[2])>=4 for rec in after)
 short=len(after)-long
 future_support=sum(min(2,inc.get(n,0)) for n in endpoints)/12
 diversity=len({c for r in after for c in r[2]})/8
 return (CO["role_path_squared_length"]*strong
  +CO["stable_long_record_count"]*long
  +CO["future_public_endpoint_incidence"]*future_support
  +CO["frontier_record_cost"]*short
  +CO["role_code_diversity"]*diversity)
def collect(public):
 assert len(public)==72 and all(len(e)==3 for e in public)
 samples=[]
 teacher_merges=0
 state=()
 for i,event in enumerate(public):
  candidates=choices(state,event,i)
  future=public[i+1:]  # OFFLINE TRAIN ONLY
  rated=[(offline_teacher_utility(after,future),-j,action,after,feat)
      for j,(action,after,feat) in enumerate(candidates)]
  best=max(rated,key=lambda x:(x[0],x[1]))
  best_utility=best[0]
  for util,_tie,action,_after,feats in rated[:32]:
   if util>=best_utility-1e-8:continue
   diff=tuple(a-b for a,b in zip(best[4],feats))
   if not any(abs(x)>1e-9 for x in diff):continue
   target=min(1,max(0,8*(best_utility-util)))
   samples.append((diff,target))
  teacher_merges+=int(best[2]=="merge")
  state=best[3]
 assert len(samples)>0
 return samples,teacher_merges
def fit(public_cases):
 samples=[];teacher_merges=0
 for case in public_cases:
  data,merges=collect(case)
  samples.extend(data);teacher_merges+=merges
 weights=[0.0]*POLICY.PARAMS
 for _epoch in range(CONTRACT["training"]["epochs"]):
  for diffs,target in samples:
   pred=math.tanh(sum(w*x for w,x in zip(weights,diffs)))
   for i,x in enumerate(diffs):
    weights[i]+=CONTRACT["training"]["SGD_step"]*(target-pred)*x
 quant=tuple(max(-127,min(127,round(w*32))) for w in weights)
 assert len(quant)==POLICY.PARAMS
 return quant,dict(examples=len(samples),teacher_merges=teacher_merges)
def synthetic():
 cases=[POLICY.SRC.source(-2801-i,(-2,-1)[i%2])[0] for i in range(8)]
 weights,training=fit(cases)
 rows=[]
 for i in range(8):
  seed=-2821-i;family=(-2,-1)[i%2]
  public,q,meta=POLICY.SRC.source(seed,family)
  learned,trace,merges=POLICY.online(public,weights,True,True)
  claim=POLICY.BUDGET_AUDIT.verify(public,q,trace)
  assert claim["prefixes"]==72 and claim["max_payload_bytes"]<=144
  assert sum(len(r[2])>=4 for r in learned)<=8
  rows.append(dict(seed=seed,family=family,kind=meta["question_type"],
     learned_merges=merges,durable_paths=sum(len(r[2])>=4 for r in learned),
     model_correct=int(POLICY.PACK.solve(learned,q)==q["answer"])))
 return dict(schema="yggdrasil.f67.future-public-durable.synthetic-train.v1",
  stage="SYNTHETIC_ONLY",synthetic_train_cases=len(cases),
  independent_guard_cases=len(rows),training=training,
  fitted_synthetic_weights=list(weights),
  model_merges=sum(r["learned_merges"] for r in rows),
  durable_final_paths=sum(r["durable_paths"] for r in rows),
  genuine_learned_policy_preflight_qualified=(sum(r["learned_merges"] for r in rows)>0
       and sum(r["durable_paths"] for r in rows)>0),
  FIT_train_executed=False,FIT_validate_executed=False,diag_executed=False,
  original_executed=False,F3=False,rows=rows)
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 print(json.dumps(synthetic(),sort_keys=True))
