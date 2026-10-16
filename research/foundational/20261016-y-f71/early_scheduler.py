"""F71 early public-memory intervention learner — SYNTHETIC ONLY.

A signed counterfactual teacher can use future synthetic TRAIN questions
offline. The query-blind online scheduler sees only current public edges,
previous <=12 exact lossless records, and frozen int8 weights. No index as
a feature, no F70B exposed example or rescue indices, no protected FIT.
"""
from __future__ import annotations
import hashlib,importlib.util,json,math,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert blob(P/"prereg.json")=="b3e0f8c32ad639079fcf6ab85fd8b17f6285acdc"
def load(name,path,expected):
 assert blob(path)==expected,(name,"FROZEN_SOURCE_DRIFT")
 sp=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(sp);sys.modules[name]=m;sp.loader.exec_module(m)
 return m
SOURCE=load("f71_unmodified_public_source",P.parent/"20261016-y-f63c"/"source.py",
 "c04b73306861098eecf55db77b2db486aa918819")
F62=load("f71_exact_native_memory_candidates",P.parent/"20261015-y-f62"/"source_pilot.py",
 "7ed72deca5584d7c0b6562d74456fa7d4bee6712")
AUDIT=load("f71_independent_full_prefix_memory_auditor",P.parent/"20261015-y-f62"/"audit_public.py",
 "383fff0bdd8c8b48fde9538d4e4d768db1c1896f")
PACK=F62.codec()
PARAMS=12
def stats(records):
 paths=[len(code) for _,_,code in records]
 nodes={n for a,b,_ in records for n in (a,b)}
 codes={c//2 for _,_,role in records for c in role}
 deg={}
 for a,b,_ in records:
  deg[a]=deg.get(a,0)+1;deg[b]=deg.get(b,0)+1
 return dict(total=sum(paths),maximum=max(paths,default=0),
   endpoints=nodes,composition=sum(x>=2 for x in paths),
   branching=sum(v>1 for v in deg.values()),roles=len(codes))
def features(before,baseline,after,event,action,drop):
 base=stats(baseline);alt=stats(after)
 already={n for a,b,_ in before for n in (a,b)}
 a,_r,b=event
 return (1.0,
  (alt["total"]-base["total"])/72,
  (alt["maximum"]-base["maximum"])/6,
  (len(alt["endpoints"])-len(base["endpoints"]))/24,
  (alt["composition"]-base["composition"])/12,
  (int(a in alt["endpoints"])+int(b in alt["endpoints"])
   -int(a in base["endpoints"])-int(b in base["endpoints"]))/2,
  (int(a in already)+int(b in already))/2,
  len(before)/12,
  int(action=="merge"),
  int(drop>=0),
  (alt["branching"]-base["branching"])/12,
  (alt["roles"]-base["roles"])/8)
def sigmoid_sign(z):
 return math.tanh(max(-20,min(20,z)))
def native_alternatives(before,event,i):
 baseline=F62._f60_step(before,event,PACK)
 seen=set();out=[]
 for act,_old,drop,after,_f in F62.actions(before,event,i,PACK):
  if after==baseline or after in seen:continue
  seen.add(after)
  out.append((act,drop,after,features(before,baseline,after,event,act,drop)))
 return baseline,tuple(out)
def online(public,weights,trace=False,interventions_enabled=True):
 assert len(weights)==PARAMS and all(type(w) is int and -127<=w<=127 for w in weights)
 assert len(public)==72 and all(len(e)==3 for e in public)
 mem=();rows=[]
 overrides=0;early=0;f60_count=0
 for i,e in enumerate(public):
  base,alternatives=native_alternatives(mem,e,i)
  best=None
  if interventions_enabled:
   for j,(act,drop,after,x) in enumerate(alternatives):
    score=sum((w/32)*feature for w,feature in zip(weights,x))
    key=(score,-j)
    if best is None or key>best[0]:best=(key,after)
  if best is not None and best[0][0]>.05:
   mem=best[1];overrides+=1;early+=int(i<48)
  else:mem=base;f60_count+=1
  F62._valid_memory(mem,PACK)
  if trace:rows.append(tuple(PACK.pack(*r).hex() for r in mem))
 return (mem,tuple(rows),dict(overrides=overrides,early_overrides=early,
          frozen_default_steps=f60_count)) if trace else mem
def training_examples(public,q):
 mem=();cases=[];counts=dict(positive=0,harmful=0,neutral=0)
 for i,e in enumerate(public):
  baseline,alts=native_alternatives(mem,e,i)
  if alts:
   control=F62._finish_fixed(baseline,public[i+1:],PACK)
   control_good=F62.codec().solve(control,q)==q["answer"]
   for act,drop,after,x in alts:
    terminal=F62._finish_fixed(after,public[i+1:],PACK)
    alt_good=PACK.solve(terminal,q)==q["answer"]
    if alt_good and not control_good:label=1.0;counts["positive"]+=1
    elif control_good and not alt_good:label=-1.0;counts["harmful"]+=1
    else:label=-.25;counts["neutral"]+=1
    cases.append((x,label))
  mem=baseline
 return cases,counts
def synthetic_train(data):
 examples=[];counts=dict(positive=0,harmful=0,neutral=0)
 for public,q in data:
  batch,stat=training_examples(public,q)
  examples.extend(batch)
  for k,v in stat.items():counts[k]+=v
 assert counts["positive"]>0 and counts["harmful"]>0,"F71_SYNTHETIC_TEACHER_LACKS_BIDIRECTIONAL_CREDIT"
 weights=[0.0]*PARAMS
 class_weight={1.0:4.0,-1.0:1.0,-.25:.1}
 for _ in range(3):
  for x,label in examples:
   score=sigmoid_sign(sum(w*feature for w,feature in zip(weights,x)))
   step=.025*class_weight[label]*(label-score)
   for j,v in enumerate(x):weights[j]+=step*v
 quant=tuple(max(-127,min(127,round(v*32))) for v in weights)
 return quant,dict(**counts,examples=len(examples))
def synthetic_smoke():
 data=[]
 for i in range(8):
  public,q,_=SOURCE.source(-3601-i,(-2,-1)[i%2])
  data.append((public,q))
 weights,labels=synthetic_train(data)
 guarded=[]
 for i in range(8):
  seed=-3611-i;family=(-2,-1)[i%2]
  public,q,meta=SOURCE.source(seed,family)
  mem,trace,activity=online(public,weights,True,True)
  fixed,proof,_=online(public,weights,True,False)
  assert AUDIT.verify(public,q,trace)["prefixes"]==72
  assert AUDIT.verify(public,q,proof)["prefixes"]==72
  assert fixed==F62.controls()[0].online_fixed(public)
  guarded.append(dict(seed=seed,kind=meta["question_type"],
    learned_correct=int(PACK.solve(mem,q)==q["answer"]),
    F60_correct=int(PACK.solve(fixed,q)==q["answer"]),
    early_legal_interventions=activity["early_overrides"]))
 total=sum(x["learned_correct"] for x in guarded)
 baseline=sum(x["F60_correct"] for x in guarded)
 early=sum(x["early_legal_interventions"] for x in guarded)
 passed=early>0 and total>=baseline
 result=dict(schema="yggdrasil.f71.synthetic-early-scheduler-qualification.v1",
  status="UNREGISTERED_SYNTHETIC_ONLY",training_cases=len(data),
  guard_cases=len(guarded),teacher_labels=labels,
  synthetic_weights=list(weights),learned_correct=total,
  frozen_F60_correct=baseline,early_interventions=early,
  method_prequalification_pass=passed,
  exact_prefix_audit_pass=True,
  registered_FIT_train_used=False,registered_FIT_validate_used=False,
  diagnostics_used=False,originals_used=False,F3=False,
  policy_promotion=False,guard_rows=guarded)
 print(json.dumps(result,sort_keys=True))
 if not passed:raise AssertionError("F71_SYNTHETIC_SCHEDULER_FAILED_PREQUALIFICATION")
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 synthetic_smoke()
