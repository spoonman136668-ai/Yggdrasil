"""F66B independent synthetic frozen model validation; no registered seeds.

Read-only public prefix receipts, offline answers only after policy retention.
No FIT reruns or model changes. Expected blobs verified before execution.
"""
import hashlib,importlib.util,json,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes();return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def load(n,path,expected):
 assert blob(path)==expected,(n,"FROZEN_BLOB_DRIFT")
 spec=importlib.util.spec_from_file_location(n,path)
 mod=importlib.util.module_from_spec(spec);sys.modules[n]=mod;spec.loader.exec_module(mod);return mod
receipt=json.loads((HERE/"f66b_frozen_receipt.json").read_text())
assert blob(HERE/"dense_opportunity_teacher.py")==receipt["method_blob"]
assert blob(HERE/"prereg-opportunity-cost-amendment.json")==receipt["prereg_amendment_blob"]
assert blob(HERE/"prereg.json")==receipt["prereg_blob"]
method=load("f66b_preval_frozen_policy",HERE/"two_head_continuation.py",receipt["online_blob"])
weights=tuple(receipt["frozen_int8_weights"])
assert len(weights)==20 and all(type(w)==int for w in weights)
assert hashlib.sha256(bytes(w%256 for w in weights)).hexdigest()==receipt["weights_sha256"]
assert receipt["heldout_used"] is False and receipt["no_post_fit_tuning"]
F62=method.ACTION
f60,f59,f58,f61=F62.controls()
PACK=method.PACK
F63=load("f66b_preval_F63C",HERE.parent/"20261016-y-f63"/"learn_reliability.py","4eef37159bb96e90cf7f89c4dc0ed91b6d9d23c5")
F64=load("f66b_preval_F64",HERE.parent/"20261016-y-f64"/"bridge_features.py","75d952228c53cf9d41d1cb557fee27e421a96972")
F65=load("f66b_preval_F65",HERE.parent/"20261016-y-f65"/"path_assembly.py","10c2ba041c1d3e3063e1e98ba5726fa458db5f3a")
rows=[]
for i in range(24):
 seed=-2401-i;family=(-2,-1)[i%2]
 public,q,meta=method.SOURCE.source(seed,family)
 trained,trace,merges=method.online(public,weights,True)
 ablated,trace_ab,ablated_merges=method.online(public,weights,True,False)
 p=method.AUDITOR.verify(public,q,trace)
 p_ab=method.AUDITOR.verify(public,q,trace_ab)
 assert p["prefixes"]==p_ab["prefixes"]==72
 assert p["max_payload_bytes"]<=144 and p_ab["max_payload_bytes"]<=144
 assert method.AUDITOR.solve(tuple(method.AUDITOR.decode(s) for s in trace[-1]),q)==PACK.solve(trained,q)
 assert method.AUDITOR.solve(tuple(method.AUDITOR.decode(s) for s in trace_ab[-1]),q)==PACK.solve(ablated,q)
 controls=dict(
  F60_fixed=f60.online_fixed(public),
  F59_deferred=f59.fixed_deferred_component_buffer(public),
  F58_frontier=f58.frontier_online(public),
  F61_frozen=f61.learned_online(public,F62.F61_WEIGHTS)[0],
  F62_frozen=F62.learned_online(public,(0,2,1,1,1,1,1,3,0,3,0,0),PACK)[0],
  F63C_frozen=F63.m.select(public,PACK,(50,93,45,100),True)[0],
  F64_frozen=F64.online(public,(6,-5,13,0,2,2,1,-1)),
  F65_frozen=F65.online(public,(0,0,-3,2,8,2,0,-1,-1,0,-1,0,0,0,0,0)),
  fixed_DAG=f61.fixed_online(public,"fixed_pair_triple_DAG"),
  fixed_FIFO=f61.fixed_online(public,"FIFO_hash"))
 score=dict(F66B_learned=int(PACK.solve(trained,q)==q["answer"]),
            F66B_no_continuation_ablation=int(PACK.solve(ablated,q)==q["answer"]))
 for k,m in controls.items():
  F62._valid_memory(m,PACK)
  score[k]=int(PACK.solve(m,q)==q["answer"])
 rows.append(dict(seed=seed,family=family,kind=meta["question_type"],
    regime=meta["regime"],merges=merges,ablation_merges=ablated_merges,
    divergent_prefixes=sum(a!=b for a,b in zip(trace,trace_ab)),score=score))
totals={k:sum(r["score"][k] for r in rows) for k in rows[0]["score"]}
fair=("F60_fixed","F59_deferred","F58_frontier","F61_frozen","F62_frozen","F63C_frozen","F64_frozen","F65_frozen","fixed_DAG","fixed_FIFO")
best=max(totals[k] for k in fair)
result=dict(schema="yggdrasil.f66b.frozen-independent-synthetic-prevalidation.v1",
  stage="PREVALIDATION_UNREGISTERED_SYNTHETIC_ONLY",
  frozen_weights=list(weights),weight_sha256=receipt["weights_sha256"],
  cases=len(rows),scores=totals,
  strongest_fair_synthetic_correct=best,
  frozen_policy_merge_count=sum(r["merges"] for r in rows),
  ablation_merge_count=sum(r["ablation_merges"] for r in rows),
  ablation_positive=totals["F66B_learned"]>totals["F66B_no_continuation_ablation"],
  learned_above_strongest_fair=totals["F66B_learned"]>best,
  different_prefixes=sum(r["divergent_prefixes"] for r in rows),
  causal_independent_audit=True,
  training_rerun=False,fit_validation_executed=False,diagnostic_executed=False,
  original_executed=False,F3=False,policy_promotion=False,rows=rows)
print(json.dumps(result,sort_keys=True))
