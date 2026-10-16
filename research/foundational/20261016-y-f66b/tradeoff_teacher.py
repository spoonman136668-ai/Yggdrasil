"""F66B prospective offline public-continuation teacher, synthetic engineering.

Uses frozen two-head ONLINE policy unchanged. Future public observations are
seen only inside offline TRAIN labels. No protected registered data permitted.
"""
from __future__ import annotations
import hashlib,importlib.util,json,math,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert blob(HERE/"prereg.json")=="551644239204be97cdb5944b7108d9ecca82c709"
def load(name,path,expected):
 assert blob(path)==expected,(name,"PINNED_BLOB_DRIFT")
 sp=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(sp);sys.modules[name]=m;sp.loader.exec_module(m);return m
POLICY=load("f66b_frozen_deployed_two_head",HERE.parent/"20261016-y-f66"/"two_head_continuation.py",
 "fa08d72d79380a82814c86482e98b206b69b4d4a")
OLD=load("f66b_original_invalid_teacher",HERE.parent/"20261016-y-f66"/"dense_teacher.py",
 "4924a409a446403c0c2a5d1e146adc8171ae4791")
def public_teacher_value(records,future_public):
 assert all(len(e)==3 for e in future_public)
 incidence={}
 for a,_role,b in future_public:
  incidence[a]=incidence.get(a,0)+1
  incidence[b]=incidence.get(b,0)+1
 endpoints={n for rec in records for n in rec[:2]}
 compressed=sum(len(r[2])**2 for r in records)
 attachment=sum(min(2,incidence.get(n,0)) for n in endpoints)
 flexibility=len(endpoints)
 return (0.18*compressed+0.55*attachment+0.28*flexibility)/12
def samples_for_one(public):
 assert len(public)==72 and all(len(e)==3 for e in public)
 gate=[];rank=[];positive=negative=neutral=0
 memory=()
 for i,event in enumerate(public):
  later=public[i+1:] # offline FIT TRAIN teacher only
  options=POLICY.ACTION.actions(memory,event,i,POLICY.PACK)
  per_action={}
  for j,(action,_old,drop,after,_old_features) in enumerate(options):
   utility=public_teacher_value(after,later)
   key=(utility,-j)
   if action not in per_action or key>per_action[action][0]:
    per_action[action]=(key,after,drop)
  if "merge" in per_action:
   mg=per_action["merge"];ap=per_action["append"]
   gf=POLICY.gate_features(memory,mg[1],ap[1],event,i)
   advantage=mg[0][0]-ap[0][0]
   target=max(-1,min(1,advantage*8))
   gate.append((gf,target))
   if advantage>1e-9:positive+=1
   elif advantage< -1e-9:negative+=1
   else:neutral+=1
  for action in ("append","merge"):
   if action not in per_action:continue
   best=per_action[action]
   best_f=POLICY.rank_features(best[1],action,best[2],i,len(memory))
   for candidate,_old,drop,after,_old_features in options:
    if candidate!=action or after==best[1]:continue
    new_f=POLICY.rank_features(after,action,drop,i,len(memory))
    delta=tuple(a-b for a,b in zip(best_f,new_f))
    if any(abs(x)>1e-10 for x in delta):
     advantage=best[0][0]-public_teacher_value(after,later)
     rank.append((delta,max(-1,min(1,advantage*8))))
  memory=POLICY.ACTION._f60_step(memory,event,POLICY.PACK)
 return gate,rank,positive,negative,neutral
def fit(public_cases):
 gate=[];rank=[];pos=neg=neutral=0
 for public in public_cases:
  g,r,p,n,z=samples_for_one(public)
  gate+=g;rank+=r;pos+=p;neg+=n;neutral+=z
 assert len(gate)>0 and len(rank)>0
 assert pos>0 and neg>0,"F66B_NO_BALANCED_PROSPECTIVE_PUBLIC_LABELS"
 weights_gate=[0.]*POLICY.GATE_PARAMS
 weights_rank=[0.]*POLICY.RANK_PARAMS
 for _ in range(3):
  for features,target in gate:
   prediction=math.tanh(sum(w*f for w,f in zip(weights_gate,features)))
   for j,f in enumerate(features):weights_gate[j]+=.03*(target-prediction)*f
  for features,target in rank:
   prediction=math.tanh(sum(w*f for w,f in zip(weights_rank,features)))
   for j,f in enumerate(features):weights_rank[j]+=.01*(target-prediction)*f
 weights=tuple(max(-127,min(127,round(w*32))) for w in weights_gate+weights_rank)
 assert len(weights)==POLICY.TOTAL_PARAMS
 return weights,dict(merge_labels_positive=pos,merge_labels_negative=neg,
   merge_labels_neutral=neutral,gate_examples=len(gate),rank_examples=len(rank))
def synthetic_guard():
 training=[POLICY.SOURCE.source(-2001-i,(-2,-1)[i%2])[0] for i in range(8)]
 weights,stats=fit(training)
 guards=[]
 for i in range(4):
  seed=-2021-i;family=(-2,-1)[i%2]
  public,q,metadata=POLICY.SOURCE.source(seed,family)
  kept,trace,merges=POLICY.online(public,weights,True)
  assert POLICY.AUDITOR.verify(public,q,trace)["prefixes"]==72
  disabled,abl_trace,abl_merges=POLICY.online(public,weights,True,False)
  assert POLICY.AUDITOR.verify(public,q,abl_trace)["prefixes"]==72
  guards.append(dict(seed=seed,kind=metadata["question_type"],
       merges=merges,ablated_merges=abl_merges,
       accurate=int(POLICY.PACK.solve(kept,q)==q["answer"])))
 return dict(schema="yggdrasil.f66b.synthetic-tradeoff-training.v1",
   stage="UNREGISTERED_SYNTHETIC_ONLY",train_cases=len(training),guards=guards,
   teacher=stats,synthetic_weights=list(weights),
   learned_merges=sum(r["merges"] for r in guards),
   positive_trained_merge_action_test=sum(r["merges"] for r in guards)>0,
   fit_train_executed=False,heldout_executed=False,original_executed=False,F3=False)
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 print(json.dumps(synthetic_guard(),sort_keys=True))
