#!/usr/bin/env python3
"""F86: frozen query-blind, causal native memory retention.

Only previously retained 12-byte records, the current public role edge, and
the public index affect the online decision. No future events, correct answer,
question operators, seed, family, or source metadata enter online().
No learned weights and no post-result tuning.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
PREREG_BLOB="a82e11df3df375cef008407d22ddf84c7101a5b2"
F85_METHOD_BLOB="e4eb4bfbd6a01212f8c1eebc38af09b15c6d9cc3"
F83_METHOD_BLOB="68138887c8bc42a17f8866df96cbede8e2594325"
F76_SOURCE_BLOB="5b8928b0399ce9f869854beadeab04b29c8703a5"
F62_NATIVE_BLOB="7ed72deca5584d7c0b6562d74456fa7d4bee6712"
GUARD_SEEDS=range(-5221,-5237,-1)
FAMILIES=(-2,-1)


def gitblob(path):
    content=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(content)).encode()+b"\0"+content).hexdigest()


def load_exact(name,path,sha):
    assert gitblob(path)==sha,("TRANSITIVE_FROZEN_CODE_DRIFT",str(path))
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


def priority(memory,after,index):
    """Fixed lexicographic score using only public native records.

    Neither numeric node magnitudes nor future/target graph information is
    used. Endpoint equality supplies query-blind possible-join structure.
    """
    del index
    lengths=tuple(len(r[2]) for r in after)
    assert all(1<=length<=6 for length in lengths)
    total=sum(lengths)
    squares=sum(length*length for length in lengths)
    joinable=sum(1 for i,a in enumerate(after) for b in after[i+1:]
                 if a[0] in (b[0],b[1]) or a[1] in (b[0],b[1]))
    multi=sum(length>=2 for length in lengths)
    changed=int(tuple(memory)!=tuple(after))
    return (total,squares,joinable,multi,changed,lengths)


def online(public,pack,F62,trace=False):
    """Online source-native transition selection, with no question parameter."""
    assert len(public)==72 and all(len(x)==3 for x in public)
    memory=()
    receipts=[]
    selected=[]
    for index,event in enumerate(public):
        candidates=F62.actions(memory,event,index,pack)
        assert candidates
        ix=max(range(len(candidates)),
               key=lambda n:(priority(memory,candidates[n][3],index),-n))
        action,old,drop,after,_features=candidates[ix]
        assert after in {x[3] for x in candidates}
        F62._valid_memory(after,pack)
        memory=after
        selected.append((action,old,drop))
        if trace:
            receipts.append(tuple(pack.pack(*record).hex() for record in memory))
    if trace:
        return memory,tuple(receipts),tuple(selected)
    return memory


def evaluate():
    assert gitblob(HERE/"prereg.json")==PREREG_BLOB, "F86_PREREG_DRIFT"
    config=json.loads((HERE/"prereg.json").read_text())
    assert config["cohorts"]["guard"]=={
        "start":-5221,"stop_exclusive":-5237,"step":-1}
    assert config["stage"]=="FROZEN_PRECODE_NEGATIVE_SYNTHETIC_ONLY"
    assert config["parent"]["exact_F85_head_sha"]=="f476fbb0c1ee9d8dd3e043fb332933c4d4279f24"
    F85=load_exact("f86_frozen_f85_global_solver",
                   ROOT/"20261016-y-f85"/"global_solver.py",F85_METHOD_BLOB)
    F84=F85.checked_loader("f86_frozen_f84_source",
                           ROOT/"20261016-y-f84"/"forensic_reachability.py",
                           F85.F84_SHA)
    assert gitblob(ROOT/"20261016-y-f83"/"pairwise_learner.py")==F83_METHOD_BLOB
    assert gitblob(ROOT/"20261016-y-f76"/"source.py")==F76_SOURCE_BLOB
    assert gitblob(ROOT/"20261015-y-f62"/"source_pilot.py")==F62_NATIVE_BLOB
    weights=F84.assert_frozen()
    F83=F84.load_f83()
    F62=F83.M.F62
    pack=F83.M.PACK
    rows=[]
    max_memory=0
    max_dp=0
    for seed in GUARD_SEEDS:
        for family in FAMILIES:
            public,q,meta=F83.M.SOURCE.source(seed,family)
            unique_answer,_=F84.independently_resolve_public(public,q)
            assert unique_answer==frozenset({q["answer"]}),"GUARD_SOURCE_NOT_UNIQUE"
            f60=F84.audit_f60(F83,public,q)
            f83,f83trace,_=F83.online(public,weights,True,True)
            proof83=F83.M.AUDITOR.verify(public,q,f83trace)
            assert proof83["prefixes"]==72 and proof83["max_payload_bytes"]<=144
            f86,trace,actions=online(public,pack,F62,True)
            audit=F83.M.AUDITOR.verify(public,q,trace)
            assert audit["prefixes"]==72 and audit["max_payload_bytes"]<=144
            assert len(actions)==72
            max_memory=max(max_memory,audit["max_payload_bytes"])
            result=dict(seed=seed,family=family,
                regime=meta["arrival_regime"],kind=meta["question_type"],
                f86_native_action_steps=len(actions),
                f86_public_prefixes_audited=audit["prefixes"],
                f86_max_memory_bytes=audit["max_payload_bytes"])
            for name,memory in (("f60",f60),("f83",f83),("f86",f86)):
                pred,diagnostics=F85.solve_global(
                    memory,{"start":q["start"],"ops":q["ops"]},pack)
                assert pred in (None,q["answer"]),("F86_INVALID_PREDICTION",seed,family,name)
                assert not diagnostics["resource_cap_triggered"]
                assert diagnostics["persistent_memory_bytes"]<=144
                max_dp=max(max_dp,diagnostics["record_state_pairs_examined"])
                result[name+"_correct"]=int(pred==q["answer"])
                result[name+"_bytes"]=diagnostics["persistent_memory_bytes"]
                if name=="f86":
                    result["f86_original_solver_correct"]=int(
                        pack.solve(memory,q)==q["answer"])
            rows.append(result)
    assert len(rows)==32
    assert all(x["f86_public_prefixes_audited"]==72 for x in rows)
    by={}
    for regime in ("original","local_rotate4"):
        subset=[r for r in rows if r["regime"]==regime]
        assert len(subset)==16
        by[regime]={}
        for kind in ("within_component_4_steps","crosslink_reach_6_steps"):
            local=[r for r in subset if r["kind"]==kind]
            assert local,("MISSING_QUESTION_TYPE",regime,kind)
            by[regime][kind]=dict(
                cases=len(local),
                f60_correct=sum(x["f60_correct"] for x in local),
                f83_correct=sum(x["f83_correct"] for x in local),
                f86_correct=sum(x["f86_correct"] for x in local),
                rescue_over_f60=sum((not x["f60_correct"]) and x["f86_correct"]
                                     for x in local),
                regression_from_f60=sum(x["f60_correct"] and (not x["f86_correct"])
                                        for x in local))
    metrics={arm:sum(x[arm+"_correct"] for x in rows)
             for arm in ("f60","f83","f86")}
    six=[x for x in rows if x["kind"]=="crosslink_reach_6_steps"]
    rescue6=sum((not x["f60_correct"]) and x["f86_correct"] for x in six)
    regress=sum(x["f60_correct"] and (not x["f86_correct"]) for x in rows)
    prequalified=(len(six)>0 and rescue6>0 and regress==0)
    classification=("synthetic_mechanism_supported" if prequalified else
                    "synthetic_negative")
    return dict(
        schema="yggdrasil.f86.queryblind-native-retention.synthetic-guard.v1",
        stage="NEW_NEGATIVE_SYNTHETIC_GUARD_ONLY",
        classification=classification,
        synthetic_prequalification=prequalified,
        guard_cases=32,guard_seeds=[-5221,-5237],
        results_by_model=metrics,
        six_step_cases=len(six),
        six_step_rescues_over_F60=rescue6,
        regressions_from_F60=regress,
        by_regime_and_kind=by,
        max_f86_persistent_memory_bytes=max_memory,
        max_global_solver_candidate_examinations=max_dp,
        independent_prefix_audit_all_72=True,
        native_actions_only=True,policy_training_count=0,
        no_question_in_online_signature=True,
        no_registered_positive_source_used=True,
        protected_original_used=False,
        protected_FIT_used=False,
        protected_DIAG_used=False,
        scientific_qualified=False,
        optimizer_promotion=False,
        rows=rows)


if __name__=="__main__":
    if sys.argv[1:]!=["--new-negative-synthetic-guard-only"]:
        raise SystemExit("F86 no original, validation, protected FIT/DIAG dispatch")
    print(json.dumps(evaluate(),sort_keys=True))
