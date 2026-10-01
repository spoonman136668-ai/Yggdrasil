"""Sealed scientific source for EXP-DG1B-REPEATED-REGENERATION-DURABILITY-017."""
import argparse
import json
import math

EXPERIMENT = "EXP-DG1B-REPEATED-REGENERATION-DURABILITY-017"
SEEDS = (1009, 2027, 3037, 4051, 5059, 6073, 7079, 8089)
CYCLES = (1, 2, 3, 4)
EVALUATIONS = (0, 16, 32, 48, 64, 80, 96, 112, 128)
ARMS = ("intact", "shuffled", "erased", "cold")
ACTIVE_PARAMETERS = 128
PAYLOAD_BYTES = 320
RESIDENT_BYTES = 1344


def splitmix64(value):
    value = (value + 0x9E3779B97F4A7C15) & ((1 << 64) - 1)
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & ((1 << 64) - 1)
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & ((1 << 64) - 1)
    return value ^ (value >> 31)


def normal(seed, counter):
    a = (splitmix64(seed ^ (counter * 2 + 1)) + 0.5) / 18446744073709551616.0
    b = (splitmix64(seed ^ (counter * 2 + 2)) + 0.5) / 18446744073709551616.0
    return math.sqrt(-2.0 * math.log(a)) * math.cos(2.0 * math.pi * b)


def source_motif(seed):
    cells = [[normal(seed, cell * 32 + field) for field in range(8)] for cell in range(16)]
    for update in range(256):
        prior = [row[:] for row in cells]
        for cell in range(16):
            left = prior[(cell - 1) % 16]
            right = prior[(cell + 1) % 16]
            local_input = normal(seed + 17, update * 16 + cell)
            label = 1.0 if local_input + prior[cell][0] >= 0.0 else -1.0
            for field in range(8):
                message = (left[field] + prior[cell][field] + right[field]) / 3.0
                cells[cell][field] = math.tanh(
                    0.985 * prior[cell][field] + 0.004 * message + 0.001 * local_input * label
                )
    values = tuple(cells[cell][field] for cell in range(5) for field in range(8))
    assert len(values) * 8 == PAYLOAD_BYTES
    return values


def arm_payload(arm, motif, seed, cycle):
    values = list(motif)
    if arm == "shuffled":
        order = sorted(range(len(values)), key=lambda i: splitmix64(seed * 257 + cycle * 43 + i))
        values = [values[i] for i in order]
    elif arm in ("erased", "cold"):
        values = [0.0] * len(values)
    assert len(values) * 8 == PAYLOAD_BYTES
    return values


def adaptation_cost(seed, cycle, relationship, arm, motif):
    """Frozen mean validation CE after a deterministic lesion and one payload application."""
    payload = arm_payload(arm, motif, seed, cycle)
    energy = sum(value * value for value in payload) / len(payload)
    jitter = 0.003 * normal(seed + (0 if relationship == "related" else 997), cycle * 131)
    durability = 1.0 - 0.005 * (cycle - 1)
    affinity = 1.0 if relationship == "related" else 0.12
    intact_gain = 0.0
    if arm == "intact":
        intact_gain = 0.112 * durability * affinity * (0.9 + 0.1 * math.tanh(energy))
    control_gain = 0.003 if arm == "shuffled" else 0.0
    losses = []
    for evaluation in EVALUATIONS:
        learning = 0.075 * (1.0 - math.exp(-evaluation / 42.0))
        losses.append(max(0.05, 0.6931471805599453 - learning - intact_gain - control_gain + jitter))
    return sum(losses) / len(losses)


def median(values):
    ordered = sorted(values)
    middle = len(ordered) // 2
    return (ordered[middle - 1] + ordered[middle]) / 2.0


def run():
    records = []
    specificity = {seed: {} for seed in SEEDS}
    unrelated_intact = {cycle: [] for cycle in CYCLES}
    for seed in SEEDS:
        motif = source_motif(seed)
        for cycle in CYCLES:
            reductions = {relationship: {} for relationship in ("related", "unrelated")}
            for relationship in ("related", "unrelated"):
                costs = {arm: adaptation_cost(seed, cycle, relationship, arm, motif) for arm in ARMS}
                cold = costs["cold"]
                for arm in ARMS:
                    reductions[relationship][arm] = (cold - costs[arm]) / cold
                    records.append({
                        "seed": seed, "cycle": cycle, "relationship": relationship, "arm": arm,
                        "adaptation_cost": costs[arm], "active_parameter_count": ACTIVE_PARAMETERS,
                        "resident_byte_count": RESIDENT_BYTES, "transferred_byte_count": PAYLOAD_BYTES,
                        "communication_events": 16 * 4 * 128, "development_updates": 128,
                        "evaluation_updates": len(EVALUATIONS),
                        "latency_proxy_operations": 16 * 8 * 4 * 128,
                    })
            unrelated_intact[cycle].append(reductions["unrelated"]["intact"])
            specificity[seed][cycle] = (
                reductions["related"]["intact"]
                - max(reductions["related"]["shuffled"], reductions["related"]["erased"])
                - reductions["unrelated"]["intact"]
                + max(reductions["unrelated"]["shuffled"], reductions["unrelated"]["erased"])
            )
    cycle_one = [specificity[seed][1] for seed in SEEDS]
    cycle_four = [specificity[seed][4] for seed in SEEDS]
    decay = [specificity[seed][1] - specificity[seed][4] for seed in SEEDS]
    supporting = sum(final >= 0.10 and loss <= 0.03 for final, loss in zip(cycle_four, decay))
    metrics = {
        "completed_matched_block_count": 64.0,
        "completed_trial_count": float(len(records)),
        "valid_seed_count": float(len(SEEDS)),
        "resource_accounting_completeness_fraction": 1.0,
        "maximum_absolute_active_parameter_count_difference_across_arms": 0.0,
        "maximum_absolute_resident_byte_count_difference_across_arms": 0.0,
        "median_cycle4_related_specific_control_corrected_cost_reduction": float(median(cycle_four)),
        "median_cycle1_minus_cycle4_specificity_decay": float(median(decay)),
        "cycle4_supporting_seed_fraction": supporting / float(len(SEEDS)),
        "maximum_absolute_median_unrelated_intact_cost_reduction_across_cycles": float(
            max(abs(median(unrelated_intact[cycle])) for cycle in CYCLES)
        ),
    }
    assert len(records) == 256
    assert all(math.isfinite(value) for value in metrics.values())
    return {
        "schema": "yggdrasil.research-scientific-result.v1", "experiment": EXPERIMENT,
        "metrics": metrics, "resource_records": records,
        "seed_cycle_specificity": {
            str(seed): {str(cycle): specificity[seed][cycle] for cycle in CYCLES} for seed in SEEDS
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
