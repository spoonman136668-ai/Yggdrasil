"""F82 frozen-weight confidence-margin forensics on new unregistered negatives.

Exploratory ONLY. Neither train a model nor adjust the preregistered 0.90
threshold. No protected first-use, future labels, or future events in policy.
"""
from __future__ import annotations
import hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 data=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
path=P/"compact_role_learner.py"
assert blob(path)=="b5d969deeb63e99c1b235f675a0532c16863e519"
spec=importlib.util.spec_from_file_location("f82_exact_frozen_model",path)
M=importlib.util.module_from_spec(spec);sys.modules[spec.name]=M;spec.loader.exec_module(M)
weights=(1,-86,13,-34,-44,-10,5,-3,-103,-21,-9,-31,-31,-23,1,-10,58,-33,80,-30,84,107,-6,-3)
assert hashlib.sha256(bytes(w%256 for w in weights)).hexdigest()=="2eed8b880546c87fe6cdfc411653431d4b0ab9748861e81d1a27586522aee9c9"
rows=[];all_probs=[]
for seed in range(-5001,-5017,-1):
 for family in (-2,-1):
  public,q,meta=M.SOURCE.source(seed,family)
  assert M.SOURCE.BASE.public_witness(public,q)=={q["answer"]}
  memory=();case_probs=[]
  for index,event in enumerate(public):
   base,options=M.F79.unique_alternatives(memory,event,index)
   if options:
    probs=[M.sigmoid(sum((w/32)*x for w,x in zip(weights,
      M.features(memory,base,after,event,action,drop))))
      for action,drop,after,_ in options]
    case_probs.extend(probs)
   memory=base
  all_probs.extend(case_probs)
  rows.append(dict(seed=seed,family=family,regime=meta["arrival_regime"],
   number_candidates=len(case_probs),
   max_candidate_probability=max(case_probs,default=0),
   candidates_above_preregistered_0_90=sum(p>.90 for p in case_probs)))
assert len(rows)==32 and all_probs
all_probs.sort()
def quantile(p):
 return all_probs[min(len(all_probs)-1,round(p*(len(all_probs)-1)))]
report=dict(schema="yggdrasil.f82.frozen-score-margin-exploratory.v1",
 stage="POST_NEGATIVE_UNREGISTERED_FORENSICS_ONLY",
 source_model_sha=blob(path),weights=list(weights),
 cutoff_unchanged=0.90,cases=len(rows),candidate_actions=len(all_probs),
 maximum_probability=all_probs[-1],median_probability=quantile(.5),
 p95_probability=quantile(.95),p99_probability=quantile(.99),
 candidate_actions_above_cutoff=sum(p>.90 for p in all_probs),
 cases_with_action_above_cutoff=sum(r["candidates_above_preregistered_0_90"]>0 for r in rows),
 training_repeated=False,guard_cohort_reused=False,
 registered_FIT_or_original_used=False,F3=False,optimizer_promotion=False,
 confidence_threshold_changed=False,scientific_qualified=False,rows=rows)
print(json.dumps(report,sort_keys=True))
