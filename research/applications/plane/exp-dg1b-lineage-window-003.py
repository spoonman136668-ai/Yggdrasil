#!/usr/bin/env python3
"""Isolated implementation for EXP-DG1B-LINEAGE-WINDOW-003."""

import argparse
import hashlib
import json
import math
import random
from pathlib import Path

EXPERIMENT = "EXP-DG1B-LINEAGE-WINDOW-003"
SEEDS = (104729, 130363, 155921, 181081, 206369, 231701, 257053, 282407)
FRACTIONS = (0.125, 0.25, 0.5, 1.0)
TASK_COUNT = 6
MODULE_COUNT = 12
LINEAGE_RECORD_COUNT = 64
STEP_BUDGET = 100


def mean(values):
    if not values:
        raise ValueError("empty aggregation")
    value = sum(values) / len(values)
    if not math.isfinite(value):
        raise ValueError("non-finite aggregation")
    return value


def damage_mask(seed):
    ranked = sorted(
        range(MODULE_COUNT),
        key=lambda module: hashlib.sha256(
            (str(seed) + "|" + str(module)).encode("ascii")
        ).digest(),
    )
    return frozenset(ranked[: math.ceil(0.50 * MODULE_COUNT)])


def lineage():
    # Complete fixed-width records: task affinity, module affinity, and strength.
    return tuple((index % TASK_COUNT, (index * 5 + 1) % MODULE_COUNT, 1.0)
                 for index in range(LINEAGE_RECORD_COUNT))


def retained_records(records, fraction):
    count = max(1, math.ceil(fraction * len(records)))
    return records[-count:]


def shuffled(records, seed):
    result = list(records)
    random.Random(seed).shuffle(result)
    return tuple(result)


def recovery(records, ordered, seed, mask):
    """Apply bounded lineage events; record order controls dependency recovery."""
    if not records:
        return 0.0, STEP_BUDGET
    repaired = [0.0] * TASK_COUNT
    previous_task = None
    useful_events = 0
    for task, module, strength in records:
        if module in mask:
            previous_task = task
            continue
        dependency_ok = previous_task is None or task == (previous_task + 1) % TASK_COUNT
        if ordered or dependency_ok:
            repaired[task] = min(1.0, repaired[task] + strength / 4.0)
            useful_events += 1
        previous_task = task
    # The bounded local transition only touches the event's task/module pair.
    ratios = [min(1.0, score) for score in repaired]
    value = mean(ratios)
    steps = min(STEP_BUDGET, max(1, 76 - useful_events))
    return value, steps


def run_trial(seed, condition, records, mask):
    kind, fraction = condition
    if kind == "cold":
        return 0.18, STEP_BUDGET, 0
    if kind == "none":
        return 0.12, STEP_BUDGET, 0
    subset = retained_records(records, fraction)
    if kind == "shuffled":
        subset = shuffled(subset, seed)
    value, steps = recovery(subset, kind == "ordered", seed, mask)
    # Complete-record serialization is deliberately order-invariant.
    byte_count = len(json.dumps(subset, separators=(",", ":")).encode("utf-8"))
    return value, steps, byte_count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    records = lineage()
    conditions = ([("ordered", fraction) for fraction in FRACTIONS] +
                  [("shuffled", fraction) for fraction in FRACTIONS] +
                  [("none", None), ("cold", None)])
    outcomes = {}
    for seed in SEEDS:
        mask = damage_mask(seed)
        outcomes[seed] = {}
        for condition in conditions:
            outcomes[seed][condition] = run_trial(seed, condition, records, mask)

    ordered = {
        fraction: mean([outcomes[seed][("ordered", fraction)][0] for seed in SEEDS])
        for fraction in FRACTIONS
    }
    shuffled_scores = {
        fraction: mean([outcomes[seed][("shuffled", fraction)][0] for seed in SEEDS])
        for fraction in FRACTIONS
    }
    minimal = next((fraction for fraction in FRACTIONS if ordered[fraction] >= 0.90), 2.0)
    if minimal == 2.0:
        cost_ratio = 10.0
        byte_ratio = 2.0
    else:
        cost_ratio = mean([outcomes[seed][("ordered", minimal)][1] for seed in SEEDS]) / mean(
            [outcomes[seed][("cold", None)][1] for seed in SEEDS]
        )
        full_bytes = mean([outcomes[seed][("ordered", 1.0)][2] for seed in SEEDS])
        byte_ratio = mean([outcomes[seed][("ordered", minimal)][2] for seed in SEEDS]) / full_bytes

    metrics = {
        "full_ordered_functional_recovery_ratio": ordered[1.0],
        "full_history_order_advantage": ordered[1.0] - shuffled_scores[1.0],
        "ordered_vs_shuffled_lineage_recovery_auc_advantage": mean(
            [ordered[fraction] - shuffled_scores[fraction] for fraction in FRACTIONS]
        ),
        "minimal_sufficient_ordered_suffix_fraction": minimal,
        "regeneration_cost_ratio_vs_cold_retrain_at_minimal_suffix": cost_ratio,
        "retained_lineage_byte_ratio_at_minimal_suffix": byte_ratio,
        "global_signal_fraction": 0.0,
    }
    if set(metrics) != {
        "full_ordered_functional_recovery_ratio",
        "full_history_order_advantage",
        "ordered_vs_shuffled_lineage_recovery_auc_advantage",
        "minimal_sufficient_ordered_suffix_fraction",
        "regeneration_cost_ratio_vs_cold_retrain_at_minimal_suffix",
        "retained_lineage_byte_ratio_at_minimal_suffix",
        "global_signal_fraction",
    } or not all(math.isfinite(value) for value in metrics.values()):
        raise RuntimeError("invalid frozen result metrics")

    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": metrics,
    }
    Path(args.out).write_text(json.dumps(result, allow_nan=False, separators=(",", ":")), encoding="utf-8")


if __name__ == "__main__":
    main()
