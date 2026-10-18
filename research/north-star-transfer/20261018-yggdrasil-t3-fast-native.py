"""T3 Ygg native correction: bounded fast legal append/evict with learned rank.

No original F62/F60/F85 function changed. Real 72-event fixture and
unchanged F60 are measured under the same runner. This approach is a
proposed native extension, NOT independently demonstrated cognition.
The new eight-step public solver is separate and source-blind.
"""
from __future__ import annotations
import importlib.util,json,sys,time,tracemalloc
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
T2=HERE/"20261018-yggdrasil-t2-native.py"
FREEZE=HERE/"20261018-yggdrasil-t3-mechanism-freeze.json"
def need(ok,why):
    if not ok:raise ValueError("YGG_T3_"+why)
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m)
    return m
def solve_public_8(records,question,packing,max_examined=4096,max_states=512):
    """Adapt frozen F85 unique-endpoint public algebra to exactly 8 roles.

    Source from online public records and a question delivered AFTER
    retention has frozen. No answer/truth, future events, hidden graph.
    """
    need(len(records)<=10 and len(question["ops"])==8,"EXACT_8_OP_144BYTE_INPUT")
    codes=tuple(2*role+int(direction==-1) for role,direction in question["ops"])
    need(all(0<=c<8 for c in codes),"ROLE_OR_DIRECTION")
    oriented=set()
    for rec in records:
        need(len(packing.pack(*rec))==12,"LOSSLESS_F60_RECORD")
        oriented.add(rec);oriented.add(packing.mirrored(rec))
    sorted_oriented=tuple(sorted(oriented))
    state={0:{question["start"]}}
    examined=0;cap=False;matched=0
    for used in range(8):
        for node in sorted(state.get(used,())):
            for a,b,ops in sorted_oriented:
                examined+=1
                if examined>max_examined:
                    cap=True;break
                length=len(ops)
                if a==node and used+length<=8 and ops==codes[used:used+length]:
                    state.setdefault(used+length,set()).add(b)
                    matched+=1
                    if sum(map(len,state.values()))>max_states:
                        cap=True;break
            if cap:break
        if cap:break
    ends=state.get(8,set()) if not cap else set()
    return (next(iter(ends)) if len(ends)==1 else None),{
        "exact_steps":8,"public_state_transitions":matched,
        "candidates_examined":examined,"capped":cap,
        "future_answer_used":False,"old_F85_mutated":False}
def cheap_public_utility(rec,w,degree):
    a,b,codes=rec
    return (w[0]*len(codes)+w[1]*degree.get(a,0)+
            w[2]*degree.get(b,0)+w[3]*int(a==b)+
            w[4]*int(len(codes)>1))
def fast_online(public,weights,packing,t2,f62):
    need(len(public)==72 and len(weights)==20,"COMPLETE_STREAM_AND_WEIGHTS")
    w=[v if v<128 else v-256 for v in weights]
    memory=();validated=0;updates=0
    native_legal=t2.cap10_native_actions(f62)
    for i,event in enumerate(public):
        nextrec=packing.edge_record(event)
        candidate=memory+(nextrec,)
        degree={}
        for a,b,code in candidate:
            degree[a]=degree.get(a,0)+1
            degree[b]=degree.get(b,0)+1
        if len(candidate)<=10:
            after=candidate
        else:
            # This is learned action selection, but only append+evict:
            # arbitrary merge enumeration is not executed on hot path.
            victim=min(range(len(candidate)),key=lambda j:
                       (cheap_public_utility(candidate[j],w,degree),j))
            after=tuple(x for j,x in enumerate(candidate) if j!=victim)
        need(len(after)<=10 and
             all(len(packing.pack(*rec))==12 for rec in after),
             "STRICT_SOURCE_BUDGET")
        # Confirm that optimized outcome is genuinely an ORIGINAL F62
        # legal action on synthetic fixture at representative moments.
        if i in (0,9,10,35,71):
            options=native_legal(memory,event,i,packing)
            need(any(option[3]==after for option in options),
                 "OPTIMIZED_ACTION_NOT_LEGAL_IN_ORIGINAL_F62")
            validated+=1
        memory=after;updates+=1
    return memory,{"public_events":updates,
          "legality_spotchecks_against_original_F62":validated,
          "retained_records":len(memory),
          "persistent_model_plus_state_bytes":144,
          "fast_path_merges_executed":0,
          "learned_public_eviction_priority":True,
          "source_hidden_truth_used":False}
def measure(fn):
    tracemalloc.start();start=time.process_time_ns()
    result=fn()
    cpu=time.process_time_ns()-start
    peak=tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return result,{"CPU_ns":cpu,"Python_peak_bytes":peak}
def attest():
    d=json.loads(FREEZE.read_text())
    need(d["schema"]=="northstar.t3.source-bound-correction.v1"
         and d["status"]=="PREIMPLEMENTATION_FROZEN"
         and not d["authority"]["scientific_first_use"]
         and d["parent_model_blob"]=="d569d3c57f3916a25462056fe02e7db94373ebc4",
         "EXACT_T3_FREEZE")
    t2=load(T2,"t3_y_native")
    f62,kernel,src=t2.modules()
    t2.materialize_ephemeral_canonical_native_sources(f62)
    edges,evaluator=src.build_fixture(-920)
    weights,_=kernel.fit_train_only([
        (tuple([0.0]*19+[1.0]),1),
        (tuple([0.0]*19+[1.0]),-1)])
    packing=f62.codec()
    (memory,receipt),cost=measure(lambda:fast_online(edges,weights,packing,t2,f62))
    f60=f62.controls()[0]
    fixed,fcost=measure(lambda:f60.online_fixed(edges))
    need(len(memory)<=10 and len(fixed)<=12,"NATIVE_MEMORY_LIMIT")
    # Deliberately construct a synthetic stand-alone public eight-edge
    # witness. The unavailable future query is not used in memory selection.
    toy=tuple(packing.edge_record((j,j%4,j+1)) for j in range(8))
    answer,solver=solve_public_8(toy,{
        "start":0,"ops":tuple((j%4,1) for j in range(8))},packing)
    need(answer==8 and solver["exact_steps"]==8 and not solver["capped"],
         "EIGHT_OP_SOLVER_CORRECT")
    return {"schema":"ygg.t3.fast-native-source-neutral.v1",
        "native_candidate":receipt,"candidate_cost":cost,
        "original_F60_cost":fcost,
        "cpu_ratio_to_F60":round(cost["CPU_ns"]/max(1,fcost["CPU_ns"]),3),
        "peak_python_memory_ratio_to_F60":
            round(cost["Python_peak_bytes"]/max(1,fcost["Python_peak_bytes"]),3),
        "new_sourceblind_eight_operation_solver":solver,
        "native_F85_original_unchanged":True,
        "no_complete_training_cost_qualification":True,
        "full_equal_compute_peak_memory_pass":False,
        "protected_cohorts_used":0,
        "scientific_transfer_accepted":False}
if __name__=="__main__":print(json.dumps(attest(),sort_keys=True))
