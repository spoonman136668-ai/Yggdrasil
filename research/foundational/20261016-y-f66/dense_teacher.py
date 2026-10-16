"""Y-F66 dense public-graph continuation teacher: synthetic-only qualification.

The offline teacher observes *future public edges* only on FIT TRAIN.
The learned online two-head controller is causal and cannot read future
public events, hidden labels, future questions, DIAG or originals.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,math,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert blob(P/"prereg.json")=="fc3283f28ab307b6834c93d530fffce98ad7c0de"
assert blob(P/"two_head_continuation.py")=="fa08d72d79380a82814c86482e98b206b69b4d4a"
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
 return m
POLICY=load("f66_frozen_two_head_online",P/"two_head_continuation.py")
def teacher_future_public_utility(records,later_public):
 """Unfair offline TRAIN-only lookahead: public graph, never hidden query."""
 degrees={}
 for a,_role,b in later_public:
  degrees[a]=degrees.get(a,0)+1
  degrees[b]=degrees.get(b,0)+1
 total=0.
 for start,end,codes in records:
  length=len(codes)
  future_hubs=min(4,degrees.get(start,0)+degrees.get(end,0))/4
  total+=(length*length/36)*(1+future_hubs/2)
 return total/12
def candidate_group(memory,event,index,public_later):
 options=POLICY.ACTION.actions(memory,event,index,POLICY.PACK)
 best={}
 for j,(action,_old,drop,after,_ignored) in enumerate(options):
  utility=teacher_future_public_utility(after,public_later)
  key=(utility,-j)
  if action not in best or key>best[action][0]:
   best[action]=(key,after,drop,index,action)
 return best,options
def supervised_case(public):
 assert len(public)==72 and all(len(x)==3 for x in public)
 gate_examples=[]
 rank_examples=[]
 positives=negatives=0
 mem=()
 for index,event in enumerate(public):
  following=public[index+1:]   # OFFLINE TRAIN ONLY, NEVER ONLINE
  best,options=candidate_group(mem,event,index,following)
  if "merge" in best:
   mg=best["merge"]
   ap=best["append"]
   gf=POLICY.gate_features(mem,mg[1],ap[1],event,index)
   udelta=mg[0][0]-ap[0][0]
   target=max(-1,min(1,udelta*8))
   if udelta>1e-8:positives+=1
   if udelta< -1e-8:negatives+=1
   gate_examples.append((gf,target))
  # Dense retention comparisons against the strongest *within-action*
  # teacher candidate; avoids leaking the teacher's future at runtime.
  for action in ("append","merge"):
   if action not in best:continue
   anchor=best[action]
   teacher_features=POLICY.rank_features(anchor[1],action,anchor[2],index,len(mem))
   for a,_old,drop,after,_f in options:
    if a!=action or after==anchor[1]:continue
    f=POLICY.rank_features(after,a,drop,index,len(mem))
    delta=tuple(x-y for x,y in zip(teacher_features,f))
    utility_gap=anchor[0][0]-teacher_future_public_utility(after,following)
    target=max(-1,min(1,utility_gap*8))
    if any(abs(z)>1e-10 for z in delta):
     rank_examples.append((delta,target))
  mem=POLICY.ACTION._f60_step(mem,event,POLICY.PACK)
 return gate_examples,rank_examples,positives,negatives
def train(public_cases):
 gate=[];rank=[];positive=negative=0
 for public in public_cases:
  g,r,p,n=supervised_case(public)
  gate.extend(g);rank.extend(r);positive+=p;negative+=n
 assert len(gate)>0 and len(rank)>0 and positive>0 and negative>0,"DENSE_TEACHER_NO_BALANCED_ACTION_EVIDENCE"
 gw=[0.0]*POLICY.GATE_PARAMS
 rw=[0.0]*POLICY.RANK_PARAMS
 for _ in range(3):
  for x,t in gate:
   score=math.tanh(sum(w*val for w,val in zip(gw,x)))
   for j,v in enumerate(x):gw[j]+=.03*(t-score)*v
  for x,t in rank:
   score=math.tanh(sum(w*val for w,val in zip(rw,x)))
   for j,v in enumerate(x):rw[j]+=.01*(t-score)*v
 weights=tuple(max(-127,min(127,round(w*32))) for w in gw+rw)
 assert len(weights)==POLICY.TOTAL_PARAMS
 return weights,dict(gate_examples=len(gate),rank_examples=len(rank),
                     teacher_merge_positive=positive,teacher_merge_negative=negative)
def synthetic_guard():
 train_public=[]
 for i in range(8):
  seed=-1901-i;family=(-2,-1)[i%2]
  public,_q,_meta=POLICY.SOURCE.source(seed,family)
  train_public.append(public)
 weights,stats=train(train_public)
 guards=[]
 for i in range(4):
  seed=-1911-i;family=(-2,-1)[i%2]
  public,q,meta=POLICY.SOURCE.source(seed,family)
  kept,trace,merges=POLICY.online(public,weights,True)
  proof=POLICY.AUDITOR.verify(public,q,trace)
  assert proof["prefixes"]==72 and proof["max_payload_bytes"]<=144
  disabled,other,other_merges=POLICY.online(public,weights,True,False)
  assert POLICY.AUDITOR.verify(public,q,other)["prefixes"]==72
  guards.append(dict(seed=seed,kind=meta["question_type"],learned_merges=merges,
    ablation_merges=other_merges,learned_correct=int(POLICY.PACK.solve(kept,q)==q["answer"])))
 selected=sum(x["learned_merges"] for x in guards)
 return dict(schema="yggdrasil.f66.dense-public-teacher.synthetic-qualification.v1",
  stage="UNREGISTERED_SYNTHETIC_ONLY",synthetic_fit_cases=len(train_public),
  guard_cases=len(guards),teacher_counts=stats,
  synthetic_frozen_weights=list(weights),learned_merge_steps=selected,
  model_synthetic_merge_qualified=selected>0,
  actual_FIT_train_executed=False,heldout_executed=False,
  DIAG_executed=False,original_executed=False,F3=False,guards=guards)
if __name__=="__main__":
 parser=argparse.ArgumentParser()
 parser.add_argument("--synthetic-only",action="store_true")
 args=parser.parse_args()
 if not args.synthetic_only:raise SystemExit("F66 source method is synthetic-only; registered FIT requires a separate authorized frozen entrypoint")
 print(json.dumps(synthetic_guard(),sort_keys=True))
