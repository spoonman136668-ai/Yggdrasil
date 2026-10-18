"""T2 source-pinned adapter for F62 native legal action enumeration.

Non-consuming synthetic 72-public-event acceptance only. This adapter uses
unaltered F62.actions() and F60.codec() and an exactly packed 144-byte learned
state; the native F85 solver cannot yet answer unseen 8-op questions.
"""
from __future__ import annotations
import importlib.util,sys,hashlib,inspect,json,time,tracemalloc,types,subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
F62=ROOT/"research/foundational/20261015-y-f62/source_pilot.py"
F60=ROOT/"research/foundational/20261015-y-f60/source_feasibility.py"
F85=ROOT/"research/foundational/20261016-y-f85/global_solver.py"
KERNEL=HERE/"20261018-yggdrasil-learned-kernel.py"
SOURCE=HERE/"20261018-yggdrasil-t2-source.py"
EXPECTED={"f62":"7ed72deca5584d7c0b6562d74456fa7d4bee6712",
          "f60":"123dd7e979485ae07664118f948cd651b0386526",
          "f85":"e4eb4bfbd6a01212f8c1eebc38af09b15c6d9cc3",
          "kernel":"f0ded7d42d74814464d6cc9b0422c9616038cd8c"}
def need(ok,tag):
    if not ok:raise ValueError("YGG_T2_NATIVE_"+tag)
def blob(path):
    # Git's canonical content identity honors the checkout's Windows CRLF
    # normalization rules. Do not hash worktree bytes on Windows.
    p=subprocess.run(["git","hash-object",str(path)],cwd=ROOT,
                     check=True,capture_output=True,text=True)
    return p.stdout.strip()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m
    spec.loader.exec_module(m)
    return m

def modules():
    for k,p in (("f62",F62),("f60",F60),("f85",F85),("kernel",KERNEL)):
        need(blob(p)==EXPECTED[k],"TRANSITIVE_NATIVE_"+k.upper()+"_SOURCE_DRIFT")
    return load("t2_y_f62",F62),load("t2_y_kernel",KERNEL),load("t2_y_source",SOURCE)

def state_pack(records,weights,step,packing):
    need(len(records)<=10 and len(weights)==20 and 0<=step<72,"HARD_144_LAYOUT")
    packed=[packing.pack(*rec) for rec in records]
    need(all(len(x)==12 and packing.unpack(x)==rec
             for x,rec in zip(packed,records)),"EXACT_NATIVE_PACKING_CODEC")
    state=b"".join(packed)+bytes((10-len(packed))*12)+weights+bytes((len(records),step,0,0))
    need(len(state)==144 and state[-4]==len(records),"COMPLETE_STATE_INCLUDES_WEIGHTS")
    return state

def cap10_native_actions(f62):
    """Instantiates ORIGINAL F62 actions bytecode with stricter 10-record cap.

    This is a new candidate variant requiring independent native acceptance;
    neither F62 source nor its 12-record behavior changes. Complete legal
    append/merge/evict action enumeration is shared byte-for-byte, with
    F62's original _valid_memory bytecode rebound to the 10-record cap.
    """
    valid_env=dict(f62._valid_memory.__globals__,CAP=10)
    valid=types.FunctionType(f62._valid_memory.__code__,valid_env,
          f62._valid_memory.__name__,f62._valid_memory.__defaults__)
    action_env=dict(f62.actions.__globals__,CAP=10,_valid_memory=valid)
    action=types.FunctionType(f62.actions.__code__,action_env,
          f62.actions.__name__,f62.actions.__defaults__)
    need(action.__code__ is f62.actions.__code__
         and valid.__code__ is f62._valid_memory.__code__,
         "EXACT_NATIVE_F62_ACTION_BYTECODE")
    return action

def online_native_adapter(events,weights,packing,f62,kernel):
    need(type(events) in (tuple,list) and len(events)==72
         and all(type(e) is tuple and len(e)==3 for e in events),
         "ONLY_72_PUBLIC_EVENTS_NO_EVALUATOR_METADATA")
    records=()
    cap10_actions=cap10_native_actions(f62)
    actions=[]
    states=0
    for i,event in enumerate(events):
        possibilities=cap10_actions(records,event,i,packing)
        incoming=packing.pack(*packing.edge_record(event))
        eligible=[]
        for j,(kind,old,drop,after,f62_features) in enumerate(possibilities):
            if len(after)>10:continue
            state=state_pack(after,weights,i,packing)
            score,_=kernel.public_score(state,incoming,i)
            eligible.append((score,-j,j,after,kind,old,drop,state))
            states+=1
        need(eligible,"F62_LEGAL_ACTIONS_WITHIN_144_BYTE_LEARNED_CAP")
        choice=max(eligible)
        score,_,_,records,kind,old,drop,state=choice
        need(len(records)<=10 and len(state)==144,"EXACT_PERSISTENT_LIMIT")
        actions.append((kind,old,drop))
    return records,tuple(actions),{"native_legal_candidates_evaluated":states,
        "native_records_retained":len(records),
        "persistent_total_bytes":144,
        "F62_actions_called":72,
        "native_F62_source_untouched":True,
        "native_F62_legal_action_algorithm_same_bytecode":True,
        "new_candidate_legal_capacity_binding":10,
        "original_F62_capacity_unchanged":12,
        "learned_public_features_only":True,
        "future_question_seen":False}

def measure(fn):
    tracemalloc.start()
    start=time.process_time_ns()
    result=fn()
    cpu=time.process_time_ns()-start
    peak=tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return result,{"CPU_ns":cpu,"Python_peak_bytes":peak}

def attest():
    f62,kernel,source=modules()
    events,evaluator=source.build_fixture(-920)
    need(len(evaluator["ops"])==8 and len(events)==72,"NEW_SOURCE_NOT_F62_REHASH")
    packing=f62.codec()
    training=[(tuple([0.0]*19+[1.0]),1),
              (tuple([0.0]*19+[1.0]),-1)]
    weights,train=kernel.fit_train_only(training)
    (native,acts,receipt),candidate_cost=measure(
        lambda:online_native_adapter(events,weights,packing,f62,kernel))
    f60=f62.controls()[0]
    (baseline_records),baseline_cost=measure(lambda:f60.online_fixed(events))
    need(len(native)<=10 and len(baseline_records)<=12
         and receipt["persistent_total_bytes"]==144,
         "OLD_AND_NEW_NATIVE_RESIDENCY")
    solver_source=F85.read_text(encoding="utf8")
    solver_cannot_handle_8="assert len(ops) in (4,6)" in solver_source
    need(solver_cannot_handle_8,"F85_LONG_CHAIN_GATE_CHANGED_REQUALIFY")
    return {"schema":"ygg.t2.native-actions-nonconsuming-resource-probe.v1",
        "native_source_pins_verified":True,
        "original_F62_legal_action_algorithm_instantiated_at_capacity_10":True,
        "original_F62_12_record_source_untouched":True,
        "native_persistent_bytes":144,
        "F60_original_persistent_budget_bytes":144,
        "learned_weights_bytes":20,
        "native_learner":receipt,
        "candidate_cost":candidate_cost,"original_F60_cost":baseline_cost,
        "training_parameter_updates":train["training_parameter_updates"],
        "F85_8_op_solver_not_supported":True,
        "equal_or_lower_compute_and_peak_memory_demonstrated":
            (candidate_cost["CPU_ns"]<=baseline_cost["CPU_ns"] and
             candidate_cost["Python_peak_bytes"]<=baseline_cost["Python_peak_bytes"]),
        "result_is_synthetic_diagnostic_only":True,
        "unseen_constructed":0,"native_transfer_scientifically_qualified":False,
        "independent_protected_first_use":False}
if __name__=="__main__":print(json.dumps(attest(),sort_keys=True))
