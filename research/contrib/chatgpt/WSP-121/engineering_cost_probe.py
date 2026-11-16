"""WSP-121 matched *engineering-only* numerical/symbolic process-cost probe.

Only 121900..121903 are legal. Same source owner, public graph, disclosed
observations, held scoring and cold-restore requirement for both implementations.
Informational timing: no source-science admission, no energy measurements,
no significance test and no original-world data consumption.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import platform
from statistics import median
from time import perf_counter_ns

import meta_operator as M
import source_custody as C

ARMS = ("NUMERIC_FAST", "SYMBOLIC_TABLE_STRONG")
PHASES = ("source", "train", "infer", "cold_restore")
WORLD_IDS = (121900, 121901, 121902, 121903)


def _digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"))
                  .encode("utf-8")).hexdigest()


def _restore_symbolic(model):
    """Optimized direct lookup serialization; no artificial slow enumeration."""
    blob = json.dumps(sorted(model.table.items()), separators=(",", ":"))
    records = json.loads(blob)
    if (type(records) is not list or
            any(type(item) is not list or len(item) != 2 or
                type(item[0]) is not int or not 0 <= item[0] < 8 or
                type(item[1]) is not int or item[1] not in (0, 1)
                for item in records)):
        raise ValueError("WSP121_COST_SYMBOLIC_COLD_INVALID")
    restored = M.SymbolicMemo()
    restored.table = {k: v for k, v in records}
    if len(restored.table) != len(records):
        raise ValueError("WSP121_COST_SYMBOLIC_DUPLICATE")
    return restored


def _single_arm(name):
    if name not in ARMS:
        raise ValueError("WSP121_COST_UNKNOWN_ARM")
    start = perf_counter_ns()
    learner = (M.NumericFastWeights() if name == "NUMERIC_FAST"
               else M.SymbolicMemo())
    durations = dict.fromkeys(PHASES, 0)
    durations["train"] += perf_counter_ns() - start
    receipts = []
    for seed in WORLD_IDS:
        start = perf_counter_ns()
        custodian = C.EngineeringCustodian(seed)
        public = custodian.public
        world = M.PublicWorld(seed, public.graph, public.legal, public.held)
        # Independently owned engineering source: never ask for held labels.
        observations = tuple((s, custodian.query(s))
                             for s in public.legal[:custodian.budget])
        source_digest = custodian.source_sha256
        view_digest = public.fingerprint()
        durations["source"] += perf_counter_ns() - start

        start = perf_counter_ns()
        for subject, outcome in observations:
            learner.observe(world, subject, outcome)
        durations["train"] += perf_counter_ns() - start

        start = perf_counter_ns()
        predictions = {s: learner.infer(world, s) for s in public.held}
        scored = custodian.score_held_once(predictions)
        durations["infer"] += perf_counter_ns() - start
        if (scored["source_sha256"] != source_digest or
                scored["public_sha256"] != view_digest or
                scored["source_calls"] != custodian.budget or
                scored["source_first_use"] or scored["scientific_pass"] or
                scored["native_admission"]):
            raise AssertionError("WSP121_COST_SOURCE_OR_STATUS_MISMATCH")

        start = perf_counter_ns()
        learner = (M.NumericFastWeights.restore(learner.snapshot())
                   if name == "NUMERIC_FAST" else _restore_symbolic(learner))
        restored = {s: learner.infer(world, s) for s in public.held}
        durations["cold_restore"] += perf_counter_ns() - start
        if restored != predictions:
            raise AssertionError("WSP121_COST_COLD_PREDICTIONS_DIFFER")
        receipts.append({
            "seed": seed, "source_sha256": source_digest,
            "public_sha256": view_digest,
            "held_predictions_sha256": scored["held_predictions_sha256"],
            "budget": custodian.budget, "correct": scored["correct"],
            "wrong_confident": scored["wrong_confident"],
            "abstained": scored["abstained"],
        })
    if sum(row["budget"] for row in receipts) != 24:
        raise AssertionError("WSP121_COST_QUERY_BUDGET")
    return {"parts_ns": durations, "total_ns": sum(durations.values()),
            "receipts": receipts, "receipt_sha256": _digest(receipts)}


def run_probe(repeats=7):
    if type(repeats) is not int or not 1 <= repeats <= 15:
        raise ValueError("WSP121_COST_INVALID_REPEAT_COUNT")
    if set(WORLD_IDS) != C.ENGINEERING or set(WORLD_IDS) & (C.PRIMARY | C.PROTECTED):
        raise PermissionError("WSP121_COST_WORLD_FENCE")
    trials = []
    for i in range(repeats):
        # Rotate ordering to mitigate systematic warmup/runner ordering bias.
        order = ARMS if i % 2 == 0 else tuple(reversed(ARMS))
        current = {name: _single_arm(name) for name in order}
        n, s = current[ARMS[0]], current[ARMS[1]]
        if n["receipt_sha256"] != s["receipt_sha256"] or n["receipts"] != s["receipts"]:
            raise AssertionError("WSP121_COST_MATCHED_EVIDENCE_OR_SCORE_PARITY")
        trials.append(current)

    medians = {
        name: {
            "whole_seconds": median(t[name]["total_ns"] for t in trials) / 1e9,
            "source_seconds": median(t[name]["parts_ns"]["source"]
                                     for t in trials) / 1e9,
            "train_seconds": median(t[name]["parts_ns"]["train"]
                                    for t in trials) / 1e9,
            "infer_seconds": median(t[name]["parts_ns"]["infer"]
                                    for t in trials) / 1e9,
            "cold_restore_seconds": median(t[name]["parts_ns"]["cold_restore"]
                                           for t in trials) / 1e9,
        }
        for name in ARMS
    }
    nums = [t[ARMS[0]]["total_ns"] for t in trials]
    syms = [t[ARMS[1]]["total_ns"] for t in trials]
    ratios = [s / n for n, s in zip(nums, syms)]
    return {
        "schema": "wsp121.engineering-matched-cost.v1",
        "status": "DEVELOPMENT_INFORMATION_ONLY",
        "scientific_pass": False, "first_use": False, "native_admission": False,
        "worlds": list(WORLD_IDS), "worlds_per_arm": len(WORLD_IDS),
        "source_calls_per_arm": 24, "held_scored_per_arm": 96,
        "repeats": repeats, "ordering": "alternating_AB_BA",
        "platform": platform.system(), "python": platform.python_version(),
        "platform_machine": platform.machine(),
        "matched_receipts_sha256": trials[0][ARMS[0]]["receipt_sha256"],
        "receipts_stable": all(
            t[ARMS[0]]["receipt_sha256"] == trials[0][ARMS[0]]["receipt_sha256"]
            for t in trials),
        "medians": medians,
        "paired_speedup_symbolic_over_numeric": [round(x, 6) for x in ratios],
        "median_speedup_symbolic_over_numeric": round(median(ratios), 6),
        "exploratory_2x_reached": median(ratios) >= 2.0,
        "caveats": [
            "Four repeated engineering world IDs are not independent science worlds",
            "Whole-path includes source birth, verified observations, fit, "
            "full held scoring and cold restoration",
            "Current Python implementations, not optimized native backends",
            "No independent original source, calibrated energy or per-arm RSS",
            "Paired timing is noisy and does not establish frozen 95% CI",
            "Only necessary strong symbolic cost comparator probed, not trained MLP",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=7)
    args = parser.parse_args()
    print("WSP121_ENGINEERING_COST_JSON=" +
          json.dumps(run_probe(args.repeats), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
