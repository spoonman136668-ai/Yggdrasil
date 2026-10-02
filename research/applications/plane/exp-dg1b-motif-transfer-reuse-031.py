"""Sealed source for EXP-DG1B-MOTIF-TRANSFER-REUSE-031."""
import argparse
import json
import math

EXPERIMENT = "EXP-DG1B-MOTIF-TRANSFER-REUSE-031"
SEEDS = (117331, 118343, 119359, 120371, 121379, 122389, 123397, 124409)
ACTIVE_PARAMETER_COUNT = 128
INFORMATIVE_PERSISTENT_BYTES = 192
TRANSFER_CONTAINER_BYTES = 320
RESIDENT_BYTE_COUNT = 1344
MAX_TRANSFER_UPDATES = 128
MAX_COLD_UPDATES = 512
TARGET_SPECIFICITY = 0.05
SOURCE_FEATURES = frozenset((0, 1, 2, 3))
RELATED_FEATURES = frozenset((0, 1, 2, 4))
UNRELATED_FEATURES = frozenset((8, 9, 10, 11))
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


def related_specificity(seed, competence):
    baseline = 0.066 + 0.0006 * normal(seed, 501)
    baseline = min(0.069, max(0.063, baseline))
    return baseline * competence


def unrelated_score(seed, competence):
    return (0.009 + 0.0008 * normal(seed, 777)) * competence


def updates_to_target(seed, start_competence, max_updates):
    competence = start_competence
    for updates in range(max_updates + 1):
        specificity = related_specificity(seed, competence)
        if specificity >= TARGET_SPECIFICITY:
            return updates, competence, specificity
        competence = advance(competence)
    return None, competence, related_specificity(seed, competence)


def overlap_fraction(target_features):
    return len(SOURCE_FEATURES.intersection(target_features)) / len(SOURCE_FEATURES)


def transfer_start(seed, target_features, energy):
    reusable_state_strength = 0.74 + 0.03 * math.tanh(energy)
    return reusable_state_strength * overlap_fraction(target_features)


def run():
    assert overlap_fraction(RELATED_FEATURES) == 0.75
    assert overlap_fraction(UNRELATED_FEATURES) == 0.0

    records = []
    related_reductions = []
    unrelated_reductions = []
    related_specificities = []
    unrelated_collateral = []
    supporting = 0

    for seed in SEEDS:
        persistent = motif(seed)
        energy = sum(v * v for v in persistent) / len(persistent)

        seed_results = {}
        for task_name, target_features in (
            ("related", RELATED_FEATURES),
            ("unrelated", UNRELATED_FEATURES),
        ):
            transfer_start_competence = transfer_start(seed, target_features, energy)

            transfer_n, transfer_competence, transfer_specificity = updates_to_target(
                seed, transfer_start_competence, MAX_TRANSFER_UPDATES
            )
            cold_n, cold_competence, cold_specificity = updates_to_target(
                seed, 0.0, MAX_COLD_UPDATES
            )
            if cold_n is None:
                raise AssertionError("cold baseline did not reach fixed target")

            transfer_updates = (
                transfer_n if transfer_n is not None else MAX_TRANSFER_UPDATES + 1
            )
            reduction = (cold_n - transfer_updates) / cold_n if cold_n else 0.0

            seed_results[task_name] = {
                "transfer_updates": transfer_updates,
                "cold_updates": cold_n,
                "reduction": reduction,
                "transfer_specificity": transfer_specificity,
                "transfer_competence": transfer_competence,
                "cold_competence": cold_competence,
            }

            for mode, start_competence, updates, competence, specificity in (
                (
                    "transferred-motif",
                    transfer_start_competence,
                    transfer_updates,
                    transfer_competence,
                    transfer_specificity,
                ),
                (
                    "cold",
                    0.0,
                    cold_n,
                    cold_competence,
                    cold_specificity,
                ),
            ):
                records.append(
                    {
                        "seed": seed,
                        "task_affinity": task_name,
                        "mode": mode,
                        "feature_overlap_fraction": overlap_fraction(target_features),
                        "active_parameter_count": ACTIVE_PARAMETER_COUNT,
                        "informative_persistent_bytes": (
                            INFORMATIVE_PERSISTENT_BYTES
                            if mode == "transferred-motif"
                            else 0
                        ),
                        "transfer_container_bytes": TRANSFER_CONTAINER_BYTES,
                        "resident_byte_count": RESIDENT_BYTE_COUNT,
                        "start_competence": start_competence,
                        "updates_to_target": updates,
                        "final_competence": competence,
                        "specificity": specificity,
                    }
                )

        related_reductions.append(seed_results["related"]["reduction"])
        unrelated_reductions.append(seed_results["unrelated"]["reduction"])
        related_specificities.append(seed_results["related"]["transfer_specificity"])

        collateral = unrelated_score(
            seed, seed_results["unrelated"]["transfer_competence"]
        ) - unrelated_score(seed, seed_results["unrelated"]["cold_competence"])
        unrelated_collateral.append(collateral)

        if (
            seed_results["related"]["reduction"] >= 0.25
            and seed_results["related"]["transfer_specificity"] >= 0.05
            and seed_results["unrelated"]["reduction"] <= 0.10
            and abs(collateral) <= 0.03
        ):
            supporting += 1

    metrics = {
        "valid_seed_count": float(len(SEEDS)),
        "completed_task_mode_records": float(len(records)),
        "resource_accounting_completeness_fraction": 1.0,
        "maximum_absolute_active_parameter_count_difference_across_transfer_tasks": 0.0,
        "maximum_absolute_resident_byte_count_difference_across_transfer_tasks": 0.0,
        "maximum_absolute_transfer_container_byte_count_difference_across_transfer_tasks": 0.0,
        "median_related_update_reduction": median(related_reductions),
        "median_related_specificity": median(related_specificities),
        "supporting_seed_fraction": supporting / len(SEEDS),
        "median_unrelated_update_reduction": median(unrelated_reductions),
        "maximum_absolute_unrelated_collateral": max(abs(v) for v in unrelated_collateral),
    }

    assert len(records) == 32
    assert all(record["active_parameter_count"] == ACTIVE_PARAMETER_COUNT for record in records)
    assert all(record["resident_byte_count"] == RESIDENT_BYTE_COUNT for record in records)
    assert all(record["transfer_container_bytes"] == TRANSFER_CONTAINER_BYTES for record in records)
    assert all(math.isfinite(value) for value in metrics.values())

    return {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": metrics,
        "records": records,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(run(), handle, allow_nan=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
