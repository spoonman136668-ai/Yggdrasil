#!/usr/bin/env python3
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

ALPHA = 0.001
PARENT_SIGMA = 0.22
SCALES = np.asarray([0.22, 0.44, 0.88], dtype=np.float64)
WORLD_START = 20260925000000
WORLD_COUNT = 8
TRIGGER_NMSE = 0.02
OOD_CAP = 8
OOD_CENTER = np.asarray([0.0, 0.0], dtype=np.float64)
OOD_SD = 0.10
OOD_RADIUS_MAX = 0.30
OOD_FREQ_MIN = 5.0
OOD_FREQ_MAX = 8.0
OLD_CAPS = (0, 1, 2)
ADDITION_ORDER = (3, 4, 5, 6, 7)


def parent_sites():
    pts = []
    for i in range(-32, 33):
        for j in range(-32, 33):
            if i * i + j * j <= 32 * 32:
                pts.append((i / 32.0, j / 32.0))
    out = np.asarray(pts, dtype=np.float64)
    assert out.shape == (3209, 2)
    return out


PARENT = parent_sites()
CAND_CENTERS = np.repeat(PARENT, 3, axis=0)
CAND_WIDTHS = np.tile(SCALES, PARENT.shape[0])


def uniform_disk(rng, n):
    u = rng.random(n)
    th = rng.uniform(0.0, 2.0 * math.pi, size=n)
    r = np.sqrt(u)
    return np.column_stack((r * np.cos(th), r * np.sin(th)))


def gaussian_features(x, centers, sigmas):
    d2 = ((x[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
    return np.exp(-d2 / (2.0 * (sigmas[None, :] ** 2)))


def ridge_fit(x, y, alpha=ALPHA):
    k = x.shape[1]
    if k == 0:
        return np.empty(0, dtype=np.float64)
    return np.linalg.solve(x.T @ x + alpha * np.eye(k), x.T @ y)


def nmse(yhat, y):
    v = float(np.var(y))
    return float(np.mean((yhat - y) ** 2) / (v + 1e-12))


def context_centers(k=8):
    ang = 2.0 * math.pi * np.arange(k, dtype=np.float64) / float(k)
    return np.column_stack((0.60 * np.cos(ang), 0.60 * np.sin(ang)))


def sample_ring_context(rng, centers, cap_i, n):
    chunks = []
    have = 0
    center = centers[cap_i]
    while have < n:
        draw_n = max(64, (n - have) * 3)
        p = rng.normal(loc=center, scale=0.14, size=(draw_n, 2))
        p = p[np.sum(p * p, axis=1) <= 1.0]
        if len(p):
            d2 = ((p[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
            p = p[np.argmin(d2, axis=1) == cap_i]
        if len(p):
            take = min(n - have, len(p))
            chunks.append(p[:take])
            have += take
    return np.concatenate(chunks, axis=0)


def sample_ood_context(rng, n):
    chunks = []
    have = 0
    while have < n:
        draw_n = max(64, (n - have) * 3)
        p = rng.normal(loc=OOD_CENTER, scale=OOD_SD, size=(draw_n, 2))
        p = p[np.sum(p * p, axis=1) <= OOD_RADIUS_MAX * OOD_RADIUS_MAX]
        if len(p):
            take = min(n - have, len(p))
            chunks.append(p[:take])
            have += take
    return np.concatenate(chunks, axis=0)


def source_params_9(rng):
    centers = uniform_disk(rng, 8)
    sigmas = rng.uniform(0.12, 0.42, size=8)
    dec = rng.normal(0.0, 1.0, size=(8, 9))
    sins = []
    for cap_i in range(9):
        a = rng.uniform(0.5, 1.5)
        if cap_i == OOD_CAP:
            wx = rng.uniform(OOD_FREQ_MIN, OOD_FREQ_MAX)
            wy = rng.uniform(OOD_FREQ_MIN, OOD_FREQ_MAX)
        else:
            wx = rng.uniform(1.0, 4.0)
            wy = rng.uniform(1.0, 4.0)
        phase = rng.uniform(0.0, 2.0 * math.pi)
        sins.append((a, wx, wy, phase))
    return centers, sigmas, dec, sins


def raw_residual(x, cap_i, params):
    centers, sigmas, dec, sins = params
    shared = gaussian_features(x, centers, sigmas) @ dec[:, cap_i]
    a, wx, wy, phase = sins[cap_i]
    extra = 0.10 * a * np.sin(wx * x[:, 0] + wy * x[:, 1] + phase)
    return shared + extra


def build_world_data(seed):
    rng = np.random.default_rng(np.random.PCG64(seed))
    ring_centers = context_centers(8)
    params = source_params_9(rng)
    dist_x, held_x, dist_y, held_y = [], [], [], []

    for cap_i in range(9):
        if cap_i < 8:
            pts = sample_ring_context(rng, ring_centers, cap_i, 128 + 512)
        else:
            pts = sample_ood_context(rng, 128 + 512)
        xd, xh = pts[:128], pts[128:]
        yd = raw_residual(xd, cap_i, params)
        yh = raw_residual(xh, cap_i, params)
        scale = float(np.sqrt(np.mean(yd * yd)))
        if scale < 1e-12:
            scale = 1.0
        dist_x.append(xd)
        held_x.append(xh)
        dist_y.append(yd / scale)
        held_y.append(yh / scale)

    return dist_x, held_x, dist_y, held_y


def fit_decoder(x, y, support):
    z = gaussian_features(x, CAND_CENTERS[support], CAND_WIDTHS[support])
    return ridge_fit(z, y)


def predict_decoder(x, beta, support):
    z = gaussian_features(x, CAND_CENTERS[support], CAND_WIDTHS[support])
    return z @ beta


def recruit_support(dist_x, dist_y, active, rank=8):
    zd = {
        i: gaussian_features(dist_x[i], CAND_CENTERS, CAND_WIDTHS)
        for i in active
    }
    selected = []
    available = np.ones(len(CAND_WIDTHS), dtype=bool)

    for _ in range(rank):
        total_score = np.zeros(len(CAND_WIDTHS), dtype=np.float64)
        for i in active:
            y = dist_y[i]
            zall = zd[i]
            if not selected:
                denom = np.sum(zall * zall, axis=0) + ALPHA
                gamma = (zall.T @ y) / denom
                pred_new = zall * gamma[None, :]
            else:
                xsel = zall[:, selected]
                ainv = np.linalg.inv(
                    xsel.T @ xsel + ALPHA * np.eye(len(selected))
                )
                beta = ainv @ (xsel.T @ y)
                pred = xsel @ beta
                qmat = xsel.T @ zall
                v = ainv @ qmat
                u = zall - xsel @ v
                h = (
                    np.sum(zall * zall, axis=0)
                    + ALPHA
                    - np.sum(qmat * v, axis=0)
                )
                numer = zall.T @ y - qmat.T @ beta
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


def one_patch_step(xd, yd, selected):
    zall = gaussian_features(xd, CAND_CENTERS, CAND_WIDTHS)
    xsel = zall[:, selected]
    ainv = np.linalg.inv(xsel.T @ xsel + ALPHA * np.eye(len(selected)))
    beta = ainv @ (xsel.T @ yd)
    pred = xsel @ beta
    qmat = xsel.T @ zall
    v = ainv @ qmat
    u = zall - xsel @ v
    h = np.sum(zall * zall, axis=0) + ALPHA - np.sum(qmat * v, axis=0)
    numer = zall.T @ yd - qmat.T @ beta
    gamma = numer / h
    pred_new = pred[:, None] + u * gamma[None, :]
    mse = np.mean((yd[:, None] - pred_new) ** 2, axis=0)
    available = np.ones(len(CAND_WIDTHS), dtype=bool)
    available[selected] = False
    mse[~available] = np.inf
    return int(np.argmin(mse))


def support_meta(support):
    slots = [int(v % 3) for v in support]
    return {
        "candidates": [int(v) for v in support],
        "center_indices": [int(v // 3) for v in support],
        "scale_slots": slots,
        "scale_slot_counts": {
            "S0_0p22": int(slots.count(0)),
            "S1_0p44": int(slots.count(1)),
            "S2_0p88": int(slots.count(2)),
        },
    }


def develop_p8_core(dist_x, held_x, dist_y, held_y):
    support = recruit_support(dist_x, dist_y, OLD_CAPS, rank=8)
    decoders = {}
    cap_supports = {}
    held_predictions = {}
    patch_records = []

    for i in OLD_CAPS:
        beta = fit_decoder(dist_x[i], dist_y[i], support)
        decoders[i] = beta.copy()
        cap_supports[i] = list(support)
        held_predictions[i] = predict_decoder(
            held_x[i], beta, cap_supports[i]
        )

    for new_cap in ADDITION_ORDER:
        beta_try = fit_decoder(dist_x[new_cap], dist_y[new_cap], support)
        pd_try = predict_decoder(dist_x[new_cap], beta_try, support)
        triggered = bool(nmse(pd_try, dist_y[new_cap]) > TRIGGER_NMSE)
        if triggered:
            idx = one_patch_step(
                dist_x[new_cap], dist_y[new_cap], support
            )
            support = list(support) + [idx]
            patch_records.append({
                "triggering_capability": int(new_cap),
                "candidate": int(idx),
            })
        beta_new = fit_decoder(dist_x[new_cap], dist_y[new_cap], support)
        decoders[new_cap] = beta_new.copy()
        cap_supports[new_cap] = list(support)
        held_predictions[new_cap] = predict_decoder(
            held_x[new_cap], beta_new, cap_supports[new_cap]
        )

    old_held_nmse = {}
    old_dist_nmse = {}
    old_ops = {}
    for i in range(8):
        pd = predict_decoder(dist_x[i], decoders[i], cap_supports[i])
        ph = predict_decoder(held_x[i], decoders[i], cap_supports[i])
        old_dist_nmse[i] = nmse(pd, dist_y[i])
        old_held_nmse[i] = nmse(ph, held_y[i])
        old_ops[i] = 2 * len(cap_supports[i])

    return {
        "support": list(support),
        "decoders": decoders,
        "cap_supports": cap_supports,
        "held_predictions": held_predictions,
        "patch_count": len(patch_records),
        "patch_records": patch_records,
        "old_held_nmse": old_held_nmse,
        "old_dist_nmse": old_dist_nmse,
        "old_ops": old_ops,
    }


def fit_policy(support, dist_x, held_x, dist_y, held_y):
    beta = fit_decoder(dist_x[OOD_CAP], dist_y[OOD_CAP], support)
    pd = predict_decoder(dist_x[OOD_CAP], beta, support)
    ph = predict_decoder(held_x[OOD_CAP], beta, support)
    return {
        "dist_nmse": nmse(pd, dist_y[OOD_CAP]),
        "held_nmse": nmse(ph, held_y[OOD_CAP]),
    }


def normalized_prediction_drift(before, after):
    return nmse(after, before)


def old_preservation(developed, held_x):
    drift = 0.0
    for i in range(8):
        ph = predict_decoder(
            held_x[i],
            developed["decoders"][i],
            developed["cap_supports"][i],
        )
        drift = max(
            drift,
            normalized_prediction_drift(
                developed["held_predictions"][i], ph
            ),
        )
    return float(drift)


def factor_meta(idx, pre_support, local8_support, joint_support):
    center = CAND_CENTERS[idx]
    pre_centers = CAND_CENTERS[pre_support]
    nearest = float(np.min(np.sqrt(np.sum(
        (pre_centers - center[None, :]) ** 2, axis=1
    ))))
    return {
        "candidate": int(idx),
        "center_index": int(idx // 3),
        "scale_slot": int(idx % 3),
        "width": float(CAND_WIDTHS[idx]),
        "nearest_prepatch_center_distance": nearest,
        "in_ood_local8_support": bool(idx in set(local8_support)),
        "in_joint_refit8_support": bool(idx in set(joint_support)),
    }


def one_world(seed):
    dist_x, held_x, dist_y, held_y = build_world_data(seed)
    developed = develop_p8_core(dist_x, held_x, dist_y, held_y)
    developed_support = list(developed["support"])

    local8_support = recruit_support(
        dist_x, dist_y, (OOD_CAP,), rank=8
    )
    local8 = fit_policy(
        local8_support, dist_x, held_x, dist_y, held_y
    )

    joint_support = recruit_support(
        dist_x, dist_y, tuple(range(9)), rank=8
    )
    joint = fit_policy(
        joint_support, dist_x, held_x, dist_y, held_y
    )

    patch0 = fit_policy(
        developed_support, dist_x, held_x, dist_y, held_y
    )

    idx1 = one_patch_step(
        dist_x[OOD_CAP], dist_y[OOD_CAP], developed_support
    )
    support1 = developed_support + [idx1]
    patch1 = fit_policy(
        support1, dist_x, held_x, dist_y, held_y
    )

    idx2 = one_patch_step(
        dist_x[OOD_CAP], dist_y[OOD_CAP], support1
    )
    support2 = support1 + [idx2]
    patch2 = fit_policy(
        support2, dist_x, held_x, dist_y, held_y
    )

    old_vals = [developed["old_held_nmse"][i] for i in range(8)]
    drift = old_preservation(developed, held_x)

    def finalize(policy, support, patch_count):
        vals = old_vals + [policy["held_nmse"]]
        reduction = (
            (patch0["held_nmse"] - policy["held_nmse"])
            / (patch0["held_nmse"] + 1e-12)
        )
        return {
            "ood_dist_nmse": float(policy["dist_nmse"]),
            "ood_held_nmse": float(policy["held_nmse"]),
            "ood_generalization_gap": float(
                policy["held_nmse"] - policy["dist_nmse"]
            ),
            "ood_error_reduction_vs_patch0": float(reduction),
            "ood_gap_vs_local8": float(
                policy["held_nmse"] - local8["held_nmse"]
            ),
            "ood_gap_vs_joint_refit8": float(
                policy["held_nmse"] - joint["held_nmse"]
            ),
            "world_mean_nmse": float(np.mean(vals)),
            "world_worst_nmse": float(np.max(vals)),
            "old_prediction_drift_max": drift,
            "old_decoder_max_abs_change": 0.0,
            "factor_count": int(len(support)),
            "ood_decoder_scalars": int(len(support)),
            "ood_residual_ops": int(2 * len(support)),
            "shared_factor_growth": int(patch_count),
        }

    return {
        "seed": int(seed),
        "pre_ood": {
            "in_distribution_patch_count": int(developed["patch_count"]),
            "developed_shared_factor_count": int(len(developed_support)),
            "old_cap_residual_ops": {
                str(i): int(developed["old_ops"][i]) for i in range(8)
            },
        },
        "PATCH0": finalize(patch0, developed_support, 0),
        "PATCH1": finalize(patch1, support1, 1),
        "PATCH2": finalize(patch2, support2, 2),
        "PATCH1_factor": factor_meta(
            idx1, developed_support, local8_support, joint_support
        ),
        "PATCH2_factors": [
            factor_meta(
                idx1, developed_support, local8_support, joint_support
            ),
            factor_meta(
                idx2, support1, local8_support, joint_support
            ),
        ],
        "OOD_LOCAL8": {
            "ood_dist_nmse": float(local8["dist_nmse"]),
            "ood_held_nmse": float(local8["held_nmse"]),
            "support": support_meta(local8_support),
        },
        "JOINT_REFIT8": {
            "ood_dist_nmse": float(joint["dist_nmse"]),
            "ood_held_nmse": float(joint["held_nmse"]),
            "support": support_meta(joint_support),
        },
    }


def q(values, p):
    return float(np.quantile(np.asarray(values, dtype=np.float64), p))


def policy_summary(rows, name):
    pr = [r[name] for r in rows]
    return {
        "ood_dist_nmse_median": q([r["ood_dist_nmse"] for r in pr], 0.5),
        "ood_held_nmse_median": q([r["ood_held_nmse"] for r in pr], 0.5),
        "ood_held_nmse_p90": q([r["ood_held_nmse"] for r in pr], 0.90),
        "ood_generalization_gap_median": q([
            r["ood_generalization_gap"] for r in pr
        ], 0.5),
        "ood_error_reduction_vs_patch0_median": q([
            r["ood_error_reduction_vs_patch0"] for r in pr
        ], 0.5),
        "ood_gap_vs_local8_median": q([
            r["ood_gap_vs_local8"] for r in pr
        ], 0.5),
        "ood_gap_vs_joint_refit8_median": q([
            r["ood_gap_vs_joint_refit8"] for r in pr
        ], 0.5),
        "world_mean_nmse_median": q([r["world_mean_nmse"] for r in pr], 0.5),
        "world_worst_nmse_median": q([r["world_worst_nmse"] for r in pr], 0.5),
        "old_prediction_drift_max": float(np.max([
            r["old_prediction_drift_max"] for r in pr
        ])),
        "old_decoder_max_abs_change": float(np.max([
            r["old_decoder_max_abs_change"] for r in pr
        ])),
        "factor_count_median": q([r["factor_count"] for r in pr], 0.5),
        "ood_residual_ops_median": q([r["ood_residual_ops"] for r in pr], 0.5),
    }


def robust_elastic(s):
    return (
        s["ood_held_nmse_median"] <= 0.05
        and s["ood_error_reduction_vs_patch0_median"] >= 0.50
        and s["ood_gap_vs_local8_median"] <= 0.04
        and s["old_prediction_drift_max"] <= 1e-12
        and s["old_decoder_max_abs_change"] == 0.0
        and s["ood_generalization_gap_median"] <= 0.05
    )


def summarize(rows):
    local8_med = q(
        [r["OOD_LOCAL8"]["ood_held_nmse"] for r in rows], 0.5
    )
    joint_med = q(
        [r["JOINT_REFIT8"]["ood_held_nmse"] for r in rows], 0.5
    )
    policies = {
        name: policy_summary(rows, name)
        for name in ("PATCH0", "PATCH1", "PATCH2")
    }
    dictionary_capable = bool(local8_med <= 0.05)
    p1_ok = dictionary_capable and robust_elastic(policies["PATCH1"])
    p2_ok = dictionary_capable and robust_elastic(policies["PATCH2"])

    if not dictionary_capable:
        classification = "DICTIONARY_FAMILY_LIMIT"
    elif p1_ok:
        classification = "PATCH1_ROBUST_ELASTIC"
    elif p2_ok:
        classification = "PATCH2_ROBUST_ELASTIC"
    elif (
        policies["PATCH2"]["ood_held_nmse_median"] > 0.05
        or policies["PATCH2"]["ood_gap_vs_local8_median"] > 0.04
    ):
        classification = "PATCH_BUDGET_LIMIT"
    else:
        classification = "MIXED"

    patch1_meta = [r["PATCH1_factor"] for r in rows]
    patch2_meta = [f for r in rows for f in r["PATCH2_factors"]]

    return {
        "worlds": len(rows),
        "dictionary_capable": dictionary_capable,
        "classification": classification,
        "pre_ood_in_distribution_patch_count_median": q([
            r["pre_ood"]["in_distribution_patch_count"] for r in rows
        ], 0.5),
        "pre_ood_shared_factor_count_median": q([
            r["pre_ood"]["developed_shared_factor_count"] for r in rows
        ], 0.5),
        "oldest_cap_residual_ops_median": q([
            r["pre_ood"]["old_cap_residual_ops"]["0"] for r in rows
        ], 0.5),
        "newest_pre_ood_cap_residual_ops_median": q([
            r["pre_ood"]["old_cap_residual_ops"]["7"] for r in rows
        ], 0.5),
        "OOD_LOCAL8": {
            "ood_held_nmse_median": local8_med,
            "ood_dist_nmse_median": q([
                r["OOD_LOCAL8"]["ood_dist_nmse"] for r in rows
            ], 0.5),
        },
        "JOINT_REFIT8": {
            "ood_held_nmse_median": joint_med,
            "ood_dist_nmse_median": q([
                r["JOINT_REFIT8"]["ood_dist_nmse"] for r in rows
            ], 0.5),
        },
        "policies": policies,
        "patch1_geometry": {
            "scale_slot_counts": {
                "S0_0p22": int(sum(f["scale_slot"] == 0 for f in patch1_meta)),
                "S1_0p44": int(sum(f["scale_slot"] == 1 for f in patch1_meta)),
                "S2_0p88": int(sum(f["scale_slot"] == 2 for f in patch1_meta)),
            },
            "nearest_prepatch_center_distance_median": q([
                f["nearest_prepatch_center_distance"] for f in patch1_meta
            ], 0.5),
            "ood_local8_overlap_rate": float(np.mean([
                f["in_ood_local8_support"] for f in patch1_meta
            ])),
            "joint_refit8_overlap_rate": float(np.mean([
                f["in_joint_refit8_support"] for f in patch1_meta
            ])),
        },
        "patch2_geometry": {
            "scale_slot_counts": {
                "S0_0p22": int(sum(f["scale_slot"] == 0 for f in patch2_meta)),
                "S1_0p44": int(sum(f["scale_slot"] == 1 for f in patch2_meta)),
                "S2_0p88": int(sum(f["scale_slot"] == 2 for f in patch2_meta)),
            },
            "nearest_prepatch_center_distance_median": q([
                f["nearest_prepatch_center_distance"] for f in patch2_meta
            ], 0.5),
            "ood_local8_overlap_rate": float(np.mean([
                f["in_ood_local8_support"] for f in patch2_meta
            ])),
            "joint_refit8_overlap_rate": float(np.mean([
                f["in_joint_refit8_support"] for f in patch2_meta
            ])),
        },
    }


def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def run():
    rows = [one_world(WORLD_START + i) for i in range(WORLD_COUNT)]
    return {
        "schema": "yggdrasil.h191-p9-ood-elastic-core-expansion.v1",
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
