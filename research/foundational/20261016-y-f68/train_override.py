"""F68 frozen counterfactual FIT-TRAIN-only junction credit; SYNTHETIC FIRST.

Offline teacher can finish remaining public TRAIN observations and check the
TRAIN question. Its signed-int8 online weights never see future evidence.
Unchanged F60 is the exact default at every non-junction public prefix.
"""
from __future__ import annotations
import hashlib,importlib.util,json,math,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def gitblob(path):
 raw=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
assert gitblob(P/"method_prereg.json")=="704a4e8ea30f7523505daebff14d716c59b07f69"
assert gitblob(P/"guarded_junction.py")=="f74c5acdc28ea91c0e5615483c644fcae040db93"
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
 return m
m=load("f68_fixed_shielded_online",P/"guarded_junction.py")
method=json.loads((P/"method_prereg.json").read_text())
def examples(public,question):
 assert len(public)==72
 memory=()
 counts=dict(eligible_junction_steps=0,positive=0,negative=0,neutral=0)
 pairs=[]
 for i,event in enumerate(public):
  baseline=m.ACTION._f60_step(memory,event,m.PACK)
  sep,_frontier,_both=m.BASE.public_junction_signal(memory,event)
  if sep:
   counts["eligible_junction_steps"]+=1
   options=m.ACTION.actions(memory,event,i,m.PACK)
   base_terminal=m.ACTION._finish_fixed(baseline,public[i+1:],m.PACK)
   base_correct=m.PACK.solve(base_terminal,question)==question["answer"]
   for action,_old,drop,after,_feat in options:
    if after==baseline:continue
    terminal=m.ACTION._finish_fixed(after,public[i+1:],m.PACK)
    other_correct=m.PACK.solve(terminal,question)==question["answer"]
    if other_correct and not base_correct:
     target=1.0;counts["positive"]+=1
    elif base_correct and not other_correct:
     target=-1.0;counts["negative"]+=1
    else:
     target=-.25;counts["neutral"]+=1
    x=m.score_features(baseline,after,event,action,drop,i)
    assert len(x)==m.PARAMS
    pairs.append((x,target))
  memory=baseline
 return pairs,counts
def train(cases):
 pairs=[];counts=dict(eligible_junction_steps=0,positive=0,negative=0,neutral=0)
 for public,q in cases:
  group,stat=examples(public,q)
  pairs.extend(group)
  for k,v in stat.items():counts[k]+=v
 if not (counts["positive"]>0 and counts["negative"]>0):
  raise AssertionError("F68_COUNTERFACTUAL_CREDIT_NO_BIDIRECTIONAL_EVIDENCE")
 w=[0.0]*m.PARAMS
 for _ in range(method["fixed_optimizer"]["epochs"]):
  for x,target in pairs:
   pred=math.tanh(sum(a*f for a,f in zip(w,x)))
   error=target-pred
   for j,f in enumerate(x):
    w[j]+=.03*error*f
 weights=tuple(max(-127,min(127,round(x*32))) for x in w)
 assert len(weights)==m.PARAMS
 counts["total_examples"]=len(pairs)
 return weights,counts
def synthetic_preflight():
 fit=[]
 for i in range(8):
  seed=-3001-i;family=(-2,-1)[i%2]
  public,q,_meta=m.SOURCE.source(seed,family)
  fit.append((public,q))
 weights,labels=train(fit)
 guards=[]
 for i in range(8):
  seed=-3011-i;family=(-2,-1)[i%2]
  public,q,meta=m.SOURCE.source(seed,family)
  learned,trace,stats=m.online(public,weights,True,True)
  fixed,ftrace,_=m.online(public,weights,True,False)
  claim=m.AUDITOR.verify(public,q,trace)
  assert claim["prefixes"]==72 and claim["max_payload_bytes"]<=144
  assert m.AUDITOR.verify(public,q,ftrace)["prefixes"]==72
  assert stats["nonjunction_steps"]==stats["nonjunction_exact_F60_parity"]
  guards.append(dict(seed=seed,kind=meta["question_type"],
    learned_correct=int(m.PACK.solve(learned,q)==q["answer"]),
    F60_correct=int(m.PACK.solve(fixed,q)==q["answer"]),
    override_steps=stats["override_steps"]))
 improved=sum(r["learned_correct"] for r in guards)
 baseline=sum(r["F60_correct"] for r in guards)
 overrides=sum(r["override_steps"] for r in guards)
 eligible=(overrides>0 and improved>=baseline)
 output=dict(schema="yggdrasil.f68.counterfactual-junction-credit.synthetic.v1",
   stage="UNREGISTERED_SYNTHETIC_ONLY",train_cases=8,guard_cases=8,
   frozen_model_weights=list(weights),offline_labels=labels,
   learned_synthetic_correct=improved,frozen_F60_correct=baseline,
   learned_override_steps=overrides,source_prequalification_pass=eligible,
   independent_causal_memory_proved=True,
   FIT_train_used=False,FIT_validation_used=False,
   DIAG_used=False,original_used=False,F3=False,policy_promotion=False,
   rows=guards)
 print(json.dumps(output,sort_keys=True))
 if not eligible:raise AssertionError("F68_SYNTHETIC_SHIELDING_OR_LEARNED_OVERRIDE_GATE_FAILED")
 return output
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 synthetic_preflight()
