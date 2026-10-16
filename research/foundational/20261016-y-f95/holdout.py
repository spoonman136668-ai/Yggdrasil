#!/usr/bin/env python3
"""F95 read-only validation/guard of policy frozen on disjoint TRAIN source.

No fitting, decision-rule selection, source-label tuning or protected research
can occur in this evaluator. Every evaluated public prefix is independently
audited by the historical native source-only receipt verifier.
"""
from __future__ import annotations
import hashlib,importlib.util,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parent
PREREG="b03be01fe77f09663f33673ff2095e99f220f16d"
METHOD="b68712cab0d1774c4fc27e928b4f4b57748a1fe4"
POLICY="faa67955f124ead548bd6dbcd3e4a8dc276649be"
F90_POL="56d1c1c81faf432c7f2eb33e6ce45e3513a9c9ae"
FAMILY=(-2,-1)
VALID=range(-6121,-6129,-1)
GUARD=range(-6141,-6157,-1)
def blob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def load(name,path,expected):
 assert blob(path)==expected,("F95_SOURCE_DRIFT",name)
 spec=importlib.util.spec_from_file_location(name,path)
 mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod)
 return mod
def exact_policy():
 assert blob(P/"prereg.json")==PREREG
 assert blob(P/"frozen-policy.json")==POLICY
 p=json.loads((P/"frozen-policy.json").read_text())
 plan=json.loads((P/"prereg.json").read_text())
 assert p["stage"]=="TRAINED_POLICY_FROZEN_BEFORE_VALIDATION_AND_GUARD"
 assert p["training_workflow_run"]==38982686736 and p["exact_method_blob"]==METHOD
 assert p["validation_used"] is False and p["guard_used"] is False
 table=p["policy"]
 assert len(table)==p["eligible_buckets"]
 canonical=json.dumps(table,sort_keys=True,separators=(",",":")).encode()
 assert hashlib.sha256(canonical).hexdigest()==p["canonical_policy_sha256"]
 assert len(canonical)==p["canonical_policy_bytes"]
 return table,plan
def aggregate(rows,select):
 subset=[r for r in rows if select(r)]
 return dict(cases=len(subset),
  correct={arm:sum(r[arm+"_correct"] for r in subset) for arm in ("f60","f83","f90","f95")},
  rescued=sum(not r["f60_correct"] and r["f95_correct"] for r in subset),
  regressed=sum(r["f60_correct"] and not r["f95_correct"] for r in subset),
  learned_interventions=sum(r["f95_interventions"] for r in subset))
def evaluate(mode):
 table,pre=exact_policy()
 conf=pre["cohorts"]["validation" if mode=="validation" else "guard"]
 seeds=VALID if mode=="validation" else GUARD
 assert list(seeds)==list(range(conf["start"],conf["stop_exclusive"],conf["step"]))
 assert len(seeds)*len(FAMILY)==conf["cases"]
 F95=load("f95_exact_frozen_method",P/"risk_lookup.py",METHOD)
 F94=F95.load("f95_frozen_F94",ROOT/"20261016-y-f94"/"single_deviation_feasibility.py",F95.F94_SHA)
 F93=F94.load_exact("f95_frozen_F93",ROOT/"20261016-y-f93b"/"role_grammar.py",F94.F93_BLOB)
 F92=F93.load("f95_frozen_F92",ROOT/"20261016-y-f92"/"dense_path_credit.py",F93.F92_BLOB)
 F91=F92.load("f95_frozen_F91",ROOT/"20261016-y-f91"/"conservative_credit.py",F92.F91_BLOB)
 F90=F91.loader("f95_frozen_F90",ROOT/"20261016-y-f90"/"temporal_credit.py",F91.F90_BLOB)
 F89=F90.load_checked("f95_frozen_F89",ROOT/"20261016-y-f89r"/"graded_exchange.py",F90.F89R_METHOD_BLOB)
 F88=F89.load_exact("f95_frozen_F88",ROOT/"20261016-y-f88"/"frontier.py",F89.F88_BLOB)
 F87=F88.load_exact("f95_frozen_F87",ROOT/"20261016-y-f87b"/"bridge_reserve.py",F88.F87B_BLOB)
 F86=F87.load("f95_frozen_F86",ROOT/"20261016-y-f86"/"queryblind_retention.py",F87.F86_SHA)
 F85=F86.load_exact("f95_frozen_F85",ROOT/"20261016-y-f85"/"global_solver.py",F86.F85_METHOD_BLOB)
 F84=F85.checked_loader("f95_frozen_F84",ROOT/"20261016-y-f84"/"forensic_reachability.py",F85.F84_SHA)
 F83=F84.load_f83();weights83=F84.assert_frozen()
 pack=F83.M.PACK;native=F83.M.F62
 assert blob(ROOT/"20261016-y-f90"/"frozen-policy.json")==F90_POL
 prior=json.loads((ROOT/"20261016-y-f90"/"frozen-policy.json").read_text())
 w90=tuple(prior["weights_int8"])
 assert hashlib.sha256(bytes(x%256 for x in w90)).hexdigest()==prior["weights_sha256"]
 rows=[]
 for seed in seeds:
  for family in FAMILY:
   public,q,meta=F83.M.SOURCE.source(seed,family)
   assert F84.independently_resolve_public(public,q)[0]==frozenset({q["answer"]})
   f60=F84.audit_f60(F83,public,q)
   f83,t83,_=F83.online(public,weights83,True,True)
   assert F83.M.AUDITOR.verify(public,q,t83)["prefixes"]==72
   f90,t90,_=F90.online(public,w90,pack,native,True)
   assert F83.M.AUDITOR.verify(public,q,t90)["prefixes"]==72
   f95,t95,stats=F95.online(public,table,pack,native,True)
   audit=F83.M.AUDITOR.verify(public,q,t95)
   assert audit["prefixes"]==72 and audit["max_payload_bytes"]<=144
   assert stats["native_interventions"]<=1 and stats["latch_bits"]==1
   row=dict(seed=seed,family=family,regime=meta["arrival_regime"],
     kind=meta["question_type"],f95_interventions=stats["native_interventions"],
     source_candidate_count=stats["legal_alternatives_seen"],
     max_native_bytes=audit["max_payload_bytes"],
     identical_F60_final_memory=(f95==f60))
   for arm,mem in (("f60",f60),("f83",f83),("f90",f90),("f95",f95)):
    pred,account=F85.solve_global(mem,{"start":q["start"],"ops":q["ops"]},pack)
    assert pred is None or pred==q["answer"],"FALSE_PUBLIC_SOURCE_OUTPUT"
    assert not account["resource_cap_triggered"] and account["persistent_memory_bytes"]<=144
    row[arm+"_correct"]=int(pred==q["answer"])
   rows.append(row)
 assert len(rows)==conf["cases"]
 total=aggregate(rows,lambda x:True)
 six=aggregate(rows,lambda x:x["kind"]=="crosslink_reach_6_steps")
 strata={}
 for arrival in ("original","local_rotate4"):
  strata[arrival]={}
  for kind in ("within_component_4_steps","crosslink_reach_6_steps"):
   strata[arrival][kind]=aggregate(rows,lambda x:x["regime"]==arrival and x["kind"]==kind)
   assert strata[arrival][kind]["cases"]>0
 supported=six["rescued"]>0 and total["regressed"]==0
 return dict(schema="yggdrasil.f95.risk-lookup.frozen-holdout.v1",
  stage="F95_VALIDATION_ONLY" if mode=="validation" else "F95_ONE_TIME_DISJOINT_GUARD",
  classification=("synthetic_mechanism_supported" if supported else
                  "synthetic_negative_inactive" if total["learned_interventions"]==0 else "synthetic_negative"),
  cases=len(rows),six_step_cases=six["cases"],scores=total["correct"],
  six_step_rescues=six["rescued"],F60_correct_regressions=total["regressed"],
  learned_native_interventions=total["learned_interventions"],
  all_f95_memory_identical_F60=all(r["identical_F60_final_memory"] for r in rows),
  by_regime_and_type=strata,
  max_native_memory_bytes=max(r["max_native_bytes"] for r in rows),
  policy_parameter_bytes=len(json.dumps(table,sort_keys=True,separators=(",",":")).encode()),
  latch_extra_bits=1,all_native_72_prefixes_audited=True,
  trained_policy_frozen_before_holdout=True,no_holdout_model_selection=True,
  no_registered_FIT=True,no_DIAG=True,no_original=True,no_F3=True,
  accepted_science=False,optimizer_promotion=False,controller_mutation=False,rows=rows)
if __name__=="__main__":
 if sys.argv[1:]==["--validation"]:print(json.dumps(evaluate("validation"),sort_keys=True))
 elif sys.argv[1:]==["--guard"]:print(json.dumps(evaluate("guard"),sort_keys=True))
 else:raise SystemExit("F95 read-only evaluation refuses training and protected source")
