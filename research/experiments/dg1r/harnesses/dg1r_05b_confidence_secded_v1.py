#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

WIDTH = 128
BLOCKS = 16
LOGICAL_BITS = 64
POST_STEPS = 32
DAMAGE_AFTER_STEPS = 1024
WORLD_START = 20260926052000
WORLD_COUNT = 8
HORIZONS = (1, 4, 8, 16, 32)
MIX_RULES = np.asarray([90, 150, 110, 22, 30], dtype=np.uint16)
METHODS = (
    "HAM74_REPAIR_ALWAYS_REFERENCE",
    "SECDED84_DETECT_ONLY",
    "SECDED84_REPAIR_ABSTAIN",
    "SECDED84_BLIND_SYNDROME",
)
FAMILIES = (
    "SINGLE1_LOCAL",
    "PARITY1_LOCAL",
    "DOUBLE2_LOCAL",
    "TRIPLE3_LOCAL",
    "DISTRIBUTED3",
    "DISTRIBUTED5",
)
PRIMARY = "SECDED84_REPAIR_ABSTAIN"
DATA_OFFSETS = np.asarray([2, 4, 5, 6], dtype=np.int64)
MAPPED_BLOCKS = np.asarray([1, 2, 5, 7, 10, 11, 13, 14], dtype=np.int64)
BASE_BLOCKS = (0, 4, 8, 12)
DIST3_BLOCKS = (0, 4, 8)
DIST5_BLOCKS = (0, 3, 6, 9, 12)


def eca_step_mixed(state, rules):
    left = np.roll(state, 1)
    right = np.roll(state, -1)
    idx = (left << 2) | (state << 1) | right
    return ((rules >> idx) & 1).astype(np.uint8)


def mixed_rules(rng, width):
    reps = width // len(MIX_RULES)
    rem = width % len(MIX_RULES)
    arr = np.concatenate((np.tile(MIX_RULES, reps), MIX_RULES[:rem])).astype(np.uint16)
    rng.shuffle(arr)
    return arr


def ham74_encode4(d):
    out = np.empty(d.shape[:-1] + (7,), dtype=np.uint8)
    d1, d2, d3, d4 = [d[..., i] for i in range(4)]
    out[..., 0] = d1 ^ d2 ^ d4
    out[..., 1] = d1 ^ d3 ^ d4
    out[..., 2] = d1
    out[..., 3] = d2 ^ d3 ^ d4
    out[..., 4] = d2
    out[..., 5] = d3
    out[..., 6] = d4
    return out


def ham74_decode7(code):
    return code[..., [2, 4, 5, 6]].copy()


def syndrome7(code):
    s1 = code[..., 0] ^ code[..., 2] ^ code[..., 4] ^ code[..., 6]
    s2 = code[..., 1] ^ code[..., 2] ^ code[..., 5] ^ code[..., 6]
    s4 = code[..., 3] ^ code[..., 4] ^ code[..., 5] ^ code[..., 6]
    return (s1 + 2 * s2 + 4 * s4).astype(np.uint8)


def secded_encode4(d):
    c7 = ham74_encode4(d)
    q = np.bitwise_xor.reduce(c7, axis=-1).astype(np.uint8)
    return np.concatenate((c7, q[..., None]), axis=-1)


def encode_physical(logical, method):
    d = logical.reshape(BLOCKS, 4)
    if method == "HAM74_REPAIR_ALWAYS_REFERENCE":
        c7 = ham74_encode4(d)
        c8 = np.concatenate((c7, np.zeros((BLOCKS, 1), dtype=np.uint8)), axis=1)
    else:
        c8 = secded_encode4(d)
    return c8.reshape(WIDTH).copy()


def decode_physical(state):
    blocks = state.reshape(BLOCKS, 8)
    return ham74_decode7(blocks[:, :7]).reshape(LOGICAL_BITS)


def mapped_logical_positions(rng):
    offsets = rng.integers(0, 4, size=len(MAPPED_BLOCKS), dtype=np.int64)
    return np.asarray(
        [int(b * 4 + off) for b, off in zip(MAPPED_BLOCKS, offsets)],
        dtype=np.int64,
    )


def mapped_physical_positions(mapped_logical):
    return np.asarray(
        [
            int((lp // 4) * 8 + DATA_OFFSETS[int(lp % 4)])
            for lp in mapped_logical
        ],
        dtype=np.int64,
    )


def classify_secded(block):
    syn = int(syndrome7(block[:7]))
    overall = int(np.bitwise_xor.reduce(block))
    if syn == 0 and overall == 0:
        return "no_error", None
    if syn != 0 and overall == 1:
        return "single_data", syn - 1
    if syn == 0 and overall == 1:
        return "single_parity", 7
    return "ambiguous_double", None


def init_tel():
    return {
        "no_error": 0,
        "single_data": 0,
        "single_parity": 0,
        "ambiguous_double": 0,
        "corrections": 0,
        "abstentions": 0,
        "false_corrections": 0,
        "missed_correctable": 0,
    }


def hamming_reference_repair(state, reference_state=None, tel=None):
    blocks = state.reshape(BLOCKS, 8)
    refb = None if reference_state is None else reference_state.reshape(BLOCKS, 8)
    for b in range(BLOCKS):
        syn = int(syndrome7(blocks[b, :7]))
        if syn == 0:
            continue
        idx = syn - 1
        if tel is not None:
            tel["corrections"] += 1
            if refb is not None and blocks[b, idx] == refb[b, idx]:
                tel["false_corrections"] += 1
        blocks[b, idx] ^= 1


def secded_policy(state, method, reference_state=None, tel=None):
    blocks = state.reshape(BLOCKS, 8)
    refb = None if reference_state is None else reference_state.reshape(BLOCKS, 8)
    for b in range(BLOCKS):
        label, idx = classify_secded(blocks[b])
        if tel is not None:
            tel[label] += 1

        # Evaluation-only correctability telemetry.
        correctable = False
        if refb is not None:
            diff = np.flatnonzero(blocks[b] != refb[b])
            correctable = len(diff) == 1

        do_repair = False
        target = None

        if method == "SECDED84_DETECT_ONLY":
            if label != "no_error":
                if tel is not None:
                    tel["abstentions"] += 1
        elif method == "SECDED84_REPAIR_ABSTAIN":
            if label in ("single_data", "single_parity"):
                do_repair = True
                target = idx
            elif label == "ambiguous_double":
                if tel is not None:
                    tel["abstentions"] += 1
        elif method == "SECDED84_BLIND_SYNDROME":
            syn = int(syndrome7(blocks[b, :7]))
            overall = int(np.bitwise_xor.reduce(blocks[b]))
            if syn != 0:
                do_repair = True
                target = syn - 1
            elif overall == 1:
                do_repair = True
                target = 7

        if do_repair:
            if tel is not None:
                tel["corrections"] += 1
                if refb is not None and blocks[b, target] == refb[b, target]:
                    tel["false_corrections"] += 1
            blocks[b, target] ^= 1
        elif correctable and label != "no_error":
            if tel is not None:
                tel["missed_correctable"] += 1


def step(state, bit, mapped_logical, rules, method, reference_state=None, tel=None):
    if method == "HAM74_REPAIR_ALWAYS_REFERENCE":
        hamming_reference_repair(state, reference_state=reference_state, tel=tel)
    else:
        secded_policy(state, method, reference_state=reference_state, tel=tel)
    logical = decode_physical(state)
    logical[mapped_logical] = np.uint8(bit)
    logical = eca_step_mixed(logical, rules)
    state[:] = encode_physical(logical, method)


def evolve_prefix(method, u, mapped_logical, rules):
    state = encode_physical(np.zeros(LOGICAL_BITS, dtype=np.uint8), method)
    for t in range(DAMAGE_AFTER_STEPS):
        step(state, int(u[t]), mapped_logical, rules, method)
    return state


def scenarios():
    out = []
    for b in BASE_BLOCKS:
        out.append(("SINGLE1_LOCAL", (b,), (2,)))
        out.append(("PARITY1_LOCAL", (b,), (7,)))
        out.append(("DOUBLE2_LOCAL", (b, b), (2, 4)))
        out.append(("TRIPLE3_LOCAL", (b, b, b), (2, 4, 5)))
    out.append(("DISTRIBUTED3", DIST3_BLOCKS, (2, 2, 2)))
    out.append(("DISTRIBUTED5", DIST5_BLOCKS, (2, 2, 2, 2, 2)))
    return out


def lesion_indices(blocks, offsets):
    return np.asarray([int(b * 8 + off) for b, off in zip(blocks, offsets)], dtype=np.int64)


def no_damage_control(method, pre, future, mapped_logical, rules):
    a = pre.copy()
    b = pre.copy()
    for bit in future:
        step(a, int(bit), mapped_logical, rules, method)
        step(b, int(bit), mapped_logical, rules, method)
        if np.any(a != b):
            return False
    return True


def one_scenario(method, pre, future, mapped_logical, mapped_phys, rules, family, blocks, offsets):
    lesion = lesion_indices(blocks, offsets)
    assert len(lesion) == len(offsets)
    assert not np.any(np.isin(lesion, mapped_phys))

    ref = pre.copy()
    dmg = pre.copy()
    dmg[lesion] ^= 1

    tel_ref = init_tel()
    tel_dmg = init_tel()

    lesion_mask = np.zeros(WIDTH, dtype=bool)
    lesion_mask[lesion] = True
    outside = ~lesion_mask
    curve = []
    flags = []
    hmetrics = {}

    for h, bit in enumerate(future, start=1):
        ref_pre = ref.copy()
        step(ref, int(bit), mapped_logical, rules, method, reference_state=None, tel=tel_ref)
        step(dmg, int(bit), mapped_logical, rules, method, reference_state=ref_pre, tel=tel_dmg)

        diff = dmg != ref
        whole = float(np.mean(diff))
        recovery = float(1.0 - np.mean(diff[lesion_mask]))
        outside_div = float(np.mean(diff[outside]))
        spread = int(np.sum(diff[outside]))
        exact = bool(not np.any(diff))
        curve.append(whole)
        flags.append(exact)

        if h in HORIZONS:
            hmetrics[f"h{h}"] = {
                "whole_state_divergence": whole,
                "damaged_site_recovery": recovery,
                "outside_lesion_divergence": outside_div,
                "damage_spread_count": spread,
                "full_recovery": exact,
            }

    recovery_time = None
    for h in range(1, POST_STEPS + 1):
        if all(flags[h-1:]):
            recovery_time = h
            break

    delta = {k: int(tel_dmg[k] - tel_ref[k]) for k in tel_dmg}

    return {
        "family": family,
        "lesion_indices": [int(v) for v in lesion],
        "horizons": hmetrics,
        "excess_divergence_area": float(np.sum(curve)),
        "full_recovery": bool(recovery_time is not None),
        "recovery_time": recovery_time,
        "telemetry_delta": delta,
    }


def one_world(seed):
    rng = np.random.default_rng(np.random.PCG64(seed))
    u = rng.integers(0, 2, size=DAMAGE_AFTER_STEPS + POST_STEPS, dtype=np.uint8)
    mapped_logical = mapped_logical_positions(rng)
    mapped_phys = mapped_physical_positions(mapped_logical)
    rules = mixed_rules(rng, LOGICAL_BITS)
    future = u[DAMAGE_AFTER_STEPS:]

    methods = {}
    for method in METHODS:
        pre = evolve_prefix(method, u, mapped_logical, rules)
        control = no_damage_control(method, pre, future, mapped_logical, rules)
        sc = []
        for family, blocks, offsets in scenarios():
            sc.append(
                one_scenario(
                    method, pre, future, mapped_logical, mapped_phys,
                    rules, family, blocks, offsets
                )
            )
        methods[method] = {
            "no_damage_control": bool(control),
            "scenarios": sc,
        }

    return {
        "seed": int(seed),
        "mapped_logical": [int(v) for v in mapped_logical],
        "mapped_physical": [int(v) for v in mapped_phys],
        "methods": methods,
    }


def q(values, p):
    return float(np.quantile(np.asarray(values, dtype=np.float64), p))


def family_rows(rows, method, family):
    return [
        sc
        for row in rows
        for sc in row["methods"][method]["scenarios"]
        if sc["family"] == family
    ]


def summarize_family(scenarios):
    out = {"scenario_count": len(scenarios), "horizons": {}}
    for h in HORIZONS:
        k = f"h{h}"
        whole = [s["horizons"][k]["whole_state_divergence"] for s in scenarios]
        rec = [s["horizons"][k]["damaged_site_recovery"] for s in scenarios]
        outside = [s["horizons"][k]["outside_lesion_divergence"] for s in scenarios]
        exact = [s["horizons"][k]["full_recovery"] for s in scenarios]
        out["horizons"][k] = {
            "whole_state_divergence_median": q(whole, 0.5),
            "whole_state_divergence_p90": q(whole, 0.90),
            "damaged_site_recovery_median": q(rec, 0.5),
            "damaged_site_recovery_p10": q(rec, 0.10),
            "outside_lesion_divergence_median": q(outside, 0.5),
            "outside_lesion_divergence_p90": q(outside, 0.90),
            "full_recovery_rate_at_horizon": float(np.mean(exact)),
        }

    auc = [s["excess_divergence_area"] for s in scenarios]
    full = [s["full_recovery"] for s in scenarios]
    out["excess_divergence_area_median"] = q(auc, 0.5)
    out["excess_divergence_area_p90"] = q(auc, 0.90)
    out["full_recovery_rate"] = float(np.mean(full))

    tel_keys = list(scenarios[0]["telemetry_delta"].keys())
    out["telemetry"] = {}
    for key in tel_keys:
        vals = [s["telemetry_delta"][key] for s in scenarios]
        out["telemetry"][key] = {
            "median": q(vals, 0.5),
            "sum": int(np.sum(vals)),
        }

    corrections = out["telemetry"]["corrections"]["sum"]
    false = out["telemetry"]["false_corrections"]["sum"]
    ambiguous = out["telemetry"]["ambiguous_double"]["sum"]
    out["false_correction_fraction"] = float(false / corrections) if corrections > 0 else 0.0
    out["ambiguous_classification_count"] = ambiguous
    return out


def summarize(rows):
    mechanical_valid = all(
        row["methods"][m]["no_damage_control"]
        for row in rows
        for m in METHODS
    )

    out = {
        "worlds": len(rows),
        "mechanical_valid": bool(mechanical_valid),
        "methods": {},
    }

    for method in METHODS:
        out["methods"][method] = {
            fam: summarize_family(family_rows(rows, method, fam))
            for fam in FAMILIES
        }

    p = out["methods"][PRIMARY]

    safe_single = (
        p["SINGLE1_LOCAL"]["horizons"]["h1"]["damaged_site_recovery_median"] == 1.0
        and p["SINGLE1_LOCAL"]["horizons"]["h1"]["whole_state_divergence_median"] == 0.0
        and p["SINGLE1_LOCAL"]["full_recovery_rate"] == 1.0
        and p["SINGLE1_LOCAL"]["telemetry"]["false_corrections"]["sum"] == 0
    )

    parity_repair = (
        p["PARITY1_LOCAL"]["full_recovery_rate"] == 1.0
        and p["PARITY1_LOCAL"]["telemetry"]["false_corrections"]["sum"] == 0
    )

    double_scenarios = len(family_rows(rows, PRIMARY, "DOUBLE2_LOCAL"))
    double_abstention = (
        p["DOUBLE2_LOCAL"]["telemetry"]["ambiguous_double"]["sum"] == double_scenarios
        and p["DOUBLE2_LOCAL"]["telemetry"]["corrections"]["sum"] == 0
        and p["DOUBLE2_LOCAL"]["telemetry"]["abstentions"]["sum"] == double_scenarios
        and p["DOUBLE2_LOCAL"]["telemetry"]["false_corrections"]["sum"] == 0
    )

    distributed_safe = all(
        p[fam]["full_recovery_rate"] == 1.0
        and p[fam]["excess_divergence_area_median"] == 0.0
        and p[fam]["telemetry"]["false_corrections"]["sum"] == 0
        for fam in ("DISTRIBUTED3", "DISTRIBUTED5")
    )

    blind = out["methods"]["SECDED84_BLIND_SYNDROME"]["DOUBLE2_LOCAL"]
    ham = out["methods"]["HAM74_REPAIR_ALWAYS_REFERENCE"]["DOUBLE2_LOCAL"]
    blind_miscorrection = (
        blind["telemetry"]["false_corrections"]["sum"] > 0
        and ham["telemetry"]["false_corrections"]["sum"] > 0
    )

    out["safe_single_repair"] = bool(safe_single)
    out["parity_self_repair"] = bool(parity_repair)
    out["double_abstention"] = bool(double_abstention)
    out["distributed_safe_repair"] = bool(distributed_safe)
    out["blind_double_miscorrection_signal"] = bool(blind_miscorrection)
    out["confidence_aware_repair_signal"] = bool(
        mechanical_valid
        and safe_single
        and parity_repair
        and double_abstention
        and distributed_safe
        and blind_miscorrection
    )
    return out


def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def run():
    rows = [one_world(WORLD_START + i) for i in range(WORLD_COUNT)]
    return {
        "schema": "yggdrasil.dg1r-05b-confidence-aware-secded.v1",
        "rows": rows,
        "summary": summarize(rows),
        "worlds": len(rows),
        "seed_start": WORLD_START,
        "seed_end": WORLD_START + WORLD_COUNT - 1,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    obj = run()
    raw = (encode(obj) + "\n").encode("utf-8")
    Path(args.out).write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    print(encode({
        "output": args.out,
        "sha256": digest,
        "summary": obj["summary"],
        "worlds": obj["worlds"],
    }))


if __name__ == "__main__":
    main()