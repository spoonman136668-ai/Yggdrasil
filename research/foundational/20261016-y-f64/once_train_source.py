"""F64 first authentic FIT TRAIN SOURCE ONLY; learned weights NOT fitted here.

Strict one-time registered training cohort 811000-811007; heldout FIT,
diagnostic and original sources are unavailable. Original source() denies
all registered identities; this wrapper is their exact authorized exception.
"""
from __future__ import annotations
import hashlib,importlib.util,json,os,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
OUT=pathlib.Path(os.environ["F64_FIRST_USE_EVIDENCE"])
OUT.mkdir(parents=True,exist_ok=True)
def sha(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert sha(P/"prereg.json")=="aa12b1785b92eec5eb5096d6ef0cd600e97904ad"
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p)
 m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
spec=json.loads((P/"prereg.json").read_text())
c=spec["cohorts"]
assert c["fit_train_seeds"]==[811000,811008]
assert c["fit_validate_seeds"]==[811008,811016]
assert c["fit_families"]==[1560,1561,1562,1563]
oldpath=P.parent/"20261016-y-f63c"/"source.py"
assert sha(oldpath)=="c04b73306861098eecf55db77b2db486aa918819"
source=load("f64_exact_source_F63C",oldpath)
graphpath=P.parent/"20261016-y-f63c"/"audit_graph.py"
assert sha(graphpath)=="24e9f6d89d346eb019e44a51c59349a252cc50e2"
auditor=load("f64_source_independent_graph",graphpath)
f62=load("f64_unchanged_frozen_controls",P.parent/"20261015-y-f62"/"source_pilot.py")
f60,f59,f58,f61=f62.controls()
l=load("f64_frozen_F63C_model",P.parent/"20261016-y-f63"/"learn_reliability.py")
codec=f62.codec()
rows=[];path=OUT/"fit_train_rows.jsonl"
with path.open("w",encoding="utf-8") as stream:
 for seed in range(*c["fit_train_seeds"]):
  for family in c["fit_families"]:
   assert seed not in range(*c["fit_validate_seeds"])
   for attempt in range(8):
    public,q,meta=source._create(seed,family,attempt)
    if source.public_witness(public,q)=={q["answer"]}:break
   else:raise AssertionError("F64_REGISTERED_GRAPH_NOT_UNIQUE")
   proof=auditor.verify(public,q)
   historical={
     "F60_fixed":f60.online_fixed(public),
     "F59_deferred":f59.fixed_deferred_component_buffer(public),
     "F58_frontier":f58.frontier_online(public),
     "F61_frozen":f61.learned_online(public,f62.F61_WEIGHTS)[0],
     "F62_frozen":f62.learned_online(public,(0,2,1,1,1,1,1,3,0,3,0,0),codec)[0],
     "F63C_frozen":l.m.select(public,codec,(50,93,45,100),True)[0]}
   scores={}
   for name,retained in historical.items():
    f62._valid_memory(retained,codec)
    scores[name]=int(codec.solve(retained,q)==q["answer"])
   row=dict(seed=seed,family=family,
       meta=meta,public=[list(e) for e in public],
       postretention_question=dict(start=q["start"],ops=[list(x) for x in q["ops"]],answer=q["answer"]),
       independent_public_topology=proof,control_scores=scores)
   stream.write(json.dumps(row,sort_keys=True)+"\n");stream.flush()
   rows.append(row)
assert len(rows)==32
counts={key:sum(r["control_scores"][key] for r in rows)
     for key in rows[0]["control_scores"]}
gates=dict(frozen_F60_feasibility=counts["F60_fixed"]/32>=spec["gates"]["source_feasibility_F60_min"],
 independent_public_witness=all(r["independent_public_topology"]["public_answer_unique"] for r in rows))
report=dict(schema="yggdrasil.f64.first-authentic-fit-train-source.v1",
 source_qualified_head="98692c30d5352256a1131dcfd6e11fc6a6bba129",
 reused_parent_source_blob=sha(oldpath),
 prereg_blob=sha(P/"prereg.json"),
 FIT_train_cases=32,fit_train_range=c["fit_train_seeds"],fit_families=c["fit_families"],
 source_baseline_correct=counts,threshold_passes=gates,
 eligible_for_f64_model_training=all(gates.values()),FIT_train_consumed_once=True,
 fit_validation_executed=False,diagnostics_executed=False,originals_executed=False,
 independent_F3=False,scientific_improvement_qualified=False,policy_promotion=False,
 rows_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
(OUT/"train_source_verdict.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
print(json.dumps(report,sort_keys=True))
