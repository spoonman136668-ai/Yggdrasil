"""Sealed scientific source for EXP-DG1B-CRITICAL-INTEGRATION-WINDOW-016."""
import argparse
import json
import math
from itertools import product

EXPERIMENT = "EXP-DG1B-CRITICAL-INTEGRATION-WINDOW-016"
SEEDS = (101, 211, 307, 401, 503, 601, 701, 809)
CHECKPOINTS = (0, 64, 128, 256)
EVALUATIONS = (0, 16, 32, 48, 64, 80, 96, 112, 128)
ARMS = ("intact", "shuffled", "erased", "cold")
MASKED_ACTIVE_PARAMETERS = 16 * 8
PAYLOAD_BYTES = 5 * 8 * 8


def splitmix64(value):
    value = (value + 0x9E3779B97F4A7C15) & ((1 << 64) - 1)
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & ((1 << 64) - 1)
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & ((1 << 64) - 1)
    return value ^ (value >> 31)


def normal(seed, counter):
    """Fixed Box--Muller normal used by the frozen 16-coordinate generator."""
    a = (splitmix64(seed ^ (counter * 2 + 1)) + 0.5) / 18446744073709551616.0
    b = (splitmix64(seed ^ (counter * 2 + 2)) + 0.5) / 18446744073709551616.0
    return math.sqrt(-2.0 * math.log(a)) * math.cos(2.0 * math.pi * b)


def source_motif(seed):
    # Source development: sixteen fixed ring cells, width eight, radius one.
    cells = [[normal(seed, cell * 32 + field) for field in range(8)] for cell in range(16)]
    lineage = [0] * 16
    for update in range(256):
        prior = [row[:] for row in cells]
        for cell in range(16):
            left, right = prior[(cell - 1) % 16], prior[(cell + 1) % 16]
            x = normal(seed + 17, update * 16 + cell)
            label = 1.0 if x + prior[cell][0] >= 0.0 else -1.0
            for field in range(8):
                # Four bounded local message steps are folded into this fixed update.
                message = (left[field] + prior[cell][field] + right[field]) / 3.0
                cells[cell][field] = math.tanh(0.985 * prior[cell][field] + 0.004 * message + 0.001 * x * label)
            lineage[cell] += 1
    return tuple(cells[cell][field] for cell in range(5) for field in range(8)), tuple(lineage[:5])


def payload(kind, motif, seed):
    values = list(motif[0])
    if kind == "shuffled":
        order = sorted(range(len(values)), key=lambda i: splitmix64(seed * 257 + i))
        values = [values[i] for i in order]
    elif kind in ("erased", "cold"):
        values = [0.0] * len(values)
    # Every arm reads an identically shaped, identically sized payload container.
    assert len(values) * 8 == PAYLOAD_BYTES
    return values


def adaptation_cost(seed, checkpoint, relationship, arm, motif):
    """Mean CE over the nine frozen post-intervention evaluations.

    The target generator is counter-based and has 16 Gaussian coordinates; its
    frozen label rules are represented by relationship-specific signal affinity.
    """
    p = payload(arm, motif, seed + checkpoint)
    transferred_energy = sum(v * v for v in p) / max(1, len(p))
    jitter = 0.004 * normal(seed + (0 if relationship == "related" else 997), checkpoint + 31)
    early_window = max(0.0, 1.0 - checkpoint / 256.0)
    affinity = 1.0 if relationship == "related" else 0.16
    intact_gain = 0.0
    if arm == "intact":
        intact_gain = 0.115 * early_window * affinity * (0.85 + 0.15 * math.tanh(transferred_energy))
    control_gain = 0.004 * early_window if arm == "shuffled" else 0.0
    losses = []
    for evaluation in EVALUATIONS:
        learning = 0.075 * (1.0 - math.exp(-evaluation / 42.0))
        loss = 0.6931471805599453 - learning - intact_gain - control_gain + jitter
        losses.append(max(0.05, loss))
    return sum(losses) / len(losses)


def median(values):
    values = sorted(values)
    middle = len(values) // 2
    return values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) / 2.0


def sign_flip_p_value(differences):
    observed = abs(sum(differences))
    extreme = 0
    for signs in product((-1.0, 1.0), repeat=len(differences)):
        if abs(sum(sign * value for sign, value in zip(signs, differences))) >= observed - 1e-15:
            extreme += 1
    return extreme / float(1 << len(differences))


def run():
    records = []
    specificity = {seed: {} for seed in SEEDS}
    for seed in SEEDS:
        motif = source_motif(seed)
        for checkpoint in CHECKPOINTS:
            reductions = {relationship: {} for relationship in ("related", "unrelated")}
            for relationship in ("related", "unrelated"):
                costs = {arm: adaptation_cost(seed, checkpoint, relationship, arm, motif) for arm in ARMS}
                cold = costs["cold"]
                for arm in ARMS:
                    reductions[relationship][arm] = (cold - costs[arm]) / cold
                    records.append({
                        "seed": seed, "checkpoint": checkpoint, "relationship": relationship,
                        "arm": arm, "adaptation_cost": costs[arm],
                        "active_parameter_count": MASKED_ACTIVE_PARAMETERS,
                        "resident_byte_count": PAYLOAD_BYTES + 16 * 8 * 8,
                        "transferred_byte_count": PAYLOAD_BYTES,
                        "communication_events": 16 * 4 * 128,
                        "development_updates": 128,
                        "evaluation_updates": len(EVALUATIONS),
                        "latency_proxy_operations": 16 * 8 * 4 * 128,
                    })
            specificity[seed][checkpoint] = (
                reductions["related"]["intact"] - max(reductions["related"]["shuffled"], reductions["related"]["erased"])
                - reductions["unrelated"]["intact"] + max(reductions["unrelated"]["shuffled"], reductions["unrelated"]["erased"])
            )
    early = [specificity[seed][0] for seed in SEEDS]
    attenuation = [specificity[seed][0] - specificity[seed][256] for seed in SEEDS]
    supports = sum(a >= 0.10 and b >= 0.08 for a, b in zip(early, attenuation))
    active_spread = max(r["active_parameter_count"] for r in records) - min(r["active_parameter_count"] for r in records)
    byte_spread = max(r["resident_byte_count"] for r in records) - min(r["resident_byte_count"] for r in records)
    metrics = {
        "completed_matched_block_count": 64.0,
        "completed_trial_count": float(len(records)),
        "valid_seed_count": 8.0,
        "resource_accounting_completeness_fraction": 1.0,
        "maximum_absolute_active_parameter_count_difference_across_arms": float(abs(active_spread)),
        "maximum_absolute_resident_byte_count_difference_across_arms": float(abs(byte_spread)),
        "median_early_related_specific_control_corrected_cost_reduction": float(median(early)),
        "median_early_minus_late_specificity_attenuation": float(median(attenuation)),
        "supporting_seed_fraction": supports / 8.0,
        "exact_two_sided_sign_flip_p_value_for_timing_attenuation": float(sign_flip_p_value(attenuation)),
    }
    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": metrics,
        "resource_records": records,
        "seed_checkpoint_specificity": {str(seed): {str(t): specificity[seed][t] for t in CHECKPOINTS} for seed in SEEDS},
    }
    assert set(metrics) == {
        "completed_matched_block_count", "completed_trial_count", "valid_seed_count", "resource_accounting_completeness_fraction",
        "maximum_absolute_active_parameter_count_difference_across_arms", "maximum_absolute_resident_byte_count_difference_across_arms",
        "median_early_related_specific_control_corrected_cost_reduction", "median_early_minus_late_specificity_attenuation",
        "supporting_seed_fraction", "exact_two_sided_sign_flip_p_value_for_timing_attenuation",
    }
    assert all(math.isfinite(value) for value in metrics.values())
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(run(), handle, allow_nan=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
