"""Read-only diagnosis of F66 sparse/imbalanced offline teacher labels."""
import hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def gitblob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert gitblob(P/"dense_teacher.py")=="4924a409a446403c0c2a5d1e146adc8171ae4791"
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
teacher=load("f66_frozen_synthetic_teacher_diagnostics",P/"dense_teacher.py")
rows=[]
for cohort in (1,2):
 for i in range(8):
  seed=(-1901 if cohort==1 else -1921)-i
  family=(-2,-1)[i%2]
  public,q,meta=teacher.POLICY.SOURCE.source(seed,family)
  gate,rank,positive,negative=teacher.supervised_case(public)
  rows.append(dict(seed=seed,cohort=cohort,family=family,
      available_gate=len(gate),rank_pairs=len(rank),
      positive=positive,negative=negative,
      neutral=sum(abs(t)<1e-8 for _x,t in gate),
      question_type=meta["question_type"]))
counts={k:sum(r[k] for r in rows) for k in
 ("available_gate","rank_pairs","positive","negative","neutral")}
status="BALANCED" if min(counts["positive"],counts["negative"])>0 else "IMBALANCED"
print(json.dumps(dict(schema="yggdrasil.f66.synthetic-teacher-label-forensics.v1",
 status=status,cases=len(rows),counts=counts,
 registered_fit_executed=False,heldout_executed=False,
 teacher_method_modified=False,F3=False,rows=rows),sort_keys=True))
