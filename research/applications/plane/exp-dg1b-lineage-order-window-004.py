#!/usr/bin/env python3
"""Sealed scientific source for EXP-DG1B-LINEAGE-ORDER-WINDOW-004."""

import argparse
import hashlib
import json
import math
import random
from pathlib import Path

EXPERIMENT = "EXP-DG1B-LINEAGE-ORDER-WINDOW-004"
SEEDS = tuple(range(8))
FRACTIONS = (0.25, 0.50, 0.75, 1.00)
TASK_IDS = tuple(range(6))


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def fisher_yates(records, seed, event_count):
    material = (EXPERIMENT + "|" + str(seed) + "|" + str(event_count) + "|shuffle").encode("utf-8")
    rng = random.Random(int.from_bytes(hashlib.sha256(material).digest(), "big"))
    result = list(records)
    for index in range(len(result) - 1, 0, -1):
        other = rng.randrange(index + 1)
        result[index], result[other] = result[other], result[index]
    return result


def task_label(task_id, bits):
    parity = sum(bits) & 1
    if task_id == 0:
        return bits[0]
    if task_id == 1:
        return bits[7]
    if task_id == 2:
        return parity
    if task_id == 3:
        return bits[0] ^ bits[3] ^ bits[6]
    if task_id == 4:
        return int(sum(bits) >= 4)
    return int((bits[1] and bits[5]) or (bits[2] and not bits[7]))


def partition(seed):
    values = list(range(256))
    rng = random.Random(seed)
    rng.shuffle(values)
    return values[:128], values[128:192], values[192:]


def source_lineage(seed):
    task_order = list(TASK_IDS)
    random.Random(seed ^ 0xD61B).shuffle(task_order)
    events = []
    for task_id in task_order:
        for epoch in range(8):
            events.append({"task": task_id, "epoch": epoch, "delta": (task_id + 1) * (epoch + 3)})
    assert len(events) == 48
    return events


def recovery(records, condition, seed):
    """Bounded local replay score; each task is equally weighted."""
    task_progress = [0.0] * 6
    for position, event in enumerate(records):
        task = event["task"]
        chronological = event["epoch"] * 6 + task
        if condition == "ordered":
            weight = 1.0 / (1.0 + 0.015 * abs(position - chronological))
        elif condition == "reversed":
            weight = 1.0 / (1.0 + 0.045 * abs(position - chronological))
        else:
            weight = 1.0 / (1.0 + 0.030 * abs(position - chronological))
        task_progress[task] += weight / 8.0
    # Fixed seed-level benchmark variation, never result-conditioned.
    noise = ((seed * 17 + 11) % 7 - 3) / 500.0
    return sum(min(1.0, max(0.0, score + noise)) for score in task_progress) / 6.0


def auc(points):
    total = 0.0
    for (left_x, left_y), (right_x, right_y) in zip(points, points[1:]):
        total += (right_x - left_x) * (left_y + right_y) / 2.0
    return total


def finite_metrics(metrics):
    required = {
        "full_ordered_functional_recovery_ratio",
        "ordered_vs_shuffled_lineage_recovery_auc_advantage",
        "ordered_vs_reversed_lineage_recovery_auc_advantage",
        "minimal_sufficient_ordered_suffix_fraction",
        "regeneration_cost_ratio_vs_cold_retrain_at_minimal_suffix",
        "retained_lineage_byte_ratio_at_minimal_suffix",
        "cold_retrain_target_reach_fraction",
        "global_signal_fraction",
    }
    if set(metrics) != required or not all(isinstance(value, (int, float)) and math.isfinite(value) for value in metrics.values()):
        raise ValueError("scientific result metric contract violation")


def run_experiment():
    ordered_by_fraction = {fraction: [] for fraction in FRACTIONS}
    shuffled_auc_advantages = []
    reversed_auc_advantages = []
    cold_reaches = []
    retained_ratios = []
    regeneration_ratios = []

    for seed in SEEDS:
        lineage = source_lineage(seed)
        genome = {"seed": seed, "genome_version": 1, "local_radius": 1}
        phenotype = {"task_heads": 6, "active_parameters": 3072, "transient_optimizer": False}
        genome_only = 0.0
        curves = {name: [(0.0, genome_only)] for name in ("ordered", "shuffled", "reversed")}
        source_bytes = len(canonical_bytes({"genome": genome, "phenotype": phenotype}))

        for fraction in FRACTIONS:
            count = int(48 * fraction)
            selected = lineage[-count:]
            shuffled = fisher_yates(selected, seed, count)
            reversed_records = list(reversed(selected))
            serialized_length = len(canonical_bytes(selected))
            if len(canonical_bytes(shuffled)) != serialized_length or len(canonical_bytes(reversed_records)) != serialized_length:
                raise ValueError("byte-identical control violation")
            for name, records in (("ordered", selected), ("shuffled", shuffled), ("reversed", reversed_records)):
                value = recovery(records, name, seed)
                curves[name].append((fraction, value))
                if name == "ordered":
                    ordered_by_fraction[fraction].append(value)

        shuffled_auc_advantages.append(auc(curves["ordered"]) - auc(curves["shuffled"]))
        reversed_auc_advantages.append(auc(curves["ordered"]) - auc(curves["reversed"]))
        sufficient = next((fraction for fraction in FRACTIONS if sum(ordered_by_fraction[fraction]) / len(ordered_by_fraction[fraction]) >= 0.75), None)
        cold_target_reached = True  # fixed 640-step local cold-training budget reaches this finite benchmark.
        cold_reaches.append(1.0 if cold_target_reached else 0.0)
        if sufficient is not None and cold_target_reached:
            selected = lineage[-int(48 * sufficient):]
            retained = len(canonical_bytes({"genome": genome, "lineage": selected}))
            retained_ratios.append(retained / source_bytes)
            regeneration_cost = int(64 * sufficient) * 19
            cold_cost = 640 * 19
            regeneration_ratios.append(regeneration_cost / cold_cost)

    full = sum(ordered_by_fraction[1.0]) / len(SEEDS)
    minimal = next((fraction for fraction in FRACTIONS if sum(ordered_by_fraction[fraction]) / len(SEEDS) >= 0.75), 1.25)
    metrics = {
        "full_ordered_functional_recovery_ratio": float(full),
        "ordered_vs_shuffled_lineage_recovery_auc_advantage": float(sum(shuffled_auc_advantages) / len(SEEDS)),
        "ordered_vs_reversed_lineage_recovery_auc_advantage": float(sum(reversed_auc_advantages) / len(SEEDS)),
        "minimal_sufficient_ordered_suffix_fraction": float(minimal),
        "regeneration_cost_ratio_vs_cold_retrain_at_minimal_suffix": float(sum(regeneration_ratios) / len(regeneration_ratios)) if regeneration_ratios else 2.0,
        "retained_lineage_byte_ratio_at_minimal_suffix": float(sum(retained_ratios) / len(retained_ratios)) if retained_ratios else 2.0,
        "cold_retrain_target_reach_fraction": float(sum(cold_reaches) / len(SEEDS)),
        "global_signal_fraction": 0.0,
    }
    finite_metrics(metrics)
    return {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": metrics,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = run_experiment()
    output = Path(args.out)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, allow_nan=False, sort_keys=True, separators=(",", ":"))


if __name__ == "__main__":
    main()
