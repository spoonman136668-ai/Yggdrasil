"""F83 frozen pairwise public-only ranking learner; negative-seed synthetic ONLY.

Distinct from F82's logistic-probability classifier; training ranks source
native interventions at same causal observation prefix. Independent guard
cohort is touched only after 24 int8 weights have been finalized.
"""
from __future__ import annotations
import collections,hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def gitblob(path):
 raw=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
assert gitblob(P/"prereg.json")=="2c47c4116bcad183ef2e3f327b9760b8ea95b3c1"
old=P.parent/"20261016-y-f82"/"compact_role_learner.py"
assert gitblob(old)=="b5d969deeb63e99c1b235f675a0532c16863e519"
spec=importlib.util.spec_from_file_location("f83_exact_source_public_roles",old)
M=importlib.util.module_from_spec(spec);sys.modules[spec.name]=M;spec.loader.exec_module(M)
NUM=24
def score(weights,x):
 assert len(weights)==len(x)==NUM
 return sum(w*z for w,z in zip(weights,x))
def training_groups(public,q):
 memory=()
 groups=[]
 counts=collections.Counter()
 for index,event in enumerate(public):
  baseline,options=M.F79.unique_alternatives(memory,event,index)
  group=[]
  if options:
   base_end=M.F62._finish_fixed(baseline,public[index+1:],M.PACK)
   good=M.PACK.solve(base_end,q)==q["answer"]
   for action,drop,after,_ in options:
    candidate_end=M.F62._finish_fixed(after,public[index+1:],M.PACK)
    candidate_good=M.PACK.solve(candidate_end,q)==q["answer"]
    label="beneficial" if candidate_good and not good else ("harmful" if good and not candidate_good else "neutral")
    vector=M.features(memory,baseline,after,event,action,drop)
    group.append((vector,label))
    counts[label]+=1
  if group:groups.append(group)
  memory=baseline
 return groups,counts
def train(data):
 groups=[];totals=collections.Counter()
 for public,q in data:
  local,count=training_groups(public,q)
  groups.extend(local);totals.update(count)
 assert totals["beneficial"]>0 and totals["harmful"]>0, "NO_BIDIRECTIONAL_LABELS"
 weights=[0.0]*NUM
 zero=(0.0,)*NUM
 for epoch in range(4):
  for group in groups:
   positives=[vec for vec,label in group if label=="beneficial"]
   for positive in positives:
    competing=[vec for vec,_ in group if vec!=positive]
    other=max(competing,key=lambda v:score(weights,v)) if competing else zero
    delta=[a-b for a,b in zip(positive,other)]
    if score(weights,delta)<0.5:
     for i,d in enumerate(delta):weights[i]+=.05*d
   for vec,label in group:
    z=score(weights,vec)
    if label=="harmful" and z>-.1:
     for i,v in enumerate(vec):weights[i]-=.05*v
    elif label=="neutral" and z>.1:
     for i,v in enumerate(vec):weights[i]-=.002*v
 quant=tuple(max(-127,min(127,round(w*64))) for w in weights)
 assert len(quant)==NUM
 return quant,dict(labels=dict(totals),training_cases=len(data),
  candidate_examples=sum(totals.values()),contexts=len(groups))
def online(public,quant,enabled,trace=False):
 assert len(quant)==NUM and all(type(w) is int and -127<=w<=127 for w in quant)
 memory=()
 snapshots=[]
 interventions=0
 for index,event in enumerate(public):
  baseline,options=M.F79.unique_alternatives(memory,event,index)
  ranked=[]
  if enabled:
   for j,(act,drop,after,_) in enumerate(options):
    vector=M.features(memory,baseline,after,event,act,drop)
    s=score(tuple(w/64 for w in quant),vector)
    ranked.append((s,-j,after))
  ranked.sort(reverse=True)
  if ranked:
   top=ranked[0][0]
   runnerup=ranked[1][0] if len(ranked)>1 else 0.0
   if top>0.0 and top-runnerup>=.05:
    memory=ranked[0][2];interventions+=1
   else:memory=baseline
  else:memory=baseline
  M.F62._valid_memory(memory,M.PACK)
  if trace:snapshots.append(tuple(M.PACK.pack(*record).hex() for record in memory))
 return memory,tuple(snapshots),interventions
def evaluate():
 spec=json.loads((P/"prereg.json").read_text())
 assert spec["cohorts"]["synthetic_train_seeds"]==[-5101,-5117]
 assert spec["cohorts"]["synthetic_guard_seeds"]==[-5121,-5137]
 inputs=[]
 for seed in range(-5101,-5117,-1):
  for family in (-2,-1):
   public,q,_=M.SOURCE.source(seed,family)
   assert M.SOURCE.BASE.public_witness(public,q)=={q["answer"]}
   inputs.append((public,q))
 frozen,train_report=train(inputs)
 rows=[]
 for seed in range(-5121,-5137,-1):
  for family in (-2,-1):
   public,q,meta=M.SOURCE.source(seed,family)
   model,trace,interventions=online(public,frozen,True,True)
   fixed,baseline_trace,no=online(public,frozen,False,True)
   assert no==0 and fixed==M.F62.controls()[0].online_fixed(public)
   for snap in (trace,baseline_trace):
    proof=M.AUDITOR.verify(public,q,snap)
    assert proof["prefixes"]==72 and proof["max_payload_bytes"]<=144
   rows.append(dict(seed=seed,family=family,
    regime=meta["arrival_regime"],kind=meta["question_type"],
    learned_correct=int(M.PACK.solve(model,q)==q["answer"]),
    F60_correct=int(M.PACK.solve(fixed,q)==q["answer"]),
    interventions=interventions))
 by={}
 for regime in ("original","local_rotate4"):
  case=[r for r in rows if r["regime"]==regime]
  assert len(case)==16
  learned=sum(r["learned_correct"] for r in case)
  fixed=sum(r["F60_correct"] for r in case)
  by[regime]=dict(cases=len(case),learned_correct=learned,
   F60_correct=fixed,interventions=sum(r["interventions"] for r in case),
   rescued=sum(r["learned_correct"] and not r["F60_correct"] for r in case),
   regressed=sum(r["F60_correct"] and not r["learned_correct"] for r in case),
   nondegradation=learned>=fixed)
 qualified=(all(x["nondegradation"] for x in by.values())
  and sum(x["interventions"] for x in by.values())>0
  and sum(x["rescued"] for x in by.values())>0)
 result=dict(schema="yggdrasil.f83.pairwise-rare-public-intervention.synthetic.v1",
  stage="FROZEN_SYNTHETIC_TRAIN_AND_DISJOINT_GUARD",
  train_cases=len(inputs),guard_cases=len(rows),frozen_24_signed_int8=list(frozen),
  frozen_weights_sha256=hashlib.sha256(bytes(w%256 for w in frozen)).hexdigest(),
  training_receipt=train_report,by_arrival_regime=by,
  source_native_action_only=True,independent_all_72_prefix_audits_pass=True,
  prereg_synthetic_qualification=qualified,
  FIT_TRAIN_used=False,FIT_VALIDATION_used=False,DIAG_used=False,
  ORIGINAL_used=False,F3=False,optimizer_promotion=False,rows=rows)
 print(json.dumps(result,sort_keys=True),flush=True)
 if not qualified:raise AssertionError("F83_PREREG_SYNTHETIC_PREQUALIFICATION_FAILED")
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 evaluate()
