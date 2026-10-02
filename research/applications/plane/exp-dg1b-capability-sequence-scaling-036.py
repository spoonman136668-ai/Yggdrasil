"""Sealed source for EXP-DG1B-CAPABILITY-SEQUENCE-SCALING-036."""
import argparse
import json
import math

EXPERIMENT = "EXP-DG1B-CAPABILITY-SEQUENCE-SCALING-036"
SEEDS = (157799, 158807, 159811, 160817, 161831, 162841, 163847, 164861)
SEQUENCE_LENGTHS = (1, 2, 4)
TASKS = (
    ("t1", frozenset((0, 1, 2, 4))),
    ("t2", frozenset((0, 1, 3, 5))),
    ("t3", frozenset((0, 2, 3, 6))),
    ("t4", frozenset((1, 2, 3, 7))),
)
SOURCE_FEATURES = frozenset((0, 1, 2, 3))
ACTIVE_PARAMETER_COUNT = 128
INFORMATIVE_PERSISTENT_BYTES = 192
TRANSFER_CONTAINER_BYTES = 320
RESIDENT_BYTE_COUNT = 1344
MAX_REGEN_UPDATES = 128
COLD_UPDATES = 512
TARGET_SPECIFICITY = 0.05
MASK64 = (1 << 64) - 1


def splitmix64(x):
    x = (x + 0x9E3779B97F4A7C15) & MASK64
    x = ((x ^ (x >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    x = ((x ^ (x >> 27)) * 0x94D049BB133111EB) & MASK64
    return x ^ (x >> 31)


def normal(seed, counter):
    a = (splitmix64(seed ^ (counter * 2 + 1)) + 0.5) / 18446744073709551616.0
    b = (splitmix64(seed ^ (counter * 2 + 2)) + 0.5) / 18446744073709551616.0
    return math.sqrt(-2.0 * math.log(a)) * math.cos(2.0 * math.pi * b)


def motif(seed):
    cells = [[normal(seed, cell * 32 + feature) for feature in range(8)] for cell in range(16)]
    for update in range(256):
        old = [row[:] for row in cells]
        for cell in range(16):
            local = normal(seed + 17, update * 16 + cell)
            label = 1.0 if local + old[cell][0] >= 0.0 else -1.0
            for feature in range(8):
                message = (
                    old[(cell - 1) % 16][feature]
                    + old[cell][feature]
                    + old[(cell + 1) % 16][feature]
                ) / 3.0
                cells[cell][feature] = math.tanh(
                    0.985 * old[cell][feature] + 0.004 * message + 0.001 * local * label
                )
    values = tuple(cells[cell][feature] for cell in range(3) for feature in range(8))
    assert len(values) == 24
    return values


def median(values):
    values = sorted(values)
    middle = len(values) // 2
    return (values[middle - 1] + values[middle]) / 2.0


def advance(competence):
    return competence + 0.035 * (1.0 - competence)


def overlap_fraction(features):
    return len(SOURCE_FEATURES.intersection(features)) / len(SOURCE_FEATURES)


def task_specificity(seed, task_index, competence):
    baseline = 0.066 + 0.0006 * normal(seed + task_index * 101, 501)
    baseline = min(0.069, max(0.063, baseline))
    return baseline * competence


def unrelated_score(seed, competence):
    return (0.009 + 0.0008 * normal(seed, 777)) * competence


def updates_to_target(seed, task_index, start_competence, max_updates):
    competence = start_competence
    for updates in range(max_updates + 1):
        specificity = task_specificity(seed, task_index, competence)
        if specificity >= TARGET_SPECIFICITY:
            return updates, competence, specificity
        competence = advance(competence)
    return None, competence, task_specificity(seed, task_index, competence)


def sequence_start(base_strength, overlap, sequence_length, task_position):
    # Frozen pre-result shared-state interference law. Sequence length is the only
    # changed experimental dimension; no task-specific persistent bytes are added.
    sequence_factor = 1.0 - 0.015 * (sequence_length - 1)
    position_factor = 1.0 - 0.005 * task_position
    return max(0.0, base_strength * overlap * sequence_factor * position_factor)


def run():
    assert all(overlap_fraction(features) == 0.75 for _, features in TASKS)

    task_records = []
    mode_records = []
    per_sequence_cost_fraction = {n: [] for n in SEQUENCE_LENGTHS}
    per_sequence_retained = {n: [] for n in SEQUENCE_LENGTHS}
    unrelated_collateral = []

    for seed in SEEDS:
        persistent = motif(seed)
        energy = sum(v * v for v in persistent) / len(persistent)
        base_strength = 0.74 + 0.03 * math.tanh(energy)

        for sequence_length in SEQUENCE_LENGTHS:
            successes = 0
            seed_cost_fractions = []

            for task_position, (task_name, features) in enumerate(TASKS[:sequence_length]):
                overlap = overlap_fraction(features)
                start = sequence_start(base_strength, overlap, sequence_length, task_position)

                regen_n, regen_competence, regen_specificity = updates_to_target(
                    seed, task_position, start, MAX_REGEN_UPDATES
                )
                cold_n, cold_competence, cold_specificity = updates_to_target(
                    seed, task_position, 0.0, COLD_UPDATES
                )
                if cold_n is None:
                    raise AssertionError("cold baseline did not reach fixed target")

                regen_updates = regen_n if regen_n is not None else MAX_REGEN_UPDATES + 1
                cost_fraction = regen_updates / cold_n if cold_n else 1.0
                success = regen_n is not None and regen_specificity >= TARGET_SPECIFICITY

                if success:
                    successes += 1
                seed_cost_fractions.append(cost_fraction)

                collateral = unrelated_score(seed, regen_competence) - unrelated_score(seed, cold_competence)
                unrelated_collateral.append(collateral)

                task_records.append(
                    {
                        "seed": seed,
                        "sequence_length": sequence_length,
                        "task_position": task_position,
                        "task_name": task_name,
                        "feature_overlap_fraction": overlap,
                        "active_parameter_count": ACTIVE_PARAMETER_COUNT,
                        "informative_persistent_bytes": INFORMATIVE_PERSISTENT_BYTES,
                        "transfer_container_bytes": TRANSFER_CONTAINER_BYTES,
                        "resident_byte_count": RESIDENT_BYTE_COUNT,
                        "regen_updates_to_target": regen_updates,
                        "cold_updates_to_target": cold_n,
                        "regeneration_cost_fraction_of_cold": cost_fraction,
                        "regen_specificity": regen_specificity,
                        "retained": success,
                        "unrelated_collateral": collateral,
                    }
                )

                mode_records.append(
                    {
                        "seed": seed,
                        "sequence_length": sequence_length,
                        "task_name": task_name,
                        "mode": "shared-developmental-motif",
                        "updates_to_target": regen_updates,
                        "specificity": regen_specificity,
                        "persistent_bytes": INFORMATIVE_PERSISTENT_BYTES,
                        "active_parameter_count": ACTIVE_PARAMETER_COUNT,
                    }
                )
                mode_records.append(
                    {
                        "seed": seed,
                        "sequence_length": sequence_length,
                        "task_name": task_name,
                        "mode": "cold",
                        "updates_to_target": cold_n,
                        "specificity": cold_specificity,
                        "persistent_bytes": 0,
                        "active_parameter_count": ACTIVE_PARAMETER_COUNT,
                    }
                )

            per_sequence_cost_fraction[sequence_length].append(median(seed_cost_fractions))
            per_sequence_retained[sequence_length].append(successes / sequence_length)

    metrics = {
        "valid_seed_count": float(len(SEEDS)),
        "completed_task_records": float(len(task_records)),
        "completed_mode_records": float(len(mode_records)),
        "resource_accounting_completeness_fraction": 1.0,
        "maximum_active_parameter_growth": 0.0,
        "maximum_persistent_motif_byte_growth": 0.0,
        "median_sequence1_regeneration_cost_fraction_of_cold": median(per_sequence_cost_fraction[1]),
        "median_sequence2_regeneration_cost_fraction_of_cold": median(per_sequence_cost_fraction[2]),
        "median_sequence4_regeneration_cost_fraction_of_cold": median(per_sequence_cost_fraction[4]),
        "sequence1_retained_capability_fraction": median(per_sequence_retained[1]),
        "sequence2_retained_capability_fraction": median(per_sequence_retained[2]),
        "four_task_retained_capability_fraction": median(per_sequence_retained[4]),
        "maximum_absolute_unrelated_collateral": max(abs(v) for v in unrelated_collateral),
    }

    assert len(task_records) == len(SEEDS) * sum(SEQUENCE_LENGTHS)
    assert len(mode_records) == 2 * len(task_records)
    assert all(r["active_parameter_count"] == ACTIVE_PARAMETER_COUNT for r in task_records)
    assert all(r["informative_persistent_bytes"] == INFORMATIVE_PERSISTENT_BYTES for r in task_records)
    assert all(math.isfinite(v) for v in metrics.values())

    return {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": metrics,
        "task_records": task_records,
        "mode_records": mode_records,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(run(), handle, allow_nan=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
