"""F66B one-time prospective FIT TRAIN source feasibility; no model fitting.

Strict 32 preregistered seeds/families, immutable F63C generator and frozen
controls. No validation, diagnostics, protected originals or policy promotion.
"""
from __future__ import annotations
import hashlib,importlib.util,json,os,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
OUT=pathlib.Path(os.environ["F66B_ONCE_TRAIN_SOURCE_EVIDENCE"])
OUT.mkdir(parents=True,exist_ok=True)
def sha(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def load(name,path,expected):
 assert sha(path)==expected,("FROZEN_SOURCE_DRIFT",name)
 s=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
assert sha(P/"prereg.json")=="fc3283f28ab307b6834c93d530fffce98ad7c0de"
assert sha(P/"prereg-opportunity-cost-amendment.json")=="3502d23f503cb0fdc798b2ac7db3f5cdb09c254d"
spec=json.loads((P/"prereg.json").read_text())
c=spec["cohorts"]
assert c["fit_train_seeds"]==[831000,831008]
assert c["fit_validate_seeds"]==[831008,831016]
assert c["fit_families"]==[1600,1601,1602,1603]
SRC=load("f66b_exact_generator",P.parent/"20261016-y-f63c"/"source.py","c04b73306861098eecf55db77b2db486aa918819")
GRAPH=load("f66b_independent_graph",P.parent/"20261016-y-f63c"/"audit_graph.py","24e9f6d89d346eb019e44a51c59349a252cc50e2")
F62=load("f66b_sha_pinned_historical",P.parent/"20261015-y-f62"/"source_pilot.py","7ed72deca5584d7c0b6562d74456fa7d4bee6712")
F63=load("f66b_frozen_f63c",P.parent/"20261016-y-f63"/"learn_reliability.py","4eef37159bb96e90cf7f89c4dc0ed91b6d9d23c5")
F64=load("f66b_frozen_f64",P.parent/"20261016-y-f64"/"bridge_features.py","75d952228c53cf9d41d1cb557fee27e421a96972")
F65=load("f66b_frozen_f65",P.parent/"20261016-y-f65"/"path_assembly.py","10c2ba041c1d3e3063e1e98ba5726fa458db5f3a")
f60,f59,f58,f61=F62.controls()
pack=F62.codec()
rows=[]
path=OUT/"fit_train_rows.jsonl"
with path.open("w",encoding="utf-8") as stream:
 for seed in range(*c["fit_train_seeds"]):
  for family in c["fit_families"]:
   assert seed not in range(*c["fit_validate_seeds"])
   for attempt in range(8):
    public,q,meta=SRC._create(seed,family,attempt)
    if SRC.public_witness(public,q)=={q["answer"]}:break
   else:raise AssertionError("PROTECTED_SOURCE_PUBLIC_UNIQUENESS_FAIL")
   independent=GRAPH.verify(public,q)
   old={
    "F60_fixed":f60.online_fixed(public),
    "F59_deferred":f59.fixed_deferred_component_buffer(public),
    "F58_frontier":f58.frontier_online(public),
    "F61_frozen":f61.learned_online(public,F62.F61_WEIGHTS)[0],
    "F62_frozen":F62.learned_online(public,(0,2,1,1,1,1,1,3,0,3,0,0),pack)[0],
    "F63C_frozen":F63.m.select(public,pack,(50,93,45,100),True)[0],
    "F64_frozen":F64.online(public,(6,-5,13,0,2,2,1,-1)),
    "F65_frozen":F65.online(public,(0,0,-3,2,8,2,0,-1,-1,0,-1,0,0,0,0,0))}
   scores={}
   for name,records in old.items():
    F62._valid_memory(records,pack)
    scores[name]=int(pack.solve(records,q)==q["answer"])
   row=dict(seed=seed,family=family,regime=meta["regime"],question_type=meta["question_type"],
       public_events=[list(e) for e in public],
       postretention_question=dict(start=q["start"],ops=[list(op) for op in q["ops"]],answer=q["answer"]),
       independent_graph=independent,frozen_control_scores=scores)
   stream.write(json.dumps(row,sort_keys=True)+"\n");stream.flush()
   rows.append(row)
assert len(rows)==32
totals={name:sum(row["frozen_control_scores"][name] for row in rows) for name in rows[0]["frozen_control_scores"]}
criteria=dict(F60_feasibility=totals["F60_fixed"]/32>=spec["gates"]["source_F60_feasibility_min"],
 public_graph_witness=all(row["independent_graph"]["public_answer_unique"] for row in rows))
result=dict(schema="yggdrasil.f66b.authentic-once-train-only-source.v1",
 trained_model_exists=False,source_qualified_head="bba0389206e8c4c5d50b50e56bac121647de4384",
 first_use_train_seeds=c["fit_train_seeds"],first_use_families=c["fit_families"],
 cases=32,control_correct=totals,
 threshold_passes=criteria,eligible_for_separate_model_fit=all(criteria.values()),
 rows_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
 FIT_train_consumed_once=True,FIT_validation_consumed=False,DIAG_consumed=False,
 original_consumed=False,F3=False,scientific_improvement_qualified=False,
 accepted_ref_mutation=False,optimizer_promotion=False)
(OUT/"source_first_use.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
print(json.dumps(result,sort_keys=True))
