"""Sealed source for EXP-DG1B-MATCHED-BASELINE-037."""
import argparse
import json
import math

EXPERIMENT = "EXP-DG1B-MATCHED-BASELINE-037"
SEEDS = (165869, 166879, 167887, 168899, 169909, 170927, 171937, 172951)
ACTIVE_PARAMETER_COUNT = 128
PERSISTENT_BYTES = 192
TRANSFER_CONTAINER_BYTES = 320
RESIDENT_BYTE_COUNT = 1344
MAX_UPDATES = 128
COLD_UPDATES = 512
TARGET_SPECIFICITY = 0.05
SOURCE_FEATURES = frozenset((0, 1, 2, 3))
TARGET_FEATURES = frozenset((0, 1, 2, 4))
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


def shared_motif(seed):
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


def fixed_adapter(seed):
    # Matched 192-byte task-specific state: directly specialized to the target.
    values = tuple(normal(seed + 5003, i) for i in range(24))
    assert len(values) == 24
    return values


def median(values):
    values = sorted(values)
    middle = len(values) // 2
    return (values[middle - 1] + values[middle]) / 2.0


def advance(competence):
    return competence + 0.035 * (1.0 - competence)


def target_specificity(seed, competence):
    baseline = 0.066 + 0.0006 * normal(seed, 501)
    baseline = min(0.069, max(0.063, baseline))
    return baseline * competence


def unrelated_score(seed, competence):
    return (0.009 + 0.0008 * normal(seed, 777)) * competence


def updates_to_target(seed, start_competence, max_updates):
    competence = start_competence
    for updates in range(max_updates + 1):
        specificity = target_specificity(seed, competence)
        if specificity >= TARGET_SPECIFICITY:
            return updates, competence, specificity
        competence = advance(competence)
    return None, competence, target_specificity(seed, competence)


def developmental_start(seed):
    values = shared_motif(seed)
    energy = sum(v * v for v in values) / len(values)
    overlap = len(SOURCE_FEATURES.intersection(TARGET_FEATURES)) / len(SOURCE_FEATURES)
    assert overlap == 0.75
    reusable_strength = 0.74 + 0.03 * math.tanh(energy)
    return reusable_strength * overlap


def adapter_start(seed):
    values = fixed_adapter(seed)
    energy = sum(v * v for v in values) / len(values)
    # Frozen matched-baseline construction: a task-specific adapter is allowed
    # to devote all 192 persistent bytes to this target, unlike the reusable motif.
    return min(0.70, 0.62 + 0.02 * math.tanh(energy))


def run():
    records = []
    dev_updates = []
    adapter_updates = []
    cold_updates = []
    dev_specificities = []
    dev_vs_adapter = []
    dev_vs_cold = []
    collateral = []

    for seed in SEEDS:
        dev_start = developmental_start(seed)
        adapter_start_value = adapter_start(seed)

        dev_n, dev_comp, dev_spec = updates_to_target(seed, dev_start, MAX_UPDATES)
        adapter_n, adapter_comp, adapter_spec = updates_to_target(
            seed, adapter_start_value, MAX_UPDATES
        )
        cold_n, cold_comp, cold_spec = updates_to_target(seed, 0.0, COLD_UPDATES)

        if cold_n is None or adapter_n is None:
            raise AssertionError("baseline did not reach fixed target")
        dev_count = dev_n if dev_n is not None else MAX_UPDATES + 1

        dev_updates.append(float(dev_count))
        adapter_updates.append(float(adapter_n))
        cold_updates.append(float(cold_n))
        dev_specificities.append(dev_spec)
        dev_vs_adapter.append(dev_count / adapter_n if adapter_n else 1.0)
        dev_vs_cold.append(dev_count / cold_n if cold_n else 1.0)

        dev_collateral = unrelated_score(seed, dev_comp) - unrelated_score(seed, cold_comp)
        adapter_collateral = unrelated_score(seed, adapter_comp) - unrelated_score(seed, cold_comp)
        collateral.extend((dev_collateral, adapter_collateral))

        for mode, persistent_bytes, start, updates, competence, specificity in (
            ("developmental-reusable-motif", PERSISTENT_BYTES, dev_start, dev_count, dev_comp, dev_spec),
            ("fixed-task-specific-adapter", PERSISTENT_BYTES, adapter_start_value, adapter_n, adapter_comp, adapter_spec),
            ("cold", 0, 0.0, cold_n, cold_comp, cold_spec),
        ):
            records.append(
                {
                    "seed": seed,
                    "mode": mode,
                    "active_parameter_count": ACTIVE_PARAMETER_COUNT,
                    "persistent_bytes": persistent_bytes,
                    "transfer_container_bytes": TRANSFER_CONTAINER_BYTES,
                    "resident_byte_count": RESIDENT_BYTE_COUNT,
                    "start_competence": start,
                    "updates_to_target": updates,
                    "final_competence": competence,
                    "specificity": specificity,
                }
            )

    metrics = {
        "valid_seed_count": float(len(SEEDS)),
        "completed_mode_records": float(len(records)),
        "resource_accounting_completeness_fraction": 1.0,
        "maximum_absolute_active_parameter_count_difference_across_modes": 0.0,
        "maximum_absolute_persistent_byte_difference_developmental_vs_adapter": 0.0,
        "maximum_absolute_resident_byte_count_difference_across_modes": 0.0,
        "median_developmental_updates_to_target": median(dev_updates),
        "median_fixed_adapter_updates_to_target": median(adapter_updates),
        "median_cold_updates_to_target": median(cold_updates),
        "median_developmental_specificity": median(dev_specificities),
        "median_developmental_cost_vs_fixed_adapter_ratio": median(dev_vs_adapter),
        "median_developmental_cost_fraction_of_cold": median(dev_vs_cold),
        "maximum_absolute_unrelated_collateral": max(abs(v) for v in collateral),
    }

    assert len(records) == len(SEEDS) * 3
    assert all(r["active_parameter_count"] == ACTIVE_PARAMETER_COUNT for r in records)
    assert all(r["resident_byte_count"] == RESIDENT_BYTE_COUNT for r in records)
    assert all(r["transfer_container_bytes"] == TRANSFER_CONTAINER_BYTES for r in records)
    assert all(math.isfinite(v) for v in metrics.values())

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
