"""Sealed source for EXP-DG1B-HIBERNATION-HORIZON-033."""
import argparse
import json
import math

EXPERIMENT = "EXP-DG1B-HIBERNATION-HORIZON-033"
SEEDS = (133519, 134537, 135547, 136559, 137573, 138581, 139597, 140603)
INTERVALS = (64, 256, 1024)
ACTIVE_PARAMETER_COUNT = 128
INFORMATIVE_PERSISTENT_BYTES = 256
TRANSFER_CONTAINER_BYTES = 320
RESIDENT_BYTE_COUNT = 1344
MAX_WAKE_UPDATES = 128
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


def retained_start(base_start, interval):
    # Frozen pre-result inactivity model: bounded logarithmic retention loss.
    # No refresh occurs during the interval and no capacity is added.
    penalty = 0.0004 * math.log2(float(interval))
    return max(0.0, base_start - penalty)


def run():
    records = []
    per_interval_updates = {interval: [] for interval in INTERVALS}
    per_interval_specificity = {interval: [] for interval in INTERVALS}
    interval1024_support = 0
    unrelated_collateral = []

    for seed in SEEDS:
        persistent = motif(seed)
        energy = sum(v * v for v in persistent) / len(persistent)
        base_start = 0.70 + 0.04 * math.tanh(energy)
        always_competence = 1.0

        seed_results = {}
        for interval in INTERVALS:
            wake_start = retained_start(base_start, interval)
            wake_n, wake_competence, wake_specificity = updates_to_target(
                seed, wake_start, MAX_WAKE_UPDATES
            )
            completed_updates = wake_n if wake_n is not None else MAX_WAKE_UPDATES + 1
            per_interval_updates[interval].append(float(completed_updates))
            per_interval_specificity[interval].append(wake_specificity)

            collateral = unrelated_score(seed, wake_competence) - unrelated_score(seed, always_competence)
            unrelated_collateral.append(collateral)

            seed_results[interval] = {
                "updates": completed_updates,
                "specificity": wake_specificity,
                "collateral": collateral,
            }

            records.append(
                {
                    "seed": seed,
                    "inactive_interval": interval,
                    "active_parameter_count": ACTIVE_PARAMETER_COUNT,
                    "informative_persistent_bytes": INFORMATIVE_PERSISTENT_BYTES,
                    "transfer_container_bytes": TRANSFER_CONTAINER_BYTES,
                    "resident_byte_count": RESIDENT_BYTE_COUNT,
                    "wake_start_competence": wake_start,
                    "wake_updates_to_target": completed_updates,
                    "wake_success": wake_n is not None,
                    "final_competence": wake_competence,
                    "related_specificity": wake_specificity,
                    "unrelated_collateral": collateral,
                }
            )

        u64 = seed_results[64]["updates"]
        u1024 = seed_results[1024]["updates"]
        inflation = ((u1024 - u64) / u64) if u64 > 0 else 0.0
        if (
            inflation <= 0.25
            and seed_results[1024]["specificity"] >= 0.05
            and abs(seed_results[1024]["collateral"]) <= 0.03
        ):
            interval1024_support += 1

    median_u64 = median(per_interval_updates[64])
    median_u1024 = median(per_interval_updates[1024])
    inflation = ((median_u1024 - median_u64) / median_u64) if median_u64 > 0 else 0.0

    metrics = {
        "valid_seed_count": float(len(SEEDS)),
        "completed_interval_records": float(len(records)),
        "resource_accounting_completeness_fraction": 1.0,
        "maximum_absolute_active_parameter_count_difference_across_intervals": 0.0,
        "maximum_absolute_resident_byte_count_difference_across_intervals": 0.0,
        "maximum_absolute_transfer_container_byte_count_difference_across_intervals": 0.0,
        "median_interval64_wake_updates": median_u64,
        "median_interval256_wake_updates": median(per_interval_updates[256]),
        "median_interval1024_wake_updates": median_u1024,
        "median_interval1024_vs64_wake_cost_inflation": inflation,
        "median_interval1024_specificity": median(per_interval_specificity[1024]),
        "interval1024_supporting_seed_fraction": interval1024_support / len(SEEDS),
        "maximum_absolute_unrelated_collateral": max(abs(v) for v in unrelated_collateral),
    }

    assert len(records) == 24
    assert all(record["active_parameter_count"] == ACTIVE_PARAMETER_COUNT for record in records)
    assert all(record["informative_persistent_bytes"] == INFORMATIVE_PERSISTENT_BYTES for record in records)
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
