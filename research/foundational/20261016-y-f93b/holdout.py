"""F93B: separate, frozen-grammar read-only validation and guard qualification."""
from __future__ import annotations
import hashlib,importlib.util,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parent
PRE="a9e0c04027e6488220c068eb59e580a1295c736b"
METHOD="b70af0a91ecc16d8a173b7245b007b646fed8ad6"
GRAMMAR_BLOB="792e2b6b8329a3b786c5c0b8bb5c53659bafd11a"
F90_POLICY="56d1c1c81faf432c7f2eb33e6ce45e3513a9c9ae"
F91_POLICY="4382ec2c4eeda870b575ec95b000286feee53449"
F92_POLICY="6a94f730baefe008a21f7286416f3163835ed93e"
def blob(path):
 data=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
def load(name,path,sha):
 assert blob(path)==sha,("F93B_HOLDOUT_SOURCE_DRIFT",name)
 s=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m)
 return m
def verified_policy(path,sha,keys):
 assert blob(path)==sha
 policy=json.loads(path.read_text())
 weights=tuple(int(x) for key in keys for x in policy[key])
 assert all(-96<=x<=96 for x in weights)
 assert hashlib.sha256(bytes(v%256 for v in weights)).hexdigest()==policy["weights_sha256"]
 return tuple(tuple(policy[key]) for key in keys)
def subset(rows,predicate):
 t=[r for r in rows if predicate(r)]
 return {"cases":len(t),"correct":{a:sum(r[a+"_correct"] for r in t)
         for a in ("f60","f83","f90","f91","f92","f93b")},
  "rescue":sum(not r["f60_correct"] and r["f93b_correct"] for r in t),
  "regression":sum(r["f60_correct"] and not r["f93b_correct"] for r in t),
  "interventions":sum(r["interventions"] for r in t)}
def evaluate(mode):
 assert blob(P/"prereg.json")==PRE and blob(P/"frozen-grammar.json")==GRAMMAR_BLOB
 reg=json.loads((P/"prereg.json").read_text())
 pol=json.loads((P/"frozen-grammar.json").read_text())
 assert pol["stage"]=="TRAINED_GRAMMAR_FROZEN_BEFORE_ANY_VALIDATION_OR_GUARD"
 assert pol["model_source_blob"]==METHOD and pol["train_run_id"]==38981050121
 patterns=tuple(tuple(x) for x in pol["model"])
 assert 0<len(patterns)<=3 and all(len(p)==6 for p in patterns)
 assert hashlib.sha256(json.dumps([list(p) for p in patterns],separators=(",",":")).encode()).hexdigest()==pol["grammar_sha256"]
 cfg=reg["cohorts"]["validation" if mode=="validation" else "guard"]
 seeds=range(cfg["start"],cfg["end_exclusive"],cfg["step"])
 assert len(seeds)*len(cfg["families"])==cfg["cases"]
 F93=load("f93b_holdout_exact",P/"role_grammar.py",METHOD)
 F92=F93.load("f93b_exact_f92",R/"20261016-y-f92"/"dense_path_credit.py",F93.F92_BLOB)
 F91=F92.load("f93b_exact_f91",R/"20261016-y-f91"/"conservative_credit.py",F92.F91_BLOB)
 F90=F91.loader("f93b_exact_f90",R/"20261016-y-f90"/"temporal_credit.py",F91.F90_BLOB)
 F89=F90.load_checked("f93b_exact_f89",R/"20261016-y-f89r"/"graded_exchange.py",F90.F89R_METHOD_BLOB)
 F88=F89.load_exact("f93b_exact_f88",R/"20261016-y-f88"/"frontier.py",F89.F88_BLOB)
 F87=F88.load_exact("f93b_exact_f87",R/"20261016-y-f87b"/"bridge_reserve.py",F88.F87B_BLOB)
 F86=F87.load("f93b_exact_f86",R/"20261016-y-f86"/"queryblind_retention.py",F87.F86_SHA)
 F85=F86.load_exact("f93b_exact_f85",R/"20261016-y-f85"/"global_solver.py",F86.F85_METHOD_BLOB)
 F84=F85.checked_loader("f93b_exact_f84",R/"20261016-y-f84"/"forensic_reachability.py",F85.F84_SHA)
 F83=F84.load_f83();f83weights=F84.assert_frozen()
 pack=F83.M.PACK;native=F83.M.F62
 w90=verified_policy(R/"20261016-y-f90"/"frozen-policy.json",F90_POLICY,("weights_int8",))[0]
 w91=verified_policy(R/"20261016-y-f91"/"frozen-policy.json",F91_POLICY,("benefit_weights","harm_weights"))
 w92=verified_policy(R/"20261016-y-f92"/"frozen-policy.json",F92_POLICY,("benefit_weights","harm_weights"))
 rows=[]
 for seed in seeds:
  for family in cfg["families"]:
   public,q,meta=F83.M.SOURCE.source(seed,family)
   assert F84.independently_resolve_public(public,q)[0]=={q["answer"]}
   states={"f60":F84.audit_f60(F83,public,q)}
   states["f83"],t83,_=F83.online(public,f83weights,True,True)
   assert F83.M.AUDITOR.verify(public,q,t83)["prefixes"]==72
   states["f90"],t90,_=F90.online(public,w90,pack,native,True)
   assert F83.M.AUDITOR.verify(public,q,t90)["prefixes"]==72
   states["f91"],t91,_=F91.online(public,*w91,pack,native,True)
   assert F83.M.AUDITOR.verify(public,q,t91)["prefixes"]==72
   states["f92"],t92,_=F92.online(public,*w92,pack,native,F91,True)
   assert F83.M.AUDITOR.verify(public,q,t92)["prefixes"]==72
   states["f93b"],t93,detail=F93.online(public,patterns,pack,native,True)
   cert=F83.M.AUDITOR.verify(public,q,t93)
   assert cert["prefixes"]==72 and cert["max_payload_bytes"]<=144
   assert detail["interventions"]<=1 and detail["latch_bits"]==1
   row={"seed":seed,"family":family,"regime":meta["arrival_regime"],
     "kind":meta["question_type"],"interventions":detail["interventions"],
     "candidate_states":detail["scored_candidates"],"cap_events":detail["cap_events"],
     "memory_bytes":cert["max_payload_bytes"]}
   for name,mem in states.items():
    pred,diag=F85.solve_global(mem,{"start":q["start"],"ops":q["ops"]},pack)
    assert pred is None or pred==q["answer"],"F93B_WRONG_NONPUBLIC_ANSWER"
    assert not diag["resource_cap_triggered"] and diag["persistent_memory_bytes"]<=144
    row[name+"_correct"]=int(pred==q["answer"])
   rows.append(row)
 assert len(rows)==cfg["cases"]
 all_=subset(rows,lambda x:True)
 six=subset(rows,lambda x:x["kind"]=="crosslink_reach_6_steps")
 by={}
 for regime in ("original","local_rotate4"):
  by[regime]={}
  for kind in ("within_component_4_steps","crosslink_reach_6_steps"):
   by[regime][kind]=subset(rows,lambda x:x["regime"]==regime and x["kind"]==kind)
   assert by[regime][kind]["cases"]>0
 supported=six["rescue"]>0 and all_["regression"]==0
 return {"schema":"yggdrasil.f93b.grammar-holdout.v1",
  "stage":"F93B_FROZEN_VALIDATION" if mode=="validation" else "F93B_NEW_DISJOINT_GUARD",
  "classification":"synthetic_mechanism_supported" if supported else
    "synthetic_negative_inactive" if all_["interventions"]==0 else "synthetic_negative",
  "cases":len(rows),"six_step_cases":six["cases"],"scores":all_["correct"],
  "six_step_rescues":six["rescue"],"F60_correct_regressions":all_["regression"],
  "native_interventions":all_["interventions"],"cap_events":sum(r["cap_events"] for r in rows),
  "native_candidates_considered":sum(r["candidate_states"] for r in rows),
  "by_arrival_and_kind":by,"max_persistent_bytes":max(r["memory_bytes"] for r in rows),
  "frozen_grammar_bytes":18,"latch_bits":1,
  "source_public_prefixes_all_audited":True,"no_holdout_refit":True,
  "no_protected_source":True,"scientific_accepted":False,
  "optimizer_promotion":False,"rows":rows}
if __name__=="__main__":
 if sys.argv[1:]==["--validation"]:print(json.dumps(evaluate("validation"),sort_keys=True))
 elif sys.argv[1:]==["--guard"]:print(json.dumps(evaluate("guard"),sort_keys=True))
 else:raise SystemExit("Only disjoint synthetic holdout qualification permitted")
