#!/usr/bin/env python3
"""F96 matched-graph arrival-order feasibility and causal public observability.

Uses two orderings of the exact same graph and question. One-deviation
retrospective labels require historical future and answer and are NOT an
admissible online controller. No learned policy, validation fitting, or
protected registered source is accessed.
"""
from __future__ import annotations
import collections,hashlib,importlib.util,json,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
PREREG_BLOB="031f7edd0d43ebe9d66d42832ea4b4057f752406"
F95_BLOB="b68712cab0d1774c4fc27e928b4f4b57748a1fe4"
F76_BLOB="5b8928b0399ce9f869854beadeab04b29c8703a5"
COHORTS={"calibration":range(-6201,-6209,-1),
         "heldout":range(-6241,-6257,-1)}
FAMILIES=(-2,-1)

def gitblob(path):
    raw=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def load_exact(name,path,expected):
    assert gitblob(path)==expected,("F96_FROZEN_SOURCE_DRIFT",str(path))
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod

def undo_rotate4(public):
    """Exact inverse of F76's original -> (1,2,3,0) local block rotation."""
    assert len(public)==72
    return tuple(event for i in range(0,72,4)
                 for event in (public[i+3],public[i],public[i+1],public[i+2]))

def matched_orders(observed,source_regime,source):
    """Reconstruct two orderings from same source events, never regenerate."""
    assert len(observed)==72 and source_regime in ("original","local_rotate4")
    original=tuple(observed) if source_regime=="original" else undo_rotate4(observed)
    orig,name0=source.shift(original,-2)
    rotated,name1=source.shift(original,-1)
    assert name0=="original" and name1=="local_rotate4"
    assert orig==original
    assert observed==(orig if source_regime=="original" else rotated)
    assert collections.Counter(orig)==collections.Counter(rotated)
    assert len(orig)==len(rotated)==72
    return orig,rotated

def public_prefix_descriptors(public,pack,F62):
    """Only previous native F60 retained memory and current PUBLIC event.

    Cumulative returned counters are OFFLINE analysis outputs; not free
    persistent online policy state or admissible external metadata.
    """
    memory=()
    joins=0
    touches=0
    alternatives=0
    observed=0
    for index,event in enumerate(public):
        assert len(event)==3
        if 12<=index<48:
            observed+=1
            a,role,b=event
            touch=any(a in (u,v) or b in (u,v) for u,v,_ in memory)
            join=any(v==a or u==b for u,v,_ in memory)
            choices=F62.actions(memory,event,index,pack)
            baseline=F62._f60_step(memory,event,pack)
            assert sum(x[3]==baseline for x in choices)==1
            touches+=int(touch)
            joins+=int(join)
            alternatives+=len(choices)-1
        memory=F62._f60_step(memory,event,pack)
        F62._valid_memory(memory,pack)
    assert observed==36 and len(memory)<=12
    return dict(prefix_positions=36,
                memory_endpoint_touches=touches,
                directed_memory_joins=joins,
                native_alternatives=alternatives,
                final_record_count=len(memory))

def paired_graph(seed,family,F76,F94,F84,F85,pack,F62):
    observed,q,meta=F76.source(seed,family)
    assert meta["arrival_regime"] in ("original","local_rotate4")
    orig,rotated=matched_orders(observed,meta["arrival_regime"],F76)
    assert F84.independently_resolve_public(orig,q)[0]=={q["answer"]}
    assert F84.independently_resolve_public(rotated,q)[0]=={q["answer"]}
    report={}
    for label,public in (("original",orig),("local_rotate4",rotated)):
        desc=public_prefix_descriptors(public,pack,F62)
        identity=dict(meta,seed=seed,family=family,arrival_regime=label)
        historical=F94.evaluate_case(public,q,identity,F62,F85,F84,pack)
        assert historical["seed"]==seed and historical["family"]==family
        assert historical["regime"]==label
        report[label]=dict(
            f60_correct=historical["f60_correct"],
            rescue_feasible=historical["one_step_rescue"],
            harmful_alternative_exists=historical["one_step_harm"],
            safe_overlap_rescue=historical["safe_overlap_rescue"],
            safe_overlap_harm=historical["safe_overlap_harm"],
            legal_single_deviation_actions=historical["alternatives"],
            rescue_by_period={p:historical["by_period"][p]["rescue_actions"]
                              for p in ("early","middle","late")},
            harm_by_period={p:historical["by_period"][p]["harm_actions"]
                            for p in ("early","middle","late")},
            public_descriptors=desc)
    return dict(seed=seed,source_family=family,
                question_type=meta["question_type"],
                F63C_regime=meta["original_F63C_regime"],
                pair_same_graph_and_question=True,
                original=report["original"],
                rotated=report["local_rotate4"])

def paired_summary(rows):
    orig=lambda r:r["original"]
    rot=lambda r:r["rotated"]
    return dict(
        graphs=len(rows),episodes=len(rows)*2,
        four_step_graphs=sum(r["question_type"]=="within_component_4_steps" for r in rows),
        six_step_graphs=sum(r["question_type"]=="crosslink_reach_6_steps" for r in rows),
        F60_original_correct=sum(orig(r)["f60_correct"] for r in rows),
        F60_rotated_correct=sum(rot(r)["f60_correct"] for r in rows),
        F60_original_only_correct=sum(orig(r)["f60_correct"] and not rot(r)["f60_correct"]
                                       for r in rows),
        F60_rotated_only_correct=sum(rot(r)["f60_correct"] and not orig(r)["f60_correct"]
                                      for r in rows),
        F60_both_correct=sum(orig(r)["f60_correct"] and rot(r)["f60_correct"]
                              for r in rows),
        F60_both_incorrect=sum(not orig(r)["f60_correct"] and not rot(r)["f60_correct"]
                                for r in rows),
        hindsight_six_step_rescue_original=sum(
            r["question_type"]=="crosslink_reach_6_steps" and
            orig(r)["rescue_feasible"] for r in rows),
        hindsight_six_step_rescue_rotated=sum(
            r["question_type"]=="crosslink_reach_6_steps" and
            rot(r)["rescue_feasible"] for r in rows),
        hindsight_six_step_rescue_rotated_only=sum(
            r["question_type"]=="crosslink_reach_6_steps" and
            rot(r)["rescue_feasible"] and not orig(r)["rescue_feasible"] for r in rows),
        hindsight_six_step_rescue_original_only=sum(
            r["question_type"]=="crosslink_reach_6_steps" and
            orig(r)["rescue_feasible"] and not rot(r)["rescue_feasible"] for r in rows),
        harmful_F60_correct_cases_original=sum(orig(r)["f60_correct"] and
                                  orig(r)["harmful_alternative_exists"] for r in rows),
        harmful_F60_correct_cases_rotated=sum(rot(r)["f60_correct"] and
                                  rot(r)["harmful_alternative_exists"] for r in rows),
        native_one_deviation_alternatives_original=sum(orig(r)["legal_single_deviation_actions"] for r in rows),
        native_one_deviation_alternatives_rotated=sum(rot(r)["legal_single_deviation_actions"] for r in rows),
        joins_observed_original=sum(orig(r)["public_descriptors"]["directed_memory_joins"] for r in rows),
        joins_observed_rotated=sum(rot(r)["public_descriptors"]["directed_memory_joins"] for r in rows),
        endpoint_touches_original=sum(orig(r)["public_descriptors"]["memory_endpoint_touches"] for r in rows),
        endpoint_touches_rotated=sum(rot(r)["public_descriptors"]["memory_endpoint_touches"] for r in rows),
        native_candidate_count_original=sum(orig(r)["public_descriptors"]["native_alternatives"] for r in rows),
        native_candidate_count_rotated=sum(rot(r)["public_descriptors"]["native_alternatives"] for r in rows))

def run(mode):
    assert gitblob(HERE/"prereg.json")==PREREG_BLOB,"F96_PREREG_DRIFT"
    cfg=json.loads((HERE/"prereg.json").read_text())
    assert cfg["stage"]=="FROZEN_PRECODE_MATCHED_PAIRS_SOURCE_ONLY_NO_ONLINE_POLICY"
    assert gitblob(ROOT/"20261016-y-f76"/"source.py")==F76_BLOB
    expected=cfg["paired_source"]["calibration" if mode=="calibration" else "heldout"]
    seeds=COHORTS[mode]
    assert list(seeds)==list(range(expected["seeds_start"],expected["seeds_stop_exclusive"],expected["step"]))
    assert len(seeds)*len(FAMILIES)==expected["distinct_graphs"]
    F95=load_exact("f96_frozen_F95",ROOT/"20261016-y-f95"/"risk_lookup.py",F95_BLOB)
    F94=F95.load("f96_frozen_F94",ROOT/"20261016-y-f94"/"single_deviation_feasibility.py",F95.F94_SHA)
    F93=F94.load_exact("f96_frozen_F93",ROOT/"20261016-y-f93b"/"role_grammar.py",F94.F93_BLOB)
    F92=F93.load("f96_frozen_F92",ROOT/"20261016-y-f92"/"dense_path_credit.py",F93.F92_BLOB)
    F91=F92.load("f96_frozen_F91",ROOT/"20261016-y-f91"/"conservative_credit.py",F92.F91_BLOB)
    F90=F91.loader("f96_frozen_F90",ROOT/"20261016-y-f90"/"temporal_credit.py",F91.F90_BLOB)
    F89=F90.load_checked("f96_frozen_F89",ROOT/"20261016-y-f89r"/"graded_exchange.py",F90.F89R_METHOD_BLOB)
    F88=F89.load_exact("f96_frozen_F88",ROOT/"20261016-y-f88"/"frontier.py",F89.F88_BLOB)
    F87=F88.load_exact("f96_frozen_F87",ROOT/"20261016-y-f87b"/"bridge_reserve.py",F88.F87B_BLOB)
    F86=F87.load("f96_frozen_F86",ROOT/"20261016-y-f86"/"queryblind_retention.py",F87.F86_SHA)
    F85=F86.load_exact("f96_frozen_F85",ROOT/"20261016-y-f85"/"global_solver.py",F86.F85_METHOD_BLOB)
    F84=F85.checked_loader("f96_frozen_F84",ROOT/"20261016-y-f84"/"forensic_reachability.py",F85.F84_SHA)
    F83=F84.load_f83()
    F76=F83.M.SOURCE
    pack=F83.M.PACK
    F62=F83.M.F62
    rows=[]
    for seed in seeds:
        for family in FAMILIES:
            rows.append(paired_graph(seed,family,F76,F94,F84,F85,pack,F62))
    assert len(rows)==expected["distinct_graphs"]
    assert all(r["pair_same_graph_and_question"] for r in rows)
    assert any(r["question_type"]=="within_component_4_steps" for r in rows)
    assert any(r["question_type"]=="crosslink_reach_6_steps" for r in rows)
    return dict(
        schema="yggdrasil.f96.matched-public-order-native-feasibility.v1",
        stage=("CALIBRATION_SOURCE_DIAGNOSTIC_ONLY" if mode=="calibration"
               else "HELDOUT_PAIRED_SOURCE_DIAGNOSTIC_FIRST_USE"),
        mode=mode,
        classification="matched_order_observational_diagnostic_not_policy_qualification",
        source_graphs=len(rows),paired_order_episodes=len(rows)*2,
        summary=paired_summary(rows),
        by_original_source_family={str(f):paired_summary([r for r in rows if r["source_family"]==f])
                                   for f in FAMILIES},
        by_question_type={k:paired_summary([r for r in rows if r["question_type"]==k])
                          for k in ("within_component_4_steps","crosslink_reach_6_steps")},
        source_graph_and_task_exactly_matched=True,
        all_original_public_answers_independently_verified=True,
        all_native_actions_exactly_enumerated=True,
        retrospective_oracle_uses_future_and_answer=True,
        online_policy_qualified=False,
        public_descriptor_state_is_offline_only=True,
        native_memory_bytes_max=144,
        fitted_policy=False,scientific_accepted=False,
        no_protected_FIT=True,no_DIAG=True,no_original=True,no_F3=True,
        no_controller_mutation=True,no_optimizer_promotion=True,
        rows=rows)

if __name__=="__main__":
    if sys.argv[1:]==["--calibration-only"]:
        print(json.dumps(run("calibration"),sort_keys=True))
    elif sys.argv[1:]==["--heldout-first-use-only"]:
        print(json.dumps(run("heldout"),sort_keys=True))
    else:
        raise SystemExit("F96 denies protected experiments, learned policy fitting, or unregistered sources")
