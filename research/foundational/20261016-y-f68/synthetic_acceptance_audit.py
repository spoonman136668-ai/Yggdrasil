"""F68 independent complete pre-FIT synthetic acceptance audit.

Confirms archived fixed weights, unrepeated eight synthetic guard identities,
and the preregistered *nonzero accuracy / F60 comparison* gate. Does not
overwrite the successful narrower structural-retention result.
"""
import hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(p):
 b=p.read_bytes();return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def load(name,path,digest):
 assert blob(path)==digest,(name,"SOURCE_IDENTITY_DRIFT")
 s=importlib.util.spec_from_file_location(name,path)
 x=importlib.util.module_from_spec(s);sys.modules[name]=x;s.loader.exec_module(x);return x
M=load("f68_frozen_model_acceptance",P/"action_conditioned.py",
       "c079cb2b6993429c302f4f634e2862d05056fbdb")
PUB=load("f68_frozen_independent_bridge_truth",P/"public_bridge_labels.py",
       "aab85cca8d1f84b71dd4d1ed2733b80ebed087a2")
assert blob(P/"train_method_precode.json")=="99d024db0ab22775f8a2790f0156eb2c56fe2101"
WEIGHTS=(0,-14,4,-22,-26,46,-13,46,0,-2,7,0,5,3,0,-21)
assert len(WEIGHTS)==16
f60,f59,f58,f61=M.ACTION.controls()
rows=[]
for k in range(8):
 seed=-2811-k;family=(-2,-1)[k%2]
 public,q,meta=M.SOURCE.source(seed,family)
 learned,trace,actions=M.online(public,WEIGHTS,True,True)
 disabled,trace_ab,_=M.online(public,WEIGHTS,True,False)
 assert M.AUDITOR.verify(public,q,trace)["prefixes"]==72
 assert M.AUDITOR.verify(public,q,trace_ab)["prefixes"]==72
 bridges={M.PACK.edge_record(e) for e in PUB.full_public_bridge_edges(public)}
 score=dict(
  model=int(M.PACK.solve(learned,q)==q["answer"]),
  ablation=int(M.PACK.solve(disabled,q)==q["answer"]),
  frozen_F60=int(M.PACK.solve(f60.online_fixed(public),q)==q["answer"]),
  frozen_F59=int(M.PACK.solve(f59.fixed_deferred_component_buffer(public),q)==q["answer"]),
  frozen_F58=int(M.PACK.solve(f58.frontier_online(public),q)==q["answer"]),
  bridge_kept=sum(int(rec in bridges) for rec in learned),
  bridge_ablation=sum(int(rec in bridges) for rec in disabled))
 rows.append(dict(seed=seed,family=family,kind=meta["question_type"],
                  exact_pretrained_weights=True,scores=score))
totals={key:sum(row["scores"][key] for row in rows)
        for key in rows[0]["scores"]}
method_prereg=json.loads((P/"train_method_precode.json").read_text())
assert method_prereg["synthetic_gates"]["nonzero_accuracy_and_frozen_F60_comparison_report"] is True
passes=dict(
 genuinely_action_conditioned_retention=totals["bridge_kept"]>totals["bridge_ablation"],
 learned_nonzero_correct=totals["model"]>0,
 independent_F60_comparator_reported=True,
 independent_causal_prefix_audit=True)
result=dict(schema="yggdrasil.f68.full-preregistered-synthetic-acceptance.v1",
 status="READ_ONLY_INDEPENDENT_COMPLETENESS_AUDIT",
 frozen_model_weights=list(WEIGHTS),synthetic_guard_cases=len(rows),
 totals=totals,preregistered_gates=passes,
 eligible_for_protected_FIT=all(passes.values()),
 registered_train_consumed=False,validation_consumed=False,
 diagnostic_consumed=False,original_consumed=False,F3=False,
 optimizer_promotion=False,rows=rows)
print(json.dumps(result,sort_keys=True))
