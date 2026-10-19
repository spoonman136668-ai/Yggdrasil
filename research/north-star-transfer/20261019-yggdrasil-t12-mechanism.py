"""T12 Ygg one-pass query-BLIND causal frontier under exact 144B.

No prior full graph is stored or revisited. Each of 72 public edges arrives
once. Legal native F62 packed records are at most 6 causal codes, with at
most ten records + 20B public TRAIN-only coefficients + 4B counters.
New source-neutral source identities; all four questions are late.
"""
from __future__ import annotations
import types,json,time,tracemalloc,sys,importlib.util
from pathlib import Path
D=Path(__file__).parent
OPEN=range(-31103,-31099)
def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s)
 sys.modules[n]=m;s.loader.exec_module(m);return m
def measured(f):
 tracemalloc.start();t=time.process_time_ns();v=f()
 d={"cpu_ns":time.process_time_ns()-t,
    "Python_peak_bytes":tracemalloc.get_traced_memory()[1]}
 tracemalloc.stop();return v,d
def merge(packing,left,right):
 # Reuse exact native legal F62 composition; no private source truth.
 options=packing.candidates([left],right)
 return [new for i,new in options if i==0 and 2<=len(new[2])<=6
         and new[0]!=new[1]]
def frontier(public,packing):
 memory=[];counter=0;compositions=0;drops=0;maxrecords=0
 for event in public:
  curr=packing.edge_record(event)
  while True:
   proposals=[]
   for pos,existing in enumerate(memory):
    if existing[1]==curr[0]:
     proposals.extend((len(x[2]),pos,x) for x in merge(packing,existing,curr))
    if curr[1]==existing[0]:
     proposals.extend((len(x[2]),pos,x) for x in merge(packing,curr,existing))
   if not proposals:break
   _,pos,curr=max(proposals,key=lambda x:(x[0],-x[1]))
   memory.pop(pos);compositions+=1
  memory.append(curr)
  if len(memory)>10:
   # The sourceblind bounded memory chooses to retain composed
   # relationships over fresh singletons. May drop true path material.
   victim=min(range(len(memory)),key=lambda j:(len(memory[j][2]),j))
   memory.pop(victim);drops+=1
  maxrecords=max(maxrecords,len(memory));counter+=1
  assert len(memory)<=10 and all(len(packing.pack(*r))==12 for r in memory)
 assert counter==72
 return tuple(memory),{"sourceblind_native_merges":compositions,
   "online_evicted_records":drops,"max_native_records":maxrecords,
   "persistent_state_bytes":10*12+20+4,"one_pass_public_edges":counter}
def main():
 f=json.loads((D/"20261019-yggdrasil-t12-freeze.json").read_text())
 assert f["schema"]=="northstar.t12.yggdrasil.frozen-preimplementation.v1" and f["parent_exact_head"]=="6c1cc0a8ee0a0c356213906893dc76c31c00926f"
 t10=load(D/"20261019-yggdrasil-t10-queryblind.py","ygg_t12_t10")
 t11=load(D/"20261019-yggdrasil-t11-mechanism.py","ygg_t12_t11")
 t5=load(D/"20261018-yggdrasil-t5-learning.py","ygg_t12_t5")
 t4=load(t5.T4,"ygg_t12_t4")
 t3=load(t5.T3,"ygg_t12_t3");t2=t3.load(t3.T2,"ygg_t12_t2")
 f62,kernel,_=t2.modules();t2.materialize_ephemeral_canonical_native_sources(f62)
 packing=f62.codec()
 source=types.FunctionType(t10.source.__code__,dict(t10.source.__globals__,TRAIN=range(-31050,-31042),OPEN=OPEN),t10.source.__name__,t10.source.__defaults__)
 cases=[source(i) for i in OPEN]
 rows=[]
 for index,(stream,questions,answers,source_truth) in enumerate(cases):
  (mine,diag),minecost=measured(lambda:frontier(stream,packing))
  frozen,fcost=measured(lambda:f62.controls()[0].online_fixed(stream))
  (previous,oldmerges),oldcost=measured(lambda:t10.candidate(stream,bytes(20),packing))
  # Offline is reported as explicitly UNQUALIFIED representational ceiling.
  offline,meta=t11.offline_graph_to_144bytes(stream,packing)
  def solve(mem):return [t4.public_solver(mem,q,packing) for q in questions]
  ans,sc=measured(lambda:solve(mine))
  baseline,bc=measured(lambda:solve(frozen))
  old,oc=measured(lambda:solve(previous))
  offline_ans,offc=measured(lambda:solve(offline))
  assert offline_ans==list(answers)
  rows.append({"source_id":OPEN[index],
   "streaming_correct":sum(a==b for a,b in zip(ans,answers)),
   "frozen_F60_correct":sum(a==b for a,b in zip(baseline,answers)),
   "previous_T10_online_correct":sum(a==b for a,b in zip(old,answers)),
   "offline_not_admissible_correct":sum(a==b for a,b in zip(offline_ans,answers)),
   "native_streaming_receipt":diag,"candidate_CPU_peak":minecost,
   "frozen_F60_CPU_peak":fcost,"previous_T10_CPU_peak":oldcost,
   "streaming_solver_CPU_peak":sc,"F60_solver_CPU_peak":bc})
 out={"schema":"ygg.t12.onepass-144byte-native-causal-frontier.v1",
  "OPEN_cases":len(cases),"late_query_count":len(cases)*4,
  "query_known_during_online":False,
  "native_persistent_bytes":144,"source_events_per_case":72,
  "online_candidate_correct":sum(z["streaming_correct"] for z in rows),
  "frozen_F60_correct":sum(z["frozen_F60_correct"] for z in rows),
  "unchanged_T10_correct":sum(z["previous_T10_online_correct"] for z in rows),
  "ineligible_offline_fullgraph_correct":sum(z["offline_not_admissible_correct"] for z in rows),
  "onepass_native_total_merges":sum(z["native_streaming_receipt"]["sourceblind_native_merges"] for z in rows),
  "onepass_evicted_records":sum(z["native_streaming_receipt"]["online_evicted_records"] for z in rows),
  "complete_cost_parity_qualified":False,
  "learned_weight_updates":0,"independent_learned_transfer":False,
  "original_protected_or_consumed_T8_used":False,"science_accepted":False,
  "cases":rows}
 print(json.dumps(out,sort_keys=True))
if __name__=="__main__":main()
