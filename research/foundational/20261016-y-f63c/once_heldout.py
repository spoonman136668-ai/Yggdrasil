"""Yggdrasil F63C one-time frozen prospective FIT VALIDATION.

This experiment may consume ONLY preregistered heldout seeds 801008–801015,
families 1540–1543; never train/refit/rerun or dispatch DIAG/original.
"""
from __future__ import annotations
import hashlib,importlib.util,json,os,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
OUT=pathlib.Path(os.environ["F63C_VALIDATION_EVIDENCE_DIR"])
OUT.mkdir(parents=True,exist_ok=True)
def gitblob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert gitblob(P/"prereg.json")=="c0e69c1bc0a170646c8ad997efeb154b64ce9862"
assert gitblob(P/"source.py")=="c04b73306861098eecf55db77b2db486aa918819"
assert gitblob(P/"audit_graph.py")=="24e9f6d89d346eb019e44a51c59349a252cc50e2"
assert gitblob(P/"frozen_model_receipt.json")=="a896895963b1cbfa59737ef2b35a3279483f4ebb"
def load(name,path):
 sp=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(sp);sys.modules[name]=m;sp.loader.exec_module(m);return m
prereg=json.loads((P/"prereg.json").read_text())
receipt=json.loads((P/"frozen_model_receipt.json").read_text())
v=prereg["fit"]
assert v["train_seeds"]==[801000,801008] and v["validate_seeds"]==[801008,801016]
assert v["families"]==[1540,1541,1542,1543]
assert receipt["fit_validate_executed"] is False
assert receipt["retraining_permitted"] is False
weights=tuple(receipt["frozen_reliability_int8_weights"])
assert len(weights)==4
assert hashlib.sha256(bytes(w%256 for w in weights)).hexdigest()==receipt["weights_sha256"]
source=load("f63c_frozen_validation_source",P/"source.py")
graph=load("f63c_public_graph_independent",P/"audit_graph.py")
learn=load("f63c_frozen_validation_learner",P.parent/"20261016-y-f63"/"learn_reliability.py")
auditor=load("f63c_readonly_prefix_audit",P.parent/"20261015-y-f62"/"audit_public.py")
f62=learn.f62
f60,f59,f58,f61=f62.controls()
codec=learn.packing
fair=("F60_fixed","F59_deferred","F58_frontier","F61_frozen_no_refit",
      "F62_frozen_no_refit","fixed_pair_triple_DAG","fixed_FIFO_hash")
rows=[]
rowpath=OUT/"heldout_once_rows.jsonl"
with rowpath.open("w",encoding="utf-8") as stream:
 for seed in range(*v["validate_seeds"]):
  for family in v["families"]:
   assert seed not in range(*v["train_seeds"])
   # Single-use exception to source()'s explicit registered-source
   # denial. Exact source SHA and unchanged validation cohort mandatory.
   for attempt in range(8):
    public,q,meta=source._create(seed,family,attempt)
    if source.public_witness(public,q)=={q["answer"]}:
     break
   else:raise AssertionError("REGISTERED_SOURCE_PUBLIC_UNIQUENESS_FAILED")
   topology=graph.verify(public,q)
   # Crucial information boundary: q is NEVER passed to online methods.
   learned,trace=learn.m.select(public,codec,weights,True)
   without,ablation_trace=learn.m.select(public,codec,weights,False)
   forensic=auditor.verify(public,q,trace)
   forensic_abl=auditor.verify(public,q,ablation_trace)
   assert forensic["prefixes"]==forensic_abl["prefixes"]==72
   assert forensic["max_payload_bytes"]<=144 and forensic_abl["max_payload_bytes"]<=144
   assert auditor.solve(tuple(auditor.decode(x) for x in trace[-1]),q)==codec.solve(learned,q)
   assert auditor.solve(tuple(auditor.decode(x) for x in ablation_trace[-1]),q)==codec.solve(without,q)
   score=dict(F63C_trained_reliability=int(codec.solve(learned,q)==q["answer"]),
       F63C_no_reliability_ablation=int(codec.solve(without,q)==q["answer"]))
   controls=dict(F60_fixed=f60.online_fixed(public),
       F59_deferred=f59.fixed_deferred_component_buffer(public),
       F58_frontier=f58.frontier_online(public),
       F61_frozen_no_refit=f61.learned_online(public,f62.F61_WEIGHTS)[0],
       F62_frozen_no_refit=f62.learned_online(public,(0,2,1,1,1,1,1,3,0,3,0,0),codec)[0],
       fixed_pair_triple_DAG=f61.fixed_online(public,"fixed_pair_triple_DAG"),
       fixed_FIFO_hash=f61.fixed_online(public,"FIFO_hash"))
   for name,memory in controls.items():
    f62._valid_memory(memory,codec)
    score[name]=int(codec.solve(memory,q)==q["answer"])
   row=dict(seed=seed,family=family,meta=meta,score=score,
     public=[list(x) for x in public],
     postretention_question={"start":q["start"],"ops":[list(op) for op in q["ops"]],"answer":q["answer"]},
     topology=topology,learned_prefix_trace=[list(x) for x in trace],
     ablation_prefix_trace=[list(x) for x in ablation_trace],
     independent_model_audit=forensic,independent_ablation_audit=forensic_abl,
     frozen_control_receipts={name:[codec.pack(*x).hex() for x in mem] for name,mem in controls.items()})
   stream.write(json.dumps(row,sort_keys=True)+"\n");stream.flush()
   rows.append(row)
assert len(rows)==32
totals={key:sum(r["score"][key] for r in rows)
       for key in rows[0]["score"]}
best=max(fair,key=lambda name:(totals[name],-fair.index(name)))
learned=totals["F63C_trained_reliability"]
ablated=totals["F63C_no_reliability_ablation"]
family_scores={}
for family in v["families"]:
 subset=[r for r in rows if r["family"]==family]
 family_scores[str(family)]=dict(
  trained=sum(r["score"]["F63C_trained_reliability"] for r in subset),
  strongest_fair=max(sum(r["score"][n] for r in subset) for n in fair))
passes=dict(
 absolute_F60_feasibility=(totals["F60_fixed"]/32>=prereg["thresholds"]["f60_fixed_feasibility_min"]),
 independent_public_witness=(all(r["topology"]["public_answer_unique"] for r in rows) and 1.0>=prereg["thresholds"]["independent_public_witness_min"]),
 gain_over_strongest_fair=(learned-totals[best])/32>=prereg["thresholds"]["heldout_gain_vs_best_equal_byte_min"],
 per_family_nondegradation=all(t["trained"]>=t["strongest_fair"] for t in family_scores.values()),
 reliability_feature_ablation_positive=(learned>ablated))
verdict=dict(schema="yggdrasil.f63c.once-authentic-heldout-science.v1",
    frozen_training_artifact=receipt["training_artifact_id"],
    frozen_weights_sha256=receipt["weights_sha256"],
    source_blob=receipt["source_blob"],prereg_blob=receipt["prereg_blob"],
    registered_validation_cases=32,fit_validation_seeds=v["validate_seeds"],
    fit_validation_families=v["families"],scores=totals,
    learned_correct=learned,ablation_correct=ablated,
    strongest_fair=best,strongest_fair_correct=totals[best],
    observed_gain=(learned-totals[best])/32,
    per_family=family_scores,preregistered_threshold_passes=passes,
    scientific_qualified=all(passes.values()),
    source_fit_train_rerun=False,fit_validate_consumed_once=True,
    diagnostics_executed=False,originals_executed=False,
    independent_F3=False,accepted_ref_mutation=False,policy_promotion=False,
    row_sha256=hashlib.sha256(rowpath.read_bytes()).hexdigest())
(OUT/"heldout_verdict.json").write_text(json.dumps(verdict,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print(json.dumps(verdict,sort_keys=True))
