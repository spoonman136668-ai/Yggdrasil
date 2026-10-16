#!/usr/bin/env python3
"""F89 frozen query-blind graded exchange in source-native retained memory.

The online function sees only the retained 144-byte native state, current
public arrival, index and frozen F62 actions. No query/answer, future events,
source labels or training. Negative synthetic cohorts are never FIT/DIAG.
"""
from __future__ import annotations
import hashlib,importlib.util,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
PREREG_BLOB="4fd1967d6b6e225471f49a0d10b8c17534bd05ce"
F88_BLOB="1e613ee872e545d0ec874ec81c2d4d3ba4742d8d"
GUARD=range(-5521,-5537,-1)
FAMILIES=(-2,-1)
MAX_LOST_SHORT=3
LONG_GAIN_PER_LOST_SHORT=2

def gitblob(path):
    data=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def load_exact(name,path,expected):
    assert gitblob(path)==expected,("F89_FROZEN_SOURCE_DRIFT",str(path))
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module

def decide(memory,event,index,pack,F62,language):
    """Choose among ONLY native F62 legal afterstates using public grammar."""
    baseline=F62._f60_step(memory,event,pack)
    candidates=F62.actions(memory,event,index,pack)
    legal={x[3] for x in candidates}
    assert baseline in legal, "F60_EXACT_NATIVE_PARITY_DRIFT"
    base=language(baseline,pack)
    if base is None:
        return baseline,dict(override=0,capped=1,eligible=0,short_lost=0,long_gain=0)
    base_short,base_five,base_six,_=base
    baseline_long=2*base_six+base_five
    best=None
    eligible=0
    capped=0
    for i,candidate in enumerate(candidates):
        after=candidate[3]
        if after==baseline:continue
        measured=language(after,pack)
        if measured is None:
            capped+=1
            continue
        short,five,six,_=measured
        lost=len(base_short-short)
        if lost>MAX_LOST_SHORT:
            continue
        long_gain=2*six+five-baseline_long
        if long_gain<2*lost+1:
            continue
        eligible+=1
        score=(long_gain-2*lost,-lost,six,-i)
        if best is None or score>best[0]:
            best=(score,after,lost,long_gain)
    if best is None:
        return baseline,dict(override=0,capped=capped,eligible=eligible,short_lost=0,long_gain=0)
    _score,result,lost,gain=best
    assert result in legal
    F62._valid_memory(result,pack)
    return result,dict(override=1,capped=capped,eligible=eligible,short_lost=lost,long_gain=gain)

def online(public,pack,F62,language,trace=False):
    assert len(public)==72 and all(len(event)==3 for event in public)
    memory=()
    receipts=[]
    metrics=dict(overrides=0,capped=0,eligible=0,short_lost=0,long_gain=0)
    for index,event in enumerate(public):
        memory,audit=decide(memory,event,index,pack,F62,language)
        F62._valid_memory(memory,pack)
        for field in metrics:
            metrics[field]+=audit[field]
        if trace:
            receipts.append(tuple(pack.pack(*r).hex() for r in memory))
    if trace:
        return memory,tuple(receipts),metrics
    return memory

def run():
    assert gitblob(HERE/"prereg.json")==PREREG_BLOB,"F89_PREREG_DRIFT"
    reg=json.loads((HERE/"prereg.json").read_text())
    assert reg["stage"]=="FROZEN_PRECODE_DISJOINT_NEGATIVE_SYNTHETIC_ONLY"
    assert reg["new_guard"]=={"seed_start":-5521,"seed_stop_exclusive":-5537,
                              "step":-1,"families":[-2,-1],"cases":32,
                              "expected_six_step_cases":8,
                              "source":"Exact frozen F76 two-arrival synthetic generator; negative seeds only",
                              "previous_consumed":[[-5121,-5137],[-5221,-5237],[-5321,-5337],[-5421,-5437]]}
    assert reg["parent"]["exact_F88_head_sha"]=="a24abab5f778c753f2e8e3f21adf077ceb1cb6b8"
    F88=load_exact("f89_immutable_F88",ROOT/"20261016-y-f88"/"frontier.py",F88_BLOB)
    F87=F88.load_exact("f89_immutable_F87",ROOT/"20261016-y-f87b"/"bridge_reserve.py",F88.F87B_BLOB)
    F86=F87.load("f89_immutable_F86",ROOT/"20261016-y-f86"/"queryblind_retention.py",F87.F86_SHA)
    F85=F86.load_exact("f89_immutable_F85",ROOT/"20261016-y-f85"/"global_solver.py",F86.F85_METHOD_BLOB)
    F84=F85.checked_loader("f89_immutable_F84",ROOT/"20261016-y-f84"/"forensic_reachability.py",F85.F84_SHA)
    F83=F84.load_f83()
    weights=F84.assert_frozen()
    pack=F83.M.PACK
    F62=F83.M.F62
    rows=[]
    for seed in GUARD:
        for family in FAMILIES:
            public,question,meta=F83.M.SOURCE.source(seed,family)
            assert F84.independently_resolve_public(public,question)[0]==frozenset({question["answer"]})
            memory={}
            memory["f60"]=F84.audit_f60(F83,public,question)
            memory["f83"],t83,_=F83.online(public,weights,True,True)
            assert F83.M.AUDITOR.verify(public,question,t83)["prefixes"]==72
            memory["f86"],t86,_=F86.online(public,pack,F62,True)
            assert F83.M.AUDITOR.verify(public,question,t86)["prefixes"]==72
            memory["f87"],t87,_=F87.online(public,pack,F62,True)
            assert F83.M.AUDITOR.verify(public,question,t87)["prefixes"]==72
            memory["f88"],t88,_=F88.online(public,pack,F62,True)
            assert F83.M.AUDITOR.verify(public,question,t88)["prefixes"]==72
            memory["f89"],t89,stats=online(public,pack,F62,F88.public_language,True)
            cert=F83.M.AUDITOR.verify(public,question,t89)
            assert cert["prefixes"]==72 and cert["max_payload_bytes"]<=144
            row=dict(seed=seed,family=family,regime=meta["arrival_regime"],
                     kind=meta["question_type"],overrides=stats["overrides"],
                     eligible=stats["eligible"],capped=stats["capped"],
                     lost_short_tuples=stats["short_lost"],
                     earned_long_weight=stats["long_gain"],max_bytes=cert["max_payload_bytes"])
            for name,retained in memory.items():
                prediction,cost=F85.solve_global(retained,
                    {"start":question["start"],"ops":question["ops"]},pack)
                assert prediction is None or prediction==question["answer"],"NONPUBLIC_OR_INCORRECT_OUTPUT"
                assert not cost["resource_cap_triggered"] and cost["persistent_memory_bytes"]<=144
                row[name+"_correct"]=int(prediction==question["answer"])
            row["f89_greedy_correct"]=int(pack.solve(memory["f89"],question)==question["answer"])
            rows.append(row)
    assert len(rows)==32
    by={}
    for regime in ("original","local_rotate4"):
        by[regime]={}
        for kind in ("within_component_4_steps","crosslink_reach_6_steps"):
            subset=[r for r in rows if r["regime"]==regime and r["kind"]==kind]
            assert subset,("MISSING_SOURCE_STRATUM",regime,kind)
            by[regime][kind]=dict(cases=len(subset),
                correct={arm:sum(r[arm+"_correct"] for r in subset)
                         for arm in ("f60","f83","f86","f87","f88","f89")},
                f89_rescued=sum(not r["f60_correct"] and r["f89_correct"] for r in subset),
                f89_regressed=sum(r["f60_correct"] and not r["f89_correct"] for r in subset),
                f89_override_events=sum(r["overrides"] for r in subset))
    six=[r for r in rows if r["kind"]=="crosslink_reach_6_steps"]
    rescues=sum(not r["f60_correct"] and r["f89_correct"] for r in six)
    regressions=sum(r["f60_correct"] and not r["f89_correct"] for r in rows)
    overrides=sum(r["overrides"] for r in rows)
    status=("synthetic_mechanism_supported" if rescues and not regressions
            else "synthetic_negative")
    return dict(
        schema="yggdrasil.f89.graded-language-tradeoff.synthetic-firstuse.v1",
        stage="NEW_NEGATIVE_SYNTHETIC_ONLY",classification=status,
        cases=32,six_step_cases=len(six),
        scores={arm:sum(r[arm+"_correct"] for r in rows)
                for arm in ("f60","f83","f86","f87","f88","f89")},
        six_step_rescues_from_F60=rescues,F60_correct_case_regressions=regressions,
        native_override_events=overrides,
        eligible_native_action_opportunities=sum(r["eligible"] for r in rows),
        resource_cap_events=sum(r["capped"] for r in rows),
        total_allowed_short_tuple_losses=sum(r["lost_short_tuples"] for r in rows),
        per_regime_and_kind=by,
        max_persistent_memory_bytes=max(r["max_bytes"] for r in rows),
        no_query_or_future_in_online=True,all_72_causal_prefixes_audited=True,
        no_policy_fitting=True,no_protected_original=True,no_FIT=True,no_DIAG=True,
        no_F3=True,no_controller_or_optimizer_mutation=True,
        science_accepted=False,rows=rows
    )

if __name__=="__main__":
    if sys.argv[1:]!=["--once-disjoint-synthetic-only"]:
        raise SystemExit("F89 refuses protected original, FIT and DIAG access")
    print(json.dumps(run(),sort_keys=True))
