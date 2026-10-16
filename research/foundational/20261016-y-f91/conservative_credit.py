#!/usr/bin/env python3
"""F91 frozen conservative learned temporal-credit mechanism.

Only TRAIN label extraction sees a future suffix or known answer.
Inference consumes (public arrivals, signed-int8 weights, exact native
actions/codec). The intervention latch is a single explicitly counted bit.
"""
from __future__ import annotations
import hashlib,importlib.util,json,math,sys
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parent
PREREG_SHA="7a680c47029777f5d27b924d75c750bb348c06fc"
F90_BLOB="0b689d66135a246987b20e189b9724b1c0715c25"
TRAIN_SEEDS=range(-5801,-5817,-1)
FAMILIES=(-2,-1)
CHECKPOINTS=(47,59,71)
MAX_ALT=8
DIMS=12

def gitblob(p):
 b=p.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def loader(name,p,blob):
 assert gitblob(p)==blob,("F91_FROZEN_PARENT_DRIFT",name)
 s=importlib.util.spec_from_file_location(name,p)
 m=importlib.util.module_from_spec(s)
 sys.modules[name]=m;s.loader.exec_module(m)
 return m
def vector(base_features,alternative_features):
 assert len(base_features)==len(alternative_features)==DIMS
 return (1.0,)+tuple(float(alternative_features[i]-base_features[i]) for i in range(1,DIMS))
def sigmoid(x):
 return 1.0/(1.0+math.exp(-max(-30.,min(30.,x))))
def score(weights,features):
 assert len(weights)==DIMS and len(features)==DIMS
 return sigmoid(sum((weight/48.0)*feature for weight,feature in zip(weights,features)))
def fit(examples):
 """Exact deterministic 2-head logistic objective; no cohort selection."""
 assert examples
 benefit=[0.]*DIMS
 harm=[0.]*DIMS
 for epoch in range(4):
  for features,advantage in examples:
   assert advantage in (-1,0,1)
   for weights,target,positive_cost in (
       (benefit,float(advantage==1),4.0),
       (harm,float(advantage==-1),6.0)):
    p=sigmoid(sum(w*x for w,x in zip(weights,features)))
    multiplier=positive_cost if target else 1.0
    for i,x in enumerate(features):
     weights[i]=max(-2.0,min(2.0,0.995*weights[i]+0.08*multiplier*(target-p)*x))
 b=tuple(max(-96,min(96,round(w*48))) for w in benefit)
 h=tuple(max(-96,min(96,round(w*48))) for w in harm)
 assert len(b)==len(h)==DIMS
 return b,h

def choose(memory,event,index,used,benefit,harm,pack,F62):
 """Only known public prefix and native F62 actions, no question or future."""
 assert type(used) is bool
 assert all(type(v) is int and -96<=v<=96 for v in (*benefit,*harm))
 assert len(benefit)==len(harm)==DIMS
 baseline=F62._f60_step(memory,event,pack)
 options=F62.actions(memory,event,index,pack)
 exact=[op for op in options if op[3]==baseline]
 assert len(exact)==1,"F91_F60_BASELINE_NOT_NATIVE"
 if used or index<48:
  return baseline,False,0
 base_features=exact[0][4]
 choices=[]
 examined=0
 for j,op in enumerate(options):
  after=op[3]
  if after==baseline:continue
  examined+=1
  required=min(10,max(0,len(baseline)-1))
  overlap=sum(r in baseline for r in after)
  if overlap<required:continue
  features=vector(base_features,op[4])
  p_good=score(benefit,features)
  p_harm=score(harm,features)
  if p_good>=0.70 and p_harm<=0.20 and p_good-p_harm>=0.55:
   choices.append((p_good-p_harm,p_good,-j,after))
 if choices:
  selected=max(choices)[3]
  assert selected in {c[3] for c in options}
  F62._valid_memory(selected,pack)
  return selected,True,examined
 return baseline,False,examined

def online(public,benefit,harm,pack,F62,trace=False):
 assert len(public)==72 and all(len(e)==3 for e in public)
 memory=()
 used=False
 receipts=[]
 scored=0
 for index,event in enumerate(public):
  memory,modified,n=choose(memory,event,index,used,benefit,harm,pack,F62)
  scored+=n
  used=used or modified
  F62._valid_memory(memory,pack)
  if trace:receipts.append(tuple(pack.pack(*r).hex() for r in memory))
 if trace:return memory,tuple(receipts),dict(interventions=int(used),alternatives_scored=scored,latch_extra_bits=1)
 return memory

def training_examples(public,question,pack,F62,F85):
 """Teacher uses only TRAIN future and truth to assign terminal credit."""
 assert len(public)==72 and all(len(e)==3 for e in public)
 memory=()
 labeled=[]
 counts={-1:0,0:0,1:0}
 for i,event in enumerate(public):
  baseline=F62._f60_step(memory,event,pack)
  if i in CHECKPOINTS:
   choices=F62.actions(memory,event,i,pack)
   exact=[c for c in choices if c[3]==baseline]
   assert len(exact)==1
   suffix=public[i+1:]
   baseline_final=F62._finish_fixed(baseline,suffix,pack)
   solved=int(F85.solve_global(baseline_final,{
    "start":question["start"],"ops":question["ops"]},pack)[0]==question["answer"])
   attempted=0
   for c in choices:
    if c[3]==baseline:continue
    if attempted>=MAX_ALT:break
    attempted+=1
    final=F62._finish_fixed(c[3],suffix,pack)
    result=int(F85.solve_global(final,{
     "start":question["start"],"ops":question["ops"]},pack)[0]==question["answer"])
    adv=result-solved
    labeled.append((vector(exact[0][4],c[4]),adv))
    counts[adv]+=1
  memory=baseline
 return labeled,counts

def train_only():
 assert gitblob(P/"prereg.json")==PREREG_SHA
 reg=json.loads((P/"prereg.json").read_text())
 assert reg["stage"]=="FROZEN_PRECODE_SYNTHETIC_TRAIN_THEN_INDEPENDENT_HOLDOUT"
 assert reg["cohorts"]["train"]=={"start":-5801,"stop_exclusive":-5817,"step":-1,"families":[-2,-1],"cases":32}
 F90=loader("f91_frozen_F90",ROOT/"20261016-y-f90"/"temporal_credit.py",F90_BLOB)
 F89=F90.load_checked("f91_F89R",ROOT/"20261016-y-f89r"/"graded_exchange.py",F90.F89R_METHOD_BLOB)
 F88=F89.load_exact("f91_F88",ROOT/"20261016-y-f88"/"frontier.py",F89.F88_BLOB)
 F87=F88.load_exact("f91_F87",ROOT/"20261016-y-f87b"/"bridge_reserve.py",F88.F87B_BLOB)
 F86=F87.load("f91_F86",ROOT/"20261016-y-f86"/"queryblind_retention.py",F87.F86_SHA)
 F85=F86.load_exact("f91_F85",ROOT/"20261016-y-f85"/"global_solver.py",F86.F85_METHOD_BLOB)
 F84=F85.checked_loader("f91_F84",ROOT/"20261016-y-f84"/"forensic_reachability.py",F85.F84_SHA)
 F83=F84.load_f83()
 pack=F83.M.PACK
 F62=F83.M.F62
 examples=[]
 counts={-1:0,0:0,1:0}
 cases=0
 for seed in TRAIN_SEEDS:
  for fam in FAMILIES:
   public,q,_=F83.M.SOURCE.source(seed,fam)
   assert F84.independently_resolve_public(public,q)[0]=={q["answer"]}
   local,labels=training_examples(public,q,pack,F62,F85)
   examples.extend(local)
   for k,v in labels.items():counts[k]+=v
   cases+=1
 assert cases==32 and len(examples)>0
 benefit,harm=fit(examples)
 weights=(*benefit,*harm)
 digest=hashlib.sha256(bytes(w%256 for w in weights)).hexdigest()
 return dict(schema="yggdrasil.f91.conservative-temporal-credit.train.v1",
  stage="F91_TRAIN_ONLY_NO_VALIDATION_OR_GUARD",
  train_cases=cases,examples=len(examples),label_counts={
    "beneficial":counts[1],"harmful":counts[-1],"neutral":counts[0]},
  benefit_weights=list(benefit),harm_weights=list(harm),signed_int8_sha256=digest,
  model_parameter_bytes=24,intervention_latch_bits=1,
  prereg_git_blob=PREREG_SHA,frozen_parent_F90_blob=F90_BLOB,
  validation_accessed=False,guard_accessed=False,protected_science_used=False,
  optimizer_promotion=False)
if __name__=="__main__":
 if sys.argv[1:]!=["--training-negative-synthetic-only"]:
  raise SystemExit("F91 training entrypoint refuses validation, guard and protected original")
 print(json.dumps(train_only(),sort_keys=True))
