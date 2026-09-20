#!/usr/bin/env python3
import argparse
import hashlib
import itertools
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HYPER_EDGES = [
    (0,2,7,9),(1,3,6,11),(4,5,9,10),(2,3,5,8),(0,1,4,8),
    (6,7,8,10),(2,4,6,11),(0,3,5,7),(1,7,10,11),(1,5,6,9),
    (3,8,9,10),(0,4,8,11),(0,2,6,10),(1,3,4,7),(2,5,7,11),
    (2,3,4,10),(0,1,5,10),(0,3,9,11),(1,2,8,9),(4,6,7,9),
]
EXPECTED_DEG = (7,7,7,7,7,6,6,7,6,7,7,6)
BLOCKS = 12
CHECKS = 20
PLANES = 4
COST_PAIRS = (
    ("COST_CHECK_1_7", 7, 1),
    ("COST_CHECK_1_6", 6, 1),
    ("COST_CHECK_1_2", 2, 1),
    ("COST_EQUAL", 1, 1),
    ("COST_CHECK_2", 1, 2),
)


def columns_from_edges():
    cols = [0] * BLOCKS
    for i, edge in enumerate(HYPER_EDGES):
        for b in edge:
            cols[b] |= 1 << i
    return tuple(cols)


COLS = columns_from_edges()


def logical_syndrome(mask):
    s = 0
    for b in range(BLOCKS):
        if (mask >> b) & 1:
            s ^= COLS[b]
    return s


def gf2_rank(vectors):
    basis = {}
    for x in vectors:
        v = int(x)
        while v:
            p = v.bit_length() - 1
            if p in basis:
                v ^= basis[p]
            else:
                basis[p] = v
                break
    return len(basis)


def validate_design():
    assert len(HYPER_EDGES) == 20
    assert len(set(HYPER_EDGES)) == 20
    degrees = tuple(c.bit_count() for c in COLS)
    assert degrees == EXPECTED_DEG
    pair_counts = Counter()
    for edge in HYPER_EDGES:
        for a, b in itertools.combinations(edge, 2):
            pair_counts[tuple(sorted((a, b)))] += 1
    assert max(pair_counts.values()) <= 2
    assert sum(1 for _ in range(1 << BLOCKS)) == 4096
    assert math.comb(BLOCKS, 2) == 66
    assert sum(math.comb(CHECKS, w) for w in range(1, 5)) == 6195
    return {
        "edge_count": len(HYPER_EDGES),
        "degree_vector": list(degrees),
        "max_pair_cooccurrence": max(pair_counts.values()),
        "logical_masks": 1 << BLOCKS,
        "two_region_masks": math.comb(BLOCKS, 2),
        "check_only_weight_1_to_4_patterns": sum(math.comb(CHECKS, w) for w in range(1, 5)),
    }


def build_logical_map():
    rows = []
    syndrome_to_masks = defaultdict(list)
    by_weight_hist = {w: Counter() for w in range(BLOCKS + 1)}
    for mask in range(1 << BLOCKS):
        s = logical_syndrome(mask)
        lw = mask.bit_count()
        sw = s.bit_count()
        rows.append((mask, lw, s, sw))
        syndrome_to_masks[s].append(mask)
        by_weight_hist[lw][sw] += 1
    return rows, syndrome_to_masks, by_weight_hist


def summarize_logical_map(rows, syndrome_to_masks, by_weight_hist):
    kernel = [mask for mask, lw, s, sw in rows if mask != 0 and s == 0]
    multiplicities = Counter(len(v) for v in syndrome_to_masks.values())
    by_weight = {}
    for w in range(BLOCKS + 1):
        hist = by_weight_hist[w]
        if not hist:
            continue
        vals = []
        for sw, count in hist.items():
            vals.extend([sw] * count)
        by_weight[str(w)] = {
            "mask_count": len(vals),
            "min_syndrome_weight": min(vals),
            "max_syndrome_weight": max(vals),
            "syndrome_weight_histogram": {str(k): int(v) for k, v in sorted(hist.items())},
        }
    return {
        "gf2_rank": gf2_rank(COLS),
        "distinct_logical_only_syndromes": len(syndrome_to_masks),
        "syndrome_multiplicity_histogram": {str(k): int(v) for k, v in sorted(multiplicities.items())},
        "nonzero_logical_kernel_masks": [
            {"mask": int(m), "blocks": [b for b in range(BLOCKS) if (m >> b) & 1], "logical_weight": m.bit_count()}
            for m in kernel
        ],
        "by_logical_weight": by_weight,
    }


def exact_mimic_metrics(rows):
    singles = []
    for b in range(BLOCKS):
        mask = 1 << b
        s = logical_syndrome(mask)
        singles.append({"block": b, "degree": COLS[b].bit_count(), "check_mimic_weight": s.bit_count(), "syndrome": s})
    pairs = []
    for a, b in itertools.combinations(range(BLOCKS), 2):
        mask = (1 << a) | (1 << b)
        s = logical_syndrome(mask)
        pairs.append({"blocks": [a, b], "check_mimic_weight": s.bit_count(), "syndrome": s})
    pair_min = min(x["check_mimic_weight"] for x in pairs)
    min_pairs = [x for x in pairs if x["check_mimic_weight"] == pair_min]
    min_by_lw = {}
    positive = []
    for w in range(1, BLOCKS + 1):
        vals = [sw for mask, lw, s, sw in rows if lw == w]
        pos = [x for x in vals if x > 0]
        min_by_lw[str(w)] = {
            "minimum": min(pos) if pos else None,
            "zero_syndrome_count": sum(x == 0 for x in vals),
        }
        positive.extend(pos)
    return {
        "single_region": singles,
        "two_region": pairs,
        "two_region_minimum": pair_min,
        "two_region_minimum_pairs": min_pairs,
        "minimum_positive_by_logical_weight": min_by_lw,
        "global_minimum_positive": min(positive),
    }


def make_arrays(rows):
    syndromes = np.asarray([s for _, _, s, _ in rows], dtype=np.uint32)
    logical_weights = np.asarray([lw for _, lw, _, _ in rows], dtype=np.int16)
    pc = np.fromiter((i.bit_count() for i in range(1 << CHECKS)), dtype=np.uint8, count=1 << CHECKS)
    return syndromes, logical_weights, pc


def classify_true(s, true_mask, logical_cost, check_cost, syndromes, logical_weights, popcount_table):
    residual_w = popcount_table[np.bitwise_xor(syndromes, np.uint32(s))].astype(np.int32)
    costs = logical_weights.astype(np.int32) * logical_cost + residual_w * check_cost
    min_cost = int(costs.min())
    minima = np.flatnonzero(costs == min_cost)
    in_min = bool(np.any(minima == true_mask))
    if in_min and len(minima) == 1:
        cls = "TRUE_EXPLANATION_UNIQUE_MINIMUM"
    elif in_min:
        cls = "TRUE_EXPLANATION_TIED_MINIMUM"
    else:
        cls = "TRUE_EXPLANATION_NOT_MINIMUM"
    return {
        "classification": cls,
        "minimum_cost": min_cost,
        "minimum_count": int(len(minima)),
        "minimum_logical_masks": [int(x) for x in minima[:32]],
        "minimum_list_truncated": bool(len(minima) > 32),
        "true_cost": int(costs[true_mask]),
    }


def first_incident(block, n):
    xs = [i for i, edge in enumerate(HYPER_EDGES) if block in edge]
    assert len(xs) >= n
    return xs[:n]


def mask_from_positions(xs):
    m = 0
    for x in xs:
        m |= 1 << x
    return m


def selected_weighted_boundaries(rows, mimic, syndromes, logical_weights, popcount_table):
    min_pair = mimic["two_region_minimum_pairs"][0]["blocks"]
    selected = {
        "SINGLE_LOGICAL_D6": {"syndrome": logical_syndrome(1 << 5), "true_mask": 1 << 5},
        "SINGLE_LOGICAL_D7": {"syndrome": logical_syndrome(1 << 2), "true_mask": 1 << 2},
        "TWO_LOGICAL_MINPAIR": {
            "syndrome": logical_syndrome((1 << min_pair[0]) | (1 << min_pair[1])),
            "true_mask": (1 << min_pair[0]) | (1 << min_pair[1]),
            "derived_blocks": min_pair,
        },
        "CHECK4_INCIDENT_D6": {"syndrome": mask_from_positions(first_incident(5, 4)), "true_mask": 0, "incident_block": 5},
        "CHECK4_INCIDENT_D7": {"syndrome": mask_from_positions(first_incident(2, 4)), "true_mask": 0, "incident_block": 2},
    }
    out = {}
    for name, info in selected.items():
        row = {k: v for k, v in info.items() if k not in ("syndrome", "true_mask")}
        row["syndrome_weight"] = int(info["syndrome"].bit_count())
        row["true_logical_mask"] = int(info["true_mask"])
        row["cost_pairs"] = {}
        for cname, lc, cc in COST_PAIRS:
            row["cost_pairs"][cname] = classify_true(
                info["syndrome"], info["true_mask"], lc, cc, syndromes, logical_weights, popcount_table
            )
        out[name] = row
    return out


def all_check_only_boundaries(syndromes, logical_weights, popcount_table):
    result = {cname: {} for cname, _, _ in COST_PAIRS}
    for w in range(1, 5):
        synds = [mask_from_positions(c) for c in itertools.combinations(range(CHECKS), w)]
        assert len(synds) == math.comb(CHECKS, w)
        counters = {cname: Counter() for cname, _, _ in COST_PAIRS}
        for s in synds:
            residual_matrix = None
            for cname, lc, cc in COST_PAIRS:
                residual_w = popcount_table[np.bitwise_xor(syndromes, np.uint32(s))].astype(np.int32)
                costs = logical_weights.astype(np.int32) * lc + residual_w * cc
                mc = int(costs.min())
                minima = np.flatnonzero(costs == mc)
                zero_in = bool(np.any(minima == 0))
                if zero_in and len(minima) == 1:
                    counters[cname]["zero_unique"] += 1
                elif zero_in:
                    counters[cname]["zero_tied"] += 1
                else:
                    counters[cname]["all_minima_nonzero"] += 1
        n = len(synds)
        for cname, _, _ in COST_PAIRS:
            c = counters[cname]
            result[cname][str(w)] = {
                "patterns": n,
                "zero_unique": int(c["zero_unique"]),
                "zero_tied": int(c["zero_tied"]),
                "all_minima_nonzero": int(c["all_minima_nonzero"]),
                "zero_unique_fraction": float(c["zero_unique"] / n),
                "zero_tied_fraction": float(c["zero_tied"] / n),
                "all_minima_nonzero_fraction": float(c["all_minima_nonzero"] / n),
            }
    return result


def crossplane_lift():
    rows = []
    exact_all = True
    for b in range(BLOCKS):
        incident = [i for i, edge in enumerate(HYPER_EDGES) if b in edge]
        col = COLS[b]
        for p in range(1, PLANES + 1):
            logical_obs = [col if k < p else 0 for k in range(PLANES)]
            check_obs = [mask_from_positions(incident) if k < p else 0 for k in range(PLANES)]
            eq = logical_obs == check_obs
            exact_all = exact_all and eq
            rows.append({
                "block": b,
                "planes": p,
                "degree": len(incident),
                "logical_fault_bit_count": p,
                "integrity_fault_bit_count": len(incident) * p,
                "integrity_channel_event_count": len(incident),
                "exact_syndrome_equality": bool(eq),
            })
    return {"rows": rows, "all_constructed_exact": bool(exact_all)}


def run():
    mechanical = validate_design()
    rows, syndrome_to_masks, by_weight_hist = build_logical_map()
    logical_map = summarize_logical_map(rows, syndrome_to_masks, by_weight_hist)
    mimic = exact_mimic_metrics(rows)
    syndromes, logical_weights, popcount_table = make_arrays(rows)
    selected = selected_weighted_boundaries(rows, mimic, syndromes, logical_weights, popcount_table)
    check_only = all_check_only_boundaries(syndromes, logical_weights, popcount_table)
    cross = crossplane_lift()

    signals = {
        "snapshot_logical_only_full_rank": bool(logical_map["gf2_rank"] == BLOCKS),
        "nonzero_logical_kernel": bool(logical_map["nonzero_logical_kernel_masks"]),
        "single_region_exact_check_mimic_floor": min(x["check_mimic_weight"] for x in mimic["single_region"]),
        "two_region_exact_check_mimic_floor": int(mimic["two_region_minimum"]),
        "global_nonzero_exact_check_mimic_floor": int(mimic["global_minimum_positive"]),
        "crossplane_exact_mimic_exists": bool(any(x["exact_syndrome_equality"] for x in cross["rows"])),
        "crossplane_adds_information_under_arbitrary_correlation": bool(not any(x["exact_syndrome_equality"] for x in cross["rows"])),
    }

    return {
        "schema": "yggdrasil.dg1r-05j-hyper20-identifiability.v1",
        "mechanical_valid": True,
        "mechanical": mechanical,
        "logical_only_map": logical_map,
        "exact_check_mimic": mimic,
        "weighted_selected_boundaries": selected,
        "check_only_weight_1_to_4_boundaries": check_only,
        "crossplane_exact_collision_lift": cross,
        "signals": signals,
        "canonical_scientific_execution": False,
        "stab18_r1_touched": False,
    }


def encode_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    obj = run()
    raw = (encode_json(obj) + "\n").encode("utf-8")
    Path(args.out).write_bytes(raw)
    print(encode_json({
        "output": args.out,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "mechanical_valid": obj["mechanical_valid"],
        "signals": obj["signals"],
    }))


if __name__ == "__main__":
    main()
