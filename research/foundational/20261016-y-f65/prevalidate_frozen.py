"""F65 frozen model causal and ablation synthetic-only prevalidation.

No registered FIT, DIAG or originals can enter this path. A zero-result
learned model is a block against consuming protected validation.
"""
import hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
custody=json.loads((P/"frozen_model_receipt.json").read_text())
assert blob(P/"prereg.json")==custody["prereg_blob"]=="9bbfd50b740be2c9d4ec891b3b360cd9650b7e23"
assert blob(P/"path_assembly.py")==custody["source_blob"]=="10c2ba041c1d3e3063e1e98ba5726fa458db5f3a"
weights=tuple(custody["frozen_int8_weights"])
assert len(weights)==16 and hashlib.sha256(bytes(w%256 for w in weights)).hexdigest()==custody["weights_sha256"]
assert custody["no_retraining"] and not custody["fit_validation_used"]
method=load("f65_prevalidated_frozen_method",P/"path_assembly.py")
f62=method.BASE;f60,f59,f58,f61=f62.controls()
codec=method.PACK
f63=load("f65_prevalidation_frozen_f63",P.parent/"20261016-y-f63"/"learn_reliability.py")
f64=load("f65_prevalidation_frozen_f64",P.parent/"20261016-y-f64"/"bridge_features.py")
rows=[]
for i in range(24):
 seed=-1401-i
 family=(-2,-1)[i%2]
 public,q,meta=method.SOURCE.source(seed,family)
 trained,trace,nmerge=method.online(public,weights,trace=True)
 disabled,trace_ab,merges_ab=method.online(public,weights,trace=True,allow_assembly=False)
 rep=method.AUDITOR.verify(public,q,trace)
 rep_ab=method.AUDITOR.verify(public,q,trace_ab)
 assert rep["prefixes"]==rep_ab["prefixes"]==72
 assert rep["max_payload_bytes"]<=144 and rep_ab["max_payload_bytes"]<=144
 assert method.AUDITOR.solve(tuple(method.AUDITOR.decode(x) for x in trace[-1]),q)==codec.solve(trained,q)
 assert method.AUDITOR.solve(tuple(method.AUDITOR.decode(x) for x in trace_ab[-1]),q)==codec.solve(disabled,q)
 controls={
   "F60_fixed":f60.online_fixed(public),
   "F59_deferred":f59.fixed_deferred_component_buffer(public),
   "F58_frontier":f58.frontier_online(public),
   "F61_frozen":f61.learned_online(public,f62.F61_WEIGHTS)[0],
   "F62_frozen":f62.learned_online(public,(0,2,1,1,1,1,1,3,0,3,0,0),codec)[0],
   "F63C_frozen":f63.m.select(public,codec,(50,93,45,100),True)[0],
   "F64_frozen":f64.online(public,(6,-5,13,0,2,2,1,-1)),
   "fixed_pair_triple_DAG":f61.fixed_online(public,"fixed_pair_triple_DAG"),
   "fixed_FIFO_hash":f61.fixed_online(public,"FIFO_hash")}
 score={"F65_frozen_assembly":int(codec.solve(trained,q)==q["answer"]),
        "F65_no_assembly_feature_ablation":int(codec.solve(disabled,q)==q["answer"])}
 for name,records in controls.items():
  f62._valid_memory(records,codec)
  score[name]=int(codec.solve(records,q)==q["answer"])
 rows.append(dict(seed=seed,family=family,kind=meta["question_type"],
   regime=meta["regime"],merges=nmerge,ablation_merges=merges_ab,
   divergent_prefixes=sum(int(a!=b) for a,b in zip(trace,trace_ab)),
   scores=score))
totals={name:sum(row["scores"][name] for row in rows) for name in rows[0]["scores"]}
learned=totals["F65_frozen_assembly"]
ablated=totals["F65_no_assembly_feature_ablation"]
result=dict(schema="yggdrasil.f65.frozen-model-synthetic-prevalidation.v1",
 stage="INDEPENDENT_SYNTHETIC_ONLY",model_weights=list(weights),
 model_weights_sha256=custody["weights_sha256"],
 cases=len(rows),scores=totals,merges_selected=sum(r["merges"] for r in rows),
 ablation_merges_selected=sum(r["ablation_merges"] for r in rows),
 ablation_divergent_prefixes=sum(r["divergent_prefixes"] for r in rows),
 independent_prefix_causal_audit=True,positive_assembly_ablation=(learned>ablated),
 model_prevalidation_positive=(learned>ablated and learned>=totals["F60_fixed"] and sum(r["merges"] for r in rows)>0),
 first_use_training_rerun=False,fit_validation_used=False,diagnostics_used=False,
 originals_used=False,F3=False,scientific_qualified=False,policy_promotion=False,
 rows=rows)
print(json.dumps(result,sort_keys=True))
