"""F74 bounded two-step native causal memory rescue under arrival shift.

All public graphs are new unregistered negative synthetic sources.
The offline task-aware oracle is NONCOMPETITIVE and not a learner.
Never claim infeasibility if the 2048-pair cap censors exploration.
"""
from __future__ import annotations
import collections,hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes();return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert blob(P/"prereg.json")=="d96ad126e109a1eab7dfbf1dda522ae1ee08014a"
parent=P.parent/"20261016-y-f73"/"arrival_oracle.py"
assert blob(parent)=="f7bac62e00b52273ef7fa89889d5f018f591d307"
spec=importlib.util.spec_from_file_location("f74_exact_parent_order_oracle",parent)
f=importlib.util.module_from_spec(spec);sys.modules[spec.name]=f;spec.loader.exec_module(f)
PACK=f.PACK
ACTION=f.ACTION
AUDIT=f.AUDIT
CAP=2048
ANCHORS=(0,8,16,24,32,40,48,56,64)
def alternatives(before,event,index):
 baseline=ACTION._f60_step(before,event,PACK)
 return tuple(dict.fromkeys(c[3] for c in ACTION.actions(before,event,index,PACK)
                            if c[3]!=baseline))
def certified_replay(public,q,overrides):
 mem=();trace=[]
 for i,event in enumerate(public):
  baseline=ACTION._f60_step(mem,event,PACK)
  if i in overrides:
   target=overrides[i]
   assert target in alternatives(mem,event,i),"UNAUTHORIZED_COUNTERFACTUAL_ACTION"
   mem=target
  else:mem=baseline
  ACTION._valid_memory(mem,PACK)
  trace.append(tuple(PACK.pack(*r).hex() for r in mem))
 assertion=AUDIT.verify(public,q,trace)
 assert assertion["prefixes"]==72 and assertion["max_payload_bytes"]<=144
 return PACK.solve(mem,q)==q["answer"]
def two_step(public,q):
 before,last=f.replay(public,q)
 assert PACK.solve(last,q)!=q["answer"]
 pairs=0
 for i in ANCHORS:
  for first in alternatives(before[i],public[i],i):
   middle=first
   for j in range(i+1,min(i+9,72)):
    if j>i+1:
     middle=ACTION._f60_step(middle,public[j-1],PACK)
    for second in alternatives(middle,public[j],j):
     pairs+=1
     terminal=ACTION._finish_fixed(second,public[j+1:],PACK)
     if PACK.solve(terminal,q)==q["answer"]:
      assert certified_replay(public,q,{i:first,j:second})
      return dict(status="RESCUED",candidates_tested=pairs,indices=[i,j])
     if pairs>=CAP:
      return dict(status="CENSORED",candidates_tested=pairs,indices=None)
 return dict(status="NOT_FOUND_WITHIN_FROZEN_SEARCH",candidates_tested=pairs,indices=None)
def run():
 prereg=json.loads((P/"prereg.json").read_text())
 assert prereg["search_frozen"]["cap_per_case"].startswith("2048")
 result=[]
 for k in range(8):
  seed=-3901-k;family=(-2,-1)[k%2]
  public,q,meta=f.SOURCE.source(seed,family)
  for name,ordered in f.orders(public).items():
   assert collections.Counter(ordered)==collections.Counter(public)
   assert f.SOURCE.public_witness(ordered,q)=={q["answer"]}
   one=f.evaluate(ordered,q)
   if one["F60_correct"]:
    status="NOT_NEEDED";two=dict(status=status,candidates_tested=0,indices=None)
   elif one["one_step_rescue"]:
    status="ONE_STEP_ALREADY_RESCUED";two=dict(status=status,candidates_tested=0,indices=None)
   else:
    two=two_step(ordered,q)
   result.append(dict(seed=seed,family=family,arrival_order=name,
     question_type=meta["question_type"],
     F60_correct=one["F60_correct"],
     one_step_rescue=one["one_step_rescue"],
     one_step_index=one["first_rescue_index"],
     one_step_candidates=one["alternatives_tested"],
     two_step_status=two["status"],
     two_step_candidates=two["candidates_tested"],
     two_step_indices=two["indices"]))
 groups={}
 for name in ("original","reverse","even_odd"):
  rows=[r for r in result if r["arrival_order"]==name]
  failures=[r for r in rows if not r["F60_correct"]]
  groups[name]=dict(cases=len(rows),
     frozen_F60_correct=sum(r["F60_correct"] for r in rows),
     F60_failures=len(failures),
     one_step_rescued=sum(r["one_step_rescue"] for r in failures),
     two_step_rescued=sum(r["two_step_status"]=="RESCUED" for r in failures),
     two_step_censored=sum(r["two_step_status"]=="CENSORED" for r in failures),
     two_step_not_found_in_search=sum(r["two_step_status"]=="NOT_FOUND_WITHIN_FROZEN_SEARCH" for r in failures),
     legal_one_step_candidates=sum(r["one_step_candidates"] for r in failures),
     legal_two_step_pairs=sum(r["two_step_candidates"] for r in failures))
 outcome=dict(schema="yggdrasil.f74.bounded-two-intervention-arrival-robustness.v1",
  stage="UNREGISTERED_READ_ONLY_UNFAIR_ORACLE",
  base_cases=8,schedules=3,total_task_evaluations=len(result),
  pair_cap_per_case=CAP,grouped=groups,
  no_unsupported_infeasibility_claims=True,
  exact_original_causal_prefix_auditor=True,original_source_preserved=True,
  no_learning_or_fitting=True,registered_train_used=False,
  validation_used=False,DIAG_used=False,originals_used=False,
  F3=False,optimizer_promotion=False,rows=result)
 print(json.dumps(outcome,sort_keys=True))
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 run()
