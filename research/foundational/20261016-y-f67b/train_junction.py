"""F67B preregistered public-junction contrastive learning: SYNTHETIC ONLY.

Frozen online policy uses public memory/prefix only. Offline teacher uses
only the currently available public prefix and frozen F60 next-state
imitation outside public junctions. No future query/answers/edges/tags.
"""
from __future__ import annotations
import hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert blob(P/"training_prereg.json")=="a3a8450ae8ee149f81b6a2c9e061ed5ae198d539"
assert blob(P/"action_junction.py")=="7ea16c037642dedbc46d5e6e27cc1d5975bbb3f5"
def load(name,path):
 sp=importlib.util.spec_from_file_location(name,path)
 obj=importlib.util.module_from_spec(sp);sys.modules[name]=obj;sp.loader.exec_module(obj)
 return obj
m=load("f67b_training_exact_source",P/"action_junction.py")
frozen=json.loads((P/"training_prereg.json").read_text())
def public_value(after,event):
 c=frozen["frozen_coefficients"]
 hops=sum(len(roles)**2 for _,_,roles in after)
 endpoints={n for a,b,_ in after for n in (a,b)}
 a,_,b=event
 supported=int(a in endpoints)+int(b in endpoints)
 return (c["composed_hop_coverage"]*min(1,hops/72)
        +c["distinct_retained_endpoints"]*min(1,len(endpoints)/24)
        +c["event_endpoint_support"]*supported/2)
def teacher_choice(mem,event,index):
 candidates=m.ACTION.actions(mem,event,index,m.PACK)
 baseline=m.ACTION._f60_step(mem,event,m.PACK)
 sep,frontier,_both=m.BASE.public_junction_signal(mem,event)
 if sep or frontier:
  k=max(range(len(candidates)),
        key=lambda j:(public_value(candidates[j][3],event),-j))
 else:
  matching=[j for j,candidate in enumerate(candidates) if candidate[3]==baseline]
  assert matching,"FROZEN_F60_NOT_IN_NATIVE_ACTIONS"
  k=matching[0]
 return k,candidates,baseline,bool(sep or frontier)
def train(publics):
 groups=[]
 stats=dict(teacher_append=0,teacher_merge=0,junction_steps=0,
            nonjunction_steps=0,pairwise_examples=0,zero_feature_differences=0)
 for public in publics:
  assert len(public)==72
  mem=()
  for i,event in enumerate(public):
   target,options,base,junction=teacher_choice(mem,event,i)
   target_action,_,target_drop,target_after,_f=options[target]
   stats["junction_steps" if junction else "nonjunction_steps"]+=1
   stats["teacher_merge" if target_action=="merge" else "teacher_append"]+=1
   f_target=m.public_action_features(mem,event,i,target_action,target_drop,target_after,True)
   for j,(action,_old,drop,after,_features) in enumerate(options):
    if j==target or after==target_after:continue
    f=m.public_action_features(mem,event,i,action,drop,after,True)
    delta=tuple(x-y for x,y in zip(f_target,f))
    if all(abs(v)<1e-12 for v in delta):
     stats["zero_feature_differences"]+=1
     continue
    groups.append(delta);stats["pairwise_examples"]+=1
   mem=base
 assert stats["teacher_merge"]>0 and stats["teacher_append"]>0
 assert stats["pairwise_examples"]>0
 w=[0.0]*m.PARAMS
 for _ in range(3):
  for delta in groups:
   margin=sum(a*x for a,x in zip(w,delta))
   if margin<.1:
    for j,x in enumerate(delta):
     w[j]+=.025*x
 quant=tuple(max(-127,min(127,round(x*32))) for x in w)
 assert len(quant)==m.PARAMS
 return quant,stats
def synthetic_preflight():
 train_cases=[]
 for i in range(8):
  public,_question,_meta=m.SOURCE.source(-2701-i,(-2,-1)[i%2])
  train_cases.append(public)
 weights,stats=train(train_cases)
 guard=[]
 for i in range(8):
  seed=-2711-i;fam=(-2,-1)[i%2]
  public,q,meta=m.SOURCE.source(seed,fam)
  kept,trace,merges=m.online(public,weights,True,True)
  ab,ab_trace,ab_merges=m.online(public,weights,True,False)
  assert m.AUDITOR.verify(public,q,trace)["prefixes"]==72
  assert m.AUDITOR.verify(public,q,ab_trace)["prefixes"]==72
  f60=m.ACTION.controls()[0].online_fixed(public)
  guard.append(dict(seed=seed,family=fam,kind=meta["question_type"],
    learned_merges=merges,ablation_merges=ab_merges,
    learned_correct=int(m.PACK.solve(kept,q)==q["answer"]),
    ablation_correct=int(m.PACK.solve(ab,q)==q["answer"]),
    fixed_F60_correct=int(m.PACK.solve(f60,q)==q["answer"])))
 total=sum(r["learned_merges"] for r in guard)
 result=dict(schema="yggdrasil.f67b.junction-distillation.synthetic-preflight.v1",
   stage="UNREGISTERED_SYNTHETIC_ONLY",
   frozen_weights=list(weights),teacher_counts=stats,
   train_synthetic_cases=len(train_cases),guard_synthetic_cases=len(guard),
   guard_learned_merges=total,ablation_merges=sum(r["ablation_merges"] for r in guard),
   guard_learned_correct=sum(r["learned_correct"] for r in guard),
   guard_ablation_correct=sum(r["ablation_correct"] for r in guard),
   guard_F60_correct=sum(r["fixed_F60_correct"] for r in guard),
   source_prequalification_pass=total>0,
   FIT_train_consumed=False,FIT_validate_consumed=False,
   DIAG_consumed=False,original_consumed=False,F3=False,
   policy_promotion=False,guards=guard)
 print(json.dumps(result,sort_keys=True))
 if not result["source_prequalification_pass"]:
  raise AssertionError("LEARNED_F67B_SELECTS_ZERO_MERGES")
 return result
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 synthetic_preflight()
