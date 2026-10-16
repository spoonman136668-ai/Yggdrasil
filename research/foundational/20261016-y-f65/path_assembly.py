"""Yggdrasil F65 learned path assembly — synthetic engineering ONLY.

Online retention receives public edge, exact packed memory, fixed weights.
Never receives source labels, a future query, private truth or unseen events.
"""
from __future__ import annotations
import hashlib,importlib.util,json,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent
PIN={"prereg.json":"9bbfd50b740be2c9d4ec891b3b360cd9650b7e23"}
def blob(path):
 raw=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
for name,digest in PIN.items():assert blob(HERE/name)==digest,(name,"F65_PREREG_CHANGED")
def load(name,path,sha):
 assert blob(path)==sha,("SOURCE_DRIFT",name)
 spec=importlib.util.spec_from_file_location(name,path)
 module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
 return module
SOURCE=load("f65_unchanged_source",HERE.parent/"20261016-y-f63c"/"source.py",
            "c04b73306861098eecf55db77b2db486aa918819")
BASE=load("f65_frozen_candidate_actions",HERE.parent/"20261015-y-f62"/"source_pilot.py",
          "7ed72deca5584d7c0b6562d74456fa7d4bee6712")
AUDITOR=load("f65_independent_prefix_audit",HERE.parent/"20261015-y-f62"/"audit_public.py",
          "383fff0bdd8c8b48fde9538d4e4d768db1c1896f")
PACK=BASE.codec()
PARAMS=16
def features(before,event,index,action,removed,after):
 assert len(event)==3 and len(before)<=12 and len(after)<=12
 before_l=[len(r[2]) for r in before]
 after_l=[len(r[2]) for r in after]
 num=lambda lengths,minlength:sum(x>=minlength for x in lengths)
 before_codes={x for rec in before for x in rec[2]}
 after_codes={x for rec in after for x in rec[2]}
 endpoint_degree={}
 for a,b,_ in after:
  endpoint_degree[a]=endpoint_degree.get(a,0)+1
  endpoint_degree[b]=endpoint_degree.get(b,0)+1
 a,_role,b=event
 event_supported=int(any(((p==a or p==b or q==a or q==b) and len(c)>=2) for p,q,c in after))
 cross_endpoint=int(any(p in endpoint_degree and endpoint_degree[p]>1 or q in endpoint_degree and endpoint_degree[q]>1 for p,q,_ in after))
 return (1.0,
    int(action=="merge"),
    (max(after_l,default=0)-max(before_l,default=0))/6,
    (num(after_l,2)-num(before_l,2))/12,
    (num(after_l,4)-num(before_l,4))/12,
    (sum(after_l)-sum(before_l))/72,
    event_supported,
    (len(after_codes)-len(before_codes))/8,
    min(sum(v>=2 for v in endpoint_degree.values()),24)/24,
    cross_endpoint,
    len(after_codes)/8,
    int(removed>=0),
    int(removed>=0 and len(before_l)>0 and max(after_l,default=0)<max(before_l)),
    len(after)/12,
    index/71,
    max(before_l,default=0)/6)
def online(public,weights,trace=False,allow_assembly=True):
 assert len(weights)==PARAMS and all(type(w) is int and -127<=w<=127 for w in weights)
 assert len(public)==72 and all(len(e)==3 for e in public)
 memory=()
 receipts=[]
 merges=0
 for index,event in enumerate(public):
  choices=BASE.actions(memory,event,index,PACK)
  best=None;chosen=None
  for j,(action,_old,evict,after,_original) in enumerate(choices):
   x=features(memory,event,index,action,evict,after)
   if not allow_assembly:
    x=x[:1]+(0.0,)*5+x[6:]
   score=sum(w*v for w,v in zip(weights,x))
   key=(score,-j)
   if best is None or key>best:
    best=key;chosen=(action,after)
  action,memory=chosen
  merges+=int(action=="merge")
  BASE._valid_memory(memory,PACK)
  if trace:receipts.append(tuple(PACK.pack(*r).hex() for r in memory))
 if trace:return memory,tuple(receipts),merges
 return memory
def synthetic_smoke():
 provisional=(0,22,18,10,15,5,2,1,0,1,1,0,-2,0,0,0)
 result=[]
 for seed,family in ((-1001,-2),(-1002,-1),(-1003,-2),(-1004,-1)):
  public,q,meta=SOURCE.source(seed,family)
  learned,trace,merges=online(public,provisional,trace=True)
  assert AUDITOR.verify(public,q,trace)["prefixes"]==72
  assert len(learned)*12<=144
  ablation,ablation_trace,ablation_merges=online(public,provisional,trace=True,allow_assembly=False)
  assert AUDITOR.verify(public,q,ablation_trace)["prefixes"]==72
  result.append(dict(seed=seed,family=family,kind=meta["question_type"],
       merges=merges,ablation_merges=ablation_merges,
       public_case_correct=int(PACK.solve(learned,q)==q["answer"])))
 assert sum(r["merges"] for r in result)>0,"ASSEMBLY_OPERATOR_UNREACHABLE"
 return dict(schema="yggdrasil.f65.source-only-synthetic-qualification.v1",
 stage="SOURCE_ONLY_UNTRAINED",synthetic_cases=len(result),
 synthetic_placeholder_only=True,merges_selected=sum(r["merges"] for r in result),
 actual_model_trained=False,registered_fit_used=False,
 heldout_used=False,diagnostic_used=False,original_used=False,
 F3=False,policy_promotion=False,rows=result)
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 print(json.dumps(synthetic_smoke(),sort_keys=True))
