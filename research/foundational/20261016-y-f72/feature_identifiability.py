"""F72 preregistered public feature-identifiability SCIENTIFIC DIAGNOSTIC.

All 32 cases use fresh unregistered negative source seeds. The full future
question and future public events are available only to an UNFAIR offline
counterfactual auditor. No fitted policy is constructed or promoted.
"""
from __future__ import annotations
import collections,hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def gitblob(path):
 raw=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
assert gitblob(P/"prereg.json")=="e2cab52f897b9a7542c20e1667f1d6a3dc6fecc9"
original=P.parent/"20261016-y-f71"/"early_scheduler.py"
assert gitblob(original)=="edddfedb04af27dac7332ca85cc742aef5772a4b"
s=importlib.util.spec_from_file_location("f72_immutable_F71_public_features",original)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
spec=json.loads((P/"prereg.json").read_text())
assert spec["synthetic_cohort"]["seeds"]==[-3801,-3833]
def time_window(i):
 for d in spec["method"]["time_windows"]:
  if d["range"][0]<=i<d["range"][1]:return d["label"]
 raise AssertionError("INVALID_FIXED_WINDOW")
def validate_one_override(public,q,index,after):
 traces=[];state=()
 for i,e in enumerate(public):
  baseline=m.F62._f60_step(state,e,m.PACK)
  if i==index:
   options=[c[3] for c in m.F62.actions(state,e,i,m.PACK)]
   assert after in options and after!=baseline,"NONCAUSAL_ORACLE_INTERVENTION"
   state=after
  else:state=baseline
  m.F62._valid_memory(state,m.PACK)
  traces.append(tuple(m.PACK.pack(*r).hex() for r in state))
 assert m.AUDIT.verify(public,q,traces)["prefixes"]==72
 assert m.PACK.solve(state,q)==q["answer"],"FALSE_ORACLE_RESCUE"
 return True
def evaluate():
 all_cases=[]
 histogram=collections.Counter()
 signatures=collections.defaultdict(lambda:collections.Counter())
 cases_with_earliest_rescue=0
 number_of_features=0
 raw_labels=collections.Counter()
 for number in range(32):
  seed=-3801-number;family=(-2,-1)[number%2]
  public,q,meta=m.SOURCE.source(seed,family)
  assert len(public)==72
  assert m.SOURCE.public_witness(public,q)=={q["answer"]}
  current=();observed=collections.Counter()
  first_rescue=None
  for index,event in enumerate(public):
   baseline,alts=m.native_alternatives(current,event,index)
   if alts:
    base_end=m.F62._finish_fixed(baseline,public[index+1:],m.PACK)
    base_good=m.PACK.solve(base_end,q)==q["answer"]
    for act,drop,after,features in alts:
     number_of_features+=1
     terminal=m.F62._finish_fixed(after,public[index+1:],m.PACK)
     alternative_good=m.PACK.solve(terminal,q)==q["answer"]
     if alternative_good and not base_good:
      label="beneficial"
      if first_rescue is None:
       first_rescue=(index,after)
     elif base_good and not alternative_good:label="harmful"
     else:label="neutral"
     key=time_window(index)
     observed[label]+=1
     histogram[(meta["question_type"],key,label)]+=1
     raw_labels[label]+=1
     signature=tuple(round(float(v),4) for v in features)
     assert len(signature)==12
     signatures[signature][label]+=1
   current=baseline
  frozen_good=m.PACK.solve(current,q)==q["answer"]
  certified=False
  if first_rescue is not None:
   certified=validate_one_override(public,q,first_rescue[0],first_rescue[1])
   cases_with_earliest_rescue+=1
  all_cases.append(dict(seed=seed,family=family,
   question_type=meta["question_type"],frozen_F60_correct=bool(frozen_good),
   beneficial_candidates=observed["beneficial"],
   harmful_candidates=observed["harmful"],
   neutral_candidates=observed["neutral"],
   earliest_beneficial_index=first_rescue[0] if first_rescue else None,
   earliest_rescue_independently_audited=certified))
 assert number_of_features==sum(raw_labels.values())
 mixed_signatures={k:v for k,v in signatures.items()
                    if v["beneficial"]>0 and v["harmful"]>0}
 positive_ambiguous=sum(v["beneficial"] for v in mixed_signatures.values())
 negative_ambiguous=sum(v["harmful"] for v in mixed_signatures.values())
 by_stratum=[]
 for typ in ("within_component_4_steps","crosslink_reach_6_steps"):
  for d in spec["method"]["time_windows"]:
   window=d["label"]
   by_stratum.append(dict(question_type=typ,window=window,
    **{label:histogram[(typ,window,label)]
      for label in ("beneficial","harmful","neutral")}))
 result=dict(schema="yggdrasil.f72.public-feature-identifiability.synthetic-diagnostic.v1",
  stage="UNREGISTERED_NONCOMPETITIVE_OFFLINE_ORACLE",
  provenance=dict(prereg_blob="e2cab52f897b9a7542c20e1667f1d6a3dc6fecc9",
    original_F71_source_blob="edddfedb04af27dac7332ca85cc742aef5772a4b"),
  cases=len(all_cases),
  frozen_F60_correct=sum(c["frozen_F60_correct"] for c in all_cases),
  cases_with_independently_verified_single_step_rescue=cases_with_earliest_rescue,
  candidate_samples=number_of_features,label_counts=dict(raw_labels),
  unique_public_feature_signatures=len(signatures),
  coarsened_signatures_conflicting_beneficial_vs_harmful=len(mixed_signatures),
  beneficial_examples_with_harmful_signature_collision=positive_ambiguous,
  harmful_examples_with_beneficial_signature_collision=negative_ambiguous,
  precision_decimal_places=4,
  fixed_stratum_counts=by_stratum,
  source_preregistered=True,source_or_weights_modified=False,
  unfair_oracle_noncompetitive=True,learned_model_fit=False,
  protected_FIT_train_used=False,protected_FIT_validation_used=False,
  diagnostics_used=False,original_used=False,F3=False,optimizer_promotion=False,
  cases_summary=all_cases)
 print(json.dumps(result,sort_keys=True))
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 evaluate()
