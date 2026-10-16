"""F67 durable long-path reservoir with bounded short frontier.

Precode synthetic-only. Persistent online state is exactly <=12 lossless
12-byte packed role-path records; no graph sidecar or future-question input.
"""
from __future__ import annotations
import hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes();return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def load(name,path,expected):
 assert blob(path)==expected,(name,"SOURCE_IDENTITY_DRIFT")
 sp=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(sp);sys.modules[name]=m;sp.loader.exec_module(m);return m
assert blob(P/"prereg.json")=="86294dd7240aa0438f33a00168c7da14f2c8af8b"
SRC=load("f67_exact_public_generator",P.parent/"20261016-y-f63c"/"source.py",
 "c04b73306861098eecf55db77b2db486aa918819")
BASE=load("f67_exact_action_engine",P.parent/"20261015-y-f62"/"source_pilot.py",
 "7ed72deca5584d7c0b6562d74456fa7d4bee6712")
AUDIT=load("f67_independent_causal_audit",P.parent/"20261015-y-f62"/"audit_public.py",
 "383fff0bdd8c8b48fde9538d4e4d768db1c1896f")
PACK=BASE.codec()
BUDGET_AUDIT=load("f67_independent_budget_auditor",P/"audit_budget_public.py",
 "d9661ce5a9cac4212f6f816f6296225be7d32172")
MAX_STABLE=8
MAX_FRONTIER=4
PARAMS=16
def covers_prior_long(old,candidate):
 # Composing source-only role-code prefixes and suffixes preserves
 # exact visible endpoints; never substitute a same-role unrelated path.
 oa,ob,oc=old
 ca,cb,cc=candidate
 n=len(oc)
 return (len(cc)>n and
   ((ca==oa and cc[:n]==oc) or (cb==ob and cc[-n:]==oc)))
def is_admissible(before,after):
 if len(after)>12:return False
 stable=sum(len(x[2])>=4 for x in after)
 frontier=len(after)-stable
 if stable>MAX_STABLE or frontier>MAX_FRONTIER:return False
 for old in before:
  if len(old[2])<4 or old in after:continue
  if not any(covers_prior_long(old,new) for new in after):return False
 return True
def features(before,event,action,after,index):
 before_long=[r for r in before if len(r[2])>=4]
 after_long=[r for r in after if len(r[2])>=4]
 after_short=[r for r in after if len(r[2])<4]
 lens=[len(r[2]) for r in after]
 degree={}
 for a,b,_ in after:
  degree[a]=degree.get(a,0)+1;degree[b]=degree.get(b,0)+1
 a,_role,b=event
 return (1.0,
   len(after_long)/8,
   len(after_short)/4,
   max(lens,default=0)/6,
   sum(l*l for l in lens)/(12*36),
   int(action=="merge"),
   sum(len(r[2])>=5 for r in after)/8,
   sum(len(r[2])>=6 for r in after)/8,
   int(any(a in rec[:2] or b in rec[:2] for rec in before)),
   int(degree.get(a,0)>1 or degree.get(b,0)>1),
   min(sum(n>=2 for n in degree.values()),12)/12,
   (len(after_long)-len(before_long))/8,
   (len(after)-len(before))/12,
   len({c for r in after for c in r[2]})/8,
   index/71,
   sum(len(r[2]) for r in after)/72)
def online(public,weights,trace=False,protect=True):
 assert len(public)==72 and all(len(x)==3 for x in public)
 assert len(weights)==PARAMS and all(type(w)==int and -127<=w<=127 for w in weights)
 memory=()
 snapshots=[];merges=0
 for i,event in enumerate(public):
  actions=BASE.actions(memory,event,i,PACK)
  candidates=[]
  for j,(act,_old,_drop,after,_features) in enumerate(actions):
   # The inherited action engine evicts only when 12 records are full.
   # The 4-slot frontier may fill sooner: generate causal short-record
   # evictions locally, without any unseen observations or extra state.
   options=[after]
   if protect:
    options.extend(after[:k]+after[k+1:] for k,r in enumerate(after) if len(r[2])<4)
   for k,proposal in enumerate(options):
    if protect and not is_admissible(memory,proposal):continue
    ft=features(memory,event,act,proposal,i)
    score=sum(w*x for w,x in zip(weights,ft))
    candidates.append(((score,-(j*32+k)),act,proposal))
  if not candidates:
   # Refusing the current public edge is a lossless causal state action.
   assert protect and is_admissible(memory,memory),"INVALID_PREVIOUS_MEMORY"
   candidates=[((-10**12,0),"reject",memory)]
  _,act,memory=max(candidates,key=lambda entry:entry[0])
  if protect:assert is_admissible(memory,memory)
  BASE._valid_memory(memory,PACK)
  merges+=int(act=="merge")
  if trace:snapshots.append(tuple(PACK.pack(*r).hex() for r in memory))
 return (memory,tuple(snapshots),merges) if trace else memory
def smoke():
 # Source-only engineering weights are NOT trained scientific weights.
 demo=(0,14,1,9,14,7,10,9,0,0,2,15,0,1,0,3)
 rows=[]
 for i in range(12):
  seed=-2701-i;family=(-2,-1)[i%2]
  public,q,meta=SRC.source(seed,family)
  m,trace,merges=online(public,demo,True)
  claim=BUDGET_AUDIT.verify(public,q,trace)
  assert claim["prefixes"]==72 and claim["max_payload_bytes"]<=144
  without,abl_trace,abl_merges=online(public,demo,True,False)
  assert AUDIT.verify(public,q,abl_trace)["prefixes"]==72
  rows.append(dict(seed=seed,kind=meta["question_type"],
     protected_merges=merges,unprotected_merges=abl_merges,
     final_stable=sum(len(r[2])>=4 for r in m),
     model_correct=int(PACK.solve(m,q)==q["answer"])))
 assert sum(r["protected_merges"] for r in rows)>0,"F67_NO_MERGE_DEMONSTRATION"
 assert sum(r["final_stable"] for r in rows)>0,"F67_NO_DURABLE_LONG_PATH_DEMONSTRATION"
 return dict(schema="yggdrasil.f67.durable-budget.synthetic-source.v1",
   stage="UNTRAINED_SYNTHETIC_ONLY",synthetic_cases=len(rows),
   merges=sum(r["protected_merges"] for r in rows),
   durable_records=sum(r["final_stable"] for r in rows),
   final_model_science_fitted=False,registered_fit_used=False,heldout_used=False,
   diag_used=False,original_used=False,F3=False,rows=rows)
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 print(json.dumps(smoke(),sort_keys=True))
