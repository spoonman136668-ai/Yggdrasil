"""F63C independent frozen-control source feasibility on SYNTHETIC ONLY."""
import hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
expect={"prereg.json":"c0e69c1bc0a170646c8ad997efeb154b64ce9862",
        "source.py":"c04b73306861098eecf55db77b2db486aa918819",
        "audit_graph.py":"24e9f6d89d346eb019e44a51c59349a252cc50e2"}
for name,sha in expect.items():assert blob(P/name)==sha,(name,"IDENTITY_DRIFT")
def load(n,path):
 sp=importlib.util.spec_from_file_location(n,path)
 obj=importlib.util.module_from_spec(sp);sys.modules[n]=obj;sp.loader.exec_module(obj);return obj
prereg=json.loads((P/"prereg.json").read_text())
source=load("f63c_synthetic_source",P/"source.py")
audit=load("f63c_public_independent_auditor",P/"audit_graph.py")
old=load("f63c_frozen_f62_controls",P.parent/"20261015-y-f62"/"source_pilot.py")
f60,f59,f58,f61=old.controls();packing=old.codec()
rows=[]
for i in range(24):
 seed=-401-i;family=(-2,-1)[i%2]
 public,question,meta=source.source(seed,family)
 witness=audit.verify(public,question)
 scores={}
 for name,records in {
  "F60_fixed":f60.online_fixed(public),
  "F59_deferred":f59.fixed_deferred_component_buffer(public),
  "F58_frontier":f58.frontier_online(public),
  "F61_frozen_no_refit":f61.learned_online(public,old.F61_WEIGHTS)[0],
  "F62_frozen_no_refit":old.learned_online(public,(0,2,1,1,1,1,1,3,0,3,0,0),packing)[0]
 }.items():
  old._valid_memory(records,packing)
  scores[name]=int(packing.solve(records,question)==question["answer"])
 rows.append(dict(seed=seed,family=family,regime=meta["regime"],
  question_type=meta["question_type"],graph=witness,scores=scores))
assert len(rows)==24
n=len(rows)
counts={key:sum(r["scores"][key] for r in rows) for key in rows[0]["scores"]}
modes=sorted({x["regime"] for x in rows})
types=sorted({x["question_type"] for x in rows})
assert len(modes)==len(types)==2
assert all(r["graph"]["public_answer_unique"] for r in rows)
assert all("F60_fixed" in r["scores"] for r in rows)
assert all(not 801000<=r["seed"]<801016 for r in rows)
result=dict(schema="yggdrasil.f63c.synthetic-frozen-source-feasibility.v1",
 source_blobs=expect,stage="SYNTHETIC_ONLY",cases=n,
 frozen_control_correct=counts,regimes=modes,question_types=types,
 public_independent_witness_correct=n,
 f60_threshold=prereg["thresholds"]["f60_fixed_feasibility_min"],
 witness_threshold=prereg["thresholds"]["independent_public_witness_min"],
 f60_feasibility_pass=counts["F60_fixed"]/n>=prereg["thresholds"]["f60_fixed_feasibility_min"],
 public_witness_pass=True,
 eligible_for_first_FIT=False,
 fit_train_executed=False,fit_validation_executed=False,
 diag_executed=False,original_executed=False,
 scientific_qualified=False,F3=False,policy_promotion=False,rows=rows)
print(json.dumps(result,sort_keys=True))
