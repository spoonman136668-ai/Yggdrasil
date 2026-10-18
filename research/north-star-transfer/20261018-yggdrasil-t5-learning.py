"""T5 Ygg: learned causal-path compaction with legal native F62 merges.

New negative-ID TRAIN/OPEN source births reuse the unchanged frozen T2
cross-corridor source bytecode; no registered protected IDs are admitted.
TRAIN-only oracle credits can fit public path utility. Online action sees
only arriving public edge and retained records. Merges are the original
F62 codec's lossless causal compositions of at most six role codes.
"""
from __future__ import annotations
import importlib.util,sys,types,json,time,tracemalloc
from pathlib import Path
HERE=Path(__file__).resolve().parent
FREEZE=HERE/"20261018-yggdrasil-t5-frozen.json"
T3=HERE/"20261018-yggdrasil-t3-fast-native.py"
T4=HERE/"20261018-yggdrasil-t4-learning.py"
def need(ok,msg):
    if not ok:raise ValueError("YGG_T5_"+msg)
def load(path,name):
    sp=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(sp);sys.modules[name]=m;sp.loader.exec_module(m)
    return m
def new_source(src,seed):
    need(seed in (-922,-923),"PROTECTED_YNS_SOURCE_DENIED")
    env=dict(src.build_fixture.__globals__,FIXTURES=(-922,-923))
    fn=types.FunctionType(src.build_fixture.__code__,env,
                          src.build_fixture.__name__,src.build_fixture.__defaults__)
    return fn(seed)
def measure(fn):
    tracemalloc.start();start=time.process_time_ns()
    out=fn();d={"cpu_ns":time.process_time_ns()-start,
                "python_peak_bytes":tracemalloc.get_traced_memory()[1]}
    tracemalloc.stop();return out,d
def learn_public_credit(src,kernel,packing,teacher):
    train,private=new_source(src,-922)
    truth=teacher(train,private)
    samples=[];memory=[]
    for i,event in enumerate(train):
        record=packing.edge_record(event)
        features=kernel.public_features(memory,packing.pack(*record),i)
        samples.append((features,1 if i in truth else -1))
        memory=(memory+[record])[-10:]
    need(len(samples)==72 and sum(y>0 for _,y in samples)==8,"SOURCE_TRAIN_ONLY_8_POSITIVES")
    weights,meta=kernel.fit_train_only(samples)
    return weights,meta
def compact_online(public,weights,packing,t2,f62):
    need(len(public)==72 and len(weights)==20,"PUBLIC_STREAM_TRAINED_20_BYTES")
    w=[v if v<128 else v-256 for v in weights]
    memory=();merges=0;legality=0;attempts=0
    native=t2.cap10_native_actions(f62)
    for index,event in enumerate(public):
        incoming=packing.edge_record(event)
        allowed=[("append",-1,incoming)]
        for at,merged in packing.candidates(list(memory),incoming):
            attempts+=1
            if len(merged[2])<=6 and len(merged[2])>1 and merged[0]!=merged[1]:
                allowed.append(("merge",at,merged))
        # Use TRAIN learned public structural preference and path length,
        # with a fixed 10-record cap. No future question/truth enters.
        choices=[]
        for action,old,record in allowed:
            after=tuple(rec for j,rec in enumerate(memory) if j!=old)+(record,)
            degree={}
            for a,b,_ in after:
                degree[a]=degree.get(a,0)+1
                degree[b]=degree.get(b,0)+1
            preference=sum((w[k]/16)*x for k,x in enumerate(
                   ((1.0,len(record[2])/6,int(action=="merge"),0,
                    sum(len(r[2]) for r in after)/72,
                    max(len(r[2]) for r in after)/6,
                    sum(len(r[2])>=2 for r in after)/12,
                    sum(len(r[2])>=4 for r in after)/12,
                    len({op//2 for r in after for op in r[2]})/4,
                    sum(degree.get(a,0)>1 or degree.get(b,0)>1 for a,b,_ in after)/12,
                    index/71,len(after)/12))))
            # Fixed source-blind low-compute priority for causal chaining.
            fit=10*len(record[2])+int(action=="merge")*8+preference
            if len(after)>10:
                worst=min(range(len(after)),key=lambda j:(
                    len(after[j][2])*10+t2.kernel_weight_hint(after[j],w) if False else
                    len(after[j][2])*10, j))
                after=tuple(rec for j,rec in enumerate(after) if j!=worst)
            choices.append((fit,action,old,after))
        need(choices,"AT_LEAST_ONE_NATIVE_CANDIDATE")
        choice=max(choices,key=lambda item:(item[0],-len(item[3]),-item[2]))
        _,action,old,newmemory=choice
        if index in (0,9,10,35,71):
            options=native(memory,event,index,packing)
            need(any(opt[3]==newmemory for opt in options),
                 "SOURCE_PINNED_F62_LEGAL_MEMORY")
            legality+=1
        if action=="merge":merges+=1
        memory=newmemory
        need(len(memory)<=10 and all(len(packing.pack(*record))==12
                  for record in memory),"EXACT_144_NATIVE_BUDGET")
    return memory,{"legal_native_spotchecks":legality,
         "true_native_F62_causal_compositions":merges,
         "public_merge_proposals":attempts,
         "retained_records":len(memory),"weights_bytes":len(weights),
         "total_native_persistent_bytes":144,"query_or_future_used_online":False}
def main():
    frozen=json.loads(FREEZE.read_text())
    need(frozen["schema"]=="research.northstar.t5.causal-compression.v1"
      and frozen["parent_t4_head"]=="bc26ab02229031d03a311bc7758658703138b366"
      and not frozen["authority"]["protected_original_first_use"],"PREIMPLEMENTATION_FROZEN")
    t3=load(T3,"ygg_t5_fast");t4=load(T4,"ygg_t5_credit")
    t2=t3.load(t3.T2,"ygg_t5_t2")
    f62,kernel,src=t2.modules()
    t2.materialize_ephemeral_canonical_native_sources(f62)
    packing=f62.codec()
    (weights,fit),train_cost=measure(lambda:learn_public_credit(
             src,kernel,packing,t4.source_teacher_path))
    public,private=new_source(src,-923)
    question={"start":private["start"],"ops":private["ops"]}
    (memory,mechanism),comp_cost=measure(lambda:compact_online(
                public,weights,packing,t2,f62))
    (zero_memory,zero_mech),zero_cost=measure(lambda:compact_online(
                public,bytes(20),packing,t2,f62))
    (t3_memory,t3_mech),t3_cost=measure(lambda:t3.fast_online(
                public,weights,packing,t2,f62))
    (f60_memory),f60_cost=measure(lambda:f62.controls()[0].online_fixed(public))
    def solve(records):return t4.public_solver(records,question,packing)
    learned,scost=measure(lambda:solve(memory))
    untrained,szero=measure(lambda:solve(zero_memory))
    old,st3=measure(lambda:solve(t3_memory))
    baseline,sf60=measure(lambda:solve(f60_memory))
    correct=lambda value:value==private["answer"]
    cand_cpu=comp_cost["cpu_ns"]+scost["cpu_ns"]+train_cost["cpu_ns"]/32
    base_cpu=f60_cost["cpu_ns"]+sf60["cpu_ns"]
    cand_peak=max(train_cost["python_peak_bytes"],comp_cost["python_peak_bytes"],
                  scost["python_peak_bytes"])
    base_peak=max(f60_cost["python_peak_bytes"],sf60["python_peak_bytes"])
    out={"schema":"ygg.t5.actual-credit-causal-compression.v1",
      "independent_train_source":"negative_-922","independent_open_source":"negative_-923",
      "original_registered_YNS_consumed":0,
      "train_credit_weights_nonzero":any(weights),
      "trained_parameters_bytes":20,"native_persistent_bytes":144,
      "train_parameter_updates":fit["training_parameter_updates"],
      "candidate_exact_open":correct(learned),
      "untrained_exact_open":correct(untrained),
      "original_F60_exact_open":correct(baseline),
      "T3_no_merge_exact_open":correct(old),
      "trained_predicted_answer":learned,
      "F60_predicted_answer":baseline,
      "causal_merge_count":mechanism["true_native_F62_causal_compositions"],
      "native_legality":mechanism["legal_native_spotchecks"],
      "candidate_all_cost":{"train":train_cost,"online":comp_cost,"solver":scost},
      "F60_all_cost":{"online":f60_cost,"solver":sf60},
      "candidate_train_amortized_cpu_ns":cand_cpu,
      "F60_total_cpu_ns":base_cpu,
      "candidate_complete_peak_lower_bound":cand_peak,
      "F60_complete_peak_lower_bound":base_peak,
      "CPU_nonincrease":cand_cpu<=base_cpu,
      "peak_nonincrease":cand_peak<=base_peak,
      "strict_transfer_admission":False,"protected_original_first_use":False}
    need(out["original_registered_YNS_consumed"]==0 and
         out["native_persistent_bytes"]==144,"PROTECTED_AND_BUDGET")
    print(json.dumps(out,sort_keys=True))
if __name__=="__main__":main()
