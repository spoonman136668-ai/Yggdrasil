"""WSP-118 public fixture-only knowledge coverage curve.

This does not use real Wikidata or protected science. It quantifies when
three-edge source graph evidence becomes enough to infer a pre-specified family
of triple relational laws; it does not measure the onset of intelligence.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import random
import statistics
import time

import mechanism as M


def bootstrap_worlds(world_rows):
    """Paired 100%-versus-25% held accuracy, worlds as independent clusters."""
    by_seed={}
    for row in world_rows:
        by_seed.setdefault(row["seed"],{}).setdefault(row["threshold"],[]).append(row["correct"]/M.HELD_SOURCES)
    per_world=[]
    for seed in M.PUBLIC_SEEDS:
        v=by_seed[seed]
        assert set(v)==set(M.DENSITIES)
        per_world.append(statistics.mean(v[256])-statistics.mean(v[64]))
    rng=random.Random(1180)
    simulations=[]
    for _ in range(10_000):
        pick=[per_world[rng.randrange(len(per_world))] for _ in per_world]
        simulations.append(statistics.mean(pick))
    simulations.sort()
    return {"mean":statistics.mean(per_world),
            "ci95":[simulations[249],simulations[9749]]}


def inspect_all_public():
    t0=time.perf_counter()
    raw_rows=[]
    source_hash=sha256()
    parity_mismatches=0
    failed_cold=0
    for seed in M.PUBLIC_SEEDS:
        world=M.new_public_world(seed)
        # Only this evaluator sees the source-hidden target-law tuples. Both
        # inference algorithms get visible_graph plus public demonstrations.
        for threshold in M.DENSITIES:
            graph=world.public_graph(threshold)
            visible_count=sum(len(x) for x in graph)
            source_hash.update(seed.to_bytes(4,"little"))
            source_hash.update(threshold.to_bytes(2,"little"))
            for rel in graph:
                for s,o in sorted(rel.items()):
                    source_hash.update(bytes((s,o)))
            for law_index,true_law in enumerate(world.targets):
                examples=world.public_examples(true_law)
                direct=M.NumericTripleWeights(graph,threshold).learn(examples)
                symbolic=M.ExactSymbolicSynthesizer(graph).learn(examples)
                checkpoint=direct.snapshot()
                clone=M.NumericTripleWeights.restore(graph,checkpoint)
                if checkpoint!=clone.snapshot():
                    failed_cold+=1
                    raise AssertionError("WSP118_COLD_READBACK_CHANGED")
                if direct.law()!=symbolic.law():
                    parity_mismatches+=1
                    raise AssertionError("WSP118_INDEPENDENT_SYMBOLIC_LAW_MISMATCH")

                # Source-safe hard controls use ONLY current public graph and
                # witnessed examples. No held targets until AFTER predictions.
                short=M.short_grammar_control(graph,examples)
                shuffled=M.NumericTripleWeights(graph,threshold).learn(
                    M.shuffled_examples(examples,seed,law_index))
                held=world.held_subjects()
                assert not set(held).intersection(s for s,_ in examples)
                d_pred=[direct.infer(s) for s in held]
                symbolic_pred=[symbolic.infer(s) for s in held]
                restored_pred=[clone.infer(s) for s in held]
                short_pred=[M.visible_walk(graph,s,short) if short is not None else None
                            for s in held]
                shuffle_pred=[shuffled.infer(s) for s in held]
                # Memorizing only demos cannot cover any unseen held subject.
                demo_memorizer={s:o for s,o in examples}
                memorized=[demo_memorizer.get(s) for s in held]
                if d_pred!=symbolic_pred or d_pred!=restored_pred:
                    parity_mismatches+=1
                    raise AssertionError("WSP118_PUBLIC_HELD_PREDICTION_MISMATCH")
                truth=[world.actual(s,true_law) for s in held]

                def score(pred):
                    issued=sum(x is not None for x in pred)
                    correct=sum(x is not None and x==y for x,y in zip(pred,truth))
                    return (correct,issued,issued-correct)
                correct,issued,wrong=score(d_pred)
                short_correct,short_issued,short_wrong=score(short_pred)
                shuffled_correct,shuffled_issued,shuffled_wrong=score(shuffle_pred)
                memorized_correct,memorized_issued,_=score(memorized)
                if memorized_correct or memorized_issued:
                    raise AssertionError("WSP118_LEAKED_HELD_SOURCE_TO_MEMORIZER")
                raw_rows.append({
                    "seed":seed,"threshold":threshold,"law_number":law_index,
                    "public_facts":visible_count,
                    "numeric_correct_law":int(direct.law()==true_law),
                    "numeric_declared_law":int(direct.law() is not None),
                    "correct":correct,"issued":issued,"wrong":wrong,
                    "twohop_correct":short_correct,"twohop_issued":short_issued,
                    "twohop_wrong":short_wrong,
                    "shuffled_correct":shuffled_correct,
                    "shuffled_issued":shuffled_issued,
                    "shuffled_wrong":shuffled_wrong,
                    "direct_storage_bytes":len(direct.synapses)*direct.synapses.itemsize
                })

    rows_by_tier={}
    for threshold in M.DENSITIES:
        group=[x for x in raw_rows if x["threshold"]==threshold]
        expected_cases=len(M.PUBLIC_SEEDS)*4
        assert len(group)==expected_cases
        held_total=expected_cases*M.HELD_SOURCES
        rows_by_tier[str(threshold)]={
            "label":next(x["label"] for x in _TIER_DISPLAY if x["value"]==threshold),
            "worlds":len(M.PUBLIC_SEEDS),"task_law_cases":len(group),
            "total_held_queries":held_total,
            "mean_visible_foundation_facts":sum(x["public_facts"] for x in group)/len(group),
            "law_identified":sum(x["numeric_correct_law"] for x in group),
            "law_declared":sum(x["numeric_declared_law"] for x in group),
            "numeric_top1_correct":sum(x["correct"] for x in group),
            "numeric_top1_accuracy":sum(x["correct"] for x in group)/held_total,
            "numeric_issued":sum(x["issued"] for x in group),
            "numeric_wrong":sum(x["wrong"] for x in group),
            "twohop_top1_correct":sum(x["twohop_correct"] for x in group),
            "twohop_wrong":sum(x["twohop_wrong"] for x in group),
            "shuffled_top1_correct":sum(x["shuffled_correct"] for x in group),
            "shuffled_wrong":sum(x["shuffled_wrong"] for x in group),
            "memorization_correct":0
        }
    boot=bootstrap_worlds(raw_rows)
    full=rows_by_tier["256"];quarter=rows_by_tier["64"]
    passing=(full["numeric_top1_accuracy"]>=.8 and
             full["numeric_top1_accuracy"]-quarter["numeric_top1_accuracy"]>=.2 and
             boot["ci95"][0]>0 and parity_mismatches==0 and failed_cold==0 and
             rows_by_tier["0"]["numeric_issued"]==0)
    first_half_law=None
    for threshold in M.DENSITIES:
        if rows_by_tier[str(threshold)]["law_identified"]>=len(M.PUBLIC_SEEDS)*4*.5:
            first_half_law=threshold
            break
    receipt=sha256(json.dumps(raw_rows,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return {
        "schema":"wsp118.public-synthetic-foundation-density.v1",
        "classification":("SOURCE_SAFE_DENSITY_SIGNAL_WITH_EXACT_SYMBOLIC_TIE" if passing
                          else "SOURCE_SAFE_DENSITY_NO_GO"),
        "public_fixture_only":True,
        "scientific_pass":False,
        "native_model_modified":False,
        "protected_first_use":False,
        "real_wikidata_source_rescanned":False,
        "original_predefined_threehop_grammar":True,
        "source_worlds":len(M.PUBLIC_SEEDS),
        "relation_laws_per_world":4,
        "foundation_levels":len(M.DENSITIES),
        "source_public_graph_sha256":source_hash.hexdigest(),
        "all_case_metrics_sha256":receipt,
        "direct_learned_int32_bytes":len(M.TRIPLES)*2*4,
        "symbolic_disagreements":parity_mismatches,
        "cold_restore_errors":failed_cold,
        "first_density_with_at_least_50pct_law_identification":first_half_law,
        "paired_world_full_vs_quarter":boot,
        "tier_results":rows_by_tier,
        "elapsed_seconds":time.perf_counter()-t0
    }


_TIER_DISPLAY=[
    {"label":"0%","value":0},{"label":"6.25%","value":16},
    {"label":"25%","value":64},{"label":"50%","value":128},
    {"label":"75%","value":192},{"label":"87.5%","value":224},
    {"label":"100%","value":256}
]


if __name__=="__main__":
    print("WSP118_PUBLIC_FIXTURE_RESULT="+json.dumps(inspect_all_public(),sort_keys=True))
