#!/usr/bin/env python3
import argparse
import hashlib
import importlib.util
import json
import time
from pathlib import Path

import numpy as np

BASE_NAME = "dg1r_01_reca_rule_sweep_v1.py"
WORLD_START = 20260926020000
WORLD_COUNT = 8
R = 8
LD = 16
I = 4
RULES = {
    "90": 90,
    "150": 150,
    "182": 182,
    "22": 22,
}
METHODS = (
    "OW90", "XR90",
    "OW150", "XR150",
    "OW182", "XR182",
    "OW22", "XR22",
    "OW_MIXED5", "XR_MIXED5",
    "RAW32", "RANDOM512",
)


def load_base():
    path = Path(__file__).resolve().parent / BASE_NAME
    spec = importlib.util.spec_from_file_location("dg1r01_base", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def mapped_positions(rng):
    return np.asarray([
        j * LD + int(rng.integers(0, LD))
        for j in range(R)
    ], dtype=np.int64)


def apply_input(state, mapped, bit, policy):
    if policy == "overwrite":
        state[mapped] = np.uint8(bit)
    elif policy == "xor":
        if bit:
            state[mapped] ^= 1
    else:
        raise ValueError(policy)


def run_reca_features(base, u, mapped, policy, rule=None, rule_by_cell=None):
    state = np.zeros(base.WIDTH, dtype=np.uint8)
    x = np.empty((len(u), base.WIDTH * I), dtype=np.uint8)
    snapshot = None
    for t, bit in enumerate(u):
        apply_input(state, mapped, int(bit), policy)
        off = 0
        for _ in range(I):
            if rule_by_cell is None:
                state = base.eca_step_uniform(state, int(rule))
            else:
                state = base.eca_step_mixed(state, rule_by_cell)
            x[t, off:off + base.WIDTH] = state
            off += base.WIDTH
        if t == 512:
            snapshot = state.copy()
    return x, snapshot


def perturbation_profile(base, u, mapped, snapshot, policy, rule=None, rule_by_cell=None):
    a = snapshot.copy()
    b = snapshot.copy()
    b[64] ^= 1
    horizons = {1: None, 4: None, 8: None, 16: None}
    for h in range(1, 17):
        bit = int(u[512 + h])
        apply_input(a, mapped, bit, policy)
        apply_input(b, mapped, bit, policy)
        for _ in range(I):
            if rule_by_cell is None:
                a = base.eca_step_uniform(a, int(rule))
                b = base.eca_step_uniform(b, int(rule))
            else:
                a = base.eca_step_mixed(a, rule_by_cell)
                b = base.eca_step_mixed(b, rule_by_cell)
        if h in horizons:
            horizons[h] = float(np.mean(a != b))
    return {f"h{h}": horizons[h] for h in (1, 4, 8, 16)}


def reca_resource(policy):
    return {
        "persistent_state_bits": 128,
        "persistent_state_bitpacked_bytes": 16,
        "readout_feature_bits": 512,
        "readout_feature_bitpacked_bytes": 64,
        "cell_updates_per_external_step": 512,
        "mapped_positions": R,
        "mapping_compartments": R,
        "diffuse_length": LD,
        "recurrence_policy": policy,
        "trainable_reservoir_parameters": 0,
        "trainable_readout_scalars_per_task": 513,
    }


def one_world(base, seed):
    rng = np.random.default_rng(np.random.PCG64(seed))
    u = rng.integers(0, 2, size=base.SEQ_LEN, dtype=np.uint8)
    mapped = mapped_positions(rng)
    mixed_rules = base.mixed_rule_assignment(rng)
    random_weights = rng.choice(
        np.asarray([-1, 1], dtype=np.int8),
        size=(32, 512),
        replace=True,
    )
    random_biases = rng.integers(-4, 5, size=512, dtype=np.int16)
    targets = base.build_targets(u)
    methods = {}
    runtime = {}

    for short, rule in RULES.items():
        for prefix, policy in (("OW", "overwrite"), ("XR", "xor")):
            name = prefix + short
            t0 = time.perf_counter()
            x, snapshot = run_reca_features(
                base, u, mapped, policy, rule=rule
            )
            runtime[name] = float(time.perf_counter() - t0)
            perturb = perturbation_profile(
                base, u, mapped, snapshot, policy, rule=rule
            )
            m = base.method_metrics(x, targets, perturb=perturb)
            m["resources"] = reca_resource(policy)
            methods[name] = m

    for prefix, policy in (("OW", "overwrite"), ("XR", "xor")):
        name = prefix + "_MIXED5"
        t0 = time.perf_counter()
        x, snapshot = run_reca_features(
            base, u, mapped, policy, rule_by_cell=mixed_rules
        )
        runtime[name] = float(time.perf_counter() - t0)
        perturb = perturbation_profile(
            base, u, mapped, snapshot, policy, rule_by_cell=mixed_rules
        )
        m = base.method_metrics(x, targets, perturb=perturb)
        m["resources"] = reca_resource(policy)
        methods[name] = m

    t0 = time.perf_counter()
    raw = base.raw32_features(u)
    runtime["RAW32"] = float(time.perf_counter() - t0)
    methods["RAW32"] = base.method_metrics(raw, targets, perturb=None)
    methods["RAW32"]["resources"] = base.resource_record("RAW32")

    t0 = time.perf_counter()
    rnd = base.random512_features(raw, random_weights, random_biases)
    runtime["RANDOM512"] = float(time.perf_counter() - t0)
    methods["RANDOM512"] = base.method_metrics(rnd, targets, perturb=None)
    methods["RANDOM512"]["resources"] = base.resource_record("RANDOM512")

    return {
        "seed": int(seed),
        "mapped_positions": [int(v) for v in mapped],
        "mixed_rule_counts": {
            str(int(r)): int(np.sum(mixed_rules == r))
            for r in base.MIX_RULES
        },
        "methods": methods,
    }, runtime


def q(values, p):
    return float(np.quantile(np.asarray(values, dtype=np.float64), p))


def summarize_method(rows, name, is_reca):
    mr = [r["methods"][name] for r in rows]
    task_summary = {}
    for task in rows[0]["methods"][name]["tasks"]:
        vals = [x["tasks"][task] for x in mr]
        task_summary[task] = {"median": q(vals, 0.5), "p10": q(vals, 0.10)}
    s = {
        "tasks": task_summary,
        "memory_score": {
            "median": q([x["memory_score"] for x in mr], 0.5),
            "p10": q([x["memory_score"] for x in mr], 0.10),
        },
        "nonlinear_score": {
            "median": q([x["nonlinear_score"] for x in mr], 0.5),
            "p10": q([x["nonlinear_score"] for x in mr], 0.10),
        },
        "state_entropy": {
            "median": q([x["state_entropy"] for x in mr], 0.5),
            "p10": q([x["state_entropy"] for x in mr], 0.10),
        },
        "feature_rank": {
            "median": q([x["feature_rank"] for x in mr], 0.5),
            "p10": q([x["feature_rank"] for x in mr], 0.10),
        },
        "feature_rank_fraction": {
            "median": q([x["feature_rank_fraction"] for x in mr], 0.5),
            "p10": q([x["feature_rank_fraction"] for x in mr], 0.10),
        },
        "fisher_parity5": {"median": q([x["fisher_parity5"] for x in mr], 0.5)},
        "fisher_motif2_12": {"median": q([x["fisher_motif2_12"] for x in mr], 0.5)},
        "resources": mr[0]["resources"],
    }
    if is_reca:
        s["perturbation"] = {}
        for h in (1, 4, 8, 16):
            vals = [x["perturbation"][f"h{h}"] for x in mr]
            s["perturbation"][f"h{h}"] = {
                "median": q(vals, 0.5),
                "p10": q(vals, 0.10),
            }
        memory_capable = (
            s["memory_score"]["median"] >= 0.70
            and s["tasks"]["D16"]["median"] >= 0.70
        )
        nonlinear_hits = sum(
            s["tasks"][task]["median"] >= 0.60
            for task in ("XOR3_11", "PARITY5", "MOTIF2_12")
        )
        nonlinear_capable = (
            s["nonlinear_score"]["median"] >= 0.60
            and nonlinear_hits >= 2
        )
        ent = s["state_entropy"]["median"]
        h16 = s["perturbation"]["h16"]["median"]
        balanced = 0.20 <= ent <= 0.95 and 0.01 <= h16 <= 0.75
        s["classification"] = {
            "memory_capable": bool(memory_capable),
            "nonlinear_capable": bool(nonlinear_capable),
            "dynamically_balanced": bool(balanced),
            "temporal_substrate_candidate": bool(memory_capable and nonlinear_capable and balanced),
        }
    return s


def paired_delta(rows, ow, xr):
    keys = ("D1", "D8", "D16", "D32")
    out = {}
    for key in keys:
        vals = [r["methods"][ow]["tasks"][key] - r["methods"][xr]["tasks"][key] for r in rows]
        out[key] = {"median": q(vals, 0.5), "p10": q(vals, 0.10)}
    for key in ("memory_score", "nonlinear_score", "state_entropy"):
        vals = [r["methods"][ow][key] - r["methods"][xr][key] for r in rows]
        out[key] = {"median": q(vals, 0.5), "p10": q(vals, 0.10)}
    vals = [
        r["methods"][ow]["perturbation"]["h16"]
        - r["methods"][xr]["perturbation"]["h16"]
        for r in rows
    ]
    out["perturbation_h16"] = {"median": q(vals, 0.5), "p10": q(vals, 0.10)}
    return out


def summarize(rows):
    out = {"worlds": len(rows), "methods": {}, "recurrence_effect": {}}
    for name in METHODS:
        out["methods"][name] = summarize_method(
            rows, name, name not in ("RAW32", "RANDOM512")
        )

    pairs = (
        ("90", "OW90", "XR90"),
        ("150", "OW150", "XR150"),
        ("182", "OW182", "XR182"),
        ("22", "OW22", "XR22"),
        ("MIXED5", "OW_MIXED5", "XR_MIXED5"),
    )
    for label, ow, xr in pairs:
        out["recurrence_effect"][label] = paired_delta(rows, ow, xr)

    recovery = any(
        out["methods"][ow]["classification"]["memory_capable"]
        and not out["methods"][xr]["classification"]["memory_capable"]
        for _, ow, xr in pairs
    )
    strong = any(
        out["methods"][ow]["classification"]["temporal_substrate_candidate"]
        and not out["methods"][xr]["classification"]["temporal_substrate_candidate"]
        for _, ow, xr in pairs
    )
    out["overwrite_recovery_signal"] = bool(recovery)
    out["strong_recurrence_signal"] = bool(strong)
    out["temporal_substrate_candidates"] = [
        name for name in METHODS
        if name not in ("RAW32", "RANDOM512")
        and out["methods"][name]["classification"]["temporal_substrate_candidate"]
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
        "schema": "yggdrasil.dg1r-02-recurrent-overwrite-fidelity.v1",
        "rows": rows,
        "summary": summarize(rows),
        "worlds": len(rows),
        "seed_start": WORLD_START,
        "seed_end": WORLD_START + WORLD_COUNT - 1,
        "R": R,
        "Ld": LD,
        "I": I,
    }
    runtime = {
        "schema": "yggdrasil.dg1r-02-runtime-sidecar.v1",
        "rows": runtime_rows,
    }
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
        Path(args.runtime_out).write_text(
            json.dumps(runtime, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
    digest = hashlib.sha256(raw).hexdigest()
    print(encode({
        "output": args.out,
        "sha256": digest,
        "summary": obj["summary"],
        "worlds": obj["worlds"],
    }))


if __name__ == "__main__":
    main()
