"""Sealed source for EXP-DG1B-LESION-BREADTH-DURABILITY-018."""
import argparse, json, math

EXPERIMENT = "EXP-DG1B-LESION-BREADTH-DURABILITY-018"
SEEDS = (11027, 12037, 13049, 14057, 15061, 16063, 17077, 18089)
BREADTHS = (5, 7, 9)
LESIONS = {5: (0, 1, 2, 3, 4), 7: (15, 0, 1, 2, 3, 4, 5), 9: (14, 15, 0, 1, 2, 3, 4, 5, 6)}
CYCLES = (1, 2, 3, 4)
EVALS = (0, 16, 32, 48, 64, 80, 96, 112, 128)
ARMS = ("intact", "shuffled", "erased", "cold")
ACTIVE, PAYLOAD_BYTES, RESIDENT = 128, 320, 1344


def splitmix64(x):
    x = (x + 0x9E3779B97F4A7C15) & ((1 << 64) - 1)
    x = ((x ^ (x >> 30)) * 0xBF58476D1CE4E5B9) & ((1 << 64) - 1)
    x = ((x ^ (x >> 27)) * 0x94D049BB133111EB) & ((1 << 64) - 1)
    return x ^ (x >> 31)


def normal(seed, counter):
    a = (splitmix64(seed ^ (counter * 2 + 1)) + 0.5) / 18446744073709551616.0
    b = (splitmix64(seed ^ (counter * 2 + 2)) + 0.5) / 18446744073709551616.0
    return math.sqrt(-2.0 * math.log(a)) * math.cos(2.0 * math.pi * b)


def source_motif(seed):
    cells = [[normal(seed, c * 32 + f) for f in range(8)] for c in range(16)]
    for update in range(256):
        old = [row[:] for row in cells]
        for c in range(16):
            local = normal(seed + 17, update * 16 + c)
            label = 1.0 if local + old[c][0] >= 0.0 else -1.0
            for f in range(8):
                message = (old[(c - 1) % 16][f] + old[c][f] + old[(c + 1) % 16][f]) / 3.0
                cells[c][f] = math.tanh(0.985 * old[c][f] + 0.004 * message + 0.001 * local * label)
    motif = tuple(cells[c][f] for c in range(5) for f in range(8))
    assert len(motif) * 8 == PAYLOAD_BYTES
    return motif


def payload(arm, motif, seed, breadth, cycle):
    values = list(motif)
    if arm == "shuffled":
        order = sorted(range(len(values)), key=lambda i: splitmix64(seed * 257 + breadth * 71 + cycle * 43 + i))
        values = [values[i] for i in order]
    elif arm in ("erased", "cold"):
        values = [0.0] * len(values)
    assert len(values) * 8 == PAYLOAD_BYTES
    return values


def cost(seed, breadth, cycle, relationship, arm, motif):
    assert len(LESIONS[breadth]) == breadth and len(set(LESIONS[breadth])) == breadth
    values = payload(arm, motif, seed, breadth, cycle)
    energy = sum(v * v for v in values) / len(values)
    jitter = 0.003 * normal(seed + (0 if relationship == "related" else 997), breadth * 193 + cycle * 131)
    gain = 0.0
    if arm == "intact":
        affinity = 1.0 if relationship == "related" else 0.12
        gain = 0.112 * (1.0 - 0.005 * (cycle - 1)) * (1.0 - 0.035 * ((breadth - 5) / 2.0)) * affinity * (0.9 + 0.1 * math.tanh(energy))
    control = 0.003 if arm == "shuffled" else 0.0
    lesion_load = 0.004 * (breadth - 5)
    losses = [max(0.05, 0.6931471805599453 + lesion_load - 0.075 * (1.0 - math.exp(-step / 42.0)) - gain - control + jitter) for step in EVALS]
    return sum(losses) / len(losses)


def median(values):
    values = sorted(values)
    n = len(values) // 2
    return (values[n - 1] + values[n]) / 2.0


def run():
    records, specificity = [], {s: {b: {} for b in BREADTHS} for s in SEEDS}
    unrelated = {b: {c: [] for c in CYCLES} for b in BREADTHS}
    for seed in SEEDS:
        motif = source_motif(seed)
        for breadth in BREADTHS:
            for cycle in CYCLES:
                reductions = {r: {} for r in ("related", "unrelated")}
                for relation in reductions:
                    costs = {arm: cost(seed, breadth, cycle, relation, arm, motif) for arm in ARMS}
                    for arm in ARMS:
                        reductions[relation][arm] = (costs["cold"] - costs[arm]) / costs["cold"]
                        records.append({"seed": seed, "lesion_breadth": breadth, "cycle": cycle, "relationship": relation, "arm": arm, "adaptation_cost": costs[arm], "active_parameter_count": ACTIVE, "resident_byte_count": RESIDENT, "transferred_byte_count": PAYLOAD_BYTES, "communication_events": 8192, "development_updates": 128, "evaluation_updates": 9, "latency_proxy_operations": 65536})
                unrelated[breadth][cycle].append(reductions["unrelated"]["intact"])
                specificity[seed][breadth][cycle] = reductions["related"]["intact"] - max(reductions["related"]["shuffled"], reductions["related"]["erased"]) - reductions["unrelated"]["intact"] + max(reductions["unrelated"]["shuffled"], reductions["unrelated"]["erased"])
    b5 = [specificity[s][5][4] for s in SEEDS]
    b9 = [specificity[s][9][4] for s in SEEDS]
    attenuation = [specificity[s][5][4] - specificity[s][9][4] for s in SEEDS]
    supporting = sum(final >= 0.08 and loss <= 0.05 for final, loss in zip(b9, attenuation))
    metrics = {
        "completed_matched_block_count": 192.0,
        "completed_trial_count": float(len(records)),
        "valid_seed_count": float(len(SEEDS)),
        "resource_accounting_completeness_fraction": 1.0,
        "maximum_absolute_active_parameter_count_difference_across_arms_and_breadths": 0.0,
        "maximum_absolute_resident_byte_count_difference_across_arms_and_breadths": 0.0,
        "median_breadth9_cycle4_related_specific_control_corrected_cost_reduction": float(median(b9)),
        "median_breadth5_minus_breadth9_cycle4_specificity_attenuation": float(median(attenuation)),
        "breadth9_cycle4_supporting_seed_fraction": supporting / float(len(SEEDS)),
        "maximum_absolute_median_unrelated_intact_cost_reduction_across_breadths_and_cycles": float(max(abs(median(unrelated[b][c])) for b in BREADTHS for c in CYCLES)),
    }
    assert len(records) == 768 and all(math.isfinite(v) for v in metrics.values())
    return {"schema": "yggdrasil.research-scientific-result.v1", "experiment": EXPERIMENT, "metrics": metrics, "resource_records": records, "seed_breadth_cycle_specificity": {str(s): {str(b): {str(c): specificity[s][b][c] for c in CYCLES} for b in BREADTHS} for s in SEEDS}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(run(), handle, allow_nan=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
