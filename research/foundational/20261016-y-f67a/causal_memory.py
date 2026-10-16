"""F67A native, audit-authorized public junction-memory source candidate.

Every transition is one of the original independent F62 ACTION.actions
successors. The two logical 'junction' slots are recomputed from the
12 packed records, not persistent metadata or an extra memory buffer.
SYNTHETIC ONLY; no protected FIT identities are authorized here.
"""
from __future__ import annotations
import hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes();return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert blob(P/"prereg.json")=="5ecade3402c33120a1eabfd34bbc66e91200dcb8"
def load(name,path,expected):
 assert blob(path)==expected,("EXACT_FROZEN_DEPENDENCY_DRIFT",name)
 s=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m)
 return m
SOURCE=load("f67a_immutable_public_source",P.parent/"20261016-y-f63c"/"source.py",
 "c04b73306861098eecf55db77b2db486aa918819")
ACTION=load("f67a_immutable_actions",P.parent/"20261015-y-f62"/"source_pilot.py",
 "7ed72deca5584d7c0b6562d74456fa7d4bee6712")
AUDITOR=load("f67a_independent_prefix_auditor",P.parent/"20261015-y-f62"/"audit_public.py",
 "383fff0bdd8c8b48fde9538d4e4d768db1c1896f")
PACK=ACTION.codec()
PARAMS=16
def connected(records):
 parent={}
 def root(n):
  parent.setdefault(n,n)
  while parent[n]!=n:
   parent[n]=parent[parent[n]];n=parent[n]
  return n
 for a,b,_ in records:
  parent[root(b)]=root(a)
 return {node:root(node) for node in parent}
def public_junction_signal(before,event):
 a,_role,b=event
 mapping=connected(before)
 both=a in mapping and b in mapping
 separated=both and mapping[a]!=mapping[b]
 frontier=(a in mapping) != (b in mapping)
 return int(separated),int(frontier),int(both)
def logical_partition(records):
 """Pure deterministic view over actual packed memory, zero extra state."""
 n=len(records)
 reserve_count=max(0,n-10)
 deg={}
 for a,b,_ in records:
  deg[a]=deg.get(a,0)+1;deg[b]=deg.get(b,0)+1
 priority=sorted(range(n),key=lambda i:(
    -(deg[records[i][0]]+deg[records[i][1]]),
    len(records[i][2]),i))
 reserved=set(priority[:reserve_count])
 ordinary=tuple(record for i,record in enumerate(records) if i not in reserved)
 junction=tuple(record for i,record in enumerate(records) if i in reserved)
 assert len(ordinary)<=10 and len(junction)<=2
 assert len(ordinary)+len(junction)==len(records)
 return ordinary,junction
def features(before,event,index,action,dropped,after):
 separ,frontier,both=public_junction_signal(before,event)
 normal,reserved=logical_partition(after)
 hops=sum(len(r[2]) for r in after)
 maxlen=max((len(r[2]) for r in after),default=0)
 degree={}
 for a,b,_ in after:
  degree[a]=degree.get(a,0)+1;degree[b]=degree.get(b,0)+1
 roles={v//2 for _,_,codes in after for v in codes}
 return (1.0,
  int(action=="merge"),
  hops/72,
  maxlen/6,
  sum(len(r[2])>=4 for r in after)/12,
  separ,frontier,both,
  min(sum(v>1 for v in degree.values()),12)/12,
  len(roles)/4,
  len(after)/12,
  len(reserved)/2,
  len(normal)/10,
  int(dropped>=0),
  index/71,
  int(any(event[0] in rec[:2] or event[2] in rec[:2] for rec in reserved)))
def online(public,weights,trace=False,enable_junction=True):
 assert len(public)==72 and all(len(event)==3 for event in public)
 assert len(weights)==PARAMS and all(type(w) is int and -127<=w<=127 for w in weights)
 memory=()
 traces=[];summary={"chosen_merges":0,"public_junction_events":0,
  "logical_junction_slot_states":0}
 for i,event in enumerate(public):
  sep,frontier,both=public_junction_signal(memory,event)
  summary["public_junction_events"]+=int(bool(sep or frontier))
  candidates=ACTION.actions(memory,event,i,PACK)
  best=None
  for j,(action,_old,drop,after,_features) in enumerate(candidates):
   x=features(memory,event,i,action,drop,after)
   if not enable_junction:
    x=x[:5]+(0.0,0.0,0.0)+x[8:11]+(0.0,)+x[12:15]+(0.0,)
   score=sum(w*value for w,value in zip(weights,x))
   key=(score,-j)
   if best is None or key>best[0]:best=(key,action,after)
  _,action,memory=best
  summary["chosen_merges"]+=int(action=="merge")
  ACTION._valid_memory(memory,PACK)
  _normal,_junction=logical_partition(memory)
  summary["logical_junction_slot_states"]+=int(len(_junction)>0)
  if trace:traces.append(tuple(PACK.pack(*rec).hex() for rec in memory))
 return (memory,tuple(traces),summary) if trace else memory
def synthetic_smoke():
 # Deliberately UNTRAINED engineering demonstration only.
 demonstration=(0,20,4,16,9,10,6,0,0,0,0,0,0,0,0,0)
 rows=[]
 for n in range(12):
  seed=-2401-n;family=(-2,-1)[n%2]
  public,q,meta=SOURCE.source(seed,family)
  memory,trace,stats=online(public,demonstration,True)
  claim=AUDITOR.verify(public,q,trace)
  assert claim["prefixes"]==72 and claim["max_payload_bytes"]<=144
  ab,ab_trace,_=online(public,demonstration,True,False)
  assert AUDITOR.verify(public,q,ab_trace)["prefixes"]==72
  rows.append(dict(seed=seed,kind=meta["question_type"],
     merges=stats["chosen_merges"],junction_signals=stats["public_junction_events"],
     reserve_states=stats["logical_junction_slot_states"],
     fitted=False,correct=int(PACK.solve(memory,q)==q["answer"])))
 assert sum(row["merges"] for row in rows)>0
 assert sum(row["junction_signals"] for row in rows)>0
 return dict(schema="yggdrasil.f67a.causal-hierarchical-source.synthetic.v1",
   stage="UNREGISTERED_SYNTHETIC_ONLY",
   cases=len(rows),model_fitted=False,
   merges=sum(x["merges"] for x in rows),
   public_junction_signals=sum(x["junction_signals"] for x in rows),
   causal_72_prefix_auditor_pass=True,
   fit_train_consumed=False,heldout_consumed=False,
   diag_consumed=False,original_consumed=False,F3=False,
   policy_promotion=False,rows=rows)
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 print(json.dumps(synthetic_smoke(),sort_keys=True))
