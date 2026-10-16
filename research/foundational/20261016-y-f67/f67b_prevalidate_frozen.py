"""F67B frozen-model synthetic-only independent prospective sanity test.

Online sees 72 public edges and fixed weights; postretention question is
only passed to independent causal auditors and to offline scoring.
"""
from __future__ import annotations
import hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes();return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def load(name,path,expected):
 assert blob(path)==expected,(name,"FROZEN_IDENTITY_DRIFT")
 sp=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(sp);sys.modules[name]=m;sp.loader.exec_module(m);return m
rec=json.loads((P/"f67b_frozen_receipt.json").read_text())
method=load("f67b_prevalid_frozen_method",P/"durable_policy.py",rec["source_blob"])
assert blob(P/"prereg-positive-admission.json")==rec["prereg_blob"]
weights=tuple(rec["frozen_int8_weights"])
assert len(weights)==16
assert hashlib.sha256(bytes(w%256 for w in weights)).hexdigest()==rec["weights_sha256"]
assert rec["no_retraining"] and rec["FIT_validate_used"] is False
F62=method.BASE;f60,f59,f58,f61=F62.controls()
PACK=method.PACK
rows=[]
for i in range(24):
 seed=-3201-i;family=(-2,-1)[i%2]
 public,q,meta=method.SRC.source(seed,family)
 memory,trace,merges=method.online(public,weights,True,True)
 ablation,trace_ab,abl_merges=method.online(public,weights,True,False)
 receipt=method.BUDGET_AUDIT.verify(public,q,trace)
 receipt_ab=method.AUDIT.verify(public,q,trace_ab)
 assert receipt["prefixes"]==receipt_ab["prefixes"]==72
 assert receipt["max_payload_bytes"]<=144 and receipt_ab["max_payload_bytes"]<=144
 assert method.BUDGET_AUDIT.f62.solve(memory,q)==PACK.solve(memory,q)
 score=dict(F67B_frozen=int(PACK.solve(memory,q)==q["answer"]),
            F67B_no_stable_budget_ablation=int(PACK.solve(ablation,q)==q["answer"]))
 for name,mem in dict(F60=f60.online_fixed(public),
    F59=f59.fixed_deferred_component_buffer(public),
    F58=f58.frontier_online(public),
    F61=f61.learned_online(public,F62.F61_WEIGHTS)[0],
    F62=F62.learned_online(public,(0,2,1,1,1,1,1,3,0,3,0,0),PACK)[0],
    DAG=f61.fixed_online(public,"fixed_pair_triple_DAG"),
    FIFO=f61.fixed_online(public,"FIFO_hash")).items():
  F62._valid_memory(mem,PACK)
  score[name]=int(PACK.solve(mem,q)==q["answer"])
 rows.append(dict(seed=seed,family=family,kind=meta["question_type"],
   regime=meta["regime"],merges=merges,ablation_merges=abl_merges,
   durable=sum(len(r[2])>=4 for r in memory),score=score))
totals={key:sum(r["score"][key] for r in rows) for key in rows[0]["score"]}
strongest_fair=max(totals[k] for k in ("F60","F59","F58","F61","F62","DAG","FIFO"))
kinds={kind:{name:sum(r["score"][name] for r in rows if r["kind"]==kind)
  for name in ("F67B_frozen","F67B_no_stable_budget_ablation","F60")}
  for kind in sorted(set(r["kind"] for r in rows))}
out=dict(schema="yggdrasil.f67b.frozen-synthetic-prevalidation.v1",
 status="FROZEN_SYNTHETIC_ONLY",model_weights=list(weights),
 weights_sha256=rec["weights_sha256"],cases=len(rows),scores=totals,
 strongest_fair_correct=strongest_fair,
 learned_model_merges=sum(r["merges"] for r in rows),
 learned_final_long_records=sum(r["durable"] for r in rows),
 ablation_merges=sum(r["ablation_merges"] for r in rows),
 positive_stable_budget_ablation=(totals["F67B_frozen"]>totals["F67B_no_stable_budget_ablation"]),
 learned_matches_strongest_fair=(totals["F67B_frozen"]>=strongest_fair),
 per_question_strata=kinds,independent_prefix_audit_pass=True,
 fit_train_reused=False,fit_validation_used=False,diagnostics_used=False,
 original_used=False,F3=False,scientific_qualified=False,policy_promotion=False,rows=rows)
print(json.dumps(out,sort_keys=True))
