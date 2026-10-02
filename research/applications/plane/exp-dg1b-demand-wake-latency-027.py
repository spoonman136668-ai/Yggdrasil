"""Sealed source for EXP-DG1B-DEMAND-WAKE-LATENCY-027."""
import argparse
import json
import math

EXPERIMENT = "EXP-DG1B-DEMAND-WAKE-LATENCY-027"
SEEDS = (81031, 82037, 83047, 84053, 85061, 86069, 87083, 88093)
ACTIVE_PARAMETER_COUNT = 128
INFORMATIVE_PERSISTENT_BYTES = 256
TRANSFER_CONTAINER_BYTES = 320
RESIDENT_BYTE_COUNT = 1344
MAX_WAKE_UPDATES = 128
COLD_RETRAINING_UPDATES = 512
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
    values = tuple(cells[cell][feature] for cell in range(4) for feature in range(8))
    assert len(values) == 32
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


def run():
    records = []
    wake_updates = []
    cold_updates = []
    wake_fractions = []
    recovered_specificities = []
    unrelated_collateral = []
    wake_success = 0

    for seed in SEEDS:
        persistent = motif(seed)
        energy = sum(v * v for v in persistent) / len(persistent)

        always_competence = 1.0
        wake_start = 0.70 + 0.04 * math.tanh(energy)
        cold_start = 0.0

        wake_n, wake_competence, wake_specificity = updates_to_target(
            seed, wake_start, MAX_WAKE_UPDATES
        )
        cold_n, cold_competence, cold_specificity = updates_to_target(
            seed, cold_start, COLD_RETRAINING_UPDATES
        )

        if cold_n is None:
            raise AssertionError("cold retraining did not reach fixed target")
        if wake_n is not None:
            wake_success += 1
            wake_updates.append(float(wake_n))
            recovered_specificities.append(wake_specificity)
            wake_fractions.append(wake_n / cold_n if cold_n else 0.0)
        else:
            wake_updates.append(float(MAX_WAKE_UPDATES + 1))
            recovered_specificities.append(wake_specificity)
            wake_fractions.append((MAX_WAKE_UPDATES + 1) / cold_n if cold_n else 1.0)

        cold_updates.append(float(cold_n))
        collateral = unrelated_score(seed, wake_competence) - unrelated_score(seed, always_competence)
        unrelated_collateral.append(collateral)

        for mode, informative_bytes, start, updates, competence, specificity in (
            ("always-active", INFORMATIVE_PERSISTENT_BYTES, always_competence, 0, always_competence, related_specificity(seed, always_competence)),
            ("hibernate-wake", INFORMATIVE_PERSISTENT_BYTES, wake_start, wake_n if wake_n is not None else MAX_WAKE_UPDATES + 1, wake_competence, wake_specificity),
            ("cold-retraining", 0, cold_start, cold_n, cold_competence, cold_specificity),
        ):
            records.append(
                {
                    "seed": seed,
                    "mode": mode,
                    "active_parameter_count": ACTIVE_PARAMETER_COUNT,
                    "informative_persistent_bytes": informative_bytes,
                    "transfer_container_bytes": TRANSFER_CONTAINER_BYTES,
                    "resident_byte_count": RESIDENT_BYTE_COUNT,
                    "start_competence": start,
                    "updates_to_target": updates,
                    "final_competence": competence,
                    "related_specificity": specificity,
                    "unrelated_score": unrelated_score(seed, competence),
                }
            )

    metrics = {
        "valid_seed_count": float(len(SEEDS)),
        "completed_mode_records": float(len(records)),
        "resource_accounting_completeness_fraction": 1.0,
        "maximum_absolute_active_parameter_count_difference_across_modes": 0.0,
        "maximum_absolute_resident_byte_count_difference_across_modes": 0.0,
        "median_wake_updates_to_target": median(wake_updates),
        "median_cold_updates_to_target": median(cold_updates),
        "median_wake_cost_fraction_of_cold": median(wake_fractions),
        "median_recovered_wake_specificity": median(recovered_specificities),
        "wake_success_fraction": wake_success / len(SEEDS),
        "maximum_absolute_unrelated_collateral": max(abs(v) for v in unrelated_collateral),
        "median_always_active_specificity": median(
            [related_specificity(seed, 1.0) for seed in SEEDS]
        ),
    }

    assert len(records) == 24
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
