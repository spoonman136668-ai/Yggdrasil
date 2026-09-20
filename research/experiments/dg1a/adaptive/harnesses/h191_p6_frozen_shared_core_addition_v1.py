#!/usr/bin/env python3
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np

P5_NAME = "h191_p5_capability_count_scaling_v1.py"
WORLD_START = 20260924700000
WORLD_COUNT = 6
STAGES = (
    ("CORE3", (0, 1, 2), (0, 1, 2)),
    ("CAP4", (0, 1, 2, 3), (3,)),
    ("CAP5", (0, 1, 2, 3, 4), (4,)),
    ("CAP6", (0, 1, 2, 3, 4, 5), (5,)),
    ("CAP8", (0, 1, 2, 3, 4, 5, 6, 7), (6, 7)),
)


def load_p5():
    path = Path(__file__).resolve().parent / P5_NAME
    spec = importlib.util.spec_from_file_location("h191_p5_base", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def recruit_support(p5, base, dist_x, dist_y, active):
    cand_centers = np.repeat(base.PARENT, 3, axis=0)
    cand_widths = np.tile(p5.SCALES, base.PARENT.shape[0])
    m = len(cand_widths)
    zd = {
        i: base.gaussian_features(dist_x[i], cand_centers, cand_widths)
        for i in active
    }
    selected = []
    available = np.ones(m, dtype=bool)

    for _ in range(8):
        total_score = np.zeros(m, dtype=np.float64)
        for i in active:
            y = dist_y[i]
            zall = zd[i]
            if not selected:
                denom = np.sum(zall * zall, axis=0) + p5.ALPHA
                gamma = (zall.T @ y) / denom
                pred_new = zall * gamma[None, :]
            else:
                xsel = zall[:, selected]
                ata = xsel.T @ xsel + p5.ALPHA * np.eye(len(selected))
                ainv = np.linalg.inv(ata)
                xty = xsel.T @ y
                beta = ainv @ xty
                pred = xsel @ beta
                q = xsel.T @ zall
                v = ainv @ q
                u = zall - xsel @ v
                h = np.sum(zall * zall, axis=0) + p5.ALPHA - np.sum(q * v, axis=0)
                numer = zall.T @ y - q.T @ beta
                gamma = numer / h
                pred_new = pred[:, None] + u * gamma[None, :]
            mse = np.mean((y[:, None] - pred_new) ** 2, axis=0)
            total_score += mse / (float(np.var(y)) + 1e-12)
        total_score /= float(len(active))
        total_score[~available] = np.inf
        idx = int(np.argmin(total_score))
        selected.append(idx)
        available[idx] = False
    return selected


def fit_decoder(p5, base, x, y, selected):
    centers = np.repeat(base.PARENT, 3, axis=0)[selected]
    widths = np.tile(p5.SCALES, base.PARENT.shape[0])[selected]
    z = base.gaussian_features(x, centers, widths)
    return base.ridge_fit(z, y, p5.ALPHA)


def predict_decoder(p5, base, x, beta, selected):
    centers = np.repeat(base.PARENT, 3, axis=0)[selected]
    widths = np.tile(p5.SCALES, base.PARENT.shape[0])[selected]
    z = base.gaussian_features(x, centers, widths)
    return z @ beta


def support_meta(selected):
    slots = [int(v % 3) for v in selected]
    counts = [slots.count(i) for i in range(3)]
    return {
        "candidates": [int(v) for v in selected],
        "center_indices": [int(v // 3) for v in selected],
        "scale_slots": slots,
        "scale_slot_counts": {
            "S0_0p22": int(counts[0]),
            "S1_0p44": int(counts[1]),
            "S2_0p88": int(counts[2]),
        },
    }


def support_overlap(a, b):
    sa = set(a)
    sb = set(b)
    inter = len(sa & sb)
    union = len(sa | sb)
    return {
        "exact_shared_candidates": int(inter),
        "jaccard": float(inter / union if union else 1.0),
    }


def normalized_prediction_drift(base, before, after):
    return base.nmse(after, before)


def build_world_data(p5, base, seed):
    rng = np.random.default_rng(np.random.PCG64(seed))
    centers = p5.context_centers(8)
    params = p5.source_params(base, rng, 8)

    dist_x = []
    held_x = []
    dist_y = []
    held_y = []
    for cap_i in range(8):
        pts = p5.sample_context(rng, centers, cap_i, 128 + 512)
        xd = pts[:128]
        xh = pts[128:]
        yd = p5.raw_residual(base, xd, cap_i, params)
        yh = p5.raw_residual(base, xh, cap_i, params)
        scale = float(np.sqrt(np.mean(yd * yd)))
        if scale < 1e-12:
            scale = 1.0
        dist_x.append(xd)
        held_x.append(xh)
        dist_y.append(yd / scale)
        held_y.append(yh / scale)
    return dist_x, held_x, dist_y, held_y


def one_world(p5, base, seed):
    dist_x, held_x, dist_y, held_y = build_world_data(p5, base, seed)

    core_active = STAGES[0][1]
    core_support = recruit_support(p5, base, dist_x, dist_y, core_active)
    frozen_decoders = {
        i: fit_decoder(p5, base, dist_x[i], dist_y[i], core_support)
        for i in core_active
    }
    previous_predictions = {
        i: predict_decoder(p5, base, held_x[i], frozen_decoders[i], core_support)
        for i in core_active
    }

    stages = {}

    for stage_i, (label, active, new_caps) in enumerate(STAGES):
        if stage_i > 0:
            old_caps = tuple(i for i in active if i not in new_caps)
            decoder_snapshot = {i: frozen_decoders[i].copy() for i in old_caps}
            for i in new_caps:
                frozen_decoders[i] = fit_decoder(
                    p5, base, dist_x[i], dist_y[i], core_support
                )
            decoder_change = 0.0
            for i in old_caps:
                decoder_change = max(
                    decoder_change,
                    float(np.max(np.abs(frozen_decoders[i] - decoder_snapshot[i]))),
                )
        else:
            old_caps = ()
            decoder_change = 0.0

        frozen_pred = {}
        frozen_dist = {}
        frozen_held_nmse = {}
        frozen_dist_nmse = {}
        for i in active:
            pd = predict_decoder(p5, base, dist_x[i], frozen_decoders[i], core_support)
            ph = predict_decoder(p5, base, held_x[i], frozen_decoders[i], core_support)
            frozen_dist[i] = pd
            frozen_pred[i] = ph
            frozen_dist_nmse[i] = base.nmse(pd, dist_y[i])
            frozen_held_nmse[i] = base.nmse(ph, held_y[i])

        old_prediction_drift = 0.0
        if stage_i > 0:
            for i in old_caps:
                old_prediction_drift = max(
                    old_prediction_drift,
                    normalized_prediction_drift(
                        base, previous_predictions[i], frozen_pred[i]
                    ),
                )

        joint_support = recruit_support(p5, base, dist_x, dist_y, active)
        joint_held_nmse = {}
        joint_dist_nmse = {}
        for i in active:
            beta = fit_decoder(p5, base, dist_x[i], dist_y[i], joint_support)
            pd = predict_decoder(p5, base, dist_x[i], beta, joint_support)
            ph = predict_decoder(p5, base, held_x[i], beta, joint_support)
            joint_dist_nmse[i] = base.nmse(pd, dist_y[i])
            joint_held_nmse[i] = base.nmse(ph, held_y[i])

        frozen_vals = [frozen_held_nmse[i] for i in active]
        joint_vals = [joint_held_nmse[i] for i in active]
        new_frozen = [frozen_held_nmse[i] for i in new_caps]
        new_joint = [joint_held_nmse[i] for i in new_caps]

        stages[label] = {
            "active_capabilities": [int(i) for i in active],
            "new_capabilities": [int(i) for i in new_caps],
            "frozen_core": {
                "held_nmse": {str(i): float(frozen_held_nmse[i]) for i in active},
                "dist_nmse": {str(i): float(frozen_dist_nmse[i]) for i in active},
                "world_mean_nmse": float(np.mean(frozen_vals)),
                "world_worst_nmse": float(np.max(frozen_vals)),
                "new_cap_mean_nmse": (
                    float(np.mean(new_frozen)) if new_frozen else float(np.mean(frozen_vals))
                ),
            },
            "joint_refit": {
                "held_nmse": {str(i): float(joint_held_nmse[i]) for i in active},
                "dist_nmse": {str(i): float(joint_dist_nmse[i]) for i in active},
                "world_mean_nmse": float(np.mean(joint_vals)),
                "world_worst_nmse": float(np.max(joint_vals)),
                "new_cap_mean_nmse": (
                    float(np.mean(new_joint)) if new_joint else float(np.mean(joint_vals))
                ),
            },
            "developmental_cost": {
                "world_mean_gap": float(np.mean(frozen_vals) - np.mean(joint_vals)),
                "world_worst_gap": float(np.max(frozen_vals) - np.max(joint_vals)),
                "new_cap_gap": (
                    float(np.mean(new_frozen) - np.mean(new_joint)) if new_frozen else 0.0
                ),
            },
            "preservation": {
                "old_decoder_max_abs_change": float(decoder_change),
                "old_prediction_drift_max": float(old_prediction_drift),
            },
            "support_pressure": support_overlap(core_support, joint_support),
            "joint_support": support_meta(joint_support),
            "memory_compute": {
                "learned_decoder_scalars": int(8 * len(active)),
                "shared_site_ids": 8,
                "shared_scale_slots": 8,
                "geometry_growth": 0,
                "per_query_residual_ops": 16,
            },
        }

        previous_predictions = {
            i: frozen_pred[i].copy()
            for i in active
        }

    return {
        "seed": int(seed),
        "core_support": support_meta(core_support),
        "stages": stages,
    }


def q(values, p):
    return float(np.quantile(np.asarray(values, dtype=np.float64), p))


def summarize_stage(rows, label):
    stage_rows = [r["stages"][label] for r in rows]
    mean_gap = [s["developmental_cost"]["world_mean_gap"] for s in stage_rows]
    worst_gap = [s["developmental_cost"]["world_worst_gap"] for s in stage_rows]
    new_gap = [s["developmental_cost"]["new_cap_gap"] for s in stage_rows]
    new_nmse = [s["frozen_core"]["new_cap_mean_nmse"] for s in stage_rows]
    frozen_mean = [s["frozen_core"]["world_mean_nmse"] for s in stage_rows]
    joint_mean = [s["joint_refit"]["world_mean_nmse"] for s in stage_rows]
    frozen_worst = [s["frozen_core"]["world_worst_nmse"] for s in stage_rows]
    joint_worst = [s["joint_refit"]["world_worst_nmse"] for s in stage_rows]
    drift = [s["preservation"]["old_prediction_drift_max"] for s in stage_rows]
    decoder_change = [s["preservation"]["old_decoder_max_abs_change"] for s in stage_rows]
    overlap = [s["support_pressure"]["exact_shared_candidates"] for s in stage_rows]
    jaccard = [s["support_pressure"]["jaccard"] for s in stage_rows]

    mean_gap_med = q(mean_gap, 0.5)
    new_gap_med = q(new_gap, 0.5)
    new_nmse_med = q(new_nmse, 0.5)
    drift_max = float(np.max(drift))
    if (
        mean_gap_med <= 0.02
        and new_gap_med <= 0.03
        and new_nmse_med <= 0.05
        and drift_max <= 1e-12
    ):
        regime = "ROBUST"
    elif mean_gap_med > 0.05 and new_gap_med > 0.07:
        regime = "OVER_CAPACITY"
    elif (
        (0.02 < mean_gap_med <= 0.05)
        or (0.03 < new_gap_med <= 0.07)
    ):
        regime = "TRANSITION"
    else:
        regime = "MIXED_UNCLASSIFIED"

    active_count = len(stage_rows[0]["active_capabilities"])
    slot_counts = [0, 0, 0]
    for s in stage_rows:
        c = s["joint_support"]["scale_slot_counts"]
        slot_counts[0] += c["S0_0p22"]
        slot_counts[1] += c["S1_0p44"]
        slot_counts[2] += c["S2_0p88"]

    return {
        "worlds": len(rows),
        "active_capability_count": int(active_count),
        "mechanical_regime": regime,
        "frozen_core_world_mean_median": q(frozen_mean, 0.5),
        "joint_refit_world_mean_median": q(joint_mean, 0.5),
        "frozen_core_world_worst_median": q(frozen_worst, 0.5),
        "joint_refit_world_worst_median": q(joint_worst, 0.5),
        "world_mean_gap_median": mean_gap_med,
        "world_mean_gap_p90": q(mean_gap, 0.90),
        "world_worst_gap_median": q(worst_gap, 0.5),
        "new_cap_frozen_nmse_median": new_nmse_med,
        "new_cap_gap_median": new_gap_med,
        "old_prediction_drift_max": drift_max,
        "old_decoder_max_abs_change": float(np.max(decoder_change)),
        "core_vs_joint_exact_candidate_overlap_median": q(overlap, 0.5),
        "core_vs_joint_jaccard_median": q(jaccard, 0.5),
        "joint_scale_slot_counts": {
            "S0_0p22": int(slot_counts[0]),
            "S1_0p44": int(slot_counts[1]),
            "S2_0p88": int(slot_counts[2]),
        },
        "memory_compute": {
            "learned_decoder_scalars": int(8 * active_count),
            "shared_site_ids": 8,
            "shared_scale_slots": 8,
            "geometry_growth": 0,
            "per_query_residual_ops": 16,
        },
    }


def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def run():
    p5 = load_p5()
    base = p5.load_base()
    rows = [one_world(p5, base, WORLD_START + i) for i in range(WORLD_COUNT)]
    summary = {
        label: summarize_stage(rows, label)
        for label, _, _ in STAGES
    }
    return {
        "schema": "yggdrasil.h191-p6-frozen-shared-core-addition.v1",
        "rows": rows,
        "summary": summary,
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
