"""Y-F57 bounded learned causal online graph-component consolidation.

No diagnostic, original, or private future-query inputs to the policy.
An integer six-parameter state-action policy chooses merging, repeated local
component completion, and eviction from only 12 losslessly coded records
and the current public edge. Parameters are selected by deterministic,
bounded reward optimization on first-half FIT source streams only and frozen
before second-half FIT validation. This does not qualify native 576B memory.
"""
from __future__ import annotations
import importlib.util,json,random,sys
from pathlib import Path
P=Path(__file__).resolve().parent
def load(alias,path):
 spec=importlib.util.spec_from_file_location(alias,path)
 mod=importlib.util.module_from_spec(spec)
 sys.modules[alias]=mod;spec.loader.exec_module(mod)
 return mod
src=load("y57_frozen_source",P/"source_feasibility.py")
codec=src.codec
TRAIN=range(651000,651008)
VALID=range(651008,651016)
FAMS=src.FIT_FAMILIES
POLICIES=("learned_causal_component","frozen_F57_online","fixed_pair_chunk",
          "fixed_triple_chunk","public_component_priority","public_FIFO",
          "public_hash","offline_full_public_noncompetitive",
          "future_query_oracle_unfair")
PARAMS=6
CAP=12
def utility(rec,memory,w):
 a,b,codes=rec
 endpoint_degree=sum(a in (x,y) for x,y,z in memory)+sum(b in (x,y) for x,y,z in memory)
 n=len(codes)
 return (w[0]*n+w[1]*(n==2)+w[2]*(n==3)+w[3]*(n==4)+
         w[4]*min(3,endpoint_degree)+w[5]*len({v//2 for v in codes}))
def learned_memory(stream,w):
 memory=[]
 for idx,event in enumerate(stream):
  # Only the public role edge; discard even the randomized public tag,
  # which is intentionally balanced between useful and distractor edges.
  new=codec.edge_record(event[:3])
  for attempt in range(2):
   options=[(at,merged) for at,merged in codec.candidates(memory,new)
            if len(merged[2])<=4]
   if not options:break
   choices=[(utility(rec,memory,w)-utility(new,memory,w),
             len(rec[2]),-at,at,rec) for at,rec in options]
   best=max(choices,key=lambda x:x[:3])
   if best[0]<0:break
   at=best[3]
   memory.pop(at)
   new=best[4]
  memory.append(new)
  if len(memory)>CAP:
   remove=min(range(len(memory)),key=lambda k:(utility(memory[k],memory,w),k))
   memory.pop(remove)
  assert len(memory)<=CAP
  assert all(codec.unpack(codec.pack(*r))==r for r in memory)
 return tuple(memory)
def fixed_memory(stream,mode):
 if mode=="frozen_F57_online":
  return src.online_fixed(stream)
 if mode in ("fixed_pair_chunk","fixed_triple_chunk","public_component_priority"):
  memory=[]
  limit={"fixed_pair_chunk":2,"fixed_triple_chunk":3,
         "public_component_priority":4}[mode]
  for event in stream:
   new=codec.edge_record(event[:3])
   options=[(i,r) for i,r in codec.candidates(memory,new) if len(r[2])<=limit]
   if options:
    i,joined=max(options,key=lambda x:(len(x[1][2]),-x[0]))
    memory.pop(i);new=joined
   memory.append(new)
   if len(memory)>CAP:
    if mode=="public_component_priority":
     degree=lambda r:sum(r[0] in (x,y) or r[1] in (x,y) for x,y,_ in memory)
     drop=min(range(len(memory)),key=lambda i:(len(memory[i][2]),degree(memory[i]),i))
    else:drop=min(range(len(memory)),key=lambda i:(len(memory[i][2]),i))
    memory.pop(drop)
  return tuple(memory)
 if mode=="public_FIFO":
  return tuple(codec.edge_record(e[:3]) for e in stream[-CAP:])
 if mode=="public_hash":
  # Record-independent stable public priority; no source labels.
  ranked=[codec.edge_record(e[:3]) for e in stream]
  return tuple(sorted(ranked,key=codec.hash_value)[-CAP:])
 raise ValueError("invalid baseline")
def eval_policy(w,split):
 scores=0
 for seed in split:
  for family in FAMS:
   stream,q,_=src.source(seed,family)
   memory=learned_memory(stream,w)
   scores+=int(codec.solve(memory,q)==q["answer"])
 return scores
def train():
 # 48 candidate policies maximum; a deterministic FIT-only
 # bounded evolutionary optimization, not a fixed strategy bank.
 rng=random.Random(57057)
 population=[(0,)*PARAMS,(3,2,-1,3,0,1),(3,1,1,3,0,1),
             (5,3,-2,2,2,1)]
 evaluated={}
 for generation in range(4):
  for w in population:
   if w not in evaluated:evaluated[w]=eval_policy(w,TRAIN)
  best=sorted(evaluated,key=lambda w:(-evaluated[w],sum(abs(x) for x in w),w))[:4]
  if generation==3:break
  population=list(best)
  for k in range(8):
   parent=best[k%len(best)]
   mutated=list(parent)
   j=rng.randrange(PARAMS)
   mutated[j]=max(-8,min(8,mutated[j]+rng.choice((-3,-2,-1,1,2,3))))
   if rng.random()<.30:
    j=rng.randrange(PARAMS)
    mutated[j]=max(-8,min(8,mutated[j]+rng.choice((-2,2))))
   population.append(tuple(mutated))
 winner=min(evaluated,key=lambda w:(-evaluated[w],sum(abs(x) for x in w),w))
 assert len(evaluated)<=64
 return winner,evaluated[winner],len(evaluated)
def evaluate():
 assert not set(TRAIN)&set(VALID)
 assert not set(TRAIN)&set(src.DIAG)
 assert not set(VALID)&set(src.ORIGINAL)
 weights,fit_correct,policy_candidates=train()
 rows=[]
 for seed in VALID:
  for family in FAMS:
   stream,q,regime=src.source(seed,family)
   cases={};receipts={}
   for arm in POLICIES[:-2]:
    stored=learned_memory(stream,weights) if arm==POLICIES[0] else fixed_memory(stream,arm)
    cases[arm]=int(codec.solve(stored,q)==q["answer"])
    receipts[arm]=[codec.pack(*r).hex() for r in stored]
   full=src.offline_public_witness(stream)
   cases[POLICIES[-2]]=int(codec.solve(full,q)==q["answer"])
   cases[POLICIES[-1]]=1
   retained=[codec.unpack(bytes.fromhex(z)) for z in receipts[POLICIES[0]]]
   no_chunk=int(codec.solve([r for r in retained if len(r[2])==1],q)==q["answer"])
   rows.append(dict(seed=seed,family=family,regime=regime,
     public_events=[list(e[:3]) for e in stream],
     question=dict(start=q["start"],ops=[list(x) for x in q["ops"]],answer=q["answer"]),
     answers=cases,receipts=receipts,learned_without_chunks=no_chunk))
 scores={arm:sum(row["answers"][arm] for row in rows) for arm in POLICIES}
 by_family={str(f):{arm:sum(r["answers"][arm] for r in rows if r["family"]==f)
             for arm in POLICIES} for f in FAMS}
 fair=POLICIES[1:-2]
 strongest=max(fair,key=lambda a:scores[a])
 gain=(scores[POLICIES[0]]-scores[strongest])/len(rows)
 ablation=(scores[POLICIES[0]]-sum(r["learned_without_chunks"] for r in rows))/len(rows)
 safe=all(by_family[str(f)][POLICIES[0]]>=max(by_family[str(f)][arm]
          for arm in fair) for f in FAMS)
 accepted=(gain>=.05 and ablation>0 and safe)
 return dict(schema="yggdrasil.f57.trainable-causal-component.within-FIT.v1",
   stage="F57_NEW_FIT_SPLIT_ONLY_NO_DIAGNOSTIC",
   parent_F57_frozen_source_head="0269f25f0ae4e9590f5087de7a4909c97bd64edb",
   training_seeds=[TRAIN.start,TRAIN.stop],
   validation_seeds=[VALID.start,VALID.stop],
   FIT_families=list(FAMS),training_cases=len(TRAIN)*len(FAMS),
   validation_cases=len(rows),train_correct=fit_correct,
   learned_int8_policy_parameters=list(weights),
   candidates_examined=policy_candidates,
   records_max=CAP,record_bytes=12,persistent_record_budget_bytes=144,
   learned_parameter_bytes=PARAMS,model_params_not_in_144B_record_count=True,
   query_and_core_membership_hidden_during_policy=True,
   rows=rows,correct=scores,by_family=by_family,
   strongest_same_byte_online_fair=strongest,
   learned_gain_vs_fair=gain,learned_composition_ablation_gain=ablation,
   per_family_nondegradation=safe,frozen_gate_met=accepted,
   verdict="FIT_ONLY_LEARNED_CAUSAL_CONSOLIDATION_SUPPORTED" if accepted else
            "FIT_ONLY_LEARNED_CAUSAL_CONSOLIDATION_NEGATIVE",
   future_DIAG_untouched=True,originals_untouched=True,
   independent_F3=False,native_total_576B_unverified=True,
   accepted_ref_mutation=False,paid_API_calls=0)
if __name__=="__main__":
 if len(sys.argv)!=2 or sys.argv[1]!="--fit-validation":
  raise SystemExit("Only source-independent FIT training and FIT validation")
 print(json.dumps(evaluate(),sort_keys=True))
