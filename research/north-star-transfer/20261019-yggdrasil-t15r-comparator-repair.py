"""T15R Ygg source reissue: repair ONLY the original comparator's 8-op
precondition so it handles the preregistered 6-hop questions. T15 learner,
source grammar, 144B native serialization, controls and science thresholds
are unchanged. Original failed cohort IDs are permanently consumed.
"""
from __future__ import annotations
import json,time,tracemalloc,sys,importlib.util
from pathlib import Path
D=Path(__file__).parent
def load(path,name):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def measured(f):
    tracemalloc.start();t=time.process_time_ns()
    try:return f(),{"cpu_ns":time.process_time_ns()-t,"python_peak_bytes":tracemalloc.get_traced_memory()[1]}
    finally:tracemalloc.stop()
def compatible_public_solver(records,question,packing):
    # Literal generalization of frozen T4 public_solver to 6-op prereg
    # source grammar. No private evaluator, source IDs or trained weights.
    assert len(records)<=12 and len(question["ops"])==6
    codes=tuple(2*r+int(d==-1) for r,d in question["ops"])
    oriented=set()
    for rec in records:
        oriented.add(rec);oriented.add(packing.mirrored(rec))
    states={0:{question["start"]}};scanned=0
    for step in range(6):
        for node in tuple(sorted(states.get(step,()))):
            for a,b,roles in sorted(oriented):
                scanned+=1
                assert scanned<=4096
                if a==node and step+len(roles)<=6 and roles==codes[step:step+len(roles)]:
                    states.setdefault(step+len(roles),set()).add(b)
                    assert sum(map(len,states.values()))<=512
    dest=states.get(6,set())
    return next(iter(dest)) if len(dest)==1 else None
def main():
    freeze=json.loads((D/"20261019-yggdrasil-t15r-comparator-repair-freeze.json").read_text())
    assert freeze["schema"]=="northstar.t15.yggdrasil.comparator-compatibility-reissue.v1"
    assert freeze["source"]["source_wrapper_blob"]=="f65831b3cde0733ac5eb6b784675a8df924c9144"
    source=load(D/"20261019-yggdrasil-t15r-source-reissue.py","y15r_source")
    learner=load(D/"20261019-yggdrasil-t15-mechanism.py","y15r_original_learner")
    t14=load(D/"20261019-yggdrasil-t14-mechanism.py","y15r_t14")
    t12=load(D/"20261019-yggdrasil-t12-mechanism.py","y15r_t12")
    t5=load(D/"20261018-yggdrasil-t5-learning.py","y15r_t5")
    t3=load(t5.T3,"y15r_t3");t2=t3.load(t3.T2,"y15r_t2")
    f62,_,_=t2.modules();t2.materialize_ephemeral_canonical_native_sources(f62)
    packing=f62.codec()
    (weights,updates),tcost=measured(lambda:learner.fit(source,t14))
    assert len(weights)==20 and updates>0
    cases=[]
    for seed in source.OPEN:
        public,questions,answers=source.birth(seed)
        (memory,diag),ccost=measured(lambda:learner.online(public,weights,t14))
        (zero,zdiag),zcost=measured(lambda:learner.online(public,(0,)*20,t14))
        (prior,pdiag),pcost=measured(lambda:t14.online(public,weights))
        (control,cdiag),bcost=measured(lambda:t12.frontier(public,packing))
        predict=lambda records:[t14.solve(records,q) for q in questions]
        cand,cs=measured(lambda:predict(memory))
        zerop,zs=measured(lambda:predict(zero))
        old,ps=measured(lambda:predict(prior))
        frozen,bs=measured(lambda:[compatible_public_solver(control,q,packing) for q in questions])
        score=lambda xs:sum(x==y for x,y in zip(xs,answers))
        regress=lambda xs:sum(x==y and z!=y for x,z,y in zip(xs,cand,answers))
        cases.append({"seed":seed,
            "candidate":score(cand),"zero_weight":score(zerop),
            "T14_online":score(old),"T12_native":score(frozen),
            "regressions_vs_zero":regress(zerop),
            "regressions_vs_T14":regress(old),
            "regressions_vs_T12":regress(frozen),
            "native":diag,"candidate_cpu_ns":ccost["cpu_ns"]+cs["cpu_ns"],
            "zero_cpu_ns":zcost["cpu_ns"]+zs["cpu_ns"],
            "T14_cpu_ns":pcost["cpu_ns"]+ps["cpu_ns"],
            "T12_cpu_ns":bcost["cpu_ns"]+bs["cpu_ns"],
            "candidate_python_peak":max(ccost["python_peak_bytes"],cs["python_peak_bytes"]),
            "zero_python_peak":max(zcost["python_peak_bytes"],zs["python_peak_bytes"]),
            "T14_python_peak":max(pcost["python_peak_bytes"],ps["python_peak_bytes"])})
    total=lambda name:sum(x[name] for x in cases)
    result={"schema":"yggdrasil.t15r.fresh-sixhop-comparator-compatible.v1",
        "TRAIN":len(source.TRAIN),"OPEN":len(source.OPEN),"late_questions":len(source.OPEN)*4,
        "original_failed_source_ids_replayed":False,
        "frozen_original_learner_git_blob":"9b9bcbb0ce5f42feaae86a52520141700e65f0a5",
        "new_source_wrapper_blob":freeze["source"]["source_wrapper_blob"],
        "train_updates":updates,"candidate_correct":total("candidate"),
        "zero_weight_correct":total("zero_weight"),"T14_correct":total("T14_online"),
        "T12_native_correct":total("T12_native"),
        "regressions_vs_zero":total("regressions_vs_zero"),
        "regressions_vs_T14":total("regressions_vs_T14"),
        "regressions_vs_T12":total("regressions_vs_T12"),
        "max_native_persistent_bytes":max(x["native"]["max_serialized_state_bytes"] for x in cases),
        "candidate_amortized_cpu_ns":total("candidate_cpu_ns")+tcost["cpu_ns"]//len(source.OPEN),
        "zero_cpu_ns":total("zero_cpu_ns"),"T14_cpu_ns":total("T14_cpu_ns"),
        "T12_cpu_ns":total("T12_cpu_ns"),
        "TRAIN_cpu_ns":tcost["cpu_ns"],
        "candidate_training_inclusive_python_peak":max(tcost["python_peak_bytes"],max(x["candidate_python_peak"] for x in cases)),
        "zero_peak":max(x["zero_python_peak"] for x in cases),
        "T14_python_peak":max(x["T14_python_peak"] for x in cases),
        "native_full_cpu_rss_parity":False,
        "independent_signed_source":False,
        "signed_scientific_acceptance":False,"optimizer_admission":False,"cases":cases}
    assert result["max_native_persistent_bytes"]<=144
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
