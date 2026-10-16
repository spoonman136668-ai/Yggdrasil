"""F67 two-lane lossless public-path / provisional junction memory.

SOURCE ONLY, synthetic negative seeds. Public-prefix causal decisions,
12 total records x 12 bytes; no future question or labels ever enter online.
"""
from __future__ import annotations
import hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 raw=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
assert blob(P/"prereg.json")=="1db81bfd134da0896684abf045c1912a98d6bcf6"
def load(name,path,sha):
 assert blob(path)==sha,(name,"F67_FROZEN_DEPENDENCY_DRIFT")
 s=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m)
 return m
SOURCE=load("f67_structural_source",P.parent/"20261016-y-f63c"/"source.py",
 "c04b73306861098eecf55db77b2db486aa918819")
ACTION=load("f67_original_action_engine",P.parent/"20261015-y-f62"/"source_pilot.py",
 "7ed72deca5584d7c0b6562d74456fa7d4bee6712")
AUDITOR=load("f67_independent_causal_auditor",P.parent/"20261015-y-f62"/"audit_public.py",
 "383fff0bdd8c8b48fde9538d4e4d768db1c1896f")
PACK=ACTION.codec()
WEIGHT_CAP=16
def components(records):
 parents={}
 def root(x):
  parents.setdefault(x,x)
  while parents[x]!=x:
   parents[x]=parents[parents[x]]
   x=parents[x]
  return x
 for a,b,_ in records:
  x=root(a);y=root(b);parents[y]=x
 return {x:root(x) for x in parents}
def junction_features(ordinary,reserve,event,index):
 a,r,b=event
 existing=components(ordinary+reserve)
 both=int(a in existing and b in existing)
 separate=int(both and existing[a]!=existing[b])
 frontier=int((a in existing) != (b in existing))
 endpoint_degree=sum(int(n in (a,b)) for rec in ordinary+reserve for n in rec[:2])
 roles=len({v//2 for rec in ordinary+reserve for v in rec[2]})
 return (1.0,separate,frontier,both,
   min(endpoint_degree,4)/4,roles/4,
   len(ordinary)/10,len(reserve)/2,index/71,
   r/3, int(len(reserve)<2),
   int(len(ordinary)<10),0.0,0.0,0.0,0.0)
def choose_junction(ordinary,reserve,event,index,weights):
 assert len(weights)==WEIGHT_CAP
 assert all(type(w) is int and -127<=w<=127 for w in weights)
 f=junction_features(ordinary,reserve,event,index)
 candidate=bool(f[1] or f[2])
 score=sum(w*x for w,x in zip(weights,f))
 return candidate and score>0,score
def online(public,weights,trace=False,enable_junction=True):
 assert len(public)==72 and all(len(e)==3 for e in public)
 ordinary=()
 reserve=()
 trace_rows=[]
 activity={"junction_reserves":0,"ordinary_merges":0,"junction_merges":0,
           "reserve_replacements":0}
 for i,event in enumerate(public):
  proposed,score=choose_junction(ordinary,reserve,event,i,weights)
  if proposed and enable_junction:
   old=reserve
   incoming=PACK.edge_record(event)
   joins=[(at,merged) for at,merged in PACK.candidates(list(reserve),incoming)
          if 1<len(merged[2])<=6]
   if joins:
    at,incoming=max(joins,key=lambda a:(len(a[1][2]),-a[0]))
    reserve=tuple(rec for j,rec in enumerate(reserve) if j!=at)
    activity["junction_merges"]+=1
   reserve=reserve+(incoming,)
   if len(reserve)>2:
    drop=min(range(len(reserve)),key=lambda j:(len(reserve[j][2]),j))
    reserve=tuple(rec for j,rec in enumerate(reserve) if j!=drop)
    activity["reserve_replacements"]+=1
   activity["junction_reserves"]+=1
  else:
   previous=ordinary
   ordinary=ACTION._f60_step(ordinary,event,PACK)
   if len(ordinary)>10:
    drop=min(range(len(ordinary)),key=lambda j:(len(ordinary[j][2]),j))
    ordinary=tuple(rec for j,rec in enumerate(ordinary) if j!=drop)
   if any(len(rec[2])>1 for rec in ordinary):
    activity["ordinary_merges"]+=int(
       any(len(rec[2])>1 and rec not in previous for rec in ordinary))
  memory=ordinary+reserve
  assert len(ordinary)<=10 and len(reserve)<=2 and len(memory)<=12
  ACTION._valid_memory(memory,PACK)
  if trace:trace_rows.append(tuple(PACK.pack(*rec).hex() for rec in memory))
 return (ordinary+reserve,tuple(trace_rows),activity) if trace else ordinary+reserve
def synthetic_smoke():
 # Explicitly untrained engineering coefficients; scientific FIT untouched.
 demo=(-2,18,9,0,0,0,0,-1,0,0,0,0,0,0,0,0)
 rows=[]
 for k in range(12):
  seed=-2301-k;family=(-2,-1)[k%2]
  public,q,meta=SOURCE.source(seed,family)
  mem,trace,actions=online(public,demo,True,True)
  without,other,other_actions=online(public,demo,True,False)
  aud=AUDITOR.verify(public,q,trace)
  assert aud["prefixes"]==72 and aud["max_payload_bytes"]<=144
  assert AUDITOR.verify(public,q,other)["prefixes"]==72
  rows.append(dict(seed=seed,kind=meta["question_type"],
      junction_actions=actions["junction_reserves"],
      junction_merges=actions["junction_merges"],
      ordinary_merges=actions["ordinary_merges"],
      memory_records=len(mem),actual_correct=int(PACK.solve(mem,q)==q["answer"]),
      no_junction_correct=int(PACK.solve(without,q)==q["answer"])))
 assert sum(r["junction_actions"] for r in rows)>0
 assert sum(r["ordinary_merges"] for r in rows)>0
 return dict(schema="yggdrasil.f67.synthetic-hierarchical-source.v1",
   stage="SYNTHETIC_SOURCE_ONLY_UNTRAINED",
   source_cases=len(rows),
   proposed_junction_actions=sum(r["junction_actions"] for r in rows),
   ordinary_compositional_merges=sum(r["ordinary_merges"] for r in rows),
   full_regression_not_claimed_here=True,
   actual_model_fit_used=False,registered_fit_used=False,
   heldout_used=False,diagnostic_used=False,original_used=False,F3=False,
   optimizer_promotion=False,rows=rows)
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 print(json.dumps(synthetic_smoke(),sort_keys=True))
