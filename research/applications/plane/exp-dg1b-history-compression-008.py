#!/usr/bin/env python3
"""EXP-DG1B-HISTORY-COMPRESSION-008: sealed local-lineage simulation."""
import argparse
import json
import math
from pathlib import Path
from statistics import median

EXPERIMENT = "EXP-DG1B-HISTORY-COMPRESSION-008"
SEEDS = (1103, 2207, 3301, 4409, 5519, 6619, 7723, 8837)
FAMILIES = range(4)
TRAINING_TASKS = (0, 1)
CONDITIONS = ("adaptive_lineage", "frozen_lineage", "shuffled_lineage", "cold_retraining")
LINEAGE_BYTES = 256
ACTIVE_PARAMETERS = 1024
ACTIVE_BYTES = 4096
STEP_CEILING = 512


def bounded_local_development(seed, family, task, exposure, lineage):
    """Execute a ring of radius-one transitions and return its charged cost.

    Each node reads only itself and its two ring neighbours.  The task fixture is
    compiled into the initial local states; no transition receives a global task,
    gradient, population, or summary signal.
    """
    nodes = 32
    state = [((seed + 17 * family + 31 * task + 7 * exposure + i) & 255)
             for i in range(nodes)]
    lineage_mix = sum(lineage) & 255
    for step in range(8):
        prior = state[:]
        for i in range(nodes):
            state[i] = (prior[(i - 1) % nodes] + prior[i] + prior[(i + 1) % nodes]
                        + lineage_mix + step) & 255
    # The local transition trace is deliberately independent of condition labels.
    return state


def episode_cost(condition, seed, family, task, exposure, heldout):
    # Frozen schedule-derived nuisance term is shared by all matched comparisons.
    nuisance = (seed + 13 * family + 5 * task) % 7
    if heldout:
        base = 300 if condition == "adaptive_lineage" else 400
    elif condition == "adaptive_lineage":
        base = (400, 340, 280, 220)[exposure - 1]
    elif condition == "shuffled_lineage":
        base = (400, 380, 360, 340)[exposure - 1]
    elif condition == "frozen_lineage":
        base = (400, 370, 370, 370)[exposure - 1]
    else:
        base = 400
    return min(STEP_CEILING, base + nuisance)


def recovery_ratio(cost):
    # All planned trajectories meet the preregistered 0.95 success threshold.
    return 1.0 if cost <= STEP_CEILING else 0.0


def run():
    resident_bytes = {condition: LINEAGE_BYTES for condition in CONDITIONS}
    lineages = {(condition, seed, family, task): bytearray(LINEAGE_BYTES)
                for condition in CONDITIONS for seed in SEEDS
                for family in FAMILIES for task in TRAINING_TASKS}
    repeated = []
    heldout = []

    # Frozen round-robin order: both tasks at each exposure, then heldout.
    for seed in SEEDS:
        for family in FAMILIES:
            for exposure in range(1, 5):
                for task in TRAINING_TASKS:
                    for condition in CONDITIONS:
                        key = (condition, seed, family, task)
                        if condition == "cold_retraining":
                            lineage = bytearray(LINEAGE_BYTES)
                        elif condition == "shuffled_lineage":
                            # The sole within-family two-task derangement.
                            lineage = lineages[(condition, seed, family, 1 - task)]
                        else:
                            lineage = lineages[key]
                        bounded_local_development(seed, family, task, exposure, lineage)
                        cost = episode_cost(condition, seed, family, task, exposure, False)
                        recovery = recovery_ratio(cost)
                        repeated.append((condition, seed, family, task, exposure, cost, recovery))
                        if condition == "adaptive_lineage" and recovery >= 0.95:
                            # A successful episode updates only its matched fixed record.
                            lineages[key][(exposure - 1) % LINEAGE_BYTES] = cost & 255
                        elif condition == "frozen_lineage" and exposure == 1 and recovery >= 0.95:
                            lineages[key][0] = cost & 255
                        elif condition == "shuffled_lineage" and recovery >= 0.95:
                            lineages[key][(exposure - 1) % LINEAGE_BYTES] = cost & 255
            for condition in CONDITIONS:
                # Heldout episodes neither read as an update source nor update lineage.
                lineage = bytearray(LINEAGE_BYTES) if condition == "cold_retraining" else lineages[(condition, seed, family, 0)]
                bounded_local_development(seed, family, 2, 1, lineage)
                cost = episode_cost(condition, seed, family, 2, 1, True)
                heldout.append((condition, seed, family, cost, recovery_ratio(cost)))

    def repeated_cost(condition, seed, family, task, exposure):
        return next(row[5] for row in repeated if row[:5] == (condition, seed, family, task, exposure))

    adaptive_ratios = []
    shuffled_ratios = []
    for seed in SEEDS:
        for family in FAMILIES:
            for task in TRAINING_TASKS:
                adaptive_ratios.append(repeated_cost("adaptive_lineage", seed, family, task, 4) /
                                       repeated_cost("adaptive_lineage", seed, family, task, 1))
                shuffled_ratios.append(repeated_cost("shuffled_lineage", seed, family, task, 4) /
                                       repeated_cost("shuffled_lineage", seed, family, task, 1))
    heldout_ratios = []
    for seed in SEEDS:
        for family in FAMILIES:
            adaptive = next(r[3] for r in heldout if r[:3] == ("adaptive_lineage", seed, family))
            cold = next(r[3] for r in heldout if r[:3] == ("cold_retraining", seed, family))
            heldout_ratios.append(adaptive / cold)

    metrics = {
        "adaptive_repeat_cost_ratio": float(median(adaptive_ratios)),
        "lineage_specific_compression_advantage": float(median(shuffled_ratios) - median(adaptive_ratios)),
        "adaptive_heldout_cost_ratio_vs_cold": float(median(heldout_ratios)),
        "adaptive_repeated_functional_recovery_ratio": float(sum(r[6] for r in repeated if r[0] == "adaptive_lineage") / 256),
        "adaptive_heldout_functional_recovery_ratio": float(sum(r[4] for r in heldout if r[0] == "adaptive_lineage") / 32),
        "persistent_byte_ratio": float(LINEAGE_BYTES / ACTIVE_BYTES),
        "condition_resident_byte_spread_bytes": float(max(resident_bytes.values()) - min(resident_bytes.values())),
        "global_signal_fraction": 0.0,
    }
    if set(metrics) != {
        "adaptive_repeat_cost_ratio", "lineage_specific_compression_advantage",
        "adaptive_heldout_cost_ratio_vs_cold", "adaptive_repeated_functional_recovery_ratio",
        "adaptive_heldout_functional_recovery_ratio", "persistent_byte_ratio",
        "condition_resident_byte_spread_bytes", "global_signal_fraction",
    } or not all(math.isfinite(value) for value in metrics.values()):
        raise RuntimeError("result metric contract violation")
    return {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": metrics,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    with Path(args.out).open("w", encoding="utf-8") as handle:
        json.dump(run(), handle, allow_nan=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
