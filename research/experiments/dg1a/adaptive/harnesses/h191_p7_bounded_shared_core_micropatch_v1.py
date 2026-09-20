#!/usr/bin/env python3
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np

P6_NAME = "h191_p6_frozen_shared_core_addition_v1.py"
WORLD_START = 20260924800000
WORLD_COUNT = 12
OLD_CAPS = (0, 1, 2)
NEW_CAP = 3


def load_p6():
    path = Path(__file__).resolve().parent / P6_NAME
    spec = importlib.util.spec_from_file_location("h191_p6_base", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def dictionary(p5, base):
    centers = np.repeat(base.PARENT, 3, axis=0)
    widths = np.tile(p5.SCALES, base.PARENT.shape[0])
    return centers, widths


def fit_new_decoder(p6, p5, base, x, y, selected):
    return p6.fit_decoder(p5, base, x, y, selected)


def one_patch_step(p6, p5, base, xd, yd, selected, excluded):
    centers, widths = dictionary(p5, base)
    zall = base.gaussian_features(xd, centers, widths)
    xsel = zall[:, selected]

    ata = xsel.T @ xsel + p5.ALPHA * np.eye(len(selected))
    ainv = np.linalg.inv(ata)
    xty = xsel.T @ yd
    beta = ainv @ xty
    pred = xsel @ beta

    q = xsel.T @ zall
    v = ainv @ q
    u = zall - xsel @ v
    h = np.sum(zall * zall, axis=0) + p5.ALPHA - np.sum(q * v, axis=0)
    numer = zall.T @ yd - q.T @ beta
    gamma = numer / h
    pred_new = pred[:, None] + u * gamma[None, :]
    mse = np.mean((yd[:, None] - pred_new) ** 2, axis=0)

    available = np.ones(len(widths), dtype=bool)
    available[list(excluded)] = False
    mse[~available] = np.inf
    idx = int(np.argmin(mse))
    return idx


def cap_metrics(p6, p5, base, selected, beta, xd, yd, xh, yh):
    pd = p6.predict_decoder(p5, base, xd, beta, selected)
    ph = p6.predict_decoder(p5, base, xh, beta, selected)
    return {
        "dist_nmse": base.nmse(pd, yd),
        "held_nmse": base.nmse(ph, yh),
        "prediction": ph,
    }


def patch_factor_meta(p5, base, idx, core_support, joint_support):
    centers, widths = dictionary(p5, base)
    center = centers[idx]
    core_centers = centers[core_support]
    nearest = float(np.min(np.sqrt(np.sum((core_centers - center[None, :]) ** 2, axis=1))))
    return {
        "candidate": int(idx),
        "center_index": int(idx // 3),
        "scale_slot": int(idx % 3),
        "width": float(widths[idx]),
        "nearest_core_center_distance": nearest,
        "in_joint_refit8_support": bool(idx in set(joint_support)),
    }


def evaluate_policy(p6, p5, base, core_support, old_decoders, old_core_predictions,
                    selected, new_beta, dist_x, held_x, dist_y, held_y):
    active = OLD_CAPS + (NEW_CAP,)
    held = {}
    dist = {}
    old_drift = 0.0
    old_decoder_change = 0.0

    for i in OLD_CAPS:
        before_beta = old_decoders[i]
        after_beta = old_decoders[i]
        old_decoder_change = max(
            old_decoder_change,
            float(np.max(np.abs(after_beta - before_beta))),
        )
        ph = p6.predict_decoder(p5, base, held_x[i], after_beta, core_support)
        pd = p6.predict_decoder(p5, base, dist_x[i], after_beta, core_support)
        held[i] = base.nmse(ph, held_y[i])
        dist[i] = base.nmse(pd, dist_y[i])
        old_drift = max(
            old_drift,
            p6.normalized_prediction_drift(base, old_core_predictions[i], ph),
        )

    newm = cap_metrics(
        p6, p5, base, selected, new_beta,
        dist_x[NEW_CAP], dist_y[NEW_CAP], held_x[NEW_CAP], held_y[NEW_CAP],
    )
    held[NEW_CAP] = newm["held_nmse"]
    dist[NEW_CAP] = newm["dist_nmse"]

    hvals = [held[i] for i in active]
    return {
        "held_nmse": {str(i): float(held[i]) for i in active},
        "dist_nmse": {str(i): float(dist[i]) for i in active},
        "new_cap_held_nmse": float(held[NEW_CAP]),
        "new_cap_dist_nmse": float(dist[NEW_CAP]),
        "world_mean_nmse": float(np.mean(hvals)),
        "world_worst_nmse": float(np.max(hvals)),
        "old_prediction_drift_max": float(old_drift),
        "old_decoder_max_abs_change": float(old_decoder_change),
    }


def one_world(p6, p5, base, seed):
    dist_x, held_x, dist_y, held_y = p6.build_world_data(p5, base, seed)

    core_support = p6.recruit_support(p5, base, dist_x, dist_y, OLD_CAPS)
    old_decoders = {
        i: p6.fit_decoder(p5, base, dist_x[i], dist_y[i], core_support)
        for i in OLD_CAPS
    }
    old_core_predictions = {
        i: p6.predict_decoder(p5, base, held_x[i], old_decoders[i], core_support)
        for i in OLD_CAPS
    }

    active4 = OLD_CAPS + (NEW_CAP,)
    joint_support = p6.recruit_support(p5, base, dist_x, dist_y, active4)
    joint_decoders = {
        i: p6.fit_decoder(p5, base, dist_x[i], dist_y[i], joint_support)
        for i in active4
    }
    joint_held = {}
    joint_dist = {}
    for i in active4:
        ph = p6.predict_decoder(p5, base, held_x[i], joint_decoders[i], joint_support)
        pd = p6.predict_decoder(p5, base, dist_x[i], joint_decoders[i], joint_support)
        joint_held[i] = base.nmse(ph, held_y[i])
        joint_dist[i] = base.nmse(pd, dist_y[i])
    joint_vals = [joint_held[i] for i in active4]
    joint = {
        "held_nmse": {str(i): float(joint_held[i]) for i in active4},
        "dist_nmse": {str(i): float(joint_dist[i]) for i in active4},
        "new_cap_held_nmse": float(joint_held[NEW_CAP]),
        "new_cap_dist_nmse": float(joint_dist[NEW_CAP]),
        "world_mean_nmse": float(np.mean(joint_vals)),
        "world_worst_nmse": float(np.max(joint_vals)),
    }

    beta0 = fit_new_decoder(
        p6, p5, base, dist_x[NEW_CAP], dist_y[NEW_CAP], core_support
    )
    patch0 = evaluate_policy(
        p6, p5, base, core_support, old_decoders, old_core_predictions,
        core_support, beta0, dist_x, held_x, dist_y, held_y,
    )

    patch1_idx = one_patch_step(
        p6, p5, base, dist_x[NEW_CAP], dist_y[NEW_CAP],
        core_support, set(core_support),
    )
    support1 = core_support + [patch1_idx]
    beta1 = fit_new_decoder(
        p6, p5, base, dist_x[NEW_CAP], dist_y[NEW_CAP], support1
    )
    patch1 = evaluate_policy(
        p6, p5, base, core_support, old_decoders, old_core_predictions,
        support1, beta1, dist_x, held_x, dist_y, held_y,
    )

    patch2_idx = one_patch_step(
        p6, p5, base, dist_x[NEW_CAP], dist_y[NEW_CAP],
        support1, set(support1),
    )
    support2 = support1 + [patch2_idx]
    beta2 = fit_new_decoder(
        p6, p5, base, dist_x[NEW_CAP], dist_y[NEW_CAP], support2
    )
    patch2 = evaluate_policy(
        p6, p5, base, core_support, old_decoders, old_core_predictions,
        support2, beta2, dist_x, held_x, dist_y, held_y,
    )

    for policy in (patch0, patch1, patch2):
        policy["developmental_cost"] = {
            "new_cap_gap": float(policy["new_cap_held_nmse"] - joint["new_cap_held_nmse"]),
            "world_mean_gap": float(policy["world_mean_nmse"] - joint["world_mean_nmse"]),
            "world_worst_gap": float(policy["world_worst_nmse"] - joint["world_worst_nmse"]),
        }

    patch1["patch_factors"] = [
        patch_factor_meta(p5, base, patch1_idx, core_support, joint_support)
    ]
    patch2["patch_factors"] = [
        patch_factor_meta(p5, base, patch1_idx, core_support, joint_support),
        patch_factor_meta(p5, base, patch2_idx, core_support, joint_support),
    ]

    patch0["memory_compute"] = {
        "factor_count": 8,
        "new_cap_decoder_scalars": 8,
        "new_cap_residual_ops": 16,
        "old_cap_residual_ops": 16,
        "geometry_growth_fraction": 0.0,
    }
    patch1["memory_compute"] = {
        "factor_count": 9,
        "new_cap_decoder_scalars": 9,
        "new_cap_residual_ops": 18,
        "old_cap_residual_ops": 16,
        "geometry_growth_fraction": 0.125,
    }
    patch2["memory_compute"] = {
        "factor_count": 10,
        "new_cap_decoder_scalars": 10,
        "new_cap_residual_ops": 20,
        "old_cap_residual_ops": 16,
        "geometry_growth_fraction": 0.25,
    }

    return {
        "seed": int(seed),
        "core_support": p6.support_meta(core_support),
        "joint_refit8_support": p6.support_meta(joint_support),
        "core_vs_joint": p6.support_overlap(core_support, joint_support),
        "PATCH0": patch0,
        "PATCH1": patch1,
        "PATCH2": patch2,
        "JOINT_REFIT8": joint,
    }


def q(values, p):
    return float(np.quantile(np.asarray(values, dtype=np.float64), p))


def classify(policy_rows):
    new_gap = [r["developmental_cost"]["new_cap_gap"] for r in policy_rows]
    mean_gap = [r["developmental_cost"]["world_mean_gap"] for r in policy_rows]
    held = [r["new_cap_held_nmse"] for r in policy_rows]
    gen_gap = [r["new_cap_held_nmse"] - r["new_cap_dist_nmse"] for r in policy_rows]
    drift = max(r["old_prediction_drift_max"] for r in policy_rows)
    dchange = max(r["old_decoder_max_abs_change"] for r in policy_rows)

    new_gap_med = q(new_gap, 0.5)
    mean_gap_med = q(mean_gap, 0.5)
    held_med = q(held, 0.5)
    gen_gap_med = q(gen_gap, 0.5)

    if (
        held_med <= 0.05
        and new_gap_med <= 0.03
        and mean_gap_med <= 0.02
        and drift <= 1e-12
        and dchange == 0.0
        and gen_gap_med <= 0.05
    ):
        regime = "ROBUST_MICROPATCH"
    elif new_gap_med > 0.07 and mean_gap_med > 0.05:
        regime = "OVER_CAPACITY"
    elif (0.03 < new_gap_med <= 0.07) or (0.02 < mean_gap_med <= 0.05):
        regime = "TRANSITION"
    else:
        regime = "MIXED_UNCLASSIFIED"

    return {
        "mechanical_regime": regime,
        "new_cap_held_nmse_median": held_med,
        "new_cap_held_nmse_p90": q(held, 0.90),
        "new_cap_gap_median": new_gap_med,
        "new_cap_gap_p90": q(new_gap, 0.90),
        "world_mean_gap_median": mean_gap_med,
        "world_mean_gap_p90": q(mean_gap, 0.90),
        "generalization_gap_median": gen_gap_med,
        "old_prediction_drift_max": float(drift),
        "old_decoder_max_abs_change": float(dchange),
    }


def summarize(rows):
    out = {"worlds": len(rows), "policies": {}}
    for name in ("PATCH0", "PATCH1", "PATCH2"):
        pr = [r[name] for r in rows]
        s = classify(pr)
        s["world_mean_nmse_median"] = q([r["world_mean_nmse"] for r in pr], 0.5)
        s["world_worst_nmse_median"] = q([r["world_worst_nmse"] for r in pr], 0.5)
        s["memory_compute"] = pr[0]["memory_compute"]
        if name != "PATCH0":
            factors = [f for r in pr for f in r["patch_factors"]]
            s["patch_scale_slot_counts"] = {
                "S0_0p22": int(sum(f["scale_slot"] == 0 for f in factors)),
                "S1_0p44": int(sum(f["scale_slot"] == 1 for f in factors)),
                "S2_0p88": int(sum(f["scale_slot"] == 2 for f in factors)),
            }
            s["nearest_core_center_distance_median"] = q(
                [f["nearest_core_center_distance"] for f in factors], 0.5
            )
            s["joint_refit8_support_overlap_rate"] = float(np.mean([
                f["in_joint_refit8_support"] for f in factors
            ]))
        out["policies"][name] = s

    joint = [r["JOINT_REFIT8"] for r in rows]
    out["joint_refit8"] = {
        "new_cap_held_nmse_median": q([r["new_cap_held_nmse"] for r in joint], 0.5),
        "world_mean_nmse_median": q([r["world_mean_nmse"] for r in joint], 0.5),
        "world_worst_nmse_median": q([r["world_worst_nmse"] for r in joint], 0.5),
    }
    out["core_vs_joint_exact_candidate_overlap_median"] = q(
        [r["core_vs_joint"]["exact_shared_candidates"] for r in rows], 0.5
    )
    out["core_vs_joint_jaccard_median"] = q(
        [r["core_vs_joint"]["jaccard"] for r in rows], 0.5
    )
    return out


def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def run():
    p6 = load_p6()
    p5 = p6.load_p5()
    base = p5.load_base()
    rows = [one_world(p6, p5, base, WORLD_START + i) for i in range(WORLD_COUNT)]
    return {
        "schema": "yggdrasil.h191-p7-bounded-shared-core-micropatch.v1",
        "rows": rows,
        "summary": summarize(rows),
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
