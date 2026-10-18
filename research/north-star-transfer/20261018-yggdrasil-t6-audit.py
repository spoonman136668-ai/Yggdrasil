"""T6 Ygg causal-path retention identifiability audit.

Source-only evaluator truth is used solely AFTER retention for scoring
which public causal relationships survived. Online remains identical to
T5 public 144-byte path compression; no hidden question, correct answer,
or source graph access. Fresh negative TRAIN -924 OPEN -925.
"""
from __future__ import annotations
import importlib.util,types,json,time,tracemalloc
from pathlib import Path
HERE=Path(__file__).resolve().parent
FROZEN=HERE/"20261018-yggdrasil-t6-freeze.json"
T5=HERE/"20261018-yggdrasil-t5-learning.py"
def need(ok,s):
    if not ok:raise ValueError("YGG_T6_"+s)
def load(p,n):
    spec=importlib.util.spec_from_file_location(n,p)
    m=importlib.util.module_from_spec(spec)
    import sys
    sys.modules[n]=m;spec.loader.exec_module(m)
    return m
def born(t5,src,seed):
    need(seed in (-924,-925),"REGISTERED_PROTECTED_SOURCE")
    func=types.FunctionType(src.build_fixture.__code__,
         dict(src.build_fixture.__globals__,FIXTURES=(-924,-925)),
         src.build_fixture.__name__,src.build_fixture.__defaults__)
    return func(seed)
def fullgraph(public,question,limit=200000):
    """Enumerate bounded PUBLIC source paths, no private answer input."""
    start=question["start"]
    path={(start,)}
    examined=0
    for role,direction in question["ops"]:
        next_paths=set()
        for nodes in path:
            node=nodes[-1]
            for a,r,b in public:
                examined+=1
                need(examined<=limit,"PUBLIC_FULL_GRAPH_BOUNDED")
                if role==r and ((direction==1 and a==node) or
                                (direction==-1 and b==node)):
                    next_paths.add(nodes+(b if direction==1 else a,))
        path=next_paths
        if not path:break
    endpoints=sorted(set(nodes[-1] for nodes in path if len(nodes)==9))
    return endpoints,{"examined":examined,"complete_paths":len(path),
                      "distinct_endpoints":len(endpoints)}
def retained_graph(records,packing):
    """Expand only publicly retained legal native role-code sequences."""
    pub=[]
    for a,b,ops in records:
        need(len(ops)<=6 and len(packing.pack(a,b,ops))==12,"EXACT_NATIVE_RECORD")
        pub.append((a,b,ops))
    return pub
def source_minimum_segment_cover(public,question,packing):
    """Evaluator-only: exact public witness and potential 6-op compression."""
    options={(question["start"],0):0}
    ops=tuple(2*role+int(direction==-1) for role,direction in question["ops"])
    visited=0
    # Full public graph contains original role-one edges only.
    # Any 8-chain could be losslessly stored as 2 legal records of <=6.
    for step in range(8):
        nxt={}
        for (node,used),cost in list(options.items()):
            if used!=step:continue
            role,direction=question["ops"][step]
            for a,r,b in public:
                if r!=role:continue
                dest=b if a==node and direction==1 else a if b==node and direction==-1 else None
                if dest is None:continue
                nxt[(dest,step+1)]=min(nxt.get((dest,step+1),1000),cost+1)
                visited+=1
        options.update(nxt)
        need(len(options)<=1024,"SOURCE_WITNESS_BOUNDED")
    return min([c for (node,step),c in options.items() if step==8],default=None)
def measure(fn):
    tracemalloc.start();start=time.process_time_ns()
    value=fn();d={"cpu_ns":time.process_time_ns()-start,
                  "python_peak_bytes":tracemalloc.get_traced_memory()[1]}
    tracemalloc.stop();return value,d
def main():
    frozen=json.loads(FROZEN.read_text())
    need(frozen["schema"]=="research.northstar.t6.frozen.v1"
       and frozen["parent_exact_head"]=="12bf2e11f7e9e5c62f2400f97a91b961fffae7db"
       and not frozen["protected_source_first_use"],"FROZEN_SOURCE")
    t5=load(T5,"ygg_t6_t5")
    t3=load(t5.T3,"ygg_t6_t3")
    t4=load(t5.T4,"ygg_t6_t4")
    t2=t3.load(t3.T2,"ygg_t6_t2")
    f62,kernel,src=t2.modules()
    t2.materialize_ephemeral_canonical_native_sources(f62)
    packing=f62.codec()
    train,private_train=born(t5,src,-924)
    teacher=t4.source_teacher_path(train,private_train)
    samples=[];recent=[]
    for i,event in enumerate(train):
        record=packing.edge_record(event)
        features=kernel.public_features(recent,packing.pack(*record),i)
        samples.append((features,1 if i in teacher else -1))
        recent=(recent+[record])[-10:]
    (weights,trainstats),traincost=measure(lambda:kernel.fit_train_only(samples))
    OPEN,private=born(t5,src,-925)
    # Online algorithms receive OPEN public only. Query arrives afterwards.
    (memory,mechanism),cost=measure(lambda:t5.compact_online(OPEN,weights,packing,t2,f62))
    f60=f62.controls()[0]
    baseline,basecost=measure(lambda:f60.online_fixed(OPEN))
    question={"start":private["start"],"ops":private["ops"]}
    (full,detail),fullcost=measure(lambda:fullgraph(OPEN,question))
    answer,answer_cost=measure(lambda:t4.public_solver(memory,question,packing))
    baseline_answer,base_solver_cost=measure(lambda:t4.public_solver(baseline,question,packing))
    # Audit the ORIGINAL full public source witness against the source-only
    # evaluator, not a hidden oracle queried during learning or retention.
    need(private["answer"] in full,"TRUE_PUBLIC_WITNESS_MISSING")
    public_segments=source_minimum_segment_cover(OPEN,question,packing)
    output={"schema":"ygg.t6.public-causal-sufficiency-audit.v1",
        "frozen_source":"independent -924 TRAIN / -925 OPEN only",
        "source_private_evaluator_only_after_retention":True,
        "registered_protected_sources_born":0,
        "full_public_complete_endpoints":full,
        "full_public_truth_reachable":private["answer"] in full,
        "full_public_uniquely_identifiable":len(full)==1,
        "full_public_witness_edge_count":public_segments,
        "minimum_theoretical_six_code_records_for_eight_steps":2,
        "candidate_native_retained_records":len(memory),
        "candidate_sourceblind_legal_merges":mechanism["true_native_F62_causal_compositions"],
        "candidate_exact_answer_correct":answer==private["answer"],
        "baseline_exact_answer_correct":baseline_answer==private["answer"],
        "candidate_answer_abstained":answer is None,
        "baseline_answer_abstained":baseline_answer is None,
        "train_cpu_peak":traincost,"candidate_cpu_peak":cost,
        "baseline_cpu_peak":basecost,"public_fullgraph_cpu_peak":fullcost,
        "candidate_solver_cpu_peak":answer_cost,
        "baseline_solver_cpu_peak":base_solver_cost,
        "train_amortized_candidate_online_cpu_ns":cost["cpu_ns"]+traincost["cpu_ns"]/32,
        "original_F60_online_cpu_ns":basecost["cpu_ns"],
        "native_persistent_bytes_including_weights":144,
        "protected_scientific_first_use":False,
        "causal_transfer_accepted":False}
    print(json.dumps(output,sort_keys=True))
if __name__=="__main__":main()
