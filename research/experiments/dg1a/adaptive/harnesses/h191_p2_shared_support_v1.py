#!/usr/bin/env python3
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np

BASE_NAME = "h191_p0_surrogate_mechanical_v1.py"
WORLD_START = 20260924390000
WORLD_COUNT = 40


def load_base():
    path = Path(__file__).resolve().parent / BASE_NAME
    spec = importlib.util.spec_from_file_location("h191_p0_base", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def shared_support_recruit(base, dist_x, dist_y, held_x, held_y):
    zd = {c: base.rbf_features(dist_x[c], base.PARENT, base.PARENT_SIGMA) for c in base.CAPS}
    zh = {c: base.rbf_features(held_x[c], base.PARENT, base.PARENT_SIGMA) for c in base.CAPS}
    m = base.PARENT.shape[0]

    selected = []
    available = np.ones(m, dtype=bool)
    snapshots = {}

    for step in range(1, 9):
        total_score = np.zeros(m, dtype=np.float64)

        for c in base.CAPS:
            y = dist_y[c]
            zall = zd[c]
            if not selected:
                denom = np.sum(zall * zall, axis=0) + base.ALPHA
                gamma = (zall.T @ y) / denom
                pred_new = zall * gamma[None, :]
            else:
                xsel = zall[:, selected]
                ata = xsel.T @ xsel + base.ALPHA * np.eye(len(selected))
                ainv = np.linalg.inv(ata)
                xty = xsel.T @ y
                beta = ainv @ xty
                pred = xsel @ beta

                q = xsel.T @ zall
                v = ainv @ q
                u = zall - xsel @ v
                h = np.sum(zall * zall, axis=0) + base.ALPHA - np.sum(q * v, axis=0)
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
            for c in base.CAPS:
                xs = zd[c][:, selected]
                b = base.ridge_fit(xs, dist_y[c])
                decoders.append(b)
                pd = xs @ b
                ph = zh[c][:, selected] @ b
                per_cap[c] = {
                    "dist_nmse": base.nmse(pd, dist_y[c]),
                    "held_nmse": base.nmse(ph, held_y[c]),
                    "decoder": [float(v) for v in b],
                }

            sc = base.PARENT[selected]
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
                "selected_center_indices": [int(v) for v in selected],
                "selected_width_slots": [0 for _ in selected],
                "selected_widths": [float(base.PARENT_SIGMA) for _ in selected],
                "widths": [float(base.PARENT_SIGMA)],
                "center_spread": center_spread,
                "decoder_concentration_mean": float(np.mean(concentration)),
            }
            snapshots[step] = per_cap
    return snapshots


def transform_rows(rows):
    for row in rows:
        for field in ("held_nmse", "dist_nmse"):
            d = row[field]
            d["SUPPORT2"] = d.pop("LATENT2")
            d["SUPPORT4"] = d.pop("LATENT4")
            d["SUPPORT8"] = d.pop("LATENT8")
        row["support4_meta"] = row.pop("latent4_meta")
        row["support8_meta"] = row.pop("latent8_meta")
    return rows


def q(values, p):
    return float(np.quantile(np.asarray(values, dtype=np.float64), p))


def summarize(rows):
    methods = ("PROXY8", "SUPPORT2", "SUPPORT4", "SUPPORT8")
    out = {"worlds": len(rows), "methods": {}}
    for m in methods:
        cap_medians = {
            c: q([r["held_nmse"][m][c] for r in rows], 0.5)
            for c in ("A", "B", "C")
        }
        means = [
            float(np.mean([r["held_nmse"][m][c] for c in ("A", "B", "C")]))
            for r in rows
        ]
        all01 = sum(
            all(r["held_nmse"][m][c] <= 0.01 for c in ("A", "B", "C"))
            for r in rows
        ) / len(rows)
        all02 = sum(
            all(r["held_nmse"][m][c] <= 0.02 for c in ("A", "B", "C"))
            for r in rows
        ) / len(rows)
        gaps = [
            float(np.mean([
                r["held_nmse"][m][c] - r["dist_nmse"][m][c]
                for c in ("A", "B", "C")
            ]))
            for r in rows
        ]
        out["methods"][m] = {
            "held_cap_median": cap_medians,
            "held_mean_median": q(means, 0.5),
            "held_mean_p90": q(means, 0.90),
            "all_caps_le_0p01_rate": float(all01),
            "all_caps_le_0p02_rate": float(all02),
            "mean_dist_to_held_gap_median": q(gaps, 0.5),
        }

    deltas = []
    for r in rows:
        s = np.mean([r["held_nmse"]["SUPPORT8"][c] for c in ("A", "B", "C")])
        p = np.mean([r["held_nmse"]["PROXY8"][c] for c in ("A", "B", "C")])
        deltas.append(float(s - p))
    out["support8_minus_proxy8"] = {
        "median": q(deltas, 0.5),
        "p90": q(deltas, 0.90),
        "win_rate": float(np.mean(np.asarray(deltas) < 0.0)),
    }
    out["support8_decoder_concentration_median"] = q(
        [r["support8_meta"]["decoder_concentration_mean"] for r in rows], 0.5
    )
    out["support8_center_spread_median"] = q(
        [r["support8_meta"]["center_spread"] for r in rows], 0.5
    )
    return out


def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    base = load_base()
    base.WORLD_START = WORLD_START
    base.WORLD_COUNT = WORLD_COUNT
    base.latent_recruit = lambda dx, dy, hx, hy: shared_support_recruit(base, dx, dy, hx, hy)

    obj = base.run()
    obj["rows"] = transform_rows(obj["rows"])
    obj["summary"] = summarize(obj["rows"])
    obj["schema"] = "yggdrasil.h191-p2-shared-support.v1"

    raw = (encode(obj) + "\n").encode("utf-8")
    Path(args.out).write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    print(encode({"output": args.out, "sha256": digest, "summary": obj["summary"]}))


if __name__ == "__main__":
    main()
