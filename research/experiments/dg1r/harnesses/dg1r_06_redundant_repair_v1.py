#!/usr/bin/env python3
import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np

WORKERS = 64
MAINT = 64
STATE_BITS = 128
SEQ_PRE = 1024
POST_STEPS = 32
WORLD_START = 20260926060000
WORLD_COUNT = 8
HORIZONS = (1, 4, 8, 16, 32)
MIX_RULES = np.asarray([90, 150, 110, 22, 30], dtype=np.uint16)
METHODS = (
    "BASE64_INERT64",
    "STRIPE_ECC_DETECT",
    "LOCAL_ECC_REPAIR",
    "STRIPE_ECC_REPAIR",
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


def groups_for(layout):
    if layout == "LOCAL":
        return tuple(
            np.asarray([4 * j + k for k in range(4)], dtype=np.int64)
            for j in range(16)
        )
    if layout == "STRIPE":
        return tuple(
            np.asarray([j, j + 16, j + 32, j + 48], dtype=np.int64)
            for j in range(16)
        )
    raise ValueError(layout)


LOCAL_GROUPS = groups_for("LOCAL")
STRIPE_GROUPS = groups_for("STRIPE")


def encode_group(data4):
    d0, d1, d2, d3 = [int(v) for v in data4]
    p1 = d0 ^ d1 ^ d3
    p2 = d0 ^ d2 ^ d3
    p4 = d1 ^ d2 ^ d3
    p8 = p1 ^ p2 ^ d0 ^ p4 ^ d1 ^ d2 ^ d3
    return np.asarray([p1, p2, p4, p8], dtype=np.uint8)


def encode_all(workers, maint, groups):
    for j, idx in enumerate(groups):
        maint[4 * j:4 * j + 4] = encode_group(workers[idx])


def decode_group(workers, maint, idx, group_index, correct, telemetry):
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

    if syndrome != 0 and overall == 1:
        if not correct:
            return True
        pos = syndrome
        if pos == 1:
            maint[4 * group_index] ^= 1
            telemetry["corrected_parity_bits"] += 1
        elif pos == 2:
            maint[4 * group_index + 1] ^= 1
            telemetry["corrected_parity_bits"] += 1
        elif pos == 3:
            workers[idx[0]] ^= 1
            telemetry["corrected_data_bits"] += 1
        elif pos == 4:
            maint[4 * group_index + 2] ^= 1
            telemetry["corrected_parity_bits"] += 1
        elif pos == 5:
            workers[idx[1]] ^= 1
            telemetry["corrected_data_bits"] += 1
        elif pos == 6:
            workers[idx[2]] ^= 1
            telemetry["corrected_data_bits"] += 1
        elif pos == 7:
            workers[idx[3]] ^= 1
            telemetry["corrected_data_bits"] += 1
        return True

    if syndrome == 0 and overall == 1:
        if correct:
            maint[4 * group_index + 3] ^= 1
            telemetry["corrected_parity_bits"] += 1
        return True

    telemetry["uncorrectable_events"] += 1
    return True


def scan_ecc(workers, maint, groups, correct, telemetry):
    any_event = False
    for j, idx in enumerate(groups):
        if decode_group(workers, maint, idx, j, correct, telemetry):
            any_event = True
    return any_event


def empty_telemetry():
    return {
        "syndrome_detections": 0,
        "corrected_data_bits": 0,
        "corrected_parity_bits": 0,
        "uncorrectable_events": 0,
    }


def method_layout(method):
    if method == "LOCAL_ECC_REPAIR":
        return LOCAL_GROUPS
    if method in ("STRIPE_ECC_DETECT", "STRIPE_ECC_REPAIR"):
        return STRIPE_GROUPS
    return None


def initialize_state(method):
    workers = np.zeros(WORKERS, dtype=np.uint8)
    maint = np.zeros(MAINT, dtype=np.uint8)
    groups = method_layout(method)
    if groups is not None:
        encode_all(workers, maint, groups)
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
    groups = method_layout(method)
    if telemetry is None:
        telemetry = empty_telemetry()

    if groups is not None:
        pre = dict(telemetry)
        correct = method in ("LOCAL_ECC_REPAIR", "STRIPE_ECC_REPAIR")
        event = scan_ecc(workers, maint, groups, correct, telemetry)
        if encoding_control is not None and event:
            encoding_control["clean"] = False
            encoding_control["pre_step_events"] += 1
        if encoding_control is not None:
            encoding_control["syndrome_detections"] += (
                telemetry["syndrome_detections"] - pre["syndrome_detections"]
            )
            encoding_control["uncorrectable_events"] += (
                telemetry["uncorrectable_events"] - pre["uncorrectable_events"]
            )

    workers[mapped] = np.uint8(bit)
    workers[:] = eca_step_mixed(workers, mixed_rules)

    if groups is not None:
        encode_all(workers, maint, groups)
    else:
        maint[:] = 0


def develop_prefix(u, mapped, mixed_rules, method):
    workers, maint = initialize_state(method)
    control = {
        "clean": True,
        "pre_step_events": 0,
        "syndrome_detections": 0,
        "uncorrectable_events": 0,
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
    max_worker = 0.0
    max_full = 0.0
    for h in range(1, POST_STEPS + 1):
        bit = int(u[SEQ_PRE + h - 1])
        evolve_one_external(wa, ma, bit, mapped, mixed_rules, method)
        evolve_one_external(wb, mb, bit, mapped, mixed_rules, method)
        max_worker = max(max_worker, float(np.mean(wa != wb)))
        full_a = np.concatenate((wa, ma))
        full_b = np.concatenate((wb, mb))
        max_full = max(max_full, float(np.mean(full_a != full_b)))
    return {
        "max_worker_divergence": float(max_worker),
        "max_full_divergence": float(max_full),
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
    curve = []

    for h in range(1, POST_STEPS + 1):
        bit = int(u[SEQ_PRE + h - 1])
        evolve_one_external(
            rw, rm, bit, mapped, mixed_rules, method, telemetry=ref_tel
        )
        evolve_one_external(
            dw, dm, bit, mapped, mixed_rules, method, telemetry=dmg_tel
        )

        wdiff = dw != rw
        full_ref = np.concatenate((rw, rm))
        full_dmg = np.concatenate((dw, dm))
        fdiff = full_dmg != full_ref
        worker_div = float(np.mean(wdiff))
        full_div = float(np.mean(fdiff))
        lesion_recovery = float(1.0 - np.mean(wdiff[lesion_mask]))
        outside_div = float(np.mean(wdiff[outside]))
        exact_worker = bool(not np.any(wdiff))
        exact_full = bool(not np.any(fdiff))
        curve.append(worker_div)

        if h in HORIZONS:
            horizons[f"h{h}"] = {
                "worker_divergence": worker_div,
                "full_state_divergence": full_div,
                "lesion_recovery": lesion_recovery,
                "outside_lesion_worker_divergence": outside_div,
                "exact_worker_recovery": exact_worker,
                "exact_full_recovery": exact_full,
            }

    delta = {
        key: int(dmg_tel[key] - ref_tel[key])
        for key in dmg_tel
    }
    return {
        "compartment": int(compartment),
        "lesion_size": lesion_size,
        "lesion_workers": [int(v) for v in lesion],
        "horizons": horizons,
        "worker_divergence_area": float(np.sum(curve)),
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
            "no_damage_control": no_damage,
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
        worker = [sc["horizons"][key]["worker_divergence"] for sc in scenarios]
        full = [sc["horizons"][key]["full_state_divergence"] for sc in scenarios]
        recovery = [sc["horizons"][key]["lesion_recovery"] for sc in scenarios]
        outside = [
            sc["horizons"][key]["outside_lesion_worker_divergence"]
            for sc in scenarios
        ]
        exact_worker = [
            sc["horizons"][key]["exact_worker_recovery"] for sc in scenarios
        ]
        exact_full = [
            sc["horizons"][key]["exact_full_recovery"] for sc in scenarios
        ]
        out["horizons"][key] = {
            "worker_divergence_median": q(worker, 0.5),
            "worker_divergence_p90": q(worker, 0.90),
            "full_state_divergence_median": q(full, 0.5),
            "full_state_divergence_p90": q(full, 0.90),
            "lesion_recovery_median": q(recovery, 0.5),
            "lesion_recovery_p10": q(recovery, 0.10),
            "outside_lesion_worker_divergence_median": q(outside, 0.5),
            "outside_lesion_worker_divergence_p90": q(outside, 0.90),
            "exact_worker_recovery_rate": float(np.mean(exact_worker)),
            "exact_full_recovery_rate": float(np.mean(exact_full)),
        }

    area = [sc["worker_divergence_area"] for sc in scenarios]
    out["worker_divergence_area_median"] = q(area, 0.5)
    out["worker_divergence_area_p90"] = q(area, 0.90)

    out["telemetry_delta"] = {}
    for key in (
        "syndrome_detections",
        "corrected_data_bits",
        "corrected_parity_bits",
        "uncorrectable_events",
    ):
        vals = [sc["telemetry_delta"][key] for sc in scenarios]
        out["telemetry_delta"][key] = {
            "median": q(vals, 0.5),
            "p10": q(vals, 0.10),
            "p90": q(vals, 0.90),
        }
    return out


def reduction(value, reference):
    if reference <= 1e-15:
        return 0.0
    return float((reference - value) / reference)


def summarize(rows):
    no_damage_pass = all(
        row["methods"][method]["no_damage_control"]["max_worker_divergence"] == 0.0
        and row["methods"][method]["no_damage_control"]["max_full_divergence"] == 0.0
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
            "SMALL3": summarize_scenarios(flatten(rows, method, "SMALL3")),
            "LARGE5": summarize_scenarios(flatten(rows, method, "LARGE5")),
            "COMBINED": summarize_scenarios(flatten(rows, method, None)),
        }

    base = out["methods"]["BASE64_INERT64"]["COMBINED"]
    detect = out["methods"]["STRIPE_ECC_DETECT"]["COMBINED"]
    local = out["methods"]["LOCAL_ECC_REPAIR"]["COMBINED"]
    stripe = out["methods"]["STRIPE_ECC_REPAIR"]["COMBINED"]

    redundancy_only = reduction(
        detect["worker_divergence_area_median"],
        base["worker_divergence_area_median"],
    ) >= 0.25

    local_gain = (
        local["horizons"]["h1"]["exact_worker_recovery_rate"]
        - base["horizons"]["h1"]["exact_worker_recovery_rate"]
    )
    local_signal = local_gain >= 0.25

    stripe_small = out["methods"]["STRIPE_ECC_REPAIR"]["SMALL3"]
    stripe_large = out["methods"]["STRIPE_ECC_REPAIR"]["LARGE5"]
    stripe_signal = (
        stripe_small["horizons"]["h1"]["exact_worker_recovery_rate"] >= 0.95
        and stripe_large["horizons"]["h1"]["exact_worker_recovery_rate"] >= 0.95
        and stripe["horizons"]["h32"]["exact_full_recovery_rate"] >= 0.95
    )

    striping_advantage = (
        stripe["horizons"]["h1"]["exact_worker_recovery_rate"]
        - local["horizons"]["h1"]["exact_worker_recovery_rate"]
    ) >= 0.25

    stripe_uncorrectable = stripe["telemetry_delta"]["uncorrectable_events"]["median"]
    full_signal = (
        stripe_signal
        and no_damage_pass
        and encoding_pass
        and stripe_uncorrectable == 0.0
    )

    out["redundancy_only_signal"] = bool(redundancy_only)
    out["local_ecc_repair_signal"] = bool(local_signal)
    out["striped_ecc_repair_signal"] = bool(stripe_signal)
    out["striping_advantage"] = bool(striping_advantage)
    out["full_redundant_self_repair_signal"] = bool(full_signal)
    out["relative"] = {
        "detect_area_reduction_vs_base": reduction(
            detect["worker_divergence_area_median"],
            base["worker_divergence_area_median"],
        ),
        "local_h1_exact_worker_gain_vs_base": float(local_gain),
        "stripe_h1_exact_worker_gain_vs_local": float(
            stripe["horizons"]["h1"]["exact_worker_recovery_rate"]
            - local["horizons"]["h1"]["exact_worker_recovery_rate"]
        ),
    }
    return out


def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def run():
    rows = [one_world(WORLD_START + i) for i in range(WORLD_COUNT)]
    canonical = {
        "schema": "yggdrasil.dg1r-06-distributed-redundancy-repair.v1",
        "rows": rows,
        "summary": summarize(rows),
        "worlds": len(rows),
        "seed_start": WORLD_START,
        "seed_end": WORLD_START + WORLD_COUNT - 1,
        "pre_steps": SEQ_PRE,
        "post_steps": POST_STEPS,
    }
    return canonical


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
                {
                    "schema": "yggdrasil.dg1r-06-runtime-sidecar.v1",
                    "seconds": elapsed,
                },
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
