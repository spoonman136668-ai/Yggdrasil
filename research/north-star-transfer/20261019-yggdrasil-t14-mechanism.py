"""T14-B Ygg one-pass learned compact causal fragments, native-bound diagnostics.
Only TRAIN poststream public queries supervise score learning. OPEN late queries
are not passed to retention; full-graph reconstruction is not an online control.
"""
from __future__ import annotations
import json,sys,time,tracemalloc
from pathlib import Path
D=Path(__file__).parent
def load(path,name):
    import importlib.util
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module
def measured(fn):
    tracemalloc.start();t=time.process_time_ns()
    try:return fn(),{"cpu_ns":time.process_time_ns()-t,"python_peak_bytes":tracemalloc.get_traced_memory()[1]}
    finally:tracemalloc.stop()
def packfrag(f):
    a,b,ops=f
    assert 0<=a<1<<24 and 0<=b<1<<24 and 1<=len(ops)<=8
    assert all(0<=r<4 for r in ops)
    tail=sum(r<<(2*(i-1)) for i,r in enumerate(ops) if i)
    v=a.to_bytes(3,"big")+b.to_bytes(3,"big")+bytes(((len(ops)<<4)|(ops[0]<<2),))
    v+=tail.to_bytes((2*(len(ops)-1)+7)//8,"little")
    assert 7<=len(v)<=9
    return v
def unpackfrag(data):
    a=int.from_bytes(data[:3],"big");b=int.from_bytes(data[3:6],"big")
    size=data[6]>>4;first=(data[6]>>2)&3
    assert 1<=size<=8
    rest=int.from_bytes(data[7:],"little")
    ops=(first,)+tuple((rest>>(2*(i-1)))&3 for i in range(1,size))
    result=(a,b,ops);assert packfrag(result)==data
    return result
def feat(f):
    a,b,ops=f
    # Purely public, fixed 20 scalar features. Training cannot use OPEN labels.
    return (1,min(len(ops),8),int(len(ops)>1),int(len(ops)>3),
            *(int(ops[0]==j) for j in range(4)),
            int(a&1),int(b&1),int((a>>3)&1),int((b>>3)&1),
            int((a>>7)&1),int((b>>7)&1),int((a>>13)&1),
            int((b>>13)&1),int(a<b),int(a>b),int(a%3==b%3),int(len(ops)>5))
def credit_from_train(public,queries,answers):
    # After-stream TRAIN supervision reconstructed solely from TRAIN public edges
    # and the TRAIN questions. No generator truth-edge oracle is consulted.
    by_start={}
    for a,r,b in public:by_start.setdefault(a,[]).append((r,b))
    credited=set()
    for q,answer in zip(queries,answers):
        current=q["start"];chosen=[]
        for role,inv in q["ops"]:
            assert inv==1
            possible=[b for r,b in by_start.get(current,()) if r==role]
            if len(possible)!=1:break
            nxt=possible[0];chosen.append((current,role,nxt));current=nxt
        if current==answer and len(chosen)==len(q["ops"]):
            credited.update(chosen)
    return credited
def fit(src):
    weights=[0]*20;updates=0
    for seed in src.TRAIN:
        public,queries,answers,_=src.birth(seed)
        positives=credit_from_train(public,queries,answers)
        for a,r,b in public:
            x=feat((a,b,(r,)));y=1 if (a,r,b) in positives else -1
            if y*sum(v*w for v,w in zip(x,weights))<=0:
                weights=[max(-127,min(127,w+y*v)) for v,w in zip(x,weights)]
                updates+=1
    assert updates>0 and len(weights)==20
    return tuple(weights),updates
def online(public,weights):
    # Bounded serialized persistent state: <=120B fragment area +20B model +4B counter.
    memory=[];peak=0;merges=0;evictions=0
    for tick,(a,r,b) in enumerate(public):
        f=(a,b,(r,))
        assert packfrag(f) and unpackfrag(packfrag(f))==f
        while True:
            choices=[]
            for index,prev in enumerate(memory):
                x,y,ops=prev
                if len(ops)+len(f[2])>8:continue
                if y==f[0]:choices.append((len(ops)+len(f[2]),index,(x,f[1],ops+f[2])))
                if f[1]==x:choices.append((len(ops)+len(f[2]),index,(f[0],y,f[2]+ops)))
            if not choices:break
            _,i,f=max(choices,key=lambda z:(z[0],-z[1]))
            memory.pop(i);merges+=1
        memory.append(f)
        while sum(len(packfrag(v)) for v in memory)>120:
            victim=min(range(len(memory)),key=lambda i:(
                sum(w*x for w,x in zip(weights,feat(memory[i]))),i))
            memory.pop(victim);evictions+=1
        used=sum(len(packfrag(v)) for v in memory)+24
        assert used<=144
        peak=max(peak,used)
    return tuple(memory),{"max_persistent_bytes":peak,"evictions":evictions,
        "merges":merges,"events":len(public),"single_pass":True,
        "weights_bytes":20,"counter_bytes":4}
def solve(memory,q):
    options=[(q["start"],0)]
    seen=set()
    while options:
        node,n=options.pop()
        if n==len(q["ops"]):return node
        if (node,n) in seen:continue
        seen.add((node,n))
        for a,b,ops in memory:
            if a==node and tuple(x[0] for x in q["ops"][n:n+len(ops)])==ops:
                options.append((b,n+len(ops)))
    return None
def main():
    f=json.loads((D/"20261019-yggdrasil-t14-complete-source-and-assay-freeze.json").read_text())
    assert f["source_blob"]=="848149ac9752c7d9fa11a4429d985905a45953a1"
    src=load(D/"20261019-yggdrasil-t14-source.py","y_t14_source")
    t12=load(D/"20261019-yggdrasil-t12-mechanism.py","y_t14_frozen_T12")
    t5=load(D/"20261018-yggdrasil-t5-learning.py","y_t14_t5")
    t4=load(t5.T4,"y_t14_t4")
    t3=load(t5.T3,"y_t14_t3");t2=t3.load(t3.T2,"y_t14_t2")
    f62,_,_=t2.modules();t2.materialize_ephemeral_canonical_native_sources(f62)
    packing=f62.codec()
    (weights,updates),tcost=measured(lambda:fit(src))
    assert all(-127<=v<=127 for v in weights)
    records=[]
    for seed in src.OPEN:
        public,queries,answers,_=src.birth(seed)
        (memory,diag),ccost=measured(lambda:online(public,weights))
        (zero,zdiag),zcost=measured(lambda:online(public,(0,)*20))
        (t12memory,t12diag),t12cost=measured(lambda:t12.frontier(public,packing))
        frozen,fcost=measured(lambda:f62.controls()[0].online_fixed(public))
        pred,scost=measured(lambda:[solve(memory,q) for q in queries])
        zpred,zsc=measured(lambda:[solve(zero,q) for q in queries])
        p12,p12sc=measured(lambda:[t4.public_solver(t12memory,q,packing) for q in queries])
        p60,p60sc=measured(lambda:[t4.public_solver(frozen,q,packing) for q in queries])
        score=lambda v:sum(a==b for a,b in zip(v,answers))
        records.append({"seed":seed,"candidate":score(pred),"zero_weight_control":score(zpred),
          "T12":score(p12),"F60":score(p60),"native_state":diag,
          "candidate_cpu":ccost["cpu_ns"]+scost["cpu_ns"],
          "zero_cpu":zcost["cpu_ns"]+zsc["cpu_ns"],
          "T12_cpu":t12cost["cpu_ns"]+p12sc["cpu_ns"],
          "F60_cpu":fcost["cpu_ns"]+p60sc["cpu_ns"],
          "candidate_python_peak":max(ccost["python_peak_bytes"],scost["python_peak_bytes"]),
          "zero_python_peak":max(zcost["python_peak_bytes"],zsc["python_peak_bytes"])})
    total=lambda key:sum(v[key] for v in records)
    out={"schema":"yggdrasil.t14.original-sourceonly-diagnostic.v1","TRAIN":len(src.TRAIN),
      "OPEN":len(src.OPEN),"late_queries":len(src.OPEN)*4,
      "TRAIN_updates":updates,"candidate_correct":total("candidate"),
      "strong_equal_format_zero_correct":total("zero_weight_control"),
      "T12_online_correct":total("T12"),"F60_online_correct":total("F60"),
      "no_regressions_vs_equal_format":all(r["candidate"]>=r["zero_weight_control"] for r in records),
      "maximum_persistent_state_bytes":max(r["native_state"]["max_persistent_bytes"] for r in records),
      "candidate_amortized_CPU_ns":total("candidate_cpu")+tcost["cpu_ns"]//len(src.OPEN),
      "zero_control_CPU_ns":total("zero_cpu"),"TRAIN_CPU_ns":tcost["cpu_ns"],
      "candidate_python_peak_including_train":max(tcost["python_peak_bytes"],max(r["candidate_python_peak"] for r in records)),
      "zero_control_python_peak":max(r["zero_python_peak"] for r in records),
      "actual_python_heap_fits_144_bytes":False,
      "independent_topology_replication":False,"signed_scientific_acceptance":False,
      "optimizer_admission":False,"cases":records}
    assert out["maximum_persistent_state_bytes"]<=144
    print(json.dumps(out,sort_keys=True))
if __name__=="__main__":main()
