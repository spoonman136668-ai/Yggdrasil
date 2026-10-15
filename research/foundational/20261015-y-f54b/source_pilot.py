"""Y-F54B lossless, query-blind multi-hop relation records under 144-byte budget.

No future query is passed to online ingestion. FIT-only path labels train the
public ranker. At most 12 records, 12 bytes each (payload only); Python
metadata and operating/runtime memory NOT included in physical qualification.
"""
import importlib.util,json,math,random,sys
from pathlib import Path
P=Path(__file__).resolve().parent.parent/"20261015-y-f53"/"source_pilot.py"
spec=importlib.util.spec_from_file_location("yf54_source_parent",P)
base=importlib.util.module_from_spec(spec);sys.modules[spec.name]=base;spec.loader.exec_module(base)
FIT=range(621000,621008);DIAG=range(621100,621116)
FIT_FAM=(1240,1241,1242,1243);DIAG_FAM=(1244,1245,1246,1247)
RESERVED=range(622000,622016)
base.FIT=FIT;base.DIAG=DIAG;base.RESERVED=RESERVED
base.FIT_FAM=(1140,1141,1142,1143);base.DIAG_FAM=(1144,1145,1146,1147)
ARMS=("fit_public_two_link_composition","fixed_public_two_link_composition",
"fixed_public_three_link_composition","public_connected_component_raw",
"public_degree_raw","FIFO_raw","public_hash_raw",
"private_future_question_oracle_UNFAIR")
CAP=12;PAYLOAD=12;EVENTS=64;DIM=8
def source(seed,family):
 if not ((seed in FIT and family in FIT_FAM) or
         (seed in DIAG and family in DIAG_FAM)):
  raise ValueError("unregistered seed/family; original denied")
 return base.source(seed,family-100)
def rawrecord(e,i):
 u,role,v,tag=e
 return (u,((role,1),),v,(i,),i,float(tag))
def inverted(record):
 u,steps,v,indices,idx,tag=record
 return (v,tuple((r,-d) for r,d in reversed(steps)),u,tuple(reversed(indices)),idx,tag)
def expand(left,right,max_len):
 if left[2]!=right[0] or set(left[3])&set(right[3]):return None
 steps=left[1]+right[1]
 if len(steps)>max_len:return None
 return (left[0],steps,right[2],left[3]+right[3],max(left[4],right[4]),
         (left[5]*len(left[1])+right[5]*len(right[1]))/len(steps))
def candidates(memory,incoming,max_len):
 raw=rawrecord(incoming[1],incoming[0])
 options=list(memory)+[raw]
 if max_len>1:
  for old in memory:
   for a,b in ((old,raw),(raw,old),(inverted(old),raw),(raw,inverted(old))):
    record=expand(a,b,max_len)
    if record:options.append(record)
 # Prevent artificially multiplying a candidate to fill slots.
 by_key={}
 for z in options:
  key=(z[0],z[1],z[2],tuple(sorted(z[3])))
  if key not in by_key or z[4]>by_key[key][4]:by_key[key]=z
 return list(by_key.values())
def features(z,pool):
 u,steps,v,indices,i,tag=z
 deg=sum((p[0]==u)+(p[2]==u)+(p[0]==v)+(p[2]==v) for p in pool)
 nroles=len({role for role,d in steps})
 age=i/63
 join=sum(p[2]==u or p[0]==v for p in pool)
 return (1.,len(steps)/3,deg/32,nroles/3,age,tag,
         min(12,join)/12.,(len(steps)-1)/2)
def publichash(z):
 return random.Random(z[0]*211+z[2]*61+len(z[1])*311+z[4]*107+5401).random()
def rating(z,pool,arm,w):
 feat=features(z,pool)
 if arm=="fit_public_two_link_composition":
  return sum(a*b for a,b in zip(w,feat))
 if arm=="fixed_public_two_link_composition":
  return feat[1]*4+feat[2]+feat[6]/4
 if arm=="fixed_public_three_link_composition":
  return feat[1]*4+feat[3]+feat[2]/4
 if arm=="public_connected_component_raw":return feat[6]*4+feat[2]
 if arm=="public_degree_raw":return feat[2]*4+feat[3]/4
 if arm=="FIFO_raw":return feat[4]
 if arm=="public_hash_raw":return publichash(z)
 raise ValueError("unregistered online method")
def ingest(events,arm,w):
 """Completely blind to future question or hidden true-path membership."""
 memory=[]
 max_len=2 if arm in ("fit_public_two_link_composition",
                        "fixed_public_two_link_composition") else (
 3 if arm=="fixed_public_three_link_composition" else 1)
 for i,e in enumerate(events):
  options=candidates(memory,(i,e),max_len)
  memory=sorted(options,key=lambda z:(rating(z,options,arm,w),
                 z[4],z[0],z[2],len(z[1])),reverse=True)[:CAP]
  assert len(memory)<=CAP and all(1<=len(z[1])<=max_len for z in memory)
 return memory
def solve_records(memory,question):
 """Compose stored public role paths at query time; no unavailable raw edges."""
 possible={question["start"]};seq=tuple(tuple(z) for z in question["chain"])
 for off in range(len(seq)):
  next_possible=set()
  if off==0:states={(question["start"],0)}
  else:break
  for _ in range(len(seq)):
   updated=set()
   for at,j in states:
    for z in memory:
     for r in (z,inverted(z)):
      n=len(r[1])
      if r[0]==at and seq[j:j+n]==r[1]:
       updated.add((r[2],j+n))
   states|=updated
  return question["answer"] in {node for node,i in states if i==len(seq)}
def fit():
 data=[]
 for seed in FIT:
  for family in FIT_FAM:
   events,q,paths=source(seed,family)
   relevant=set()
   for path in paths:
    es=list(path["edges"])
    for i in range(len(es)):
     for size in (1,2):
      if i+size<=len(es):
       relevant.add(frozenset(tuple(es[j]) for j in range(i,i+size)))
   # Samples from public online candidate construction, FIT labels allowed.
   mem=[]
   for i,e in enumerate(events):
    opts=candidates(mem,(i,e),2)
    for z in opts:
     witness=frozenset(tuple(events[j][:3]) for j in z[3])
     data.append((features(z,opts),int(witness in relevant)))
    mem=sorted(opts,key=lambda z:(len(z[1]),z[4]),reverse=True)[:CAP]
 w=[0.]*DIM
 for epoch in range(6):
  for feat,y in data:
   z=sum(a*b for a,b in zip(feat,w))
   pred=1/(1+math.exp(-max(-12,min(12,z))))
   for i in range(DIM):w[i]-=.015*((pred-y)*feat[i]+.0001*w[i])
 return tuple(w),len(data)
def report_record(z):
 return dict(from_node=z[0],steps=[list(k) for k in z[1]],to_node=z[2],
             witness_indices=list(z[3]),latest_event_index=z[4],
             public_tag_average=z[5],serialized_payload_bytes=PAYLOAD)
def run():
 w,nfit=fit();rows=[]
 for seed in DIAG:
  for family in DIAG_FAM:
   events,q,paths=source(seed,family)
   results={};receipts={}
   question=dict(start=q["start"],chain=[list(z) for z in q["chain"]],
                 answer=q["answer"])
   for arm in ARMS[:-1]:
    retained=ingest(events,arm,w)
    receipts[arm]=[report_record(z) for z in retained]
    results[arm]=int(solve_records(retained,question))
   results[ARMS[-1]]=int(base.solve(q["edges"],q)==q["answer"])
   rows.append(dict(seed=seed,family=family,public_events=[list(e) for e in events],
        question=question,results=results,retained_records=receipts))
 scores={a:dict(correct=sum(r["results"][a] for r in rows),total=len(rows))
         for a in ARMS}
 for sc in scores.values():sc["accuracy"]=sc["correct"]/sc["total"]
 by={str(f):{a:sum(r["results"][a] for r in rows if r["family"]==f)
             for a in ARMS} for f in DIAG_FAM}
 cand=ARMS[0];fair=ARMS[1:-1];best=max(fair,key=lambda a:scores[a]["correct"])
 gain=(scores[cand]["correct"]-scores[best]["correct"])/len(rows)
 no_reg=all(by[str(f)][cand]>=max(by[str(f)][a] for a in fair) for f in DIAG_FAM)
 passed=gain>=.05 and no_reg
 return dict(schema="yggdrasil.f54b.query-blind-multihop-composition.trainonly.v1",
  stage="FRESH_EQUAL_PAYLOAD_TRAIN_ONLY_NO_ORIGINAL",
  fit_seeds=[FIT.start,FIT.stop],fit_families=list(FIT_FAM),
  diagnostic_seeds=[DIAG.start,DIAG.stop],diagnostic_families=list(DIAG_FAM),
  original_seeds_NOT_RESERVED=[RESERVED.start,RESERVED.stop],
  train_examples=nfit,learned_fit_weights=list(w),cases=len(rows),rows=rows,
  scores=scores,by_family=by,strongest_fair_control=best,candidate_gain=gain,
  per_family_nondegradation=no_reg,frozen_gate_met=passed,
  serialized_payload_bytes_per_record=PAYLOAD,serialized_payload_budget_bytes=PAYLOAD*CAP,
  total_native_576B_residency_qualified=False,
  future_question_hidden_during_ingestion=True,independent_F3=False,
  original_executed=False,accepted_ref_mutation=False,paid_api_calls=0,
  verdict="TRAIN_ONLY_COMPOSITION_SUPPORTED_NOT_F3" if passed
         else "TRAIN_ONLY_COMPOSITION_NOT_SUPPORTED")
if __name__=="__main__":print(json.dumps(run(),sort_keys=True))
