"""T7 Ygg independent PUBLIC-IDENTIFIABLE 72-edge causal source.

Source construction is independent of all T6 outcomes. Only source-
neutral -16000 fixture is instantiated in preflight. Prospective original
TRAIN/OPEN and independent replica are born only in original first use.
"""
from __future__ import annotations
import json,random,importlib.util,sys,time,tracemalloc
from pathlib import Path
HERE=Path(__file__).resolve().parent
FREEZE=HERE/"20261018-yggdrasil-t7-preregister.json"
T5=HERE/"20261018-yggdrasil-t5-learning.py"
T6=HERE/"20261018-yggdrasil-t6-audit.py"
FIXTURE=-16000
ORIGINAL=(-16001,-16002)
REPLICA=(-16003,-16004)
def need(ok,tag):
    if not ok:raise ValueError("YGG_T7_"+tag)
def load(path,name):
    sp=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(sp);sys.modules[sp.name]=m
    sp.loader.exec_module(m);return m
def born(seed,mode):
    if mode=="fixture":need(seed==FIXTURE,"ONLY_NONCONSUMING_FIXTURE")
    else:need(seed in ORIGINAL+REPLICA,"EXACT_PROSPECTIVE_OR_REPLICA")
    rng=random.Random((90283723 ^ (abs(seed)*37901))
                      if seed in REPLICA else 121219+abs(seed)*47309)
    nodes=[];used=set()
    def fresh():
        while True:
            n=rng.randrange(1,2147480000)
            if n not in used:
                used.add(n);return n
    for _ in range(4):
        nodes.append(tuple(fresh() for i in range(9)))
    roles=tuple((i%4,1) for i in range(8))
    edges=[]
    for lane in range(4):
        for i in range(8):
            # Public graph has 4 valid native corridors, one rooted in
            # publicly selected target 0. Model cannot inspect source lane.
            edges.append((nodes[lane][i],i%4,nodes[lane][i+1]))
    for i in range(8):
        from_lane=i%4;to_lane=1+(i%3)
        a=nodes[from_lane][i%8]
        b=nodes[to_lane][(i+2)%9]
        # If from_lane is target, deliberately give wrong next role, so
        # a cross-join cannot alter any complete target-role path.
        op=(i%4+1)%4
        edges.append((a,op,b))
    for i in range(32):
        if i<16:
            # Incoming noise TO target path nodes: never outgoing from
            # target when following positive-only public query edges.
            a=fresh();b=nodes[0][(i//2)%9]
            edges.append((a,rng.randrange(4),b))
        else:
            a=fresh();b=fresh()
            edges.append((a,rng.randrange(4),b))
    need(len(edges)==72 and len(set(edges))==72,"72_UNIQUE_PUBLIC_EVENTS")
    rng.shuffle(edges)
    evaluator={"start":nodes[0][0],
               "ops":roles,
               "answer":nodes[0][8],
               "private_source_lane":0,
               "source_id":seed}
    return tuple(edges),evaluator
def preflight():
    f=json.loads(FREEZE.read_text())
    need(f["schema"]=="northstar.t7.yggdrasil.preimplementation-prospective.v1"
         and f["source_parent_head"]=="14857917e7fc009eb5bcba3a111d290619b2789a",
         "FROZEN_BEFORE_SOURCE")
    t6=load(T6,"ygg_t7_preflight_audit")
    public,private=born(FIXTURE,"fixture")
    endpoints,diag=t6.fullgraph(public,private)
    need(len(endpoints)==1 and endpoints[0]==private["answer"]
         and len(public)==72,"INDEPENDENT_SOURCE_PUBLIC_UNIQUE_ANSWER")
    for bad in ORIGINAL+REPLICA+(-925,892001):
        try:born(bad,"fixture")
        except ValueError:pass
        else:raise AssertionError("prospective source consumed in preflight")
    return {"schema":"ygg.t7.preflight-unique-source.v1",
       "synthetic_fixture_source":FIXTURE,
       "source_public_complete_endpoints":endpoints,
       "source_public_examined":diag["examined"],
       "source_has_single_public_answer":True,
       "new_T7_prospective_source_constructed":0,
       "old_YNS_protected_consumed":0}
def measured(fn):
    tracemalloc.start();start=time.process_time_ns()
    val=fn();rec={"CPU_ns":time.process_time_ns()-start,
                  "Python_peak_bytes":tracemalloc.get_traced_memory()[1]}
    tracemalloc.stop();return val,rec
def evaluate_pair(trainid,testid,provider):
    t5,t3,t4,t2,f62,kernel,packing,t6=provider
    training,private_train=born(trainid,"original")
    path=t4.source_teacher_path(training,private_train)
    samples=[];recent=[]
    for i,event in enumerate(training):
        rec=packing.edge_record(event)
        features=kernel.public_features(recent,packing.pack(*rec),i)
        samples.append((features,1 if i in path else -1))
        recent=(recent+[rec])[-10:]
    (weights,_),traincost=measured(lambda:kernel.fit_train_only(samples))
    public,private=born(testid,"original")
    question={"start":private["start"],"ops":private["ops"]}
    # These values are provided AFTER both native retention processes.
    (memory,mstat),ccost=measured(lambda:t5.compact_online(public,weights,packing,t2,f62))
    old,bcost=measured(lambda:f62.controls()[0].online_fixed(public))
    cand,scost=measured(lambda:t4.public_solver(memory,question,packing))
    control,obcost=measured(lambda:t4.public_solver(old,question,packing))
    endpoints,graphcost=measured(lambda:t6.fullgraph(public,question))
    need(endpoints==[private["answer"]],"FIRST_USE_SOURCE_PUBLIC_IDENTIFIABILITY")
    candidate_cpu=ccost["CPU_ns"]+scost["CPU_ns"]+traincost["CPU_ns"]/32
    baseline_cpu=bcost["CPU_ns"]+obcost["CPU_ns"]
    candidate_peak=max(traincost["Python_peak_bytes"],ccost["Python_peak_bytes"],
                       scost["Python_peak_bytes"])
    baseline_peak=max(bcost["Python_peak_bytes"],obcost["Python_peak_bytes"])
    return {"source_ids":[trainid,testid],
         "full_graph_unique":True,
         "native_true_answer_recovered":cand==private["answer"],
         "F60_true_answer_recovered":control==private["answer"],
         "native_retained_records":len(memory),
         "sourceblind_F62_native_merges":mstat["true_native_F62_causal_compositions"],
         "candidate_train_amortized_cpu_ns":candidate_cpu,
         "original_F60_plus_solver_cpu_ns":baseline_cpu,
         "candidate_full_Python_peak_bytes":candidate_peak,
         "F60_full_Python_peak_bytes":baseline_peak,
         "CPU_nonincrease":candidate_cpu<=baseline_cpu,
         "peak_nonincrease":candidate_peak<=baseline_peak,
         "native_persistent_bytes":144,
         "true_private_answer_never_online":True}
def original():
    preflight()
    t5=load(T5,"ygg_t7_t5")
    t3=load(t5.T3,"ygg_t7_t3");t4=load(t5.T4,"ygg_t7_t4")
    t2=t3.load(t3.T2,"ygg_t7_t2")
    f62,kernel,src=t2.modules()
    t2.materialize_ephemeral_canonical_native_sources(f62)
    packing=f62.codec()
    t6=load(T6,"ygg_t7_t6")
    provider=(t5,t3,t4,t2,f62,kernel,packing,t6)
    first=evaluate_pair(*ORIGINAL,provider)
    eligible=(first["native_true_answer_recovered"]
              and first["CPU_nonincrease"] and first["peak_nonincrease"]
              and (not first["F60_true_answer_recovered"]))
    second=evaluate_pair(*REPLICA,provider) if eligible else None
    return {"schema":"ygg.t7.first-prospective-unique-public-causal.v1",
      "first":first,"first_eligible":eligible,"independent_replica":second,
      "replica_first_used":second is not None,
      "protected_original_YNS_used":0,"scientific_acceptance":False,
      "optimizer_promotion":False}
if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--mode",choices=("preflight","original"),default="preflight")
    z=p.parse_args()
    print(json.dumps(preflight() if z.mode=="preflight" else original(),sort_keys=True))
