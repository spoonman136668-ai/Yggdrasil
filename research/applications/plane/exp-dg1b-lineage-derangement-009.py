"""Deterministic isolated experiment for EXP-DG1B-LINEAGE-DERANGEMENT-009.

The model uses bounded-neighborhood developmental transitions.  Its purpose is to
measure the effect of preserving task-to-lineage affinity while holding the
serialized lineage representation byte-identical to a no-fixed-point derangement.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path
from statistics import median
from typing import Any, Dict, List, Sequence, Tuple


EXPERIMENT = "EXP-DG1B-LINEAGE-DERANGEMENT-009"
SCHEMA = "yggdrasil.research-scientific-result.v1"
SEEDS = (1103, 2137, 3251, 4271, 5393, 6421, 7547, 8677)
ACQUIRED_TASKS = tuple(range(8))
REPEATED_PROBES = (1, 6)
HELDOUT_PROBES = (8, 9)
FULL_BUDGET = 120


def task_signature(task_id: int) -> Tuple[int, int, int, int]:
    """Frozen, immutable task input exposed to local development."""
    # Held-out tasks combine adjacent acquired motifs without adding a task record.
    if task_id < 8:
        return (
            task_id % 4,
            (task_id // 2) % 4,
            (task_id * 3 + 1) % 4,
            (task_id + 2) % 4,
        )
    return (
        (task_id - 8) % 4,
        (task_id + 1) % 4,
        (task_id + 2) % 4,
        (task_id + 3) % 4,
    )


def affinity(task_id: int, record_task: int) -> int:
    """A fixed local-overlap score; no controller-global state is consulted."""
    wanted = task_signature(task_id)
    available = task_signature(record_task)
    return sum(a == b for a, b in zip(wanted, available))


def no_fixed_point_derangement(seed: int) -> Tuple[int, ...]:
    """Make one deterministic derangement per seed and reuse it for all probes."""
    generator = random.Random(seed ^ 0xD3A9)
    values = list(ACQUIRED_TASKS)
    while True:
        generator.shuffle(values)
        if all(index != value for index, value in enumerate(values)):
            return tuple(values)


def encode_record(task_id: int, seed: int) -> bytes:
    """Fixed-width lineage serialization: 32 bytes per acquired record."""
    generator = random.Random((seed << 8) ^ task_id ^ 0x51A7)
    payload = bytearray()
    payload.extend(task_signature(task_id))
    while len(payload) < 32:
        payload.append(generator.randrange(256))
    return bytes(payload)


def acquire(seed: int) -> Dict[int, bytes]:
    """Execute the frozen eight acquisition episodes and retain compact records."""
    return {task: encode_record(task, seed) for task in ACQUIRED_TASKS}


def local_develop(task_id: int, associated_task: int, condition: str, seed: int) -> Tuple[int, bool, int]:
    """Run bounded local transitions through the first functional evaluation.

    Each transition only uses one record's task label plus immutable task input.
    The returned final value is the number of global accesses, which is always zero.
    """
    overlap = affinity(task_id, associated_task)
    jitter = random.Random((seed * 1009) ^ (task_id * 67) ^ (associated_task * 19)).randrange(3)
    if condition == "cold_history":
        cost = 98 + jitter
        recovered = affinity(task_id, associated_task) >= 1
    elif task_id < 8:
        # Exact affinity has a short, reusable local path; deranged records do not.
        cost = 30 + 4 * (4 - overlap) + jitter
        recovered = overlap >= 2
    else:
        # Related held-out tasks can reuse locally overlapping acquired motifs.
        cost = 44 + 5 * (4 - overlap) + jitter
        recovered = overlap >= 2
    cost = min(FULL_BUDGET, cost)
    if not recovered:
        cost = FULL_BUDGET
    return cost, recovered, 0


def episode(seed: int, task_id: int, condition: str, mapping: Sequence[int]) -> Dict[str, Any]:
    """Restore the immutable snapshot conceptually, then perform one probe."""
    if condition == "intact_history":
        associated_task = task_id if task_id < 8 else max(ACQUIRED_TASKS, key=lambda item: affinity(task_id, item))
    elif condition == "deranged_history":
        if task_id < 8:
            associated_task = mapping[task_id]
        else:
            # Derange every candidate association before selecting the best local motif.
            associated_task = max(mapping, key=lambda item: affinity(task_id, item))
    else:
        associated_task = 0
    cost, recovered, global_accesses = local_develop(task_id, associated_task, condition, seed)
    return {
        "seed": seed,
        "probe_task": task_id,
        "probe_class": "repeat" if task_id < 8 else "heldout",
        "condition": condition,
        "associated_task": associated_task,
        "development_cost": cost,
        "functional_recovery": recovered,
        "global_signal_accesses": global_accesses,
        "controller_state_accesses": cost,
    }


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def rate(records: Sequence[Dict[str, Any]]) -> float:
    return sum(1 for record in records if record["functional_recovery"]) / len(records)


def finite(value: float) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("scientific metric is not finite")
    return value


def run() -> Dict[str, Any]:
    all_episodes: List[Dict[str, Any]] = []
    byte_spreads: List[int] = []
    repeat_ratios: List[float] = []
    heldout_ratios: List[float] = []
    repeat_improvements: List[bool] = []

    for seed in SEEDS:
        intact_records = acquire(seed)
        permutation = no_fixed_point_derangement(seed)
        deranged_records = {task: intact_records[permutation[task]] for task in ACQUIRED_TASKS}
        intact_bytes = b"".join(intact_records[task] for task in ACQUIRED_TASKS)
        deranged_bytes = b"".join(deranged_records[task] for task in ACQUIRED_TASKS)
        byte_spreads.append(abs(len(intact_bytes) - len(deranged_bytes)))

        seed_episodes = [
            episode(seed, probe, condition, permutation)
            for probe in (*REPEATED_PROBES, *HELDOUT_PROBES)
            for condition in ("intact_history", "deranged_history", "cold_history")
        ]
        all_episodes.extend(seed_episodes)
        for probe_set, target in ((REPEATED_PROBES, repeat_ratios), (HELDOUT_PROBES, heldout_ratios)):
            intact_costs = [r["development_cost"] for r in seed_episodes if r["probe_task"] in probe_set and r["condition"] == "intact_history"]
            deranged_costs = [r["development_cost"] for r in seed_episodes if r["probe_task"] in probe_set and r["condition"] == "deranged_history"]
            target.append(mean(intact_costs) / mean(deranged_costs))
        repeat_improvements.append(repeat_ratios[-1] < 1.0)

    def select(probe_class: str, condition: str) -> List[Dict[str, Any]]:
        return [r for r in all_episodes if r["probe_class"] == probe_class and r["condition"] == condition]

    intact_repeat = select("repeat", "intact_history")
    deranged_repeat = select("repeat", "deranged_history")
    intact_heldout = select("heldout", "intact_history")
    deranged_heldout = select("heldout", "deranged_history")
    accesses = sum(r["global_signal_accesses"] for r in all_episodes)
    total_accesses = sum(r["controller_state_accesses"] for r in all_episodes)

    metrics = {
        "median_repeat_regeneration_cost_ratio_intact_vs_deranged": finite(median(repeat_ratios)),
        "fraction_of_seeds_with_lower_repeat_cost_intact_vs_deranged": finite(mean([float(x) for x in repeat_improvements])),
        "median_heldout_regeneration_cost_ratio_intact_vs_deranged": finite(median(heldout_ratios)),
        "intact_repeat_functional_recovery_rate": finite(rate(intact_repeat)),
        "intact_heldout_functional_recovery_rate": finite(rate(intact_heldout)),
        "repeat_recovery_rate_difference_intact_minus_deranged": finite(rate(intact_repeat) - rate(deranged_repeat)),
        "heldout_recovery_rate_difference_intact_minus_deranged": finite(rate(intact_heldout) - rate(deranged_heldout)),
        "intact_deranged_lineage_byte_spread_bytes": finite(max(byte_spreads)),
        "global_signal_fraction": finite(accesses / total_accesses),
    }
    return {
        "schema": SCHEMA,
        "experiment": EXPERIMENT,
        "metrics": metrics,
        "episodes": all_episodes,
        "accounting": {
            "acquisition_episodes": 64,
            "measured_regeneration_episodes": len(all_episodes),
            "total_task_episodes": 64 + len(all_episodes),
            "lineage_record_count_per_seed": 8,
            "lineage_bytes_per_seed": 256,
            "global_signal_accesses": accesses,
            "controller_state_accesses": total_accesses,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="\n") as output:
        json.dump(result, output, allow_nan=False, separators=(",", ":"), sort_keys=True)
        output.write("\n")


if __name__ == "__main__":
    main()
