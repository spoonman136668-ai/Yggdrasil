"""WSP89 frozen sourced-knowledge recall and simulated source-conflict study.

This is NOT unseen real-world knowledge transfer: original Wikidata claim
objects are explicitly observed by both candidate and controls.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import random
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from source import read_frozen
from weights import (
    CORRECTION, DECOY, DirectEvidenceWeights, FullyTrainedSigmoidControl,
    SymbolicEvidenceControl, canonical,
)

PREREG = json.loads((HERE / "prereg.json").read_text(encoding="utf-8"))
FIXTURE = tuple(PREREG["source_collection"]["fixture_subjects"])
RESERVED = tuple(PREREG["source_collection"]["reserved_dev_subjects"])

def queries(rows: list[dict]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted({(r["subject"], r["predicate"]) for r in rows}))

def oracle(rows: list[dict]) -> dict[tuple[str, str], dict]:
    expected = defaultdict(lambda: {"values": set(), "citations": []})
    for row in rows:
        if row["source_type"] == DECOY:
            continue
        ans = expected[(row["subject"], row["predicate"])]
        ans["values"].add(row["object"])
        ans["citations"].append({
            "value": row["object"], "source_url": row["source_url"],
            "statement_id": row["statement_id"],
            "source_type": row["source_type"], "revision": row.get("revision"),
        })
    return {k: {
        "values": tuple(sorted(v["values"])),
        "citations": tuple(sorted(v["citations"],
                           key=lambda x:(x["value"], x["statement_id"]))),
    } for k,v in expected.items()}

def freeze(*outputs: object) -> str:
    return hashlib.sha256(canonical(outputs).encode("ascii")).hexdigest()

def truth_rows(model: SymbolicEvidenceControl) -> list[dict]:
    return [dict(row) for row in model.active.values() if row["source_type"] != DECOY]

def decoy_events(rows: list[dict], seed: int) -> list[dict]:
    answers = oracle(rows)
    alternatives: dict[str, set[str]] = defaultdict(set)
    for r in rows:
        alternatives[r["predicate"]].add(r["object"])
    keys = list(queries(rows))
    random.Random(seed).shuffle(keys)
    out = []
    for sub, pid in keys:
        current = set(answers[(sub,pid)]["values"])
        choices = sorted(alternatives[pid] - current)
        if not choices:
            continue
        wrong = choices[(seed + len(out)) % len(choices)]
        out.append({
            "subject": sub, "predicate": pid, "object": wrong,
            "statement_id": f"CF-UNTRUSTED-{seed}-{len(out)}",
            "source_url": f"counterfactual:wsp89:{seed}:decoy:{len(out)}",
            "revision": None, "source_type": DECOY,
        })
        if len(out) >= 12:
            break
    return out

def correction_events(rows: list[dict], seed: int) -> list[tuple[str, dict]]:
    by_key: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        by_key[(row["subject"], row["predicate"])].append(row)
    options: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        options[row["predicate"]].add(row["object"])
    keys = sorted(k for k, group in by_key.items() if len(group) == 1)
    random.Random(seed + 42).shuffle(keys)
    corrections = []
    for sub, pid in keys:
        old = by_key[(sub,pid)][0]
        replacement = sorted(options[pid] - {old["object"]})
        if not replacement:
            continue
        new_value = replacement[(seed + len(corrections)) % len(replacement)]
        row = {
            "subject": sub, "predicate": pid, "object": new_value,
            "statement_id": f"CF-CORRECTION-{seed}-{len(corrections)}",
            "source_url": f"counterfactual:wsp89:{seed}:correction:{len(corrections)}",
            "revision": None, "source_type": CORRECTION,
        }
        corrections.append((old["statement_id"], row))
        if len(corrections) >= 8:
            break
    return corrections

def study(corpus: dict, *, dev: bool) -> dict:
    t0 = time.process_time_ns()
    seed = PREREG["seeds"]["dev_first_use" if dev else "fixture"]
    subjects = set(RESERVED if dev else FIXTURE)
    rows = [dict(r) for r in corpus["claims"] if r["subject"] in subjects]
    expected_keys = queries(rows)
    numeric, graph = DirectEvidenceWeights(), SymbolicEvidenceControl()

    candidate_start = time.process_time_ns()
    for row in rows:
        numeric.assert_evidence(row)
    candidate_stageA_cpu = time.process_time_ns() - candidate_start
    for row in rows:
        graph.assert_evidence(row)

    learned = FullyTrainedSigmoidControl()
    conventional_start = time.process_time_ns()
    learned.fit(rows)
    conventional_stageA_cpu = time.process_time_ns() - conventional_start
    stage_a_numeric = tuple(numeric.answer(*q) for q in expected_keys)
    stage_a_symbolic = tuple(graph.answer(*q) for q in expected_keys)
    stage_a_sgd = tuple(learned.answer(*q) for q in expected_keys)
    cold_stage_a = numeric.snapshot()
    stage_a_frozen_sha = freeze(stage_a_numeric, stage_a_symbolic, stage_a_sgd)
    # Source truth is evaluated only once all models have produced their answers.
    stage_a_truth = oracle(rows)
    exact_stage_a = sum(ans == stage_a_truth[q]
                        for q, ans in zip(expected_keys, stage_a_numeric))
    attribution_correct = sum(
        ans == stage_a_truth[q] for q, ans in zip(expected_keys, stage_a_numeric))
    independent_parity_a = stage_a_numeric == stage_a_symbolic
    trained_correct_a = sum(
        ans == stage_a_truth[q]["values"] for q, ans in zip(expected_keys, stage_a_sgd))

    decoys = decoy_events(rows, seed)
    for row in decoys:
        numeric.assert_evidence(row)
        graph.assert_evidence(row)
    stage_b_numeric = tuple(numeric.answer(*q) for q in expected_keys)
    stage_b_graph = tuple(graph.answer(*q) for q in expected_keys)
    decoy_rejections = sum(
        (numeric.answer(r["subject"], r["predicate"]) ==
         stage_a_truth[(r["subject"], r["predicate"])] and
         all(c["statement_id"] != r["statement_id"] for c in
             numeric.answer(r["subject"], r["predicate"])["citations"]))
        for r in decoys)
    cold_after_decoys = numeric.snapshot()
    corrections = correction_events(rows, seed)
    affected = set()
    for old_sid, new_row in corrections:
        affected.add((new_row["subject"], new_row["predicate"]))
        numeric.retract_evidence(old_sid)
        numeric.assert_evidence(new_row)
        graph.retract_evidence(old_sid)
        graph.assert_evidence(new_row)

    unaffected = [q for q in expected_keys if q not in affected]
    post_numeric = tuple(numeric.answer(*q) for q in expected_keys)
    post_graph = tuple(graph.answer(*q) for q in expected_keys)
    corrected_predictions = tuple(numeric.answer(*q) for q in sorted(affected))
    stable_predictions = tuple(numeric.answer(*q) for q in unaffected)
    unknown_pairs = ((("Q999999999999", "P36"), ("Q16", "P999999999999"),
                      ("Q888888888888", "P999999999999")))
    unknown_preds = tuple(numeric.answer(*q) for q in unknown_pairs)

    conventional_start = time.process_time_ns()
    learned.fit(truth_rows(graph))
    conventional_stageC_cpu = time.process_time_ns() - conventional_start
    stage_c_sgd = tuple(learned.answer(*q) for q in expected_keys)
    cold_stage_c = numeric.snapshot()
    restored = DirectEvidenceWeights.restore(cold_stage_c)
    restore_bitwise_equal = restored.snapshot() == cold_stage_c
    old_cold = DirectEvidenceWeights.restore(cold_stage_a)
    cold_old_equal = (old_cold.snapshot() == cold_stage_a and
                      tuple(old_cold.answer(*q) for q in expected_keys) ==
                      stage_a_numeric)
    decoy_cold = DirectEvidenceWeights.restore(cold_after_decoys)
    decoy_cold_equal = (decoy_cold.snapshot() == cold_after_decoys and
                        tuple(decoy_cold.answer(*q) for q in expected_keys) ==
                        stage_b_numeric)

    # Explicit zero-weight negative; citation journal alone cannot answer.
    zeroed = DirectEvidenceWeights.restore(cold_stage_c)
    for weights in zeroed.weights.values():
        for obj in list(weights):
            weights[obj] = 0.0
    zero_control_none = all(zeroed.answer(*q) is None for q in expected_keys)

    tampered = json.loads(cold_stage_c)
    one_key = next(iter(tampered["payload"]["weights"]))
    one_object = next(iter(tampered["payload"]["weights"][one_key]))
    tampered["payload"]["weights"][one_key][one_object] += 0.5
    tamper_rejected = False
    try:
        DirectEvidenceWeights.restore(json.dumps(tampered))
    except ValueError:
        tamper_rejected = True

    final_hash = freeze(post_numeric, post_graph, stage_c_sgd, unknown_preds)
    expected_c = oracle(truth_rows(graph))
    correction_correct = sum(
        numeric.answer(*key) == expected_c[key] for key in affected)
    retained_correct = sum(
        numeric.answer(*key) == stage_a_truth[key] for key in unaffected)
    sgd_correct_c = sum(
        ans == expected_c[q]["values"] for q,ans in zip(expected_keys, stage_c_sgd))
    return {
        "schema": "wsp89.source-backed-factual-dev-result.v1",
        "cohort": "RESERVED_DEV_FIRST_USE" if dev else "PUBLIC_FIXTURE",
        "source_claims_sha256": corpus["claims_sha256"],
        "stageA_queries": len(expected_keys), "stageA_correct": exact_stage_a,
        "source_attribution_correct": attribution_correct,
        "stageA_training_claims": len(rows),
        "independent_symbolic_parity_all_stages": (
            independent_parity_a and stage_b_numeric == stage_b_graph
            and post_numeric == post_graph),
        "decoys_total": len(decoys), "decoys_rejected": decoy_rejections,
        "counterfactual_corrections_total": len(affected),
        "counterfactual_corrections_correct": correction_correct,
        "unaffected_total": len(unaffected),
        "unaffected_retained": retained_correct,
        "unknown_confident": sum(x is not None for x in unknown_preds),
        "cold_restore_bitwise": (
            restore_bitwise_equal and cold_old_equal and decoy_cold_equal),
        "tamper_rejected": tamper_rejected,
        "zero_weight_negative": zero_control_none,
        "SGD_stageA_correct": trained_correct_a,
        "SGD_stageC_correct": sgd_correct_c,
        "SGD_fit_accuracy": learned.training_accuracy,
        "SGD_last_mean_BCE": learned.mean_bce,
        "candidate_stageA_cpu_ns": candidate_stageA_cpu,
        "conventional_stageA_cpu_ns": conventional_stageA_cpu,
        "conventional_stageC_cpu_ns": conventional_stageC_cpu,
        "whole_process_cpu_ns": time.process_time_ns() - t0,
        "numerical_slots": numeric.numeric_weight_slots(),
        "source_ledger_events": numeric.evidence_count(),
        "predictions_frozen_before_scoring_sha256": stage_a_frozen_sha,
        "post_correction_prediction_sha256": final_hash,
        "interpretation": ("Real CC0 source claims were directly observed; recall "
                          "and correction of the same claims is not transfer."),
    }

def classify(result: dict, *, dev: bool) -> dict:
    threshold = PREREG["frozen_thresholds"]
    min_positive = threshold["min_real_claim_predictions"] if dev else 6
    checks = {
        "real_claim_coverage": result["stageA_training_claims"] >= min_positive,
        "source_claim_precision": (result["stageA_correct"] == result["stageA_queries"]),
        "source_revision_attribution": (
            result["source_attribution_correct"] == result["stageA_queries"]),
        "independent_symbolic_parity": result["independent_symbolic_parity_all_stages"],
        "false_decoys_resisted": (
            result["decoys_total"] >= (8 if dev else 2) and
            result["decoys_rejected"] == result["decoys_total"]),
        "counterfactual_corrections": (
            result["counterfactual_corrections_total"] >= (4 if dev else 1) and
            result["counterfactual_corrections_correct"] ==
            result["counterfactual_corrections_total"]),
        "unaffected_retention": (
            result["unaffected_total"] > 0 and
            result["unaffected_retained"] == result["unaffected_total"]),
        "unknown_abstention": result["unknown_confident"] == 0,
        "cold_restore": result["cold_restore_bitwise"],
        "tamper_detection": result["tamper_rejected"],
        "zero_weight_negative": result["zero_weight_negative"],
        "trained_SGD_baseline": (
            result["SGD_fit_accuracy"] >= threshold["trained_control_training_accuracy_min"]
            and result["SGD_stageA_correct"] == result["stageA_queries"]
            and result["SGD_stageC_correct"] == result["stageA_queries"]),
        "whole_CPU_and_state_report": (
            # Windows CPU clocks can quantize sub-millisecond work to 0 ns.
            # Preserve the reported zero as a measured resolution limit;
            # require a positive entire-process measurement.
            result["whole_process_cpu_ns"] > 0 and
            result["candidate_stageA_cpu_ns"] >= 0 and
            result["conventional_stageA_cpu_ns"] >= 0 and
            result["conventional_stageC_cpu_ns"] >= 0 and
            result["numerical_slots"] > 0 and
            result["source_ledger_events"] > 0)
    }
    return {
        **result, "checks": checks, "passed_checks": sum(checks.values()),
        "total_checks": len(checks),
        "classification": (
            ("DEV_SOURCE_KNOWLEDGE_FEASIBLE" if all(checks.values())
             else "DEV_SOURCE_KNOWLEDGE_NEGATIVE") if dev
            else ("FIXTURE_FEASIBLE" if all(checks.values())
                  else "FIXTURE_NEGATIVE")),
        "scientific_acceptance": "UNVERIFIED",
        "general_intelligence_or_language_mastery": False,
        "symbolic_or_conventional_superiority": False,
        "deployment": "NONE",
    }

def main():
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--public-fixture-only", action="store_true")
    modes.add_argument("--reserved-dev-first-use", action="store_true")
    args = parser.parse_args()
    corpus = read_frozen()
    report = classify(study(corpus, dev=args.reserved_dev_first_use),
                      dev=args.reserved_dev_first_use)
    print("WSP89_RESULT=" + canonical(report))

if __name__ == "__main__":
    main()
