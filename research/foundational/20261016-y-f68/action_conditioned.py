"""F68 public context × candidate action interaction policy — source only.

All next memories belong to the original frozen ACTION.actions candidate
space and pass the separate causal-prefix auditor. No protected cohorts.
"""
from __future__ import annotations
import hashlib,importlib.util,json,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes();return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert blob(HERE/"prereg.json")=="d6bb9395bce54562bb89bfb07dcb445a9996123a"
def load(name,path,sha):
 assert blob(path)==sha,("F68_DEPENDENCY_DRIFT",name)
 s=importlib.util.spec_from_file_location(name,path)
 o=importlib.util.module_from_spec(s);sys.modules[name]=o;s.loader.exec_module(o)
 return o
PARENT=load("f68_immutable_parent",HERE.parent/"20261016-y-f67a"/"causal_memory.py",
 "b370396b3c3571be2c01ab2b33effef14f248eef")
SOURCE=PARENT.SOURCE
ACTION=PARENT.ACTION
AUDITOR=PARENT.AUDITOR
PACK=PARENT.PACK
NWEIGHTS=16
def features(before,event,index,action,drop,after):
 assert len(event)==3 and 0<=index<72
 signal=PARENT.public_junction_signal(before,event)
 edge=PACK.edge_record(event)
 retained=int(edge in after)
 lengths=[len(x[2]) for x in after]
 roles={c//2 for _a,_b,codes in after for c in codes}
 endpoints=set(n for a,b,_codes in after for n in (a,b))
 ordinary,junction=PARENT.logical_partition(after)
 return (
  1.0, int(action=="merge"),
  sum(lengths)/72, max(lengths,default=0)/6,
  retained,retained*signal[0],retained*signal[1],
  retained*signal[2],
  len(roles)/4,len(endpoints)/24,
  sum(x>=4 for x in lengths)/12,
  len(ordinary)/10,len(junction)/2,
  int(drop>=0),index/71,
  retained*int(len(after)>=10))
def online(public,weights,trace=False,enable_interaction=True):
 assert len(public)==72 and all(len(x)==3 for x in public)
 assert len(weights)==NWEIGHTS and all(type(w) is int and -127<=w<=127 for w in weights)
 memory=();receipts=[]
 counts={"merge_actions":0,"incoming_retained":0,"junction_interactions":0,
         "choices_with_action_dependent_junction_features":0}
 for index,event in enumerate(public):
  choices=ACTION.actions(memory,event,index,PACK)
  xlist=[features(memory,event,index,action,drop,after)
         for action,_old,drop,after,_p in choices]
  if any(x[5:8]!=xlist[0][5:8] for x in xlist[1:]):
   counts["choices_with_action_dependent_junction_features"]+=1
  best=None
  for j,((action,_old,_drop,after,_p),x) in enumerate(zip(choices,xlist)):
   if not enable_interaction:
    x=x[:5]+(0.0,0.0,0.0)+x[8:]
   score=sum(w*v for w,v in zip(weights,x))
   key=(score,-j)
   if best is None or key>best[0]:
    best=(key,action,after,x)
  _,action,memory,x=best
  counts["merge_actions"]+=int(action=="merge")
  counts["incoming_retained"]+=int(PACK.edge_record(event) in memory)
  counts["junction_interactions"]+=int(bool(x[5] or x[6] or x[7]))
  ACTION._valid_memory(memory,PACK)
  if trace:receipts.append(tuple(PACK.pack(*r).hex() for r in memory))
 return (memory,tuple(receipts),counts) if trace else memory
def smoke():
 # Not scientific learned weights: only shows the registered architecture
 # has action-dependent public junction features and causal transitions.
 demo=(0,32,6,10,8,12,9,3,0,1,6,0,0,-2,0,2)
 rows=[]
 for k in range(12):
  seed=-2701-k;family=(-2,-1)[k%2]
  public,q,meta=SOURCE.source(seed,family)
  mem,trace,stats=online(public,demo,True)
  aud=AUDITOR.verify(public,q,trace)
  assert aud["prefixes"]==72 and aud["max_payload_bytes"]<=144
  ab,abtrace,_=online(public,demo,True,False)
  assert AUDITOR.verify(public,q,abtrace)["prefixes"]==72
  rows.append(dict(seed=seed,kind=meta["question_type"],
      action_conditional_choice_points=stats["choices_with_action_dependent_junction_features"],
      merges=stats["merge_actions"],retained_incidents=stats["incoming_retained"],
      correct=int(PACK.solve(mem,q)==q["answer"]),
      ablation_correct=int(PACK.solve(ab,q)==q["answer"])))
 totals=dict(synthetic_cases=len(rows),
  feature_interaction_choice_points=sum(x["action_conditional_choice_points"] for x in rows),
  merges=sum(x["merges"] for x in rows))
 assert totals["feature_interaction_choice_points"]>0
 assert totals["merges"]>0
 return dict(schema="yggdrasil.f68.action-conditioned-source.synthetic.v1",
    stage="UNTRAINED_SYNTHETIC_SOURCE_ONLY",totals=totals,
    causal_prefix_audit_pass=True,
    model_trained=False,registered_fit_used=False,heldout_used=False,
    diagnostics_used=False,originals_used=False,F3=False,policy_promotion=False,
    rows=rows)
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 print(json.dumps(smoke(),sort_keys=True))
