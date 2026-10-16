"""F68 query-blind rare public junction override, synthetic-only source.

The unchanged frozen F60 transition is *mandatory* when the current
incoming public edge does not join two distinct components of the actual
bounded memory. Legal exceptional successors come from frozen ACTION.actions.
All test identities here are unregistered, synthetic negative seeds.
"""
from __future__ import annotations
import hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert blob(P/"prereg.json")=="f447f69142644e5af7832bf0d2079bc060a3a058"
def load(name,path,sha):
 assert blob(path)==sha,(name,"F68_FROZEN_DEPENDENCY_IDENTITY_DRIFT")
 spec=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
 return m
BASE=load("f68_unchanged_F67A_qualified_causal_source",
 P.parent/"20261016-y-f67a"/"causal_memory.py",
 "b370396b3c3571be2c01ab2b33effef14f248eef")
SOURCE=BASE.SOURCE
ACTION=BASE.ACTION
AUDITOR=BASE.AUDITOR
PACK=BASE.PACK
PARAMS=8
def score_features(baseline,after,event,action,drop,index):
 b_hops=sum(len(c) for _,_,c in baseline)
 a_hops=sum(len(c) for _,_,c in after)
 b_end={x for a,b,_ in baseline for x in (a,b)}
 a_end={x for a,b,_ in after for x in (a,b)}
 x,_,y=event
 retained_change=(int(x in a_end)+int(y in a_end)
                  -int(x in b_end)-int(y in b_end))/2
 return (1.0,
         (max((len(c) for _,_,c in after),default=0)
          -max((len(c) for _,_,c in baseline),default=0))/6,
         (a_hops-b_hops)/72,
         retained_change,
         (len(a_end)-len(b_end))/24,
         (sum(len(c)>=2 for _,_,c in after)
          -sum(len(c)>=2 for _,_,c in baseline))/12,
         int(action=="merge"),
         int(drop>=0))
def step(before,event,index,weights,enable_override=True):
 assert len(weights)==PARAMS and all(type(w) is int and -127<=w<=127 for w in weights)
 baseline=ACTION._f60_step(before,event,PACK)
 sep,_frontier,_both=BASE.public_junction_signal(before,event)
 if not enable_override or not sep:
  return baseline,False,sep,False
 options=ACTION.actions(before,event,index,PACK)
 choices=[]
 for j,(act,_old,drop,after,_features) in enumerate(options):
  if after==baseline:continue
  feat=score_features(baseline,after,event,act,drop,index)
  score=sum(w*f for w,f in zip(weights,feat))
  choices.append((score,-j,act,after))
 if not choices:return baseline,False,sep,True
 score,_,act,after=max(choices,key=lambda t:(t[0],t[1]))
 if score<=0:return baseline,False,sep,True
 ACTION._valid_memory(after,PACK)
 return after,True,sep,True
def online(public,weights,trace=False,enable_override=True):
 assert len(public)==72 and all(len(e)==3 for e in public)
 mem=()
 steps=[]
 stats=dict(eligible_junction_steps=0,override_steps=0,
   nonjunction_exact_F60_parity=0,nonjunction_steps=0,
   f60_default_steps=0)
 for i,event in enumerate(public):
  before=mem
  baseline=ACTION._f60_step(before,event,PACK)
  mem,chosen,separate,_candidate=step(before,event,i,weights,enable_override)
  stats["eligible_junction_steps"]+=int(bool(separate))
  stats["override_steps"]+=int(chosen)
  stats["f60_default_steps"]+=int(mem==baseline)
  if not separate:
   stats["nonjunction_steps"]+=1
   stats["nonjunction_exact_F60_parity"]+=int(mem==baseline)
   assert mem==baseline,"NONJUNCTION_F60_PROTECTION_VIOLATION"
  ACTION._valid_memory(mem,PACK)
  if trace:steps.append(tuple(PACK.pack(*rec).hex() for rec in mem))
 return (mem,tuple(steps),stats) if trace else mem
def synthetic_smoke():
 # Untrained engineering weights solely show the exception is reachable.
 demo=(8,0,0,0,0,0,0,0)
 rows=[]
 for k in range(24):
  seed=-2901-k;fam=(-2,-1)[k%2]
  public,q,meta=SOURCE.source(seed,fam)
  memory,trace,stats=online(public,demo,True)
  aud=AUDITOR.verify(public,q,trace)
  assert aud["prefixes"]==72 and aud["max_payload_bytes"]<=144
  baseline,baseline_trace,disabled=online(public,demo,True,False)
  assert AUDITOR.verify(public,q,baseline_trace)["prefixes"]==72
  fixed=ACTION.controls()[0].online_fixed(public)
  assert baseline==fixed
  rows.append(dict(seed=seed,family=fam,kind=meta["question_type"],
      learned_demo_correct=int(PACK.solve(memory,q)==q["answer"]),
      F60_correct=int(PACK.solve(fixed,q)==q["answer"]),**stats))
 count_over=sum(row["override_steps"] for row in rows)
 count_nonjunction=sum(row["nonjunction_steps"] for row in rows)
 count_parity=sum(row["nonjunction_exact_F60_parity"] for row in rows)
 assert count_over>0,"RARE_EXCEPTION_NOT_REACHABLE"
 assert count_nonjunction==count_parity
 return dict(schema="yggdrasil.f68.baseline-shielded.synthetic-source.v1",
  stage="UNTRAINED_SYNTHETIC_SOURCE",cases=len(rows),
  all_nonjunction_parity_pass=True,nonjunction_steps=count_nonjunction,
  all_eligible_junction_steps=sum(r["eligible_junction_steps"] for r in rows),
  provisional_override_steps=count_over,
  frozen_F60_correct=sum(r["F60_correct"] for r in rows),
  demo_correct=sum(r["learned_demo_correct"] for r in rows),
  independent_prefix_causality=True,
  model_fit_executed=False,registered_FIT_train_used=False,
  registered_FIT_validation_used=False,DIAG_used=False,
  original_used=False,F3=False,policy_promotion=False,rows=rows)
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 print(json.dumps(synthetic_smoke(),sort_keys=True))
