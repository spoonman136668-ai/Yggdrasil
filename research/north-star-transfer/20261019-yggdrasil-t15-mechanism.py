"""T15 Yggdrasil: learned query-blind online path-fragment retention.
OPEN braided relation topology is novel to TRAIN and previous T14.
Only immutable 144B serialized memory is bounded; Python process heap is
separately reported and is NOT misrepresented as 144B whole-system memory.
"""
from __future__ import annotations
import json,sys,time,tracemalloc
from pathlib import Path
D=Path(__file__).parent
def load(file,name):
    import importlib.util
    s=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(s)
    sys.modules[name]=m;s.loader.exec_module(m);return m
def measured(fn):
    tracemalloc.start();t=time.process_time_ns()
    try:return fn(),{"cpu_ns":time.process_time_ns()-t,"python_peak_bytes":tracemalloc.get_traced_memory()[1]}
    finally:tracemalloc.stop()
def fit(src,t14):
    weights=[0]*20;updates=0
    for seed in src.TRAIN:
        events,questions,answers=src.birth(seed)
        credit=t14.credit_from_train(events,questions,answers)
        for a,r,b in events:
            feat=t14.feat((a,b,(r,)))
            label=1 if (a,r,b) in credit else -1
            if label*sum(w*f for w,f in zip(weights,feat))<=0:
                weights=[max(-127,min(127,w+label*f)) for w,f in zip(weights,feat)]
                updates+=1
    return tuple(weights),updates
def score(fragment,records,weights,t14):
    a,b,roles=fragment
    signed=sum(w*f for w,f in zip(weights,t14.feat(fragment)))
    neighbors=sum(int(a==v[1] or b==v[0]) for v in records if v!=fragment)
    return signed+24*(len(roles)-1)+6*min(neighbors,3)
def online(events,weights,t14):
    assert len(weights)==20
    records=[];peak=0;merge_count=0;evictions=0
    for event in events:
        a,r,b=event;entry=(a,b,(r,))
        assert t14.unpackfrag(t14.packfrag(entry))==entry
        while True:
            choices=[]
            for i,old in enumerate(records):
                x,y,path=old
                if len(path)+len(entry[2])>8:continue
                if y==entry[0]:
                    new=(x,entry[1],path+entry[2])
                    choices.append((score(new,records,weights,t14),i,new))
                if entry[1]==x:
                    new=(entry[0],y,entry[2]+path)
                    choices.append((score(new,records,weights,t14),i,new))
            if not choices:break
            _,which,entry=max(choices,key=lambda z:(z[0],-z[1]))
            records.pop(which);merge_count+=1
        records.append(entry)
        while sum(len(t14.packfrag(rec)) for rec in records)>120:
            which=min(range(len(records)),key=lambda i:(
                score(records[i],records,weights,t14),i))
            records.pop(which);evictions+=1
        used=24+sum(len(t14.packfrag(x)) for x in records)
        assert used<=144
        peak=max(peak,used)
    return tuple(records),{"max_serialized_state_bytes":peak,
      "edges_seen_once":len(events),"compositions":merge_count,"evictions":evictions}
def main():
    freeze=json.loads((D/"20261019-yggdrasil-t15-preimplementation-freeze.json").read_text())
    assert freeze["schema"]=="northstar.t15.yggdrasil.freeze.v1"
    assert freeze["source_blob"]=="dd9616e662bcedf1d15bc2318eb7cfdae9d93ad9"
    src=load(D/"20261019-yggdrasil-t15-source.py","y15src")
    t14=load(D/"20261019-yggdrasil-t14-mechanism.py","y15t14")
    t12=load(D/"20261019-yggdrasil-t12-mechanism.py","y15t12")
    t5=load(D/"20261018-yggdrasil-t5-learning.py","y15t5")
    t4=load(t5.T4,"y15t4")
    t3=load(t5.T3,"y15t3");t2=t3.load(t3.T2,"y15t2")
    f62,_,_=t2.modules();t2.materialize_ephemeral_canonical_native_sources(f62)
    packing=f62.codec()
    (weights,updates),tcost=measured(lambda:fit(src,t14))
    assert len(weights)==20 and updates>0
    metrics=[]
    for seed in src.OPEN:
        stream,questions,answers=src.birth(seed)
        (candidate,diag),ccost=measured(lambda:online(stream,weights,t14))
        (zero,zdiag),zcost=measured(lambda:online(stream,(0,)*20,t14))
        (prior,pdiag),pcost=measured(lambda:t14.online(stream,weights))
        (frozen,tdiag),bcost=measured(lambda:t12.frontier(stream,packing))
        calc=lambda m:[t14.solve(m,q) for q in questions]
        predicted,sc=measured(lambda:calc(candidate))
        zeropred,zs=measured(lambda:calc(zero))
        priorpred,ps=measured(lambda:calc(prior))
        freeze_pred,bs=measured(lambda:[t4.public_solver(frozen,q,packing) for q in questions])
        score=lambda results:sum(a==b for a,b in zip(results,answers))
        reg=lambda baseline:sum(a==b and z!=b for a,z,b in zip(baseline,predicted,answers))
        metrics.append({"seed":seed,"candidate_correct":score(predicted),
          "untrained_equal_format_correct":score(zeropred),
          "T14_online_correct":score(priorpred),"T12_online_correct":score(freeze_pred),
          "regressions_vs_equal_format":reg(zeropred),
          "regressions_vs_T14":reg(priorpred),
          "regressions_vs_T12":reg(freeze_pred),
          "native_state":diag,
          "candidate_cpu_ns":ccost["cpu_ns"]+sc["cpu_ns"],
          "T14_cpu_ns":pcost["cpu_ns"]+ps["cpu_ns"],
          "zero_cpu_ns":zcost["cpu_ns"]+zs["cpu_ns"],
          "T12_cpu_ns":bcost["cpu_ns"]+bs["cpu_ns"],
          "candidate_python_peak":max(ccost["python_peak_bytes"],sc["python_peak_bytes"]),
          "T14_python_peak":max(pcost["python_peak_bytes"],ps["python_peak_bytes"])})
    total=lambda name:sum(row[name] for row in metrics)
    result={"schema":"yggdrasil.t15.sourceonly-braided-graph.v1","TRAIN":len(src.TRAIN),
       "OPEN":len(src.OPEN),"late_queries":4*len(src.OPEN),
       "train_updates":updates,"candidate_correct":total("candidate_correct"),
       "same_format_zero_correct":total("untrained_equal_format_correct"),
       "T14_online_correct":total("T14_online_correct"),
       "T12_online_correct":total("T12_online_correct"),
       "baseline_correct_regressions":total("regressions_vs_equal_format")+total("regressions_vs_T14")+total("regressions_vs_T12"),
       "max_serialized_native_state_bytes":max(row["native_state"]["max_serialized_state_bytes"] for row in metrics),
       "amortized_candidate_CPU_ns":total("candidate_cpu_ns")+tcost["cpu_ns"]//len(src.OPEN),
       "T14_CPU_ns":total("T14_cpu_ns"),"zero_CPU_ns":total("zero_cpu_ns"),
       "candidate_peak_training_inclusive":max(tcost["python_peak_bytes"],max(row["candidate_python_peak"] for row in metrics)),
       "T14_python_peak":max(row["T14_python_peak"] for row in metrics),
       "complete_native_CPU_RSS_parity_authenticated":False,
       "independent_external_source_custody":False,
       "signed_scientific_acceptance":False,"optimizer_admission":False,
       "protected_cohort_used":False,"cases":metrics}
    assert result["max_serialized_native_state_bytes"]<=144
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
