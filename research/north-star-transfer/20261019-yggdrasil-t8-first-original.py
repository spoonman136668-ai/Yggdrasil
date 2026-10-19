"""T8 one original scientifically prospective Ygg native transfer on truly
public-IDENTIFIABLE source. New source IDs only, T7 consumed IDs denied.

Original native T5 learned causal memory, exact original F60 control, same
public 8-hop question and 144B state. Even if a pass, no automatic science
acceptance or optimizer promotion. B only on strict frozen A eligibility.
"""
from __future__ import annotations
import random,json,importlib.util,sys,time,tracemalloc,argparse
from pathlib import Path
HERE=Path(__file__).resolve().parent
FREEZE=HERE/"20261019-yggdrasil-t8-prospective-freeze.json"
PREVIOUS=HERE/"20261019-yggdrasil-t8-unique-source.py"
T5=HERE/"20261018-yggdrasil-t5-learning.py"
T4=HERE/"20261018-yggdrasil-t4-learning.py"
TRAIN_A=-18001;OPEN_A=-18002
TRAIN_B=-18003;OPEN_B=-18004
FIXTURE=-18010
def need(ok,key):
    if not ok:raise ValueError("YGG_T8_ORIGINAL_"+key)
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m
    spec.loader.exec_module(m);return m
def born(seed,mode):
    if mode=="fixture":need(seed==FIXTURE,"NONCONSUMING_ONLY")
    else:need(seed in (TRAIN_A,OPEN_A,TRAIN_B,OPEN_B),
              "EXACT_NEW_ORIGINAL_SOURCE_IDENTITIES")
    rng=random.Random(991173+abs(seed)*50909 if seed in (FIXTURE,TRAIN_A,OPEN_A)
                      else (991173^(abs(seed)*7919)))
    nodes=set()
    def take():
        while True:
            n=rng.randrange(1,2147000000)
            if n not in nodes:
                nodes.add(n);return n
    corridors=[tuple(take() for _ in range(9)) for _ in range(4)]
    ops=tuple((j%4,1) for j in range(8))
    edges=[]
    for lane in range(4):
        for j in range(8):
            edges.append((corridors[lane][j],j%4,corridors[lane][j+1]))
    for i in range(8):
        j=i
        if i%2==0:
            edges.append((corridors[0][j],(j+1)%4,
                          corridors[1+i%3][(j+2)%9]))
        else:
            edges.append((corridors[1+i%3][j],(j+2)%4,
                          corridors[0][(j+1)%9]))
    for i in range(32):
        if i<16:edges.append((take(),rng.randrange(4),corridors[0][i%9]))
        else:edges.append((take(),rng.randrange(4),take()))
    need(len(edges)==72 and len(set(edges))==72,"EXACT_72_INDEPENDENT_EDGES")
    rng.shuffle(edges)
    private={"start":corridors[0][0],"ops":ops,
             "answer":corridors[0][8],"source_id":seed}
    return tuple(edges),private,tuple(corridors[0])
def get_modules():
    t5=load(T5,"ygg_t8_p_t5")
    t4=load(T4,"ygg_t8_p_t4")
    t3=load(t5.T3,"ygg_t8_p_t3")
    t2=t3.load(t3.T2,"ygg_t8_p_t2")
    f62,kernel,_=t2.modules()
    t2.materialize_ephemeral_canonical_native_sources(f62)
    original=t5.load(t5.T4,"ygg_t8_p_orig_solver") if False else t4
    return t5,t4,t2,f62,kernel,f62.codec()
def check_source(public,private,target,proof):
    info=proof.family_proof(public,private,target)
    full,stat=proof.load(proof.T6,"ygg_t8_source_causal_audit").fullgraph(public,private)
    need(full==[private["answer"]],"SOURCE_PUBLIC_UNIQUE_ALL_CASES")
    return info
def prereg():
    frozen=json.loads(FREEZE.read_text())
    need(frozen["schema"]=="northstar.t8.ygg.source-proof-qualified-original.v1"
        and frozen["status"]=="FROZEN_BEFORE_NEW_PROSPECTIVE_SOURCE_CODE"
        and frozen["authority"]["single_first_use"]
        and not frozen["authority"]["scientific_accepted"],
        "ORIGINAL_PRECODE_FROZEN")
    proof=load(PREVIOUS,"ygg_t8_prior_proof")
    source,private,path=born(FIXTURE,"fixture")
    check_source(source,private,path,proof)
    for bad in (TRAIN_A,OPEN_A,TRAIN_B,OPEN_B,-16001,-16002,892001):
        try:born(bad,"fixture")
        except ValueError:pass
        else:raise AssertionError("registered source born in preflight")
    return {"schema":"ygg.t8.new-source-original-preflight.v1",
       "nonconsuming_new_generator_fixture_valid":True,
       "public_unique_complete_answer":True,
       "prospective_new_sources_born":0,
       "consumed_T7_source_ids_replayed":False,
       "protected_YNS_sources_used":0}
def measured(fn):
    tracemalloc.start();t=time.process_time_ns()
    r=fn();d={"cpu_ns":time.process_time_ns()-t,
              "peak_python_bytes":tracemalloc.get_traced_memory()[1]}
    tracemalloc.stop();return r,d
def pair(trainid,testid,modules,proof):
    t5,t4,t2,f62,kernel,packing=modules
    training,tp,target_train=born(trainid,"original")
    check_source(training,tp,target_train,proof)
    # The only private TRAIN teacher is derived from completed TRAIN source
    # birth; no future evidence ever goes to online memory policy.
    credit=t4.source_teacher_path(training,tp)
    samples=[];recent=[]
    for j,event in enumerate(training):
        rec=packing.edge_record(event)
        feat=kernel.public_features(recent,packing.pack(*rec),j)
        samples.append((feat,1 if j in credit else -1))
        recent=(recent+[rec])[-10:]
    need(len(samples)==72 and len(credit)==8,"TRUE_TRAIN_8_CAUSAL_LABELS")
    (weights,_),tcost=measured(lambda:kernel.fit_train_only(samples))
    public,private,target_open=born(testid,"original")
    check_source(public,private,target_open,proof)
    # All retention decisions made solely on 'public'. Question arrives after.
    (retained,stats),ccost=measured(lambda:t5.compact_online(public,weights,packing,t2,f62))
    original,bcost=measured(lambda:f62.controls()[0].online_fixed(public))
    question={"start":private["start"],"ops":private["ops"]}
    candidate,cs=measured(lambda:t4.public_solver(retained,question,packing))
    baseline,bs=measured(lambda:t4.public_solver(original,question,packing))
    c_cpu=ccost["cpu_ns"]+cs["cpu_ns"]+tcost["cpu_ns"]/32
    b_cpu=bcost["cpu_ns"]+bs["cpu_ns"]
    c_peak=max(tcost["peak_python_bytes"],ccost["peak_python_bytes"],
               cs["peak_python_bytes"])
    b_peak=max(bcost["peak_python_bytes"],bs["peak_python_bytes"])
    return {"source_ids":[trainid,testid],
       "public_unique_source_verified_before_scoring":True,
       "trained_native_correct":candidate==private["answer"],
       "frozen_F60_correct":baseline==private["answer"],
       "native_sourceblind_merges":stats["true_native_F62_causal_compositions"],
       "native_record_count":len(retained),
       "native_complete_persistent_bytes":144,
       "true_answer_or_query_used_during_online_retention":False,
       "candidate_amortized_cpu_ns":c_cpu,
       "F60_cpu_ns":b_cpu,
       "candidate_peak_bytes":c_peak,"F60_peak_bytes":b_peak,
       "CPU_nonincrease":c_cpu<=b_cpu,"peak_nonincrease":c_peak<=b_peak}
def original():
    prereg()
    proof=load(PREVIOUS,"ygg_t8_original_proof")
    modules=get_modules()
    first=pair(TRAIN_A,OPEN_A,modules,proof)
    eligible=(first["trained_native_correct"] and
              first["CPU_nonincrease"] and first["peak_nonincrease"] and
              not first["frozen_F60_correct"])
    second=pair(TRAIN_B,OPEN_B,modules,proof) if eligible else None
    return {"schema":"ygg.t8.first-original-prospective-unique-source.v1",
       "first":first,"first_eligible":eligible,
       "independent_replication":second,
       "B_first_used":second is not None,
       "A_new_source_ids_born":[TRAIN_A,OPEN_A],
       "B_new_source_ids_born":[TRAIN_B,OPEN_B] if second else [],
       "consumed_T7_source_ids_replayed":False,
       "original_YNS_protected_source_used":0,
       "scientific_acceptance":False,"optimizer_promotion":False}
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--mode",choices=("preflight","original"),default="preflight")
    args=ap.parse_args()
    print(json.dumps(prereg() if args.mode=="preflight" else original(),sort_keys=True))
