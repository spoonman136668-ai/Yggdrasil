"""F67B source-only causal public junction/action interaction policy.

Changes ONLY three feature coordinates of frozen F67A. Actual candidate
successors, bytes, causal auditor, original F60 controls are untouched.
All evaluation here is synthetic negative-seed and no model is trained.
"""
from __future__ import annotations
import hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert blob(P/"prereg.json")=="bf6d45260a237f532287c128da60b301a4a04f2e"
def load(name,path,sha):
 assert blob(path)==sha,(name,"FROZEN_SOURCE_DRIFT")
 spec=importlib.util.spec_from_file_location(name,path)
 obj=importlib.util.module_from_spec(spec);sys.modules[name]=obj;spec.loader.exec_module(obj)
 return obj
BASE=load("f67b_frozen_f67a_source",P.parent/"20261016-y-f67a"/"causal_memory.py",
 "b370396b3c3571be2c01ab2b33effef14f248eef")
SOURCE=BASE.SOURCE
ACTION=BASE.ACTION
AUDITOR=BASE.AUDITOR
PACK=BASE.PACK
PARAMS=16
def public_action_features(before,event,index,action,drop,after,interactions=True):
 v=list(BASE.features(before,event,index,action,drop,after))
 assert len(v)==PARAMS
 if interactions:
  separate,frontier,both=BASE.public_junction_signal(before,event)
  before_reserved=BASE.logical_partition(before)[1]
  after_reserved=BASE.logical_partition(after)[1]
  x,_,y=event
  def touches(reserve):
   return int(any(x in (a,b) or y in (a,b) for a,b,_ in reserve))
  hops_delta=(sum(len(c) for _,_,c in after)-sum(len(c) for _,_,c in before))/6
  v[5]=separate*(1 if action=="merge" else -1)
  v[6]=frontier*(touches(after_reserved)-touches(before_reserved))
  v[7]=both*max(-1,min(1,hops_delta))
 return tuple(v)
def online(public,weights,trace=False,action_interactions=True):
 assert len(public)==72 and all(len(event)==3 for event in public)
 assert len(weights)==PARAMS and all(type(w) is int and -127<=w<=127 for w in weights)
 mem=();traces=[];merges=0
 for i,event in enumerate(public):
  candidates=ACTION.actions(mem,event,i,PACK)
  selected=None
  for j,(action,_old,drop,after,_old_features) in enumerate(candidates):
   features=public_action_features(mem,event,i,action,drop,after,action_interactions)
   score=sum(w*f for w,f in zip(weights,features))
   key=(score,-j)
   if selected is None or key>selected[0]:
    selected=(key,action,after)
  _,action,mem=selected
  merges+=int(action=="merge")
  ACTION._valid_memory(mem,PACK)
  if trace:traces.append(tuple(PACK.pack(*record).hex() for record in mem))
 return (mem,tuple(traces),merges) if trace else mem
def synthetic_smoke():
 # Untrained engineering weights do not count as prospective results.
 demonstration=(0,20,4,16,9,10,6,3,0,0,0,0,0,0,0,0)
 rows=[]
 identifiability_steps=0
 for n in range(12):
  seed=-2601-n;family=(-2,-1)[n%2]
  public,q,meta=SOURCE.source(seed,family)
  kept,trace,merges=online(public,demonstration,True)
  assert AUDITOR.verify(public,q,trace)["prefixes"]==72
  removed,other,disabled_merges=online(public,demonstration,True,False)
  assert AUDITOR.verify(public,q,other)["prefixes"]==72
  mem=()
  for i,event in enumerate(public):
   sep,frontier,both=BASE.public_junction_signal(mem,event)
   candidates=ACTION.actions(mem,event,i,PACK)
   if (sep or frontier or both) and len(candidates)>1:
    vectors=[public_action_features(mem,event,i,act,drop,after)
             for act,_old,drop,after,_f in candidates]
    identifiability_steps+=int(len({v[5:8] for v in vectors})>1)
   mem=ACTION._f60_step(mem,event,PACK)
  rows.append(dict(seed=seed,family=family,question_type=meta["question_type"],
     selected_merges=merges,ablation_merges=disabled_merges,
     demo_correct=int(PACK.solve(kept,q)==q["answer"])))
 selected=sum(r["selected_merges"] for r in rows)
 assert identifiability_steps>0,"F67B_JUNCTION_ACTION_FEATURES_INERT"
 assert selected>0,"F67B_SOURCE_CANNOT_COMPOSE"
 return dict(schema="yggdrasil.f67b.synthetic-causal-source.v1",
   status="SYNTHETIC_SOURCE_ONLY",cases=len(rows),
   action_dependent_junction_decision_steps=identifiability_steps,
   provisional_demo_merges=selected,model_scientifically_trained=False,
   causal_public_prefix_audit=True,fit_train_used=False,
   fit_validation_used=False,diagnostic_used=False,
   original_used=False,F3=False,policy_promotion=False,rows=rows)
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 print(json.dumps(synthetic_smoke(),sort_keys=True))
