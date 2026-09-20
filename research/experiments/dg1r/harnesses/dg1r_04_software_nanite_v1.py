#!/usr/bin/env python3
import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np

WIDTH = 128
MICROTICKS = 4
SEQ_LEN = 4096
TRAIN_START = 64
TRAIN_ROWS = 2048
TEST_START = 2560
TEST_ROWS = 1024
RIDGE_ALPHA = 1e-3
WORLD_START = 20260926040000
WORLD_COUNT = 8
MIX_RULES = np.asarray([90, 150, 110, 22, 30], dtype=np.uint16)
TASKS = ("D1", "D4", "D8", "D16", "D32", "XOR3_11", "PARITY5", "MOTIF2_12")
RECA_METHODS = (
    "SLOW128_MIXED1",
    "N16_H5",
    "N16_H6",
    "N16_H6_DAMP",
    "N16_H6_REPAIR",
)
METHODS = RECA_METHODS + ("RAW32", "RANDOM512")
NANITE_SITES = np.arange(7, WIDTH, 8, dtype=np.int64)
WORKER_MASK = np.ones(WIDTH, dtype=bool)
WORKER_MASK[NANITE_SITES] = False
WORKER_SITES = np.flatnonzero(WORKER_MASK)
BLOCKS = tuple((start, start + 7) for start in range(0, WIDTH, 8))
ELIGIBLE_INPUT_OFFSETS = np.asarray(
    [i for i in range(16) if i not in (7, 15)],
    dtype=np.int64,
)


def eca_step_mixed(state, rules):
    left = np.roll(state, 1)
    right = np.roll(state, -1)
    idx = (left << 2) | (state << 1) | right
    return ((rules >> idx) & 1).astype(np.uint8)


def mixed_rule_assignment(rng):
    reps = WIDTH // len(MIX_RULES)
    rem = WIDTH % len(MIX_RULES)
    arr = np.concatenate((np.tile(MIX_RULES, reps), MIX_RULES[:rem])).astype(np.uint16)
    rng.shuffle(arr)
    return arr


def mapped_positions(rng):
    out = []
    for j in range(8):
        off = int(rng.choice(ELIGIBLE_INPUT_OFFSETS))
        out.append(j * 16 + off)
    return np.asarray(out, dtype=np.int64)


def nanite_threshold(method):
    if method == "N16_H5":
        return 5
    if method in ("N16_H6", "N16_H6_DAMP", "N16_H6_REPAIR"):
        return 6
    return None


def init_telemetry():
    return {
        "nanite_bit_changes": 0,
        "damp_suppressed_transitions": 0,
        "repair_attempts": 0,
        "repair_state_changes": 0,
        "prev_nanite_bits": np.zeros(len(NANITE_SITES), dtype=np.uint8),
        "nanite_run_lengths": np.zeros(len(NANITE_SITES), dtype=np.int64),
        "completed_run_lengths": [],
    }


def update_run_telemetry(state, telemetry):
    now = state[NANITE_SITES].copy()
    prev = telemetry["prev_nanite_bits"]
    runs = telemetry["nanite_run_lengths"]
    for i in range(len(now)):
        if now[i] != prev[i]:
            telemetry["nanite_bit_changes"] += 1
            if runs[i] > 0:
                telemetry["completed_run_lengths"].append(int(runs[i]))
            runs[i] = 1
        else:
            runs[i] += 1
    telemetry["prev_nanite_bits"] = now


def finalize_telemetry(telemetry):
    runs = list(telemetry["completed_run_lengths"])
    runs.extend(int(v) for v in telemetry["nanite_run_lengths"] if v > 0)
    mean_run = float(np.mean(runs)) if runs else 0.0
    median_run = float(np.median(runs)) if runs else 0.0
    return {
        "nanite_bit_changes": int(telemetry["nanite_bit_changes"]),
        "nanite_bit_changes_per_external_step": float(
            telemetry["nanite_bit_changes"] / SEQ_LEN
        ),
        "nanite_bit_changes_per_nanite_step": float(
            telemetry["nanite_bit_changes"] / (SEQ_LEN * len(NANITE_SITES))
        ),
        "damp_suppressed_transitions": int(
            telemetry["damp_suppressed_transitions"]
        ),
        "damp_suppression_rate_per_worker_evolution": float(
            telemetry["damp_suppressed_transitions"]
            / (SEQ_LEN * len(WORKER_SITES))
        ),
        "repair_attempts": int(telemetry["repair_attempts"]),
        "repair_state_changes": int(telemetry["repair_state_changes"]),
        "repair_state_changes_per_external_step": float(
            telemetry["repair_state_changes"] / SEQ_LEN
        ),
        "nanite_run_length_mean": mean_run,
        "nanite_run_length_median": median_run,
    }


def apply_hysteresis(state, threshold):
    old = state[NANITE_SITES].copy()
    new = old.copy()
    for bi, (start, nano) in enumerate(BLOCKS):
        ones = int(np.sum(state[start:nano]))
        if threshold == 5:
            if ones >= 5:
                new[bi] = 1
            elif ones <= 2:
                new[bi] = 0
        else:
            if ones >= 6:
                new[bi] = 1
            elif ones <= 1:
                new[bi] = 0
    state[NANITE_SITES] = new


def nanite_worker_update(state, mixed_rules, method, telemetry=None):
    candidate = eca_step_mixed(state, mixed_rules)

    if method == "N16_H6_DAMP":
        for start, nano in BLOCKS:
            nbit = state[nano]
            workers = np.arange(start, nano, dtype=np.int64)
            matches = state[workers] == nbit
            if int(np.sum(matches)) >= 5:
                suppress = matches & (candidate[workers] != nbit)
                if telemetry is not None:
                    telemetry["damp_suppressed_transitions"] += int(
                        np.sum(suppress)
                    )
                candidate[workers[suppress]] = state[workers[suppress]]

    state[WORKER_SITES] = candidate[WORKER_SITES]

    threshold = nanite_threshold(method)
    apply_hysteresis(state, threshold)

    if method == "N16_H6_REPAIR":
        for start, nano in BLOCKS:
            nbit = state[nano]
            workers = np.arange(start, nano, dtype=np.int64)
            disagreement = int(np.sum(state[workers] != nbit))
            if disagreement in (4, 5):
                center = start + 3
                if telemetry is not None:
                    telemetry["repair_attempts"] += 1
                if state[center] != nbit:
                    state[center] = nbit
                    if telemetry is not None:
                        telemetry["repair_state_changes"] += 1


def evolve_one_external(
    state,
    bit,
    mapped,
    mixed_rules,
    method,
    telemetry=None,
    record=None,
):
    state[mapped] = np.uint8(bit)

    for micro in range(1, MICROTICKS + 1):
        if micro == 4:
            if method == "SLOW128_MIXED1":
                state[:] = eca_step_mixed(state, mixed_rules)
            else:
                nanite_worker_update(
                    state, mixed_rules, method, telemetry=telemetry
                )
                if telemetry is not None:
                    update_run_telemetry(state, telemetry)

        if record is not None:
            off = (micro - 1) * WIDTH
            record[off:off + WIDTH] = state


def run_reca_features(u, mapped, mixed_rules, method):
    state = np.zeros(WIDTH, dtype=np.uint8)
    x = np.empty((len(u), WIDTH * MICROTICKS), dtype=np.uint8)
    snapshot = None
    telemetry = None if method == "SLOW128_MIXED1" else init_telemetry()

    for t, bit in enumerate(u):
        evolve_one_external(
            state,
            int(bit),
            mapped,
            mixed_rules,
            method,
            telemetry=telemetry,
            record=x[t],
        )
        if t == 512:
            snapshot = state.copy()

    final_tel = (
        None if telemetry is None
        else finalize_telemetry(telemetry)
    )
    return x, snapshot, final_tel


def perturbation_profile(u, mapped, mixed_rules, method, snapshot):
    a = snapshot.copy()
    b = snapshot.copy()
    b[112] ^= 1
    out = {}
    for h in range(1, 17):
        bit = int(u[512 + h])
        evolve_one_external(
            a, bit, mapped, mixed_rules, method, telemetry=None
        )
        evolve_one_external(
            b, bit, mapped, mixed_rules, method, telemetry=None
        )
        if h in (1, 4, 8, 16):
            out[f"h{h}"] = float(np.mean(a != b))
    return out


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
    ymat = np.column_stack(
        [targets[name][tr] for name in TASKS]
    ).astype(np.float64)

    gram = xa.T @ xa
    reg = RIDGE_ALPHA * np.eye(gram.shape[0], dtype=np.float64)
    reg[-1, -1] = 0.0
    beta = np.linalg.solve(gram + reg, xa.T @ ymat)
    pred = xva @ beta

    metrics = {}
    for j, name in enumerate(TASKS):
        yp = (pred[:, j] >= 0.5).astype(np.uint8)
        yt = targets[name][te]
        if name == "MOTIF2_12":
            metrics[name] = balanced_accuracy(yt, yp)
        else:
            metrics[name] = float(np.mean(yp == yt))
    return metrics


def binary_entropy_features(x):
    p = np.mean(x, axis=0, dtype=np.float64)
    mask = (p > 0.0) & (p < 1.0)
    h = np.zeros_like(p)
    h[mask] = -(
        p[mask] * np.log2(p[mask])
        + (1.0 - p[mask]) * np.log2(1.0 - p[mask])
    )
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
    return float(
        between / (0.5 * (within_a + within_b) + 1e-12)
    )


def resource_record(method):
    if method == "SLOW128_MIXED1":
        return {
            "persistent_state_bits": 128,
            "worker_cells": 128,
            "nanite_cells": 0,
            "worker_candidate_updates_per_external_step": 128,
            "nanite_controller_evaluations_per_external_step": 0,
            "readout_feature_bits": 512,
            "trainable_reservoir_parameters": 0,
            "trainable_readout_scalars_per_task": 513,
        }
    return {
        "persistent_state_bits": 128,
        "worker_cells": 112,
        "nanite_cells": 16,
        "worker_candidate_updates_per_external_step": 112,
        "nanite_controller_evaluations_per_external_step": 16,
        "readout_feature_bits": 512,
        "trainable_reservoir_parameters": 0,
        "trainable_readout_scalars_per_task": 513,
    }


def method_metrics(x, targets, perturb, telemetry, method):
    te = slice(TEST_START, TEST_START + TEST_ROWS)
    tasks = train_readouts(x, targets)
    entropy = binary_entropy_features(x[te])
    rank, rank_frac = feature_rank(x[te])
    parity_sep = fisher_ratio(
        x[te], targets["PARITY5"][te]
    )
    motif_sep = fisher_ratio(
        x[te], targets["MOTIF2_12"][te]
    )
    memory_score = float(
        np.mean([
            tasks["D8"],
            tasks["D16"],
            tasks["D32"],
        ])
    )
    nonlinear_score = float(
        np.mean([
            tasks["XOR3_11"],
            tasks["PARITY5"],
            tasks["MOTIF2_12"],
        ])
    )
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
        "nanite_telemetry": telemetry,
        "resources": resource_record(method),
    }


def one_world(seed):
    rng = np.random.default_rng(np.random.PCG64(seed))
    u = rng.integers(0, 2, size=SEQ_LEN, dtype=np.uint8)
    mapped = mapped_positions(rng)
    mixed_rules = mixed_rule_assignment(rng)
    random_weights = rng.choice(
        np.asarray([-1, 1], dtype=np.int8),
        size=(32, 512),
        replace=True,
    )
    random_biases = rng.integers(
        -4, 5, size=512, dtype=np.int16
    )
    targets = build_targets(u)
    methods = {}
    runtime = {}

    for method in RECA_METHODS:
        t0 = time.perf_counter()
        x, snapshot, telemetry = run_reca_features(
            u, mapped, mixed_rules, method
        )
        runtime[method] = float(time.perf_counter() - t0)
        perturb = perturbation_profile(
            u, mapped, mixed_rules, method, snapshot
        )
        methods[method] = method_metrics(
            x, targets, perturb, telemetry, method
        )

    t0 = time.perf_counter()
    raw = raw32_features(u)
    runtime["RAW32"] = float(time.perf_counter() - t0)
    methods["RAW32"] = method_metrics(
        raw, targets, None, None, "SLOW128_MIXED1"
    )
    methods["RAW32"]["resources"] = {
        "persistent_state_bits": 32,
        "readout_feature_bits": 32,
        "trainable_feature_parameters": 0,
        "trainable_readout_scalars_per_task": 33,
    }

    t0 = time.perf_counter()
    rnd = random512_features(
        raw, random_weights, random_biases
    )
    runtime["RANDOM512"] = float(time.perf_counter() - t0)
    methods["RANDOM512"] = method_metrics(
        rnd, targets, None, None, "SLOW128_MIXED1"
    )
    methods["RANDOM512"]["resources"] = {
        "persistent_state_bits": 32,
        "readout_feature_bits": 512,
        "fixed_projection_sign_bits": 32 * 512,
        "fixed_projection_biases": 512,
        "trainable_feature_parameters": 0,
        "trainable_readout_scalars_per_task": 513,
    }

    return {
        "seed": int(seed),
        "mapped_positions": [int(v) for v in mapped],
        "nanite_sites": [int(v) for v in NANITE_SITES],
        "mixed_rule_counts": {
            str(int(r)): int(np.sum(mixed_rules == r))
            for r in MIX_RULES
        },
        "methods": methods,
    }, runtime


def q(values, p):
    return float(
        np.quantile(
            np.asarray(values, dtype=np.float64),
            p,
        )
    )


def summarize_nanite_telemetry(mr):
    keys = (
        "nanite_bit_changes",
        "nanite_bit_changes_per_external_step",
        "nanite_bit_changes_per_nanite_step",
        "damp_suppressed_transitions",
        "damp_suppression_rate_per_worker_evolution",
        "repair_attempts",
        "repair_state_changes",
        "repair_state_changes_per_external_step",
        "nanite_run_length_mean",
        "nanite_run_length_median",
    )
    out = {}
    for key in keys:
        vals = [
            x["nanite_telemetry"][key]
            for x in mr
        ]
        out[key] = {
            "median": q(vals, 0.5),
            "p10": q(vals, 0.10),
        }
    return out


def summarize_method(rows, name):
    mr = [r["methods"][name] for r in rows]
    task_summary = {}
    for task in TASKS:
        vals = [x["tasks"][task] for x in mr]
        task_summary[task] = {
            "median": q(vals, 0.5),
            "p10": q(vals, 0.10),
        }

    s = {
        "tasks": task_summary,
        "memory_score": {
            "median": q(
                [x["memory_score"] for x in mr], 0.5
            ),
            "p10": q(
                [x["memory_score"] for x in mr], 0.10
            ),
        },
        "nonlinear_score": {
            "median": q(
                [x["nonlinear_score"] for x in mr], 0.5
            ),
            "p10": q(
                [x["nonlinear_score"] for x in mr], 0.10
            ),
        },
        "state_entropy": {
            "median": q(
                [x["state_entropy"] for x in mr], 0.5
            ),
            "p10": q(
                [x["state_entropy"] for x in mr], 0.10
            ),
        },
        "feature_rank": {
            "median": q(
                [x["feature_rank"] for x in mr], 0.5
            ),
            "p10": q(
                [x["feature_rank"] for x in mr], 0.10
            ),
        },
        "feature_rank_fraction": {
            "median": q(
                [x["feature_rank_fraction"] for x in mr], 0.5
            ),
            "p10": q(
                [x["feature_rank_fraction"] for x in mr], 0.10
            ),
        },
        "fisher_parity5": {
            "median": q(
                [x["fisher_parity5"] for x in mr], 0.5
            ),
        },
        "fisher_motif2_12": {
            "median": q(
                [x["fisher_motif2_12"] for x in mr], 0.5
            ),
        },
        "resources": mr[0]["resources"],
    }

    if name in RECA_METHODS:
        s["perturbation"] = {}
        for h in (1, 4, 8, 16):
            vals = [
                x["perturbation"][f"h{h}"]
                for x in mr
            ]
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
            for task in (
                "XOR3_11",
                "PARITY5",
                "MOTIF2_12",
            )
        )
        nonlinear_capable = (
            s["nonlinear_score"]["median"] >= 0.60
            and nonlinear_hits >= 2
        )
        ent = s["state_entropy"]["median"]
        h16 = s["perturbation"]["h16"]["median"]
        balanced = (
            0.20 <= ent <= 0.95
            and 0.01 <= h16 <= 0.75
        )
        overstabilized = (
            ent < 0.20
            or s["feature_rank_fraction"]["median"] < 0.10
        )
        s["classification"] = {
            "memory_capable": bool(memory_capable),
            "nonlinear_capable": bool(nonlinear_capable),
            "dynamically_balanced": bool(balanced),
            "temporal_substrate_candidate": bool(
                memory_capable
                and nonlinear_capable
                and balanced
            ),
            "overstabilized": bool(overstabilized),
        }

        if name != "SLOW128_MIXED1":
            s["nanite_telemetry"] = (
                summarize_nanite_telemetry(mr)
            )
    return s


def paired_delta(rows, name, ref="SLOW128_MIXED1"):
    out = {}
    for key in (
        "D1", "D4", "D8", "D16", "D32"
    ):
        vals = [
            r["methods"][name]["tasks"][key]
            - r["methods"][ref]["tasks"][key]
            for r in rows
        ]
        out[key] = {
            "median": q(vals, 0.5),
            "p10": q(vals, 0.10),
        }
    for key in ("memory_score", "nonlinear_score"):
        vals = [
            r["methods"][name][key]
            - r["methods"][ref][key]
            for r in rows
        ]
        out[key] = {
            "median": q(vals, 0.5),
            "p10": q(vals, 0.10),
        }
    return out


def summarize(rows):
    out = {
        "worlds": len(rows),
        "methods": {},
        "relative_to_slow128": {},
    }
    for name in METHODS:
        out["methods"][name] = summarize_method(
            rows, name
        )

    nanite_methods = (
        "N16_H5",
        "N16_H6",
        "N16_H6_DAMP",
        "N16_H6_REPAIR",
    )
    for name in nanite_methods:
        out["relative_to_slow128"][name] = (
            paired_delta(rows, name)
        )

    long_signal = any(
        out["relative_to_slow128"][name]["D16"]["median"] >= 0.10
        or out["relative_to_slow128"][name]["D32"]["median"] >= 0.10
        for name in nanite_methods
    )

    slow_nonlinear = out["methods"][
        "SLOW128_MIXED1"
    ]["nonlinear_score"]["median"]

    strong = False
    for name in nanite_methods:
        s = out["methods"][name]
        if (
            s["tasks"]["D16"]["median"] >= 0.65
            and s["tasks"]["D32"]["median"] >= 0.60
            and s["nonlinear_score"]["median"]
            >= slow_nonlinear - 0.05
            and s["state_entropy"]["median"] >= 0.20
        ):
            strong = True
            break

    slow_candidate = out["methods"][
        "SLOW128_MIXED1"
    ]["classification"]["temporal_substrate_candidate"]
    full = any(
        out["methods"][name]["classification"][
            "temporal_substrate_candidate"
        ]
        for name in nanite_methods
    ) and not slow_candidate

    out["nanite_long_memory_signal"] = bool(
        long_signal
    )
    out["strong_nanite_signal"] = bool(strong)
    out["full_nanite_recovery"] = bool(full)
    out["overstabilized_methods"] = [
        name
        for name in nanite_methods
        if out["methods"][name]["classification"][
            "overstabilized"
        ]
    ]
    out["temporal_substrate_candidates"] = [
        name
        for name in RECA_METHODS
        if out["methods"][name]["classification"][
            "temporal_substrate_candidate"
        ]
    ]
    return out


def encode(obj):
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def run():
    rows = []
    runtime_rows = []
    for i in range(WORLD_COUNT):
        row, runtime = one_world(WORLD_START + i)
        rows.append(row)
        runtime_rows.append({
            "seed": row["seed"],
            "feature_generation_seconds": runtime,
        })

    canonical = {
        "schema": (
            "yggdrasil.dg1r-04-local-"
            "software-nanite-memory.v1"
        ),
        "rows": rows,
        "summary": summarize(rows),
        "worlds": len(rows),
        "seed_start": WORLD_START,
        "seed_end": WORLD_START + WORLD_COUNT - 1,
    }
    runtime = {
        "schema": "yggdrasil.dg1r-04-runtime-sidecar.v1",
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
            json.dumps(
                runtime,
                sort_keys=True,
                indent=2,
            )
            + "\n",
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
