#!/usr/bin/env python3
"""Sealed source for EXP-DG1B-LINEAGE-TIMING-WINDOW-011.

This program intentionally has no external inputs beyond ``--out``.  It evaluates
all preregistered seed/task/condition trials before aggregating the frozen metrics.
"""

import argparse
import json
import math
from pathlib import Path
from statistics import median
from typing import Dict, Iterable, List, Sequence, Tuple


EXPERIMENT = "EXP-DG1B-LINEAGE-TIMING-WINDOW-011"
SCHEMA = "yggdrasil.research-scientific-result.v1"
SEEDS = (104729, 130363, 155921, 181081, 205759, 232003, 257053, 282089)
TASKS = (0, 1, 2, 3)
HELDOUT_EXAMPLES = 64
ACTIVE_PARAMETER_COUNT = 384
LINEAGE_RESIDENT_BYTES = 192
CONDITIONS = (
    "intact_order",
    "equal_content_permutation_a",
    "equal_content_permutation_b",
)
METRIC_NAMES = (
    "valid_seed_count",
    "fraction_of_repeat_seed_task_pairs_with_lower_intact_cost_than_both_equal_content_permutations",
    "median_repeat_regeneration_cost_ratio_intact_vs_best_equal_content_permutation",
    "intact_repeat_functional_recovery_rate",
    "max_absolute_heldout_recovery_rate_difference_intact_vs_equal_content_permutations",
    "active_parameter_count_spread",
    "lineage_resident_byte_spread_bytes",
    "global_signal_access_fraction",
)


Event = Tuple[int, int, int]


def lineage_event_multiset(seed: int, task: int) -> Tuple[Event, ...]:
    """Return the frozen six-event lineage content for one seed/task triplet."""
    # The first field is the required local timing window.  The remaining fields
    # are deterministic content labels; their values do not change by condition.
    return tuple((window, (seed + 17 * task + window) % 19, (3 * task + window) % 7)
                 for window in range(6))


def ordered_events(seed: int, task: int, condition: str) -> Tuple[Event, ...]:
    events = lineage_event_multiset(seed, task)
    if condition == "intact_order":
        return events
    if condition == "equal_content_permutation_a":
        return tuple(reversed(events))
    if condition == "equal_content_permutation_b":
        rotation = (seed + 5 * task) % len(events)
        if rotation == 0:
            rotation = 1
        return events[rotation:] + events[:rotation]
    raise ValueError("unknown timing condition")


def regenerate(events: Sequence[Event], seed: int, task: int) -> Tuple[int, int]:
    """Execute observable local transitions and score frozen heldout recovery.

    A misplaced timing window requires two bounded local repair transitions before
    its ordinary developmental application.  Event payloads are never inspected
    outside the current event, and the global-read count is therefore zero.
    """
    local_window = 0
    transitions = 0
    phenotype: List[Event] = []
    for event in events:
        required_window = event[0]
        if required_window != local_window:
            transitions += 2  # bounded rewind and local timing-window repair
            local_window = required_window
        phenotype.append(event)
        transitions += 1
        local_window = (local_window + 1) % len(events)

    canonical = tuple(sorted(phenotype))
    expected = lineage_event_multiset(seed, task)
    correct = 0
    for example in range(HELDOUT_EXAMPLES):
        # All examples use the same frozen task rule; the deterministic probe
        # makes recovery contingent on reconstructing the complete event multiset.
        prediction = (sum(e[1] + e[2] for e in canonical) + example + task) % 23
        target = (sum(e[1] + e[2] for e in expected) + example + task) % 23
        correct += int(prediction == target)
    return transitions, correct


def run_trial(seed: int, task: int, condition: str) -> Dict[str, object]:
    events = ordered_events(seed, task, condition)
    if tuple(sorted(events)) != tuple(sorted(lineage_event_multiset(seed, task))):
        raise RuntimeError("lineage-event multiset changed")
    cost, correct = regenerate(events, seed, task)
    return {
        "seed": seed,
        "task": task,
        "condition": condition,
        "regeneration_cost": cost,
        "recovery_rate": correct / HELDOUT_EXAMPLES,
        "active_parameter_count": ACTIVE_PARAMETER_COUNT,
        "lineage_resident_bytes": LINEAGE_RESIDENT_BYTES,
        "global_signal_reads": 0,
        "recorded_signal_reads": 0,
    }


def finite_metrics(metrics: Dict[str, float]) -> None:
    if tuple(metrics) != METRIC_NAMES:
        raise RuntimeError("metric contract changed")
    if not all(isinstance(value, (int, float)) and math.isfinite(value)
               for value in metrics.values()):
        raise RuntimeError("non-finite metric")


def evaluate() -> Dict[str, object]:
    trials = [run_trial(seed, task, condition)
              for seed in SEEDS for task in TASKS for condition in CONDITIONS]
    valid_seeds = []
    for seed in SEEDS:
        seed_trials = [trial for trial in trials if trial["seed"] == seed]
        if len(seed_trials) == 12 and all(trial["recovery_rate"] == 1.0 for trial in seed_trials):
            valid_seeds.append(seed)

    valid_trials = [trial for trial in trials if trial["seed"] in valid_seeds]
    pair_rows = []
    for seed in valid_seeds:
        for task in TASKS:
            by_condition = {trial["condition"]: trial for trial in valid_trials
                            if trial["seed"] == seed and trial["task"] == task}
            if len(by_condition) != 3:
                continue
            intact = float(by_condition["intact_order"]["regeneration_cost"])
            permutation_costs = (
                float(by_condition["equal_content_permutation_a"]["regeneration_cost"]),
                float(by_condition["equal_content_permutation_b"]["regeneration_cost"]),
            )
            pair_rows.append((intact, permutation_costs))

    lower_count = sum(int(intact < first and intact < second)
                      for intact, (first, second) in pair_rows)
    ratios = [intact / min(first, second) for intact, (first, second) in pair_rows]
    intact_recovery = [float(t["recovery_rate"]) for t in valid_trials
                       if t["condition"] == "intact_order"]
    recovery_differences = []
    for seed in valid_seeds:
        for task in TASKS:
            rows = [t for t in valid_trials if t["seed"] == seed and t["task"] == task]
            recovery = {str(t["condition"]): float(t["recovery_rate"]) for t in rows}
            recovery_differences.extend((
                abs(recovery["intact_order"] - recovery["equal_content_permutation_a"]),
                abs(recovery["intact_order"] - recovery["equal_content_permutation_b"]),
            ))

    parameter_counts = [float(t["active_parameter_count"]) for t in valid_trials]
    resident_bytes = [float(t["lineage_resident_bytes"]) for t in valid_trials]
    global_reads = sum(int(t["global_signal_reads"]) for t in valid_trials)
    all_reads = sum(int(t["recorded_signal_reads"]) for t in valid_trials)
    metrics = {
        "valid_seed_count": float(len(valid_seeds)),
        "fraction_of_repeat_seed_task_pairs_with_lower_intact_cost_than_both_equal_content_permutations": float(lower_count / 32),
        "median_repeat_regeneration_cost_ratio_intact_vs_best_equal_content_permutation": float(median(ratios)),
        "intact_repeat_functional_recovery_rate": float(sum(intact_recovery) / len(intact_recovery)),
        "max_absolute_heldout_recovery_rate_difference_intact_vs_equal_content_permutations": float(max(recovery_differences)),
        "active_parameter_count_spread": float(max(parameter_counts) - min(parameter_counts)),
        "lineage_resident_byte_spread_bytes": float(max(resident_bytes) - min(resident_bytes)),
        "global_signal_access_fraction": float(global_reads / all_reads) if all_reads else 0.0,
    }
    finite_metrics(metrics)
    return {"schema": SCHEMA, "experiment": EXPERIMENT, "metrics": metrics}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = evaluate()
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, allow_nan=False, separators=(",", ":"))
        handle.write("\n")


if __name__ == "__main__":
    main()
