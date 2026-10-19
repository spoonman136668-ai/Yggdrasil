"""T9 Ygg: causal sufficiency of public early-query + chronological evidence.

New TASK REGIME, source-neutral fixture only: question delivered BEFORE
public stream, target-corridor evidence arrives in causal order interleaved
with independent irrelevant edges. This removes the query-blind memory
information bottleneck but changes the scientific task: compare to SAME
INFORMATION query-aware exact control, not claim learned breakthrough.
"""
from __future__ import annotations
import json,random,importlib.util,sys,time,tracemalloc
from pathlib import Path
HERE=Path(__file__).resolve().parent
FREEZE=HERE/"20261019-yggdrasil-t9-source-freeze.json"
T5=HERE/"20261018-yggdrasil-t5-learning.py"
T4=HERE/"20261018-yggdrasil-t4-learning.py"
def need(ok,tag):
    if not ok:raise ValueError("YGG_T9_"+tag)
def load(p,name):
    sp=importlib.util.spec_from_file_location(name,p)
    m=importlib.util.module_from_spec(sp);sys.modules[name]=m
    sp.loader.exec_module(m);return m
def source():
    rng=random.Random(920000)
    allocated=set()
    def node():
        while True:
            n=rng.randrange(1000,2147000000)
            if n not in allocated:
                allocated.add(n);return n
    corridors=[tuple(node() for _ in range(9)) for _ in range(4)]
    edges=[[ (c[j],j%4,c[j+1]) for j in range(8)] for c in corridors]
    # Distinct distractor-only endpoints; 40 irrelevant public events.
    noise=[(node(),rng.randrange(4),node()) for _ in range(40)]
    events=[]
    for i in range(8):
        # At each phase the target edge arrives BEFORE six other events.
        events.append(edges[0][i])
        for other in range(1,4):events.append(edges[other][i])
        events.extend(noise[5*i:5*i+5])
    need(len(events)==72 and len(set(events))==72,"72_INDEPENDENT_PUBLIC_EVENTS")
    question={"start":corridors[0][0],
              "ops":tuple((i%4,1) for i in range(8))}
    evaluator={"answer":corridors[0][8],
               "source_only_target":tuple(edges[0])}
    return tuple(events),question,evaluator
def task_aware_online(public,question,packing,weights):
    need(len(public)==72 and len(question["ops"])==8
         and len(weights)==20,"PUBLIC_72_AND_20_PARAMS")
    cursor=question["start"]
    step=0;records=[];compositions=0;ignore=0;accepted=0
    for i,event in enumerate(public):
        a,role,b=event
        # Strict public QUERY, never source evaluator fields.
        relevant=(step<8 and a==cursor and
                  role==question["ops"][step][0] and
                  question["ops"][step][1]==1)
        if not relevant:
            ignore+=1;continue
        incoming=packing.edge_record(event)
        if records:
            candidates=packing.candidates([records[-1]],incoming)
            merged=[rec for idx,rec in candidates if idx==0
                    and 1<len(rec[2])<=6]
        else:merged=[]
        if merged:
            merged.sort(key=lambda rec:(-len(rec[2]),rec))
            records[-1]=merged[0];compositions+=1
        else:
            records.append(incoming)
        cursor=b;step+=1;accepted+=1
        need(len(records)<=10 and all(len(packing.pack(*r))==12 for r in records),
             "FULL_PACKED_NATIVE_144BYTE_STATE")
    return tuple(records),{
         "online_query_public_before_stream":True,
         "public_required_edges_seen":accepted,
         "public_irrelevant_events_ignored":ignore,
         "native_f60_codec_causal_merges":compositions,
         "retained_native_records":len(records),
         "learner_weights_bytes":len(weights),
         "complete_native_state_budget_bytes":144,
         "weights_used_to_resolve_competing_public_edges":False,
         "source_only_truth_accessed_by_policy":False}
def exact_public_filter(public,question,packing):
    # This strongest control receives the SAME early public query.
    memory=[];node=question["start"];step=0
    for a,r,b in public:
        if step<8 and a==node and r==question["ops"][step][0]:
            memory.append(packing.edge_record((a,r,b)))
            node=b;step+=1
    need(len(memory)==8 and step==8,"FULL_PUBLIC_TARGET_FILTER")
    return tuple(memory)
def measure(fn):
    tracemalloc.start();start=time.process_time_ns()
    result=fn();receipt={"cpu_ns":time.process_time_ns()-start,
          "python_peak_bytes":tracemalloc.get_traced_memory()[1]}
    tracemalloc.stop();return result,receipt
def main():
    freeze=json.loads(FREEZE.read_text())
    need(freeze["schema"]=="northstar.t9.causal-sufficiency.preimplementation.v1"
         and freeze["parent_exact_head"]=="c6d6bf5b15e3d929b95e81f2eddd97bf08501b0a"
         and not freeze["authority"]["original_YNS_protected"],"FROZEN_REGIME")
    t5=load(T5,"ygg_t9_t5")
    t4=load(T4,"ygg_t9_t4")
    t3=load(t5.T3,"ygg_t9_t3")
    t2=t3.load(t3.T2,"ygg_t9_t2")
    f62,kernel,_=t2.modules()
    t2.materialize_ephemeral_canonical_native_sources(f62)
    packing=f62.codec()
    public,question,evaluator=source()
    (candidate,receipt),ccost=measure(lambda:task_aware_online(
         public,question,packing,bytes(20)))
    control,ecost=measure(lambda:exact_public_filter(public,question,packing))
    f60,bcost=measure(lambda:f62.controls()[0].online_fixed(public))
    (cand_answer),scost=measure(lambda:t4.public_solver(candidate,question,packing))
    (exact_answer),esolve=measure(lambda:t4.public_solver(control,question,packing))
    (old_answer),bsolve=measure(lambda:t4.public_solver(f60,question,packing))
    result={"schema":"ygg.t9.early-public-query-causal-memory-fixture.v1",
         "synthetic_source_id":-20000,"public_events":len(public),
         "original_T8_new_first_use_replayed":False,
         "new_prospective_original_or_replica_born":0,
         "correct_answer_on_source_neutral_fixture":
                    cand_answer==evaluator["answer"],
         "same_information_exact_filter_correct":
                    exact_answer==evaluator["answer"],
         "frozen_F60_query_agnostic_correct":old_answer==evaluator["answer"],
         "native_candidate":receipt,
         "candidate_cpu_peak":ccost,"exact_public_control_cpu_peak":ecost,
         "frozen_F60_cpu_peak":bcost,
         "candidate_solver_cpu_peak":scost,
         "exact_public_solver_cpu_peak":esolve,
         "learner_trained_weights_nonzero":False,
         "novel_cognitive_learning_demonstrated":False,
         "new_task_regime_not_equal_to_T8_source":True,
         "original_YNS_protected_used":0,
         "scientific_acceptance":False}
    need(result["correct_answer_on_source_neutral_fixture"] and
         result["same_information_exact_filter_correct"],"PUBLIC_QUERY_SUFFICIENCY")
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
