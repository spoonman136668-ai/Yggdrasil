"""T16 Ygg: non-destructive source-blind causal component memory.
Keeps both primitive and at most two forward-composable fragments until
144B packed-state capacity forces a public-only eviction. TRAIN credit is
poststream TRAIN-only. Original OPEN questions never affect retention.
"""
from __future__ import annotations
import sys,importlib.util,time,tracemalloc,json
from pathlib import Path
D=Path(__file__).parent
def load(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s)
    sys.modules[name]=m;s.loader.exec_module(m);return m
def measure(f):
    tracemalloc.start();tick=time.process_time_ns()
    try:return f(),{"cpu_ns":time.process_time_ns()-tick,"python_peak_bytes":tracemalloc.get_traced_memory()[1]}
    finally:tracemalloc.stop()
def value(rec,records,weights,t14):
    a,b,ops=rec
    # Structural ability to compose independent of target/query truth.
    out_degree=sum(z[0]==b for z in records if z!=rec)
    in_degree=sum(z[1]==a for z in records if z!=rec)
    learned=sum(w*f for w,f in zip(weights,t14.feat(rec)))
    return 28*len(ops)+2*min(3,in_degree+out_degree)+learned
def memory(stream,weights,t14):
    assert len(weights)==20
    pool=[];max_used=24;merges=0;drops=0
    for tick,(a,role,b) in enumerate(stream):
        primitive=(a,b,(role,))
        proposals=[primitive]
        # Non-destructive local composed hypotheses. A candidate path is
        # grounded exclusively in public causal events, never graph oracle.
        for old in pool:
            x,y,ops=old
            if len(ops)>=8:continue
            if y==a:proposals.append((x,b,ops+(role,)))
            if b==x:proposals.append((a,y,(role,)+ops))
        pool.extend(proposals)
        pool=list(dict.fromkeys(pool))
        while sum(len(t14.packfrag(rec)) for rec in pool)>120:
            victim=min(range(len(pool)),key=lambda i:(
                value(pool[i],pool,weights,t14),i))
            pool.pop(victim);drops+=1
        used=24+sum(len(t14.packfrag(rec)) for rec in pool)
        assert used<=144
        max_used=max(used,max_used);merges+=len(proposals)-1
    return tuple(pool),{"serial_state_bytes":max_used,"events_seen":len(stream),
        "composed_public_hypotheses":merges,"evicted":drops,"single_pass":True}
def solve(records,question):
    # All public grounded routes; never report an arbitrary first-match.
    roles=tuple(x[0] for x in question["ops"])
    assert len(roles)==6
    todo={(0,question["start"])}
    for step in range(len(roles)):
        extensions=set(todo)
        for pos,node in tuple(todo):
            if pos!=step:continue
            for a,b,ops in records:
                if a==node and roles[pos:pos+len(ops)]==ops:
                    if pos+len(ops)<=6:extensions.add((pos+len(ops),b))
        todo=extensions
    result={node for pos,node in todo if pos==6}
    return next(iter(result)) if len(result)==1 else None
def main():
    pre=json.loads((D/"20261019-yggdrasil-t16-freeze.json").read_text())
    assert pre["source_blob"]=="57b489c3f6a5bb6118423a256b70523b48bbf439"
    src=load(D/"20261019-yggdrasil-t16-source.py","y16_src")
    t14=load(D/"20261019-yggdrasil-t14-mechanism.py","y16_t14")
    t15=load(D/"20261019-yggdrasil-t15-mechanism.py","y16_t15")
    t15r=load(D/"20261019-yggdrasil-t15r-comparator-repair.py","y16_t15r")
    t12=load(D/"20261019-yggdrasil-t12-mechanism.py","y16_t12")
    t5=load(D/"20261018-yggdrasil-t5-learning.py","y16_t5")
    t3=load(t5.T3,"y16_t3");t2=t3.load(t3.T2,"y16_t2")
    f62,_,_=t2.modules();t2.materialize_ephemeral_canonical_native_sources(f62)
    packing=f62.codec()
    (weights,updates),traincost=measure(lambda:t15.fit(src,t14))
    assert len(weights)==20 and updates>0
    rows=[]
    for seed in src.OPEN:
        stream,questions,answers=src.birth(seed)
        (cand,cs),cm=measure(lambda:memory(stream,weights,t14))
        (zero,zs),zm=measure(lambda:memory(stream,(0,)*20,t14))
        (prior,ps),pm=measure(lambda:t15.online(stream,weights,t14))
        (baseline,bs),bm=measure(lambda:t12.frontier(stream,packing))
        ans,ac=measure(lambda:[solve(cand,q) for q in questions])
        zans,zc=measure(lambda:[solve(zero,q) for q in questions])
        pans,pc=measure(lambda:[solve(prior,q) for q in questions])
        bans,bc=measure(lambda:[t15r.compatible_public_solver(baseline,q,packing) for q in questions])
        score=lambda a:sum(x==y for x,y in zip(a,answers))
        losses=lambda baseline:sum(x==y and z!=y for x,z,y in zip(baseline,ans,answers))
        hard_false=sum(z is not None and z!=y for z,y in zip(ans,answers))
        rows.append({"seed":seed,"candidate":score(ans),"zero":score(zans),
          "T15":score(pans),"T12":score(bans),
          "regressions_vs_zero":losses(zans),
          "regressions_vs_T15":losses(pans),
          "regressions_vs_T12":losses(bans),"hard_false_positives":hard_false,
          "state":cs,
          "candidate_cpu_ns":cm["cpu_ns"]+ac["cpu_ns"],
          "zero_cpu_ns":zm["cpu_ns"]+zc["cpu_ns"],
          "T15_cpu_ns":pm["cpu_ns"]+pc["cpu_ns"],
          "T12_cpu_ns":bm["cpu_ns"]+bc["cpu_ns"],
          "candidate_peak":max(cm["python_peak_bytes"],ac["python_peak_bytes"]),
          "zero_peak":max(zm["python_peak_bytes"],zc["python_peak_bytes"])})
    total=lambda key:sum(v[key] for v in rows)
    out={"schema":"yggdrasil.t16.sourceblind-component-retention.v1",
       "TRAIN":len(src.TRAIN),"OPEN":len(src.OPEN),"late_questions":4*len(src.OPEN),
       "train_updates":updates,"candidate_correct":total("candidate"),
       "zero_learned_weight_correct":total("zero"),
       "frozen_T15_correct":total("T15"),"frozen_T12_correct":total("T12"),
       "hard_false_positives":total("hard_false_positives"),
       "baseline_correct_regressions":total("regressions_vs_zero")+total("regressions_vs_T15")+total("regressions_vs_T12"),
       "max_serialized_native_bytes":max(x["state"]["serial_state_bytes"] for x in rows),
       "candidate_training_amortized_CPU_ns":total("candidate_cpu_ns")+traincost["cpu_ns"]//len(src.OPEN),
       "zero_control_CPU_ns":total("zero_cpu_ns"),"T15_CPU_ns":total("T15_cpu_ns"),
       "T12_CPU_ns":total("T12_cpu_ns"),"TRAIN_CPU_ns":traincost["cpu_ns"],
       "candidate_train_inclusive_Python_peak_bytes":max(traincost["python_peak_bytes"],max(r["candidate_peak"] for r in rows)),
       "zero_control_peak_bytes":max(r["zero_peak"] for r in rows),
       "full_native_CPU_RSS_parity_qualified":False,
       "independent_replication_qualified":False,"signed_science_acceptance":False,
       "optimizer_admission":False,"cases":rows}
    assert out["max_serialized_native_bytes"]<=144
    print(json.dumps(out,sort_keys=True))
if __name__=="__main__":main()
