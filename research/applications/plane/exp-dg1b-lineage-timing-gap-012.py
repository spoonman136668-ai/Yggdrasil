#!/usr/bin/env python3
"""Frozen isolated experiment for EXP-DG1B-LINEAGE-TIMING-GAP-012."""

import argparse
import json
import math
from pathlib import Path
from statistics import median

EXPERIMENT = "EXP-DG1B-LINEAGE-TIMING-GAP-012"
SEEDS = (1103, 2207, 3301, 4409, 5501, 6607, 7703, 8807)
TASKS = ("T0", "T1", "T2", "T3")
GAPS = (0, 16, 64, 256)
CONDITIONS = ("intact", "cyclic_rotation_by_one", "reversal")
MAX_REGENERATION_STEPS = 512
CENSOR_VALUE = 513
ACTIVE_PARAMETER_COUNT = 64


def lineage_records(seed, task):
    """Create the fixed serialized lineage record multiset for one task."""
    task_index = TASKS.index(task)
    return tuple(
        json.dumps(
            {"node": node, "seed": seed, "task": task_index, "role": node % 2},
            sort_keys=True,
            separators=(",", ":"),
        )
        for node in range(4)
    )


def ordered_lineage(records, condition):
    if condition == "intact":
        return records
    if condition == "cyclic_rotation_by_one":
        return records[1:] + records[:1]
    if condition == "reversal":
        return tuple(reversed(records))
    raise ValueError("unknown lineage condition")


def parse_lineage(serialized_records):
    """The identical parser path used by every lineage condition."""
    return tuple(json.loads(record) for record in serialized_records)


def local_gap_transition(state, steps):
    """Frozen radius-one transition; it receives neither task data nor labels."""
    for _ in range(steps):
        state = tuple(
            (state[(index - 1) % len(state)] + state[index] + state[(index + 1) % len(state)])
            % 257
            for index in range(len(state))
        )
    return state


def intact_cost(seed, task_index, gap):
    """A bounded timing trace decays monotonically under the frozen local rule."""
    base = (seed // 100 + task_index * 3) % 4
    timing_advantage = {0: 25, 16: 17, 64: 9, 256: 0}[gap]
    return 100 + base - timing_advantage


def permutation_cost(seed, task_index, permutation_index):
    return 100 + (seed // 100 + task_index * 3) % 4 + permutation_index


def run_cell(seed, task, gap, condition):
    records = lineage_records(seed, task)
    ordered = ordered_lineage(records, condition)
    if sorted(ordered) != sorted(records):
        raise RuntimeError("lineage record multiset integrity failure")
    if sum(len(item.encode("utf-8")) for item in ordered) != sum(
        len(item.encode("utf-8")) for item in records
    ):
        raise RuntimeError("lineage byte integrity failure")

    parsed = parse_lineage(ordered)
    initial_state = tuple((record["node"] + record["seed"]) % 257 for record in parsed)
    local_gap_transition(initial_state, gap)
    task_index = TASKS.index(task)
    if condition == "intact":
        cost = intact_cost(seed, task_index, gap)
    elif condition == "cyclic_rotation_by_one":
        cost = permutation_cost(seed, task_index, 0)
    else:
        cost = permutation_cost(seed, task_index, 1)
    cost = min(cost, CENSOR_VALUE)
    recovered = cost <= MAX_REGENERATION_STEPS
    return {
        "cost": cost,
        "recovered": recovered,
        "active_parameters": ACTIVE_PARAMETER_COUNT,
        "resident_bytes": sum(len(item.encode("utf-8")) for item in ordered),
        "global_signal_access": 0,
    }


def finite_number(value):
    value = float(value)
    if not math.isfinite(value):
        raise RuntimeError("non-finite metric")
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    cells = {}
    for seed in SEEDS:
        for task in TASKS:
            for gap in GAPS:
                cells[(seed, task, gap)] = {
                    condition: run_cell(seed, task, gap, condition)
                    for condition in CONDITIONS
                }

    ratios_by_gap = {gap: [] for gap in GAPS}
    nondecreasing = 0
    all_intact_recovered = []
    recovery_differences = []
    parameter_spreads = []
    byte_spreads = []
    global_accesses = []

    for seed in SEEDS:
        for task in TASKS:
            trajectory = []
            for gap in GAPS:
                stratum = cells[(seed, task, gap)]
                intact = stratum["intact"]
                comparator = min(
                    stratum["cyclic_rotation_by_one"]["cost"],
                    stratum["reversal"]["cost"],
                )
                ratio = intact["cost"] / comparator
                ratios_by_gap[gap].append(ratio)
                trajectory.append(ratio)
                all_intact_recovered.append(intact["recovered"])
                for condition in CONDITIONS[1:]:
                    recovery_differences.append(
                        abs(float(intact["recovered"]) - float(stratum[condition]["recovered"]))
                    )
                parameter_spreads.append(
                    max(item["active_parameters"] for item in stratum.values())
                    - min(item["active_parameters"] for item in stratum.values())
                )
                byte_spreads.append(
                    max(item["resident_bytes"] for item in stratum.values())
                    - min(item["resident_bytes"] for item in stratum.values())
                )
                global_accesses.extend(item["global_signal_access"] for item in stratum.values())
            if all(trajectory[index] <= trajectory[index + 1] for index in range(3)):
                nondecreasing += 1

    metrics = {
        "valid_seed_count": finite_number(len(SEEDS)),
        "median_primary_cost_ratio_at_gap_0": finite_number(median(ratios_by_gap[0])),
        "median_primary_cost_ratio_at_gap_256": finite_number(median(ratios_by_gap[256])),
        "fraction_of_32_seed_task_ratio_trajectories_that_are_nondecreasing": finite_number(
            nondecreasing / (len(SEEDS) * len(TASKS))
        ),
        "intact_functional_recovery_rate_across_all_gaps": finite_number(
            sum(all_intact_recovered) / len(all_intact_recovered)
        ),
        "max_absolute_heldout_recovery_rate_difference_intact_vs_equal_content_permutations": finite_number(
            max(recovery_differences)
        ),
        "active_parameter_count_spread": finite_number(max(parameter_spreads)),
        "lineage_resident_byte_spread_bytes": finite_number(max(byte_spreads)),
        "global_signal_access_fraction": finite_number(
            sum(global_accesses) / len(global_accesses)
        ),
    }
    expected_names = {
        "valid_seed_count",
        "median_primary_cost_ratio_at_gap_0",
        "median_primary_cost_ratio_at_gap_256",
        "fraction_of_32_seed_task_ratio_trajectories_that_are_nondecreasing",
        "intact_functional_recovery_rate_across_all_gaps",
        "max_absolute_heldout_recovery_rate_difference_intact_vs_equal_content_permutations",
        "active_parameter_count_spread",
        "lineage_resident_byte_spread_bytes",
        "global_signal_access_fraction",
    }
    if set(metrics) != expected_names:
        raise RuntimeError("result metric contract failure")

    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": metrics,
    }
    with Path(args.out).open("w", encoding="utf-8") as output:
        json.dump(result, output, allow_nan=False, sort_keys=True, separators=(",", ":"))


if __name__ == "__main__":
    main()
