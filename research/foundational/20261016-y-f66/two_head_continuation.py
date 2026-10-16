"""F66 two-head public path continuation policy — UNTRAINED SOURCE ONLY.

Head 1 chooses whether to assemble role-coded records (merge/append).
Head 2 chooses which bounded 12-byte retained state to keep.
All online decisions use current public edge and previously retained records.
Future observations may provide offline FIT TRAIN labels but never online input.
"""
from __future__ import annotations
import hashlib,importlib.util,json,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert blob(HERE/"prereg.json")=="fc3283f28ab307b6834c93d530fffce98ad7c0de"
def load(name,path,sha):
 assert blob(path)==sha,("F66_TRANSITIVE_SOURCE_DRIFT",name)
 spec=importlib.util.spec_from_file_location(name,path)
 obj=importlib.util.module_from_spec(spec);sys.modules[name]=obj;spec.loader.exec_module(obj)
 return obj
SOURCE=load("f66_exact_public_generator",HERE.parent/"20261016-y-f63c"/"source.py",
 "c04b73306861098eecf55db77b2db486aa918819")
ACTION=load("f66_frozen_causal_candidate_engine",HERE.parent/"20261015-y-f62"/"source_pilot.py",
 "7ed72deca5584d7c0b6562d74456fa7d4bee6712")
AUDITOR=load("f66_independent_lossless_prefix_auditor",HERE.parent/"20261015-y-f62"/"audit_public.py",
 "383fff0bdd8c8b48fde9538d4e4d768db1c1896f")
PACK=ACTION.codec()
GATE_PARAMS=8
RANK_PARAMS=12
TOTAL_PARAMS=20
def _summary(records):
 lengths=[len(r[2]) for r in records]
 ends={}
 role_codes=set()
 for a,b,codes in records:
  ends[a]=ends.get(a,0)+1;ends[b]=ends.get(b,0)+1
  role_codes.update(codes)
 return (max(lengths,default=0)/6,
   sum(lengths)/72,
   sum(l>=2 for l in lengths)/12,
   sum(l>=4 for l in lengths)/12,
   min(sum(v>=2 for v in ends.values()),12)/12,
   len(role_codes)/8,
   len(records)/12)
def rank_features(after,action,drop,index,prior_len):
 longest,total,multi,long,hubs,roles,memfrac=_summary(after)
 return (1.0,longest,total,multi,long,hubs,roles,memfrac,
         int(drop>=0),int(action=="merge"),(memfrac-prior_len/12),index/71)
def gate_features(before,merge_after,append_after,event,index):
 m=_summary(merge_after)
 a=_summary(append_after)
 x,b,y=event
 endpoints={n for rec in before for n in rec[:2]}
 return (1.0,m[0]-a[0],m[1]-a[1],m[2]-a[2],
         m[3]-a[3],m[4]-a[4],
         int(x in endpoints and y in endpoints),index/71)
def step(before,event,index,weights,allow_continuation=True,detail=False):
 assert len(event)==3
 assert len(before)<=12
 assert len(weights)==TOTAL_PARAMS and all(type(w) is int and -127<=w<=127 for w in weights)
 options=ACTION.actions(before,event,index,PACK)
 ranked={}
 for j,(action,_old,drop,after,_f) in enumerate(options):
  f=rank_features(after,action,drop,index,len(before))
  score=sum(w*x for w,x in zip(weights[GATE_PARAMS:],f))
  key=(score,-j)
  if action not in ranked or key>ranked[action][0]:
   ranked[action]=(key,after,j)
 assert "append" in ranked
 selected="append"
 gate=None
 if "merge" in ranked:
  gf=gate_features(before,ranked["merge"][1],ranked["append"][1],event,index)
  if not allow_continuation:
   gf=(gf[0],0.0,0.0,0.0,0.0,0.0,gf[6],gf[7])
  gate=sum(w*x for w,x in zip(weights[:GATE_PARAMS],gf))
  if gate>0:selected="merge"
 after=ranked[selected][1]
 ACTION._valid_memory(after,PACK)
 return (after,selected,gate) if detail else after
def online(public,weights,trace=False,allow_continuation=True):
 assert len(public)==72 and all(len(e)==3 for e in public)
 memory=()
 snapshots=[]
 merges=0
 for index,event in enumerate(public):
  memory,action,_gate=step(memory,event,index,weights,allow_continuation,True)
  merges+=int(action=="merge")
  if trace:snapshots.append(tuple(PACK.pack(*r).hex() for r in memory))
 return (memory,tuple(snapshots),merges) if trace else memory
def smoke():
 # Engineering demonstration weights are NOT scientifically fitted.
 demo_weights=(6,2,2,2,2,2,1,0, 0,3,4,5,7,3,2,-1,-1,2,0,0)
 outcomes=[]
 for seed,family in ((-1701,-2),(-1702,-1),(-1703,-2),(-1704,-1)):
  public,q,meta=SOURCE.source(seed,family)
  memory,trace,nmerge=online(public,demo_weights,True)
  witness=AUDITOR.verify(public,q,trace)
  assert witness["prefixes"]==72 and witness["max_payload_bytes"]<=144
  without,trace_ab,ab_merges=online(public,demo_weights,True,False)
  assert AUDITOR.verify(public,q,trace_ab)["prefixes"]==72
  outcomes.append(dict(seed=seed,family=family,question_type=meta["question_type"],
   merge_steps=nmerge,ablation_merge_steps=ab_merges,
   demo_correct=int(PACK.solve(memory,q)==q["answer"])))
 assert sum(r["merge_steps"] for r in outcomes)>0
 return dict(schema="yggdrasil.f66.public-continuation-source-only.v1",
  stage="UNTRAINED_SYNTHETIC_SOURCE",synthetic_cases=len(outcomes),
  model_parameters=TOTAL_PARAMS,provisional_demo_merge_count=sum(r["merge_steps"] for r in outcomes),
  learned_weights_exist=False,registered_fit_executed=False,heldout_executed=False,
  diagnostic_executed=False,original_executed=False,F3=False,rows=outcomes)
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 print(json.dumps(smoke(),sort_keys=True))
