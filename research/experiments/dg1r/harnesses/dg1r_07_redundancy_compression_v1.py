#!/usr/bin/env python3
import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np

WORKERS = 64
STATE_BITS = 128
MAINT_CAP = 64
SEQ_PRE = 1024
POST_STEPS = 32
WORLD_START = 20260926070000
WORLD_COUNT = 8
HORIZONS = (1, 4, 8, 16, 32)
MIX_RULES = np.asarray([90, 150, 110, 22, 30], dtype=np.uint16)
METHODS = (
    "FULL16_SECDED64",
    "G8_HAMMING32",
    "G5_HAMMING25",
    "G4_HAMMING20",
    "BASE64_INERT64",
)
LESION_SIZES = ("SMALL3", "LARGE5")
LESION_COMPARTMENTS = (0, 2, 4, 6)
INPUT_COMPARTMENTS = (1, 3, 5, 7)


def eca_step_mixed(state, rules):
    left = np.roll(state, 1)
    right = np.roll(state, -1)
    idx = (left << 2) | (state << 1) | right
    return ((rules >> idx) & 1).astype(np.uint8)


def mixed_rule_assignment(rng):
    reps = WORKERS // len(MIX_RULES)
    rem = WORKERS % len(MIX_RULES)
    arr = np.concatenate(
        (np.tile(MIX_RULES, reps), MIX_RULES[:rem])
    ).astype(np.uint16)
    rng.shuffle(arr)
    return arr


def mapped_positions(rng):
    return np.asarray(
        [comp * 8 + int(rng.integers(0, 8)) for comp in INPUT_COMPARTMENTS],
        dtype=np.int64,
    )


def stripe_groups(count):
    return tuple(
        np.asarray([i for i in range(WORKERS) if i % count == j], dtype=np.int64)
        for j in range(count)
    )


FULL16_GROUPS = stripe_groups(16)
G8_GROUPS = stripe_groups(8)
G5_GROUPS = stripe_groups(5)
G4_GROUPS = stripe_groups(4)


def maintenance_bits(method):
    return {
        "FULL16_SECDED64": 64,
        "G8_HAMMING32": 32,
        "G5_HAMMING25": 25,
        "G4_HAMMING20": 20,
        "BASE64_INERT64": 0,
    }[method]


def group_config(method):
    if method == "FULL16_SECDED64":
        return FULL16_GROUPS, "SECDED", 4
    if method == "G8_HAMMING32":
        return G8_GROUPS, "HAMMING", 4
    if method == "G5_HAMMING25":
        return G5_GROUPS, "HAMMING", 5
    if method == "G4_HAMMING20":
        return G4_GROUPS, "HAMMING", 5
    return None, None, 0


def empty_telemetry():
    return {
        "syndrome_detections": 0,
        "corrected_data_bits": 0,
        "corrected_parity_bits": 0,
        "out_of_range_syndromes": 0,
    }


def secded_encode(data4):
    d0, d1, d2, d3 = [int(v) for v in data4]
    p1 = d0 ^ d1 ^ d3
    p2 = d0 ^ d2 ^ d3
    p4 = d1 ^ d2 ^ d3
    p8 = p1 ^ p2 ^ d0 ^ p4 ^ d1 ^ d2 ^ d3
    return np.asarray([p1, p2, p4, p8], dtype=np.uint8)


def secded_decode(workers, maint, idx, group_index, telemetry, correct):
    p1, p2, p4, p8 = [int(v) for v in maint[4 * group_index:4 * group_index + 4]]
    d0, d1, d2, d3 = [int(v) for v in workers[idx]]
    s1 = p1 ^ d0 ^ d1 ^ d3
    s2 = p2 ^ d0 ^ d2 ^ d3
    s4 = p4 ^ d1 ^ d2 ^ d3
    syndrome = s1 + 2 * s2 + 4 * s4
    overall = p1 ^ p2 ^ d0 ^ p4 ^ d1 ^ d2 ^ d3 ^ p8
    if syndrome == 0 and overall == 0:
        return False
    telemetry["syndrome_detections"] += 1
    if not correct:
        return True
    if syndrome != 0 and overall == 1:
        pos = syndrome
        if pos == 1:
            maint[4 * group_index] ^= 1; telemetry["corrected_parity_bits"] += 1
        elif pos == 2:
            maint[4 * group_index + 1] ^= 1; telemetry["corrected_parity_bits"] += 1
        elif pos == 3:
            workers[idx[0]] ^= 1; telemetry["corrected_data_bits"] += 1
        elif pos == 4:
            maint[4 * group_index + 2] ^= 1; telemetry["corrected_parity_bits"] += 1
        elif pos == 5:
            workers[idx[1]] ^= 1; telemetry["corrected_data_bits"] += 1
        elif pos == 6:
            workers[idx[2]] ^= 1; telemetry["corrected_data_bits"] += 1
        elif pos == 7:
            workers[idx[3]] ^= 1; telemetry["corrected_data_bits"] += 1
        return True
    if syndrome == 0 and overall == 1:
        maint[4 * group_index + 3] ^= 1
        telemetry["corrected_parity_bits"] += 1
        return True
    return True


def parity_positions(r):
    return tuple(1 << i for i in range(r))


def hamming_layout(k, r):
    n = k + r
    ppos = set(parity_positions(r))
    data_positions = [pos for pos in range(1, n + 1) if pos not in ppos]
    if len(data_positions) != k:
        raise AssertionError((k, r, n, data_positions))
    return n, tuple(data_positions), tuple(sorted(ppos))


def hamming_encode(data, r):
    k = len(data)
    n, data_positions, ppositions = hamming_layout(k, r)
    code = np.zeros(n + 1, dtype=np.uint8)
    for bit, pos in zip(data, data_positions):
        code[pos] = np.uint8(bit)
    for p in ppositions:
        v = 0
        for pos in range(1, n + 1):
            if pos & p and pos != p:
                v ^= int(code[pos])
        code[p] = np.uint8(v)
    return np.asarray([code[p] for p in ppositions], dtype=np.uint8)


def hamming_decode(workers, maint, idx, maint_start, r, telemetry, correct):
    k = len(idx)
    n, data_positions, ppositions = hamming_layout(k, r)
    code = np.zeros(n + 1, dtype=np.uint8)
    for bit, pos in zip(workers[idx], data_positions):
        code[pos] = bit
    for j, p in enumerate(ppositions):
        code[p] = maint[maint_start + j]

    syndrome = 0
    for p in ppositions:
        v = 0
        for pos in range(1, n + 1):
            if pos & p:
                v ^= int(code[pos])
        if v:
            syndrome += p

    if syndrome == 0:
        return False

    telemetry["syndrome_detections"] += 1
    if not correct:
        return True

    if syndrome > n:
        telemetry["out_of_range_syndromes"] += 1
        return True

    if syndrome in ppositions:
        pj = ppositions.index(syndrome)
        maint[maint_start + pj] ^= 1
        telemetry["corrected_parity_bits"] += 1
        return True

    if syndrome in data_positions:
        dj = data_positions.index(syndrome)
        workers[idx[dj]] ^= 1
        telemetry["corrected_data_bits"] += 1
        return True

    telemetry["out_of_range_syndromes"] += 1
    return True


def encode_all(workers, maint, method):
    maint[:] = 0
    groups, kind, r = group_config(method)
    if groups is None:
        return
    if kind == "SECDED":
        for j, idx in enumerate(groups):
            maint[4 * j:4 * j + 4] = secded_encode(workers[idx])
    else:
        cursor = 0
        for idx in groups:
            parity = hamming_encode(workers[idx], r)
            maint[cursor:cursor + len(parity)] = parity
            cursor += len(parity)
        assert cursor == maintenance_bits(method)


def scan_and_repair(workers, maint, method, telemetry, correct=True):
    groups, kind, r = group_config(method)
    if groups is None:
        return False
    any_event = False
    if kind == "SECDED":
        for j, idx in enumerate(groups):
            if secded_decode(workers, maint, idx, j, telemetry, correct):
                any_event = True
    else:
        cursor = 0
        for idx in groups:
            if hamming_decode(workers, maint, idx, cursor, r, telemetry, correct):
                any_event = True
            cursor += r
    return any_event


def initialize_state(method):
    workers = np.zeros(WORKERS, dtype=np.uint8)
    maint = np.zeros(MAINT_CAP, dtype=np.uint8)
    encode_all(workers, maint, method)
    return workers, maint


def evolve_one_external(
    workers,
    maint,
    bit,
    mapped,
    mixed_rules,
    method,
    telemetry=None,
    encoding_control=None,
):
    if telemetry is None:
        telemetry = empty_telemetry()
    if method != "BASE64_INERT64":
        before = dict(telemetry)
        event = scan_and_repair(workers, maint, method, telemetry, correct=True)
        if encoding_control is not None and event:
            encoding_control["clean"] = False
            encoding_control["pre_step_events"] += 1
        if encoding_control is not None:
            encoding_control["syndrome_detections"] += (
                telemetry["syndrome_detections"] - before["syndrome_detections"]
            )
            encoding_control["out_of_range_syndromes"] += (
                telemetry["out_of_range_syndromes"] - before["out_of_range_syndromes"]
            )

    workers[mapped] = np.uint8(bit)
    workers[:] = eca_step_mixed(workers, mixed_rules)
    encode_all(workers, maint, method)


def develop_prefix(u, mapped, mixed_rules, method):
    workers, maint = initialize_state(method)
    control = {
        "clean": True,
        "pre_step_events": 0,
        "syndrome_detections": 0,
        "out_of_range_syndromes": 0,
    }
    for t in range(SEQ_PRE):
        evolve_one_external(
            workers,
            maint,
            int(u[t]),
            mapped,
            mixed_rules,
            method,
            telemetry=None,
            encoding_control=control,
        )
    return workers, maint, control


def lesion_workers(compartment, lesion_size):
    base = compartment * 8
    offsets = (2, 3, 4) if lesion_size == "SMALL3" else (1, 2, 3, 4, 5)
    return np.asarray([base + off for off in offsets], dtype=np.int64)


def no_damage_control(pre_workers, pre_maint, u, mapped, mixed_rules, method):
    wa, ma = pre_workers.copy(), pre_maint.copy()
    wb, mb = pre_workers.copy(), pre_maint.copy()
    max_full = 0.0
    for h in range(1, POST_STEPS + 1):
        bit = int(u[SEQ_PRE + h - 1])
        evolve_one_external(wa, ma, bit, mapped, mixed_rules, method)
        evolve_one_external(wb, mb, bit, mapped, mixed_rules, method)
        a = np.concatenate((wa, ma))
        b = np.concatenate((wb, mb))
        max_full = max(max_full, float(np.mean(a != b)))
    return float(max_full)


def group_damage_load(method, lesion):
    groups, _, _ = group_config(method)
    if groups is None:
        return None
    loads = [int(np.sum(np.isin(idx, lesion))) for idx in groups]
    return {
        "max_group_load": int(max(loads)),
        "nonzero_group_count": int(sum(v > 0 for v in loads)),
        "loads": loads,
    }


def one_scenario(
    pre_workers,
    pre_maint,
    u,
    mapped,
    mixed_rules,
    method,
    compartment,
    lesion_size,
):
    lesion = lesion_workers(compartment, lesion_size)
    assert not np.any(np.isin(lesion, mapped))

    rw, rm = pre_workers.copy(), pre_maint.copy()
    dw, dm = pre_workers.copy(), pre_maint.copy()
    dw[lesion] ^= 1

    ref_tel = empty_telemetry()
    dmg_tel = empty_telemetry()
    lesion_mask = np.zeros(WORKERS, dtype=bool)
    lesion_mask[lesion] = True
    outside = ~lesion_mask
    horizons = {}
    area = []

    for h in range(1, POST_STEPS + 1):
        bit = int(u[SEQ_PRE + h - 1])
        evolve_one_external(rw, rm, bit, mapped, mixed_rules, method, ref_tel)
        evolve_one_external(dw, dm, bit, mapped, mixed_rules, method, dmg_tel)

        wdiff = dw != rw
        full_ref = np.concatenate((rw, rm))
        full_dmg = np.concatenate((dw, dm))
        fdiff = full_dmg != full_ref
        worker_div = float(np.mean(wdiff))
        area.append(worker_div)
        if h in HORIZONS:
            horizons[f"h{h}"] = {
                "worker_divergence": worker_div,
                "full_state_divergence": float(np.mean(fdiff)),
                "lesion_recovery": float(1.0 - np.mean(wdiff[lesion_mask])),
                "outside_lesion_worker_divergence": float(np.mean(wdiff[outside])),
                "exact_worker_recovery": bool(not np.any(wdiff)),
                "exact_full_recovery": bool(not np.any(fdiff)),
            }

    delta = {key: int(dmg_tel[key] - ref_tel[key]) for key in dmg_tel}
    return {
        "compartment": int(compartment),
        "lesion_size": lesion_size,
        "lesion_workers": [int(v) for v in lesion],
        "oracle_group_damage_load": group_damage_load(method, lesion),
        "horizons": horizons,
        "worker_divergence_area": float(np.sum(area)),
        "telemetry_delta": delta,
    }


def one_world(seed):
    rng = np.random.default_rng(np.random.PCG64(seed))
    u = rng.integers(0, 2, size=SEQ_PRE + POST_STEPS, dtype=np.uint8)
    mapped = mapped_positions(rng)
    mixed_rules = mixed_rule_assignment(rng)

    methods = {}
    for method in METHODS:
        workers, maint, encoding_control = develop_prefix(
            u, mapped, mixed_rules, method
        )
        no_damage = no_damage_control(
            workers, maint, u, mapped, mixed_rules, method
        )
        scenarios = []
        for compartment in LESION_COMPARTMENTS:
            for lesion_size in LESION_SIZES:
                scenarios.append(
                    one_scenario(
                        workers,
                        maint,
                        u,
                        mapped,
                        mixed_rules,
                        method,
                        compartment,
                        lesion_size,
                    )
                )
        methods[method] = {
            "encoding_control": encoding_control,
            "no_damage_control_max_full_divergence": no_damage,
            "maintenance_bits": int(maintenance_bits(method)),
            "used_state_bits": int(WORKERS + maintenance_bits(method)),
            "reclaimable_state_bits": int(STATE_BITS - WORKERS - maintenance_bits(method)),
            "scenarios": scenarios,
        }

    return {
        "seed": int(seed),
        "mapped_positions": [int(v) for v in mapped],
        "mixed_rule_counts": {
            str(int(r)): int(np.sum(mixed_rules == r)) for r in MIX_RULES
        },
        "methods": methods,
    }


def q(values, p):
    return float(np.quantile(np.asarray(values, dtype=np.float64), p))


def flatten(rows, method, lesion_size=None):
    out = []
    for row in rows:
        for sc in row["methods"][method]["scenarios"]:
            if lesion_size is None or sc["lesion_size"] == lesion_size:
                out.append(sc)
    return out


def summarize_scenarios(scenarios):
    out = {"scenario_count": len(scenarios), "horizons": {}}
    for h in HORIZONS:
        key = f"h{h}"
        exact_worker = [sc["horizons"][key]["exact_worker_recovery"] for sc in scenarios]
        exact_full = [sc["horizons"][key]["exact_full_recovery"] for sc in scenarios]
        worker_div = [sc["horizons"][key]["worker_divergence"] for sc in scenarios]
        lesion_rec = [sc["horizons"][key]["lesion_recovery"] for sc in scenarios]
        outside = [sc["horizons"][key]["outside_lesion_worker_divergence"] for sc in scenarios]
        out["horizons"][key] = {
            "exact_worker_recovery_rate": float(np.mean(exact_worker)),
            "exact_full_recovery_rate": float(np.mean(exact_full)),
            "worker_divergence_median": q(worker_div, 0.5),
            "worker_divergence_p90": q(worker_div, 0.90),
            "lesion_recovery_median": q(lesion_rec, 0.5),
            "lesion_recovery_p10": q(lesion_rec, 0.10),
            "outside_lesion_worker_divergence_median": q(outside, 0.5),
            "outside_lesion_worker_divergence_p90": q(outside, 0.90),
        }
    area = [sc["worker_divergence_area"] for sc in scenarios]
    out["worker_divergence_area_median"] = q(area, 0.5)
    out["worker_divergence_area_p90"] = q(area, 0.90)
    for key in (
        "syndrome_detections",
        "corrected_data_bits",
        "corrected_parity_bits",
        "out_of_range_syndromes",
    ):
        vals = [sc["telemetry_delta"][key] for sc in scenarios]
        out.setdefault("telemetry_delta", {})[key] = {
            "median": q(vals, 0.5),
            "p10": q(vals, 0.10),
            "p90": q(vals, 0.90),
        }
    loads = [
        sc["oracle_group_damage_load"]["max_group_load"]
        for sc in scenarios
        if sc["oracle_group_damage_load"] is not None
    ]
    out["oracle_max_group_load_median"] = q(loads, 0.5) if loads else None
    out["oracle_max_group_load_max"] = int(max(loads)) if loads else None
    return out


def summarize(rows):
    no_damage_pass = all(
        row["methods"][method]["no_damage_control_max_full_divergence"] == 0.0
        for row in rows
        for method in METHODS
    )
    encoding_pass = all(
        row["methods"][method]["encoding_control"]["clean"]
        for row in rows
        for method in METHODS
        if method != "BASE64_INERT64"
    )

    out = {
        "worlds": len(rows),
        "no_damage_control_pass": bool(no_damage_pass),
        "encoding_control_pass": bool(encoding_pass),
        "methods": {},
    }
    for method in METHODS:
        out["methods"][method] = {
            "maintenance_bits": int(maintenance_bits(method)),
            "used_state_bits": int(WORKERS + maintenance_bits(method)),
            "reclaimable_state_bits": int(STATE_BITS - WORKERS - maintenance_bits(method)),
            "maintenance_reduction_vs_full": float(
                (64 - maintenance_bits(method)) / 64
            ),
            "SMALL3": summarize_scenarios(flatten(rows, method, "SMALL3")),
            "LARGE5": summarize_scenarios(flatten(rows, method, "LARGE5")),
            "COMBINED": summarize_scenarios(flatten(rows, method, None)),
        }

    def passes(method):
        m = out["methods"][method]
        return bool(
            m["SMALL3"]["horizons"]["h1"]["exact_full_recovery_rate"] >= 0.95
            and m["LARGE5"]["horizons"]["h1"]["exact_full_recovery_rate"] >= 0.95
            and m["COMBINED"]["horizons"]["h32"]["exact_full_recovery_rate"] >= 0.95
        )

    full_ref = passes("FULL16_SECDED64")
    g8 = passes("G8_HAMMING32")
    g5 = passes("G5_HAMMING25")
    g4 = passes("G4_HAMMING20")
    floor = g5 and not g4
    strong = g5 and no_damage_pass and encoding_pass and out["methods"]["G5_HAMMING25"]["reclaimable_state_bits"] >= 35

    out["reference_preservation"] = bool(full_ref)
    out["g8_compressed_repair"] = bool(g8)
    out["g5_compressed_repair"] = bool(g5)
    out["g4_compressed_repair"] = bool(g4)
    out["resource_floor_signal"] = bool(floor)
    out["strong_redundancy_compression"] = bool(strong)
    return out


def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def run():
    rows = [one_world(WORLD_START + i) for i in range(WORLD_COUNT)]
    return {
        "schema": "yggdrasil.dg1r-07-redundancy-compression.v1",
        "rows": rows,
        "summary": summarize(rows),
        "worlds": len(rows),
        "seed_start": WORLD_START,
        "seed_end": WORLD_START + WORLD_COUNT - 1,
        "pre_steps": SEQ_PRE,
        "post_steps": POST_STEPS,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--runtime-out")
    args = ap.parse_args()
    t0 = time.perf_counter()
    obj = run()
    elapsed = float(time.perf_counter() - t0)
    raw = (encode(obj) + "\n").encode("utf-8")
    Path(args.out).write_bytes(raw)
    if args.runtime_out:
        Path(args.runtime_out).write_text(
            json.dumps(
                {"schema": "yggdrasil.dg1r-07-runtime-sidecar.v1", "seconds": elapsed},
                sort_keys=True,
                indent=2,
            ) + "\n",
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
