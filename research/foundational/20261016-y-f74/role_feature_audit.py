"""F74 independent, frozen role-identity feature diagnostic; NO MODEL FIT.

Offline counterfactual question access is NONCOMPETITIVE. Actual feature
extraction uses solely current public edge and source-native packed memory
before/after an action. Fresh negative synthetic seeds only.
"""
from __future__ import annotations
import collections,hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def gitblob(path):
 raw=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
assert gitblob(P/"prereg.json")=="81d75531ba249815af4247462244f592e4509ea9"
orig=P.parent/"20261016-y-f71"/"early_scheduler.py"
assert gitblob(orig)=="edddfedb04af27dac7332ca85cc742aef5772a4b"
s=importlib.util.spec_from_file_location("f74_frozen_F71_public_source",orig)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
def public_role_stats(records,event):
 hist=[0]*8
 incident=[0]*4
 pair=[0]*4
 endpoints={event[0],event[2]}
 for a,b,codes in records:
  assert all(type(c) is int and 0<=c<8 for c in codes)
  for code in codes:hist[code]+=1
  if a in endpoints or b in endpoints:
   for role in {c//2 for c in codes}:incident[role]+=1
  for left,right in zip(codes,codes[1:]):
   if left//2==right//2:pair[left//2]+=1
 return hist+incident+pair
def vector(before,baseline,after,event,action,drop):
 first=m.features(before,baseline,after,event,action,drop)
 old=public_role_stats(baseline,event)
 new=public_role_stats(after,event)
 extra=tuple((n-o)/12 for o,n in zip(old,new))
 assert len(first)==12 and len(extra)==16
 return tuple(first)+extra
def translate(records,bump):
 return tuple((a+bump,b+bump,tuple(codes)) for a,b,codes in records)
def verify_rename(before,baseline,after,event,action,drop):
 bump=1_000_000_000
 shifted=(event[0]+bump,event[1],event[2]+bump)
 a=vector(before,baseline,after,event,action,drop)
 b=vector(translate(before,bump),translate(baseline,bump),
  translate(after,bump),shifted,action,drop)
 assert a==b,"PUBLIC_FEATURE_DEPENDS_ON_NUMERIC_NODE_IDENTIFIER"
def certify_one(public,q,index,alternative):
 state=();trace=[]
 for i,e in enumerate(public):
  fixed=m.F62._f60_step(state,e,m.PACK)
  if i==index:
   candidates=[c[3] for c in m.F62.actions(state,e,i,m.PACK)]
   assert alternative in candidates and alternative!=fixed
   state=alternative
  else:state=fixed
  m.F62._valid_memory(state,m.PACK)
  trace.append(tuple(m.PACK.pack(*r).hex() for r in state))
 assert m.AUDIT.verify(public,q,trace)["prefixes"]==72
 assert m.PACK.solve(state,q)==q["answer"]
def evaluate():
 counters=collections.Counter()
 sig_old=collections.defaultdict(collections.Counter)
 sig_new=collections.defaultdict(collections.Counter)
 per_case=[];sample_count=0;rename_checked=0
 for n in range(32):
  seed=-4101-n;family=(-2,-1)[n%2]
  public,q,meta=m.SOURCE.source(seed,family)
  assert m.SOURCE.public_witness(public,q)=={q["answer"]}
  memory=();case_count=collections.Counter();rescue=None
  for index,event in enumerate(public):
   baseline,alternatives=m.native_alternatives(memory,event,index)
   if alternatives:
    base_terminal=m.F62._finish_fixed(baseline,public[index+1:],m.PACK)
    base_good=m.PACK.solve(base_terminal,q)==q["answer"]
    for action,drop,after,first in alternatives:
     alt_terminal=m.F62._finish_fixed(after,public[index+1:],m.PACK)
     alt_good=m.PACK.solve(alt_terminal,q)==q["answer"]
     if alt_good and not base_good:
      label="beneficial"
      if rescue is None:rescue=(index,after)
     elif base_good and not alt_good:label="harmful"
     else:label="neutral"
     old=tuple(round(float(v),8) for v in first)
     new=tuple(round(float(v),8) for v in vector(memory,baseline,after,event,action,drop))
     assert len(old)==12 and len(new)==28
     # Every examined candidate must be invariant to a bijective node rename.
     verify_rename(memory,baseline,after,event,action,drop)
     rename_checked+=1
     sig_old[old][label]+=1
     sig_new[new][label]+=1
     case_count[label]+=1
     counters[label]+=1;sample_count+=1
   memory=baseline
  correct=m.PACK.solve(memory,q)==q["answer"]
  if rescue is not None:certify_one(public,q,*rescue)
  per_case.append(dict(seed=seed,family=family,kind=meta["question_type"],
   frozen_F60_correct=bool(correct),
   beneficial=case_count["beneficial"],harmful=case_count["harmful"],neutral=case_count["neutral"],
   certified_earliest_rescue_index=rescue[0] if rescue else None))
 def collisions(groups):
  mixed=[c for c in groups.values() if c["beneficial"] and c["harmful"]]
  return dict(unique_signatures=len(groups),
    conflicting_beneficial_harmful_signatures=len(mixed),
    beneficial_examples_aliased_with_harmful=sum(c["beneficial"] for c in mixed),
    harmful_examples_aliased_with_beneficial=sum(c["harmful"] for c in mixed))
 report=dict(schema="yggdrasil.f74.directed-role-public-feature-identifiability.v1",
  stage="FROZEN_UNREGISTERED_DIAGNOSTIC_ONLY",
  cases=len(per_case),frozen_F60_correct=sum(x["frozen_F60_correct"] for x in per_case),
  legal_alternatives_examined=sample_count,
  offline_labels=dict(counters),
  cases_with_independently_audited_one_step_rescue=sum(x["certified_earliest_rescue_index"] is not None for x in per_case),
  baseline_12_public_features=collisions(sig_old),
  directed_role_28_public_features=collisions(sig_new),
  public_node_rename_invariance_checks=rename_checked,
  feature_signature_rounding_decimals=8,
  model_fitted=False,source_or_science_gate_modified=False,
  unfair_offline_answer_access_noncompetitive=True,
  registered_FIT_train_used=False,registered_FIT_validation_used=False,
  DIAG_used=False,original_used=False,F3=False,optimizer_promotion=False,
  cases_summary=per_case)
 print(json.dumps(report,sort_keys=True))
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 evaluate()
