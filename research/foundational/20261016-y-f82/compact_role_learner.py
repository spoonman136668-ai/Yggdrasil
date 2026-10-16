"""F82 compact causal public-role intervention learner, synthetic train+guard only.

Model sees 24 F81 public graph-role statistics, trained on F79's frozen
offline suffix teacher. No registered FIT/DIAG/original dispatch.
"""
from __future__ import annotations
import collections,hashlib,importlib.util,json,math,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def gitblob(path):
 raw=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
assert gitblob(P/"prereg.json")=="1b60e145d54730998c04a28829db9ac88d5a9460"
parent=P.parent/"20261016-y-f81"/"role_alias_audit.py"
assert gitblob(parent)=="3a2f6a8a46d7be36c8a793b732acd735485d73a5"
sp=importlib.util.spec_from_file_location("f82_frozen_F81_role_features",parent)
F81=importlib.util.module_from_spec(sp);sys.modules[sp.name]=F81;sp.loader.exec_module(F81)
F79=F81.F79;F62=F81.F62;PACK=F81.PACK;SOURCE=F81.SOURCE;AUDITOR=F81.AUDITOR
NUM_FEATURES=24
SYNTH_TRAIN=range(-4901,-4917,-1)
SYNTH_GUARD=range(-4921,-4937,-1)
FAMILIES=(-2,-1)
def features(before,baseline,after,event,action,drop):
 old=F81.public_role_counts(baseline,event)
 new=F81.public_role_counts(after,event)
 vec=tuple((right-left)/12 for left,right in zip(old,new))
 assert len(vec)==24
 return vec
def sigmoid(value):
 if value>=0:
  return 1/(1+math.exp(-min(value,40)))
 e=math.exp(max(value,-40))
 return e/(1+e)
def prepare_offline(public,question):
 memory=()
 examples=[]
 labels=collections.Counter()
 for index,event in enumerate(public):
  baseline,alternatives=F79.unique_alternatives(memory,event,index)
  if alternatives:
   baseline_final=F62._finish_fixed(baseline,public[index+1:],PACK)
   baseline_good=PACK.solve(baseline_final,question)==question["answer"]
   for action,drop,after,_features28 in alternatives:
    end=F62._finish_fixed(after,public[index+1:],PACK)
    alternate_good=PACK.solve(end,question)==question["answer"]
    label="beneficial" if alternate_good and not baseline_good else (
        "harmful" if baseline_good and not alternate_good else "neutral")
    examples.append((features(memory,baseline,after,event,action,drop),label))
    labels[label]+=1
  memory=baseline
 return examples,labels
def train(inputs):
 observations=[]
 labels=collections.Counter()
 for public,question in inputs:
  samples,counts=prepare_offline(public,question)
  observations.extend(samples);labels.update(counts)
 assert labels["beneficial"]>0 and labels["harmful"]>0
 weights=[0.0]*NUM_FEATURES
 grade={"beneficial":128.0,"harmful":1.0,"neutral":0.01}
 for epoch in range(3):
  for vec,label in observations:
   pred=sigmoid(sum(w*v for w,v in zip(weights,vec)))
   scale=.025*grade[label]*(int(label=="beneficial")-pred)
   for j,value in enumerate(vec):
    weights[j]+=scale*value
 quant=tuple(max(-127,min(127,round(w*32))) for w in weights)
 assert len(quant)==24
 return quant,dict(labels=dict(labels),training_cases=len(inputs),candidate_examples=len(observations))
def online(public,weights,enabled,trace=False):
 assert len(public)==72 and all(len(e)==3 for e in public)
 assert len(weights)==NUM_FEATURES and all(type(w) is int and -127<=w<=127 for w in weights)
 memory=()
 snapshots=[]
 interventions=0
 for index,event in enumerate(public):
  baseline,options=F79.unique_alternatives(memory,event,index)
  best=None
  if enabled:
   for j,(action,drop,after,_prior28) in enumerate(options):
    v=features(memory,baseline,after,event,action,drop)
    probability=sigmoid(sum((w/32)*f for w,f in zip(weights,v)))
    key=(probability,-j)
    if best is None or key>best[0]:
     best=(key,after)
  if best is not None and best[0][0]>.90:
   memory=best[1]
   interventions+=1
  else:
   memory=baseline
  F62._valid_memory(memory,PACK)
  if trace:snapshots.append(tuple(PACK.pack(*r).hex() for r in memory))
 return memory,tuple(snapshots),interventions
def evaluate():
 cfg=json.loads((P/"prereg.json").read_text())
 assert cfg["training"]["train_seeds"]==[-4901,-4917]
 assert cfg["training"]["guard_seeds"]==[-4921,-4937]
 inputs=[]
 for seed in SYNTH_TRAIN:
  for family in FAMILIES:
   public,q,meta=SOURCE.source(seed,family)
   assert SOURCE.BASE.public_witness(public,q)=={q["answer"]}
   inputs.append((public,q))
 weights,train_receipt=train(inputs)
 rows=[]
 for seed in SYNTH_GUARD:
  for family in FAMILIES:
   public,q,meta=SOURCE.source(seed,family)
   learned,trace,num_interventions=online(public,weights,True,True)
   baseline,baseline_trace,none=online(public,weights,False,True)
   assert none==0
   assert baseline==F62.controls()[0].online_fixed(public),"F82_F60_DEFAULT_DRIFT"
   for path in (trace,baseline_trace):
    audit=AUDITOR.verify(public,q,path)
    assert audit["prefixes"]==72 and audit["max_payload_bytes"]<=144
   rows.append(dict(seed=seed,family=family,
    regime=meta["arrival_regime"],kind=meta["question_type"],
    learned_correct=int(PACK.solve(learned,q)==q["answer"]),
    F60_correct=int(PACK.solve(baseline,q)==q["answer"]),
    interventions=num_interventions))
 by={}
 for regime in ("original","local_rotate4"):
  case=[r for r in rows if r["regime"]==regime]
  assert len(case)==16
  learned=sum(r["learned_correct"] for r in case)
  fixed=sum(r["F60_correct"] for r in case)
  rescue=sum(r["learned_correct"] and not r["F60_correct"] for r in case)
  damaged=sum(r["F60_correct"] and not r["learned_correct"] for r in case)
  by[regime]=dict(cases=len(case),learned_correct=learned,F60_correct=fixed,
   interventions=sum(r["interventions"] for r in case),rescued=rescue,
   regressed=damaged,nondegradation=learned>=fixed)
 qualified=(all(entry["nondegradation"] for entry in by.values())
  and sum(entry["interventions"] for entry in by.values())>0
  and sum(entry["rescued"] for entry in by.values())>0)
 verdict=dict(schema="yggdrasil.f82.compact-public-role.synthetic-train-and-guard.v1",
  stage="SYNTHETIC_FROZEN_TRAIN_SEPARATE_GUARD",
  training_receipt=train_receipt,frozen_int8_weights=list(weights),
  frozen_weights_sha256=hashlib.sha256(bytes(w%256 for w in weights)).hexdigest(),
  train_cases=len(inputs),guard_cases=len(rows),by_regime=by,
  all_public_prefix_audits_passed=True,one_model_trained_before_guard=True,
  scientific_prequalification_pass=qualified,all_protected_FIT_and_originals_untouched=True,
  no_F3_or_optimizer_promotion=True,rows=rows)
 print(json.dumps(verdict,sort_keys=True),flush=True)
 if not qualified:raise AssertionError("F82_PREREG_SYNTHETIC_METHOD_GATE_NEGATIVE")
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 evaluate()
