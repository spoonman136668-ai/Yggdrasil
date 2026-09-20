#!/usr/bin/env python3
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

ALPHA = 0.001
SCALES = np.asarray([0.22, 0.44, 0.88], dtype=np.float64)
WORLD_START = 20260925100000
WORLD_COUNT = 6
TRIGGER_NMSE = 0.02
OLD_CAPS = (0, 1, 2)
IN_DIST_ADDITION_ORDER = (3, 4, 5, 6, 7)
OOD_CAPS = (8, 9, 10, 11)
OOD_LABELS = ("OOD8", "OOD9", "OOD10", "OOD11")
OOD_CENTERS = np.asarray([
    (0.00, 0.00),
    (0.18, 0.00),
    (0.00, 0.18),
    (-0.18, 0.00),
], dtype=np.float64)
OOD_SD = 0.08
OOD_RADIUS_MAX = 0.40
OOD_FREQ_MIN = 5.0
OOD_FREQ_MAX = 8.0


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


def ridge_fit(x, y):
    k = x.shape[1]
    return np.linalg.solve(x.T @ x + ALPHA * np.eye(k), x.T @ y)


def nmse(yhat, y):
    return float(np.mean((yhat - y) ** 2) / (float(np.var(y)) + 1e-12))


def ring_centers():
    ang = 2.0 * math.pi * np.arange(8, dtype=np.float64) / 8.0
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


def sample_ood_context(rng, local_i, n):
    chunks = []
    have = 0
    center = OOD_CENTERS[local_i]
    while have < n:
        draw_n = max(64, (n - have) * 4)
        p = rng.normal(loc=center, scale=OOD_SD, size=(draw_n, 2))
        p = p[np.sum(p * p, axis=1) <= OOD_RADIUS_MAX * OOD_RADIUS_MAX]
        if len(p):
            d2 = ((p[:, None, :] - OOD_CENTERS[None, :, :]) ** 2).sum(axis=2)
            p = p[np.argmin(d2, axis=1) == local_i]
        if len(p):
            take = min(n - have, len(p))
            chunks.append(p[:take])
            have += take
    return np.concatenate(chunks, axis=0)


def source_params(rng):
    centers = uniform_disk(rng, 8)
    sigmas = rng.uniform(0.12, 0.42, size=8)
    dec = rng.normal(0.0, 1.0, size=(8, 12))
    sins = []
    for cap_i in range(12):
        a = rng.uniform(0.5, 1.5)
        if cap_i < 8:
            wx = rng.uniform(1.0, 4.0)
            wy = rng.uniform(1.0, 4.0)
        else:
            wx = rng.uniform(OOD_FREQ_MIN, OOD_FREQ_MAX)
            wy = rng.uniform(OOD_FREQ_MIN, OOD_FREQ_MAX)
        phase = rng.uniform(0.0, 2.0 * math.pi)
        sins.append((a, wx, wy, phase))
    return centers, sigmas, dec, sins


def raw_residual(x, cap_i, params):
    centers, sigmas, dec, sins = params
    shared = gaussian_features(x, centers, sigmas) @ dec[:, cap_i]
    a, wx, wy, phase = sins[cap_i]
    return shared + 0.10 * a * np.sin(wx * x[:, 0] + wy * x[:, 1] + phase)


def build_world_data(seed):
    rng = np.random.default_rng(np.random.PCG64(seed))
    rcenters = ring_centers()
    params = source_params(rng)
    dist_x, held_x, dist_y, held_y = [], [], [], []
    for cap_i in range(12):
        if cap_i < 8:
            pts = sample_ring_context(rng, rcenters, cap_i, 640)
        else:
            pts = sample_ood_context(rng, cap_i - 8, 640)
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
    return ridge_fit(gaussian_features(x, CAND_CENTERS[support], CAND_WIDTHS[support]), y)


def predict_decoder(x, beta, support):
    return gaussian_features(x, CAND_CENTERS[support], CAND_WIDTHS[support]) @ beta


def recruit_support(dist_x, dist_y, active, rank=8):
    zd = {i: gaussian_features(dist_x[i], CAND_CENTERS, CAND_WIDTHS) for i in active}
    selected = []
    available = np.ones(len(CAND_WIDTHS), dtype=bool)
    for _ in range(rank):
        total = np.zeros(len(CAND_WIDTHS), dtype=np.float64)
        for i in active:
            y = dist_y[i]
            zall = zd[i]
            if not selected:
                gamma = (zall.T @ y) / (np.sum(zall * zall, axis=0) + ALPHA)
                pred_new = zall * gamma[None, :]
            else:
                xsel = zall[:, selected]
                ainv = np.linalg.inv(xsel.T @ xsel + ALPHA * np.eye(len(selected)))
                beta = ainv @ (xsel.T @ y)
                pred = xsel @ beta
                qmat = xsel.T @ zall
                v = ainv @ qmat
                u = zall - xsel @ v
                h = np.sum(zall * zall, axis=0) + ALPHA - np.sum(qmat * v, axis=0)
                gamma = (zall.T @ y - qmat.T @ beta) / h
                pred_new = pred[:, None] + u * gamma[None, :]
            total += np.mean((y[:, None] - pred_new) ** 2, axis=0) / (float(np.var(y)) + 1e-12)
        total /= float(len(active))
        total[~available] = np.inf
        idx = int(np.argmin(total))
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
    gamma = (zall.T @ yd - qmat.T @ beta) / h
    pred_new = pred[:, None] + u * gamma[None, :]
    mse = np.mean((yd[:, None] - pred_new) ** 2, axis=0)
    available = np.ones(len(CAND_WIDTHS), dtype=bool)
    available[selected] = False
    mse[~available] = np.inf
    return int(np.argmin(mse))


def develop_base(dist_x, held_x, dist_y):
    support = recruit_support(dist_x, dist_y, OLD_CAPS, 8)
    decoders = {}
    supports = {}
    predictions = {}
    patches = 0
    for i in OLD_CAPS:
        beta = fit_decoder(dist_x[i], dist_y[i], support)
        decoders[i] = beta.copy()
        supports[i] = list(support)
        predictions[i] = predict_decoder(held_x[i], beta, supports[i])
    for cap in IN_DIST_ADDITION_ORDER:
        beta_try = fit_decoder(dist_x[cap], dist_y[cap], support)
        pd_try = predict_decoder(dist_x[cap], beta_try, support)
        if nmse(pd_try, dist_y[cap]) > TRIGGER_NMSE:
            support = list(support) + [one_patch_step(dist_x[cap], dist_y[cap], support)]
            patches += 1
        beta = fit_decoder(dist_x[cap], dist_y[cap], support)
        decoders[cap] = beta.copy()
        supports[cap] = list(support)
        predictions[cap] = predict_decoder(held_x[cap], beta, supports[cap])
    return support, decoders, supports, predictions, patches


def old_drift(decoders, supports, predictions, held_x, upto):
    drift = 0.0
    for i in range(upto):
        ph = predict_decoder(held_x[i], decoders[i], supports[i])
        drift = max(drift, nmse(ph, predictions[i]))
    return float(drift)


def patch_meta(idx, pre_support, local8_support, cap):
    center = CAND_CENTERS[idx]
    pre = CAND_CENTERS[pre_support]
    return {
        "triggering_capability": int(cap),
        "candidate": int(idx),
        "center_index": int(idx // 3),
        "scale_slot": int(idx % 3),
        "center_radius": float(np.sqrt(np.sum(center * center))),
        "nearest_existing_center_distance": float(np.min(np.sqrt(np.sum((pre - center[None, :]) ** 2, axis=1)))),
        "in_ood_local8_support": bool(idx in set(local8_support)),
    }


def one_world(seed):
    dist_x, held_x, dist_y, held_y = build_world_data(seed)
    support, decoders, supports, predictions, base_patch_count = develop_base(dist_x, held_x, dist_y)
    pre_ood_factor_count = len(support)
    stages = {}
    ood_patch_records = []
    ood_patch_count = 0

    for label, cap in zip(OOD_LABELS, OOD_CAPS):
        local8_support = recruit_support(dist_x, dist_y, (cap,), 8)
        local8_beta = fit_decoder(dist_x[cap], dist_y[cap], local8_support)
        local8_pd = predict_decoder(dist_x[cap], local8_beta, local8_support)
        local8_ph = predict_decoder(held_x[cap], local8_beta, local8_support)
        local8_dist = nmse(local8_pd, dist_y[cap])
        local8_held = nmse(local8_ph, held_y[cap])

        pre_support = list(support)
        beta_try = fit_decoder(dist_x[cap], dist_y[cap], pre_support)
        pd_try = predict_decoder(dist_x[cap], beta_try, pre_support)
        ph_try = predict_decoder(held_x[cap], beta_try, pre_support)
        decoder_only_dist = nmse(pd_try, dist_y[cap])
        decoder_only_held = nmse(ph_try, held_y[cap])
        triggered = decoder_only_dist > TRIGGER_NMSE
        patch = None

        if triggered:
            idx = one_patch_step(dist_x[cap], dist_y[cap], support)
            support = list(support) + [idx]
            ood_patch_count += 1
            patch = patch_meta(idx, pre_support, local8_support, cap)
            ood_patch_records.append(patch)

        beta = fit_decoder(dist_x[cap], dist_y[cap], support)
        decoders[cap] = beta.copy()
        supports[cap] = list(support)
        pd = predict_decoder(dist_x[cap], beta, supports[cap])
        ph = predict_decoder(held_x[cap], beta, supports[cap])
        predictions[cap] = ph.copy()

        post_dist = nmse(pd, dist_y[cap])
        post_held = nmse(ph, held_y[cap])
        reduction = (decoder_only_held - post_held) / (decoder_only_held + 1e-12)

        stages[label] = {
            "capability": int(cap),
            "decoder_only_dist_nmse": float(decoder_only_dist),
            "decoder_only_held_nmse": float(decoder_only_held),
            "triggered_patch": bool(triggered),
            "patch": patch,
            "post_rule_dist_nmse": float(post_dist),
            "post_rule_held_nmse": float(post_held),
            "ood_local8_dist_nmse": float(local8_dist),
            "ood_local8_held_nmse": float(local8_held),
            "gap_vs_ood_local8": float(post_held - local8_held),
            "error_reduction_vs_decoder_only": float(reduction),
            "cumulative_ood_patch_count": int(ood_patch_count),
            "shared_factor_count": int(len(support)),
            "new_cap_active_factor_count": int(len(supports[cap])),
            "new_cap_residual_ops": int(2 * len(supports[cap])),
            "oldest_cap_residual_ops": int(2 * len(supports[0])),
            "previous_ood_residual_ops": {
                str(i): int(2 * len(supports[i])) for i in OOD_CAPS if i < cap
            },
            "old_prediction_drift_max": old_drift(decoders, supports, predictions, held_x, cap),
            "old_decoder_max_abs_change": 0.0,
        }

    return {
        "seed": int(seed),
        "pre_ood": {
            "in_distribution_patch_count": int(base_patch_count),
            "shared_factor_count": int(pre_ood_factor_count),
            "oldest_cap_residual_ops": int(2 * len(supports[0])),
            "newest_ring_cap_residual_ops": int(2 * len(supports[7])),
        },
        "stages": stages,
        "ood_patch_records": ood_patch_records,
        "final_ood_patch_count": int(ood_patch_count),
        "final_shared_factor_count": int(len(support)),
        "ood_patches_per_capability": float(ood_patch_count / len(OOD_CAPS)),
        "final_ops": {
            "cap0": int(2 * len(supports[0])),
            "ood8": int(2 * len(supports[8])),
            "ood11": int(2 * len(supports[11])),
        },
    }


def q(values, p):
    return float(np.quantile(np.asarray(values, dtype=np.float64), p))


def summarize_stage(rows, label):
    s = [r["stages"][label] for r in rows]
    held_med = q([x["post_rule_held_nmse"] for x in s], 0.5)
    gap_med = q([x["gap_vs_ood_local8"] for x in s], 0.5)
    drift_max = float(np.max([x["old_prediction_drift_max"] for x in s]))
    dchange = float(np.max([x["old_decoder_max_abs_change"] for x in s]))
    if held_med <= 0.05 and gap_med <= 0.04 and drift_max <= 1e-12 and dchange == 0.0:
        regime = "ROBUST"
    elif held_med > 0.10 and gap_med > 0.08:
        regime = "OVER_CAPACITY"
    elif (0.05 < held_med <= 0.10) or (0.04 < gap_med <= 0.08):
        regime = "TRANSITION"
    else:
        regime = "MIXED_UNCLASSIFIED"
    return {
        "mechanical_regime": regime,
        "patch_trigger_rate": float(np.mean([x["triggered_patch"] for x in s])),
        "decoder_only_dist_nmse_median": q([x["decoder_only_dist_nmse"] for x in s], 0.5),
        "post_rule_dist_nmse_median": q([x["post_rule_dist_nmse"] for x in s], 0.5),
        "post_rule_held_nmse_median": held_med,
        "post_rule_held_nmse_p90": q([x["post_rule_held_nmse"] for x in s], 0.90),
        "ood_local8_held_nmse_median": q([x["ood_local8_held_nmse"] for x in s], 0.5),
        "gap_vs_ood_local8_median": gap_med,
        "error_reduction_vs_decoder_only_median": q([x["error_reduction_vs_decoder_only"] for x in s], 0.5),
        "cumulative_ood_patch_count_median": q([x["cumulative_ood_patch_count"] for x in s], 0.5),
        "shared_factor_count_median": q([x["shared_factor_count"] for x in s], 0.5),
        "new_cap_residual_ops_median": q([x["new_cap_residual_ops"] for x in s], 0.5),
        "oldest_cap_residual_ops_median": q([x["oldest_cap_residual_ops"] for x in s], 0.5),
        "old_prediction_drift_max": drift_max,
        "old_decoder_max_abs_change": dchange,
    }


def summarize(rows):
    stages = {label: summarize_stage(rows, label) for label in OOD_LABELS}
    final_patches = [r["final_ood_patch_count"] for r in rows]
    med_patches = q(final_patches, 0.5)
    all_avoid_over = all(stages[l]["mechanical_regime"] != "OVER_CAPACITY" for l in OOD_LABELS)
    all_robust = all(stages[l]["mechanical_regime"] == "ROBUST" for l in OOD_LABELS)
    drift_max = max(stages[l]["old_prediction_drift_max"] for l in OOD_LABELS)
    dchange_max = max(stages[l]["old_decoder_max_abs_change"] for l in OOD_LABELS)
    reuse = all_avoid_over and drift_max <= 1e-12 and dchange_max == 0.0 and med_patches < 4.0
    strong = all_robust and med_patches <= 2.0

    patches = [p for r in rows for p in r["ood_patch_records"]]
    return {
        "worlds": len(rows),
        "stages": stages,
        "pre_ood_in_distribution_patch_count_median": q([r["pre_ood"]["in_distribution_patch_count"] for r in rows], 0.5),
        "pre_ood_shared_factor_count_median": q([r["pre_ood"]["shared_factor_count"] for r in rows], 0.5),
        "final_ood_patch_count_median": med_patches,
        "final_ood_patch_count_p90": q(final_patches, 0.90),
        "final_shared_factor_count_median": q([r["final_shared_factor_count"] for r in rows], 0.5),
        "ood_patches_per_capability_median": q([r["ood_patches_per_capability"] for r in rows], 0.5),
        "repeated_ood_reuse_encouragement": bool(reuse),
        "strong_mechanical_signal": bool(strong),
        "final_oldest_cap_residual_ops_median": q([r["final_ops"]["cap0"] for r in rows], 0.5),
        "final_ood8_residual_ops_median": q([r["final_ops"]["ood8"] for r in rows], 0.5),
        "final_ood11_residual_ops_median": q([r["final_ops"]["ood11"] for r in rows], 0.5),
        "old_prediction_drift_max": float(drift_max),
        "old_decoder_max_abs_change": float(dchange_max),
        "patch_scale_slot_counts": {
            "S0_0p22": int(sum(p["scale_slot"] == 0 for p in patches)),
            "S1_0p44": int(sum(p["scale_slot"] == 1 for p in patches)),
            "S2_0p88": int(sum(p["scale_slot"] == 2 for p in patches)),
        },
        "patch_center_radius_median": q([p["center_radius"] for p in patches], 0.5) if patches else 0.0,
        "patch_nearest_existing_center_distance_median": q([p["nearest_existing_center_distance"] for p in patches], 0.5) if patches else 0.0,
        "patch_ood_local8_overlap_rate": float(np.mean([p["in_ood_local8_support"] for p in patches])) if patches else 0.0,
    }


def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def run():
    rows = [one_world(WORLD_START + i) for i in range(WORLD_COUNT)]
    return {
        "schema": "yggdrasil.h191-p10-repeated-ood-patch-reuse.v1",
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
