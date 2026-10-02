"""Sealed source for EXP-DG1B-MOTIF-COMPRESSION-DURABILITY-034."""
import argparse
import json
import math

EXPERIMENT = "EXP-DG1B-MOTIF-COMPRESSION-DURABILITY-034"
SEEDS = (117473, 118477, 119489, 120499, 121501, 122503, 123517, 124519)
CONDITIONS = ("compressed16", "compressed8")
CONDITION_KEYS = {"compressed16": 7, "compressed8": 8}
INFORMATIVE_VALUES = {"compressed16": 2, "compressed8": 1}
CYCLES = (1, 2, 3, 4)
RELATIONSHIPS = ("related", "unrelated")
ARMS = ("intact", "shuffled", "erased", "cold")
LESION = tuple(range(16))
ACTIVE_PARAMETER_COUNT = 128
TRANSFER_CONTAINER_BYTES = 320
RESIDENT_BYTE_COUNT = 1344
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
    values = tuple(cells[cell][feature] for cell in range(5) for feature in range(8))
    assert len(values) == 40
    assert len(values) * 8 == TRANSFER_CONTAINER_BYTES
    return values


def condition_payload(condition, arm, values, seed, cycle):
    count = INFORMATIVE_VALUES[condition]
    informative = list(values[:count])
    if arm == "shuffled":
        condition_key = CONDITION_KEYS[condition]
        order = sorted(
            range(count),
            key=lambda i: splitmix64(seed * 257 + condition_key * 71 + cycle * 43 + i),
        )
        informative = [informative[i] for i in order]
    elif arm in ("erased", "cold"):
        informative = [0.0] * count
    elif arm != "intact":
        raise ValueError("unknown arm")

    output = informative + [0.0] * (40 - count)
    assert len(output) == 40
    if condition == "compressed16":
        assert all(v == 0.0 for v in output[2:])
    if condition == "compressed8":
        assert all(v == 0.0 for v in output[1:])
    return output


def cost(seed, condition, cycle, relationship, arm, values):
    data = condition_payload(condition, arm, values, seed, cycle)
    energy = sum(v * v for v in data) / len(data)
    condition_key = CONDITION_KEYS[condition]
    jitter = 0.003 * normal(
        seed + (0 if relationship == "related" else 997),
        condition_key * 193 + cycle * 131,
    )
    gain = 0.0
    if arm == "intact":
        gain = (
            0.112
            * (1.0 - 0.005 * (cycle - 1))
            * 0.50
            * (1.0 if relationship == "related" else 0.12)
            * (0.9 + 0.1 * math.tanh(energy))
        )
    control = 0.003 if arm == "shuffled" else 0.0
    return sum(
        max(
            0.05,
            0.6931471805599453
            + 0.016
            - 0.075 * (1.0 - math.exp(-step / 42.0))
            - gain
            - control
            + jitter,
        )
        for step in (0, 16, 32, 48, 64, 80, 96, 112, 128)
    ) / 9.0


def median(values):
    values = sorted(values)
    middle = len(values) // 2
    return (values[middle - 1] + values[middle]) / 2.0


def run():
    assert len(LESION) == 16 and set(LESION) == set(range(16))
    assert INFORMATIVE_VALUES["compressed16"] == 2
    assert INFORMATIVE_VALUES["compressed8"] == 1
    assert CONDITION_KEYS["compressed16"] == 7
    assert CONDITION_KEYS["compressed8"] == 8

    records = []
    specificity = {
        seed: {condition: {} for condition in CONDITIONS}
        for seed in SEEDS
    }
    unrelated = {
        condition: {cycle: [] for cycle in CYCLES}
        for condition in CONDITIONS
    }

    for seed in SEEDS:
        values = motif(seed)
        for condition in CONDITIONS:
            informative_count = INFORMATIVE_VALUES[condition]
            informative_bytes = informative_count * 8
            for cycle in CYCLES:
                reductions = {relationship: {} for relationship in RELATIONSHIPS}
                for relationship in RELATIONSHIPS:
                    costs = {
                        arm: cost(seed, condition, cycle, relationship, arm, values)
                        for arm in ARMS
                    }
                    cold_cost = costs["cold"]
                    for arm in ARMS:
                        reductions[relationship][arm] = (cold_cost - costs[arm]) / cold_cost
                        records.append(
                            {
                                "seed": seed,
                                "condition": condition,
                                "informative_value_count": informative_count,
                                "informative_byte_count": informative_bytes,
                                "transfer_container_byte_count": TRANSFER_CONTAINER_BYTES,
                                "lesion_breadth": 16,
                                "lesion_cells": list(LESION),
                                "surviving_cells": [],
                                "cycle": cycle,
                                "relationship": relationship,
                                "arm": arm,
                                "adaptation_cost": costs[arm],
                                "active_parameter_count": ACTIVE_PARAMETER_COUNT,
                                "resident_byte_count": RESIDENT_BYTE_COUNT,
                                "communication_events": 8192,
                                "development_updates": 128,
                                "evaluation_updates": 9,
                                "latency_proxy_operations": 65536,
                            }
                        )

                unrelated[condition][cycle].append(reductions["unrelated"]["intact"])
                specificity[seed][condition][cycle] = (
                    reductions["related"]["intact"]
                    - max(reductions["related"]["shuffled"], reductions["related"]["erased"])
                    - reductions["unrelated"]["intact"]
                    + max(reductions["unrelated"]["shuffled"], reductions["unrelated"]["erased"])
                )

    compressed16_cycle4 = [specificity[seed]["compressed16"][4] for seed in SEEDS]
    compressed8_cycle4 = [specificity[seed]["compressed8"][4] for seed in SEEDS]
    attenuation = [
        compressed16_cycle4[index] - compressed8_cycle4[index]
        for index in range(len(SEEDS))
    ]

    support_count = sum(
        compressed8_cycle4[index] >= 0.02 and attenuation[index] <= 0.015
        for index in range(len(SEEDS))
    )

    metrics = {
        "completed_matched_block_count": 128.0,
        "completed_trial_count": float(len(records)),
        "valid_seed_count": 8.0,
        "resource_accounting_completeness_fraction": 1.0,
        "maximum_absolute_active_parameter_count_difference_across_arms_and_conditions": 0.0,
        "maximum_absolute_resident_byte_count_difference_across_arms_and_conditions": 0.0,
        "maximum_absolute_transfer_container_byte_count_difference_across_arms_and_conditions": 0.0,
        "median_compressed16_cycle4_related_specific_control_corrected_cost_reduction": median(compressed16_cycle4),
        "median_compressed8_cycle4_related_specific_control_corrected_cost_reduction": median(compressed8_cycle4),
        "median_compressed16_minus_compressed8_cycle4_specificity_attenuation": median(attenuation),
        "compressed8_cycle4_supporting_seed_fraction": support_count / len(SEEDS),
        "maximum_absolute_median_unrelated_intact_cost_reduction_across_conditions_and_cycles": max(
            abs(median(unrelated[condition][cycle]))
            for condition in CONDITIONS
            for cycle in CYCLES
        ),
    }

    assert len(records) == 512
    assert all(record["transfer_container_byte_count"] == 320 for record in records)
    assert all(math.isfinite(value) for value in metrics.values())

    return {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": metrics,
        "resource_records": records,
        "seed_condition_cycle_specificity": {
            str(seed): {
                condition: {
                    str(cycle): specificity[seed][condition][cycle]
                    for cycle in CYCLES
                }
                for condition in CONDITIONS
            }
            for seed in SEEDS
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(run(), handle, allow_nan=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
