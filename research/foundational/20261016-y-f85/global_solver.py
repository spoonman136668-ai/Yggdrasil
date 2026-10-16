#!/usr/bin/env python3
"""F85 globally constrained compositional solver on frozen memories.

No training, new sources or online memory decisions. The method sees only a
question's start + ordered role/direction operators and the already-retained
records. It MUST NOT read question['answer'] inside solve_global().
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

P = Path(__file__).resolve().parent
UP = P.parent
EXPECTED_PREREG = "3e030beba828999c8de44abd3c324ec519807a27"
F83_SHA = "68138887c8bc42a17f8866df96cbede8e2594325"
F84_SHA = "0465a0612640520a695a98a0d3fd7b255174142e"
D4_SHA = "72e5c58be0c3df0b7972bb77a1284753d62fbf03"
EXPOSED_SEEDS = range(-5121,-5137,-1)
EXPOSED_FAMILIES = (-2,-1)


def blob(p):
    b=p.read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()


def checked_loader(name,p,expected):
    assert blob(p)==expected,("FROZEN_PARENT_DRIFT",str(p))
    spec=importlib.util.spec_from_file_location(name,p)
    m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m
    spec.loader.exec_module(m)
    return m


def solve_global(records, question, codec, max_transitions=4096, max_states=512):
    """Return (unique_terminal_or_None, accounting).

    No prediction labels, hidden true answer, entire public stream, future
    events, model weights, or offline teacher enter this routine.
    """
    assert 0<=len(records)<=12 and all(len(codec.pack(*r))==12 and
                                        codec.unpack(codec.pack(*r))==r
                                        for r in records)
    start=question["start"]
    ops=question["ops"]
    assert len(ops) in (4,6)
    codes=tuple(2*role+int(direction==-1) for role,direction in ops)
    assert all(0<=c<8 for c in codes)
    oriented=set()
    for rec in records:
        oriented.add(rec)
        oriented.add(codec.mirrored(rec))
    sorted_oriented=tuple(sorted(oriented))
    states={0:{start}}
    transitions=0
    examined=0
    capped=False
    for consumed in range(len(codes)):
        if consumed not in states:continue
        for at in sorted(states[consumed]):
            for a,b,record_codes in sorted_oriented:
                examined+=1
                if examined>max_transitions:
                    capped=True
                    break
                step=len(record_codes)
                if a==at and consumed+step<=len(codes) and (
                    record_codes==codes[consumed:consumed+step]
                ):
                    states.setdefault(consumed+step,set()).add(b)
                    transitions+=1
                    if sum(len(v) for v in states.values())>max_states:
                        capped=True
                        break
            if capped:break
        if capped:break
    ends=states.get(len(codes),set()) if not capped else set()
    result=next(iter(ends)) if len(ends)==1 else None
    return result,dict(
        algorithm="global_unique_terminal_role_composition",
        transient_state_cells=sum(len(v) for v in states.values()),
        record_state_pairs_examined=examined,transitions=transitions,
        resource_cap_triggered=capped,distinct_final_endpoints=len(ends),
        returned_unique=bool(result is not None),
        persistent_memory_records=len(records),
        persistent_memory_bytes=len(records)*12
    )


def qualified_exposed_readonly_diagnostic():
    assert blob(P/"prereg.json")==EXPECTED_PREREG,"F85_PREREG_CHANGED_AFTER_FREEZE"
    prereg=json.loads((P/"prereg.json").read_text())
    assert prereg["stage"]=="FROZEN_PRECODE_EXPOSED_SYNTHETIC_ONLY_NOT_SCIENTIFIC_ACCEPTANCE"
    assert (prereg["parent"]["exact_f84_head_sha"]==
            "90c8a7f9b399e21fdf5a3a06f488ae3de8cb72f4")
    f84=checked_loader("f85_f84_unchanged_exposed",UP/"20261016-y-f84"/"forensic_reachability.py",F84_SHA)
    d4=checked_loader("f85_d4_unchanged_exposed",UP/"20261016-y-f84"/"native_legal_action_witness.py",D4_SHA)
    assert blob(UP/"20261016-y-f83"/"pairwise_learner.py")==F83_SHA
    weights=f84.assert_frozen()
    f=f84.load_f83()
    rows=[]
    peak_examined=0
    peak_states=0
    for seed in EXPOSED_SEEDS:
        for family in EXPOSED_FAMILIES:
            public,question,meta=f.M.SOURCE.source(seed,family)
            all_answers,_=f84.independently_resolve_public(public,question)
            assert all_answers==frozenset({question["answer"]})
            f60=f84.audit_f60(f,public,question)
            f83,f83_trace,_=f.online(public,weights,True,True)
            proof=f.M.AUDITOR.verify(public,question,f83_trace)
            assert proof["prefixes"]==72 and proof["max_payload_bytes"]<=144
            stat=dict(seed=seed,family=family,kind=meta["question_type"],
                      regime=meta["arrival_regime"])
            for key,memory in (("f60",f60),("f83",f83)):
                old=f.M.PACK.solve(memory,question)
                new,audit=solve_global(
                    memory,{"start":question["start"],"ops":question["ops"]},
                    f.M.PACK
                )
                assert new in (None,question["answer"]),"F85_OUTPUT_NOT_PUBLIC_WITNESSED"
                assert not audit["resource_cap_triggered"]
                assert audit["persistent_memory_bytes"]<=144
                stat[key+"_legacy_correct"]=int(old==question["answer"])
                stat[key+"_global_correct"]=int(new==question["answer"])
                stat[key+"_global_transitions"]=audit["transitions"]
                stat[key+"_global_work"]=audit["record_state_pairs_examined"]
                peak_examined=max(peak_examined,audit["record_state_pairs_examined"])
                peak_states=max(peak_states,audit["transient_state_cells"])
            if meta["question_type"]=="crosslink_reach_6_steps":
                original=d4.query_aware_legal_append_witness(f,public,question)
                d4mem,_=d4_memory_exact(f,d4,public,question)
                old=f.M.PACK.solve(d4mem,question)
                assert (old==question["answer"])==original[
                    "query_aware_offline_oracle_correct"
                ]
                new,audit=solve_global(
                    d4mem,{"start":question["start"],"ops":question["ops"]},f.M.PACK)
                assert new in (None,question["answer"])
                assert audit["persistent_memory_bytes"]<=144
                assert not audit["resource_cap_triggered"]
                stat["d4_legacy_correct"]=int(old==question["answer"])
                stat["d4_global_correct"]=int(new==question["answer"])
                stat["d4_global_work"]=audit["record_state_pairs_examined"]
                peak_examined=max(peak_examined,audit["record_state_pairs_examined"])
                peak_states=max(peak_states,audit["transient_state_cells"])
            rows.append(stat)
    assert len(rows)==32
    by={}
    for kind in ("f60","f83","d4"):
        subset=rows if kind!="d4" else [
            x for x in rows if x["kind"]=="crosslink_reach_6_steps"]
        old=sum(x[kind+"_legacy_correct"] for x in subset)
        new=sum(x[kind+"_global_correct"] for x in subset)
        rescued=sum((not x[kind+"_legacy_correct"]) and
                   x[kind+"_global_correct"] for x in subset)
        regressed=sum(x[kind+"_legacy_correct"] and
                      (not x[kind+"_global_correct"]) for x in subset)
        by[kind]=dict(cases=len(subset),legacy_correct=old,
                      global_correct=new,rescued=rescued,regressed=regressed)
    assert by["f60"]["legacy_correct"]==19
    assert by["f83"]["legacy_correct"]==10
    assert by["d4"]["legacy_correct"]==5
    assert all(row["f60_legacy_correct"]==0 and row["f83_legacy_correct"]==0
               for row in rows if row["kind"]=="crosslink_reach_6_steps")
    reg={}
    for kind in ("original","local_rotate4"):
        s=[row for row in rows if row["regime"]==kind]
        assert len(s)==16
        reg[kind]={model:{
            "old_correct":sum(x[model+"_legacy_correct"] for x in s),
            "new_correct":sum(x[model+"_global_correct"] for x in s)
        } for model in ("f60","f83")}
    nondeg=all(by[k]["regressed"]==0 for k in ("f60","f83")) and all(
        scores["new_correct"]>=scores["old_correct"]
        for r in reg.values() for scores in r.values()
    )
    qualified=nondeg and sum(by[k]["rescued"] for k in ("f60","f83"))>0
    status=("exposed_readonly_mechanism_supported" if qualified else
      "exposed_negative" if not nondeg else
      "exposed_solver_mechanism_bounded")
    return dict(
        schema="yggdrasil.f85.global-role-constraint.exposed-readonly.v1",
        stage="EXPOSED_F83_GUARD_ONLY",
        status=status,
        cases=len(rows),crosslink_cases=8,
        by_model=by,by_arrival_regime=reg,
        max_record_state_pairs_examined=peak_examined,
        max_transient_dp_state_cells=peak_states,
        max_persistent_memory_bytes=144,
        F60_F83_memory_bit_identical=True,
        no_future_question_or_answer_used_by_solver=True,
        offline_hindsight_D4_not_fair_online_control=True,
        new_source_cases_used=False,FIT_used=False,DIAG_used=False,
        ORIGINAL_used=False,F3=False,optimizer_promotion=False,
        scientific_qualified=False,
        rows=rows
    )


def d4_memory_exact(f,d4,public,question):
    """Frozen D4 algorithm exactly, no F85 selection or adaptation."""
    pack=f.M.PACK
    required=d4.query_path_in_original_public(public,question)
    target=frozenset(pack.edge_record(x) for x in required)
    order={pack.edge_record(x):i for i,x in enumerate(public)}
    memory=()
    for index,event in enumerate(public):
        options=f.M.F62.actions(memory,event,index,pack)
        append=[o for o in options if o[0]=="append" and o[1]==-1]
        def ranking(item):
            after=item[3]
            return (len(frozenset(after)&target),
                    sum(order.get(rec,-100000) for rec in after
                        if rec not in target))
        choice=max(enumerate(append),key=lambda p:(ranking(p[1]),-p[0]))[1]
        memory=choice[3]
    return memory,target


if __name__=="__main__":
    if sys.argv[1:]!=["--already-exposed-synthetic-only"]:
        raise SystemExit("F85 refuses protected/new experiments or unstaged sources")
    print(json.dumps(qualified_exposed_readonly_diagnostic(),sort_keys=True))
