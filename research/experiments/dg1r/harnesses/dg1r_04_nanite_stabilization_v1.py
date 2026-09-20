#!/usr/bin/env python3
import argparse
import hashlib
import importlib.util
import json
import time
from pathlib import Path

import numpy as np

BASE_NAME = "dg1r_03_multitimescale_v1.py"
WORLD_START = 20260926040000
WORLD_COUNT = 8
WORKERS = 112
CONTROLLERS = 16
SECTOR = 7
FAST_TICKS = (1, 2, 3, 4)
SLOW_TICKS = (4,)
RECA_METHODS = (
    "FAST128_MIXED4",
    "SLOW128_MIXED1",
    "INERT112_16_FAST4",
    "NANITE112_16_FAST4_T50",
    "NANITE112_16_FAST4_T35",
    "NANITE112_16_SLOW1_T50",
)
METHODS = RECA_METHODS + ("RAW32", "RANDOM512")


def load_base():
    path = Path(__file__).resolve().parent / BASE_NAME
    spec = importlib.util.spec_from_file_location("dg1r03_base", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def worker_mapped_positions(rng):
    return np.asarray([j * 14 + int(rng.integers(0, 14)) for j in range(8)], dtype=np.int64)


def nanite_config(name):
    if name == "INERT112_16_FAST4":
        return FAST_TICKS, None
    if name == "NANITE112_16_FAST4_T50":
        return FAST_TICKS, 0.50
    if name == "NANITE112_16_FAST4_T35":
        return FAST_TICKS, 0.35
    if name == "NANITE112_16_SLOW1_T50":
        return SLOW_TICKS, 0.50
    raise ValueError(name)


def apply_worker_update(base, workers, controllers, worker_rules, threshold, stats=None):
    proposed = base.eca_step_mixed(workers, worker_rules)
    before = workers.copy()
    if threshold is None:
        workers[:] = proposed
        controllers.fill(0)
        if stats is not None:
            stats["proposed_flips"] += int(np.sum(proposed != before))
            stats["realized_flips"] += int(np.sum(workers != before))
            stats["worker_bit_decisions"] += WORKERS
        return

    total_proposed = 0
    total_realized = 0
    for j in range(CONTROLLERS):
        s = j * SECTOR
        e = s + SECTOR
        flips = int(np.sum(proposed[s:e] != before[s:e]))
        total_proposed += flips
        veto = (flips / SECTOR) > threshold
        controllers[j] = np.uint8(1 if veto else 0)
        if not veto:
            workers[s:e] = proposed[s:e]
            total_realized += flips
        if stats is not None:
            stats["sector_decisions"] += 1
            stats["veto_decisions"] += int(veto)
    if stats is not None:
        stats["proposed_flips"] += total_proposed
        stats["realized_flips"] += total_realized
        stats["worker_bit_decisions"] += WORKERS


def evolve_nanite_external(base, workers, controllers, bit, mapped, worker_rules, ticks, threshold, record=None, stats=None):
    workers[mapped] = np.uint8(bit)
    for micro in range(1, 5):
        if micro in ticks:
            apply_worker_update(base, workers, controllers, worker_rules, threshold, stats=stats)
        if record is not None:
            off = (micro - 1) * 128
            record[off:off + WORKERS] = workers
            record[off + WORKERS:off + 128] = controllers


def run_nanite_features(base, u, mapped, worker_rules, name):
    ticks, threshold = nanite_config(name)
    workers = np.zeros(WORKERS, dtype=np.uint8)
    controllers = np.zeros(CONTROLLERS, dtype=np.uint8)
    x = np.empty((len(u), 512), dtype=np.uint8)
    stats = {
        "sector_decisions": 0,
        "veto_decisions": 0,
        "proposed_flips": 0,
        "realized_flips": 0,
        "worker_bit_decisions": 0,
    }
    snapshot = None
    for t, bit in enumerate(u):
        evolve_nanite_external(
            base, workers, controllers, int(bit), mapped, worker_rules,
            ticks, threshold, record=x[t], stats=stats,
        )
        if t == 512:
            snapshot = np.concatenate((workers.copy(), controllers.copy()))
    telemetry = {
        "veto_fraction": float(stats["veto_decisions"] / stats["sector_decisions"]) if stats["sector_decisions"] else 0.0,
        "proposed_worker_change_fraction": float(stats["proposed_flips"] / stats["worker_bit_decisions"]) if stats["worker_bit_decisions"] else 0.0,
        "realized_worker_change_fraction": float(stats["realized_flips"] / stats["worker_bit_decisions"]) if stats["worker_bit_decisions"] else 0.0,
        "sector_decisions": int(stats["sector_decisions"]),
        "veto_decisions": int(stats["veto_decisions"]),
    }
    return x, snapshot, telemetry


def perturbation_nanite(base, u, mapped, worker_rules, name, snapshot):
    ticks, threshold = nanite_config(name)
    aw = snapshot[:WORKERS].copy()
    ac = snapshot[WORKERS:].copy()
    bw = aw.copy()
    bc = ac.copy()
    bw[98] ^= 1
    out = {}
    for h in range(1, 17):
        bit = int(u[512 + h])
        evolve_nanite_external(base, aw, ac, bit, mapped, worker_rules, ticks, threshold)
        evolve_nanite_external(base, bw, bc, bit, mapped, worker_rules, ticks, threshold)
        if h in (1, 4, 8, 16):
            a = np.concatenate((aw, ac))
            b = np.concatenate((bw, bc))
            out[f"h{h}"] = float(np.mean(a != b))
    return out


def resource_record(base, name):
    if name in ("FAST128_MIXED4", "SLOW128_MIXED1"):
        return base.resource_record(name)
    if name == "INERT112_16_FAST4":
        return {
            "persistent_state_bits": 128,
            "persistent_state_bitpacked_bytes": 16,
            "worker_state_bits": 112,
            "controller_state_bits": 16,
            "readout_feature_bits": 512,
            "readout_feature_bitpacked_bytes": 64,
            "worker_ca_updates_per_external_step": 448,
            "stabilizer_decisions_per_external_step": 0,
            "mapped_overwrite_writes_per_external_step": 8,
            "trainable_reservoir_parameters": 0,
            "trainable_readout_scalars_per_task": 513,
        }
    slow = name == "NANITE112_16_SLOW1_T50"
    return {
        "persistent_state_bits": 128,
        "persistent_state_bitpacked_bytes": 16,
        "worker_state_bits": 112,
        "controller_state_bits": 16,
        "readout_feature_bits": 512,
        "readout_feature_bitpacked_bytes": 64,
        "worker_ca_updates_per_external_step": 112 if slow else 448,
        "stabilizer_decisions_per_external_step": 16 if slow else 64,
        "mapped_overwrite_writes_per_external_step": 8,
        "trainable_reservoir_parameters": 0,
        "trainable_readout_scalars_per_task": 513,
    }


def one_world(base, seed):
    rng = np.random.default_rng(np.random.PCG64(seed))
    u = rng.integers(0, 2, size=base.SEQ_LEN, dtype=np.uint8)
    mapped = worker_mapped_positions(rng)
    mixed128 = base.mixed_rule_assignment(rng)
    worker_rules = mixed128[:WORKERS].copy()
    random_weights = rng.choice(np.asarray([-1, 1], dtype=np.int8), size=(32, 512), replace=True)
    random_biases = rng.integers(-4, 5, size=512, dtype=np.int16)
    targets = base.build_targets(u)
    methods = {}
    runtime = {}

    for name in ("FAST128_MIXED4", "SLOW128_MIXED1"):
        t0 = time.perf_counter()
        x, snapshot = base.run_reca_features(u, mapped, mixed128, name)
        runtime[name] = float(time.perf_counter() - t0)
        perturb = base.perturbation_profile(u, mapped, mixed128, name, snapshot)
        m = base.method_metrics(x, targets, perturb=perturb)
        m["resources"] = resource_record(base, name)
        m["stabilizer_telemetry"] = None
        methods[name] = m

    for name in (
        "INERT112_16_FAST4",
        "NANITE112_16_FAST4_T50",
        "NANITE112_16_FAST4_T35",
        "NANITE112_16_SLOW1_T50",
    ):
        t0 = time.perf_counter()
        x, snapshot, telemetry = run_nanite_features(base, u, mapped, worker_rules, name)
        runtime[name] = float(time.perf_counter() - t0)
        perturb = perturbation_nanite(base, u, mapped, worker_rules, name, snapshot)
        m = base.method_metrics(x, targets, perturb=perturb)
        m["resources"] = resource_record(base, name)
        m["stabilizer_telemetry"] = telemetry
        methods[name] = m

    t0 = time.perf_counter()
    raw = base.raw32_features(u)
    runtime["RAW32"] = float(time.perf_counter() - t0)
    methods["RAW32"] = base.method_metrics(raw, targets, perturb=None)
    methods["RAW32"]["resources"] = base.resource_record("RAW32")
    methods["RAW32"]["stabilizer_telemetry"] = None

    t0 = time.perf_counter()
    rnd = base.random512_features(raw, random_weights, random_biases)
    runtime["RANDOM512"] = float(time.perf_counter() - t0)
    methods["RANDOM512"] = base.method_metrics(rnd, targets, perturb=None)
    methods["RANDOM512"]["resources"] = base.resource_record("RANDOM512")
    methods["RANDOM512"]["stabilizer_telemetry"] = None

    return {
        "seed": int(seed),
        "mapped_worker_positions": [int(v) for v in mapped],
        "worker_rule_counts": {str(int(r)): int(np.sum(worker_rules == r)) for r in base.MIX_RULES},
        "methods": methods,
    }, runtime


def q(values, p):
    return float(np.quantile(np.asarray(values, dtype=np.float64), p))


def summarize_method(base, rows, name):
    mr = [r["methods"][name] for r in rows]
    task_summary = {}
    for task in base.TASKS:
        vals = [x["tasks"][task] for x in mr]
        task_summary[task] = {"median": q(vals, 0.5), "p10": q(vals, 0.10)}
    s = {
        "tasks": task_summary,
        "memory_score": {"median": q([x["memory_score"] for x in mr], 0.5), "p10": q([x["memory_score"] for x in mr], 0.10)},
        "nonlinear_score": {"median": q([x["nonlinear_score"] for x in mr], 0.5), "p10": q([x["nonlinear_score"] for x in mr], 0.10)},
        "state_entropy": {"median": q([x["state_entropy"] for x in mr], 0.5), "p10": q([x["state_entropy"] for x in mr], 0.10)},
        "feature_rank": {"median": q([x["feature_rank"] for x in mr], 0.5), "p10": q([x["feature_rank"] for x in mr], 0.10)},
        "feature_rank_fraction": {"median": q([x["feature_rank_fraction"] for x in mr], 0.5), "p10": q([x["feature_rank_fraction"] for x in mr], 0.10)},
        "fisher_parity5": {"median": q([x["fisher_parity5"] for x in mr], 0.5)},
        "fisher_motif2_12": {"median": q([x["fisher_motif2_12"] for x in mr], 0.5)},
        "resources": mr[0]["resources"],
    }
    if name in RECA_METHODS:
        s["perturbation"] = {}
        for h in (1, 4, 8, 16):
            vals = [x["perturbation"][f"h{h}"] for x in mr]
            s["perturbation"][f"h{h}"] = {"median": q(vals, 0.5), "p10": q(vals, 0.10)}
        memory_capable = s["memory_score"]["median"] >= 0.70 and s["tasks"]["D16"]["median"] >= 0.70
        nonlinear_hits = sum(s["tasks"][task]["median"] >= 0.60 for task in ("XOR3_11", "PARITY5", "MOTIF2_12"))
        nonlinear_capable = s["nonlinear_score"]["median"] >= 0.60 and nonlinear_hits >= 2
        ent = s["state_entropy"]["median"]
        h16 = s["perturbation"]["h16"]["median"]
        balanced = 0.20 <= ent <= 0.95 and 0.01 <= h16 <= 0.75
        s["classification"] = {
            "memory_capable": bool(memory_capable),
            "nonlinear_capable": bool(nonlinear_capable),
            "dynamically_balanced": bool(balanced),
            "temporal_substrate_candidate": bool(memory_capable and nonlinear_capable and balanced),
        }
    tele = [x["stabilizer_telemetry"] for x in mr if x["stabilizer_telemetry"] is not None]
    if tele:
        s["stabilizer_telemetry"] = {
            "veto_fraction": {"median": q([x["veto_fraction"] for x in tele], 0.5), "p10": q([x["veto_fraction"] for x in tele], 0.10)},
            "proposed_worker_change_fraction": {"median": q([x["proposed_worker_change_fraction"] for x in tele], 0.5)},
            "realized_worker_change_fraction": {"median": q([x["realized_worker_change_fraction"] for x in tele], 0.5)},
        }
        veto_med = s["stabilizer_telemetry"]["veto_fraction"]["median"]
        s["overstabilized"] = bool(
            veto_med >= 0.75 and (
                s["state_entropy"]["median"] < 0.20
                or s["feature_rank_fraction"]["median"] < 0.15
            )
        )
    else:
        s["stabilizer_telemetry"] = None
        s["overstabilized"] = False
    return s


def paired_delta(rows, name, ref):
    out = {}
    for key in ("D1", "D4", "D8", "D16", "D32"):
        vals = [r["methods"][name]["tasks"][key] - r["methods"][ref]["tasks"][key] for r in rows]
        out[key] = {"median": q(vals, 0.5), "p10": q(vals, 0.10)}
    for key in ("memory_score", "nonlinear_score"):
        vals = [r["methods"][name][key] - r["methods"][ref][key] for r in rows]
        out[key] = {"median": q(vals, 0.5), "p10": q(vals, 0.10)}
    return out


def summarize(base, rows):
    out = {"worlds": len(rows), "methods": {}, "relative_to_inert": {}, "relative_to_slow128": {}}
    for name in METHODS:
        out["methods"][name] = summarize_method(base, rows, name)
    fast_nanites = ("NANITE112_16_FAST4_T50", "NANITE112_16_FAST4_T35")
    all_nanites = fast_nanites + ("NANITE112_16_SLOW1_T50",)
    for name in fast_nanites:
        out["relative_to_inert"][name] = paired_delta(rows, name, "INERT112_16_FAST4")
    for name in all_nanites:
        out["relative_to_slow128"][name] = paired_delta(rows, name, "SLOW128_MIXED1")

    active_signal = False
    for name in fast_nanites:
        d = out["relative_to_inert"][name]
        long_gain = d["D16"]["median"] >= 0.10 or d["D32"]["median"] >= 0.10
        nonlinear_ok = d["nonlinear_score"]["median"] >= -0.05
        if long_gain and nonlinear_ok:
            active_signal = True
            break

    passive_signal = False
    for name in all_nanites:
        d = out["relative_to_slow128"][name]
        long_gain = d["D16"]["median"] >= 0.10 or d["D32"]["median"] >= 0.10
        nonlinear_ok = d["nonlinear_score"]["median"] >= -0.05
        if long_gain and nonlinear_ok:
            passive_signal = True
            break

    nanite_recovery = any(out["methods"][name]["classification"]["memory_capable"] for name in all_nanites)
    nanite_recovery = nanite_recovery and not out["methods"]["INERT112_16_FAST4"]["classification"]["memory_capable"] and not out["methods"]["SLOW128_MIXED1"]["classification"]["memory_capable"]

    out["active_stabilization_signal"] = bool(active_signal)
    out["passive_comparison_signal"] = bool(passive_signal)
    out["nanite_memory_recovery"] = bool(nanite_recovery)
    out["temporal_substrate_candidates"] = [
        name for name in RECA_METHODS
        if out["methods"][name]["classification"]["temporal_substrate_candidate"]
    ]
    return out


def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def run():
    base = load_base()
    rows = []
    runtime_rows = []
    for i in range(WORLD_COUNT):
        row, runtime = one_world(base, WORLD_START + i)
        rows.append(row)
        runtime_rows.append({"seed": row["seed"], "feature_generation_seconds": runtime})
    canonical = {
        "schema": "yggdrasil.dg1r-04-software-nanite-stabilization.v1",
        "rows": rows,
        "summary": summarize(base, rows),
        "worlds": len(rows),
        "seed_start": WORLD_START,
        "seed_end": WORLD_START + WORLD_COUNT - 1,
    }
    runtime = {"schema": "yggdrasil.dg1r-04-runtime-sidecar.v1", "rows": runtime_rows}
    return canonical, runtime


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--runtime-out")
    args = ap.parse_args()
    obj, runtime = run()
    raw = (encode(obj) + "\n").encode("utf-8")
    Path(args.out).write_bytes(raw)
    if args.runtime_out:
        Path(args.runtime_out).write_text(json.dumps(runtime, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    print(encode({"output": args.out, "sha256": digest, "summary": obj["summary"], "worlds": obj["worlds"]}))


if __name__ == "__main__":
    main()
