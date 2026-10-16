"""F72 read-only independent synthetic counterfactual feature identifiability.

Exact F71 teacher & native alternatives. Runs ONLY preregistered negative
synthetic source identities. Task answers are inspected OFFLINE for audit,
never fed to online policy or used to train fitted weights.
"""
from __future__ import annotations
import collections,hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def gitblob(path):
 raw=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
assert gitblob(P/"prereg.json")=="b8d4c43491e5101041d07a1b83af600b335117e6"
F71=P.parent/"20261016-y-f71"/"early_scheduler.py"
assert gitblob(F71)=="edddfedb04af27dac7332ca85cc742aef5772a4b"
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
 return m
m=load("f72_sha_frozen_original_F71",F71)
SPEC=json.loads((P/"prereg.json").read_text())
cohort=SPEC["cohort"]
assert cohort["synthetic_negative_seeds"]==[-3701,-3717]
assert cohort["families"]==[-2,-1]
assert cohort["total_cases"]==16
label_classes=(1.0,-1.0,-.25)
rows=[]
aliased=collections.defaultdict(lambda:collections.Counter())
examples_by_label={k:[] for k in label_classes}
positive_indices=[]
for k in range(16):
 seed=-3701-k;family=(-2,-1)[k%2]
 public,q,meta=m.SOURCE.source(seed,family)
 assert len(public)==72
 mem=();trace=[]
 count=collections.Counter()
 positive_at=[]
 native_actions=0
 for i,event in enumerate(public):
  base,alts=m.native_alternatives(mem,event,i)
  future=m.F62._finish_fixed(base,public[i+1:],m.PACK)
  f60_expected=m.PACK.solve(future,q)==q["answer"]
  for action,drop,after,x in alts:
   terminal=m.F62._finish_fixed(after,public[i+1:],m.PACK)
   alternative_correct=m.PACK.solve(terminal,q)==q["answer"]
   if alternative_correct and not f60_expected:label=1.0
   elif f60_expected and not alternative_correct:label=-1.0
   else:label=-.25
   assert len(x)==12
   key=tuple(round(float(v),8) for v in x)
   count[label]+=1;native_actions+=1
   aliased[key][label]+=1
   examples_by_label[label].append(x)
   if label==1.0:positive_at.append(i)
  mem=base
  trace.append(tuple(m.PACK.pack(*record).hex() for record in mem))
 proof=m.AUDIT.verify(public,q,trace)
 assert proof["prefixes"]==72 and proof["max_payload_bytes"]<=144
 frozen_correct=m.PACK.solve(mem,q)==q["answer"]
 rows.append(dict(seed=seed,family=family,
  question_type=meta["question_type"],
  frozen_F60_correct=bool(frozen_correct),
  native_alternatives=native_actions,
  beneficial=count[1.0],harmful=count[-1.0],neutral=count[-.25],
  first_beneficial_index=min(positive_at) if positive_at else None,
  positive_decision_count=len(set(positive_at)),
  independent_causal_72_prefix_pass=True))
 positive_indices.extend(positive_at)
counts=dict(
 beneficial=sum(r["beneficial"] for r in rows),
 harmful=sum(r["harmful"] for r in rows),
 neutral=sum(r["neutral"] for r in rows))
aliases=dict(
 feature_vectors=len(aliased),
 beneficial_and_harmful=sum(1 for v in aliased.values() if v[1.0] and v[-1.0]),
 beneficial_and_neutral=sum(1 for v in aliased.values() if v[1.0] and v[-.25]),
 harmful_and_neutral=sum(1 for v in aliased.values() if v[-1.0] and v[-.25]))
ranges={}
for index in range(12):
 def bounds(label):
  values=[x[index] for x in examples_by_label[label]]
  return [round(min(values),8),round(max(values),8)] if values else None
 beneficial=bounds(1.0);harmful=bounds(-1.0)
 ranges[str(index)]=dict(beneficial=beneficial,harmful=harmful,
  intersects=bool(beneficial and harmful and
    max(beneficial[0],harmful[0])<=min(beneficial[1],harmful[1])))
by_kind={}
for kind in sorted({r["question_type"] for r in rows}):
 part=[r for r in rows if r["question_type"]==kind]
 by_kind[kind]=dict(cases=len(part),F60_correct=sum(r["frozen_F60_correct"] for r in part),
   beneficial=sum(r["beneficial"] for r in part),harmful=sum(r["harmful"] for r in part),
   neutral=sum(r["neutral"] for r in part),
   cases_with_beneficial=sum(r["beneficial"]>0 for r in part))
result=dict(schema="yggdrasil.f72.counterfactual-feature-identifiability.v1",
 stage="READ_ONLY_UNREGISTERED_SYNTHETIC",
 cases=len(rows),total_native_candidates=sum(r["native_alternatives"] for r in rows),
 frozen_F60_correct=sum(r["frozen_F60_correct"] for r in rows),
 labels=counts,beneficial_label_rate=counts["beneficial"]/sum(counts.values()),
 cases_with_beneficial=sum(r["beneficial"]>0 for r in rows),
 first_beneficial_positions_by_case=[
  dict(seed=r["seed"],first_index=r["first_beneficial_index"])
  for r in rows if r["first_beneficial_index"] is not None],
 feature_aliases=aliases,per_feature_ranges=ranges,by_question_type=by_kind,
 independent_72_prefix_audit=True,
 no_model_training_or_weight_fit=True,
 registered_FIT_train_used=False,registered_FIT_validate_used=False,
 DIAG_used=False,original_used=False,F3=False,optimizer_promotion=False,
 rows=rows)
print(json.dumps(result,sort_keys=True))
