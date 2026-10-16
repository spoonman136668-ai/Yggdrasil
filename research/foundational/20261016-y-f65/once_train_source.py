"""F65 once-only source-feasibility FIT TRAIN, before model fitting.

Only seeds 821000..821007/families 1580..1583. Do not touch protected
validation/diagnostic/original identities or accepted research refs.
"""
from __future__ import annotations
import hashlib,importlib.util,json,os,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent
OUT=pathlib.Path(os.environ["F65_TRAIN_SOURCE_EVIDENCE"])
OUT.mkdir(parents=True,exist_ok=True)
def gitblob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def load(name,path,expected):
 assert gitblob(path)==expected,(name,"IMMUTABLE_SOURCE_DRIFT")
 spec=importlib.util.spec_from_file_location(name,path)
 mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod)
 return mod
assert gitblob(HERE/"prereg.json")=="9bbfd50b740be2c9d4ec891b3b360cd9650b7e23"
assert gitblob(HERE/"path_assembly.py")=="10c2ba041c1d3e3063e1e98ba5726fa458db5f3a"
prereg=json.loads((HERE/"prereg.json").read_text())
c=prereg["fresh_cohorts"]
assert c["fit_train_seeds"]==[821000,821008]
assert c["fit_validation_seeds"]==[821008,821016]
assert c["fit_families"]==[1580,1581,1582,1583]
SOURCE=load("f65_exact_train_source",HERE.parent/"20261016-y-f63c"/"source.py",
            "c04b73306861098eecf55db77b2db486aa918819")
GRAPH=load("f65_independent_train_topology",HERE.parent/"20261016-y-f63c"/"audit_graph.py",
           "24e9f6d89d346eb019e44a51c59349a252cc50e2")
F62=load("f65_exact_old_comparators",HERE.parent/"20261015-y-f62"/"source_pilot.py",
         "7ed72deca5584d7c0b6562d74456fa7d4bee6712")
F63=load("f65_exact_f63c_comparator",HERE.parent/"20261016-y-f63"/"learn_reliability.py",
        "4eef37159bb96e90cf7f89c4dc0ed91b6d9d23c5")
F64=load("f65_exact_f64_comparator",HERE.parent/"20261016-y-f64"/"bridge_features.py",
        "75d952228c53cf9d41d1cb557fee27e421a96972")
f60,f59,f58,f61=F62.controls()
pack=F62.codec()
rows=[]
path=OUT/"fit_train_rows.jsonl"
with path.open("w",encoding="utf-8") as stream:
 for seed in range(*c["fit_train_seeds"]):
  for family in c["fit_families"]:
   assert seed not in range(*c["fit_validation_seeds"])
   for attempt in range(8):
    public,q,meta=SOURCE._create(seed,family,attempt)
    if SOURCE.public_witness(public,q)=={q["answer"]}:break
   else:raise AssertionError("REGISTERED_TRAIN_SOURCE_NOT_PUBLICLY_UNIQUE")
   proof=GRAPH.verify(public,q)
   frozen={
     "F60_fixed":f60.online_fixed(public),
     "F59_deferred":f59.fixed_deferred_component_buffer(public),
     "F58_frontier":f58.frontier_online(public),
     "F61_frozen":f61.learned_online(public,F62.F61_WEIGHTS)[0],
     "F62_frozen":F62.learned_online(public,(0,2,1,1,1,1,1,3,0,3,0,0),pack)[0],
     "F63C_frozen":F63.m.select(public,pack,(50,93,45,100),True)[0],
     "F64_frozen":F64.online(public,(6,-5,13,0,2,2,1,-1))}
   score={}
   for name,memory in frozen.items():
    F62._valid_memory(memory,pack)
    score[name]=int(pack.solve(memory,q)==q["answer"])
   row=dict(seed=seed,family=family,meta=meta,
     public_events=[list(e) for e in public],
     postretention_question={"start":q["start"],
        "ops":[list(op) for op in q["ops"]],"answer":q["answer"]},
     independent_audit=proof,controls=score)
   stream.write(json.dumps(row,sort_keys=True)+"\n")
   stream.flush();rows.append(row)
assert len(rows)==32
totals={name:sum(row["controls"][name] for row in rows) for name in rows[0]["controls"]}
thresholds=dict(F60_source_feasibility=totals["F60_fixed"]/32>=prereg["gates"]["source_fixed_F60_accuracy_min"],
    public_witness=all(row["independent_audit"]["public_answer_unique"] for row in rows))
result=dict(schema="yggdrasil.f65.first-use-train-only-source-feasibility.v1",
 qualified_source_head="fb8013361d3b41b0a73c85302a40524ea19b3683",
 pretrained_model_used=False,train_cases=len(rows),
 train_seed_range=c["fit_train_seeds"],families=c["fit_families"],
 frozen_control_correct=totals,preregistered_threshold_passes=thresholds,
 eligible_for_separate_model_fit=all(thresholds.values()),
 rows_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
 fit_train_consumed_once=True,fit_validation_consumed=False,
 diagnostic_consumed=False,original_consumed=False,F3=False,
 accepted_ref_mutated=False,scientific_improvement_qualified=False,
 optimizer_promotion=False)
(OUT/"source_first_use_verdict.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
print(json.dumps(result,sort_keys=True))
