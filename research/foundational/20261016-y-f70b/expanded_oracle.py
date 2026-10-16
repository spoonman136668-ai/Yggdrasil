"""F70B expanded synthetic-only 1/2-step unfair public-memory reachability.

No trained method or protected data. Every counterfactual state is a native
F62 ACTION.actions successor. The independent immutable causal auditor
certifies any claimed rescue trace across all 72 observed public events.
"""
from __future__ import annotations
import hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes();return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert blob(P/"prereg.json")=="4ba4b10147eb8e854e8c43f5a1aa6c1184d17816"
parent=P.parent/"20261016-y-f70"/"reachability.py"
assert blob(parent)=="ab650d69d823a0d29eb27af9fd56147e65ccfd73"
spec=importlib.util.spec_from_file_location("f70b_frozen_original_reachability",parent)
f=importlib.util.module_from_spec(spec);sys.modules[spec.name]=f;spec.loader.exec_module(f)
def unique_alternatives(before,event,index):
 baseline=f.ACTION._f60_step(before,event,f.PACK)
 return tuple(dict.fromkeys(c[3] for c in f.ACTION.actions(before,event,index,f.PACK)
                            if c[3]!=baseline))
def expanded_oracle(public,q):
 before,last,trace=f.f60_prefix(public)
 assert f.AUDIT.verify(public,q,trace)["prefixes"]==72
 f60=bool(f.PACK.solve(last,q)==q["answer"])
 if f60:return dict(F60_correct=True,one_step_rescue=False,
    two_step_rescue=False,first_candidates=0,second_pairs=0,
    rescue_indices=None)
 first_count=0;second_count=0
 # Every public prefix eligible, all unique authorized one-step actions.
 for i in range(72):
  for alternative in unique_alternatives(before[i],public[i],i):
   first_count+=1
   terminal=f.ACTION._finish_fixed(alternative,public[i+1:],f.PACK)
   if f.PACK.solve(terminal,q)==q["answer"]:
    assert f.oracle_success(public,q,{i:alternative})
    return dict(F60_correct=False,one_step_rescue=True,
      two_step_rescue=False,first_candidates=first_count,
      second_pairs=0,rescue_indices=[i])
 # Fixed original eight starting checkpoints; flexible 1..8-event lag.
 for i in f.CHECKPOINTS:
  choices=unique_alternatives(before[i],public[i],i)
  for alternative in choices:
   middle=alternative
   for j in range(i+1,min(72,i+9)):
    if j>i+1:
     middle=f.ACTION._f60_step(middle,public[j-1],f.PACK)
    for after in unique_alternatives(middle,public[j],j):
     second_count+=1
     terminal=f.ACTION._finish_fixed(after,public[j+1:],f.PACK)
     if f.PACK.solve(terminal,q)==q["answer"]:
      assert f.oracle_success(public,q,{i:alternative,j:after})
      return dict(F60_correct=False,one_step_rescue=False,
        two_step_rescue=True,first_candidates=first_count,
        second_pairs=second_count,rescue_indices=[i,j])
 return dict(F60_correct=False,one_step_rescue=False,
    two_step_rescue=False,first_candidates=first_count,
    second_pairs=second_count,rescue_indices=None)
def synthetic_study():
 rows=[]
 for k in range(16):
  seed=-3401-k;family=(-2,-1)[k%2]
  public,q,meta=f.SOURCE.source(seed,family)
  result=expanded_oracle(public,q)
  rows.append(dict(seed=seed,family=family,
    question_type=meta["question_type"],**result))
 failures=[r for r in rows if not r["F60_correct"]]
 outcome=dict(schema="yggdrasil.f70b.expanded-synthetic-oracle-reachability.v1",
  status="SYNTHETIC_NONCOMPETITIVE_DIAGNOSTIC",
  cases=len(rows),F60_correct=sum(r["F60_correct"] for r in rows),
  F60_failures=len(failures),
  single_step_rescues=sum(r["one_step_rescue"] for r in failures),
  two_step_rescues=sum(r["two_step_rescue"] for r in failures),
  unresolved_failures=sum(not(r["one_step_rescue"] or r["two_step_rescue"]) for r in failures),
  first_step_candidates=sum(r["first_candidates"] for r in failures),
  second_step_pairs=sum(r["second_pairs"] for r in failures),
  unfair_future_question_oracle=True,
  original_action_space_unchanged=True,
  model_trained=False,protected_FIT_used=False,
  validation_used=False,DIAG_used=False,
  original_used=False,F3=False,optimizer_promotion=False,
  rows=rows)
 print(json.dumps(outcome,sort_keys=True))
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 synthetic_study()
