"""F93B: learn six-role public grammar from TRAIN question operators only.

The causal policy's inputs are public events, native memory, a frozen
role grammar, codec and native F62 actions. It has no task/future/answer
input; the training-only source reader is not imported by online().
"""
from __future__ import annotations
import hashlib,importlib.util,json,sys
from collections import Counter
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parent
PRE="a9e0c04027e6488220c068eb59e580a1295c736b"
F92_BLOB="7fdaf5d24866c347275c2ffa3aec7dfeaed6ac5b"
MAX_STATES=512

def blob(path):
 data=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
def load(name,path,sha):
 assert blob(path)==sha,("F93B_HISTORIC_SOURCE_DRIFT",name)
 spec=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
 return m
def roles(question):
 return tuple(2*role+int(direction==-1) for role,direction in question["ops"])
def fit(questions):
 counts=Counter(roles(q) for q in questions if len(q["ops"])==6)
 assert counts and all(len(k)==6 and all(0<=v<=7 for v in k) for k in counts)
 ordered=sorted(counts,key=lambda pat:(-counts[pat],pat))
 return tuple(ordered[:3]),{"six_step_train_questions":sum(counts.values()),
       "unique_patterns":len(counts),"counts":[{"pattern":list(p),"count":counts[p]} for p in ordered[:3]]}
def coverage(records,grammar,pack,cap=MAX_STATES):
 """Exact full-native-record (forward or mirrored) grammar paths."""
 assert len(records)<=12 and all(len(r[2]) in range(1,7) for r in records)
 edges=set()
 for rec in records:
  edges.add((rec[0],rec[1],tuple(rec[2])))
  reverse=pack.mirrored(rec)
  edges.add((reverse[0],reverse[1],tuple(reverse[2])))
 outgoing={}
 for a,b,seq in sorted(edges):
  outgoing.setdefault(a,[]).append((b,seq))
 found=set()
 states_seen=0
 for gi,pattern in enumerate(grammar):
  if len(pattern)!=6:return None
  for start in outgoing:
   frontier={(start,0)}
   visited=set(frontier)
   while frontier:
    nxt=set()
    for node,progress in frontier:
     if progress==6:
      found.add((gi,start,node));continue
     for end,codes in outgoing.get(node,()):
      if progress+len(codes)>6 or codes!=pattern[progress:progress+len(codes)]:
       continue
      state=(end,progress+len(codes))
      if state not in visited:
       visited.add(state);nxt.add(state)
       states_seen+=1
       if states_seen>cap:return None
    frontier=nxt
 return frozenset(found)
def decision(before,event,index,used,grammar,pack,F62):
 assert isinstance(used,bool) and 0<len(grammar)<=3
 baseline=F62._f60_step(before,event,pack)
 if used or index<36:
  return baseline,False,0,0
 options=F62.actions(before,event,index,pack)
 assert sum(x[3]==baseline for x in options)==1
 original=coverage(baseline,grammar,pack)
 if original is None:return baseline,False,0,1
 choices=[];examined=0;capped=0
 required=min(10,max(0,len(baseline)-1))
 for j,action in enumerate(options):
  after=action[3]
  if after==baseline:continue
  examined+=1
  shared=sum(r in baseline for r in after)
  if shared<required:continue
  candidate=coverage(after,grammar,pack)
  if candidate is None:
   capped+=1;continue
  gain=len(candidate)-len(original)
  if gain>0:
   choices.append((gain,shared,-j,after))
 if not choices:return baseline,False,examined,capped
 chosen=max(choices)[3]
 assert chosen in {x[3] for x in options}
 F62._valid_memory(chosen,pack)
 return chosen,True,examined,capped
def online(public,grammar,pack,F62,trace=False):
 assert len(public)==72 and all(len(e)==3 for e in public)
 memory=();used=False;traces=[];scored=0;caps=0
 for index,event in enumerate(public):
  memory,change,n,k=decision(memory,event,index,used,grammar,pack,F62)
  used=used or change;scored+=n;caps+=k
  F62._valid_memory(memory,pack)
  if trace:traces.append(tuple(pack.pack(*r).hex() for r in memory))
 if trace:return memory,tuple(traces),{"interventions":int(used),
      "scored_candidates":scored,"cap_events":caps,"latch_bits":1}
 return memory
def training_only():
 assert blob(P/"prereg.json")==PRE
 pre=json.loads((P/"prereg.json").read_text())
 assert pre["stage"]=="FROZEN_PRECODE_NEW_NEGATIVE_SYNTHETIC_TRAIN_VALIDATION_GUARD"
 assert pre["cohorts"]["train"]=={"start":-6001,"end_exclusive":-6017,
                                 "step":-1,"families":[-2,-1],"cases":32}
 F92=load("f93b_frozen_F92",R/"20261016-y-f92"/"dense_path_credit.py",F92_BLOB)
 F91=F92.load("f93b_frozen_F91",R/"20261016-y-f91"/"conservative_credit.py",F92.F91_BLOB)
 F90=F91.loader("f93b_frozen_F90",R/"20261016-y-f90"/"temporal_credit.py",F91.F90_BLOB)
 F89=F90.load_checked("f93b_frozen_F89",R/"20261016-y-f89r"/"graded_exchange.py",F90.F89R_METHOD_BLOB)
 F88=F89.load_exact("f93b_frozen_F88",R/"20261016-y-f88"/"frontier.py",F89.F88_BLOB)
 F87=F88.load_exact("f93b_frozen_F87",R/"20261016-y-f87b"/"bridge_reserve.py",F88.F87B_BLOB)
 F86=F87.load("f93b_frozen_F86",R/"20261016-y-f86"/"queryblind_retention.py",F87.F86_SHA)
 F85=F86.load_exact("f93b_frozen_F85",R/"20261016-y-f85"/"global_solver.py",F86.F85_METHOD_BLOB)
 F84=F85.checked_loader("f93b_frozen_F84",R/"20261016-y-f84"/"forensic_reachability.py",F85.F84_SHA)
 F83=F84.load_f83()
 questions=[]
 for seed in range(-6001,-6017,-1):
  for family in (-2,-1):
   public,q,_=F83.M.SOURCE.source(seed,family)
   assert F84.independently_resolve_public(public,q)[0]=={q["answer"]}
   questions.append(q)
 assert len(questions)==32
 grammar,stats=fit(questions)
 raw=json.dumps([list(x) for x in grammar],separators=(",",":")).encode()
 return {"schema":"yggdrasil.f93b.frozen-role-prior.train.v1",
  "stage":"TRAIN_ONLY_SEPARATE_VALIDATION_GUARD",
  "train_cases":len(questions),"grammar":[list(x) for x in grammar],
  "grammar_sha256":hashlib.sha256(raw).hexdigest(),
  "grammar_extra_bytes":sum(len(x) for x in grammar),"latch_extra_bits":1,
  "training_labels_use_only_question_ops":True,
  "grammar_summary":stats,"validation_accessed":False,"guard_accessed":False,
  "protected_sources_accessed":False,"scientific_acceptance":False}
if __name__=="__main__":
 if sys.argv[1:]!=["--train-only"]:
  raise SystemExit("F93B refuses protected and holdout source during fitting")
 print(json.dumps(training_only(),sort_keys=True))
