#!/usr/bin/env python3
import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np

STATE_BITS = 128
REF_WORKERS = 64
EXP_WORKERS = 103
MAINT_BITS = 25
GROUP_COUNT = 5
HAMMING_R = 5
SEQ_LEN = 4096
TRAIN_START = 64
TRAIN_ROWS = 2048
TEST_START = 2560
TEST_ROWS = 1024
RIDGE_ALPHA = 1e-3
REPAIR_PRE = 1024
REPAIR_POST = 32
WORLD_START = 20260926080000
WORLD_COUNT = 8
HORIZONS = (1, 4, 8, 16, 32)
MIX_RULES = np.asarray([90, 150, 110, 22, 30], dtype=np.uint16)
TASKS = ("D1", "D4", "D8", "D16", "D32", "XOR3_11", "PARITY5", "MOTIF2_12")
METHODS = ("REF64_G5_25", "EXP103_G5_25", "BASE103_NOECC")
LESION_SIZES = ("SMALL3", "LARGE5")
LESION_BASES = (0, 16, 32, 48)
INPUT_REGIONS = ((8, 16), (24, 32), (40, 48), (56, 64))


def eca_step_mixed(state, rules):
    left = np.roll(state, 1)
    right = np.roll(state, -1)
    idx = (left << 2) | (state << 1) | right
    return ((rules >> idx) & 1).astype(np.uint8)


def mixed_rule_assignment_103(rng):
    reps = EXP_WORKERS // len(MIX_RULES)
    rem = EXP_WORKERS % len(MIX_RULES)
    arr = np.concatenate((np.tile(MIX_RULES, reps), MIX_RULES[:rem])).astype(np.uint16)
    rng.shuffle(arr)
    return arr


def mapped_positions(rng):
    return np.asarray(
        [int(rng.integers(lo, hi)) for lo, hi in INPUT_REGIONS],
        dtype=np.int64,
    )


def worker_count(method):
    return REF_WORKERS if method == "REF64_G5_25" else EXP_WORKERS


def coded(method):
    return method in ("REF64_G5_25", "EXP103_G5_25")


def groups_for(nworkers):
    return tuple(
        np.asarray([i for i in range(nworkers) if i % GROUP_COUNT == j], dtype=np.int64)
        for j in range(GROUP_COUNT)
    )


def parity_positions(r):
    return tuple(1 << i for i in range(r))


def hamming_layout(k, r):
    n = k + r
    ppos = tuple(sorted(parity_positions(r)))
    pset = set(ppos)
    data_positions = tuple(pos for pos in range(1, n + 1) if pos not in pset)
    if len(data_positions) != k:
        raise AssertionError((k, r, n, data_positions))
    return n, data_positions, ppos


def hamming_encode(data, r=HAMMING_R):
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


def empty_telemetry():
    return {
        "syndrome_detections": 0,
        "corrected_data_bits": 0,
        "corrected_parity_bits": 0,
        "out_of_range_syndromes": 0,
    }


def hamming_decode(workers, maint, idx, maint_start, telemetry, correct=True):
    k = len(idx)
    n, data_positions, ppositions = hamming_layout(k, HAMMING_R)
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


def encode_all(workers, maint):
    maint[:] = 0
    cursor = 0
    for idx in groups_for(len(workers)):
        p = hamming_encode(workers[idx])
        maint[cursor:cursor + len(p)] = p
        cursor += len(p)
    assert cursor == MAINT_BITS


def scan_and_repair(workers, maint, telemetry):
    cursor = 0
    event = False
    for idx in groups_for(len(workers)):
        if hamming_decode(workers, maint, idx, cursor, telemetry, correct=True):
            event = True
        cursor += HAMMING_R
    return event


def initialize_state(method):
    workers = np.zeros(worker_count(method), dtype=np.uint8)
    maint = np.zeros(MAINT_BITS, dtype=np.uint8)
    if coded(method):
        encode_all(workers, maint)
    return workers, maint


def full_state(workers, maint, method):
    if method == "REF64_G5_25":
        inactive = np.zeros(STATE_BITS - REF_WORKERS - MAINT_BITS, dtype=np.uint8)
        return np.concatenate((workers, maint, inactive))
    return np.concatenate((workers, maint))


def evolve_one_external(
    workers,
    maint,
    bit,
    mapped,
    rules,
    method,
    telemetry=None,
    encoding_control=None,
):
    if telemetry is None:
        telemetry = empty_telemetry()
    if coded(method):
        before = dict(telemetry)
        event = scan_and_repair(workers, maint, telemetry)
        if encoding_control is not None and event:
            encoding_control["clean"] = False
            encoding_control["pre_step_events"] += 1
        if encoding_control is not None:
            encoding_control["syndrome_detections"] += telemetry["syndrome_detections"] - before["syndrome_detections"]
            encoding_control["out_of_range_syndromes"] += telemetry["out_of_range_syndromes"] - before["out_of_range_syndromes"]

    workers[mapped] = np.uint8(bit)
    workers[:] = eca_step_mixed(workers, rules[:len(workers)])
    if coded(method):
        encode_all(workers, maint)
    else:
        maint[:] = 0


def run_trace(u, mapped, rules, method):
    workers, maint = initialize_state(method)
    x = np.empty((len(u), len(workers)), dtype=np.uint8)
    control = {"clean": True, "pre_step_events": 0, "syndrome_detections": 0, "out_of_range_syndromes": 0}
    for t, bit in enumerate(u):
        evolve_one_external(workers, maint, int(bit), mapped, rules, method, encoding_control=control)
        x[t] = workers
    return x, workers, maint, control


def build_targets(u):
    n = len(u)
    out = {}
    for d in (1, 4, 8, 16, 32):
        y = np.zeros(n, dtype=np.uint8)
        y[d:] = u[:-d]
        out[f"D{d}"] = y
    y = np.zeros(n, dtype=np.uint8)
    y[11:] = u[8:-3] ^ u[:-11]
    out["XOR3_11"] = y
    y = np.zeros(n, dtype=np.uint8)
    for d in range(1, 6):
        shifted = np.zeros(n, dtype=np.uint8)
        shifted[d:] = u[:-d]
        y ^= shifted
    out["PARITY5"] = y
    motif = np.zeros(n, dtype=np.uint8)
    pattern = np.asarray([1, 0, 1], dtype=np.uint8)
    for t in range(12, n):
        hist = u[t - 12:t]
        count = 0
        for i in range(10):
            if np.array_equal(hist[i:i + 3], pattern):
                count += 1
        motif[t] = 1 if count >= 2 else 0
    out["MOTIF2_12"] = motif
    return out


def balanced_accuracy(y_true, y_pred):
    pos = y_true == 1
    neg = ~pos
    tpr = float(np.mean(y_pred[pos] == 1)) if np.any(pos) else 0.5
    tnr = float(np.mean(y_pred[neg] == 0)) if np.any(neg) else 0.5
    return 0.5 * (tpr + tnr)


def train_readouts(x, targets):
    tr = slice(TRAIN_START, TRAIN_START + TRAIN_ROWS)
    te = slice(TEST_START, TEST_START + TEST_ROWS)
    xt = x[tr].astype(np.float64)
    xv = x[te].astype(np.float64)
    xa = np.column_stack((xt, np.ones(len(xt), dtype=np.float64)))
    xva = np.column_stack((xv, np.ones(len(xv), dtype=np.float64)))
    ymat = np.column_stack([targets[name][tr] for name in TASKS]).astype(np.float64)
    gram = xa.T @ xa
    reg = RIDGE_ALPHA * np.eye(gram.shape[0], dtype=np.float64)
    reg[-1, -1] = 0.0
    beta = np.linalg.solve(gram + reg, xa.T @ ymat)
    pred = xva @ beta
    metrics = {}
    for j, name in enumerate(TASKS):
        yp = (pred[:, j] >= 0.5).astype(np.uint8)
        yt = targets[name][te]
        metrics[name] = balanced_accuracy(yt, yp) if name == "MOTIF2_12" else float(np.mean(yp == yt))
    return metrics


def binary_entropy_features(x):
    p = np.mean(x, axis=0, dtype=np.float64)
    mask = (p > 0.0) & (p < 1.0)
    h = np.zeros_like(p)
    h[mask] = -(p[mask] * np.log2(p[mask]) + (1.0 - p[mask]) * np.log2(1.0 - p[mask]))
    return float(np.mean(h))


def feature_rank(x):
    rows = min(512, len(x))
    m = x[:rows].astype(np.float64)
    m -= np.mean(m, axis=0, keepdims=True)
    s = np.linalg.svd(m, compute_uv=False)
    if len(s) == 0 or s[0] == 0.0:
        rank = 0
    else:
        rank = int(np.sum(s > s[0] * 1e-8))
    return rank, float(rank / x.shape[1])


def capability_metrics(x, targets):
    te = slice(TEST_START, TEST_START + TEST_ROWS)
    tasks = train_readouts(x, targets)
    rank, rank_frac = feature_rank(x[te])
    return {
        "tasks": tasks,
        "memory_score": float(np.mean([tasks["D8"], tasks["D16"], tasks["D32"]])),
        "nonlinear_score": float(np.mean([tasks["XOR3_11"], tasks["PARITY5"], tasks["MOTIF2_12"]])),
        "state_entropy": binary_entropy_features(x[te]),
        "feature_rank": int(rank),
        "feature_rank_fraction": rank_frac,
    }


def lesion_workers(base, lesion_size):
    offsets = (2, 3, 4) if lesion_size == "SMALL3" else (1, 2, 3, 4, 5)
    return np.asarray([base + off for off in offsets], dtype=np.int64)


def develop_repair_prefix(u, mapped, rules, method):
    workers, maint = initialize_state(method)
    control = {"clean": True, "pre_step_events": 0, "syndrome_detections": 0, "out_of_range_syndromes": 0}
    for t in range(REPAIR_PRE):
        evolve_one_external(workers, maint, int(u[t]), mapped, rules, method, encoding_control=control)
    return workers, maint, control


def no_damage_control(pre_w, pre_m, u, mapped, rules, method):
    wa, ma = pre_w.copy(), pre_m.copy()
    wb, mb = pre_w.copy(), pre_m.copy()
    max_div = 0.0
    for h in range(1, REPAIR_POST + 1):
        bit = int(u[REPAIR_PRE + h - 1])
        evolve_one_external(wa, ma, bit, mapped, rules, method)
        evolve_one_external(wb, mb, bit, mapped, rules, method)
        max_div = max(max_div, float(np.mean(full_state(wa, ma, method) != full_state(wb, mb, method))))
    return float(max_div)


def one_repair_scenario(pre_w, pre_m, u, mapped, rules, method, base, lesion_size):
    lesion = lesion_workers(base, lesion_size)
    assert not np.any(np.isin(lesion, mapped))
    rw, rm = pre_w.copy(), pre_m.copy()
    dw, dm = pre_w.copy(), pre_m.copy()
    dw[lesion] ^= 1
    ref_tel = empty_telemetry()
    dmg_tel = empty_telemetry()
    lesion_mask = np.zeros(len(dw), dtype=bool)
    lesion_mask[lesion] = True
    outside = ~lesion_mask
    horizons = {}
    area = []
    for h in range(1, REPAIR_POST + 1):
        bit = int(u[REPAIR_PRE + h - 1])
        evolve_one_external(rw, rm, bit, mapped, rules, method, ref_tel)
        evolve_one_external(dw, dm, bit, mapped, rules, method, dmg_tel)
        wdiff = dw != rw
        fdiff = full_state(dw, dm, method) != full_state(rw, rm, method)
        area.append(float(np.mean(wdiff)))
        if h in HORIZONS:
            horizons[f"h{h}"] = {
                "exact_worker_recovery": bool(not np.any(wdiff)),
                "exact_full_recovery": bool(not np.any(fdiff)),
                "worker_divergence": float(np.mean(wdiff)),
                "full_state_divergence": float(np.mean(fdiff)),
                "lesion_recovery": float(1.0 - np.mean(wdiff[lesion_mask])),
                "outside_lesion_worker_divergence": float(np.mean(wdiff[outside])),
            }
    delta = {key: int(dmg_tel[key] - ref_tel[key]) for key in dmg_tel}
    return {
        "lesion_base": int(base),
        "lesion_size": lesion_size,
        "lesion_workers": [int(v) for v in lesion],
        "horizons": horizons,
        "worker_divergence_area": float(np.sum(area)),
        "telemetry_delta": delta,
    }


def one_world(seed):
    rng = np.random.default_rng(np.random.PCG64(seed))
    u = rng.integers(0, 2, size=SEQ_LEN, dtype=np.uint8)
    mapped = mapped_positions(rng)
    rules103 = mixed_rule_assignment_103(rng)
    targets = build_targets(u)

    methods = {}
    traces = {}
    for method in METHODS:
        x, final_w, final_m, cap_control = run_trace(u, mapped, rules103, method)
        traces[method] = x
        cap = capability_metrics(x, targets)
        pre_w, pre_m, repair_control = develop_repair_prefix(u, mapped, rules103, method)
        nd = no_damage_control(pre_w, pre_m, u, mapped, rules103, method)
        scenarios = []
        for base in LESION_BASES:
            for lesion_size in LESION_SIZES:
                scenarios.append(one_repair_scenario(pre_w, pre_m, u, mapped, rules103, method, base, lesion_size))
        methods[method] = {
            "capability": cap,
            "capability_encoding_control": cap_control,
            "repair_encoding_control": repair_control,
            "no_damage_control_max_full_divergence": nd,
            "worker_count": int(worker_count(method)),
            "maintenance_bits": int(MAINT_BITS if coded(method) else 0),
            "worker_updates_per_external_step": int(worker_count(method)),
            "scenarios": scenarios,
        }

    methods["EXP103_G5_25"]["base103_worker_trace_equal"] = bool(
        np.array_equal(traces["EXP103_G5_25"], traces["BASE103_NOECC"])
    )

    return {
        "seed": int(seed),
        "mapped_positions": [int(v) for v in mapped],
        "rule_counts_103": {str(int(r)): int(np.sum(rules103 == r)) for r in MIX_RULES},
        "methods": methods,
    }


def q(values, p):
    return float(np.quantile(np.asarray(values, dtype=np.float64), p))


def flatten_scenarios(rows, method, lesion_size=None):
    out = []
    for row in rows:
        for sc in row["methods"][method]["scenarios"]:
            if lesion_size is None or sc["lesion_size"] == lesion_size:
                out.append(sc)
    return out


def summarize_repair(scenarios):
    out = {"scenario_count": len(scenarios), "horizons": {}}
    for h in HORIZONS:
        k = f"h{h}"
        ew = [sc["horizons"][k]["exact_worker_recovery"] for sc in scenarios]
        ef = [sc["horizons"][k]["exact_full_recovery"] for sc in scenarios]
        wd = [sc["horizons"][k]["worker_divergence"] for sc in scenarios]
        lr = [sc["horizons"][k]["lesion_recovery"] for sc in scenarios]
        od = [sc["horizons"][k]["outside_lesion_worker_divergence"] for sc in scenarios]
        out["horizons"][k] = {
            "exact_worker_recovery_rate": float(np.mean(ew)),
            "exact_full_recovery_rate": float(np.mean(ef)),
            "worker_divergence_median": q(wd, 0.5),
            "lesion_recovery_median": q(lr, 0.5),
            "outside_lesion_worker_divergence_median": q(od, 0.5),
        }
    area = [sc["worker_divergence_area"] for sc in scenarios]
    out["worker_divergence_area_median"] = q(area, 0.5)
    for key in ("syndrome_detections", "corrected_data_bits", "corrected_parity_bits", "out_of_range_syndromes"):
        vals = [sc["telemetry_delta"][key] for sc in scenarios]
        out.setdefault("telemetry_delta", {})[key] = {"median": q(vals, 0.5), "p90": q(vals, 0.90)}
    return out


def summarize_capability(rows, method):
    caps = [row["methods"][method]["capability"] for row in rows]
    task_summary = {}
    for task in TASKS:
        vals = [c["tasks"][task] for c in caps]
        task_summary[task] = {"median": q(vals, 0.5), "p10": q(vals, 0.10)}
    return {
        "tasks": task_summary,
        "memory_score": {"median": q([c["memory_score"] for c in caps], 0.5), "p10": q([c["memory_score"] for c in caps], 0.10)},
        "nonlinear_score": {"median": q([c["nonlinear_score"] for c in caps], 0.5), "p10": q([c["nonlinear_score"] for c in caps], 0.10)},
        "state_entropy": {"median": q([c["state_entropy"] for c in caps], 0.5), "p10": q([c["state_entropy"] for c in caps], 0.10)},
        "feature_rank": {"median": q([c["feature_rank"] for c in caps], 0.5), "p10": q([c["feature_rank"] for c in caps], 0.10)},
        "feature_rank_fraction": {"median": q([c["feature_rank_fraction"] for c in caps], 0.5), "p10": q([c["feature_rank_fraction"] for c in caps], 0.10)},
    }


def summarize(rows):
    no_damage_pass = all(
        row["methods"][m]["no_damage_control_max_full_divergence"] == 0.0
        for row in rows for m in METHODS
    )
    encoding_pass = all(
        row["methods"][m]["capability_encoding_control"]["clean"]
        and row["methods"][m]["repair_encoding_control"]["clean"]
        for row in rows for m in ("REF64_G5_25", "EXP103_G5_25")
    )
    base103_equiv = all(
        row["methods"]["EXP103_G5_25"]["base103_worker_trace_equal"]
        for row in rows
    )

    out = {
        "worlds": len(rows),
        "no_damage_control_pass": bool(no_damage_pass),
        "encoding_control_pass": bool(encoding_pass),
        "base103_worker_trace_equivalence": bool(base103_equiv),
        "methods": {},
    }
    for m in METHODS:
        out["methods"][m] = {
            "worker_count": int(worker_count(m)),
            "maintenance_bits": int(MAINT_BITS if coded(m) else 0),
            "worker_updates_per_external_step": int(worker_count(m)),
            "capability": summarize_capability(rows, m),
            "SMALL3": summarize_repair(flatten_scenarios(rows, m, "SMALL3")),
            "LARGE5": summarize_repair(flatten_scenarios(rows, m, "LARGE5")),
            "COMBINED": summarize_repair(flatten_scenarios(rows, m, None)),
        }

    exp = out["methods"]["EXP103_G5_25"]
    ref = out["methods"]["REF64_G5_25"]
    repair_preserved = bool(
        exp["SMALL3"]["horizons"]["h1"]["exact_full_recovery_rate"] >= 0.95
        and exp["LARGE5"]["horizons"]["h1"]["exact_full_recovery_rate"] >= 0.95
        and exp["COMBINED"]["horizons"]["h32"]["exact_full_recovery_rate"] >= 0.95
        and no_damage_pass and encoding_pass
    )

    mem_gain = exp["capability"]["memory_score"]["median"] - ref["capability"]["memory_score"]["median"]
    nl_gain = exp["capability"]["nonlinear_score"]["median"] - ref["capability"]["nonlinear_score"]["median"]
    ref_rank = ref["capability"]["feature_rank"]["median"]
    exp_rank = exp["capability"]["feature_rank"]["median"]
    rank_gain_fraction = float((exp_rank - ref_rank) / ref_rank) if ref_rank > 0 else 0.0
    no_large_degradation = mem_gain >= -0.05 and nl_gain >= -0.05
    capability_gain = bool(
        no_large_degradation
        and (mem_gain >= 0.02 or nl_gain >= 0.02 or rank_gain_fraction >= 0.20)
    )
    strong = bool(
        repair_preserved
        and capability_gain
        and exp["capability"]["state_entropy"]["median"] >= 0.20
        and base103_equiv
    )

    out["repair_preserved_103"] = repair_preserved
    out["worker_redeployment"] = {
        "additional_workers": 39,
        "worker_increase_fraction": 39 / 64,
        "ref_worker_share": 64 / 128,
        "exp_worker_share": 103 / 128,
        "ref_workers_per_maintenance_bit": 64 / 25,
        "exp_workers_per_maintenance_bit": 103 / 25,
    }
    out["capability_delta_exp103_minus_ref64"] = {
        "memory_score_median": float(mem_gain),
        "nonlinear_score_median": float(nl_gain),
        "feature_rank_gain_fraction": rank_gain_fraction,
    }
    out["capability_gain"] = capability_gain
    out["strong_redeployment_signal"] = strong
    return out


def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def run():
    rows = [one_world(WORLD_START + i) for i in range(WORLD_COUNT)]
    return {
        "schema": "yggdrasil.dg1r-08-reclaimed-state-redeployment.v1",
        "rows": rows,
        "summary": summarize(rows),
        "worlds": len(rows),
        "seed_start": WORLD_START,
        "seed_end": WORLD_START + WORLD_COUNT - 1,
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
            json.dumps({"schema": "yggdrasil.dg1r-08-runtime-sidecar.v1", "seconds": elapsed}, sort_keys=True, indent=2) + "\n",
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
