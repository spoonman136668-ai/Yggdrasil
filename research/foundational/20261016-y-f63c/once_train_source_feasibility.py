"""F63C once-only protected FIT TRAIN *SOURCE FEASIBILITY*, not model fitting.

Requires preceding exact-source qualification PASS at 9c6b757f..., GitHub
guarded one-time workflow, pinned source/prereg/auditor and existing frozen
control identities. Heldout FIT, DIAG, originals and F3 are NEVER called.
"""
from __future__ import annotations
import hashlib,importlib.util,json,os,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent
EVIDENCE=pathlib.Path(os.environ["F63C_EVIDENCE_DIR"])
EVIDENCE.mkdir(parents=True,exist_ok=True)
def blob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
PINNED={
 "prereg.json":"c0e69c1bc0a170646c8ad997efeb154b64ce9862",
 "source.py":"c04b73306861098eecf55db77b2db486aa918819",
 "audit_graph.py":"24e9f6d89d346eb019e44a51c59349a252cc50e2"}
for name,expected in PINNED.items():
 assert blob(HERE/name)==expected,("SOURCE_DRIFT",name)
def module(name,path):
 sp=importlib.util.spec_from_file_location(name,path)
 o=importlib.util.module_from_spec(sp);sys.modules[name]=o;sp.loader.exec_module(o);return o
prereg=json.loads((HERE/"prereg.json").read_text())
cohort=prereg["fit"]
assert cohort["train_seeds"]==[801000,801008]
assert cohort["validate_seeds"]==[801008,801016]
assert cohort["families"]==[1540,1541,1542,1543]
assert prereg["engineering"]["never_run_registered_before_first_use"] is True
source=module("f63c_once_source",HERE/"source.py")
auditor=module("f63c_once_independent_public_auditor",HERE/"audit_graph.py")
f62=module("f63c_once_sha_pinned_controls",HERE.parent/"20261015-y-f62"/"source_pilot.py")
f60,f59,f58,f61=f62.controls()
codec=f62.codec()
names=("F60_fixed","F59_deferred","F58_frontier","F61_frozen_no_refit","F62_frozen_no_refit")
assert all(name in names for name in names)
trained_f62=(0,2,1,1,1,1,1,3,0,3,0,0)
rows=[]
path=EVIDENCE/"first_use_rows.jsonl"
with path.open("w",encoding="utf-8") as stream:
 for seed in range(*cohort["train_seeds"]):
  for family in cohort["families"]:
   # Protected seeds are reachable ONLY from this SHA-pinned, one-time
   # explicitly authorized FIT TRAIN wrapper. source.source() still denies.
   assert seed not in range(*cohort["validate_seeds"])
   for attempt in range(8):
    public,q,meta=source._create(seed,family,attempt)
    if source.public_witness(public,q)=={q["answer"]}:
     break
   else:raise AssertionError("NEW_SOURCE_FAILED_EIGHT_UNIQUENESS_RETRIES")
   witness=auditor.verify(public,q)
   baseline={
    "F60_fixed":f60.online_fixed(public),
    "F59_deferred":f59.fixed_deferred_component_buffer(public),
    "F58_frontier":f58.frontier_online(public),
    "F61_frozen_no_refit":f61.learned_online(public,f62.F61_WEIGHTS)[0],
    "F62_frozen_no_refit":f62.learned_online(public,trained_f62,codec)[0]}
   score={}
   for name,retained in baseline.items():
    f62._valid_memory(retained,codec)
    score[name]=int(codec.solve(retained,q)==q["answer"])
   row=dict(seed=seed,family=family,meta=meta,
      public_events=[list(e) for e in public],
      postretention_question={"start":q["start"],
         "ops":[list(op) for op in q["ops"]],"answer":q["answer"]},
      independent_audit=witness,scores=score)
   stream.write(json.dumps(row,sort_keys=True)+"\n");stream.flush()
   rows.append(row)
assert len(rows)==32
counts={key:sum(row["scores"][key] for row in rows) for key in names}
source_fixed=counts["F60_fixed"]/32
witness_fraction=sum(int(row["independent_audit"]["public_answer_unique"])
 for row in rows)/32
passes=dict(frozen_F60_source_feasibility=source_fixed>=prereg["thresholds"]["f60_fixed_feasibility_min"],
    source_independent_public_witness=witness_fraction>=prereg["thresholds"]["independent_public_witness_min"])
result=dict(schema="yggdrasil.f63c.first-registered-fit-train-source-feasibility.v1",
 source_qualified_head="9c6b757f62cbc1ecbc4fc32f59bc36fa44902303",
 pinned_git_blobs=PINNED,fit_train=[801000,801008],
 fit_families=cohort["families"],cases=len(rows),
 frozen_control_correct=counts,f60_source_accuracy=source_fixed,
 public_witness_accuracy=witness_fraction,preregistered_gates=passes,
 eligible_for_separate_fit_model_training=all(passes.values()),
 scientific_improvement_qualified=False,fit_train_used_once=True,
 fit_validation_executed=False,diagnostics_executed=False,
 originals_executed=False,F3=False,policy_promotion=False,
 exact_rows_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
(EVIDENCE/"source_feasibility_verdict.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
print(json.dumps({k:v for k,v in result.items() if k!="pinned_git_blobs"},sort_keys=True))
