"""T10 query-blind learned causal memory, 144-byte native limit.

TRAIN credit can use PRIVATE corridor labels, never at OPEN retention.
Independent negative fixture IDs only. Four eight-hop questions are revealed
only after the full 72-event stream. Native F62 codec and F60 unchanged.
"""
from __future__ import annotations
import random,json,importlib.util,sys,time,tracemalloc
from pathlib import Path
D=Path(__file__).parent
TRAIN=range(-23011,-23003);OPEN=range(-23103,-23099)
def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s)
 sys.modules[n]=m;s.loader.exec_module(m);return m
def source(seed):
 assert seed in TRAIN or seed in OPEN
 rng=random.Random(998721+abs(seed)*18181);used=set()
 def node():
  while True:
   v=rng.randrange(1000,2147000000)
   if v not in used:used.add(v);return v
 paths=[tuple(node() for j in range(9)) for i in range(4)]
 core=[(p[j],j%4,p[j+1]) for p in paths for j in range(8)]
 noise=[(node(),rng.randrange(4),node()) for _ in range(40)]
 stream=core+noise;rng.shuffle(stream)
 queries=[{"start":p[0],"ops":tuple((j%4,1) for j in range(8))} for p in paths]
 return tuple(stream),tuple(queries),tuple(p[8] for p in paths),frozenset(core)
def features(public,kernel,packing):
 samples=[];recent=[]
 for i,e in enumerate(public):
  rec=packing.edge_record(e)
  x=kernel.public_features(recent,packing.pack(*rec),i)
  samples.append(x);recent=(recent+[rec])[-10:]
 return samples
def candidate(public,weights,packing):
 # Early query NOT supplied. Sorted native public causal components only.
 assert len(public)==72 and len(weights)==20
 w=[v if v<128 else v-256 for v in weights]
 memory=();merges=0
 for i,event in enumerate(public):
  incoming=packing.edge_record(event)
  proposals=[("append",-1,incoming)]
  for j,record in packing.candidates(list(memory),incoming):
   if 1<len(record[2])<=6 and record[0]!=record[1]:
    proposals.append(("merge",j,record))
  scores=[]
  for typ,index,rec in proposals:
   after=tuple(x for j,x in enumerate(memory) if j!=index)+(rec,)
   # TRUE learned public structural score influences both action and
   # selection of the eviction victim; no graph/source truth used.
   degree={}
   for a,b,seq in after:
    degree[a]=degree.get(a,0)+1;degree[b]=degree.get(b,0)+1
   utility=lambda v:(20*len(v[2])+
                 w[0]*len(v[2])/8+w[1]*(degree.get(v[0],0)+degree.get(v[1],0))/8+
                 w[2]*int(len(v[2])>2)/8)
   if len(after)>10:
    victim=min(range(len(after)),key=lambda z:(utility(after[z]),z))
    after=tuple(x for j,x in enumerate(after) if j!=victim)
   val=sum(utility(x) for x in after)+w[3]*int(typ=="merge")/8
   scores.append((val,len(rec[2]),-index,typ,after))
  best=max(scores,key=lambda x:x[:3]);memory=best[-1]
  if best[-2]=="merge":merges+=1
  assert len(memory)<=10 and all(len(packing.pack(*rec))==12 for rec in memory)
 return memory,merges
def measure(f):
 tracemalloc.start();start=time.process_time_ns()
 v=f();r={"cpu_ns":time.process_time_ns()-start,
         "peak_bytes":tracemalloc.get_traced_memory()[1]}
 tracemalloc.stop();return v,r
def main():
 f=json.loads((D/"20261019-yggdrasil-t10-preregister.json").read_text())
 assert f["parent_head"]=="b421b75e350465f77ffdbdf5406d5262513d4d94" and not f["authority"]["protected_original_first_use"]
 t5=load(D/"20261018-yggdrasil-t5-learning.py","yt10_t5")
 t4=load(t5.T4,"yt10_t4")
 t3=load(t5.T3,"yt10_t3");t2=t3.load(t3.T2,"yt10_t2")
 f62,kernel,_=t2.modules();t2.materialize_ephemeral_canonical_native_sources(f62)
 packing=f62.codec()
 training=[source(i) for i in TRAIN];open_cases=[source(i) for i in OPEN]
 examples=[]
 for stream,questions,answers,core in training:
  for x,event in zip(features(stream,kernel,packing),stream):
   examples.append((x,1 if event in core else -1))
 (weights,fit),tc=measure(lambda:kernel.fit_train_only(examples))
 assert len(weights)==20 and any(weights)
 outputs=[];records=0;native_merges=0
 for public,queries,answers,core in open_cases:
  (learned,merges),lc=measure(lambda:candidate(public,weights,packing))
  (untrained,_),zc=measure(lambda:candidate(public,bytes(20),packing))
  baseline,bc=measure(lambda:f62.controls()[0].online_fixed(public))
  old,oc=measure(lambda:t5.compact_online(public,weights,packing,t2,f62))
  predictions=[
   [t4.public_solver(records,q,packing) for q in queries]
   for records in (learned,untrained,baseline,old[0])]
  outputs.append({"learned_correct":sum(x==y for x,y in zip(predictions[0],answers)),
   "untrained_correct":sum(x==y for x,y in zip(predictions[1],answers)),
   "F60_correct":sum(x==y for x,y in zip(predictions[2],answers)),
   "T5_correct":sum(x==y for x,y in zip(predictions[3],answers)),
   "learned_retained_records":len(learned),"native_merges":merges,
   "learned_cost":lc,"untrained_cost":zc,"F60_cost":bc,"T5_cost":oc})
 result={"schema":"ygg.t10.queryblind-trainable-causal-retention.v1",
  "TRAIN_tasks":len(training),"OPEN_tasks":len(open_cases),
  "OPEN_questions_after_stream":len(open_cases)*4,
  "TRAIN_public_examples":len(examples),"learned_weights_nonzero":any(weights),
  "TRAIN_updates":fit.get("training_parameter_updates"),
  "learned_correct":sum(r["learned_correct"] for r in outputs),
  "zero_weight_correct":sum(r["untrained_correct"] for r in outputs),
  "frozen_F60_correct":sum(r["F60_correct"] for r in outputs),
  "T5_previous_correct":sum(r["T5_correct"] for r in outputs),
  "total_questions":len(open_cases)*4,
  "native_144B_persistent_hard_limit":True,
  "learned_train_CPU_peak":tc,
  "learned_total_online_CPU_ns":sum(r["learned_cost"]["cpu_ns"] for r in outputs),
  "frozen_F60_online_CPU_ns":sum(r["F60_cost"]["cpu_ns"] for r in outputs),
  "full_solver_and_training_amortization_parity_qualified":False,
  "original_protected_or_T8_FIRST_use_replayed":False,
  "scientific_acceptance":False,"rows":outputs}
 print(json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
