#!/usr/bin/env python3
import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np

PHYSICAL_WIDTH = 128
LOGICAL_WIDTH = 64
WORLD_START = 20260926060000
WORLD_COUNT = 8
DAMAGE_AFTER_STEPS = 1024
POST_STEPS = 32
HORIZONS = (1, 4, 8, 16, 32)
MIX_RULES = np.asarray([90, 150, 110, 22, 30], dtype=np.uint16)
METHODS = ("UNCODED64_PAD64", "SECDED64_LOCAL")
DAMAGE_FAMILIES = ("SPREAD4", "SPREAD8", "LOCAL2", "LOCAL3")
DATA_PHYS_OFFSETS = np.asarray([2, 4, 5, 6], dtype=np.int64)


def eca_step_mixed(state, rules):
    left = np.roll(state, 1)
    right = np.roll(state, -1)
    idx = (left << 2) | (state << 1) | right
    return ((rules >> idx) & 1).astype(np.uint8)


def mixed_rule_assignment(rng):
    reps = LOGICAL_WIDTH // len(MIX_RULES)
    rem = LOGICAL_WIDTH % len(MIX_RULES)
    arr = np.concatenate((np.tile(MIX_RULES, reps), MIX_RULES[:rem])).astype(np.uint16)
    rng.shuffle(arr)
    return arr


def mapped_logical_positions(rng):
    return np.asarray(
        [j * 8 + int(rng.integers(0, 8)) for j in range(8)],
        dtype=np.int64,
    )


def encode_block(data):
    d0, d1, d2, d3 = [int(v) for v in data]
    p1 = d0 ^ d1 ^ d3
    p2 = d0 ^ d2 ^ d3
    p4 = d1 ^ d2 ^ d3
    p8 = p1 ^ p2 ^ d0 ^ p4 ^ d1 ^ d2 ^ d3
    return np.asarray([p1, p2, d0, p4, d1, d2, d3, p8], dtype=np.uint8)


def encode_logical(logical):
    physical = np.empty(PHYSICAL_WIDTH, dtype=np.uint8)
    for b in range(16):
        physical[b * 8:(b + 1) * 8] = encode_block(logical[b * 4:(b + 1) * 4])
    return physical


def extract_logical(method, physical):
    if method == "UNCODED64_PAD64":
        return physical[:LOGICAL_WIDTH].copy()
    out = np.empty(LOGICAL_WIDTH, dtype=np.uint8)
    for b in range(16):
        block = physical[b * 8:(b + 1) * 8]
        out[b * 4:(b + 1) * 4] = block[DATA_PHYS_OFFSETS]
    return out


def init_physical(method):
    if method == "UNCODED64_PAD64":
        return np.zeros(PHYSICAL_WIDTH, dtype=np.uint8)
    return encode_logical(np.zeros(LOGICAL_WIDTH, dtype=np.uint8))


def empty_decoder_stats():
    return {
        "no_error_blocks": 0,
        "single_corrections": 0,
        "overall_parity_corrections": 0,
        "detected_double_errors": 0,
        "correction_actions": 0,
        "actions_toward_reference": 0,
        "actions_away_from_reference": 0,
        "actions_neutral_to_reference": 0,
    }


def add_stats(dst, src):
    for k in dst:
        dst[k] += int(src[k])


def decode_secded_in_place(physical, reference_physical=None):
    stats = empty_decoder_stats()
    for b in range(16):
        start = b * 8
        block = physical[start:start + 8]
        s1 = int(block[0] ^ block[2] ^ block[4] ^ block[6])
        s2 = int(block[1] ^ block[2] ^ block[5] ^ block[6])
        s4 = int(block[3] ^ block[4] ^ block[5] ^ block[6])
        syndrome = s1 + 2 * s2 + 4 * s4
        overall = int(np.bitwise_xor.reduce(block))

        flip_local = None
        if syndrome == 0 and overall == 0:
            stats["no_error_blocks"] += 1
        elif syndrome != 0 and overall == 1:
            flip_local = syndrome - 1
            stats["single_corrections"] += 1
        elif syndrome == 0 and overall == 1:
            flip_local = 7
            stats["overall_parity_corrections"] += 1
        else:
            stats["detected_double_errors"] += 1

        if flip_local is not None:
            before = None
            if reference_physical is not None:
                before = int(np.sum(
                    extract_logical("SECDED64_LOCAL", physical)
                    != extract_logical("SECDED64_LOCAL", reference_physical)
                ))
            physical[start + flip_local] ^= 1
            stats["correction_actions"] += 1
            if reference_physical is not None:
                after = int(np.sum(
                    extract_logical("SECDED64_LOCAL", physical)
                    != extract_logical("SECDED64_LOCAL", reference_physical)
                ))
                if after < before:
                    stats["actions_toward_reference"] += 1
                elif after > before:
                    stats["actions_away_from_reference"] += 1
                else:
                    stats["actions_neutral_to_reference"] += 1
    return stats


def pre_input_decode(method, physical, reference_physical=None):
    if method == "SECDED64_LOCAL":
        return decode_secded_in_place(physical, reference_physical)
    return empty_decoder_stats()


def transition_after_decode(method, physical, bit, mapped, rules):
    logical = extract_logical(method, physical)
    logical[mapped] = np.uint8(bit)
    logical = eca_step_mixed(logical, rules)
    if method == "UNCODED64_PAD64":
        physical[:LOGICAL_WIDTH] = logical
        physical[LOGICAL_WIDTH:] = 0
    else:
        physical[:] = encode_logical(logical)


def evolve_one_external(method, physical, bit, mapped, rules, decode=True):
    stats = empty_decoder_stats()
    if decode:
        stats = pre_input_decode(method, physical)
    transition_after_decode(method, physical, bit, mapped, rules)
    return stats


def evolve_prefix(method, u, mapped, rules):
    state = init_physical(method)
    for t in range(DAMAGE_AFTER_STEPS):
        evolve_one_external(method, state, int(u[t]), mapped, rules, decode=True)
    return state


def unmapped_sibling_logical_block(mapped, compartment):
    comp_start = compartment * 8
    p = int(mapped[compartment])
    if p < comp_start + 4:
        return comp_start + 4
    return comp_start


def damage_logical_positions(mapped, family):
    if family == "SPREAD4":
        comps = (0, 2, 4, 6)
        return np.asarray(
            [unmapped_sibling_logical_block(mapped, c) + 1 for c in comps],
            dtype=np.int64,
        )
    if family == "SPREAD8":
        return np.asarray(
            [unmapped_sibling_logical_block(mapped, c) + 1 for c in range(8)],
            dtype=np.int64,
        )
    base = unmapped_sibling_logical_block(mapped, 0)
    if family == "LOCAL2":
        return np.asarray([base + 1, base + 2], dtype=np.int64)
    if family == "LOCAL3":
        return np.asarray([base + 0, base + 1, base + 2], dtype=np.int64)
    raise ValueError(family)


def logical_to_physical_data_index(logical_idx):
    block = logical_idx // 4
    local_data = logical_idx % 4
    return int(block * 8 + DATA_PHYS_OFFSETS[local_data])


def apply_damage(method, physical, logical_positions):
    if method == "UNCODED64_PAD64":
        physical[logical_positions] ^= 1
    else:
        idx = np.asarray(
            [logical_to_physical_data_index(int(v)) for v in logical_positions],
            dtype=np.int64,
        )
        physical[idx] ^= 1


def divergence(method, a, b):
    la = extract_logical(method, a)
    lb = extract_logical(method, b)
    return {
        "logical": float(np.mean(la != lb)),
        "physical": float(np.mean(a != b)),
        "logical_count": int(np.sum(la != lb)),
        "physical_count": int(np.sum(a != b)),
        "full_logical": bool(np.array_equal(la, lb)),
        "full_physical": bool(np.array_equal(a, b)),
    }


def no_damage_control(method, pre, u, mapped, rules):
    a = pre.copy()
    b = pre.copy()
    max_logical = 0.0
    max_physical = 0.0
    for h in range(1, POST_STEPS + 1):
        bit = int(u[DAMAGE_AFTER_STEPS + h - 1])
        evolve_one_external(method, a, bit, mapped, rules, decode=True)
        evolve_one_external(method, b, bit, mapped, rules, decode=True)
        d = divergence(method, a, b)
        max_logical = max(max_logical, d["logical"])
        max_physical = max(max_physical, d["physical"])
    return {
        "max_logical_divergence": float(max_logical),
        "max_physical_divergence": float(max_physical),
    }


def one_scenario(method, pre, u, mapped, rules, family):
    logical_damage = damage_logical_positions(mapped, family)
    assert not np.any(np.isin(logical_damage, mapped))

    ref = pre.copy()
    dmg = pre.copy()
    apply_damage(method, dmg, logical_damage)

    decoder_totals = empty_decoder_stats()

    ref_stats = pre_input_decode(method, ref)
    dmg_stats = pre_input_decode(method, dmg, reference_physical=ref)
    add_stats(decoder_totals, dmg_stats)

    post_decode = divergence(method, dmg, ref)

    logical_curve = []
    physical_curve = []
    full_logical_flags = []
    full_physical_flags = []
    horizon_rows = {}

    for h in range(1, POST_STEPS + 1):
        bit = int(u[DAMAGE_AFTER_STEPS + h - 1])
        transition_after_decode(method, ref, bit, mapped, rules)
        transition_after_decode(method, dmg, bit, mapped, rules)

        d = divergence(method, dmg, ref)
        logical_curve.append(d["logical"])
        physical_curve.append(d["physical"])
        full_logical_flags.append(d["full_logical"])
        full_physical_flags.append(d["full_physical"])

        if h in HORIZONS:
            horizon_rows[f"h{h}"] = d

        if h < POST_STEPS:
            ref_stats = pre_input_decode(method, ref)
            dmg_stats = pre_input_decode(method, dmg, reference_physical=ref)
            add_stats(decoder_totals, dmg_stats)

    recovery_time = None
    for h in range(1, POST_STEPS + 1):
        if all(full_logical_flags[h - 1:]):
            recovery_time = h
            break

    return {
        "damage_family": family,
        "damaged_logical_positions": [int(v) for v in logical_damage],
        "initial_logical_damage_count": int(len(logical_damage)),
        "post_decode": post_decode,
        "horizons": horizon_rows,
        "logical_divergence_area": float(np.sum(logical_curve)),
        "physical_divergence_area": float(np.sum(physical_curve)),
        "full_logical_recovery_h1": bool(full_logical_flags[0]),
        "full_logical_recovery_h32": bool(full_logical_flags[-1]),
        "full_physical_recovery_h1": bool(full_physical_flags[0]),
        "full_physical_recovery_h32": bool(full_physical_flags[-1]),
        "sustained_logical_recovery": bool(recovery_time is not None),
        "logical_recovery_time": recovery_time,
        "decoder_telemetry": decoder_totals,
    }


def one_world(seed):
    rng = np.random.default_rng(np.random.PCG64(seed))
    u = rng.integers(
        0, 2, size=DAMAGE_AFTER_STEPS + POST_STEPS,
        dtype=np.uint8,
    )
    mapped = mapped_logical_positions(rng)
    rules = mixed_rule_assignment(rng)

    methods = {}
    for method in METHODS:
        pre = evolve_prefix(method, u, mapped, rules)
        control = no_damage_control(method, pre, u, mapped, rules)
        scenarios = [
            one_scenario(method, pre, u, mapped, rules, family)
            for family in DAMAGE_FAMILIES
        ]
        methods[method] = {
            "no_damage_control": control,
            "scenarios": scenarios,
        }

    return {
        "seed": int(seed),
        "mapped_logical_positions": [int(v) for v in mapped],
        "methods": methods,
    }


def q(values, p):
    return float(np.quantile(np.asarray(values, dtype=np.float64), p))


def collect(rows, method, family):
    out = []
    for row in rows:
        for sc in row["methods"][method]["scenarios"]:
            if sc["damage_family"] == family:
                out.append(sc)
    return out


def summarize_scenarios(scenarios):
    post_l = [sc["post_decode"]["logical"] for sc in scenarios]
    post_p = [sc["post_decode"]["physical"] for sc in scenarios]
    out = {
        "scenario_count": len(scenarios),
        "post_decode_logical_divergence": {
            "median": q(post_l, 0.5),
            "p10": q(post_l, 0.10),
            "p90": q(post_l, 0.90),
        },
        "post_decode_physical_divergence": {
            "median": q(post_p, 0.5),
            "p10": q(post_p, 0.10),
            "p90": q(post_p, 0.90),
        },
        "horizons": {},
    }
    for h in HORIZONS:
        key = f"h{h}"
        lv = [sc["horizons"][key]["logical"] for sc in scenarios]
        pv = [sc["horizons"][key]["physical"] for sc in scenarios]
        fl = [sc["horizons"][key]["full_logical"] for sc in scenarios]
        fp = [sc["horizons"][key]["full_physical"] for sc in scenarios]
        out["horizons"][key] = {
            "logical_divergence_median": q(lv, 0.5),
            "logical_divergence_p90": q(lv, 0.90),
            "physical_divergence_median": q(pv, 0.5),
            "physical_divergence_p90": q(pv, 0.90),
            "full_logical_recovery_rate": float(np.mean(fl)),
            "full_physical_recovery_rate": float(np.mean(fp)),
        }

    larea = [sc["logical_divergence_area"] for sc in scenarios]
    parea = [sc["physical_divergence_area"] for sc in scenarios]
    out["logical_divergence_area"] = {
        "median": q(larea, 0.5),
        "p90": q(larea, 0.90),
    }
    out["physical_divergence_area"] = {
        "median": q(parea, 0.5),
        "p90": q(parea, 0.90),
    }
    recovered = [
        sc["logical_recovery_time"]
        for sc in scenarios
        if sc["logical_recovery_time"] is not None
    ]
    out["sustained_logical_recovery_rate"] = float(
        np.mean([sc["sustained_logical_recovery"] for sc in scenarios])
    )
    out["recovered_scenario_count"] = len(recovered)
    out["logical_recovery_time_median_recovered"] = (
        q(recovered, 0.5) if recovered else None
    )

    keys = tuple(empty_decoder_stats().keys())
    out["decoder_telemetry"] = {}
    for key in keys:
        vals = [sc["decoder_telemetry"][key] for sc in scenarios]
        out["decoder_telemetry"][key] = {
            "median": q(vals, 0.5),
            "p10": q(vals, 0.10),
            "p90": q(vals, 0.90),
        }
    return out


def summarize(rows):
    mechanical_valid = all(
        row["methods"][method]["no_damage_control"]["max_logical_divergence"] == 0.0
        and row["methods"][method]["no_damage_control"]["max_physical_divergence"] == 0.0
        for row in rows
        for method in METHODS
    )

    out = {
        "worlds": len(rows),
        "mechanical_valid": bool(mechanical_valid),
        "methods": {},
        "relative_to_uncoded": {},
    }
    for method in METHODS:
        out["methods"][method] = {
            family: summarize_scenarios(collect(rows, method, family))
            for family in DAMAGE_FAMILIES
        }

    for family in DAMAGE_FAMILIES:
        unc = out["methods"]["UNCODED64_PAD64"][family]
        sec = out["methods"]["SECDED64_LOCAL"][family]
        uarea = unc["logical_divergence_area"]["median"]
        sarea = sec["logical_divergence_area"]["median"]
        reduction = 0.0 if uarea <= 1e-15 else float((uarea - sarea) / uarea)
        out["relative_to_uncoded"][family] = {
            "logical_divergence_area_reduction_fraction": reduction,
            "post_decode_logical_divergence_delta": float(
                sec["post_decode_logical_divergence"]["median"]
                - unc["post_decode_logical_divergence"]["median"]
            ),
            "h1_full_logical_recovery_gain": float(
                sec["horizons"]["h1"]["full_logical_recovery_rate"]
                - unc["horizons"]["h1"]["full_logical_recovery_rate"]
            ),
            "h32_full_logical_recovery_gain": float(
                sec["horizons"]["h32"]["full_logical_recovery_rate"]
                - unc["horizons"]["h32"]["full_logical_recovery_rate"]
            ),
        }

    sparse = all(
        out["methods"]["SECDED64_LOCAL"][family][
            "post_decode_logical_divergence"
        ]["median"] == 0.0
        and out["methods"]["SECDED64_LOCAL"][family]["horizons"]["h1"][
            "full_logical_recovery_rate"
        ] >= 0.95
        and out["methods"]["SECDED64_LOCAL"][family]["horizons"]["h32"][
            "full_logical_recovery_rate"
        ] >= 0.95
        and out["methods"]["SECDED64_LOCAL"][family][
            "logical_divergence_area"
        ]["median"]
        <= 0.10 * out["methods"]["UNCODED64_PAD64"][family][
            "logical_divergence_area"
        ]["median"]
        for family in ("SPREAD4", "SPREAD8")
    )

    local_limit = bool(
        sparse
        and (
            out["methods"]["SECDED64_LOCAL"]["LOCAL2"]["horizons"]["h1"][
                "full_logical_recovery_rate"
            ] < 0.95
            or out["methods"]["SECDED64_LOCAL"]["LOCAL3"]["horizons"]["h1"][
                "full_logical_recovery_rate"
            ] < 0.95
        )
    )

    out["sparse_reconstruction_signal"] = bool(sparse)
    out["local_code_distance_limit_confirmed"] = local_limit
    out["redundancy_reconstruction_signal"] = bool(sparse)
    out["resources"] = {
        "UNCODED64_PAD64": {
            "physical_bits": 128,
            "logical_dynamic_bits": 64,
            "padding_bits": 64,
            "redundancy_bits": 0,
            "logical_density": 0.5,
        },
        "SECDED64_LOCAL": {
            "physical_bits": 128,
            "logical_dynamic_bits": 64,
            "padding_bits": 0,
            "redundancy_bits": 64,
            "logical_density": 0.5,
        },
    }
    return out


def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def run():
    rows = []
    runtime = []
    for i in range(WORLD_COUNT):
        seed = WORLD_START + i
        t0 = time.perf_counter()
        row = one_world(seed)
        runtime.append({"seed": seed, "world_seconds": float(time.perf_counter() - t0)})
        rows.append(row)
    canonical = {
        "schema": "yggdrasil.dg1r-06-redundant-local-reconstruction.v1",
        "rows": rows,
        "summary": summarize(rows),
        "worlds": len(rows),
        "seed_start": WORLD_START,
        "seed_end": WORLD_START + WORLD_COUNT - 1,
        "damage_after_steps": DAMAGE_AFTER_STEPS,
        "post_steps": POST_STEPS,
    }
    runtime_obj = {
        "schema": "yggdrasil.dg1r-06-runtime-sidecar.v1",
        "rows": runtime,
    }
    return canonical, runtime_obj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--runtime-out")
    args = ap.parse_args()

    obj, runtime = run()
    raw = (encode(obj) + "\n").encode("utf-8")
    Path(args.out).write_bytes(raw)
    if args.runtime_out:
        Path(args.runtime_out).write_text(
            json.dumps(runtime, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
    print(encode({
        "output": args.out,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "summary": obj["summary"],
        "worlds": obj["worlds"],
    }))


if __name__ == "__main__":
    main()
