"""F81 preregistered source-public directed role-transition alias diagnostic.

No model fitting or protected first use. Offline future-question teacher labels
only; online feature vectors depend solely on the current public event and
causally retained pre/post action memory. Uses fresh negative synthetic seeds.
"""
from __future__ import annotations
import collections,hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def gitblob(path):
 raw=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
assert gitblob(P/"prereg.json")=="ef96bb4bafa72bd930b1a47f2195cd16f920cf26"
parent=P.parent/"20261016-y-f80"/"feature_alias_audit.py"
assert gitblob(parent)=="03d7116480f30d811ca9ec97a46ca1909adfc9ae"
s=importlib.util.spec_from_file_location("f81_frozen_F80_auditor",parent)
F80=importlib.util.module_from_spec(s);sys.modules[s.name]=F80;s.loader.exec_module(F80)
F79=F80.F79;F62=F80.F62;PACK=F80.PACK;SOURCE=F80.SOURCE;AUDITOR=F80.AUDITOR

def public_role_counts(records,event):
 pairs=[0]*16
 terminal=[0]*8
 endpoints=(event[0],event[2])
 for a,b,codes in records:
  assert 1<=len(codes)<=6 and all(0<=c<8 for c in codes)
  roles=[code//2 for code in codes]
  for r,s in zip(roles,roles[1:]):
   pairs[4*r+s]+=1
  for side,endpoint in enumerate(endpoints):
   if a==endpoint:terminal[side*4+roles[0]]+=1
   if b==endpoint:terminal[side*4+roles[-1]]+=1
 return tuple(pairs+terminal)

def feature_52(before,baseline,after,event,action,drop):
 base28=F79.public_action_features(before,baseline,after,event,action,drop)
 a=public_role_counts(baseline,event)
 b=public_role_counts(after,event)
 extras=tuple((new-old)/12 for old,new in zip(a,b))
 ans=tuple(base28)+extras
 assert len(base28)==28 and len(ans)==52
 return ans

def signature(vec):
 return tuple(round(float(v),8) for v in vec)

def validate_rename(before,baseline,after,event,action,drop,x):
 offset=1000000000
 def renamed(records):
  return tuple((a+offset,b+offset,tuple(c)) for a,b,c in records)
 altered=(event[0]+offset,event[1],event[2]+offset)
 assert feature_52(renamed(before),renamed(baseline),renamed(after),altered,action,drop)==x,"NUMERIC_NODE_ID_LEAK"

def alias_counts(counter):
 mixed=[v for v in counter.values() if v["beneficial"] and v["harmful"]]
 return dict(unique_signatures=len(counter),mixed_signatures=len(mixed),
  beneficial_aliased=sum(x["beneficial"] for x in mixed),
  harmful_aliased=sum(x["harmful"] for x in mixed))

def cross_alias(regimes):
 old=regimes["original"];rot=regimes["local_rotate4"]
 return dict(cross_order_conflicting_signatures=sum(
  (a["beneficial"]>0 and rot[sig]["harmful"]>0)
  or (a["harmful"]>0 and rot[sig]["beneficial"]>0)
  for sig,a in old.items()),
  original_beneficial_vs_rotated_harmful=sum(
    a["beneficial"] for sig,a in old.items() if rot[sig]["harmful"]>0),
  rotated_beneficial_vs_original_harmful=sum(
    b["beneficial"] for sig,b in rot.items() if old[sig]["harmful"]>0))

def evaluate():
 spec=json.loads((P/"prereg.json").read_text())
 assert spec["synthetic_cohort"]["seeds"]==[-4801,-4817]
 assert spec["synthetic_cohort"]["families"]==[-2,-1]
 cells={28:collections.defaultdict(lambda:collections.defaultdict(collections.Counter)),
        52:collections.defaultdict(lambda:collections.defaultdict(collections.Counter))}
 labels=collections.defaultdict(collections.Counter)
 rows=[];rename_checks=0
 for seed in range(-4801,-4817,-1):
  for family in (-2,-1):
   public,q,meta=SOURCE.source(seed,family)
   assert SOURCE.BASE.public_witness(public,q)=={q["answer"]}
   regime=meta["arrival_regime"]
   before=()
   trace=[]
   case_labels=collections.Counter()
   first_rescue=None
   for index,event in enumerate(public):
    baseline,alternatives=F79.unique_alternatives(before,event,index)
    if alternatives:
     final_baseline=F62._finish_fixed(baseline,public[index+1:],PACK)
     base_good=PACK.solve(final_baseline,q)==q["answer"]
     for action,drop,after,feature28 in alternatives:
      final_candidate=F62._finish_fixed(after,public[index+1:],PACK)
      alt_good=PACK.solve(final_candidate,q)==q["answer"]
      if alt_good and not base_good:
       label="beneficial"
       if first_rescue is None:first_rescue=(index,after)
      elif base_good and not alt_good:
       label="harmful"
      else:label="neutral"
      feature52=feature_52(before,baseline,after,event,action,drop)
      assert feature52[:28]==tuple(feature28)
      validate_rename(before,baseline,after,event,action,drop,feature52)
      rename_checks+=1
      cells[28][regime][signature(feature28)][label]+=1
      cells[52][regime][signature(feature52)][label]+=1
      labels[regime][label]+=1
      case_labels[label]+=1
    before=baseline
    F62._valid_memory(before,PACK)
    trace.append(tuple(PACK.pack(*r).hex() for r in before))
   proof=AUDITOR.verify(public,q,trace)
   assert proof["prefixes"]==72 and proof["max_payload_bytes"]<=144
   fixed_good=PACK.solve(before,q)==q["answer"]
   if first_rescue is not None:
    assert not fixed_good
    F80.prove_single(public,q,*first_rescue)
   rows.append(dict(seed=seed,family=family,regime=regime,
     kind=meta["question_type"],frozen_F60_correct=int(fixed_good),
     beneficial=case_labels["beneficial"],harmful=case_labels["harmful"],
     neutral=case_labels["neutral"],first_valid_rescue=int(first_rescue is not None)))
 assert len(rows)==32 and rename_checks>0
 by={}
 for regime in ("original","local_rotate4"):
  case=[r for r in rows if r["regime"]==regime]
  assert len(case)==16
  by[regime]=dict(cases=16,frozen_F60_correct=sum(r["frozen_F60_correct"] for r in case),
   one_action_rescue_cases=sum(r["first_valid_rescue"] for r in case),
   labels=dict(labels[regime]),
   aliases_28=alias_counts(cells[28][regime]),
   aliases_52=alias_counts(cells[52][regime]))
  a=by[regime]["aliases_28"];b=by[regime]["aliases_52"]
  assert b["beneficial_aliased"]<=a["beneficial_aliased"]
  assert b["harmful_aliased"]<=a["harmful_aliased"]
 cross={str(dim):cross_alias(cells[dim]) for dim in (28,52)}
 assert cross["52"]["cross_order_conflicting_signatures"]<=cross["28"]["cross_order_conflicting_signatures"]
 report=dict(schema="yggdrasil.f81.directed-role-transition-feature-alias.synthetic.v1",
  stage="PREREGISTERED_SYNTHETIC_DIAGNOSTIC_ONLY",cases=len(rows),by_regime=by,
  cross_order=cross,rename_invariance_checks=rename_checks,
  frozen_F79_28_features_preserved=True,expanded_features=52,
  online_future_questions_used=False,no_model_fit=True,
  independent_72_prefix_audits_pass=True,
  FIT_TRAIN_used=False,FIT_VALIDATE_used=False,DIAG_used=False,ORIGINAL_used=False,
  F3=False,optimizer_promotion=False,
  improvement_in_opposite_credit_aliasing=(cross["52"]["cross_order_conflicting_signatures"]<cross["28"]["cross_order_conflicting_signatures"]),
  rows=rows)
 print(json.dumps(report,sort_keys=True))
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 evaluate()
