#!/usr/bin/env python3
"""F91 frozen dual-head temporal-policy independent synthetic holdout.

No fitting or selection is possible here; it reads content-addressed F91
weights, immutable controller code and frozen F76 negative synthetic source.
Protected FIT/DIAG/ORIGINAL/F3 are categorically outside this entrypoint.
"""
from __future__ import annotations
import hashlib,importlib.util,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parent
PREREG_SHA="7a680c47029777f5d27b924d75c750bb348c06fc"
MODEL_SHA="a3e9ccdbd623d996d56355bb6b9e838fb59fc3b2"
POLICY_SHA="4382ec2c4eeda870b575ec95b000286feee53449"
F90_POLICY_SHA="56d1c1c81faf432c7f2eb33e6ce45e3513a9c9ae"
FAMILY=(-2,-1)
VALID=range(-5821,-5829,-1)
GUARD=range(-5841,-5857,-1)
def blob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def load(name,path,expected):
 assert blob(path)==expected,("F91_HOLDOUT_PARENT_DRIFT",name)
 spec=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
 return m
def identities():
 assert blob(P/"prereg.json")==PREREG_SHA
 assert blob(P/"frozen-policy.json")==POLICY_SHA
 cfg=json.loads((P/"prereg.json").read_text())
 policy=json.loads((P/"frozen-policy.json").read_text())
 assert policy["method_git_blob"]==MODEL_SHA
 assert policy["stage"]=="TRAIN_WEIGHTS_FROZEN_BEFORE_VALIDATION_OR_GUARD"
 assert policy["train_run"]==38973865178
 b=tuple(policy["benefit_weights"])
 h=tuple(policy["harm_weights"])
 assert len(b)==len(h)==12 and all(type(x) is int and -96<=x<=96 for x in b+h)
 assert hashlib.sha256(bytes(w%256 for w in b+h)).hexdigest()==policy["weights_sha256"]
 assert policy["weights_sha256"]=="786d3f37c7cfcbfcb5bbe072fc41246dd55450d92e33f084873611c94847628b"
 return b,h,cfg

def aggregate(rows,filter_fn):
 subset=[r for r in rows if filter_fn(r)]
 return dict(cases=len(subset),
  correct={arm:sum(r[arm+"_correct"] for r in subset) for arm in ("f60","f83","f90","f91")},
  rescued=sum((not r["f60_correct"]) and r["f91_correct"] for r in subset),
  regressed=sum(r["f60_correct"] and not r["f91_correct"] for r in subset),
  learned_interventions=sum(r["f91_interventions"] for r in subset))
def examine(which):
 benefit,harm,cfg=identities()
 cohort=cfg["cohorts"]["validation" if which=="validation" else "guard"]
 ids=VALID if which=="validation" else GUARD
 assert list(ids)==list(range(cohort["start"],cohort["stop_exclusive"],cohort["step"]))
 F91=load("f91_frozen_holdout_policy",P/"conservative_credit.py",MODEL_SHA)
 F90=F91.loader("f91_frozen_F90",ROOT/"20261016-y-f90"/"temporal_credit.py",F91.F90_BLOB)
 assert blob(ROOT/"20261016-y-f90"/"frozen-policy.json")==F90_POLICY_SHA
 f90data=json.loads((ROOT/"20261016-y-f90"/"frozen-policy.json").read_text())
 w90=tuple(f90data["weights_int8"])
 assert hashlib.sha256(bytes(x%256 for x in w90)).hexdigest()==f90data["weights_sha256"]
 F89=F90.load_checked("f91_frozen_F89",ROOT/"20261016-y-f89r"/"graded_exchange.py",F90.F89R_METHOD_BLOB)
 F88=F89.load_exact("f91_frozen_F88",ROOT/"20261016-y-f88"/"frontier.py",F89.F88_BLOB)
 F87=F88.load_exact("f91_frozen_F87",ROOT/"20261016-y-f87b"/"bridge_reserve.py",F88.F87B_BLOB)
 F86=F87.load("f91_frozen_F86",ROOT/"20261016-y-f86"/"queryblind_retention.py",F87.F86_SHA)
 F85=F86.load_exact("f91_frozen_F85",ROOT/"20261016-y-f85"/"global_solver.py",F86.F85_METHOD_BLOB)
 F84=F85.checked_loader("f91_frozen_F84",ROOT/"20261016-y-f84"/"forensic_reachability.py",F85.F84_SHA)
 F83=F84.load_f83()
 f83_weights=F84.assert_frozen()
 pack=F83.M.PACK;F62=F83.M.F62
 rows=[]
 for seed in ids:
  for fam in FAMILY:
   public,q,meta=F83.M.SOURCE.source(seed,fam)
   assert F84.independently_resolve_public(public,q)[0]=={q["answer"]}
   state={}
   state["f60"]=F84.audit_f60(F83,public,q)
   state["f83"],trace83,_=F83.online(public,f83_weights,True,True)
   assert F83.M.AUDITOR.verify(public,q,trace83)["prefixes"]==72
   state["f90"],trace90,_=F90.online(public,w90,pack,F62,True)
   assert F83.M.AUDITOR.verify(public,q,trace90)["prefixes"]==72
   state["f91"],trace91,audit=F91.online(public,benefit,harm,pack,F62,True)
   proof=F83.M.AUDITOR.verify(public,q,trace91)
   assert proof["prefixes"]==72 and proof["max_payload_bytes"]<=144
   assert audit["interventions"]<=1 and audit["latch_extra_bits"]==1
   row=dict(seed=seed,family=fam,regime=meta["arrival_regime"],
    kind=meta["question_type"],f91_interventions=audit["interventions"],
    f91_alternatives_scored=audit["alternatives_scored"],
    f91_memory_bytes=proof["max_payload_bytes"])
   for arm,retained in state.items():
    answer,diags=F85.solve_global(retained,{
     "start":q["start"],"ops":q["ops"]},pack)
    assert answer is None or answer==q["answer"],"INVALID_NONPUBLIC_PREDICTION"
    assert not diags["resource_cap_triggered"] and diags["persistent_memory_bytes"]<=144
    row[arm+"_correct"]=int(answer==q["answer"])
   rows.append(row)
 assert len(rows)==cohort["cases"]
 by={}
 for regime in ("original","local_rotate4"):
  by[regime]={}
  for kind in ("within_component_4_steps","crosslink_reach_6_steps"):
   part=aggregate(rows,lambda row: row["regime"]==regime and row["kind"]==kind)
   assert part["cases"]>0
   by[regime][kind]=part
 total=aggregate(rows,lambda row:True)
 six=aggregate(rows,lambda row:row["kind"]=="crosslink_reach_6_steps")
 positive=six["rescued"]>0 and total["regressed"]==0
 return dict(
  schema="yggdrasil.f91.conservative-learned-temporal-"+which+".v1",
  stage=("F91_FROZEN_VALIDATION_ONLY" if which=="validation" else
         "F91_FIRST_USE_DISJOINT_NEGATIVE_SYNTHETIC_GUARD"),
  classification=("synthetic_mechanism_supported" if positive else
                  "synthetic_negative_inactive" if total["learned_interventions"]==0 else "synthetic_negative"),
  cases=len(rows),six_step_cases=six["cases"],scores=total["correct"],
  six_step_rescues=six["rescued"],F60_correct_case_regressions=total["regressed"],
  learned_native_interventions=total["learned_interventions"],
  by_regime_and_type=by,
  max_persistent_memory_bytes=max(row["f91_memory_bytes"] for row in rows),
  extra_model_bytes=24,extra_latch_bits=1,
  exact_72_public_prefix_audit=True,
  question_and_future_not_available_during_online=True,
  frozen_weights_sha256="786d3f37c7cfcbfcb5bbe072fc41246dd55450d92e33f084873611c94847628b",
  no_protected_FIT=True,no_DIAG=True,no_original=True,no_F3=True,
  no_validation_or_guard_training=True,no_retuning=True,
  science_accepted=False,optimizer_promotion=False,controller_mutation=False,
  rows=rows)
if __name__=="__main__":
 if sys.argv[1:]==["--frozen-validation-only"]:
  print(json.dumps(examine("validation"),sort_keys=True))
 elif sys.argv[1:]==["--frozen-disjoint-guard-only"]:
  print(json.dumps(examine("guard"),sort_keys=True))
 else:
  raise SystemExit("F91 only supports explicitly frozen validation or synthetic guard")
