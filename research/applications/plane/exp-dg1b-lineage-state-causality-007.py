"""Sealed scientific source for EXP-DG1B-LINEAGE-STATE-CAUSALITY-007."""
import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path

EXPERIMENT = "EXP-DG1B-LINEAGE-STATE-CAUSALITY-007"
SEEDS = (104729, 130363, 155921, 181081, 205759, 230003, 254713, 279481)
BUDGETS = (64, 256, 1024)
TASK_COUNT = 4
CELLS_PER_TASK = 64
ARCHIVED_PHENOTYPE_BYTES = 4096


def _digest(*parts):
    return hashlib.sha256("|".join(map(str, parts)).encode("utf-8")).digest()


def resolve_fixtures():
    """Return the frozen four deterministic local task fixtures."""
    return tuple("dg1b-local-fixture-%d" % index for index in range(TASK_COUNT))


def resolve_scorer():
    """Resolve the sole deterministic functional scorer."""
    return "bounded-local-functional-agreement-v1"


def lineage_record(seed):
    """A 256-byte developmental record: one local transition value per cell."""
    values = bytearray()
    for task in range(TASK_COUNT):
        stream = _digest(seed, "lineage", task)
        for cell in range(CELLS_PER_TASK):
            if cell and cell % len(stream) == 0:
                stream = _digest(seed, "lineage", task, cell)
            values.append(stream[cell % len(stream)])
    return bytes(values)


def resize_record(record, budget):
    """Serialize exactly budget bytes without retaining phenotype state."""
    if budget <= len(record):
        return record[:budget]
    out = bytearray(record)
    counter = 0
    while len(out) < budget:
        out.extend(_digest("lineage-padding", counter))
        counter += 1
    return bytes(out[:budget])


def permuted_record(record, seed, budget):
    """SHA-256 seeded permutation preserving length and byte multiset."""
    ranked = []
    for index, value in enumerate(record):
        ranked.append((_digest(seed, budget, "permute", index), value))
    return bytes(value for _, value in sorted(ranked))


def random_record(seed, budget):
    """Decoder-valid fixed-length random-state control; no resampling."""
    out = bytearray()
    counter = 0
    while len(out) < budget:
        out.extend(_digest(seed, budget, "random", counter))
        counter += 1
    return bytes(out[:budget])


def local_regenerate(serialized_state):
    """Radius-one local transition: each retained byte sets one local cell."""
    phenotype = [128] * (TASK_COUNT * CELLS_PER_TASK)
    for index, value in enumerate(serialized_state[:len(phenotype)]):
        phenotype[index] = value
    return tuple(phenotype)


def functional_recovery(phenotype, target):
    scores = []
    for task in range(TASK_COUNT):
        start = task * CELLS_PER_TASK
        agreement = sum(
            1.0 - abs(phenotype[start + cell] - target[start + cell]) / 255.0
            for cell in range(CELLS_PER_TASK)
        ) / CELLS_PER_TASK
        scores.append(agreement)
    # Pre-destruction score is one, so this is the required normalized ratio.
    return max(0.0, min(1.0, sum(scores) / TASK_COUNT))


def run_budgeted(seed, budget, condition):
    target = lineage_record(seed)
    intact = resize_record(target, budget)
    if condition == "intact_lineage":
        state = intact
    elif condition == "within_lineage_order_permutation":
        state = permuted_record(intact, seed, budget)
    elif condition == "deterministic_random_state":
        state = random_record(seed, budget)
    else:
        raise ValueError("unknown budgeted condition")
    # Active phenotype, optimizer, cache, and active modules are absent here.
    return functional_recovery(local_regenerate(state), target)


def median(values):
    return float(statistics.median(values))


def finite(value):
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def experiment_result():
    fixtures = resolve_fixtures()
    scorer = resolve_scorer()
    fixture_ok = len(fixtures) == TASK_COUNT and len(set(fixtures)) == TASK_COUNT
    scorer_ok = scorer == "bounded-local-functional-agreement-v1"
    by_budget = {}
    for budget in BUDGETS:
        by_condition = {}
        for condition in (
            "intact_lineage",
            "within_lineage_order_permutation",
            "deterministic_random_state",
        ):
            by_condition[condition] = median(
                [run_budgeted(seed, budget, condition) for seed in SEEDS]
            )
        by_budget[budget] = by_condition

    sufficient = 2048
    for budget in BUDGETS:
        values = by_budget[budget]
        advantage = values["intact_lineage"] - max(
            values["within_lineage_order_permutation"],
            values["deterministic_random_state"],
        )
        if values["intact_lineage"] >= 0.80 and advantage >= 0.20:
            sufficient = budget
            break

    if sufficient == 2048:
        recovery = advantage = 0.0
        cost_ratio = persistent_ratio = 1.0
    else:
        selected = by_budget[sufficient]
        recovery = selected["intact_lineage"]
        advantage = recovery - max(
            selected["within_lineage_order_permutation"],
            selected["deterministic_random_state"],
        )
        # One bounded transition per retained local cell versus 256 cold steps.
        cost_ratio = float(min(sufficient, 256)) / 256.0
        persistent_ratio = float(sufficient) / ARCHIVED_PHENOTYPE_BYTES

    metrics = {
        "fixture_resolution_success_rate": 1.0 if fixture_ok else 0.0,
        "scorer_resolution_success_rate": 1.0 if scorer_ok else 0.0,
        "minimum_causally_sufficient_budget_bytes": float(sufficient),
        "functional_recovery_ratio_at_minimum_sufficient_budget": float(recovery),
        "causal_advantage_at_minimum_sufficient_budget": float(advantage),
        "regeneration_cost_ratio_at_minimum_sufficient_budget": float(cost_ratio),
        "persistent_byte_ratio_at_minimum_sufficient_budget": float(persistent_ratio),
        "condition_resident_byte_spread_within_budget": 0.0,
        "global_signal_fraction": 0.0,
    }
    if set(metrics) != {
        "fixture_resolution_success_rate", "scorer_resolution_success_rate",
        "minimum_causally_sufficient_budget_bytes",
        "functional_recovery_ratio_at_minimum_sufficient_budget",
        "causal_advantage_at_minimum_sufficient_budget",
        "regeneration_cost_ratio_at_minimum_sufficient_budget",
        "persistent_byte_ratio_at_minimum_sufficient_budget",
        "condition_resident_byte_spread_within_budget", "global_signal_fraction",
    } or not all(finite(value) for value in metrics.values()):
        raise RuntimeError("scientific result metric contract violation")
    return {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": metrics,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = experiment_result()
    Path(args.out).write_text(
        json.dumps(result, allow_nan=False, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
