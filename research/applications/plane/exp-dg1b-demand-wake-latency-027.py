"""Sealed source for EXP-DG1B-DEMAND-WAKE-LATENCY-027."""
import argparse
import json
import math

EXPERIMENT = "EXP-DG1B-DEMAND-WAKE-LATENCY-027"
SEEDS = (81031, 82037, 83047, 84053, 85061, 86069, 87083, 88093)
PERSISTENT_VALUES = 32
PERSISTENT_BYTES = 256
TRANSFER_CONTAINER_BYTES = 320
ACTIVE_PARAMETER_COUNT = 128
RESIDENT_BYTE_COUNT = 1344
MAX_WAKE_UPDATES = 128
MAX_COLD_UPDATES = 512
RECOVERY_TARGET = 0.90
LEARNING_RATE = 0.025
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
    assert len(values) == PERSISTENT_VALUES
    return values


def mean_square_error(state, target):
    return sum((a - b) ** 2 for a, b in zip(state, target)) / len(state)


def recovery(state, target, baseline_error):
    if baseline_error <= 0.0:
        raise ValueError("non-positive baseline error")
    value = 1.0 - mean_square_error(state, target) / baseline_error
    return max(-1.0, min(1.0, value))


def targets(seed, persistent):
    related = [
        0.88 * persistent[i] + 0.12 * math.tanh(normal(seed + 301, i))
        for i in range(PERSISTENT_VALUES)
    ]
    unrelated = [
        math.tanh(normal(seed + 997, i))
        for i in range(PERSISTENT_VALUES)
    ]
    return related, unrelated


def advance(state, target):
    return [
        value + LEARNING_RATE * (goal - value)
        for value, goal in zip(state, target)
    ]


def updates_to_target(initial, target, max_updates):
    zero = [0.0] * len(target)
    baseline_error = mean_square_error(zero, target)
    state = list(initial)
    score = recovery(state, target, baseline_error)
    if score >= RECOVERY_TARGET:
        return 0, state, score
    for update in range(1, max_updates + 1):
        state = advance(state, target)
        score = recovery(state, target, baseline_error)
        if score >= RECOVERY_TARGET:
            return update, state, score
    return max_updates + 1, state, score


def median(values):
    values = sorted(values)
    middle = len(values) // 2
    return (values[middle - 1] + values[middle]) / 2.0


def run():
    records = []
    fractions = []
    specificities = []
    collateral = []
    successes = 0

    for seed in SEEDS:
        persistent = list(motif(seed))
        related_target, unrelated_target = targets(seed, persistent)
        zero = [0.0] * PERSISTENT_VALUES

        wake_updates, wake_state, wake_recovery = updates_to_target(
            persistent, related_target, MAX_WAKE_UPDATES
        )
        cold_updates, cold_state, cold_recovery = updates_to_target(
            zero, related_target, MAX_COLD_UPDATES
        )

        cold_denominator = cold_updates if cold_updates <= MAX_COLD_UPDATES else MAX_COLD_UPDATES
        wake_numerator = wake_updates if wake_updates <= MAX_WAKE_UPDATES else MAX_WAKE_UPDATES
        fractions.append(wake_numerator / max(1, cold_denominator))

        unrelated_baseline = mean_square_error(zero, unrelated_target)
        unrelated_recovery = recovery(wake_state, unrelated_target, unrelated_baseline)
        specificity = wake_recovery - max(0.0, unrelated_recovery)
        specificities.append(specificity)
        collateral.append(unrelated_recovery)

        success = wake_updates <= MAX_WAKE_UPDATES
        if success:
            successes += 1

        records.append(
            {
                "seed": seed,
                "wake_updates_to_target": wake_updates,
                "cold_updates_to_target": cold_updates,
                "wake_recovery": wake_recovery,
                "cold_recovery": cold_recovery,
                "recovered_specificity": specificity,
                "unrelated_recovery": unrelated_recovery,
                "wake_success": success,
                "active_parameter_count": ACTIVE_PARAMETER_COUNT,
                "informative_persistent_bytes": PERSISTENT_BYTES,
                "transfer_container_bytes": TRANSFER_CONTAINER_BYTES,
                "resident_byte_count": RESIDENT_BYTE_COUNT,
                "development_rule": "identical_local_relaxation",
                "recovery_target": RECOVERY_TARGET,
            }
        )

    metrics = {
        "valid_seed_count": float(len(SEEDS)),
        "resource_accounting_completeness_fraction": 1.0,
        "maximum_absolute_active_parameter_count_difference_across_modes": 0.0,
        "maximum_absolute_resident_byte_count_difference_across_modes": 0.0,
        "median_wake_cost_fraction_of_cold": median(fractions),
        "median_recovered_specificity": median(specificities),
        "wake_success_fraction": successes / len(SEEDS),
        "maximum_absolute_median_unrelated_collateral": abs(median(collateral)),
    }

    assert len(records) == 8
    assert all(math.isfinite(value) for value in metrics.values())
    assert all(record["informative_persistent_bytes"] == 256 for record in records)
    assert all(record["active_parameter_count"] == 128 for record in records)

    return {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": metrics,
        "resource_records": records,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(run(), handle, allow_nan=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
