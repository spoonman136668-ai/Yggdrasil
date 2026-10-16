"""F64 independent frozen synthetic replay. Registered cohorts are inaccessible.

Source is called only for negative engineering seeds. A genuinely independent
auditor verifies every public-prefix transition and byte bound. All accuracy
statistics are advisory; no synthetic tuning or claims of heldout success.
"""
from __future__ import annotations
import hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def gitblob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert gitblob(P/"frozen_model_receipt.json")=="122b5cfd0463ab0f5d95a10cd123e934e91d5210"
assert gitblob(P/"prereg.json")=="aa12b1785b92eec5eb5096d6ef0cd600e97904ad"
assert gitblob(P/"bridge_features.py")=="75d952228c53cf9d41d1cb557fee27e421a96972"
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 module=importlib.util.module_from_spec(spec)
 sys.modules[name]=module;spec.loader.exec_module(module)
 return module
receipt=json.loads((P/"frozen_model_receipt.json").read_text())
weights=tuple(receipt["weights"])
assert len(weights)==8 and weights[3]==0
assert hashlib.sha256(bytes(w%256 for w in weights)).hexdigest()==receipt["weights_sha256"]
bridge=load("f64_frozen_synthetic_bridge",P/"bridge_features.py")
graph=load("f64_independent_graph_auditor",P.parent/"20261016-y-f63c"/"audit_graph.py")
f63c=load("f64_frozen_F63C_learner",P.parent/"20261016-y-f63"/"learn_reliability.py")
codec=bridge.PACK
f62=bridge.BASE
f60,f59,f58,f61=f62.controls()
rows=[]
for index in range(32):
 seed=-901-index;family=(-2,-1)[index%2]
 public,q,meta=bridge.SOURCE.source(seed,family)
 graph_report=graph.verify(public,q)
 trained,trace=bridge.online(public,weights,True,True)
 ablated,ablation_trace=bridge.online(public,weights,True,False)
 aud_trained=bridge.AUDIT.verify(public,q,trace)
 aud_ablated=bridge.AUDIT.verify(public,q,ablation_trace)
 assert aud_trained["prefixes"]==aud_ablated["prefixes"]==72
 assert aud_trained["max_payload_bytes"]<=144 and aud_ablated["max_payload_bytes"]<=144
 assert bridge.AUDIT.solve(tuple(bridge.AUDIT.decode(s) for s in trace[-1]),q)==codec.solve(trained,q)
 assert bridge.AUDIT.solve(tuple(bridge.AUDIT.decode(s) for s in ablation_trace[-1]),q)==codec.solve(ablated,q)
 controls={
  "F60_fixed":f60.online_fixed(public),
  "F59_deferred":f59.fixed_deferred_component_buffer(public),
  "F58_frontier":f58.frontier_online(public),
  "F61_frozen":f61.learned_online(public,f62.F61_WEIGHTS)[0],
  "F62_frozen":f62.learned_online(public,(0,2,1,1,1,1,1,3,0,3,0,0),codec)[0],
  "F63C_frozen":f63c.m.select(public,codec,(50,93,45,100),True)[0],
  "fixed_public_pair_triple_DAG":f61.fixed_online(public,"fixed_pair_triple_DAG"),
  "fixed_public_FIFO_hash":f61.fixed_online(public,"FIFO_hash"),
 }
 scores={
  "F64_learned_bridge":int(codec.solve(trained,q)==q["answer"]),
  "F64_no_bridge_features":int(codec.solve(ablated,q)==q["answer"])
 }
 for name,memory in controls.items():
  f62._valid_memory(memory,codec)
  scores[name]=int(codec.solve(memory,q)==q["answer"])
 assert len(public)==72
 rows.append(dict(seed=seed,family=family,
  question_type=meta["question_type"],arrival_regime=meta["regime"],
  max_model_bytes=aud_trained["max_payload_bytes"],
  audit_valid=graph_report["public_answer_unique"],scores=scores))
total={k:sum(row["scores"][k] for row in rows) for k in rows[0]["scores"]}
fair=[key for key in total if key not in ("F64_learned_bridge","F64_no_bridge_features")]
winner=max(fair,key=lambda name:total[name])
qtypes={}
for qtype in sorted(set(r["question_type"] for r in rows)):
 subset=[r for r in rows if r["question_type"]==qtype]
 qtypes[qtype]={"cases":len(subset),"F64":sum(r["scores"]["F64_learned_bridge"] for r in subset),
   "F60":sum(r["scores"]["F60_fixed"] for r in subset),
   "ablation":sum(r["scores"]["F64_no_bridge_features"] for r in subset)}
verdict=dict(schema="yggdrasil.f64.frozen-prevalidation-synthetic.v1",
 stage="UNREGISTERED_SYNTHETIC_ONLY",fit_train_reused=False,
 fit_validation_executed=False,diagnostics_executed=False,
 original_executed=False,independent_F3=False,optimizer_promotion=False,
 model_weights=list(weights),weights_sha256=receipt["weights_sha256"],
 direct_public_bridge_coefficient=weights[3],hub_coefficient=weights[4],
 protected_cohorts_unconsumed=True,independent_public_prefix_audit_pass=True,
 cases=len(rows),totals=total,strongest_fair=winner,
 strongest_fair_correct=total[winner],question_strata=qtypes,
 bridge_feature_ablation_positive_on_synthetic=(total["F64_learned_bridge"]>total["F64_no_bridge_features"]),
 scientific_improvement_qualified=False,validation_decision_not_based_on_synthetic_tuning=True,
 rows=rows)
print(json.dumps(verdict,sort_keys=True))
