#!/usr/bin/env python3
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np

P2_NAME = "h191_p2_shared_support_v1.py"
WORLD_START = 20260924490000
WORLD_COUNT = 40
SCALES = np.asarray([0.22, 0.44, 0.88], dtype=np.float64)


def load_p2():
    path = Path(__file__).resolve().parent / P2_NAME
    spec = importlib.util.spec_from_file_location("h191_p2_base", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def multiscale_dictionary_recruit(base, dist_x, dist_y, held_x, held_y):
    cand_centers = np.repeat(base.PARENT, 3, axis=0)
    cand_widths = np.tile(SCALES, base.PARENT.shape[0])
    m = len(cand_widths)

    zd = {
        c: base.gaussian_features(dist_x[c], cand_centers, cand_widths)
        for c in base.CAPS
    }

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
            sel_centers = cand_centers[selected]
            sel_widths = cand_widths[selected]
            for c in base.CAPS:
                xs = zd[c][:, selected]
                b = base.ridge_fit(xs, dist_y[c])
                decoders.append(b)
                pd = xs @ b
                zh = base.gaussian_features(held_x[c], sel_centers, sel_widths)
                ph = zh @ b
                per_cap[c] = {
                    "dist_nmse": base.nmse(pd, dist_y[c]),
                    "held_nmse": base.nmse(ph, held_y[c]),
                    "decoder": [float(v) for v in b],
                }

            sc = sel_centers
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
                "widths": [float(v) for v in SCALES],
                "center_spread": center_spread,
                "decoder_concentration_mean": float(np.mean(concentration)),
            }
            snapshots[step] = per_cap

    return snapshots


def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    p2 = load_p2()
    base = p2.load_base()
    base.WORLD_START = WORLD_START
    base.WORLD_COUNT = WORLD_COUNT
    base.latent_recruit = lambda dx, dy, hx, hy: multiscale_dictionary_recruit(
        base, dx, dy, hx, hy
    )

    obj = base.run()
    obj["rows"] = p2.transform_rows(obj["rows"])
    for row in obj["rows"]:
        for field in ("held_nmse", "dist_nmse"):
            d = row[field]
            d["DICT2"] = d.pop("SUPPORT2")
            d["DICT4"] = d.pop("SUPPORT4")
            d["DICT8"] = d.pop("SUPPORT8")
        row["dict4_meta"] = row.pop("support4_meta")
        row["dict8_meta"] = row.pop("support8_meta")

    summary_rows = json.loads(json.dumps(obj["rows"]))
    for row in summary_rows:
        for field in ("held_nmse", "dist_nmse"):
            d = row[field]
            d["SUPPORT2"] = d.pop("DICT2")
            d["SUPPORT4"] = d.pop("DICT4")
            d["SUPPORT8"] = d.pop("DICT8")
        row["support4_meta"] = row.pop("dict4_meta")
        row["support8_meta"] = row.pop("dict8_meta")
    s = p2.summarize(summary_rows)
    s["methods"]["DICT2"] = s["methods"].pop("SUPPORT2")
    s["methods"]["DICT4"] = s["methods"].pop("SUPPORT4")
    s["methods"]["DICT8"] = s["methods"].pop("SUPPORT8")
    s["dict8_minus_proxy8"] = s.pop("support8_minus_proxy8")
    s["dict8_decoder_concentration_median"] = s.pop("support8_decoder_concentration_median")
    s["dict8_center_spread_median"] = s.pop("support8_center_spread_median")

    slot_counts = [0, 0, 0]
    for row in obj["rows"]:
        for slot in row["dict8_meta"]["selected_width_slots"]:
            slot_counts[slot] += 1
    s["dict8_scale_slot_counts"] = {
        "S0_0p22": int(slot_counts[0]),
        "S1_0p44": int(slot_counts[1]),
        "S2_0p88": int(slot_counts[2]),
    }

    obj["summary"] = s
    obj["schema"] = "yggdrasil.h191-p3-fixed-multiscale-dictionary.v1"

    raw = (encode(obj) + "\n").encode("utf-8")
    Path(args.out).write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    print(encode({"output": args.out, "sha256": digest, "summary": obj["summary"]}))


if __name__ == "__main__":
    main()
