"""F64 offline TRAIN-only bridge-credit fitting. No heldout generation.

Offline task/question is allowed only to compute sparse counterfactual
partial-query coverage labels. Learned runtime policy receives only public
prefix, lossless retained records and fitted signed-int8 bridge weights.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,math,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
EVIDENCE_SHA256="1dd0a0c58a323821ff121b4748d5d13224817c3022e5d7950ca2536e114475bd"
def gitblob(p):
 b=p.read_bytes();return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert gitblob(P/"prereg.json")=="aa12b1785b92eec5eb5096d6ef0cd600e97904ad"
def load(name,path):
 sp=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(sp);sys.modules[name]=m;sp.loader.exec_module(m);return m
FEATURES=load("f64_frozen_bridge_policy",P/"bridge_features.py")
PACK=FEATURES.PACK
BASE=FEATURES.BASE
def invert(r):
 a,b,c=r;return b,a,tuple(x^1 for x in reversed(c))
def prefix_steps(records,q):
 # OFFLINE ONLY: this question must never be supplied to online().
 codes=tuple(2*r+(direction==-1) for r,direction in q["ops"])
 states={(q["start"],0)}
 for _ in range(len(codes)):
  expanded=set(states)
  for at,offset in states:
   for rec in records:
    for a,b,steps in (rec,invert(rec)):
     if at==a and codes[offset:offset+len(steps)]==steps:
      expanded.add((b,offset+len(steps)))
  if expanded==states:break
  states=expanded
 return max(offset for _node,offset in states)
def examples_from_training(public,question):
 assert len(public)==72 and 4<=len(question["ops"])<=6
 examples=[];mem=()
 for index,event in enumerate(public):
  choices=BASE.actions(mem,event,index,PACK)
  baseline=BASE._f60_step(mem,event,PACK)
  matching=[c for c in choices if c[3]==baseline]
  assert matching,"FROZEN_F60_NOT_IN_ACTION_SPACE"
  base=matching[0]
  ref_features=FEATURES.features(mem,event,baseline,base[0],index)
  ref_coverage=prefix_steps(baseline,question)
  bridge_event=any(FEATURES.features(mem,event,c[3],c[0],index)[3]>0 for c in choices)
  if index%8==7 or bridge_event:
   for action,_old,_drop,after,_old_feats in choices:
    feats=FEATURES.features(mem,event,after,action,index)
    label=(prefix_steps(after,question)-ref_coverage)/len(question["ops"])
    diff=tuple(a-b for a,b in zip(feats,ref_features))
    if any(abs(z)>1e-9 for z in diff):
     examples.append((diff,label))
  mem=baseline
 assert examples
 return examples
def train(rows):
 observations=[]
 for public,q in rows:
  observations.extend(examples_from_training(public,q))
 assert observations
 weights=[0.0]*FEATURES.PARAMS
 for _epoch in range(3):
  for feats,delta in observations:
   x=tuple(max(-1,min(1,v)) for v in feats)
   prediction=math.tanh(sum(w*feature for w,feature in zip(weights,x)))
   for j,value in enumerate(x):
    weights[j]+=.035*(delta-prediction)*value
 fitted=tuple(max(-127,min(127,round(w*16))) for w in weights)
 assert len(fitted)==FEATURES.PARAMS
 return fitted,len(observations)
def synthetic_guard():
 rows=[]
 for seed,family in ((-801,-2),(-802,-1),(-803,-2),(-804,-1)):
  public,q,_=FEATURES.SOURCE.source(seed,family)
  rows.append((public,q))
 weights,n=train(rows)
 for public,q in rows:
  memory,trace=FEATURES.online(public,weights,True)
  claim=FEATURES.AUDIT.verify(public,q,trace)
  assert claim["prefixes"]==72 and claim["max_payload_bytes"]<=144
 return dict(schema="yggdrasil.f64.bridge-credit-algorithm.synthetic.v1",
    stage="SYNTHETIC_SOURCE_ONLY",examples=n,
    provisional_synthetic_weights=list(weights),synthetic_cases=len(rows),
    protected_fit_executed=False,heldout_executed=False,F3=False)
def fit(path):
 raw=path.read_bytes()
 assert hashlib.sha256(raw).hexdigest()==EVIDENCE_SHA256,"PROTECTED_TRAIN_EVIDENCE_DRIFT"
 rows=[json.loads(s) for s in raw.decode("utf-8").splitlines()]
 assert len(rows)==32
 identities={(r["seed"],r["family"]) for r in rows}
 expected={(seed,family) for seed in range(811000,811008) for family in (1560,1561,1562,1563)}
 assert identities==expected,"OFF-COHORT_TRAINING_REJECTED"
 # Strict boundary: q feeds ONLY offline labeler train(), never FEATURES.online.
 exposed=[(tuple(tuple(e) for e in row["public"]),row["postretention_question"]) for row in rows]
 weights,n=train(exposed)
 return dict(schema="yggdrasil.f64.bridge-credit-frozen-fit.v1",
    stage="FROZEN_AFTER_SINGLE_TRAINING_CORPUS",trained_weights=list(weights),
    weights_sha256=hashlib.sha256(bytes(w%256 for w in weights)).hexdigest(),
    source_first_use_run=38886882471,source_artifact_id=12039084883,
    fit_rows_sha256=EVIDENCE_SHA256,train_cases=len(rows),
    supervised_partial_query_credit_examples=n,params=len(weights),
    frozen_source_sha="c04b73306861098eecf55db77b2db486aa918819",
    future_question_only_offline_training=True,
    future_question_online=False,fit_train_rerun=False,
    fit_validation_executed=False,diagnostics_executed=False,
    originals_executed=False,scientific_improvement_qualified=False,
    F3=False,policy_promotion=False)
if __name__=="__main__":
 parser=argparse.ArgumentParser()
 group=parser.add_mutually_exclusive_group(required=True)
 group.add_argument("--synthetic-only",action="store_true")
 group.add_argument("--fit-evidence",type=pathlib.Path)
 args=parser.parse_args()
 print(json.dumps(synthetic_guard() if args.synthetic_only else fit(args.fit_evidence),sort_keys=True))
