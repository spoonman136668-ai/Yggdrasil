#!/usr/bin/env python3
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

ALPHA = 0.001
PARENT_SIGMA = 0.22
WORLD_START = 20260924190000
WORLD_COUNT = 40
CAPS = ("A", "B", "C")
CONTEXTS = {
    "A": ((-0.48, 0.00), 0.20),
    "B": ((+0.34, +0.34), 0.20),
    "C": ((+0.34, -0.34), 0.20),
}


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


def context_ok(cap, p):
    x = p[:, 0]
    y = p[:, 1]
    disk = x * x + y * y <= 1.0
    if cap == "A":
        return disk & (x <= -0.05)
    if cap == "B":
        return disk & (x >= 0.05) & (y >= 0.05)
    if cap == "C":
        return disk & (x >= 0.05) & (y <= -0.05)
    raise ValueError(cap)


def sample_context(rng, cap, n):
    center, sd = CONTEXTS[cap]
    chunks = []
    have = 0
    while have < n:
        draw_n = max(64, (n - have) * 3)
        p = rng.normal(loc=np.asarray(center), scale=sd, size=(draw_n, 2))
        p = p[context_ok(cap, p)]
        if len(p):
            take = min(n - have, len(p))
            chunks.append(p[:take])
            have += take
    return np.concatenate(chunks, axis=0)


def uniform_disk(rng, n):
    u = rng.random(n)
    th = rng.uniform(0.0, 2.0 * math.pi, size=n)
    r = np.sqrt(u)
    return np.column_stack((r * np.cos(th), r * np.sin(th)))


def gaussian_features(x, centers, sigmas):
    d2 = ((x[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
    return np.exp(-d2 / (2.0 * (sigmas[None, :] ** 2)))


def rbf_features(x, centers, sigma):
    d2 = ((x[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
    return np.exp(-d2 / (2.0 * sigma * sigma))


def ridge_fit(x, y, alpha=ALPHA):
    k = x.shape[1]
    if k == 0:
        return np.empty(0, dtype=np.float64)
    a = x.T @ x + alpha * np.eye(k)
    return np.linalg.solve(a, x.T @ y)


def nmse(yhat, y):
    v = float(np.var(y))
    return float(np.mean((yhat - y) ** 2) / (v + 1e-12))


def source_params(rng):
    centers = uniform_disk(rng, 6)
    sigmas = rng.uniform(0.12, 0.42, size=6)
    dec = rng.normal(0.0, 1.0, size=(6, 3))
    sins = []
    for _ in CAPS:
        a = rng.uniform(0.5, 1.5)
        wx = rng.uniform(1.0, 4.0)
        wy = rng.uniform(1.0, 4.0)
        phase = rng.uniform(0.0, 2.0 * math.pi)
        sins.append((a, wx, wy, phase))
    return centers, sigmas, dec, sins


def raw_residual(x, cap_i, params):
    centers, sigmas, dec, sins = params
    z = gaussian_features(x, centers, sigmas)
    base = z @ dec[:, cap_i]
    a, wx, wy, phase = sins[cap_i]
    extra = 0.10 * a * np.sin(wx * x[:, 0] + wy * x[:, 1] + phase)
    return base + extra


def proxy8_fit(xd, yd, xh, yh):
    phi_d = rbf_features(xd, PARENT, PARENT_SIGMA)
    phi_h = rbf_features(xh, PARENT, PARENT_SIGMA)
    energy = np.sum(phi_d * phi_d, axis=0) + ALPHA
    chosen = []
    pred = np.zeros_like(yd)
    beta = np.empty(0, dtype=np.float64)
    available = np.ones(PARENT.shape[0], dtype=bool)
    for _ in range(8):
        residual = yd - pred
        corr = phi_d.T @ residual
        score = (corr * corr) / energy
        score[~available] = -np.inf
        idx = int(np.argmax(score))
        chosen.append(idx)
        available[idx] = False
        xs = phi_d[:, chosen]
        beta = ridge_fit(xs, yd)
        pred = xs @ beta
    held = phi_h[:, chosen] @ beta
    return {
        "dist_nmse": nmse(pred, yd),
        "held_nmse": nmse(held, yh),
        "sites": chosen,
        "coef_rms": float(np.sqrt(np.mean(beta * beta))),
    }


def pooled_widths(pooled):
    d2 = ((pooled[:, None, :] - pooled[None, :, :]) ** 2).sum(axis=2)
    np.fill_diagonal(d2, np.inf)
    nn = np.sqrt(np.min(d2, axis=1))
    q = np.quantile(nn, [0.25, 0.50, 0.75])
    return np.maximum(q.astype(np.float64), 1e-6)


def latent_recruit(dist_x, dist_y, held_x, held_y):
    pooled = np.concatenate([dist_x[c] for c in CAPS], axis=0)
    widths = pooled_widths(pooled)

    cand_centers = np.repeat(pooled, 3, axis=0)
    cand_widths = np.tile(widths, pooled.shape[0])
    m = len(cand_widths)

    zd = {c: gaussian_features(dist_x[c], cand_centers, cand_widths) for c in CAPS}
    zh = {c: gaussian_features(held_x[c], cand_centers, cand_widths) for c in CAPS}

    selected = []
    available = np.ones(m, dtype=bool)
    snapshots = {}

    for step in range(1, 9):
        total_score = np.zeros(m, dtype=np.float64)

        for c in CAPS:
            y = dist_y[c]
            zall = zd[c]
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

        total_score /= 3.0
        total_score[~available] = np.inf
        idx = int(np.argmin(total_score))
        selected.append(idx)
        available[idx] = False

        if step in (2, 4, 8):
            per_cap = {}
            decoders = []
            for c in CAPS:
                xs = zd[c][:, selected]
                b = ridge_fit(xs, dist_y[c])
                decoders.append(b)
                pd = xs @ b
                ph = zh[c][:, selected] @ b
                per_cap[c] = {
                    "dist_nmse": nmse(pd, dist_y[c]),
                    "held_nmse": nmse(ph, held_y[c]),
                    "decoder": [float(v) for v in b],
                }

            sc = cand_centers[selected]
            if len(sc) > 1:
                dd = np.sqrt(((sc[:, None, :] - sc[None, :, :]) ** 2).sum(axis=2))
                tri = dd[np.triu_indices(len(sc), 1)]
                center_spread = float(np.mean(tri))
            else:
                center_spread = 0.0

            dmat = np.stack(decoders, axis=1)
            absd = np.abs(dmat)
            concentration = np.max(absd, axis=1) / (np.sum(absd, axis=1) + 1e-12)

            per_cap["_meta"] = {
                "selected_candidates": [int(v) for v in selected],
                "selected_center_indices": [int(v // 3) for v in selected],
                "selected_width_slots": [int(v % 3) for v in selected],
                "selected_widths": [float(cand_widths[v]) for v in selected],
                "widths": [float(v) for v in widths],
                "center_spread": center_spread,
                "decoder_concentration_mean": float(np.mean(concentration)),
            }
            snapshots[step] = per_cap
    return snapshots


def one_world(seed):
    rng = np.random.default_rng(np.random.PCG64(seed))
    params = source_params(rng)

    dist_x, held_x, dist_y, held_y = {}, {}, {}, {}
    for cap_i, cap in enumerate(CAPS):
        pts = sample_context(rng, cap, 128 + 512)
        xd, xh = pts[:128], pts[128:]
        yd = raw_residual(xd, cap_i, params)
        yh = raw_residual(xh, cap_i, params)
        scale = float(np.sqrt(np.mean(yd * yd)))
        if scale < 1e-12:
            scale = 1.0
        dist_x[cap] = xd
        held_x[cap] = xh
        dist_y[cap] = yd / scale
        held_y[cap] = yh / scale

    proxies = {
        c: proxy8_fit(dist_x[c], dist_y[c], held_x[c], held_y[c])
        for c in CAPS
    }
    latent = latent_recruit(dist_x, dist_y, held_x, held_y)

    methods = {
        "PROXY8": {c: proxies[c]["held_nmse"] for c in CAPS},
        "LATENT2": {c: latent[2][c]["held_nmse"] for c in CAPS},
        "LATENT4": {c: latent[4][c]["held_nmse"] for c in CAPS},
        "LATENT8": {c: latent[8][c]["held_nmse"] for c in CAPS},
    }
    dist_methods = {
        "PROXY8": {c: proxies[c]["dist_nmse"] for c in CAPS},
        "LATENT2": {c: latent[2][c]["dist_nmse"] for c in CAPS},
        "LATENT4": {c: latent[4][c]["dist_nmse"] for c in CAPS},
        "LATENT8": {c: latent[8][c]["dist_nmse"] for c in CAPS},
    }

    return {
        "seed": int(seed),
        "held_nmse": methods,
        "dist_nmse": dist_methods,
        "latent4_meta": latent[4]["_meta"],
        "latent8_meta": latent[8]["_meta"],
        "proxy_sites": {c: proxies[c]["sites"] for c in CAPS},
    }


def quantile(values, q):
    return float(np.quantile(np.asarray(values, dtype=np.float64), q))


def summarize(rows):
    methods = ("PROXY8", "LATENT2", "LATENT4", "LATENT8")
    out = {"worlds": len(rows), "methods": {}}
    for m in methods:
        cap_medians = {}
        for c in CAPS:
            cap_medians[c] = quantile([r["held_nmse"][m][c] for r in rows], 0.5)
        means = [float(np.mean([r["held_nmse"][m][c] for c in CAPS])) for r in rows]
        all01 = sum(all(r["held_nmse"][m][c] <= 0.01 for c in CAPS) for r in rows) / len(rows)
        all02 = sum(all(r["held_nmse"][m][c] <= 0.02 for c in CAPS) for r in rows) / len(rows)
        gaps = [
            float(np.mean([r["held_nmse"][m][c] - r["dist_nmse"][m][c] for c in CAPS]))
            for r in rows
        ]
        out["methods"][m] = {
            "held_cap_median": cap_medians,
            "held_mean_median": quantile(means, 0.5),
            "held_mean_p90": quantile(means, 0.90),
            "all_caps_le_0p01_rate": float(all01),
            "all_caps_le_0p02_rate": float(all02),
            "mean_dist_to_held_gap_median": quantile(gaps, 0.5),
        }

    for lm in ("LATENT4", "LATENT8"):
        deltas = []
        for r in rows:
            l = np.mean([r["held_nmse"][lm][c] for c in CAPS])
            p = np.mean([r["held_nmse"]["PROXY8"][c] for c in CAPS])
            deltas.append(float(l - p))
        out[f"{lm.lower()}_minus_proxy8"] = {
            "median": quantile(deltas, 0.5),
            "p90": quantile(deltas, 0.90),
            "win_rate": float(np.mean(np.asarray(deltas) < 0.0)),
        }

    out["latent4_decoder_concentration_median"] = quantile(
        [r["latent4_meta"]["decoder_concentration_mean"] for r in rows], 0.5
    )
    out["latent4_center_spread_median"] = quantile(
        [r["latent4_meta"]["center_spread"] for r in rows], 0.5
    )
    return out


def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def run():
    rows = [one_world(WORLD_START + i) for i in range(WORLD_COUNT)]
    summary = summarize(rows)
    return {"schema": "yggdrasil.h191-p0-surrogate.v1", "rows": rows, "summary": summary}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    obj = run()
    raw = (encode(obj) + "\n").encode("utf-8")
    Path(args.out).write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    print(encode({"output": args.out, "sha256": digest, "summary": obj["summary"]}))


if __name__ == "__main__":
    main()
