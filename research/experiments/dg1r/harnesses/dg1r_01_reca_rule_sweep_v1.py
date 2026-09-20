#!/usr/bin/env python3
import argparse
import hashlib
import json
import math
import time
from pathlib import Path

import numpy as np

WIDTH = 128
INTERNAL_STEPS = 4
INJECTION_COUNT = 16
SEQ_LEN = 4096
TRAIN_START = 64
TRAIN_ROWS = 2048
TEST_START = 2560
TEST_ROWS = 1024
RIDGE_ALPHA = 1e-3
WORLD_START = 20260926010000
WORLD_COUNT = 8
RULES = {
    "ECA90": 90,
    "ECA150": 150,
    "ECA110": 110,
    "ECA22": 22,
    "ECA30": 30,
}
MIX_RULES = np.asarray([90, 150, 110, 22, 30], dtype=np.uint16)
METHODS = tuple(RULES.keys()) + ("MIXED5", "RAW32", "RANDOM512")
TASKS = ("D1", "D4", "D8", "D16", "D32", "XOR3_11", "PARITY5", "MOTIF2_12")


def eca_step_uniform(state, rule):
    left = np.roll(state, 1)
    right = np.roll(state, -1)
    idx = (left << 2) | (state << 1) | right
    return ((rule >> idx) & 1).astype(np.uint8)


def eca_step_mixed(state, rule_by_cell):
    left = np.roll(state, 1)
    right = np.roll(state, -1)
    idx = (left << 2) | (state << 1) | right
    return ((rule_by_cell >> idx) & 1).astype(np.uint8)


def run_reca_features(u, injection, rule=None, rule_by_cell=None):
    state = np.zeros(WIDTH, dtype=np.uint8)
    x = np.empty((len(u), WIDTH * INTERNAL_STEPS), dtype=np.uint8)
    snapshot = None
    for t, bit in enumerate(u):
        if bit:
            state[injection] ^= 1
        off = 0
        for _ in range(INTERNAL_STEPS):
            if rule_by_cell is None:
                state = eca_step_uniform(state, int(rule))
            else:
                state = eca_step_mixed(state, rule_by_cell)
            x[t, off:off + WIDTH] = state
            off += WIDTH
        if t == 512:
            snapshot = state.copy()
    return x, snapshot


def perturbation_profile(u, injection, snapshot, rule=None, rule_by_cell=None):
    a = snapshot.copy()
    b = snapshot.copy()
    b[64] ^= 1
    horizons = {1: None, 4: None, 8: None, 16: None}
    for h in range(1, 17):
        bit = u[512 + h]
        if bit:
            a[injection] ^= 1
            b[injection] ^= 1
        for _ in range(INTERNAL_STEPS):
            if rule_by_cell is None:
                a = eca_step_uniform(a, int(rule))
                b = eca_step_uniform(b, int(rule))
            else:
                a = eca_step_mixed(a, rule_by_cell)
                b = eca_step_mixed(b, rule_by_cell)
        if h in horizons:
            horizons[h] = float(np.mean(a != b))
    return {f"h{h}": horizons[h] for h in (1, 4, 8, 16)}


def raw32_features(u):
    x = np.zeros((len(u), 32), dtype=np.uint8)
    for d in range(1, 33):
        x[d:, d - 1] = u[:-d]
    return x


def random512_features(raw32, weights, biases):
    score = raw32.astype(np.int16) @ weights.astype(np.int16)
    score = score + biases[None, :]
    return (score > 0).astype(np.uint8)


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
    pred_labels = {}
    for j, name in enumerate(TASKS):
        yp = (pred[:, j] >= 0.5).astype(np.uint8)
        yt = targets[name][te]
        pred_labels[name] = yp
        if name == "MOTIF2_12":
            metrics[name] = balanced_accuracy(yt, yp)
        else:
            metrics[name] = float(np.mean(yp == yt))
    return metrics, pred_labels


def binary_entropy_features(x):
    p = np.mean(x, axis=0, dtype=np.float64)
    mask = (p > 0.0) & (p < 1.0)
    h = np.zeros_like(p)
    h[mask] = -(p[mask] * np.log2(p[mask]) + (1.0 - p[mask]) * np.log2(1.0 - p[mask]))
    return float(np.mean(h))


def feature_rank(x):
    dim = x.shape[1]
    rows = min(512, len(x))
    m = x[:rows].astype(np.float64)
    m -= np.mean(m, axis=0, keepdims=True)
    s = np.linalg.svd(m, compute_uv=False)
    if len(s) == 0 or s[0] == 0.0:
        rank = 0
    else:
        rank = int(np.sum(s > s[0] * 1e-8))
    return rank, float(rank / dim)


def fisher_ratio(x, y):
    xf = x.astype(np.float64)
    a = xf[y == 0]
    b = xf[y == 1]
    if len(a) == 0 or len(b) == 0:
        return 0.0
    ca = np.mean(a, axis=0)
    cb = np.mean(b, axis=0)
    between = float(np.sum((ca - cb) ** 2))
    within_a = float(np.mean(np.sum((a - ca) ** 2, axis=1)))
    within_b = float(np.mean(np.sum((b - cb) ** 2, axis=1)))
    return float(between / (0.5 * (within_a + within_b) + 1e-12))


def method_metrics(x, targets, perturb=None):
    te = slice(TEST_START, TEST_START + TEST_ROWS)
    tasks, _ = train_readouts(x, targets)
    entropy = binary_entropy_features(x[te])
    rank, rank_frac = feature_rank(x[te])
    parity_sep = fisher_ratio(x[te], targets["PARITY5"][te])
    motif_sep = fisher_ratio(x[te], targets["MOTIF2_12"][te])
    memory_score = float(np.mean([tasks["D8"], tasks["D16"], tasks["D32"]]))
    nonlinear_score = float(np.mean([tasks["XOR3_11"], tasks["PARITY5"], tasks["MOTIF2_12"]]))
    return {
        "tasks": tasks,
        "memory_score": memory_score,
        "nonlinear_score": nonlinear_score,
        "state_entropy": entropy,
        "feature_rank": int(rank),
        "feature_rank_fraction": rank_frac,
        "fisher_parity5": parity_sep,
        "fisher_motif2_12": motif_sep,
        "perturbation": perturb,
    }


def mixed_rule_assignment(rng):
    reps = WIDTH // len(MIX_RULES)
    rem = WIDTH % len(MIX_RULES)
    arr = np.concatenate((np.tile(MIX_RULES, reps), MIX_RULES[:rem])).astype(np.uint16)
    rng.shuffle(arr)
    return arr


def one_world(seed):
    rng = np.random.default_rng(np.random.PCG64(seed))
    u = rng.integers(0, 2, size=SEQ_LEN, dtype=np.uint8)
    injection = np.sort(rng.choice(WIDTH, size=INJECTION_COUNT, replace=False)).astype(np.int64)
    mixed_rules = mixed_rule_assignment(rng)
    random_weights = rng.choice(np.asarray([-1, 1], dtype=np.int8), size=(32, 512), replace=True)
    random_biases = rng.integers(-4, 5, size=512, dtype=np.int16)
    targets = build_targets(u)
    runtime = {}
    methods = {}

    for name, rule in RULES.items():
        t0 = time.perf_counter()
        x, snapshot = run_reca_features(u, injection, rule=rule)
        runtime[name] = float(time.perf_counter() - t0)
        perturb = perturbation_profile(u, injection, snapshot, rule=rule)
        methods[name] = method_metrics(x, targets, perturb=perturb)

    t0 = time.perf_counter()
    x, snapshot = run_reca_features(u, injection, rule_by_cell=mixed_rules)
    runtime["MIXED5"] = float(time.perf_counter() - t0)
    perturb = perturbation_profile(u, injection, snapshot, rule_by_cell=mixed_rules)
    methods["MIXED5"] = method_metrics(x, targets, perturb=perturb)

    t0 = time.perf_counter()
    raw = raw32_features(u)
    runtime["RAW32"] = float(time.perf_counter() - t0)
    methods["RAW32"] = method_metrics(raw, targets, perturb=None)

    t0 = time.perf_counter()
    rnd = random512_features(raw, random_weights, random_biases)
    runtime["RANDOM512"] = float(time.perf_counter() - t0)
    methods["RANDOM512"] = method_metrics(rnd, targets, perturb=None)

    return {
        "seed": int(seed),
        "injection_positions": [int(v) for v in injection],
        "mixed_rule_counts": {
            str(int(r)): int(np.sum(mixed_rules == r)) for r in MIX_RULES
        },
        "methods": methods,
    }, runtime


def q(values, p):
    return float(np.quantile(np.asarray(values, dtype=np.float64), p))


def resource_record(name):
    if name.startswith("ECA") or name == "MIXED5":
        return {
            "persistent_state_bits": 128,
            "persistent_state_bitpacked_bytes": 16,
            "readout_feature_bits": 512,
            "readout_feature_bitpacked_bytes": 64,
            "cell_updates_per_external_step": 512,
            "trainable_reservoir_parameters": 0,
            "trainable_readout_scalars_per_task": 513,
        }
    if name == "RAW32":
        return {
            "persistent_state_bits": 32,
            "persistent_state_bitpacked_bytes": 4,
            "readout_feature_bits": 32,
            "readout_feature_bitpacked_bytes": 4,
            "trainable_feature_parameters": 0,
            "trainable_readout_scalars_per_task": 33,
        }
    return {
        "persistent_state_bits": 32,
        "persistent_state_bitpacked_bytes": 4,
        "readout_feature_bits": 512,
        "readout_feature_bitpacked_bytes": 64,
        "fixed_projection_sign_bits": 32 * 512,
        "fixed_projection_biases": 512,
        "trainable_feature_parameters": 0,
        "trainable_readout_scalars_per_task": 513,
    }


def summarize(rows):
    out = {"worlds": len(rows), "methods": {}}
    for name in METHODS:
        mr = [r["methods"][name] for r in rows]
        task_summary = {}
        for task in TASKS:
            vals = [x["tasks"][task] for x in mr]
            task_summary[task] = {"median": q(vals, 0.5), "p10": q(vals, 0.10)}
        memory_vals = [x["memory_score"] for x in mr]
        nonlinear_vals = [x["nonlinear_score"] for x in mr]
        entropy_vals = [x["state_entropy"] for x in mr]
        rank_vals = [x["feature_rank"] for x in mr]
        rank_frac_vals = [x["feature_rank_fraction"] for x in mr]
        parity_sep_vals = [x["fisher_parity5"] for x in mr]
        motif_sep_vals = [x["fisher_motif2_12"] for x in mr]

        summary = {
            "tasks": task_summary,
            "memory_score": {"median": q(memory_vals, 0.5), "p10": q(memory_vals, 0.10)},
            "nonlinear_score": {"median": q(nonlinear_vals, 0.5), "p10": q(nonlinear_vals, 0.10)},
            "state_entropy": {"median": q(entropy_vals, 0.5), "p10": q(entropy_vals, 0.10)},
            "feature_rank": {"median": q(rank_vals, 0.5), "p10": q(rank_vals, 0.10)},
            "feature_rank_fraction": {"median": q(rank_frac_vals, 0.5), "p10": q(rank_frac_vals, 0.10)},
            "fisher_parity5": {"median": q(parity_sep_vals, 0.5)},
            "fisher_motif2_12": {"median": q(motif_sep_vals, 0.5)},
            "resources": resource_record(name),
        }

        if name.startswith("ECA") or name == "MIXED5":
            for h in (1, 4, 8, 16):
                vals = [x["perturbation"][f"h{h}"] for x in mr]
                summary.setdefault("perturbation", {})[f"h{h}"] = {
                    "median": q(vals, 0.5),
                    "p10": q(vals, 0.10),
                }
            memory_capable = (
                summary["memory_score"]["median"] >= 0.70
                and summary["tasks"]["D16"]["median"] >= 0.70
            )
            nonlinear_hits = sum(
                summary["tasks"][task]["median"] >= 0.60
                for task in ("XOR3_11", "PARITY5", "MOTIF2_12")
            )
            nonlinear_capable = (
                summary["nonlinear_score"]["median"] >= 0.60
                and nonlinear_hits >= 2
            )
            h16 = summary["perturbation"]["h16"]["median"]
            ent = summary["state_entropy"]["median"]
            dynamically_balanced = 0.20 <= ent <= 0.95 and 0.01 <= h16 <= 0.75
            summary["classification"] = {
                "memory_capable": bool(memory_capable),
                "nonlinear_capable": bool(nonlinear_capable),
                "dynamically_balanced": bool(dynamically_balanced),
                "temporal_substrate_candidate": bool(memory_capable and nonlinear_capable and dynamically_balanced),
            }
        out["methods"][name] = summary

    candidates = [
        name for name in tuple(RULES.keys()) + ("MIXED5",)
        if out["methods"][name]["classification"]["temporal_substrate_candidate"]
    ]
    out["temporal_substrate_candidates"] = candidates
    out["candidate_count"] = len(candidates)
    return out


def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def run():
    rows = []
    runtime_rows = []
    for i in range(WORLD_COUNT):
        row, runtime = one_world(WORLD_START + i)
        rows.append(row)
        runtime_rows.append({"seed": row["seed"], "feature_generation_seconds": runtime})
    canonical = {
        "schema": "yggdrasil.dg1r-01-reca-rule-sweep.v1",
        "rows": rows,
        "summary": summarize(rows),
        "worlds": len(rows),
        "seed_start": WORLD_START,
        "seed_end": WORLD_START + WORLD_COUNT - 1,
    }
    runtime = {
        "schema": "yggdrasil.dg1r-01-runtime-sidecar.v1",
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
        Path(args.runtime_out).write_text(json.dumps(runtime, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    print(encode({
        "output": args.out,
        "sha256": digest,
        "summary": obj["summary"],
        "worlds": obj["worlds"],
    }))


if __name__ == "__main__":
    main()
