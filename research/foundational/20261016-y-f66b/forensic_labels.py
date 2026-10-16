"""Read-only synthetic audit of frozen F66B positive/negative labels.

No methodological changes, no registered FIT/VALIDATE/DIAG/ORIGINAL access.
"""
import hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes();return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert blob(P/"attachment_teacher.py")=="6ec8d3352be9b12f42a821bfb3781ea1570de63a"
assert blob(P/"prereg.json")=="551644239204be97cdb5944b7108d9ecca82c709"
spec=importlib.util.spec_from_file_location("f66b_frozen_label_forensic",P/"attachment_teacher.py")
t=importlib.util.module_from_spec(spec);sys.modules[spec.name]=t;spec.loader.exec_module(t)
cases=[]
for i in range(24):
 seed=-2101-i
 family=(-2,-1)[i%2]
 public,q,meta=t.POLICY.SOURCE.source(seed,family)
 gates,ranks,pos,neg=t.supervised_case(public)
 labels=[label for _features,label in gates]
 cases.append(dict(seed=seed,family=family,kind=meta["question_type"],
    gate_examples=len(gates),rank_pairs=len(ranks),
    positive=pos,negative=neg,neutral=len(gates)-pos-neg,
    max_label=max(labels,default=0),min_label=min(labels,default=0)))
totals={name:sum(r[name] for r in cases) for name in ("gate_examples","rank_pairs","positive","negative","neutral")}
result=dict(schema="yggdrasil.f66b.frozen-synthetic-label-forensics.v1",
 status="READ_ONLY_LABEL_DIAGNOSIS",unregistered_synthetic_cases=len(cases),
 totals=totals,balanced=totals["positive"]>0 and totals["negative"]>0,
 method_or_threshold_change=False,registered_fit_consumed=False,
 heldout_consumed=False,diagnostic_consumed=False,original_consumed=False,
 F3=False,optimizer_promotion=False,rows=cases)
print(json.dumps(result,sort_keys=True))
