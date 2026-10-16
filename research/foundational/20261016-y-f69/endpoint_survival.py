"""F69 learned causal public endpoint-survival memory, SYNTHETIC ONLY.

Offline TRAIN-only binary label: endpoint reappears in any later public
edge. Learned online policy uses only current public edge, currently
retained 12-byte records, and eight frozen int8 predictor weights.
"""
from __future__ import annotations
import hashlib,importlib.util,json,math,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert blob(P/"prereg.json")=="08a5afaa34df9d151c6103abc8cdd5f2ba4116b5"
def load(name,path,sha):
 assert blob(path)==sha,(name,"FROZEN_TRANSITIVE_SOURCE_DRIFT")
 s=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m)
 return m
F62=load("f69_unmodified_frozen_engine",P.parent/"20261015-y-f62"/"source_pilot.py",
 "7ed72deca5584d7c0b6562d74456fa7d4bee6712")
SOURCE=load("f69_unchanged_structural_source",P.parent/"20261016-y-f63c"/"source.py",
 "c04b73306861098eecf55db77b2db486aa918819")
AUDITOR=load("f69_independent_lossless_memory_auditor",P.parent/"20261015-y-f62"/"audit_public.py",
 "383fff0bdd8c8b48fde9538d4e4d768db1c1896f")
PACK=F62.codec()
PARAMS=8
def endpoints(records):
 return {n for a,b,_ in records for n in (a,b)}
def features(records,node,event,index):
 incident=[codes for a,b,codes in records if a==node or b==node]
 codes={c for seq in incident for c in seq}
 return (
  min(len(incident),12)/12,
  sum(len(path)<=2 for path in incident)/12,
  sum(len(path)>=2 for path in incident)/12,
  len(codes)/8,
  int(node in (event[0],event[2])),
  len(records)/12,
  max((len(path) for path in incident),default=0)/6,
  index/71)
def sigmoid(z):
 if z>=0:
  e=math.exp(-min(z,40));return 1/(1+e)
 e=math.exp(max(z,-40));return e/(1+e)
def candidate_score(records,event,index,weights):
 return sum(sigmoid(sum((w/32)*x for w,x in zip(weights,features(records,n,event,index))))
            for n in endpoints(records))
def online(public,weights,trace=False,predictive=True):
 assert len(weights)==PARAMS and all(type(w) is int and -127<=w<=127 for w in weights)
 assert len(public)==72 and all(len(e)==3 for e in public)
 memory=()
 receipts=[]
 stats=dict(proactive_deviations=0,proactive_early_deviations=0,
            frozen_F60_default_steps=0,available_alternatives=0)
 for i,event in enumerate(public):
  baseline=F62._f60_step(memory,event,PACK)
  chosen=baseline
  if predictive:
   best=None
   for j,(_action,_old,_drop,after,_features) in enumerate(F62.actions(memory,event,i,PACK)):
    if after==baseline:continue
    stats["available_alternatives"]+=1
    value=candidate_score(after,event,i,weights)-candidate_score(baseline,event,i,weights)
    key=(value,-j)
    if best is None or key>best[0]:
     best=(key,after)
   if best is not None and best[0][0]>0:
    chosen=best[1]
  if chosen!=baseline:
   stats["proactive_deviations"]+=1
   stats["proactive_early_deviations"]+=int(i<48)
  else:stats["frozen_F60_default_steps"]+=1
  memory=chosen
  F62._valid_memory(memory,PACK)
  if trace:receipts.append(tuple(PACK.pack(*record).hex() for record in memory))
 return (memory,tuple(receipts),stats) if trace else memory
def train_synthetic(publics):
 # Fixed chronological SGD for binary endpoint reappearance.
 instances=[]
 pos=neg=0
 for public in publics:
  memory=()
  for i,event in enumerate(public):
   memory=F62._f60_step(memory,event,PACK)
   future={node for a,_role,b in public[i+1:] for node in (a,b)}
   for node in sorted(endpoints(memory)):
    label=int(node in future)
    instances.append((features(memory,node,event,i),label))
    pos+=label;neg+=1-label
 assert pos>0 and neg>0 and instances,"UNBALANCED_ENDPOINT_SURVIVAL_LABELS"
 w=[0.0]*PARAMS
 for _ in range(3):
  for x,label in instances:
   pred=sigmoid(sum(a*f for a,f in zip(w,x)))
   for j,value in enumerate(x):
    w[j]+=.02*(label-pred)*value
 quant=tuple(max(-127,min(127,round(v*32))) for v in w)
 return quant,dict(positive_endpoint_labels=pos,negative_endpoint_labels=neg,
                   examples=len(instances),weights=list(quant))
def synthetic_qualification():
 train=[]
 for i in range(8):
  public,q,_=SOURCE.source(-3201-i,(-2,-1)[i%2])
  train.append(public)
 weights,stats=train_synthetic(train)
 rows=[]
 for i in range(8):
  seed=-3211-i;family=(-2,-1)[i%2]
  public,q,meta=SOURCE.source(seed,family)
  model,trace,activity=online(public,weights,True)
  control,ctrl_trace,_=online(public,weights,True,False)
  evidence=AUDITOR.verify(public,q,trace)
  assert evidence["prefixes"]==72 and evidence["max_payload_bytes"]<=144
  assert AUDITOR.verify(public,q,ctrl_trace)["prefixes"]==72
  assert control==F62.controls()[0].online_fixed(public)
  rows.append(dict(seed=seed,family=family,question_type=meta["question_type"],
    proactive_changes=activity["proactive_deviations"],
    early_proactive_changes=activity["proactive_early_deviations"],
    learned_correct=int(PACK.solve(model,q)==q["answer"]),
    frozen_F60_correct=int(PACK.solve(control,q)==q["answer"])))
 early=sum(r["early_proactive_changes"] for r in rows)
 result=dict(schema="yggdrasil.f69.endpoint-survival.synthetic-qualification.v1",
  stage="UNREGISTERED_SYNTHETIC_TRAIN_AND_GUARD",
  train_cases=len(train),guard_cases=len(rows),
  fit_info=stats,early_prelink_deviations=early,
  trained_synthetic_guard_correct=sum(r["learned_correct"] for r in rows),
  frozen_F60_guard_correct=sum(r["frozen_F60_correct"] for r in rows),
  independent_causal_prefix_pass=True,
  source_prequalification_pass=early>0,
  FIT_train_used=False,FIT_validation_used=False,
  DIAG_used=False,original_used=False,F3=False,policy_promotion=False,
  guard_rows=rows)
 print(json.dumps(result,sort_keys=True))
 if not result["source_prequalification_pass"]:
  raise AssertionError("F69_LEARNED_MEMORY_NOT_PROACTIVE")
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 synthetic_qualification()
