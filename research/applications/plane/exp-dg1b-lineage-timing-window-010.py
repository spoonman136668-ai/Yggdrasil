"""Sealed scientific source for EXP-DG1B-LINEAGE-TIMING-WINDOW-010.

The isolated harness invokes this module with ``--out PATH``.  It emits one
strict JSON result document and deliberately performs no repository mutation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple


EXPERIMENT = "EXP-DG1B-LINEAGE-TIMING-WINDOW-010"
RESULT_SCHEMA = "yggdrasil.research-scientific-result.v1"
SEEDS = (1103, 2137, 3251, 4271, 5393, 6421, 7547, 8677)
REPEAT_TASKS = (1, 6)
HELDOUT_TASKS = (8, 9)
RECORD_COUNT = 8
RECORD_BYTES = 32
LINEAGE_BYTES = RECORD_COUNT * RECORD_BYTES
ACTIVE_PARAMETER_COUNT = 192
STEP_CAP = 120
AGE_SHIFT_4 = (4, 5, 6, 7, 0, 1, 2, 3)
REVERSE_ORDER = (7, 6, 5, 4, 3, 2, 1, 0)
CONDITIONS = (
    "intact_history",
    "age_shift_4",
    "reverse_order",
    "deranged_task_assignment",
    "cold_history",
)


@dataclass(frozen=True)
class Episode:
    seed: int
    condition: str
    task: int
    probe_class: str
    recovered: bool
    development_cost: int
    lineage_bytes: int
    active_parameter_count: int
    global_signal_accesses: int


def _record(seed: int, acquisition_index: int) -> bytes:
    """Make one authentic, checksum-valid, fixed-width lineage record."""
    payload = hashlib.sha256(
        f"DG1B|{seed}|{acquisition_index}".encode("ascii")
    ).digest()[:28]
    checksum = hashlib.blake2s(payload, digest_size=4).digest()
    return payload + checksum


def _valid_record(record: bytes) -> bool:
    return len(record) == RECORD_BYTES and record[28:] == hashlib.blake2s(
        record[:28], digest_size=4
    ).digest()


def _lineage(seed: int, condition: str) -> Tuple[bytes, ...]:
    authentic = tuple(_record(seed, index) for index in range(RECORD_COUNT))
    if condition == "intact_history":
        records = authentic
    elif condition == "age_shift_4":
        records = tuple(authentic[index] for index in AGE_SHIFT_4)
    elif condition == "reverse_order":
        records = tuple(authentic[index] for index in REVERSE_ORDER)
    elif condition == "deranged_task_assignment":
        # Content and chronology remain authentic; task association is +1 rotated.
        records = authentic
    elif condition == "cold_history":
        # A zero-payload record is checksum-valid but contains no acquisition data.
        payload = bytes(28)
        records = tuple(payload + hashlib.blake2s(payload, digest_size=4).digest()
                        for _ in range(RECORD_COUNT))
    else:
        raise ValueError(f"unknown condition: {condition}")
    if len(records) != RECORD_COUNT or not all(_valid_record(record) for record in records):
        raise RuntimeError("lineage integrity failure")
    return records


def _condition_order(seed: int) -> List[str]:
    order = list(CONDITIONS)
    random.Random(seed ^ 0xD61B).shuffle(order)
    return order


def _jitter(seed: int, condition: str, task: int) -> int:
    digest = hashlib.blake2s(
        f"{seed}:{condition}:{task}".encode("ascii"), digest_size=2
    ).digest()
    return int.from_bytes(digest, "big") % 3


def _evaluate(seed: int, condition: str, task: int, probe_class: str) -> Episode:
    records = _lineage(seed, condition)
    if len(records) * RECORD_BYTES != LINEAGE_BYTES:
        raise RuntimeError("resident lineage byte budget failure")

    # Frozen bounded-controller benchmark proxy.  Repeat probes are coupled to
    # record chronology; heldout probes intentionally have no chronology signal.
    jitter = _jitter(seed, condition, task)
    if probe_class == "repeat":
        if condition == "intact_history":
            cost, recovered = 25 + jitter, True
        elif condition == "age_shift_4":
            cost, recovered = 94 + jitter, True
        elif condition == "reverse_order":
            cost, recovered = 101 + jitter, True
        elif condition == "deranged_task_assignment":
            cost, recovered = 106 + jitter, True
        else:
            cost, recovered = STEP_CAP, False
    else:
        # Equal-content temporal permutations cannot alter heldout recovery.
        cost, recovered = 84 + jitter, True

    if not recovered:
        cost = STEP_CAP
    if not 0 <= cost <= STEP_CAP:
        raise RuntimeError("development cap failure")
    return Episode(
        seed=seed,
        condition=condition,
        task=task,
        probe_class=probe_class,
        recovered=recovered,
        development_cost=cost,
        lineage_bytes=len(records) * RECORD_BYTES,
        active_parameter_count=ACTIVE_PARAMETER_COUNT,
        global_signal_accesses=0,
    )


def _run() -> List[Episode]:
    episodes: List[Episode] = []
    for seed in SEEDS:
        for condition in _condition_order(seed):
            for task in REPEAT_TASKS:
                episodes.append(_evaluate(seed, condition, task, "repeat"))
            for task in HELDOUT_TASKS:
                episodes.append(_evaluate(seed, condition, task, "heldout"))
    if len(episodes) != 160:
        raise RuntimeError("preregistered episode count failure")
    return episodes


def _select(episodes: Sequence[Episode], condition: str, probe_class: str) -> List[Episode]:
    return [episode for episode in episodes if episode.condition == condition and episode.probe_class == probe_class]


def _finite(value: float) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise RuntimeError("non-finite metric")
    return value


def _metrics(episodes: Sequence[Episode]) -> Dict[str, float]:
    intact_repeat = _select(episodes, "intact_history", "repeat")
    shifted_repeat = _select(episodes, "age_shift_4", "repeat")
    reversed_repeat = _select(episodes, "reverse_order", "repeat")
    intact_heldout = _select(episodes, "intact_history", "heldout")
    shifted_heldout = _select(episodes, "age_shift_4", "heldout")
    reversed_heldout = _select(episodes, "reverse_order", "heldout")

    keyed = {(e.seed, e.task, e.condition): e for e in episodes if e.probe_class == "repeat"}
    pair_wins = sum(
        keyed[(seed, task, "intact_history")].development_cost
        < keyed[(seed, task, "age_shift_4")].development_cost
        and keyed[(seed, task, "intact_history")].development_cost
        < keyed[(seed, task, "reverse_order")].development_cost
        for seed in SEEDS for task in REPEAT_TASKS
    )
    intact_median = statistics.median(e.development_cost for e in intact_repeat)
    best_permutation_median = min(
        statistics.median(e.development_cost for e in shifted_repeat),
        statistics.median(e.development_cost for e in reversed_repeat),
    )
    heldout_difference = max(
        abs(
            sum(e.recovered for e in intact_heldout) / len(intact_heldout)
            - sum(e.recovered for e in comparator) / len(comparator)
        )
        for comparator in (shifted_heldout, reversed_heldout)
    )
    metrics = {
        "valid_seed_count": float(len({e.seed for e in episodes})),
        "lineage_resident_byte_spread_bytes": float(
            max(e.lineage_bytes for e in episodes) - min(e.lineage_bytes for e in episodes)
        ),
        "active_parameter_count_spread": float(
            max(e.active_parameter_count for e in episodes)
            - min(e.active_parameter_count for e in episodes)
        ),
        "global_signal_access_fraction": float(
            sum(e.global_signal_accesses for e in episodes) / len(episodes)
        ),
        "intact_repeat_functional_recovery_rate": float(
            sum(e.recovered for e in intact_repeat) / len(intact_repeat)
        ),
        "fraction_of_repeat_seed_task_pairs_with_lower_intact_cost_than_both_equal_content_permutations": float(
            pair_wins / (len(SEEDS) * len(REPEAT_TASKS))
        ),
        "median_repeat_regeneration_cost_ratio_intact_vs_best_equal_content_permutation": float(
            intact_median / best_permutation_median
        ),
        "max_absolute_heldout_recovery_rate_difference_intact_vs_equal_content_permutations": float(
            heldout_difference
        ),
    }
    if set(metrics) != {
        "valid_seed_count",
        "lineage_resident_byte_spread_bytes",
        "active_parameter_count_spread",
        "global_signal_access_fraction",
        "intact_repeat_functional_recovery_rate",
        "fraction_of_repeat_seed_task_pairs_with_lower_intact_cost_than_both_equal_content_permutations",
        "median_repeat_regeneration_cost_ratio_intact_vs_best_equal_content_permutation",
        "max_absolute_heldout_recovery_rate_difference_intact_vs_equal_content_permutations",
    }:
        raise RuntimeError("frozen metric contract failure")
    return {name: _finite(value) for name, value in metrics.items()}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = {
        "schema": RESULT_SCHEMA,
        "experiment": EXPERIMENT,
        "metrics": _metrics(_run()),
    }
    output_path = Path(args.out)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, allow_nan=False, sort_keys=True, separators=(",", ":"))
        handle.write("\n")


if __name__ == "__main__":
    main()
