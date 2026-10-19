"""T11 Ygg: distinguish offline 144-byte REPRESENTABILITY from streaming
query-blind 144-byte LEARNABILITY. An offline public graph constructor is
not an admissible one-pass learner: retains all 72 public events transiently.
Original F62 native 12-byte codec; 4 x 8-hop paths into 8 records of
4 consecutive role codes, query known only AFTER retention.
"""
from __future__ import annotations
import types,json,sys,importlib.util,time,tracemalloc
from pathlib import Path
D=Path(__file__).parent
OPEN=range(-27103,-27099)
def load(p,n):
 sp=importlib.util.spec_from_file_location(n,p)
 m=importlib.util.module_from_spec(sp);sys.modules[n]=m;sp.loader.exec_module(m)
 return m
def measured(f):
 tracemalloc.start();start=time.process_time_ns()
 result=f();r={"cpu_ns":time.process_time_ns()-start,
                "Python_peak_bytes":tracemalloc.get_traced_memory()[1]}
 tracemalloc.stop();return result,r
def offline_graph_to_144bytes(public,packing):
 assert len(public)==72
 outgoing={};incoming={}
 for a,r,b in public:
  outgoing.setdefault(a,[]).append((r,b))
  incoming[b]=incoming.get(b,0)+1
 starts=sorted(a for a,options in outgoing.items() if incoming.get(a,0)==0)
 paths=[]
 for start in starts:
  node=start;edges=[];visited={node}
  for _ in range(8):
   possibilities=outgoing.get(node,[])
   if len(possibilities)!=1:break
   role,dest=possibilities[0]
   if dest in visited:break
   edges.append((node,role,dest))
   node=dest;visited.add(node)
  if len(edges)==8 and len(outgoing.get(node,[]))==0:
   paths.append(tuple(edges))
 assert len(paths)==4,"SOURCE_PUBLIC_COMPLETE_FOUR_EIGHT_HOP_PATHS"
 records=[]
 for edges in paths:
  for start in (0,4):
   chunk=edges[start:start+4]
   a=chunk[0][0];b=chunk[-1][2]
   ops=tuple(2*e[1] for e in chunk)
   rec=(a,b,ops)
   assert packing.unpack(packing.pack(*rec))==rec
   records.append(rec)
 assert len(records)==8 and sum(len(x[2]) for x in records)==32
 return tuple(records),{"offline_component_count":len(paths),
       "offline_native_records":len(records),
       "native_record_bytes":len(records)*12,
       "total_persistent_with_20B_weights_4B_counters":len(records)*12+20+4,
       "required_precompression_transient_graph_events":len(public),
       "offline_witness_not_online_admissible":True}
def main():
 f=json.loads((D/"20261019-yggdrasil-t11-freeze.json").read_text())
 assert f["schema"]=="northstar.t11.yggdrasil.preregister.v1" and f["parent_exact_head"]=="04a431c85b46c9b2d7515bf624585a0a19e08626"
 t10=load(D/"20261019-yggdrasil-t10-queryblind.py","ygg_t11_t10")
 globs=dict(t10.source.__globals__,TRAIN=range(-27050,-27042),OPEN=OPEN)
 source=types.FunctionType(t10.source.__code__,globs,t10.source.__name__,t10.source.__defaults__)
 t5=load(D/"20261018-yggdrasil-t5-learning.py","ygg_t11_t5")
 t4=load(t5.T4,"ygg_t11_t4")
 t3=load(t5.T3,"ygg_t11_t3")
 t2=t3.load(t3.T2,"ygg_t11_t2")
 f62,kernel,_=t2.modules();t2.materialize_ephemeral_canonical_native_sources(f62)
 packing=f62.codec();rows=[]
 for seed in OPEN:
  public,queries,answers,_source_tags=source(seed)
  (representation,receipt),offlinecost=measured(lambda:offline_graph_to_144bytes(public,packing))
  frozen,oldcost=measured(lambda:f62.controls()[0].online_fixed(public))
  (learned,merges),learncost=measured(lambda:t10.candidate(public,bytes(20),packing))
  def solve(mem):return [t4.public_solver(mem,q,packing) for q in queries]
  offlineanswers,sc=measured(lambda:solve(representation))
  oldanswers,os=measured(lambda:solve(frozen))
  onlineanswers,ls=measured(lambda:solve(learned))
  assert offlineanswers==list(answers),"PUBLIC_OFFLINE_CAPACITY_EXACT_FOUR_ANSWERS"
  rows.append({"source_id":seed,"offline_exact":sum(x==y for x,y in zip(offlineanswers,answers)),
   "original_F60_online_exact":sum(x==y for x,y in zip(oldanswers,answers)),
   "zero_weight_queryblind_online_exact":sum(x==y for x,y in zip(onlineanswers,answers)),
   "offline_native_record_count":receipt["offline_native_records"],
   "offline_persistent_bytes_including_weights":receipt["total_persistent_with_20B_weights_4B_counters"],
   "offline_transient_72_event_graph_read":True,
   "offline_compression_cpu_peak":offlinecost,
   "original_F60_online_cpu_peak":oldcost,
   "untrained_online_cpu_peak":learncost,
   "offline_solver_cpu_peak":sc,
   "original_F60_solver_cpu_peak":os})
 result={"schema":"ygg.t11.offline-causal-capacity-vs-queryblind-streamability.v1",
  "OPEN_source_neutral_cases":len(rows),"after_stream_questions":len(rows)*4,
  "four_causal_path_offline_native_segments_per_task":8,
  "native_offline_representation_bytes":96,
  "native_offline_total_persistent_budget_bytes":120,
  "original_144B_hard_capacity_respected_if_oracle_memory_available":True,
  "offline_exact":sum(x["offline_exact"] for x in rows),
  "frozen_F60_online_exact":sum(x["original_F60_online_exact"] for x in rows),
  "untrained_streaming_exact":sum(x["zero_weight_queryblind_online_exact"] for x in rows),
  "offline_full_graph_before_compression_violates_144B_streaming_comparison":True,
  "complete_equally_informed_online_cost_parity":False,
  "scientific_learned_transfer":False,
  "original_protected_or_consumed_T8_source_used":False,
  "science_accepted":False,"cases":rows}
 print(json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
