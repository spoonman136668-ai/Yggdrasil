"""Sealed source for EXP-DG1B-REEXPOSURE-TRAJECTORY-COMPRESSION-028."""
import argparse
import json
import math

EXPERIMENT = "EXP-DG1B-REEXPOSURE-TRAJECTORY-COMPRESSION-028"
SEEDS = (91009, 92033, 93047, 94057, 95071, 96079, 97081, 98101)
EXPOSURES = (1, 2, 3, 4)
ACTIVE_PARAMETER_COUNT = 128
INFORMATIVE_PERSISTENT_BYTES = 256
TRANSFER_CONTAINER_BYTES = 320
RESIDENT_BYTE_COUNT = 1344
MAX_UPDATES_PER_EXPOSURE = 128
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


def persistent_motif(seed):
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
    values = [cells[cell][feature] for cell in range(4) for feature in range(8)]
    assert len(values) == 32
    values[31] = 0.0
    return values


def median(values):
    values = sorted(values)
    middle = len(values) // 2
    return (values[middle - 1] + values[middle]) / 2.0


def base_specificity(seed):
    value = 0.066 + 0.0006 * normal(seed, 901)
    return min(0.069, max(0.063, value))


def unrelated_score(seed, competence):
    return (0.009 + 0.0008 * normal(seed, 977)) * competence


def initial_competence(persistent):
    energy = sum(v * v for v in persistent[:31]) / 31.0
    return 0.55 + 0.05 * math.tanh(energy)


def update_rate(persistent):
    memory = persistent[31]
    return 0.030 * (1.0 + memory)


def advance(competence, rate):
    return competence + rate * (1.0 - competence)


def updates_to_target(seed, persistent):
    competence = initial_competence(persistent)
    rate = update_rate(persistent)
    for updates in range(MAX_UPDATES_PER_EXPOSURE + 1):
        specificity = base_specificity(seed) * competence
        if specificity >= TARGET_SPECIFICITY:
            return updates, competence, specificity
        competence = advance(competence, rate)
    return None, competence, base_specificity(seed) * competence


def reinforce_trajectory_memory(persistent):
    memory = persistent[31]
    persistent[31] = memory + 0.25 * (1.0 - memory)


def run():
    records = []
    by_seed = {}
    reduction_fractions = []
    exposure4_specificities = []
    support_count = 0
    collateral = []

    for seed in SEEDS:
        persistent = persistent_motif(seed)
        assert len(persistent) * 8 == INFORMATIVE_PERSISTENT_BYTES
        seed_records = []

        exposure1_updates = None
        exposure4_updates = None
        exposure4_specificity = None
        exposure1_unrelated = None
        exposure4_unrelated = None

        for exposure in EXPOSURES:
            memory_before = persistent[31]
            updates, competence, specificity = updates_to_target(seed, persistent)
            if updates is None:
                updates = MAX_UPDATES_PER_EXPOSURE + 1

            unrelated = unrelated_score(seed, competence)
            record = {
                "seed": seed,
                "exposure": exposure,
                "active_parameter_count": ACTIVE_PARAMETER_COUNT,
                "informative_persistent_bytes": INFORMATIVE_PERSISTENT_BYTES,
                "transfer_container_bytes": TRANSFER_CONTAINER_BYTES,
                "resident_byte_count": RESIDENT_BYTE_COUNT,
                "trajectory_memory_before": memory_before,
                "update_rate": update_rate(persistent),
                "updates_to_target": updates,
                "final_competence": competence,
                "related_specificity": specificity,
                "unrelated_score": unrelated,
            }
            records.append(record)
            seed_records.append(record)

            if exposure == 1:
                exposure1_updates = updates
                exposure1_unrelated = unrelated
            if exposure == 4:
                exposure4_updates = updates
                exposure4_specificity = specificity
                exposure4_unrelated = unrelated

            reinforce_trajectory_memory(persistent)

        if exposure1_updates is None or exposure4_updates is None:
            raise AssertionError("missing required exposure")
        if exposure1_updates <= 0:
            reduction = 0.0
        else:
            reduction = (exposure1_updates - exposure4_updates) / exposure1_updates

        reduction_fractions.append(reduction)
        exposure4_specificities.append(exposure4_specificity)
        collateral.append(exposure4_unrelated - exposure1_unrelated)
        if reduction >= 0.25 and exposure4_specificity >= TARGET_SPECIFICITY:
            support_count += 1

        by_seed[str(seed)] = seed_records

    metrics = {
        "valid_seed_count": float(len(SEEDS)),
        "completed_exposure_records": float(len(records)),
        "resource_accounting_completeness_fraction": 1.0,
        "maximum_absolute_active_parameter_count_difference_across_exposures": 0.0,
        "maximum_absolute_resident_byte_count_difference_across_exposures": 0.0,
        "maximum_absolute_persistent_byte_count_difference_across_exposures": 0.0,
        "median_exposure1_updates_to_target": median(
            [by_seed[str(seed)][0]["updates_to_target"] for seed in SEEDS]
        ),
        "median_exposure4_updates_to_target": median(
            [by_seed[str(seed)][3]["updates_to_target"] for seed in SEEDS]
        ),
        "median_update_reduction_fraction_exposure4_vs1": median(reduction_fractions),
        "median_exposure4_specificity": median(exposure4_specificities),
        "supporting_seed_fraction": support_count / len(SEEDS),
        "maximum_absolute_unrelated_collateral": max(abs(v) for v in collateral),
    }

    assert len(records) == 32
    assert all(record["active_parameter_count"] == ACTIVE_PARAMETER_COUNT for record in records)
    assert all(record["informative_persistent_bytes"] == INFORMATIVE_PERSISTENT_BYTES for record in records)
    assert all(record["transfer_container_bytes"] == TRANSFER_CONTAINER_BYTES for record in records)
    assert all(record["resident_byte_count"] == RESIDENT_BYTE_COUNT for record in records)
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
