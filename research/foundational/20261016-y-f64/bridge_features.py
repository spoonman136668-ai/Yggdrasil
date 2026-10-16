"""F64 source-only trainable bridge-preservation policy; synthetic cases only.

No FIT, DIAG or original dispatch. Future question and private tags are
absent from online(), actions and features. No weights yet scientifically fitted.
"""
from __future__ import annotations
import hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes();return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def load(name,path,expected):
 assert blob(path)==expected,("FROZEN_SOURCE_DRIFT",name)
 sp=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(sp);sys.modules[name]=m;sp.loader.exec_module(m);return m
SOURCE=load("f64_frozen_public_generator",P.parent/"20261016-y-f63c"/"source.py",
 "c04b73306861098eecf55db77b2db486aa918819")
BASE=load("f64_frozen_f62_action_engine",P.parent/"20261015-y-f62"/"source_pilot.py",
 "7ed72deca5584d7c0b6562d74456fa7d4bee6712")
AUDIT=load("f64_independent_causal_auditor",P.parent/"20261015-y-f62"/"audit_public.py",
 "383fff0bdd8c8b48fde9538d4e4d768db1c1896f")
PACK=BASE.codec()
MAX_RECORDS=12
PARAMS=8
def connectivity(records):
 # Exact endpoint adjacency of already retained lossless records only.
 parent={}
 def root(v):
  parent.setdefault(v,v)
  while parent[v]!=v:
   parent[v]=parent[parent[v]]
   v=parent[v]
  return v
 for a,b,_ in records:
  x=root(a);y=root(b)
  parent[y]=x
 return {n:root(n) for n in parent}
def features(before,event,after,action,index):
 assert len(event)==3 and 0<=index<72
 assert len(after)<=12
 a,r,b=event
 old=connectivity(before)
 new=connectivity(after)
 is_bridge=int(a in old and b in old and old[a]!=old[b])
 preserved=int(is_bridge and a in new and b in new and new[a]==new[b])
 lens=[len(rec[2]) for rec in after]
 degrees={}
 for start,end,_ in after:
  degrees[start]=degrees.get(start,0)+1
  degrees[end]=degrees.get(end,0)+1
 hubs=sum(n>=2 for n in degrees.values())
 # All bounded, causal, source-independent features.
 return (sum(lens)/72,
         max(lens,default=0)/6,
         sum(n>=4 for n in lens)/12,
         preserved,
         hubs/24,
         min(len({c for rec in after for c in rec[2]}),8)/8,
         len(after)/12,
         int(action=="merge"))
def online(public,weights,trace=False,bridge_features=True):
 assert len(weights)==PARAMS and all(isinstance(w,int) and -127<=w<=127 for w in weights)
 memory=()
 history=[]
 for index,event in enumerate(public):
  candidates=BASE.actions(memory,event,index,PACK)
  best=None
  for j,(action,old,dropped,after,_original_feats) in enumerate(candidates):
   feat=features(memory,event,after,action,index)
   if not bridge_features:
    feat=feat[:3]+(0.0,0.0)+feat[5:]
   score=sum(w*v for w,v in zip(weights,feat))
   key=(score,-j)
   if best is None or key>best[0]:best=(key,after)
  memory=best[1]
  BASE._valid_memory(memory,PACK)
  if trace:history.append(tuple(PACK.pack(*record).hex() for record in memory))
 return (memory,tuple(history)) if trace else memory
def source_only_smoke():
 # Deliberately use negative synthetic identities, never protected.
 stats=[]
 engineering_weights=(6,9,18,32,6,6,4,5)
 for seed,family in ((-701,-2),(-702,-1),(-703,-2),(-704,-1)):
  public,q,_=SOURCE.source(seed,family)
  retained,trace=online(public,engineering_weights,True)
  verdict=AUDIT.verify(public,q,trace)
  assert verdict["prefixes"]==72
  assert verdict["max_payload_bytes"]<=144
  no_bridge,controltrace=online(public,engineering_weights,True,False)
  assert AUDIT.verify(public,q,controltrace)["prefixes"]==72
  stats.append(dict(seed=seed,family=family,
    engineered_demo_correct=int(PACK.solve(retained,q)==q["answer"]),
    disabled_bridge_demo_correct=int(PACK.solve(no_bridge,q)==q["answer"]),
    max_bytes=verdict["max_payload_bytes"]))
 return dict(schema="yggdrasil.f64.bridge-features.source-engineering.v1",
  stage="SOURCE_ONLY_UNTRAINED",synthetic_cases=len(stats),
  learned_fit_executed=False,registered_fit_executed=False,
  heldout_executed=False,diagnostics_executed=False,originals_executed=False,
  training_labels_enter_online=False,independent_F3=False,rows=stats)
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 print(json.dumps(source_only_smoke(),sort_keys=True))
