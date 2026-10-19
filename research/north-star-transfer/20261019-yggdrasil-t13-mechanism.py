"""T13 Ygg: 144B one-pass F62-record adversarial-prefix LOWER BOUND.

Exactly 16 publicly unrelated even-position causal edges arrive before
their connecting odd-position edges, among four unknown 8-hop corridors.
Each F62 record stores one contiguous path, so retaining every potential
late-question witness at that prefix needs 16 distinct native 12B slots.
Only ten 12B slots exist in 144B after 20B coefficients and 4B counters.
The bound concerns THIS native representation, not all conceivable
144-byte alternative encodings. No entire graph is used by online policy.
"""
from __future__ import annotations
import random,json,sys,importlib.util,time,tracemalloc
from pathlib import Path
HERE=Path(__file__).parent
SEED=-35000
def load(p,n):
 s=importlib.util.spec_from_file_location(n,p)
 m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def measured(fn):
 tracemalloc.start();t=time.process_time_ns();v=fn()
 d={"cpu_ns":time.process_time_ns()-t,
 "Python_peak_bytes":tracemalloc.get_traced_memory()[1]}
 tracemalloc.stop();return v,d
def born(seed):
 assert seed==SEED
 rng=random.Random(792311+abs(seed)*733);taken=set()
 def node():
  while True:
   x=rng.randrange(1000,1400000000)
   if x not in taken:taken.add(x);return x
 paths=[tuple(node() for j in range(9)) for i in range(4)]
 core=[[ (nodes[j],j%4,nodes[j+1]) for j in range(8)] for nodes in paths]
 prefix=[core[lane][idx] for lane in range(4) for idx in (0,2,4,6)]
 rest=[core[lane][idx] for lane in range(4) for idx in (1,3,5,7)]
 noise=[(node(),rng.randrange(4),node()) for _ in range(40)]
 rng.shuffle(rest);rng.shuffle(noise)
 public=tuple(prefix+rest+noise)
 queries=tuple({"start":p[0],"ops":tuple((j%4,1) for j in range(8))} for p in paths)
 answers=tuple(p[8] for p in paths)
 assert len(public)==72 and len(set(public))==72 and len(prefix)==16
 return public,queries,answers,tuple(prefix)
def lower_bound(prefix,packing):
 records=[packing.edge_record(x) for x in prefix]
 assert len(records)==16
 assert all(packing.unpack(packing.pack(*r))==r for r in records)
 public_nodes=[{a,b} for a,r,b in prefix]
 assert all(not (u&v) for i,u in enumerate(public_nodes)
            for v in public_nodes[i+1:])
 legal_pair_compositions=0
 for i,a in enumerate(records):
  for j,b in enumerate(records):
   if i==j:continue
   legal_pair_compositions+=sum(2<=len(merged[2])<=6
                   for k,merged in packing.candidates([a],b))
 assert legal_pair_compositions==0
 return {"prefix_native_segments":16,"all_prefix_segments_pairwise_disjoint":True,
  "native_pairwise_compositions_possible":0,
  "minimum_12B_native_record_bytes":16*12,
  "with_frozen_20B_weights_and_4B_counters":16*12+20+4,
  "available_native_record_slots":10,
  "extra_native_record_slots_required":6,
  "native_record_prefix_capacity_fail":True,
  "claim_scope":"original F62 lossless contiguous 12-byte path-record representation; not any arbitrary compressed algorithm"}
def main():
 f=json.loads((HERE/"20261019-yggdrasil-t13-freeze.json").read_text())
 assert f["schema"]=="northstar.t13.yggdrasil.preimplementation-freeze.v1"
 assert f["science_head_parent"]=="1b059853dc1e245f15d528485b94493243cf8f80"
 assert not f["safety"]["protected_science_first_use"]
 t12=load(HERE/"20261019-yggdrasil-t12-mechanism.py","ygg_t13_t12")
 t11=load(HERE/"20261019-yggdrasil-t11-mechanism.py","ygg_t13_t11")
 t5=load(HERE/"20261018-yggdrasil-t5-learning.py","ygg_t13_t5")
 t4=load(t5.T4,"ygg_t13_t4")
 t3=load(t5.T3,"ygg_t13_t3");t2=t3.load(t3.T2,"ygg_t13_t2")
 f62,kernel,_=t2.modules();t2.materialize_ephemeral_canonical_native_sources(f62)
 packing=f62.codec()
 stream,queries,answers,prefix=born(SEED)
 proof=lower_bound(prefix,packing)
 (native,diag),online_cost=measured(lambda:t12.frontier(stream,packing))
 (frozen),F60cost=measured(lambda:f62.controls()[0].online_fixed(stream))
 (offline,offline_meta),offlinecost=measured(lambda:t11.offline_graph_to_144bytes(stream,packing))
 def solve(memory):return [t4.public_solver(memory,q,packing) for q in queries]
 predicted,sc=measured(lambda:solve(native))
 baseline,bc=measured(lambda:solve(frozen))
 independent,ic=measured(lambda:solve(offline))
 assert tuple(independent)==answers
 result={"schema":"ygg.t13.native-adversarial-prefix-capacity-certificate.v1",
   "synthetic_original_fixture":SEED,"public_stream_events":len(stream),
   "public_query_arrival":"after all 72 public events",
   "prefix":proof,
   "candidate_onepass_correct":sum(a==b for a,b in zip(predicted,answers)),
   "F60_onepass_correct":sum(a==b for a,b in zip(baseline,answers)),
   "ineligible_full_public_offline_correct":sum(a==b for a,b in zip(independent,answers)),
   "candidate_native_streaming":diag,"candidate_online_cost":online_cost,
   "F60_online_cost":F60cost,"offline_noncompetitive_cost":offlinecost,
   "native_persistent_budget_bytes":144,
   "claim_not_a_general_144byte_information_theoretic_bound":True,
   "first_use_protected_or_consumed_source_used":False,
   "new_learned_representation_qualified":False,
   "scientific_transfer_accepted":False}
 print(json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
