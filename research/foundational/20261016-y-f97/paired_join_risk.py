"""F97: matched-pair TRAIN-only native action benefit/risk; query-blind online.

Trainer can see the TRAIN-only later public stream and truth. Online has only
current 3-field public arrival, retained native memory and frozen lookup.
"""
from __future__ import annotations
import hashlib,importlib.util,json,collections,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parent
PREREG_BLOB="8e8450b07681ba4899e18d446e45f2007682a147"
F96_BLOB="2cf14367527c9790661af65a84d15cbe11132bc7"
TRAIN_SEEDS=range(-6301,-6317,-1)
FAMILIES=(-2,-1)
def gitblob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def load(name,path,sha):
 assert gitblob(path)==sha,("F97_FROZEN_SOURCE_DRIFT",name)
 s=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m)
 return m
def dependencies():
 F96=load("f97_exact_f96",ROOT/"20261016-y-f96"/"paired_order_probe.py",F96_BLOB)
 F95=F96.load_exact("f97_exact_f95",ROOT/"20261016-y-f95"/"risk_lookup.py",F96.F95_BLOB)
 F94=F95.load("f97_exact_f94",ROOT/"20261016-y-f94"/"single_deviation_feasibility.py",F95.F94_SHA)
 F93=F94.load_exact("f97_exact_f93",ROOT/"20261016-y-f93b"/"role_grammar.py",F94.F93_BLOB)
 F92=F93.load("f97_exact_f92",ROOT/"20261016-y-f92"/"dense_path_credit.py",F93.F92_BLOB)
 F91=F92.load("f97_exact_f91",ROOT/"20261016-y-f91"/"conservative_credit.py",F92.F91_BLOB)
 F90=F91.loader("f97_exact_f90",ROOT/"20261016-y-f90"/"temporal_credit.py",F91.F90_BLOB)
 F89=F90.load_checked("f97_exact_f89",ROOT/"20261016-y-f89r"/"graded_exchange.py",F90.F89R_METHOD_BLOB)
 F88=F89.load_exact("f97_exact_f88",ROOT/"20261016-y-f88"/"frontier.py",F89.F88_BLOB)
 F87=F88.load_exact("f97_exact_f87",ROOT/"20261016-y-f87b"/"bridge_reserve.py",F88.F87B_BLOB)
 F86=F87.load("f97_exact_f86",ROOT/"20261016-y-f86"/"queryblind_retention.py",F87.F86_SHA)
 F85=F86.load_exact("f97_exact_f85",ROOT/"20261016-y-f85"/"global_solver.py",F86.F85_METHOD_BLOB)
 F84=F85.checked_loader("f97_exact_f84",ROOT/"20261016-y-f84"/"forensic_reachability.py",F85.F84_SHA)
 F83=F84.load_f83()
 return F96,F83,F84,F85,F83.M.F62,F83.M.PACK

def category(before,event,index,action):
 """Only retained native memory, index, public event and native action."""
 assert 0<=index<72 and len(event)==3
 a,_role,b=event
 touch=int(any(a in (u,v) or b in (u,v) for u,v,_ in before))
 join=int(any(v==a or u==b for u,v,_ in before))
 return (index//24,touch,join,int(action[0]=="merge"),int(action[2]>=0))

def decide(before,event,index,used,approved,pack,F62):
 baseline=F62._f60_step(before,event,pack)
 options=F62.actions(before,event,index,pack)
 assert sum(op[3]==baseline for op in options)==1
 if used or index>=48:return baseline,False,0
 ranked=[]
 num=0
 threshold=min(10,max(0,len(baseline)-1))
 for j,opt in enumerate(options):
  if opt[3]==baseline:continue
  num+=1
  k=category(before,event,index,opt)
  grant=approved.get(k)
  if grant is None:continue
  if sum(rec in baseline for rec in opt[3])<threshold:continue
  ranked.append((grant[0],grant[1],-j,opt[3]))
 if ranked:
  state=max(ranked)[3]
  assert state in {op[3] for op in options}
  F62._valid_memory(state,pack)
  return state,True,num
 return baseline,False,num

def online(public,approved,pack,F62,trace=False):
 assert len(public)==72 and all(len(e)==3 for e in public)
 memory=();used=False;receipts=[];alternatives=0
 for i,event in enumerate(public):
  memory,change,num=decide(memory,event,i,used,approved,pack,F62)
  used=used or change;alternatives+=num
  F62._valid_memory(memory,pack)
  if trace:receipts.append(tuple(pack.pack(*rec).hex() for rec in memory))
 if trace:return memory,tuple(receipts),dict(interventions=int(used),alternatives=alternatives,latch_bits=1)
 return memory

def train_case(public,q,pack,F62,F85):
 """TRAIN only: frozen F60 suffix, same true answer for counterfactual."""
 memory=();stats=collections.defaultdict(lambda:[0,0,0])
 for i,event in enumerate(public):
  baseline=F62._f60_step(memory,event,pack)
  if i<48:
   choices=F62.actions(memory,event,i,pack)
   assert sum(x[3]==baseline for x in choices)==1
   suffix=public[i+1:]
   control=F62._finish_fixed(baseline,suffix,pack)
   prediction,cost=F85.solve_global(control,{"start":q["start"],"ops":q["ops"]},pack)
   assert not cost["resource_cap_triggered"]
   correct=prediction==q["answer"]
   attempted=0
   for option in choices:
    if option[3]==baseline:continue
    if attempted>=8:break
    attempted+=1
    after=F62._finish_fixed(option[3],suffix,pack)
    guess,receipt=F85.solve_global(after,{"start":q["start"],"ops":q["ops"]},pack)
    assert not receipt["resource_cap_triggered"]
    assert guess is None or guess==q["answer"]
    delta=int(guess==q["answer"])-int(correct)
    key=category(memory,event,i,option)
    bin=0 if delta==1 else (1 if delta==-1 else 2)
    stats[key][bin]+=1
  memory=baseline
 return stats

def fit(rows):
 pooled=collections.defaultdict(lambda:[0,0,0])
 for local in rows:
  for k,counts in local.items():
   for i,value in enumerate(counts):pooled[k][i]+=value
 approved={k:(v[0],sum(v)) for k,v in pooled.items()
           if sum(v)>=8 and v[0]>=2 and v[1]==0}
 return approved,dict(
  categories_seen=len(pooled),eligible_categories=len(approved),
  beneficial_labels=sum(v[0] for v in pooled.values()),
  harmful_labels=sum(v[1] for v in pooled.values()),
  neutral_labels=sum(v[2] for v in pooled.values()),
  total_examples=sum(sum(v) for v in pooled.values()))

def frozen_rows(approved):
 return [dict(key=list(k),beneficial=v[0],total=v[1])
         for k,v in sorted(approved.items())]

def train():
 assert gitblob(P/"prereg.json")==PREREG_BLOB
 reg=json.loads((P/"prereg.json").read_text())
 assert reg["stage"]=="FROZEN_PRECODE_PAIRED_TRAIN_THEN_DISJOINT_HOLDOUT"
 assert reg["cohorts"]["train"]==dict(seeds_start=-6301,seeds_stop_exclusive=-6317,step=-1,families=[-2,-1],graphs=32,order_episodes=64)
 F96,F83,F84,F85,F62,pack=dependencies()
 data=[];paired=0
 for seed in TRAIN_SEEDS:
  for family in FAMILIES:
   observed,q,meta=F83.M.SOURCE.source(seed,family)
   original,rotated=F96.matched_orders(observed,meta["arrival_regime"],F83.M.SOURCE)
   assert F84.independently_resolve_public(original,q)[0]=={q["answer"]}
   assert F84.independently_resolve_public(rotated,q)[0]=={q["answer"]}
   for public in (original,rotated):
    data.append(train_case(public,q,pack,F62,F85))
   paired+=1
 assert paired==32 and len(data)==64
 approved,summary=fit(data)
 rows=frozen_rows(approved)
 payload=json.dumps(rows,sort_keys=True,separators=(",",":")).encode()
 return dict(schema="yggdrasil.f97.paired-native-join-risk.train.v1",
  stage="TRAIN_ONLY_NO_VALIDATION_OR_GUARD",paired_graphs=paired,
  paired_order_episodes=len(data),stats=summary,
  approved_categories=rows,approved_policy_sha256=hashlib.sha256(payload).hexdigest(),
  policy_parameter_bytes=len(payload),extra_latch_bits=1,
  no_holdout_used=True,no_protected_source=True,no_controller_or_optimizer_mutation=True)
if __name__=="__main__":
 assert sys.argv[1:]==["--paired-train-only"]
 print(json.dumps(train(),sort_keys=True))
