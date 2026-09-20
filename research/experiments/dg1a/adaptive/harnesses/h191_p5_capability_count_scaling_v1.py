#!/usr/bin/env python3
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path

import numpy as np

BASE_NAME = "h191_p0_surrogate_mechanical_v1.py"
ALPHA = 0.001
SCALES = np.asarray([0.22, 0.44, 0.88], dtype=np.float64)
CONTEXT_RADIUS = 0.60
CONTEXT_SD = 0.14
SOURCE_FACTORS = 8
REMAINDER = 0.10
WORLD_COUNT = 6
CONDITIONS = (
    ("CAP3", 3, 20260924600000),
    ("CAP4", 4, 20260924610000),
    ("CAP5", 5, 20260924620000),
    ("CAP6", 6, 20260924630000),
    ("CAP8", 8, 20260924640000),
)


def load_base():
    path = Path(__file__).resolve().parent / BASE_NAME
    spec = importlib.util.spec_from_file_location("h191_p0_base", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def context_centers(k):
    ang = 2.0 * math.pi * np.arange(k, dtype=np.float64) / float(k)
    return np.column_stack((CONTEXT_RADIUS * np.cos(ang), CONTEXT_RADIUS * np.sin(ang)))


def sample_context(rng, centers, cap_i, n):
    chunks = []
    have = 0
    center = centers[cap_i]
    while have < n:
        draw_n = max(64, (n - have) * 3)
        p = rng.normal(loc=center, scale=CONTEXT_SD, size=(draw_n, 2))
        disk = np.sum(p * p, axis=1) <= 1.0
        p = p[disk]
        if len(p):
            d2 = ((p[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
            owner = np.argmin(d2, axis=1)
            p = p[owner == cap_i]
        if len(p):
            take = min(n - have, len(p))
            chunks.append(p[:take])
            have += take
    return np.concatenate(chunks, axis=0)


def source_params(base, rng, k):
    centers = base.uniform_disk(rng, SOURCE_FACTORS)
    sigmas = rng.uniform(0.12, 0.42, size=SOURCE_FACTORS)
    dec = rng.normal(0.0, 1.0, size=(SOURCE_FACTORS, k))
    sins = []
    for _ in range(k):
        a = rng.uniform(0.5, 1.5)
        wx = rng.uniform(1.0, 4.0)
        wy = rng.uniform(1.0, 4.0)
        phase = rng.uniform(0.0, 2.0 * math.pi)
        sins.append((a, wx, wy, phase))
    return centers, sigmas, dec, sins


def raw_residual(base, x, cap_i, params):
    centers, sigmas, dec, sins = params
    z = base.gaussian_features(x, centers, sigmas)
    shared = z @ dec[:, cap_i]
    a, wx, wy, phase = sins[cap_i]
    extra = REMAINDER * a * np.sin(wx * x[:, 0] + wy * x[:, 1] + phase)
    return shared + extra


def proxy8_fit(base, xd, yd, xh, yh):
    phi_d = base.rbf_features(xd, base.PARENT, base.PARENT_SIGMA)
    phi_h = base.rbf_features(xh, base.PARENT, base.PARENT_SIGMA)
    energy = np.sum(phi_d * phi_d, axis=0) + ALPHA
    chosen = []
    pred = np.zeros_like(yd)
    available = np.ones(base.PARENT.shape[0], dtype=bool)
    beta = np.empty(0, dtype=np.float64)
    for _ in range(8):
        residual = yd - pred
        corr = phi_d.T @ residual
        score = (corr * corr) / energy
        score[~available] = -np.inf
        idx = int(np.argmax(score))
        chosen.append(idx)
        available[idx] = False
        xs = phi_d[:, chosen]
        beta = base.ridge_fit(xs, yd, ALPHA)
        pred = xs @ beta
    held = phi_h[:, chosen] @ beta
    return {
        "dist_nmse": base.nmse(pred, yd),
        "held_nmse": base.nmse(held, yh),
        "sites": [int(v) for v in chosen],
    }


def dict8_fit(base, dist_x, dist_y, held_x, held_y):
    k = len(dist_x)
    cand_centers = np.repeat(base.PARENT, 3, axis=0)
    cand_widths = np.tile(SCALES, base.PARENT.shape[0])
    m = len(cand_widths)
    zd = [base.gaussian_features(dist_x[i], cand_centers, cand_widths) for i in range(k)]

    selected = []
    available = np.ones(m, dtype=bool)

    for _ in range(8):
        total_score = np.zeros(m, dtype=np.float64)
        for i in range(k):
            y = dist_y[i]
            zall = zd[i]
            if not selected:
                denom = np.sum(zall * zall, axis=0) + ALPHA
                gamma = (zall.T @ y) / denom
                pred_new = zall * gamma[None, :]
            else:
                xsel = zall[:, selected]
                ata = xsel.T @ xsel + ALPHA * np.eye(len(selected))
                ainv = np.linalg.inv(ata)
                xty = xsel.T @ y
                beta = ainv @ xty
                pred = xsel @ beta
                q = xsel.T @ zall
                v = ainv @ q
                u = zall - xsel @ v
                h = np.sum(zall * zall, axis=0) + ALPHA - np.sum(q * v, axis=0)
                numer = zall.T @ y - q.T @ beta
                gamma = numer / h
                pred_new = pred[:, None] + u * gamma[None, :]
            mse = np.mean((y[:, None] - pred_new) ** 2, axis=0)
            total_score += mse / (float(np.var(y)) + 1e-12)
        total_score /= float(k)
        total_score[~available] = np.inf
        idx = int(np.argmin(total_score))
        selected.append(idx)
        available[idx] = False

    sel_centers = cand_centers[selected]
    sel_widths = cand_widths[selected]
    held_nmse = []
    dist_nmse = []
    decoders = []
    for i in range(k):
        xs = zd[i][:, selected]
        beta = base.ridge_fit(xs, dist_y[i], ALPHA)
        decoders.append(beta)
        pd = xs @ beta
        zh = base.gaussian_features(held_x[i], sel_centers, sel_widths)
        ph = zh @ beta
        dist_nmse.append(base.nmse(pd, dist_y[i]))
        held_nmse.append(base.nmse(ph, held_y[i]))

    dmat = np.stack(decoders, axis=1)
    absd = np.abs(dmat)
    denom = np.sum(absd, axis=1) + 1e-12
    concentration = np.max(absd, axis=1) / denom
    p = absd / denom[:, None]
    effective_participation = 1.0 / (np.sum(p * p, axis=1) + 1e-12)

    dd = np.sqrt(((sel_centers[:, None, :] - sel_centers[None, :, :]) ** 2).sum(axis=2))
    tri = dd[np.triu_indices(len(sel_centers), 1)]
    slot_counts = [0, 0, 0]
    for idx in selected:
        slot_counts[int(idx % 3)] += 1

    return {
        "dist_nmse": [float(v) for v in dist_nmse],
        "held_nmse": [float(v) for v in held_nmse],
        "selected_candidates": [int(v) for v in selected],
        "selected_center_indices": [int(v // 3) for v in selected],
        "selected_width_slots": [int(v % 3) for v in selected],
        "decoder_concentration_mean": float(np.mean(concentration)),
        "effective_decoder_participation_mean": float(np.mean(effective_participation)),
        "center_spread": float(np.mean(tri)),
        "slot_counts": [int(v) for v in slot_counts],
    }


def one_world(base, seed, k):
    rng = np.random.default_rng(np.random.PCG64(seed))
    centers = context_centers(k)
    params = source_params(base, rng, k)

    dist_x = []
    held_x = []
    dist_y = []
    held_y = []
    proxies = []

    for cap_i in range(k):
        pts = sample_context(rng, centers, cap_i, 128 + 512)
        xd = pts[:128]
        xh = pts[128:]
        yd = raw_residual(base, xd, cap_i, params)
        yh = raw_residual(base, xh, cap_i, params)
        scale = float(np.sqrt(np.mean(yd * yd)))
        if scale < 1e-12:
            scale = 1.0
        yd = yd / scale
        yh = yh / scale
        dist_x.append(xd)
        held_x.append(xh)
        dist_y.append(yd)
        held_y.append(yh)
        proxies.append(proxy8_fit(base, xd, yd, xh, yh))

    shared = dict8_fit(base, dist_x, dist_y, held_x, held_y)

    return {
        "seed": int(seed),
        "capability_count": int(k),
        "proxy8": {
            "held_nmse": [float(v["held_nmse"]) for v in proxies],
            "dist_nmse": [float(v["dist_nmse"]) for v in proxies],
            "sites": [v["sites"] for v in proxies],
        },
        "dict8": shared,
    }


def q(values, p):
    return float(np.quantile(np.asarray(values, dtype=np.float64), p))


def summarize(rows, k):
    p_world_mean = [float(np.mean(r["proxy8"]["held_nmse"])) for r in rows]
    d_world_mean = [float(np.mean(r["dict8"]["held_nmse"])) for r in rows]
    p_world_worst = [float(np.max(r["proxy8"]["held_nmse"])) for r in rows]
    d_world_worst = [float(np.max(r["dict8"]["held_nmse"])) for r in rows]
    deltas = [d - p for d, p in zip(d_world_mean, p_world_mean)]

    p_flat = [v for r in rows for v in r["proxy8"]["held_nmse"]]
    d_flat = [v for r in rows for v in r["dict8"]["held_nmse"]]

    p_gap = [
        float(np.mean(np.asarray(r["proxy8"]["held_nmse"]) - np.asarray(r["proxy8"]["dist_nmse"])))
        for r in rows
    ]
    d_gap = [
        float(np.mean(np.asarray(r["dict8"]["held_nmse"]) - np.asarray(r["dict8"]["dist_nmse"])))
        for r in rows
    ]

    delta_med = q(deltas, 0.5)
    win = float(np.mean(np.asarray(deltas) < 0.0))
    if delta_med <= 0.0 and win >= 0.50:
        regime = "ROBUST"
    elif delta_med > 0.03 and win < 0.25:
        regime = "OVER_CAPACITY"
    elif (0.0 < delta_med <= 0.03) or (0.25 <= win < 0.50):
        regime = "TRANSITION"
    else:
        regime = "MIXED_UNCLASSIFIED"

    slot_counts = np.sum(np.asarray([r["dict8"]["slot_counts"] for r in rows]), axis=0)

    return {
        "worlds": len(rows),
        "capability_count": int(k),
        "mechanical_regime": regime,
        "methods": {
            "PROXY8": {
                "capability_row_median": q(p_flat, 0.5),
                "world_mean_median": q(p_world_mean, 0.5),
                "world_mean_p90": q(p_world_mean, 0.90),
                "world_worst_median": q(p_world_worst, 0.5),
                "world_worst_p90": q(p_world_worst, 0.90),
                "all_caps_le_0p01_rate": float(np.mean([
                    all(v <= 0.01 for v in r["proxy8"]["held_nmse"]) for r in rows
                ])),
                "all_caps_le_0p02_rate": float(np.mean([
                    all(v <= 0.02 for v in r["proxy8"]["held_nmse"]) for r in rows
                ])),
                "mean_dist_to_held_gap_median": q(p_gap, 0.5),
            },
            "DICT8": {
                "capability_row_median": q(d_flat, 0.5),
                "world_mean_median": q(d_world_mean, 0.5),
                "world_mean_p90": q(d_world_mean, 0.90),
                "world_worst_median": q(d_world_worst, 0.5),
                "world_worst_p90": q(d_world_worst, 0.90),
                "all_caps_le_0p01_rate": float(np.mean([
                    all(v <= 0.01 for v in r["dict8"]["held_nmse"]) for r in rows
                ])),
                "all_caps_le_0p02_rate": float(np.mean([
                    all(v <= 0.02 for v in r["dict8"]["held_nmse"]) for r in rows
                ])),
                "mean_dist_to_held_gap_median": q(d_gap, 0.5),
            },
        },
        "dict8_minus_proxy8": {
            "median": delta_med,
            "p90": q(deltas, 0.90),
            "win_rate": win,
        },
        "dict8_decoder_concentration_median": q(
            [r["dict8"]["decoder_concentration_mean"] for r in rows], 0.5
        ),
        "dict8_effective_decoder_participation_median": q(
            [r["dict8"]["effective_decoder_participation_mean"] for r in rows], 0.5
        ),
        "dict8_center_spread_median": q(
            [r["dict8"]["center_spread"] for r in rows], 0.5
        ),
        "dict8_scale_slot_counts": {
            "S0_0p22": int(slot_counts[0]),
            "S1_0p44": int(slot_counts[1]),
            "S2_0p88": int(slot_counts[2]),
        },
        "memory_compute": {
            "learned_decoder_scalars": int(8 * k),
            "dict8_site_ids": 8,
            "dict8_scale_slots": 8,
            "proxy8_site_ids": int(8 * k),
            "dict8_per_query_residual_ops": 16,
            "proxy8_per_query_residual_ops": 16,
        },
    }


def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def run():
    base = load_base()
    rows = []
    conditions = {}
    for label, k, start in CONDITIONS:
        cr = [one_world(base, start + i, k) for i in range(WORLD_COUNT)]
        for row in cr:
            row["condition"] = label
        rows.extend(cr)
        conditions[label] = summarize(cr, k)
        conditions[label]["seed_start"] = int(start)
        conditions[label]["seed_end"] = int(start + WORLD_COUNT - 1)

    return {
        "schema": "yggdrasil.h191-p5-capability-count-scaling.v1",
        "conditions": conditions,
        "rows": rows,
        "worlds": len(rows),
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
        "conditions": obj["conditions"],
        "worlds": obj["worlds"],
    }))


if __name__ == "__main__":
    main()
