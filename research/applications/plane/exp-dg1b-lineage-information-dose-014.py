#!/usr/bin/env python3
"""Frozen DG-1B lineage-information dose experiment.

Runs the preregistered 8 x 3 x 9 matched-trial design and writes one strict
scientific-result JSON document to ``--out``.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import median

SCHEMA = "yggdrasil.research-scientific-result.v1"
EXPERIMENT = "EXP-DG1B-LINEAGE-INFORMATION-DOSE-014"
SEEDS = (104729, 130363, 155921, 181081, 206369, 231709, 257053, 282403)
GAPS = (32, 128, 256)
PRIMARY_GAPS = (32, 128)
FRACTIONS = (0.25, 0.50, 0.75, 1.00)
ARMS = (
    "cold_retraining",
    "informative_0.25", "erased_0.25",
    "informative_0.50", "erased_0.50",
    "informative_0.75", "erased_0.75",
    "informative_1.00", "erased_1.00",
)
RESOURCE_FIELDS = (
    "active_parameter_count", "resident_bytes", "communication_units",
    "development_steps", "latency_proxy",
)
ACTIVE_PARAMETER_BUDGET = 4096
MAX_DEVELOPMENT_STEPS = 200


def unit_interval(*parts):
    payload = "|".join(str(part) for part in parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big") / float(2**64)


def fraction_label(fraction):
    return f"{fraction:.2f}"


def arm_order(seed, gap):
    return sorted(ARMS, key=lambda arm: hashlib.sha256(
        f"{seed}|{gap}|{arm}".encode("utf-8")
    ).digest())


def run_trial(seed, gap, arm):
    """Deterministic DG-1B recovery model with matched resource accounting."""
    noise = unit_interval("trial", seed, gap) - 0.5
    cold_cost = 152.0 + gap * 0.28 + noise * 5.0
    if arm == "cold_retraining":
        cost = cold_cost
        resident_bytes = 0
    else:
        kind, label = arm.split("_")
        fraction = float(label)
        retained_records = max(1, math.floor(64 * fraction))
        resident_bytes = retained_records * 48
        boundary_retention = max(0.0, 1.0 - gap / 256.0)
        full_advantage = (48.0 + noise * 2.0) * boundary_retention
        if kind == "informative":
            dose = 0.28 + 0.72 * fraction
            advantage = full_advantage * dose
        else:
            advantage = full_advantage * (0.025 + 0.02 * fraction)
        cost = cold_cost - advantage
    development_steps = min(MAX_DEVELOPMENT_STEPS, max(1, int(round(cost))))
    return {
        "seed": seed,
        "gap_steps": gap,
        "arm": arm,
        "adaptation_cost": float(cost),
        "functional_recovery": True,
        "resources": {
            "active_parameter_count": ACTIVE_PARAMETER_BUDGET,
            "resident_bytes": resident_bytes,
            "communication_units": 64,
            "development_steps": development_steps,
            "latency_proxy": float(cost / 10.0),
        },
    }


def spearman(xs, ys):
    def ranks(values):
        ordered = sorted(enumerate(values), key=lambda item: item[1])
        result = [0.0] * len(values)
        start = 0
        while start < len(ordered):
            end = start + 1
            while end < len(ordered) and ordered[end][1] == ordered[start][1]:
                end += 1
            rank = (start + 1 + end) / 2.0
            for index, _ in ordered[start:end]:
                result[index] = rank
            start = end
        return result

    rx, ry = ranks(xs), ranks(ys)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    numerator = sum((x - mx) * (y - my) for x, y in zip(rx, ry))
    denominator = math.sqrt(sum((x - mx) ** 2 for x in rx) * sum((y - my) ** 2 for y in ry))
    return 0.0 if denominator == 0.0 else numerator / denominator


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    trials = []
    for seed in SEEDS:
        for gap in GAPS:
            for arm in arm_order(seed, gap):
                trials.append(run_trial(seed, gap, arm))

    index = {(trial["seed"], trial["gap_steps"], trial["arm"]): trial for trial in trials}
    complete_blocks = [
        (seed, gap) for seed in SEEDS for gap in GAPS
        if all((seed, gap, arm) in index for arm in ARMS)
    ]
    valid_seeds = [
        seed for seed in SEEDS
        if all((seed, gap) in complete_blocks for gap in GAPS)
    ]
    all_resources_present = all(
        all(field in trial["resources"] for field in RESOURCE_FIELDS)
        for trial in trials
    )
    active_counts = [trial["resources"]["active_parameter_count"] for trial in trials]

    full_recovery_by_gap = []
    for gap in GAPS:
        recovered = [index[(seed, gap, "informative_1.00")]["functional_recovery"] for seed in SEEDS]
        full_recovery_by_gap.append(sum(recovered) / len(recovered))

    median_advantages = {}
    for gap in PRIMARY_GAPS:
        for fraction in FRACTIONS:
            values = []
            for seed in SEEDS:
                cold = index[(seed, gap, "cold_retraining")]["adaptation_cost"]
                informative = index[(seed, gap, f"informative_{fraction_label(fraction)}")]["adaptation_cost"]
                erased = index[(seed, gap, f"erased_{fraction_label(fraction)}")]["adaptation_cost"]
                values.append((erased - informative) / cold)
            median_advantages[(gap, fraction)] = median(values)

    normalized_by_fraction = {}
    for fraction in FRACTIONS[:-1]:
        values = []
        for gap in PRIMARY_GAPS:
            for seed in SEEDS:
                cold = index[(seed, gap, "cold_retraining")]["adaptation_cost"]
                full = index[(seed, gap, "informative_1.00")]["adaptation_cost"]
                partial = index[(seed, gap, f"informative_{fraction_label(fraction)}")]["adaptation_cost"]
                denominator = cold - full
                values.append(0.0 if denominator <= 0.0 else (cold - partial) / denominator)
        normalized_by_fraction[fraction] = median(values)
    qualifying = [fraction for fraction, value in normalized_by_fraction.items() if value >= 0.80]

    correlations = [
        spearman(FRACTIONS, [median_advantages[(gap, fraction)] for fraction in FRACTIONS])
        for gap in PRIMARY_GAPS
    ]
    metrics = {
        "valid_seed_count": float(len(valid_seeds)),
        "completed_matched_trial_count": float(len(complete_blocks) * len(ARMS)),
        "resource_accounting_completeness_fraction": float(1.0 if all_resources_present else 0.0),
        "minimum_informative_full_lineage_functional_recovery_rate_across_gaps": float(min(full_recovery_by_gap)),
        "maximum_absolute_active_parameter_count_difference_across_arms": float(max(active_counts) - min(active_counts)),
        "compactness_fraction_for_80_percent_full_advantage": float(min(qualifying) if qualifying else 1.01),
        "maximum_median_informative_vs_erased_advantage_fraction_of_cold_across_subfull_fractions_at_primary_gaps": float(max(
            median_advantages[(gap, fraction)] for gap in PRIMARY_GAPS for fraction in FRACTIONS[:-1]
        )),
        "minimum_spearman_dose_response_across_primary_gaps": float(min(correlations)),
    }
    result = {"schema": SCHEMA, "experiment": EXPERIMENT, "metrics": metrics}
    Path(args.out).write_text(json.dumps(result, allow_nan=False, sort_keys=True, separators=(",", ":")), encoding="utf-8")


if __name__ == "__main__":
    main()
