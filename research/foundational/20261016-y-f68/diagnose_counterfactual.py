"""F68 read-only negative-seed signal forensic; frozen teacher untouched."""
from __future__ import annotations
import hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert blob(P/"train_override.py")=="94d53f8d976cbfaa49cf3d48ee4db26c32778797"
s=importlib.util.spec_from_file_location("f68_original_frozen_counterfactual_teacher",P/"train_override.py")
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
rows=[]
for i in range(24):
 seed=-3001-i;fam=(-2,-1)[i%2]
 public,q,meta=m.m.SOURCE.source(seed,fam)
 examples,stats=m.examples(public,q)
 rows.append(dict(seed=seed,family=fam,question_type=meta["question_type"],
    **stats,examples=len(examples)))
totals={key:sum(x[key] for x in rows) for key in
 ("eligible_junction_steps","positive","negative","neutral","examples")}
result=dict(schema="yggdrasil.f68.counterfactual-signals.synthetic-forensic.v1",
 stage="FROZEN_READ_ONLY_SYNTHETIC",cases=len(rows),totals=totals,
 both_credit_signs_present=bool(totals["positive"] and totals["negative"]),
 source_unchanged=True,teacher_unchanged=True,weights_not_fitted=True,
 registered_FIT_train_used=False,registered_FIT_validation_used=False,
 DIAG_used=False,original_used=False,F3=False,policy_promotion=False,rows=rows)
print(json.dumps(result,sort_keys=True))
