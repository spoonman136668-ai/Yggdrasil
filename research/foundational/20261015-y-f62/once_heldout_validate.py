"""One protected, preregistered Y-F62 FIT validation. Never refit weights."""
from __future__ import annotations
import hashlib,importlib.util,json,pathlib,sys
from collections import defaultdict
HERE=pathlib.Path(__file__).resolve().parent
receipt=json.loads((HERE/"frozen_train_receipt.json").read_text())
prereg=json.loads((HERE/"prereg.json").read_text())
def gitblob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert gitblob(HERE/"frozen_train_receipt.json")=="3ebca86bb230c9e6f4885f9c636d76f5d06e115f"
assert gitblob(HERE/"source_pilot.py")==receipt["source_blob"]
assert gitblob(HERE/"prereg.json")==receipt["prereg_blob"]
assert gitblob(HERE/"audit_public.py")=="383fff0bdd8c8b48fde9538d4e4d768db1c1896f"
weights=tuple(receipt["frozen_int8_weights"])
assert len(weights)==12 and all(isinstance(x,int) and -127<=x<=127 for x in weights)
assert hashlib.sha256(bytes(x%256 for x in weights)).hexdigest()==receipt["frozen_weights_sha256"]
assert receipt["validation_performed"] is False and receipt["retraining_permitted"] is False
assert prereg["fit"]["within_fit_validation"]==[761008,761016]
assert prereg["authority"]["validation_once_only_no_reruns"] is True
def load(name,filename):
 p=HERE/filename
 s=importlib.util.spec_from_file_location(name,p)
 m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
 return m
m=load("y_f62_frozen_validation", "source_pilot.py")
audit=load("y_f62_independent_validation", "audit_public.py")
packing=m.codec()
assert (m.VALIDATE.start,m.VALIDATE.stop)==(761008,761016)
assert tuple(m.FAMILIES)==(1460,1461,1462,1463)
rows=[]
for seed in m.VALIDATE:
 for family in m.FAMILIES:
  tagged,question,_paths,regime=m.source(seed,family)
  public=tuple(row[:3] for row in tagged)
  learned,actions,trace=m.learned_online(public,weights,packing,trace=True)
  ablated,ablation_actions,ablation_trace=m.learned_online(
   public,weights,packing,trace=True,allow_composition=False)
  verified=audit.verify(public,question,trace)
  verified_ablation=audit.verify(public,question,ablation_trace)
  assert verified["prefixes"]==verified_ablation["prefixes"]==72
  assert all(a[0]!="merge" for a in ablation_actions)
  controls=m.historical_controls_public(public,packing)
  scores={"learned_counterfactual_action_value":int(audit.solve(
    tuple(audit.decode(z) for z in trace[-1]),question)==question["answer"]),
    "learned_without_composition_ablation":int(audit.solve(
    tuple(audit.decode(z) for z in ablation_trace[-1]),question)==question["answer"])}
  assert scores["learned_counterfactual_action_value"]==int(packing.solve(learned,question)==question["answer"])
  for name,records in controls.items():
   scores[name]=int(packing.solve(records,question)==question["answer"])
  rows.append(dict(seed=seed,family=family,regime=regime,
   public=[[a,b,c] for a,b,c in public],question=question,
   learned_trace=[list(snapshot) for snapshot in trace],
   ablation_trace=[list(snapshot) for snapshot in ablation_trace],
   learned_actions=[list(action) for action in actions],
   ablation_actions=[list(action) for action in ablation_actions],
   scores=scores,max_payload_bytes=verified["max_payload_bytes"]))
assert len(rows)==prereg["fit"]["expected_validation_cases"]==32
fair=["F60_exact_source_fixed_online","F59_exact_source_deferred","F58_exact_source_frontier",
      "F61_frozen_learned_policy_no_refit","fixed_public_pair_triple_DAG","fixed_public_FIFO_hash"]
count=lambda key:sum(row["scores"][key] for row in rows)
control_scores={key:count(key) for key in fair}
best=max(fair,key=lambda k:(control_scores[k],-fair.index(k)))
learned=count("learned_counterfactual_action_value")
no_comp=count("learned_without_composition_ablation")
per_family={str(f):dict(learned=sum(r["scores"]["learned_counterfactual_action_value"] for r in rows if r["family"]==f),
                      strongest_equal_byte=max(sum(r["scores"][k] for r in rows if r["family"]==f) for k in fair))
            for f in m.FAMILIES}
gain=(learned-control_scores[best])/32
passes=dict(absolute_fixed_feasibility=(control_scores["F60_exact_source_fixed_online"]/32>=.25),
           learned_gain_at_least_005=(gain>=.05),
           per_family_nondegradation=all(v["learned"]>=v["strongest_equal_byte"] for v in per_family.values()),
           positive_composition_ablation=(learned>no_comp),
           public_extra_work_witness=(count("offline_full_public_graph_extra_work_noncompetitive")/32>=.85))
result=dict(schema="yggdrasil.f62.once-heldout-validation.v1",
 stage="VALID_SCIENCE_HELDOUT_ONCE",source_blob=receipt["source_blob"],
 training_artifact_id=receipt["artifact_id"],train_result_sha256=receipt["result_sha256"],
 frozen_weights_sha256=receipt["frozen_weights_sha256"],weights=list(weights),
 cases=32,learned_correct=learned,ablated_correct=no_comp,
 control_scores=control_scores,strongest_fair=best,strongest_fair_correct=control_scores[best],
 extra_work_correct=count("offline_full_public_graph_extra_work_noncompetitive"),
 accuracy_gain=gain,per_family=per_family,threshold_passes=passes,
 scientific_qualified=all(passes.values()),rows=rows,
 fit_training_rerun=False,diagnostics_executed=False,original_executed=False,
 independent_F3=False,accepted_ref_mutation=False,policy_promotion=False)
print(json.dumps(result,sort_keys=True))
