"""F92: dense delayed path credit; TRAIN-only oracle and causal native policy."""
from __future__ import annotations
import hashlib,importlib.util,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
PREREG="c56d1e1c2221ab7311ffb093921ee21b7e6f0fda"
F91_BLOB="a3e9ccdbd623d996d56355bb6b9e838fb59fc3b2"
CHECKPOINTS=(11,23,35,47,59,71)
def blob(p):
 b=p.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def load(name,p,sha):
 assert blob(p)==sha
 spec=importlib.util.spec_from_file_location(name,p)
 m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
 return m
def prefix_hops(records,q,pack):
 codes=tuple(2*role+int(direction==-1) for role,direction in q["ops"])
 oriented={v for rec in records for v in (rec,pack.mirrored(rec))}
 states={0:{q["start"]}}
 for k in range(len(codes)):
  for node in states.get(k,()):
   for a,b,seq in oriented:
    if a==node and k+len(seq)<=len(codes) and tuple(seq)==codes[k:k+len(seq)]:
     states.setdefault(k+len(seq),set()).add(b)
 return max(states)
def examples(public,q,pack,F62,F85,F91):
 memory=();out=[];counts={-1:0,0:0,1:0}
 assert len(public)==72
 for i,event in enumerate(public):
  baseline=F62._f60_step(memory,event,pack)
  if i in CHECKPOINTS:
   legal=F62.actions(memory,event,i,pack)
   equal=[x for x in legal if x[3]==baseline]
   assert len(equal)==1
   suffix=public[i+1:]
   def reward(after):
    final=F62._finish_fixed(after,suffix,pack)
    prefix=prefix_hops(final,q,pack)/len(q["ops"])
    guess,_=F85.solve_global(final,{"start":q["start"],"ops":q["ops"]},pack)
    return prefix+2.0*int(guess==q["answer"])
   control=reward(baseline);n=0
   for action in legal:
    if action[3]==baseline:continue
    if n==8:break
    n+=1
    delta=reward(action[3])-control
    label=int(delta>1e-10)-int(delta< -1e-10)
    out.append((F91.vector(equal[0][4],action[4]),label))
    counts[label]+=1
  memory=baseline
 return out,counts
def choose(before,event,index,used,benefit,harm,pack,F62,F91):
 assert type(used) is bool and len(benefit)==len(harm)==12
 baseline=F62._f60_step(before,event,pack)
 actions=F62.actions(before,event,index,pack)
 exact=[x for x in actions if x[3]==baseline]
 assert len(exact)==1
 if used or index<24:return baseline,False,0
 scored=[];n=0
 required=min(10,max(0,len(baseline)-1))
 for j,action in enumerate(actions):
  if action[3]==baseline:continue
  n+=1
  if sum(r in baseline for r in action[3])<required:continue
  x=F91.vector(exact[0][4],action[4])
  good=F91.score(benefit,x);bad=F91.score(harm,x)
  if good>=0.68 and bad<=0.18 and good-bad>=0.50:
   scored.append((good-bad,good,-j,action[3]))
 if scored:
  after=max(scored)[3]
  F62._valid_memory(after,pack)
  return after,True,n
 return baseline,False,n
def online(public,benefit,harm,pack,F62,F91,trace=False):
 assert len(public)==72 and all(len(e)==3 for e in public)
 memory=();used=False;snaps=[];candidate_count=0
 for i,event in enumerate(public):
  memory,change,n=choose(memory,event,i,used,benefit,harm,pack,F62,F91)
  used=used or change;candidate_count+=n
  F62._valid_memory(memory,pack)
  if trace:snaps.append(tuple(pack.pack(*r).hex() for r in memory))
 if trace:return memory,tuple(snaps),{"interventions":int(used),"scored":candidate_count,"latch_bits":1}
 return memory
def train():
 assert blob(HERE/"prereg.json")==PREREG
 plan=json.loads((HERE/"prereg.json").read_text())
 assert plan["stage"]=="FROZEN_PRECODE_SYNTHETIC_TRAIN_WITH_SEALED_VALIDATION_GUARD"
 assert plan["cohorts"]["train"]["start"]==-5901
 F91=load("f92_exact_f91",ROOT/"20261016-y-f91"/"conservative_credit.py",F91_BLOB)
 F90=F91.loader("f92_exact_f90",ROOT/"20261016-y-f90"/"temporal_credit.py",F91.F90_BLOB)
 F89=F90.load_checked("f92_exact_f89",ROOT/"20261016-y-f89r"/"graded_exchange.py",F90.F89R_METHOD_BLOB)
 F88=F89.load_exact("f92_exact_f88",ROOT/"20261016-y-f88"/"frontier.py",F89.F88_BLOB)
 F87=F88.load_exact("f92_exact_f87",ROOT/"20261016-y-f87b"/"bridge_reserve.py",F88.F87B_BLOB)
 F86=F87.load("f92_exact_f86",ROOT/"20261016-y-f86"/"queryblind_retention.py",F87.F86_SHA)
 F85=F86.load_exact("f92_exact_f85",ROOT/"20261016-y-f85"/"global_solver.py",F86.F85_METHOD_BLOB)
 F84=F85.checked_loader("f92_exact_f84",ROOT/"20261016-y-f84"/"forensic_reachability.py",F85.F84_SHA)
 F83=F84.load_f83();pack=F83.M.PACK;F62=F83.M.F62
 data=[];counts={-1:0,0:0,1:0}
 for seed in range(-5901,-5917,-1):
  for family in (-2,-1):
   public,q,_=F83.M.SOURCE.source(seed,family)
   assert F84.independently_resolve_public(public,q)[0]=={q["answer"]}
   obs,tally=examples(public,q,pack,F62,F85,F91);data+=obs
   for k in counts:counts[k]+=tally[k]
 assert data
 b,h=F91.fit(data)
 digest=hashlib.sha256(bytes(v%256 for v in b+h)).hexdigest()
 return {"stage":"TRAIN_ONLY_NO_HOLDOUT","train_cases":32,"examples":len(data),
 "labels":{"beneficial":counts[1],"harmful":counts[-1],"neutral":counts[0]},
 "benefit":list(b),"harm":list(h),"weights_sha256":digest,
 "extra_model_bytes":24,"extra_latch_bits":1,
 "validation_used":False,"guard_used":False,"protected_used":False}
if __name__=="__main__":
 assert sys.argv[1:]==["--train-only"]
 print(json.dumps(train(),sort_keys=True))
