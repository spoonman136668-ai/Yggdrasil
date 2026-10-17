"""F98 immutable public microchain qualified holdout, no training or model selection.

Exactly the same graph, task and true answer are exposed in frozen original
and rotate4 public arrival orders per source identity. F98 online controller
receives neither the eventual task nor the original/rotate4 treatment label.
All 72 source-native F62 audit prefixes and the immutable F85 solver are used.
"""
from __future__ import annotations
import hashlib,importlib.util,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parent
PREREG="7288b566b6c5d80690ef2c1bb5021d7d78d4530a"
METHOD="4a03573c31d24decd9a058c4930a8e9a6fbc1f3f"
FROZEN_GRAMMAR="67ae62a79cbba0d7287bc324e6df32a5277faccb"
COHORTS={"validation":range(-6421,-6429,-1),"guard":range(-6441,-6457,-1)}
FAMILIES=(-2,-1)

def blob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def load(name,path,expected):
 assert blob(path)==expected,("F98_FROZEN_SOURCE_IDENTITY_DRIFT",name)
 spec=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
 return m

def provenance():
 assert blob(P/"prereg.json")==PREREG
 assert blob(P/"frozen-grammar.json")==FROZEN_GRAMMAR
 prereg=json.loads((P/"prereg.json").read_text())
 frozen=json.loads((P/"frozen-grammar.json").read_text())
 assert prereg["stage"]=="FROZEN_PRECODE_TRAIN_ONLY_THEN_SEALED_VALIDATION_GUARD"
 assert frozen["stage"]=="TRAINED_SELF_SUPERVISED_GRAMMAR_FROZEN_BEFORE_VALIDATION_OR_GUARD"
 assert frozen["train_run_id"]==38988128570
 assert frozen["method_git_blob"]==METHOD
 pairs=tuple(tuple(x) for x in frozen["role_code_bigrams"])
 assert len(pairs)==16 and all(len(x)==2 and all(0<=v<=7 for v in x) for x in pairs)
 assert len(set(pairs))==16
 assert hashlib.sha256(bytes(v for pair in pairs for v in pair)).hexdigest()==frozen["raw_32_byte_grammar_sha256"]
 assert frozen["raw_32_byte_grammar_sha256"]=="6fa6248824feab147a6984e50132c59ab11bdc3a781f214dbf243f694c204e2f"
 assert frozen["validation_accessed"] is False and frozen["guard_accessed"] is False
 return prereg,pairs

def aggregate(rows,filter_fn):
 subset=[x for x in rows if filter_fn(x)]
 return dict(cases=len(subset),
  correct={name:sum(r[name+"_correct"] for r in subset) for name in ("f60","f83","f98")},
  F60_rescues=sum(not r["f60_correct"] and r["f98_correct"] for r in subset),
  F60_regressions=sum(r["f60_correct"] and not r["f98_correct"] for r in subset),
  native_deviations=sum(r["f98_deviations"] for r in subset),
  gross_microchain_bigram_gain=sum(r["f98_new_bigram_gain"] for r in subset))

def evaluate(mode):
 pre,grammar=provenance()
 cohort=pre["cohorts"][mode]
 seeds=COHORTS[mode]
 assert list(seeds)==list(range(cohort["start"],cohort["stop_exclusive"],cohort["step"]))
 assert len(seeds)*2==cohort["distinct_graphs"]
 F98=load("f98_frozen_controller",P/"microchain.py",METHOD)
 F97,F96,F83,F84,F85,F62,pack=F98.dependencies()
 weights83=F84.assert_frozen()
 rows=[]
 for seed in seeds:
  for family in FAMILIES:
   observed,q,meta=F83.M.SOURCE.source(seed,family)
   orig,rot=F96.matched_orders(observed,meta["arrival_regime"],F83.M.SOURCE)
   assert F84.independently_resolve_public(orig,q)[0]==frozenset({q["answer"]})
   assert F84.independently_resolve_public(rot,q)[0]==frozenset({q["answer"]})
   for arrival,public in (("original",orig),("local_rotate4",rot)):
    control=F84.audit_f60(F83,public,q)
    f83,t83,_=F83.online(public,weights83,True,True)
    cert83=F83.M.AUDITOR.verify(public,q,t83)
    assert cert83["prefixes"]==72 and cert83["max_payload_bytes"]<=144
    learned,trace,stats=F98.online(public,grammar,pack,F62,True)
    audit=F83.M.AUDITOR.verify(public,q,trace)
    assert audit["prefixes"]==72 and audit["max_payload_bytes"]<=144
    assert stats["interventions"]<=2 and stats["extra_latch_bits"]==2 and stats["model_extra_bytes"]==32
    row=dict(seed=seed,source_family=family,arrival=arrival,
      question_type=meta["question_type"],
      f98_deviations=stats["interventions"],
      f98_native_alternatives_examined=stats["candidates_considered"],
      f98_new_bigram_gain=stats["gross_new_bigrams"],
      f98_retained_bytes=audit["max_payload_bytes"])
    for name,records in (("f60",control),("f83",f83),("f98",learned)):
     prediction,cost=F85.solve_global(records,
       {"start":q["start"],"ops":q["ops"]},pack)
     assert prediction is None or prediction==q["answer"],"F98_ILLEGAL_PUBLIC_PREDICTION"
     assert not cost["resource_cap_triggered"] and cost["persistent_memory_bytes"]<=144
     row[name+"_correct"]=int(prediction==q["answer"])
    rows.append(row)
 assert len(rows)==cohort["paired_order_episodes"]
 all_rows=aggregate(rows,lambda x:True)
 six=aggregate(rows,lambda x:x["question_type"]=="crosslink_reach_6_steps")
 four=aggregate(rows,lambda x:x["question_type"]=="within_component_4_steps")
 by_arrival={}
 for arrival in ("original","local_rotate4"):
  by_arrival[arrival]={}
  for task in ("within_component_4_steps","crosslink_reach_6_steps"):
   a=aggregate(rows,lambda x:x["arrival"]==arrival and x["question_type"]==task)
   assert a["cases"]>0
   by_arrival[arrival][task]=a
 qualified=six["F60_rescues"]>=1 and all_rows["F60_regressions"]==0
 return dict(
  schema="yggdrasil.f98.native-microchain.frozen-paired-evaluation.v1",
  stage="FROZEN_VALIDATION_ONLY" if mode=="validation" else "FIRST_USE_SEALED_SYNTHETIC_GUARD",
  classification="synthetic_mechanism_supported" if qualified else
    "synthetic_negative_inactive" if all_rows["native_deviations"]==0 else "synthetic_negative_active",
  paired_graphs=len(seeds)*2,order_episodes=len(rows),
  six_step_episodes=six["cases"],four_step_episodes=four["cases"],
  scores=all_rows["correct"],six_step_rescues=six["F60_rescues"],
  four_step_regressions=four["F60_regressions"],
  F60_correct_case_regressions=all_rows["F60_regressions"],
  native_deviations=all_rows["native_deviations"],
  gross_microchain_bigram_gain=all_rows["gross_microchain_bigram_gain"],
  by_arrival_and_question_type=by_arrival,
  grammar_sha256="6fa6248824feab147a6984e50132c59ab11bdc3a781f214dbf243f694c204e2f",
  retained_memory_max_bytes=max(r["f98_retained_bytes"] for r in rows),
  extra_frozen_model_bytes=32,extra_latch_bits=2,
  exact_native_72_prefix_audit_passed=True,
  paired_graph_same_edges_and_answer=True,
  F85_solver_no_resource_caps=True,
  no_model_selection_or_refit=True,no_future_question_leakage_into_online=True,
  FIT_used=False,DIAG_used=False,ORIGINAL_used=False,F3_used=False,
  independent_science_accepted=False,optimizer_promotion=False,controller_mutation=False,
  rows=rows)
if __name__=="__main__":
 if sys.argv[1:]==["--frozen-validation"]:print(json.dumps(evaluate("validation"),sort_keys=True))
 elif sys.argv[1:]==["--frozen-guard"]:print(json.dumps(evaluate("guard"),sort_keys=True))
 else:raise SystemExit("F98 holdout denies any fitting, source selector or protected original")
