"""F68 action-sensitive public structural teacher: SYNTHETIC ONLY.

Full public 9+9 junction labels are training-only. No questions, private tags,
or future observations reach the online model, whose exact 16 features are
frozen at the already-qualified causal source blob.
"""
from __future__ import annotations
import hashlib,importlib.util,json,math,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def gitblob(p):
 b=p.read_bytes();return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert gitblob(P/"train_method_precode.json")=="99d024db0ab22775f8a2790f0156eb2c56fe2101"
assert gitblob(P/"action_conditioned.py")=="c079cb2b6993429c302f4f634e2862d05056fbdb"
def load(name,path,expected):
 assert gitblob(path)==expected,(name,"METHOD_DRIFT")
 s=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
MODEL=load("f68_immutable_action_model",P/"action_conditioned.py",
           "c079cb2b6993429c302f4f634e2862d05056fbdb")
PUB=load("f68_frozen_public_only_graph_teacher",P/"public_bridge_labels.py",
         "aab85cca8d1f84b71dd4d1ed2733b80ebed087a2")
def utility(candidate,baseline,event,true_bridge):
 exact=MODEL.PACK.edge_record(event)
 keep=int(exact in candidate)
 match=int(candidate==baseline)
 comp=sum(min(len(r[2]),4)**2 for r in candidate)/16
 return (4 if true_bridge else -1)*keep+match+.25*comp
def training_case(public):
 assert len(public)==72 and all(len(e)==3 for e in public)
 true_bridges=PUB.full_public_bridge_edges(public)
 model=MODEL
 samples=[];raw_counts=dict(true_bridge_steps=0,other_steps=0,
    positive_credit=0,negative_credit=0,pairs=0)
 memory=()
 for index,event in enumerate(public):
  legal=model.ACTION.actions(memory,event,index,model.PACK)
  baseline=model.ACTION._f60_step(memory,event,model.PACK)
  found=None
  for action,_old,drop,after,_orig in legal:
   if after==baseline:
    found=model.features(memory,event,index,action,drop,after)
    break
  assert found is not None
  truth=tuple(event) in true_bridges
  raw_counts["true_bridge_steps"]+=int(truth)
  raw_counts["other_steps"]+=int(not truth)
  reference=utility(baseline,baseline,event,truth)
  for action,_old,drop,after,_orig in legal:
   if after==baseline:continue
   feat=model.features(memory,event,index,action,drop,after)
   delta=tuple(a-b for a,b in zip(feat,found))
   if not any(abs(x)>1e-10 for x in delta):continue
   value=max(-1,min(1,utility(after,baseline,event,truth)-reference))
   if abs(value)<1e-10:continue
   raw_counts["pairs"]+=1
   raw_counts["positive_credit"]+=int(value>0)
   raw_counts["negative_credit"]+=int(value<0)
   samples.append((delta,value,16 if truth else 1))
  memory=baseline
 assert raw_counts["true_bridge_steps"]==2
 return samples,raw_counts
def train(public_cases):
 data=[];counts={k:0 for k in ("true_bridge_steps","other_steps",
    "positive_credit","negative_credit","pairs")}
 for public in public_cases:
  samples,stats=training_case(public)
  data.extend(samples)
  for k in counts:counts[k]+=stats[k]
 assert counts["positive_credit"]>0 and counts["negative_credit"]>0
 weights=[0.0]*MODEL.NWEIGHTS
 for _ in range(3):
  for x,target,multiplier in data:
   expected=math.tanh(sum(w*v for w,v in zip(weights,x)))
   err=target-expected
   for i,v in enumerate(x):
    weights[i]+=.02*multiplier*err*v
 frozen=tuple(max(-127,min(127,round(w*16))) for w in weights)
 return frozen,counts
def smoke():
 data=[]
 for i in range(8):
  source_public,q,_meta=MODEL.SOURCE.source(-2801-i,(-2,-1)[i%2])
  data.append(source_public)
 weights,counts=train(data)
 rows=[]
 for i in range(8):
  seed=-2811-i;family=(-2,-1)[i%2]
  public,q,meta=MODEL.SOURCE.source(seed,family)
  frozen,trace,act=MODEL.online(public,weights,True,True)
  no_junction,trace_ab,_=MODEL.online(public,weights,True,False)
  assert MODEL.AUDITOR.verify(public,q,trace)["prefixes"]==72
  assert MODEL.AUDITOR.verify(public,q,trace_ab)["prefixes"]==72
  edges=PUB.full_public_bridge_edges(public)
  to_find={MODEL.PACK.edge_record(e) for e in edges}
  rows.append(dict(seed=seed,kind=meta["question_type"],
     learned_true_bridge_records=sum(int(r in to_find) for r in frozen),
     ablated_true_bridge_records=sum(int(r in to_find) for r in no_junction),
     learned_correct=int(MODEL.PACK.solve(frozen,q)==q["answer"]),
     ablation_correct=int(MODEL.PACK.solve(no_junction,q)==q["answer"]),
     merge_actions=act["merge_actions"]))
 totals=dict(learned_bridge_records=sum(r["learned_true_bridge_records"] for r in rows),
   ablation_bridge_records=sum(r["ablated_true_bridge_records"] for r in rows),
   learned_correct=sum(r["learned_correct"] for r in rows),
   ablation_correct=sum(r["ablation_correct"] for r in rows),
   selected_merges=sum(r["merge_actions"] for r in rows))
 positive=totals["learned_bridge_records"]>totals["ablation_bridge_records"] or totals["learned_correct"]>totals["ablation_correct"]
 valid=bool(positive and totals["learned_bridge_records"]>0 and totals["selected_merges"]>0)
 result=dict(schema="yggdrasil.f68.action-distillation.synthetic-qualification.v1",
   stage="UNREGISTERED_SYNTHETIC_ONLY",
   training_negative_seed_cases=8,guard_negative_seed_cases=8,
   teacher_counts=counts,provisional_weights=list(weights),guards=totals,
   independent_causal_audit=True,synthetic_model_qualified=valid,
   FIT_train_consumed=False,FIT_validation_consumed=False,
   DIAG_consumed=False,original_consumed=False,F3=False,
   accepted_ref_mutation=False,policy_promotion=False,
   rows=rows)
 print(json.dumps(result,sort_keys=True))
 if not valid:raise AssertionError("F68_SYNTHETIC_LEARNED_JUNCTION_GATE_BLOCKED")
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 smoke()
