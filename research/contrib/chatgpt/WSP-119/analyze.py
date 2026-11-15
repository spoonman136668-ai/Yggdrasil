"""WSP119 frozen public-only microfeedback test.

Compare identical factual graph exposure and external answer-query budgets:
direct-active error feedback, direct-passive (no curiosity), no-update,
and independent exact symbolic active. No protected source or real corpus.
"""
from __future__ import annotations
from collections import defaultdict
from hashlib import sha256
import json
import random
import statistics
import struct
import time

import microfeedback as F


def _checkpoint(world, graph, true_law, learner, source, arm, t):
    held=F.held_subjects(world)
    if any(s in source.used for s in held):
        raise AssertionError("WSP119_HELD_SOURCE_EXPOSED")
    if learner.count!=t if isinstance(learner,F.NumericFeedback) else len(learner.observed)!=t:
        raise AssertionError("WSP119_WRONG_SOURCE_EXPOSURE")
    prediction=[learner.infer(s) for s in held]
    if isinstance(learner,F.NumericFeedback):
        sealed=learner.snapshot()
        restored=F.NumericFeedback.restore(graph,sealed)
        if restored.snapshot()!=sealed or [restored.infer(s) for s in held]!=prediction:
            raise AssertionError("WSP119_NUMERIC_COLD_MEMBERSHIP_CHANGED")
    # The unseen truth is read ONLY by this scorer, AFTER predictions.
    truth=[world.actual(s,true_law) for s in held]
    correct=sum(p is not None and p==v for p,v in zip(prediction,truth))
    emitted=sum(p is not None for p in prediction)
    return {
        "seed":world.seed,"law_index":world.targets.index(true_law),
        "tier":sum(len(edges) for edges in graph),
        "arm":arm,"exposure":t,
        "law_identified":int(learner.law()==true_law),
        "law_declared":int(learner.law() is not None),
        "held_correct":correct,"held_issued":emitted,
        "held_wrong":emitted-correct,
        "feedback_count":source.count,
        "visible_contradiction_feedback":learner.total_error_events if isinstance(learner,F.NumericFeedback) else None
    }


def _world_bootstrap(diffs, seed=1190):
    if len(diffs)!=24:raise AssertionError("WSP119_WRONG_WORLD_PAIRING")
    rng=random.Random(seed)
    draws=sorted(statistics.mean(diffs[rng.randrange(len(diffs))]
                     for _ in diffs) for i in range(10000))
    return {"mean":statistics.mean(diffs),"ci95":[draws[249],draws[9749]]}


def run_public():
    start=time.perf_counter()
    receipt=sha256()
    source_receipt=sha256()
    rows=[]
    per_world={}
    cold_checks=0
    active_symbolic_differences=0
    number_different_queries=0
    total_world_tasks=0
    source_calls_per_arm={a:0 for a in F.ARM_NAMES}

    for seed in F.PUBLIC_SEEDS:
        world=F.source_safe_world(seed)
        for threshold in F.TIERS:
            graph=world.public_graph(threshold)
            for law_index,true_law in enumerate(world.targets):
                total_world_tasks+=1
                pool=F.inquiry_pool(world)
                learners={
                    "DIRECT_ACTIVE":F.NumericFeedback(graph,active=True),
                    "DIRECT_PASSIVE":F.NumericFeedback(graph,active=False),
                    "DIRECT_NO_UPDATE":F.NumericFeedback(graph,active=False,updates=False),
                    "SYMBOLIC_ACTIVE":F.IndependentSymbolicFeedback(graph)
                }
                sources={name:F.EvidenceSource(world,true_law) for name in F.ARM_NAMES}
                selected_queries={name:[] for name in F.ARM_NAMES}

                for t in range(F.MAX_SOURCE_CALLS+1):
                    if t in F.EXPOSURES:
                        checkpoint={}
                        for arm in F.ARM_NAMES:
                            entry=_checkpoint(world,graph,true_law,learners[arm],sources[arm],arm,t)
                            entry["threshold"]=threshold
                            rows.append(entry)
                            checkpoint[arm]=entry
                        # Same evidence and same active utility must yield
                        # identical independent numeric/symbolic predictions.
                        a=checkpoint["DIRECT_ACTIVE"]
                        s=checkpoint["SYMBOLIC_ACTIVE"]
                        if any(a[k]!=s[k] for k in ("held_correct","held_issued",
                                      "held_wrong","law_identified","law_declared")):
                            active_symbolic_differences+=1
                            raise AssertionError("WSP119_EXACT_SYMBOLIC_MICROFEEDBACK_MISMATCH")
                        for arm in ("DIRECT_ACTIVE","DIRECT_PASSIVE","DIRECT_NO_UPDATE"):
                            learner=learners[arm]
                            sealed=learner.snapshot()
                            restored=F.NumericFeedback.restore(graph,sealed)
                            if restored.snapshot()!=sealed:
                                raise AssertionError("WSP119_COLD_STATE_MISMATCH")
                            cold_checks+=1

                    if t==F.MAX_SOURCE_CALLS:break
                    for arm in F.ARM_NAMES:
                        learner=learners[arm]
                        subject=learner.choose(pool)
                        # The source is an independently generated, guarded
                        # environment; its answer is unavailable to choose().
                        answer=sources[arm].query(subject)
                        learner.observe(subject,answer)
                        selected_queries[arm].append(subject)
                        source_calls_per_arm[arm]+=1
                        source_receipt.update(struct.pack("<IHHBB",seed,threshold,law_index,
                                                          F.ARM_NAMES.index(arm),t))
                        source_receipt.update(struct.pack("<II",subject,answer))
                if selected_queries["DIRECT_ACTIVE"]!=selected_queries["SYMBOLIC_ACTIVE"]:
                    active_symbolic_differences+=1
                    raise AssertionError("WSP119_ACTIVE_SOURCE_CHOICE_SYMBOLIC_MISMATCH")
                if selected_queries["DIRECT_ACTIVE"]!=selected_queries["DIRECT_PASSIVE"]:
                    number_different_queries+=1
                if any(len(q)!=12 for q in selected_queries.values()):
                    raise AssertionError("WSP119_INCOMPLETE_MATCHED_BUDGET")

    # Only cumulative, per-exposure aggregates are returned. Avoid printing
    # individual world hidden program types or all training source responses.
    summary={}
    for tier in F.TIERS:
        summary[str(tier)]={}
        for n in F.EXPOSURES:
            bucket={}
            for arm in F.ARM_NAMES:
                items=[r for r in rows if r["threshold"]==tier and
                       r["exposure"]==n and r["arm"]==arm]
                if len(items)!=len(F.PUBLIC_SEEDS)*4:
                    raise AssertionError("WSP119_INCOMPLETE_WORLD_COUNTS")
                total=len(items)*24
                bucket[arm]={
                    "laws_correct":sum(v["law_identified"] for v in items),
                    "held_correct":sum(v["held_correct"] for v in items),
                    "held_accuracy":sum(v["held_correct"] for v in items)/total,
                    "held_wrong":sum(v["held_wrong"] for v in items),
                    "held_issued":sum(v["held_issued"] for v in items)
                }
            summary[str(tier)][str(n)]=bucket

    paired={}
    for tier in (192,256):
        for n in F.EXPOSURES:
            diffs=[]
            for seed in F.PUBLIC_SEEDS:
                def per_world(arm):
                    subset=[x for x in rows if x["seed"]==seed and
                            x["threshold"]==tier and x["exposure"]==n and
                            x["arm"]==arm]
                    assert len(subset)==4
                    return sum(x["held_correct"] for x in subset)/(4*24)
                diffs.append(per_world("DIRECT_ACTIVE")-per_world("DIRECT_PASSIVE"))
            paired[str(tier)+":"+str(n)]=_world_bootstrap(diffs)
    rules=(summary["192"]["8"]["DIRECT_ACTIVE"]["held_accuracy"]-
           summary["192"]["8"]["DIRECT_PASSIVE"]["held_accuracy"]>=0.05 and
           summary["256"]["8"]["DIRECT_ACTIVE"]["held_accuracy"]-
           summary["256"]["8"]["DIRECT_PASSIVE"]["held_accuracy"]>=0.05 and
           paired["192:8"]["ci95"][0]>0 and
           paired["256:8"]["ci95"][0]>0 and
           active_symbolic_differences==0 and
           all(a==4608 for a in source_calls_per_arm.values()))
    receipt.update(json.dumps(rows,sort_keys=True,separators=(",",":")).encode())
    return {
        "schema":"wsp119.public-synthetic-internal-microfeedback.v1",
        "classification":"PUBLIC_MICROFEEDBACK_SIGNAL_SYMBOLIC_TIE" if rules else
                         "PUBLIC_MICROFEEDBACK_NO_GO_OR_STRONG_CONTROL_TIE",
        "preregistered_dev_signal":bool(rules),
        "scientific_pass":False,"native_model_modified":False,
        "real_source_opened":False,"reserved_science_opened":False,
        "exact_symbolic_active_mismatches":active_symbolic_differences,
        "cold_numeric_checkpoint_checks":cold_checks,
        "source_queries":source_calls_per_arm,
        "world_tasks":total_world_tasks,
        "active_differed_from_passive_tasks":number_different_queries,
        "case_receipt_sha256":receipt.hexdigest(),
        "source_action_response_receipt_sha256":source_receipt.hexdigest(),
        "coverage_exposure_aggregate":summary,
        "paired_world_active_minus_passive":paired,
        "elapsed_seconds":time.perf_counter()-start,
        "limitation":"Public synthetic known three-hop grammar, same exact symbolic control, no independently unknown law type, no independent science"
    }


if __name__=="__main__":
    print("WSP119_PUBLIC_MICROFEEDBACK="+json.dumps(run_public(),sort_keys=True))
