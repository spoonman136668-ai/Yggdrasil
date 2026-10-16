"""F92 sealed read-only evaluation. No training or policy selection is callable."""
from __future__ import annotations
import hashlib,importlib.util,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parent
PRE="c56d1e1c2221ab7311ffb093921ee21b7e6f0fda"
MODEL="7fdaf5d24866c347275c2ffa3aec7dfeaed6ac5b"
WEIGHTS="6a94f730baefe008a21f7286416f3163835ed93e"
F91POL="4382ec2c4eeda870b575ec95b000286feee53449"
F90POL="56d1c1c81faf432c7f2eb33e6ce45e3513a9c9ae"
def blob(path):
 data=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
def load(name,path,expected):
 assert blob(path)==expected,("F92_SOURCE_DRIFT",name)
 s=importlib.util.spec_from_file_location(name,path)
 mod=importlib.util.module_from_spec(s);sys.modules[name]=mod;s.loader.exec_module(mod)
 return mod
def policy():
 assert blob(P/"prereg.json")==PRE and blob(P/"frozen-policy.json")==WEIGHTS
 prereg=json.loads((P/"prereg.json").read_text())
 p=json.loads((P/"frozen-policy.json").read_text())
 assert p["stage"]=="FROZEN_TRAIN_WEIGHTS_BEFORE_VALIDATION_OR_GUARD"
 assert p["train_run_id"]==38975152103 and p["method_git_blob"]==MODEL
 b=tuple(p["benefit_weights"]);h=tuple(p["harm_weights"])
 assert len(b)==len(h)==12 and all(type(x)==int and -96<=x<=96 for x in b+h)
 assert hashlib.sha256(bytes(w%256 for w in b+h)).hexdigest()==p["weights_sha256"]
 assert p["weights_sha256"]=="6d0ce85ed78274bffce45e43aa022437f35ff5d5f4ebe1cc4cb5cce1d0b70e6d"
 return prereg,b,h
def group(rows,check):
 t=[r for r in rows if check(r)]
 return {"cases":len(t),
 "correct":{n:sum(x[n+"_correct"] for x in t) for n in ("f60","f83","f90","f91","f92")},
 "rescued":sum(not x["f60_correct"] and x["f92_correct"] for x in t),
 "regressed":sum(x["f60_correct"] and not x["f92_correct"] for x in t),
 "interventions":sum(x["f92_interventions"] for x in t)}
def evaluate(mode):
 prereg,b,h=policy()
 spec=prereg["cohorts"]["validation" if mode=="validation" else "guard"]
 ids=range(spec["start"],spec["stop_exclusive"],spec["step"])
 assert len(ids)*len(spec["families"])==spec["cases"]
 F92=load("f92_eval_method",P/"dense_path_credit.py",MODEL)
 F91=F92.load("f92_eval_f91",ROOT/"20261016-y-f91"/"conservative_credit.py",F92.F91_BLOB)
 F90=F91.loader("f92_eval_f90",ROOT/"20261016-y-f90"/"temporal_credit.py",F91.F90_BLOB)
 assert blob(ROOT/"20261016-y-f91"/"frozen-policy.json")==F91POL
 assert blob(ROOT/"20261016-y-f90"/"frozen-policy.json")==F90POL
 p91=json.loads((ROOT/"20261016-y-f91"/"frozen-policy.json").read_text())
 p90=json.loads((ROOT/"20261016-y-f90"/"frozen-policy.json").read_text())
 x91=tuple(p91["benefit_weights"]);y91=tuple(p91["harm_weights"]);x90=tuple(p90["weights_int8"])
 assert hashlib.sha256(bytes(w%256 for w in x91+y91)).hexdigest()==p91["weights_sha256"]
 assert hashlib.sha256(bytes(w%256 for w in x90)).hexdigest()==p90["weights_sha256"]
 F89=F90.load_checked("f92_eval_f89",ROOT/"20261016-y-f89r"/"graded_exchange.py",F90.F89R_METHOD_BLOB)
 F88=F89.load_exact("f92_eval_f88",ROOT/"20261016-y-f88"/"frontier.py",F89.F88_BLOB)
 F87=F88.load_exact("f92_eval_f87",ROOT/"20261016-y-f87b"/"bridge_reserve.py",F88.F87B_BLOB)
 F86=F87.load("f92_eval_f86",ROOT/"20261016-y-f86"/"queryblind_retention.py",F87.F86_SHA)
 F85=F86.load_exact("f92_eval_f85",ROOT/"20261016-y-f85"/"global_solver.py",F86.F85_METHOD_BLOB)
 F84=F85.checked_loader("f92_eval_f84",ROOT/"20261016-y-f84"/"forensic_reachability.py",F85.F84_SHA)
 F83=F84.load_f83();weights83=F84.assert_frozen()
 codec=F83.M.PACK;F62=F83.M.F62;rows=[]
 for seed in ids:
  for family in spec["families"]:
   public,q,meta=F83.M.SOURCE.source(seed,family)
   assert F84.independently_resolve_public(public,q)[0]==frozenset({q["answer"]})
   states={"f60":F84.audit_f60(F83,public,q)}
   states["f83"],t83,_=F83.online(public,weights83,True,True)
   assert F83.M.AUDITOR.verify(public,q,t83)["prefixes"]==72
   states["f90"],t90,_=F90.online(public,x90,codec,F62,True)
   assert F83.M.AUDITOR.verify(public,q,t90)["prefixes"]==72
   states["f91"],t91,_=F91.online(public,x91,y91,codec,F62,True)
   assert F83.M.AUDITOR.verify(public,q,t91)["prefixes"]==72
   states["f92"],t92,detail=F92.online(public,b,h,codec,F62,F91,True)
   proof=F83.M.AUDITOR.verify(public,q,t92)
   assert proof["prefixes"]==72 and proof["max_payload_bytes"]<=144
   assert detail["interventions"]<=1 and detail["latch_bits"]==1
   row={"seed":seed,"family":family,"kind":meta["question_type"],
        "arrival":meta["arrival_regime"],"f92_interventions":detail["interventions"],
        "max_retained_bytes":proof["max_payload_bytes"]}
   for name,state in states.items():
    guess,cost=F85.solve_global(state,{"start":q["start"],"ops":q["ops"]},codec)
    assert guess is None or guess==q["answer"],"F92_INVALID_PUBLIC_ANSWER"
    assert not cost["resource_cap_triggered"] and cost["persistent_memory_bytes"]<=144
    row[name+"_correct"]=int(guess==q["answer"])
   rows.append(row)
 assert len(rows)==spec["cases"]
 summary=group(rows,lambda x:True)
 six=group(rows,lambda x:x["kind"]=="crosslink_reach_6_steps")
 by={}
 for regime in ("original","local_rotate4"):
  by[regime]={}
  for kind in ("within_component_4_steps","crosslink_reach_6_steps"):
   by[regime][kind]=group(rows,lambda x:x["arrival"]==regime and x["kind"]==kind)
   assert by[regime][kind]["cases"]>0
 qualified=six["rescued"]>=1 and summary["regressed"]==0
 return {"schema":"yggdrasil.f92.dense-path-credit.holdout.v1",
 "stage":"F92_FROZEN_VALIDATION" if mode=="validation" else "F92_FIRST_USE_DISJOINT_GUARD",
 "classification":"synthetic_mechanism_supported" if qualified else
  "synthetic_negative_inactive" if summary["interventions"]==0 else "synthetic_negative",
 "cases":len(rows),"six_step_cases":six["cases"],
 "scores":summary["correct"],"six_step_rescues":six["rescued"],
 "F60_correct_case_regressions":summary["regressed"],
 "learned_interventions":summary["interventions"],"by_regime_and_type":by,
 "max_memory_bytes":max(x["max_retained_bytes"] for x in rows),
 "extra_model_bytes":24,"latch_bits":1,
 "native_72_prefix_causality_verified":True,
 "policy_frozen_before_holdout":True,"no_train_from_holdout":True,
 "no_registered_FIT":True,"no_DIAG":True,"no_original":True,"no_F3":True,
 "science_accepted":False,"optimizer_promotion":False,"controller_mutation":False,
 "rows":rows}
if __name__=="__main__":
 if sys.argv[1:]==["--frozen-validation"]:print(json.dumps(evaluate("validation"),sort_keys=True))
 elif sys.argv[1:]==["--frozen-guard"]:print(json.dumps(evaluate("guard"),sort_keys=True))
 else:raise SystemExit("Protected sources and training unavailable in F92 holdout")
