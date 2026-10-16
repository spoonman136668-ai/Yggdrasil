"""F70 fixed-budget, synthetic-only causal action reachability diagnostic.

This oracle is unfair, offline, NONCOMPETITIVE. It accesses the completed
public stream and question solely to test whether original lossless native
memory actions could have saved a frozen-F60 failure at frozen checkpoints.
No online policy is trained and no registered evidence is consumed.
"""
from __future__ import annotations
import hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert blob(P/"prereg.json")=="f9ce48f01e499d83fbf714e0982101208f1cfddc"
def load(name,path,sha):
 assert blob(path)==sha,(name,"F70_TRANSITIVE_SOURCE_IDENTITY_DRIFT")
 spec=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
 return m
SOURCE=load("f70_exact_public_synthetic_generator",P.parent/"20261016-y-f63c"/"source.py",
 "c04b73306861098eecf55db77b2db486aa918819")
ACTION=load("f70_exact_frozen_native_memory_actions",P.parent/"20261015-y-f62"/"source_pilot.py",
 "7ed72deca5584d7c0b6562d74456fa7d4bee6712")
AUDIT=load("f70_independent_causal_prefix_auditor",P.parent/"20261015-y-f62"/"audit_public.py",
 "383fff0bdd8c8b48fde9538d4e4d768db1c1896f")
PACK=ACTION.codec()
CHECKPOINTS=tuple(range(7,72,8))
def f60_prefix(public):
 mem=();traces=[];pre=[]
 for event in public:
  pre.append(mem)
  mem=ACTION._f60_step(mem,event,PACK)
  traces.append(tuple(PACK.pack(*r).hex() for r in mem))
 return tuple(pre),mem,tuple(traces)
def oracle_success(public,q,overrides):
 """Replay original F60 at every nonoverridden public event."""
 memory=();trace=[]
 for i,event in enumerate(public):
  baseline=ACTION._f60_step(memory,event,PACK)
  if i in overrides:
   after=overrides[i]
   allowed=[candidate[3] for candidate in ACTION.actions(memory,event,i,PACK)]
   assert after in allowed and after!=baseline,"ORACLE_USED_UNAUTHORIZED_MEMORY"
   memory=after
  else:memory=baseline
  ACTION._valid_memory(memory,PACK)
  trace.append(tuple(PACK.pack(*r).hex() for r in memory))
 assert AUDIT.verify(public,q,trace)["prefixes"]==72
 return int(PACK.solve(memory,q)==q["answer"])
def evaluate(public,q):
 before,last,baseline_trace=f60_prefix(public)
 assert AUDIT.verify(public,q,baseline_trace)["prefixes"]==72
 f60=int(PACK.solve(last,q)==q["answer"])
 if f60:
  return dict(F60_correct=True,one_step_rescue=False,two_step_rescue=False,
   first_step_candidates_considered=0,two_step_pairs_considered=0,
   first_rescue_index=None,second_rescue_indices=None)
 count1=count2=0
 for i in CHECKPOINTS:
  event=public[i]
  base=ACTION._f60_step(before[i],event,PACK)
  first=[c[3] for c in ACTION.actions(before[i],event,i,PACK)
         if c[3]!=base]
  # Unique resulting memory states, original order retained.
  first=list(dict.fromkeys(first))
  for state in first:
   count1+=1
   terminal=ACTION._finish_fixed(state,public[i+1:],PACK)
   if PACK.solve(terminal,q)==q["answer"]:
    assert oracle_success(public,q,{i:state})==1
    return dict(F60_correct=False,one_step_rescue=True,two_step_rescue=False,
      first_step_candidates_considered=count1,two_step_pairs_considered=count2,
      first_rescue_index=i,second_rescue_indices=None)
 # Two-step oracle, fixed exactly eight events between interventions.
 for i in CHECKPOINTS:
  initial=before[i]
  baseline=ACTION._f60_step(initial,public[i],PACK)
  first=list(dict.fromkeys(c[3] for c in ACTION.actions(initial,public[i],i,PACK)
                           if c[3]!=baseline))
  j=i+8
  if j>=72:continue
  for after_first in first:
   middle=ACTION._finish_fixed(after_first,public[i+1:j],PACK)
   second_base=ACTION._f60_step(middle,public[j],PACK)
   second=list(dict.fromkeys(c[3] for c in ACTION.actions(middle,public[j],j,PACK)
                             if c[3]!=second_base))
   for after_second in second:
    count2+=1
    terminal=ACTION._finish_fixed(after_second,public[j+1:],PACK)
    if PACK.solve(terminal,q)==q["answer"]:
     assert oracle_success(public,q,{i:after_first,j:after_second})==1
     return dict(F60_correct=False,one_step_rescue=False,two_step_rescue=True,
      first_step_candidates_considered=count1,
      two_step_pairs_considered=count2,
      first_rescue_index=None,second_rescue_indices=[i,j])
 return dict(F60_correct=False,one_step_rescue=False,two_step_rescue=False,
   first_step_candidates_considered=count1,two_step_pairs_considered=count2,
   first_rescue_index=None,second_rescue_indices=None)
def synthetic_study():
 rows=[]
 for k in range(16):
  seed=-3301-k;family=(-2,-1)[k%2]
  public,q,meta=SOURCE.source(seed,family)
  assert len(public)==72
  verdict=evaluate(public,q)
  rows.append(dict(seed=seed,family=family,
   question_type=meta["question_type"],**verdict))
 broken=[r for r in rows if not r["F60_correct"]]
 result=dict(schema="yggdrasil.f70.synthetic-bounded-action-reachability.v1",
   stage="SYNTHETIC_UNFAIR_OFFLINE_DIAGNOSTIC",
   synthetic_cases=len(rows),frozen_F60_correct=sum(r["F60_correct"] for r in rows),
   frozen_F60_failures=len(broken),
   one_step_rescues=sum(r["one_step_rescue"] for r in broken),
   two_step_rescues=sum(r["two_step_rescue"] for r in broken),
   unrescued_failures=sum(not r["one_step_rescue"] and not r["two_step_rescue"] for r in broken),
   total_first_step_candidates=sum(r["first_step_candidates_considered"] for r in broken),
   total_two_step_pairs=sum(r["two_step_pairs_considered"] for r in broken),
   protected_fit_used=False,heldout_used=False,
   diagnostics_used=False,original_used=False,
   learner_fit=False,independent_F3=False,optimizer_promotion=False,
   unfair_oracle_noncompetitive=True,rows=rows)
 print(json.dumps(result,sort_keys=True))
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 synthetic_study()
