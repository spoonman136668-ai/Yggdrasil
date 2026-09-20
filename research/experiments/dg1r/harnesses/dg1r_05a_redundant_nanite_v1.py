#!/usr/bin/env python3
import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np

WIDTH = 128
BLOCKS = 16
BLOCK_SIZE = 8
CODE_BITS = 7
LOGICAL_BITS = 64
POST_STEPS = 32
DAMAGE_AFTER_STEPS = 1024
WORLD_START = 20260926051000
WORLD_COUNT = 8
HORIZONS = (1, 4, 8, 16, 32)
MIX_RULES = np.asarray([90, 150, 110, 22, 30], dtype=np.uint16)
METHODS = (
    "UNCODED_H6_REPAIR_REFERENCE",
    "HAM74_DETECT_ONLY",
    "HAM74_REPAIR_ALWAYS",
    "HAM74_REPAIR_H6",
    "HAM74_REPAIR_ONCE",
)
PRIMARY = ("HAM74_REPAIR_ALWAYS", "HAM74_REPAIR_H6")
FAMILIES = ("SINGLE1_LOCAL", "DOUBLE2_LOCAL", "DISTRIBUTED3", "DISTRIBUTED5")
NANITE_SITES = np.arange(7, WIDTH, 8, dtype=np.int64)
WORKER_MASK = np.ones(WIDTH, dtype=bool)
WORKER_MASK[NANITE_SITES] = False
WORKER_SITES = np.flatnonzero(WORKER_MASK)
BLOCK_RANGES = tuple((b * 8, b * 8 + 7) for b in range(BLOCKS))
DATA_PHYS_OFFSETS = np.asarray([2, 4, 5, 6], dtype=np.int64)
MAPPED_BLOCKS = np.asarray([1, 2, 5, 7, 10, 11, 13, 14], dtype=np.int64)
BASE_SINGLE_BLOCKS = (0, 4, 8, 12)
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


def hamming_encode4(d):
    # d shape (..., 4), physical order [p1,p2,d1,p4,d2,d3,d4]
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


def hamming_decode7(code):
    return code[..., [2, 4, 5, 6]].copy()


def syndrome7(code):
    s1 = code[..., 0] ^ code[..., 2] ^ code[..., 4] ^ code[..., 6]
    s2 = code[..., 1] ^ code[..., 2] ^ code[..., 5] ^ code[..., 6]
    s4 = code[..., 3] ^ code[..., 4] ^ code[..., 5] ^ code[..., 6]
    return (s1 + 2 * s2 + 4 * s4).astype(np.uint8)


def physical_from_logical(logical, nanites=None):
    code = hamming_encode4(logical.reshape(BLOCKS, 4))
    out = np.zeros(WIDTH, dtype=np.uint8)
    for b in range(BLOCKS):
        start = b * 8
        out[start:start+7] = code[b]
        out[start+7] = 0 if nanites is None else nanites[b]
    return out


def logical_from_physical(state):
    data = np.empty((BLOCKS, 4), dtype=np.uint8)
    for b in range(BLOCKS):
        start = b * 8
        data[b] = hamming_decode7(state[start:start+7])
    return data.reshape(LOGICAL_BITS)


def mapped_logical_positions(rng):
    positions = []
    offsets = rng.integers(0, 4, size=len(MAPPED_BLOCKS), dtype=np.int64)
    for b, off in zip(MAPPED_BLOCKS, offsets):
        positions.append(int(b * 4 + off))
    return np.asarray(positions, dtype=np.int64)


def mapped_physical_positions(mapped_logical):
    out = []
    for lp in mapped_logical:
        b = int(lp // 4)
        off = int(lp % 4)
        out.append(int(b * 8 + DATA_PHYS_OFFSETS[off]))
    return np.asarray(out, dtype=np.int64)


def update_h6_nanites(state):
    for b in range(BLOCKS):
        start = b * 8
        nano = start + 7
        ones = int(np.sum(state[start:start+7]))
        if ones >= 6:
            state[nano] = 1
        elif ones <= 1:
            state[nano] = 0


def uncoded_worker_update(state, rules, telemetry=None):
    candidate = eca_step_mixed(state, rules)
    state[WORKER_SITES] = candidate[WORKER_SITES]
    for b in range(BLOCKS):
        start = b * 8
        nano = start + 7
        ones = int(np.sum(state[start:nano]))
        if ones >= 6:
            state[nano] = 1
        elif ones <= 1:
            state[nano] = 0
        workers = np.arange(start, nano, dtype=np.int64)
        disagreement = int(np.sum(state[workers] != state[nano]))
        if disagreement in (4, 5):
            center = start + 3
            if telemetry is not None:
                telemetry["repair_attempts"] += 1
            if state[center] != state[nano]:
                state[center] = state[nano]
                if telemetry is not None:
                    telemetry["repair_changes"] += 1


def uncoded_step(state, bit, mapped_phys, rules, telemetry=None):
    state[mapped_phys] = np.uint8(bit)
    uncoded_worker_update(state, rules, telemetry=telemetry)


def coded_repair_phase(state, method, used_once=None, reference_state=None, telemetry=None):
    for b in range(BLOCKS):
        start = b * 8
        code = state[start:start+7]
        syn = int(syndrome7(code))
        if syn == 0:
            continue
        if telemetry is not None:
            telemetry["syndrome_positive"] += 1
        do_repair = False
        if method == "HAM74_REPAIR_ALWAYS":
            do_repair = True
        elif method == "HAM74_REPAIR_H6":
            nbit = int(state[start+7])
            agrees = int(np.sum(code == nbit))
            do_repair = agrees >= 4
        elif method == "HAM74_REPAIR_ONCE":
            do_repair = not used_once[b]
        elif method == "HAM74_DETECT_ONLY":
            do_repair = False
        if not do_repair:
            continue
        idx = syn - 1
        if telemetry is not None:
            telemetry["corrections"] += 1
            if reference_state is not None:
                global_idx = start + idx
                if state[global_idx] == reference_state[global_idx]:
                    telemetry["false_corrections"] += 1
        state[start + idx] ^= 1
        if method == "HAM74_REPAIR_ONCE":
            used_once[b] = True


def coded_step(state, bit, mapped_logical, logical_rules, method, used_once=None, reference_state=None, telemetry=None):
    # repair persistent pre-input state first
    coded_repair_phase(
        state, method, used_once=used_once,
        reference_state=reference_state, telemetry=telemetry
    )
    logical = logical_from_physical(state)
    logical[mapped_logical] = np.uint8(bit)
    logical = eca_step_mixed(logical, logical_rules)
    nanites = state[NANITE_SITES].copy()
    state[:] = physical_from_logical(logical, nanites=nanites)
    update_h6_nanites(state)


def init_telemetry():
    return {
        "syndrome_positive": 0,
        "corrections": 0,
        "false_corrections": 0,
        "repair_attempts": 0,
        "repair_changes": 0,
    }


def initial_state(method, rng):
    if method == "UNCODED_H6_REPAIR_REFERENCE":
        return np.zeros(WIDTH, dtype=np.uint8)
    logical = np.zeros(LOGICAL_BITS, dtype=np.uint8)
    return physical_from_logical(logical, nanites=np.zeros(BLOCKS, dtype=np.uint8))


def evolve_prefix(method, u, mapped_logical, mapped_phys, logical_rules, physical_rules):
    state = initial_state(method, None)
    used_once = np.zeros(BLOCKS, dtype=bool)
    for t in range(DAMAGE_AFTER_STEPS):
        bit = int(u[t])
        if method == "UNCODED_H6_REPAIR_REFERENCE":
            uncoded_step(state, bit, mapped_phys, physical_rules)
        else:
            coded_step(
                state, bit, mapped_logical, logical_rules, method,
                used_once=used_once, reference_state=None, telemetry=None
            )
    return state


def lesion_scenarios():
    scenarios = []
    for b in BASE_SINGLE_BLOCKS:
        scenarios.append(("SINGLE1_LOCAL", (b,), (2,)))
        scenarios.append(("DOUBLE2_LOCAL", (b,), (2, 4)))
    scenarios.append(("DISTRIBUTED3", DIST3_BLOCKS, (2, 2, 2)))
    scenarios.append(("DISTRIBUTED5", DIST5_BLOCKS, (2, 2, 2, 2, 2)))
    return scenarios


def lesion_indices(blocks, offsets):
    return np.asarray([int(b * 8 + off) for b, off in zip(blocks, offsets)], dtype=np.int64)


def no_damage_control(method, pre, future_u, mapped_logical, mapped_phys, logical_rules, physical_rules):
    a = pre.copy()
    b = pre.copy()
    ua = np.zeros(BLOCKS, dtype=bool)
    ub = np.zeros(BLOCKS, dtype=bool)
    for bit in future_u:
        bit = int(bit)
        if method == "UNCODED_H6_REPAIR_REFERENCE":
            uncoded_step(a, bit, mapped_phys, physical_rules)
            uncoded_step(b, bit, mapped_phys, physical_rules)
        else:
            coded_step(a, bit, mapped_logical, logical_rules, method, used_once=ua)
            coded_step(b, bit, mapped_logical, logical_rules, method, used_once=ub)
        if np.any(a != b):
            return False
    return True


def one_scenario(method, pre, future_u, mapped_logical, mapped_phys, logical_rules, physical_rules, family, blocks, offsets):
    lesion = lesion_indices(blocks, offsets)
    assert not np.any(np.isin(lesion, mapped_phys))
    assert not np.any(np.isin(lesion, NANITE_SITES))

    ref = pre.copy()
    dmg = pre.copy()
    dmg[lesion] ^= 1

    used_ref = np.zeros(BLOCKS, dtype=bool)
    used_dmg = np.zeros(BLOCKS, dtype=bool)
    tel_ref = init_telemetry()
    tel_dmg = init_telemetry()

    lesion_mask = np.zeros(WIDTH, dtype=bool)
    lesion_mask[lesion] = True
    outside = ~lesion_mask
    curve = []
    flags = []
    hmetrics = {}

    for h, bit in enumerate(future_u, start=1):
        bit = int(bit)
        if method == "UNCODED_H6_REPAIR_REFERENCE":
            uncoded_step(ref, bit, mapped_phys, physical_rules, telemetry=tel_ref)
            uncoded_step(dmg, bit, mapped_phys, physical_rules, telemetry=tel_dmg)
        else:
            # Reference evolves normally. Damaged clone repair telemetry may compare
            # the corrected pre-input bit to reference's pre-input state.
            ref_pre = ref.copy()
            coded_step(
                ref, bit, mapped_logical, logical_rules, method,
                used_once=used_ref, reference_state=None, telemetry=tel_ref
            )
            coded_step(
                dmg, bit, mapped_logical, logical_rules, method,
                used_once=used_dmg, reference_state=ref_pre, telemetry=tel_dmg
            )

        diff = dmg != ref
        whole = float(np.mean(diff))
        damaged_site_recovery = float(1.0 - np.mean(diff[lesion_mask]))
        outside_div = float(np.mean(diff[outside]))
        spread = int(np.sum(diff[outside]))
        exact = bool(not np.any(diff))
        curve.append(whole)
        flags.append(exact)

        if h in HORIZONS:
            hmetrics[f"h{h}"] = {
                "whole_state_divergence": whole,
                "damaged_site_recovery": damaged_site_recovery,
                "outside_lesion_divergence": outside_div,
                "damage_spread_count": spread,
                "full_recovery": exact,
            }

    recovery_time = None
    for h in range(1, POST_STEPS + 1):
        if all(flags[h-1:]):
            recovery_time = h
            break

    return {
        "family": family,
        "lesion_indices": [int(v) for v in lesion],
        "horizons": hmetrics,
        "excess_divergence_area": float(np.sum(curve)),
        "full_recovery": bool(recovery_time is not None),
        "recovery_time": recovery_time,
        "syndrome_positive_delta": int(tel_dmg["syndrome_positive"] - tel_ref["syndrome_positive"]),
        "correction_delta": int(tel_dmg["corrections"] - tel_ref["corrections"]),
        "false_corrections": int(tel_dmg["false_corrections"]),
        "uncoded_repair_change_delta": int(tel_dmg["repair_changes"] - tel_ref["repair_changes"]),
    }


def one_world(seed):
    rng = np.random.default_rng(np.random.PCG64(seed))
    u = rng.integers(0, 2, size=DAMAGE_AFTER_STEPS + POST_STEPS, dtype=np.uint8)
    mapped_logical = mapped_logical_positions(rng)
    mapped_phys = mapped_physical_positions(mapped_logical)
    logical_rules = mixed_rules(rng, LOGICAL_BITS)
    physical_rules = mixed_rules(rng, WIDTH)
    future = u[DAMAGE_AFTER_STEPS:]

    methods = {}
    for method in METHODS:
        pre = evolve_prefix(method, u, mapped_logical, mapped_phys, logical_rules, physical_rules)
        control = no_damage_control(
            method, pre, future, mapped_logical, mapped_phys,
            logical_rules, physical_rules
        )
        scenarios = []
        for fam, blocks, offsets in lesion_scenarios():
            scenarios.append(
                one_scenario(
                    method, pre, future, mapped_logical, mapped_phys,
                    logical_rules, physical_rules,
                    fam, blocks, offsets
                )
            )
        methods[method] = {
            "no_damage_control": bool(control),
            "scenarios": scenarios,
        }

    return {
        "seed": int(seed),
        "mapped_logical": [int(v) for v in mapped_logical],
        "mapped_physical": [int(v) for v in mapped_phys],
        "methods": methods,
    }


def q(values, p):
    return float(np.quantile(np.asarray(values, dtype=np.float64), p))


def family_scenarios(rows, method, family):
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
        spread = [s["horizons"][k]["damage_spread_count"] for s in scenarios]
        exact = [s["horizons"][k]["full_recovery"] for s in scenarios]
        out["horizons"][k] = {
            "whole_state_divergence_median": q(whole, 0.5),
            "whole_state_divergence_p90": q(whole, 0.90),
            "damaged_site_recovery_median": q(rec, 0.5),
            "damaged_site_recovery_p10": q(rec, 0.10),
            "outside_lesion_divergence_median": q(outside, 0.5),
            "outside_lesion_divergence_p90": q(outside, 0.90),
            "spread_count_median": q(spread, 0.5),
            "full_recovery_rate_at_horizon": float(np.mean(exact)),
        }
    auc = [s["excess_divergence_area"] for s in scenarios]
    full = [s["full_recovery"] for s in scenarios]
    corr = [s["correction_delta"] for s in scenarios]
    false = [s["false_corrections"] for s in scenarios]
    syndrome = [s["syndrome_positive_delta"] for s in scenarios]
    total_corr = int(np.sum(corr))
    total_false = int(np.sum(false))
    out["excess_divergence_area_median"] = q(auc, 0.5)
    out["excess_divergence_area_p90"] = q(auc, 0.90)
    out["full_recovery_rate"] = float(np.mean(full))
    out["correction_delta_median"] = q(corr, 0.5)
    out["syndrome_positive_delta_median"] = q(syndrome, 0.5)
    out["false_correction_count"] = total_false
    out["correction_count"] = total_corr
    out["false_correction_fraction"] = (
        float(total_false / total_corr) if total_corr > 0 else 0.0
    )
    return out


def reduction(value, reference):
    if reference <= 1e-15:
        return 0.0
    return float((reference - value) / reference)


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
            fam: summarize_family(family_scenarios(rows, method, fam))
            for fam in FAMILIES
        }

    ref = out["methods"]["UNCODED_H6_REPAIR_REFERENCE"]
    detect = out["methods"]["HAM74_DETECT_ONLY"]

    single_signal_methods = []
    distributed_signal_methods = []
    redundancy_value_methods = []
    overcorrection_methods = []

    for method in PRIMARY:
        ms = out["methods"][method]

        single_auc_red = reduction(
            ms["SINGLE1_LOCAL"]["excess_divergence_area_median"],
            ref["SINGLE1_LOCAL"]["excess_divergence_area_median"],
        )
        single_signal = (
            ms["SINGLE1_LOCAL"]["horizons"]["h4"]["damaged_site_recovery_median"] >= 0.95
            and ms["SINGLE1_LOCAL"]["horizons"]["h4"]["whole_state_divergence_median"] <= 0.02
            and ms["SINGLE1_LOCAL"]["full_recovery_rate"] >= 0.50
            and single_auc_red >= 0.50
        )
        if single_signal:
            single_signal_methods.append(method)

        dist_ok = False
        for fam in ("DISTRIBUTED3", "DISTRIBUTED5"):
            auc_red = reduction(
                ms[fam]["excess_divergence_area_median"],
                ref[fam]["excess_divergence_area_median"],
            )
            if (
                ms[fam]["horizons"]["h8"]["damaged_site_recovery_median"] >= 0.90
                and ms[fam]["horizons"]["h8"]["outside_lesion_divergence_median"] <= 0.02
                and auc_red >= 0.40
            ):
                dist_ok = True
        if dist_ok:
            distributed_signal_methods.append(method)

        # actual reconstruction must beat detect-only on at least SINGLE1 AUC and h4 recovery
        if (
            ms["SINGLE1_LOCAL"]["excess_divergence_area_median"]
            < detect["SINGLE1_LOCAL"]["excess_divergence_area_median"]
            and ms["SINGLE1_LOCAL"]["horizons"]["h4"]["damaged_site_recovery_median"]
            > detect["SINGLE1_LOCAL"]["horizons"]["h4"]["damaged_site_recovery_median"]
        ):
            redundancy_value_methods.append(method)

        if ms["DOUBLE2_LOCAL"]["false_correction_fraction"] > 0.10:
            overcorrection_methods.append(method)

    out["single_error_reconstruction_signal"] = bool(single_signal_methods)
    out["single_error_signal_methods"] = single_signal_methods
    out["distributed_reconstruction_signal"] = bool(distributed_signal_methods)
    out["distributed_signal_methods"] = distributed_signal_methods
    out["redundancy_value_signal"] = bool(redundancy_value_methods)
    out["redundancy_value_methods"] = redundancy_value_methods
    out["overcorrection_failure_methods"] = overcorrection_methods
    return out


def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def run():
    rows = [one_world(WORLD_START + i) for i in range(WORLD_COUNT)]
    obj = {
        "schema": "yggdrasil.dg1r-05a-redundant-nanite-reconstruction.v1",
        "rows": rows,
        "summary": summarize(rows),
        "worlds": len(rows),
        "seed_start": WORLD_START,
        "seed_end": WORLD_START + WORLD_COUNT - 1,
    }
    return obj


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