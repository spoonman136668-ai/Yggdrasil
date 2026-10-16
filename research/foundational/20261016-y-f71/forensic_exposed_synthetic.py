"""F71 read-only frozen synthetic failure diagnosis.

Replays ONLY already exposed F71 negative-seed synthetics; no source,
weights, training objective or scientific gate changes. Readout is
exploratory; no re-use of outcomes as fresh prevalidation evidence.
"""
from __future__ import annotations
import hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert blob(P/"prereg.json")=="b3e0f8c32ad639079fcf6ab85fd8b17f6285acdc"
assert blob(P/"early_scheduler.py")=="edddfedb04af27dac7332ca85cc742aef5772a4b"
spec=importlib.util.spec_from_file_location("f71_exposed_frozen_model",P/"early_scheduler.py")
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
train=[]
for i in range(8):
 seed=-3601-i
 public,q,_=m.SOURCE.source(seed,(-2,-1)[i%2])
 train.append((public,q))
weights,labels=m.synthetic_train(train)
rows=[]
decision_total=potential_beneficial=potential_harmful=potential_neutral=0
for i in range(8):
 seed=-3611-i;fam=(-2,-1)[i%2]
 public,q,meta=m.SOURCE.source(seed,fam)
 learned,trace,activity=m.online(public,weights,True,True)
 frozen,fr_trace,_=m.online(public,weights,True,False)
 assert m.AUDIT.verify(public,q,trace)["prefixes"]==72
 assert m.AUDIT.verify(public,q,fr_trace)["prefixes"]==72
 baseline=()
 chosen_harm=chosen_good=chosen_neutral=0
 # Independent counterfactuals are diagnostic ONLY. q and future edges
 # never enter the frozen online policy itself.
 selected=()
 for k,event in enumerate(public):
  base,alternatives=m.native_alternatives(selected,event,k)
  scored=[(sum((w/32)*v for w,v in zip(weights,x)),j,after)
    for j,(_act,_drop,after,x) in enumerate(alternatives)]
  best=max(scored,key=lambda t:(t[0],-t[1])) if scored else None
  if best is not None and best[0]>.05:
   decision_total+=1
   alternative=best[2]
   base_end=m.F62._finish_fixed(base,public[k+1:],m.PACK)
   alt_end=m.F62._finish_fixed(alternative,public[k+1:],m.PACK)
   control_correct=m.PACK.solve(base_end,q)==q["answer"]
   other_correct=m.PACK.solve(alt_end,q)==q["answer"]
   if other_correct and not control_correct:chosen_good+=1;potential_beneficial+=1
   elif control_correct and not other_correct:chosen_harm+=1;potential_harmful+=1
   else:chosen_neutral+=1;potential_neutral+=1
   selected=alternative
  else:selected=base
 assert selected==learned
 rows.append(dict(seed=seed,family=fam,kind=meta["question_type"],
   learned_correct=int(m.PACK.solve(learned,q)==q["answer"]),
   frozen_correct=int(m.PACK.solve(frozen,q)==q["answer"]),
   model_early_overrides=activity["early_overrides"],
   model_total_overrides=activity["overrides"],
   chosen_counterfactual_beneficial=chosen_good,
   chosen_counterfactual_harmful=chosen_harm,
   chosen_counterfactual_neutral=chosen_neutral))
learned_score=sum(r["learned_correct"] for r in rows)
fixed_score=sum(r["frozen_correct"] for r in rows)
result=dict(schema="yggdrasil.f71.exposed-synthetic-failure-forensics.v1",
 stage="EXPLORATORY_READ_ONLY_NOT_NEW_PREVALIDATION",
 authentic_preflight_run=38913645941,
 original_model_blob="edddfedb04af27dac7332ca85cc742aef5772a4b",
 frozen_weights=list(weights),
 frozen_training_labels=labels,
 cases=8,
 trained_correct=learned_score,frozen_F60_correct=fixed_score,
 early_interventions=sum(r["model_early_overrides"] for r in rows),
 total_selected_counterfactual_decisions=decision_total,
 beneficial_decisions=potential_beneficial,
 harmful_decisions=potential_harmful,
 neutral_decisions=potential_neutral,
 prereg_prequalification_pass=(learned_score>=fixed_score and
     sum(r["model_early_overrides"] for r in rows)>0),
 source_modified=False,training_or_threshold_modified=False,
 protected_FIT_train_used=False,protected_FIT_validate_used=False,
 diagnostic_used=False,original_used=False,F3=False,optimizer_promotion=False,
 rows=rows)
print(json.dumps(result,sort_keys=True))
