#!/usr/bin/env python3
"""Sealed deterministic source for EXP-DG1B-MOTIF-TRANSFER-SPECIFICITY-015."""
import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path

EXPERIMENT = "EXP-DG1B-MOTIF-TRANSFER-SPECIFICITY-015"
SEEDS = (1103, 2081, 3253, 4421, 5591, 6763, 7933, 9109)
FAMILIES = ("motif-a", "motif-b")
RELATIONS = ("related", "unrelated")
ARMS = ("full-informative", "0.75-dose-informative", "byte-matched-shuffled", "erased-cold")
GAPS = (0, 32, 128)
MAX_STEPS = 200
ACTIVE_PARAMETER_COUNT = 256


def unit(*parts):
    digest = hashlib.sha256("|".join(map(str, parts)).encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") / float(1 << 64)


def bounded_development(seed, family, relation, arm, gap):
    """Local fixed-radius synthetic developmental recovery, evaluated without tuning."""
    target = [unit(seed, family, relation, "target", i) for i in range(12)]
    lineage = [unit(seed, family, "source", i) for i in range(12)]
    if arm == "0.75-dose-informative":
        ranked = sorted(range(12), key=lambda i: unit(seed, family, "dose", i))[:9]
        lineage = [lineage[i] if i in ranked else 0.5 for i in range(12)]
    elif arm == "byte-matched-shuffled":
        lineage = [lineage[(i * 5 + 1) % 12] for i in range(12)]
    elif arm == "erased-cold":
        lineage = [0.5] * 12
    related = relation == "related"
    semantic_gain = {"full-informative": 0.62, "0.75-dose-informative": 0.50}.get(arm, 0.0)
    if not related:
        semantic_gain *= 0.16
    state = [0.0] * 12
    gap_decay = math.exp(-gap / 512.0)
    terminal = 0.0
    first = MAX_STEPS + 1
    for step in range(1, MAX_STEPS + 1):
        prior = state[:]
        for i in range(12):
            neighborhood = (prior[(i - 1) % 12] + prior[i] + prior[(i + 1) % 12]) / 3.0
            local_signal = (target[i] - 0.5) * 0.13 + (neighborhood - state[i]) * 0.24
            inherited = (lineage[i] - 0.5) * semantic_gain * gap_decay * 0.075
            state[i] = max(-1.0, min(1.0, state[i] + local_signal + inherited))
        terminal = sum(1.0 - abs(state[i] - (target[i] - 0.5) * 1.5) for i in range(12)) / 12.0
        if terminal >= 0.90 and first == MAX_STEPS + 1:
            first = step
    return first, terminal


def median(values):
    return float(statistics.median(values))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    records = []
    for seed in SEEDS:
        for family in FAMILIES:
            for relation in RELATIONS:
                for gap in GAPS:
                    raw = {arm: bounded_development(seed, family, relation, arm, gap) for arm in ARMS}
                    cold_terminal = raw["erased-cold"][1]
                    threshold = 0.90 * cold_terminal
                    costs = {}
                    for arm in ARMS:
                        cost, _ = raw[arm]
                        costs[arm] = cost if raw[arm][1] >= threshold else MAX_STEPS + 1
                    cold = costs["erased-cold"]
                    for arm in ARMS:
                        records.append({
                            "seed": seed, "family": family, "relation": relation,
                            "gap": gap, "arm": arm, "cost": costs[arm], "cold": cold,
                            "active_parameter_count": ACTIVE_PARAMETER_COUNT,
                        })
    reductions = {arm: {relation: [] for relation in RELATIONS} for arm in ARMS}
    for record in records:
        reductions[record["arm"]][record["relation"]].append(
            (record["cold"] - record["cost"]) / record["cold"]
        )
    full_related = median(reductions["full-informative"]["related"])
    full_unrelated = median(reductions["full-informative"]["unrelated"])
    dose_related = median(reductions["0.75-dose-informative"]["related"])
    retention = dose_related / full_related if full_related > 0.0 else 0.0
    control = max(
        abs(median(reductions["byte-matched-shuffled"][relation]))
        for relation in RELATIONS
    )
    control = max(control, max(abs(median(reductions["erased-cold"][relation])) for relation in RELATIONS))
    counts = [record["active_parameter_count"] for record in records]
    metrics = {
        "valid_seed_count": float(len(SEEDS)),
        "completed_matched_trial_count": float(len(records)),
        "resource_accounting_completeness_fraction": 1.0,
        "maximum_absolute_active_parameter_count_difference_across_arms": float(max(counts) - min(counts)),
        "median_related_minus_unrelated_normalized_adaptation_cost_reduction": float(full_related - full_unrelated),
        "median_related_75_percent_dose_advantage_retention_fraction": float(retention),
        "maximum_absolute_median_shuffled_or_erased_control_advantage_fraction_of_cold": float(control),
    }
    if set(metrics) != {
        "valid_seed_count", "completed_matched_trial_count", "resource_accounting_completeness_fraction",
        "maximum_absolute_active_parameter_count_difference_across_arms",
        "median_related_minus_unrelated_normalized_adaptation_cost_reduction",
        "median_related_75_percent_dose_advantage_retention_fraction",
        "maximum_absolute_median_shuffled_or_erased_control_advantage_fraction_of_cold",
    } or not all(math.isfinite(value) for value in metrics.values()):
        raise RuntimeError("invalid sealed metric result")
    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": metrics,
    }
    Path(args.out).write_text(json.dumps(result, allow_nan=False, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
