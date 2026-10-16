"""F63C frozen-weight independent synthetic causal replay. No protected FIT."""
from __future__ import annotations
import hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def gitblob(path):
 b=path.read_bytes();return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert gitblob(P/"frozen_model_receipt.json")=="a896895963b1cbfa59737ef2b35a3279483f4ebb"
assert gitblob(P/"source.py")=="c04b73306861098eecf55db77b2db486aa918819"
assert gitblob(P/"prereg.json")=="c0e69c1bc0a170646c8ad997efeb154b64ce9862"
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
receipt=json.loads((P/"frozen_model_receipt.json").read_text())
weights=tuple(receipt["frozen_reliability_int8_weights"])
assert len(weights)==4
assert hashlib.sha256(bytes(w%256 for w in weights)).hexdigest()==receipt["weights_sha256"]
assert receipt["fit_validate_executed"] is False and receipt["retraining_permitted"] is False
source=load("f63c_preval_source",P/"source.py")
learn=load("f63c_preval_frozen_reliability",P.parent/"20261016-y-f63"/"learn_reliability.py")
auditor=load("f63c_preval_independent_public_auditor",P.parent/"20261015-y-f62"/"audit_public.py")
f62=learn.f62
f60,f59,f58,f61=f62.controls()
codec=learn.packing
rows=[]
for i in range(24):
 seed=-601-i;family=(-2,-1)[i%2]
 public,q,meta=source.source(seed,family)
 model,trace=learn.m.select(public,codec,weights,True)
 ablated,ablation_trace=learn.m.select(public,codec,weights,False)
 proof=auditor.verify(public,q,trace)
 ablation_proof=auditor.verify(public,q,ablation_trace)
 assert proof["prefixes"]==ablation_proof["prefixes"]==72
 assert proof["max_payload_bytes"]<=144 and ablation_proof["max_payload_bytes"]<=144
 assert auditor.solve(tuple(auditor.decode(s) for s in trace[-1]),q)==codec.solve(model,q)
 assert auditor.solve(tuple(auditor.decode(s) for s in ablation_trace[-1]),q)==codec.solve(ablated,q)
 score={"trained_frozen_reliability":int(codec.solve(model,q)==q["answer"]),
        "reliability_disabled_ablation":int(codec.solve(ablated,q)==q["answer"])}
 for name,records in {
    "F60_fixed":f60.online_fixed(public),
    "F59_deferred":f59.fixed_deferred_component_buffer(public),
    "F58_frontier":f58.frontier_online(public),
    "F61_frozen_no_refit":f61.learned_online(public,f62.F61_WEIGHTS)[0],
    "F62_frozen_no_refit":f62.learned_online(public,(0,2,1,1,1,1,1,3,0,3,0,0),codec)[0],
    "fixed_pair_triple_DAG":f61.fixed_online(public,"fixed_pair_triple_DAG"),
    "fixed_FIFO_hash":f61.fixed_online(public,"FIFO_hash"),
 }.items():
    f62._valid_memory(records,codec)
    score[name]=int(codec.solve(records,q)==q["answer"])
 rows.append(dict(seed=seed,family=family,question_type=meta["question_type"],
   arrival_regime=meta["regime"],max_bytes=proof["max_payload_bytes"],scores=score))
totals={name:sum(r["scores"][name] for r in rows) for name in rows[0]["scores"]}
print(json.dumps(dict(schema="yggdrasil.f63c.frozen-synthetic-prevalidation.v1",
 stage="SYNTHETIC_INDEPENDENT_AUDIT_ONLY",model_weights=list(weights),
 weight_identity=receipt["weights_sha256"],cases=len(rows),
 independent_public_prefix_audit_pass=True,
 scores=totals,positive_reliability_ablation_on_synthetic=totals["trained_frozen_reliability"]>totals["reliability_disabled_ablation"],
 fit_train_rerun=False,fit_validation_executed=False,diagnostics_executed=False,
 originals_executed=False,F3=False,policy_promotion=False,
 result_only_prevalidation_not_scientific_qualification=True,rows=rows),sort_keys=True))
