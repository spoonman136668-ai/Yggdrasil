#!/usr/bin/env python3
"""F95: source-native selective policy learned from TRAIN-only terminal risk.

The retrospective teacher may inspect TRAIN future public events and answer.
The online selector only sees prior retained native records, one new PUBLIC
edge, frozen bucket policy, index, and unchanged F62 actions/codec.
"""
from __future__ import annotations
import hashlib,importlib.util,json,sys
from collections import Counter,defaultdict
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parent
PREREG_SHA="b03be01fe77f09663f33673ff2095e99f220f16d"
F94_SHA="0284a3ed1cd5f263dc4ad7cf3f3f21969bb665ad"
TRAIN=range(-6101,-6117,-1)
FAMILIES=(-2,-1)

def gitblob(path):
 raw=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
def load(name,path,sha):
 assert gitblob(path)==sha,("F95_HISTORICAL_SOURCE_DRIFT",name)
 spec=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
 return m
def _overlap(baseline,after):
 return sum(r in baseline for r in after)
def eligible_overlap(baseline,after):
 return _overlap(baseline,after)>=min(10,max(0,len(baseline)-1))
def public_key(index,event,action,baseline):
 """Six categorical PUBLIC and native-action features; no query/answer."""
 name,old,drop,after,_=action
 assert 12<=index<48 and len(event)==3
 assert name in ("append","merge")
 assert 0<=event[1]<=3
 total=lambda mem:sum(len(r[2]) for r in mem)
 newlong=any(len(r[2])>=4 and r not in baseline for r in after)
 overlap=_overlap(baseline,after)
 return (int(index>=24),int(event[1]),int(name=="merge"),
         int(total(after)>total(baseline)),int(newlong),
         int(overlap>=len(baseline)-1))
def key_text(key):
 assert len(key)==6 and all(type(i) is int for i in key)
 return ":".join(str(x) for x in key)
def choose(memory,event,index,used,policy,codec,F62):
 assert type(used) is bool
 assert isinstance(policy,dict) and all(type(k) is str and type(v) is int and v>=1 for k,v in policy.items())
 baseline=F62._f60_step(memory,event,codec)
 if used or index<12 or index>=48:
  return baseline,False,0
 choices=F62.actions(memory,event,index,codec)
 assert sum(x[3]==baseline for x in choices)==1,"F95_BASELINE_NOT_NATIVE"
 best=None
 examined=0
 for i,act in enumerate(choices):
  after=act[3]
  if after==baseline:continue
  examined+=1
  if not eligible_overlap(baseline,after):continue
  count=policy.get(key_text(public_key(index,event,act,baseline)),0)
  if count<1:continue
  score=(count,_overlap(baseline,after),-i)
  if best is None or score>best[0]:
   best=(score,after)
 if best is None:return baseline,False,examined
 result=best[1]
 assert result in {x[3] for x in choices}
 F62._valid_memory(result,codec)
 return result,True,examined
def online(public,policy,codec,F62,trace=False):
 assert len(public)==72 and all(len(x)==3 for x in public)
 memory=();used=False;receipts=[];candidates=0
 for index,event in enumerate(public):
  memory,change,n=choose(memory,event,index,used,policy,codec,F62)
  used=used or change
  candidates+=n
  F62._valid_memory(memory,codec)
  if trace:receipts.append(tuple(codec.pack(*r).hex() for r in memory))
 if trace:
  return memory,tuple(receipts),dict(native_interventions=int(used),
         legal_alternatives_seen=candidates,latch_bits=1)
 return memory

def teacher_case(public,question,codec,F62,F85):
 """Offline, TRAIN-only exhaustive early/middle one-deviation labels."""
 assert len(public)==72
 memory=()
 qonly={"start":question["start"],"ops":question["ops"]}
 fixed=F62._finish_fixed((),public,codec)
 correct=F85.solve_global(fixed,qonly,codec)[0]==question["answer"]
 tally=Counter()
 examined=0
 for index,event in enumerate(public):
  baseline=F62._f60_step(memory,event,codec)
  if 12<=index<48:
   options=F62.actions(memory,event,index,codec)
   assert sum(x[3]==baseline for x in options)==1
   for act in options:
    after=act[3]
    if after==baseline or not eligible_overlap(baseline,after):continue
    terminal=F62._finish_fixed(after,public[index+1:],codec)
    result,diags=F85.solve_global(terminal,qonly,codec)
    assert not diags["resource_cap_triggered"]
    assert result is None or result==question["answer"]
    benef=int(not correct and result==question["answer"])
    harmful=int(correct and result!=question["answer"])
    assert not (benef and harmful)
    key=key_text(public_key(index,event,act,baseline))
    tally[(key,"total")]+=1
    tally[(key,"benefit")]+=benef
    tally[(key,"harm")]+=harmful
    examined+=1
  memory=baseline
 assert memory==fixed
 return tally,examined,int(correct)
def train_only():
 assert gitblob(P/"prereg.json")==PREREG_SHA,"F95_PREREG_CHANGED"
 pre=json.loads((P/"prereg.json").read_text())
 assert pre["stage"]=="FROZEN_PRECODE_DISJOINT_TRAIN_VALIDATION_GUARD"
 assert pre["cohorts"]["train"]=={"start":-6101,"stop_exclusive":-6117,
     "step":-1,"families":[-2,-1],"cases":32}
 F94=load("f95_frozen_F94",ROOT/"20261016-y-f94"/"single_deviation_feasibility.py",F94_SHA)
 F93=F94.load_exact("f95_frozen_F93",ROOT/"20261016-y-f93b"/"role_grammar.py",F94.F93_BLOB)
 F92=F93.load("f95_frozen_F92",ROOT/"20261016-y-f92"/"dense_path_credit.py",F93.F92_BLOB)
 F91=F92.load("f95_frozen_F91",ROOT/"20261016-y-f91"/"conservative_credit.py",F92.F91_BLOB)
 F90=F91.loader("f95_frozen_F90",ROOT/"20261016-y-f90"/"temporal_credit.py",F91.F90_BLOB)
 F89=F90.load_checked("f95_frozen_F89",ROOT/"20261016-y-f89r"/"graded_exchange.py",F90.F89R_METHOD_BLOB)
 F88=F89.load_exact("f95_frozen_F88",ROOT/"20261016-y-f88"/"frontier.py",F89.F88_BLOB)
 F87=F88.load_exact("f95_frozen_F87",ROOT/"20261016-y-f87b"/"bridge_reserve.py",F88.F87B_BLOB)
 F86=F87.load("f95_frozen_F86",ROOT/"20261016-y-f86"/"queryblind_retention.py",F87.F86_SHA)
 F85=F86.load_exact("f95_frozen_F85",ROOT/"20261016-y-f85"/"global_solver.py",F86.F85_METHOD_BLOB)
 F84=F85.checked_loader("f95_frozen_F84",ROOT/"20261016-y-f84"/"forensic_reachability.py",F85.F84_SHA)
 F83=F84.load_f83()
 codec=F83.M.PACK;F62=F83.M.F62
 totals=Counter();cases=0;attempts=0;f60_correct=0
 for seed in TRAIN:
  for family in FAMILIES:
   public,q,_=F83.M.SOURCE.source(seed,family)
   assert F84.independently_resolve_public(public,q)[0]==frozenset({q["answer"]})
   stats,seen,right=teacher_case(public,q,codec,F62,F85)
   totals.update(stats);attempts+=seen;f60_correct+=right;cases+=1
 assert cases==32 and attempts>0
 keys=sorted({name for name,label in totals})
 allowed={key:totals[(key,"benefit")] for key in keys
   if totals[(key,"total")]>=12 and totals[(key,"benefit")]>=1
   and totals[(key,"harm")]==0}
 canonical=json.dumps(allowed,sort_keys=True,separators=(",",":")).encode()
 return dict(schema="yggdrasil.f95.train-risk-table.v1",
   stage="TRAIN_ONLY_NO_VALIDATION_OR_GUARD",
   train_cases=cases,train_F60_correct=f60_correct,
   exact_native_training_alternatives=attempts,
   distinct_public_buckets=len(keys),
   total_teacher_beneficial=sum(totals[(key,"benefit")] for key in keys),
   total_teacher_harmful=sum(totals[(key,"harm")] for key in keys),
   eligible_buckets=len(allowed),frozen_policy=allowed,
   policy_sha256=hashlib.sha256(canonical).hexdigest(),
   policy_json_bytes=len(canonical),latch_extra_bits=1,
   no_validation_use=True,no_guard_use=True,no_protected_source=True,
   no_optimizer_promotion=True)
if __name__=="__main__":
 if sys.argv[1:]!=["--train-negative-synthetic-only"]:
  raise SystemExit("F95 training source cannot access validation, guard, or protected originals")
 print(json.dumps(train_only(),sort_keys=True))
