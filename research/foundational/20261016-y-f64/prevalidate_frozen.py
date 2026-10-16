"""F64 independent frozen-weight synthetic audit, NO registered FIT or heldout.

Runs signed-int8 bridge model and its pre-specified feature ablation on
source-only negative seeds, with independent 72-prefix causal replay.
"""
import hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
PINNED={"frozen_model_receipt.json":"bc4672326454bceeabc4374afa2b55fbcdae3e65",
        "prereg.json":"aa12b1785b92eec5eb5096d6ef0cd600e97904ad",
        "bridge_features.py":"75d952228c53cf9d41d1cb557fee27e421a96972"}
for filename,digest in PINNED.items():
 assert blob(P/filename)==digest,("F64_FROZEN_BLOB_DRIFT",filename)
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
receipt=json.loads((P/"frozen_model_receipt.json").read_text())
pre=json.loads((P/"prereg.json").read_text())
weights=tuple(receipt["frozen_int8_weights"])
assert len(weights)==8 and all(type(x) is int and -127<=x<=127 for x in weights)
assert hashlib.sha256(bytes(x%256 for x in weights)).hexdigest()==receipt["weights_sha256"]
assert receipt["heldout_consumed"] is False and receipt["no_retraining"] is True
FEATURE=load("f64_independent_prevalidation_public_model",P/"bridge_features.py")
F62=FEATURE.BASE
f60,f59,f58,f61=F62.controls()
auditor=FEATURE.AUDIT
PACK=FEATURE.PACK
F63=load("f64_frozen_f63_comp",P.parent/"20261016-y-f63"/"learn_reliability.py")
totals={}
rows=[]
for n in range(24):
 seed=-901-n;family=(-2,-1)[n%2]
 public,q,meta=FEATURE.SOURCE.source(seed,family)
 assert len(public)==72 and all(len(e)==3 for e in public)
 trained,trace=FEATURE.online(public,weights,trace=True)
 ablated,ablation_trace=FEATURE.online(public,weights,trace=True,bridge_features=False)
 p1=auditor.verify(public,q,trace)
 p2=auditor.verify(public,q,ablation_trace)
 assert p1["prefixes"]==p2["prefixes"]==72
 assert p1["max_payload_bytes"]<=144 and p2["max_payload_bytes"]<=144
 assert auditor.solve(tuple(auditor.decode(h) for h in trace[-1]),q)==PACK.solve(trained,q)
 assert auditor.solve(tuple(auditor.decode(h) for h in ablation_trace[-1]),q)==PACK.solve(ablated,q)
 scores={"F64_frozen_bridge_credit":int(PACK.solve(trained,q)==q["answer"]),
         "F64_no_bridge_feature_ablation":int(PACK.solve(ablated,q)==q["answer"])}
 controls={
    "F60_fixed":f60.online_fixed(public),
    "F59_deferred":f59.fixed_deferred_component_buffer(public),
    "F58_frontier":f58.frontier_online(public),
    "F61_frozen_no_refit":f61.learned_online(public,F62.F61_WEIGHTS)[0],
    "F62_frozen_no_refit":F62.learned_online(public,(0,2,1,1,1,1,1,3,0,3,0,0),PACK)[0],
    "F63C_frozen_no_refit":F63.m.select(public,PACK,(50,93,45,100),True)[0],
    "fixed_pair_triple_DAG":f61.fixed_online(public,"fixed_pair_triple_DAG"),
    "fixed_FIFO_hash":f61.fixed_online(public,"FIFO_hash"),
 }
 for label,mem in controls.items():
  F62._valid_memory(mem,PACK)
  scores[label]=int(PACK.solve(mem,q)==q["answer"])
 for key,value in scores.items():totals[key]=totals.get(key,0)+value
 rows.append(dict(seed=seed,family=family,question_type=meta["question_type"],regime=meta["regime"],
    scores=scores,max_bytes=p1["max_payload_bytes"],ablation_max_bytes=p2["max_payload_bytes"]))
result=dict(schema="yggdrasil.f64.frozen-synthetic-prevalidation.v1",
 status="PREVALIDATION_ONLY",source_qualified_head="98692c30d5352256a1131dcfd6e11fc6a6bba129",
 weights=list(weights),weights_sha256=receipt["weights_sha256"],
 cases=len(rows),scores=totals,
 positive_bridge_ablation_on_synthetic=totals["F64_frozen_bridge_credit"]>totals["F64_no_bridge_feature_ablation"],
 independent_prefix_causality_pass=True,
 fit_train_reused=False,fit_validation_consumed=False,
 diagnostic_consumed=False,original_consumed=False,
 scientific_improvement_qualified=False,F3=False,policy_promotion=False,rows=rows)
print(json.dumps(result,sort_keys=True))
