#!/usr/bin/env python3
"""F88: native F60-anchored, query-blind relationship-language frontier.

Source-only synthetic first use. Online selection sees solely retained public
records, current public event and index, never task question/answer, seed,
source regime, unseen events, or retrospective scientific result.
"""
from __future__ import annotations
import hashlib,importlib.util,json,sys
from pathlib import Path

P=Path(__file__).resolve().parent
ROOT=P.parent
PREREG_BLOB="95afaacbfa02506e3a534ea38171b04f9e5fcf36"
F87B_BLOB="0026a7f4a9827d960c5ed06f4ce206404e3d739a"
GUARD=range(-5421,-5437,-1)
FAMILIES=(-2,-1)
PATH_CAP=15000

def gitblob(path):
    raw=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def load_exact(name,path,expected):
    assert gitblob(path)==expected,("F88_FROZEN_SOURCE_DRIFT",str(path))
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod

def public_language(records,pack,cap=PATH_CAP):
    """Exact retained-memory directed role-language; no future or query inputs.

    Full native record segments and their frozen codec inverses are available;
    no imagined truncation of long records is permitted. Compose at matching
    endpoints. Return None on resource cap, and never interpret that as proof.
    """
    assert len(records)<=12
    oriented=set()
    for r in records:
        assert len(r)==3 and 1<=len(r[2])<=6
        oriented.add(r)
        oriented.add(pack.mirrored(r))
    by_start={}
    for a,b,codes in sorted(oriented):
        by_start.setdefault(a,[]).append((b,tuple(codes)))
    seen=set((a,b,tuple(codes)) for a,b,codes in oriented)
    if len(seen)>cap:return None
    pending=list(sorted(seen))
    cursor=0
    while cursor<len(pending):
        origin,at,codes=pending[cursor]
        cursor+=1
        for end,extra in by_start.get(at,()):
            if len(codes)+len(extra)>6:continue
            combined=(origin,end,codes+extra)
            if combined in seen:continue
            if len(seen)>=cap:return None
            seen.add(combined)
            pending.append(combined)
    short=frozenset(row for row in seen if len(row[2])<=4)
    five=sum(len(row[2])==5 for row in seen)
    six=sum(len(row[2])==6 for row in seen)
    return short,five,six,len(seen)

def decide(memory,event,index,pack,F62):
    """Return chosen strictly legal state and bounded opportunity evidence."""
    baseline=F62._f60_step(memory,event,pack)
    options=F62.actions(memory,event,index,pack)
    assert baseline in {x[3] for x in options},"F60_NOT_IN_NATIVE_ACTIONS"
    base=public_language(baseline,pack)
    if base is None:
        return baseline,dict(capped=1,eligible=0,override=0,base_paths=0)
    base_short,base_five,base_six,_=base
    highest=None
    capped=0
    eligible=0
    for option_index,opt in enumerate(options):
        after=opt[3]
        if after==baseline:continue
        candidate=public_language(after,pack)
        if candidate is None:
            capped+=1
            continue
        short,five,six,_=candidate
        if short!=base_short or six<=base_six:
            continue
        eligible+=1
        score=(six,five,-option_index)
        if highest is None or score>highest[0]:
            highest=(score,after)
    result=baseline if highest is None else highest[1]
    assert result in {x[3] for x in options}
    F62._valid_memory(result,pack)
    return result,dict(capped=capped,eligible=eligible,
                       override=int(result!=baseline),base_paths=base_six)

def online(public,pack,F62,trace=False):
    assert len(public)==72 and all(len(e)==3 for e in public)
    memory=()
    snapshots=[]
    stats=dict(capped=0,eligible=0,overrides=0,baseline_six_sum=0)
    for index,event in enumerate(public):
        memory,info=decide(memory,event,index,pack,F62)
        F62._valid_memory(memory,pack)
        stats["capped"]+=info["capped"]
        stats["eligible"]+=info["eligible"]
        stats["overrides"]+=info["override"]
        stats["baseline_six_sum"]+=info["base_paths"]
        if trace:
            snapshots.append(tuple(pack.pack(*r).hex() for r in memory))
    if trace:return memory,tuple(snapshots),stats
    return memory

def run():
    assert gitblob(P/"prereg.json")==PREREG_BLOB,"F88_PRECODE_PREREG_DRIFT"
    reg=json.loads((P/"prereg.json").read_text())
    assert reg["stage"]=="FROZEN_PRECODE_SYNTHETIC_FIRST_USE_ONLY"
    assert reg["source"]["new_synthetic_guard"]=={
        "seed_start":-5421,"seed_stop_exclusive":-5437,
        "seed_step":-1,"families":[-2,-1],"cases":32
    }
    F87=load_exact("f88_frozen_F87B",ROOT/"20261016-y-f87b"/"bridge_reserve.py",F87B_BLOB)
    F86=F87.load("f88_frozen_F86",ROOT/"20261016-y-f86"/"queryblind_retention.py",F87.F86_SHA)
    F85=F86.load_exact("f88_frozen_F85",ROOT/"20261016-y-f85"/"global_solver.py",F86.F85_METHOD_BLOB)
    F84=F85.checked_loader("f88_frozen_F84",ROOT/"20261016-y-f84"/"forensic_reachability.py",F85.F84_SHA)
    F83=F84.load_f83()
    frozen=F84.assert_frozen()
    pack=F83.M.PACK
    F62=F83.M.F62
    rows=[]
    for seed in GUARD:
        for family in FAMILIES:
            public,q,meta=F83.M.SOURCE.source(seed,family)
            assert F84.independently_resolve_public(public,q)[0]=={q["answer"]}
            states={}
            states["f60"]=F84.audit_f60(F83,public,q)
            states["f83"],t83,_=F83.online(public,frozen,True,True)
            assert F83.M.AUDITOR.verify(public,q,t83)["prefixes"]==72
            states["f86"],t86,_=F86.online(public,pack,F62,True)
            assert F83.M.AUDITOR.verify(public,q,t86)["prefixes"]==72
            states["f87"],t87,_=F87.online(public,pack,F62,True)
            assert F83.M.AUDITOR.verify(public,q,t87)["prefixes"]==72
            states["f88"],t88,stats=online(public,pack,F62,True)
            audit=F83.M.AUDITOR.verify(public,q,t88)
            assert audit["prefixes"]==72 and audit["max_payload_bytes"]<=144
            row=dict(seed=seed,family=family,regime=meta["arrival_regime"],
                     kind=meta["question_type"],overrides=stats["overrides"],
                     capped=stats["capped"],eligible=stats["eligible"],
                     f88_prefixes_verified=72,max_bytes=audit["max_payload_bytes"])
            for name,retained in states.items():
                guess,diagnostic=F85.solve_global(
                    retained,{"start":q["start"],"ops":q["ops"]},pack)
                assert guess in (None,q["answer"]),"F88_NONPUBLIC_PREDICTION"
                assert not diagnostic["resource_cap_triggered"]
                assert diagnostic["persistent_memory_bytes"]<=144
                row[name+"_correct"]=int(guess==q["answer"])
            row["f88_legacy_solver_correct"]=int(
                pack.solve(states["f88"],q)==q["answer"])
            rows.append(row)
    assert len(rows)==32
    grouped={}
    for regime in ("original","local_rotate4"):
        grouped[regime]={}
        for kind in ("within_component_4_steps","crosslink_reach_6_steps"):
            cases=[r for r in rows if r["regime"]==regime and r["kind"]==kind]
            assert cases,("MISSING_CASE_CLASS",regime,kind)
            grouped[regime][kind]=dict(
                cases=len(cases),
                correct={m:sum(r[m+"_correct"] for r in cases)
                         for m in ("f60","f83","f86","f87","f88")},
                f88_rescues=sum(not r["f60_correct"] and r["f88_correct"]
                                for r in cases),
                f88_regressions=sum(r["f60_correct"] and not r["f88_correct"]
                                    for r in cases),
                f88_overrides=sum(r["overrides"] for r in cases))
    six=[r for r in rows if r["kind"]=="crosslink_reach_6_steps"]
    rescued=sum(not r["f60_correct"] and r["f88_correct"] for r in six)
    regressed=sum(r["f60_correct"] and not r["f88_correct"] for r in rows)
    supported=bool(rescued) and regressed==0
    return dict(
        schema="yggdrasil.f88.public-language-frontier.synthetic.v1",
        stage="ONE_TIME_DISJOINT_NEGATIVE_SYNTHETIC_ONLY",
        classification=("synthetic_mechanism_supported" if supported else
                        "synthetic_negative"),
        guard_cases=len(rows),six_step_cases=len(six),
        scores={name:sum(r[name+"_correct"] for r in rows)
                for name in ("f60","f83","f86","f87","f88")},
        six_step_rescues_over_F60=rescued,
        F60_case_regressions=regressed,
        F88_native_override_events=sum(r["overrides"] for r in rows),
        F88_legal_sixstep_eligible_events=sum(r["eligible"] for r in rows),
        F88_resource_cap_events=sum(r["capped"] for r in rows),
        per_regime_and_kind=grouped,
        max_retained_memory_bytes=max(r["max_bytes"] for r in rows),
        all_F88_prefixes_verified=True,
        no_future_queries_in_online_policy=True,
        policy_fit_operations=0,new_negative_guard_first_use=True,
        no_protected_original=True,no_FIT=True,no_DIAG=True,no_F3=True,
        scientific_accepted=False,optimizer_promotion=False,
        rows=rows
    )
if __name__=="__main__":
    if sys.argv[1:]!=["--frozen-negative-synthetic-guard-only"]:
        raise SystemExit("F88 prohibits protected first-use, FIT, DIAG, originals")
    print(json.dumps(run(),sort_keys=True))
