#!/usr/bin/env python3
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path

import numpy as np

P3_NAME = "h191_p3_multiscale_dictionary_v1.py"
WORLD_COUNT = 10
CONDITIONS = (
    ("SRC4", 4, 20260924500000),
    ("SRC6", 6, 20260924510000),
    ("SRC8", 8, 20260924520000),
    ("SRC12", 12, 20260924530000),
)


def load_p3():
    path = Path(__file__).resolve().parent / P3_NAME
    spec = importlib.util.spec_from_file_location("h191_p3_base", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def source_params_k(base, rng, k):
    centers = base.uniform_disk(rng, k)
    sigmas = rng.uniform(0.12, 0.42, size=k)
    dec = rng.normal(0.0, 1.0, size=(k, 3))
    sins = []
    for _ in base.CAPS:
        a = rng.uniform(0.5, 1.5)
        wx = rng.uniform(1.0, 4.0)
        wy = rng.uniform(1.0, 4.0)
        phase = rng.uniform(0.0, 2.0 * math.pi)
        sins.append((a, wx, wy, phase))
    return centers, sigmas, dec, sins


def rename_rows_to_dict(rows):
    for row in rows:
        for field in ("held_nmse", "dist_nmse"):
            d = row[field]
            d["DICT2"] = d.pop("SUPPORT2")
            d["DICT4"] = d.pop("SUPPORT4")
            d["DICT8"] = d.pop("SUPPORT8")
        row["dict4_meta"] = row.pop("support4_meta")
        row["dict8_meta"] = row.pop("support8_meta")
    return rows


def summarize_dict(p2, rows):
    work = json.loads(json.dumps(rows))
    for row in work:
        for field in ("held_nmse", "dist_nmse"):
            d = row[field]
            d["SUPPORT2"] = d.pop("DICT2")
            d["SUPPORT4"] = d.pop("DICT4")
            d["SUPPORT8"] = d.pop("DICT8")
        row["support4_meta"] = row.pop("dict4_meta")
        row["support8_meta"] = row.pop("dict8_meta")

    s = p2.summarize(work)
    s["methods"]["DICT2"] = s["methods"].pop("SUPPORT2")
    s["methods"]["DICT4"] = s["methods"].pop("SUPPORT4")
    s["methods"]["DICT8"] = s["methods"].pop("SUPPORT8")
    s["dict8_minus_proxy8"] = s.pop("support8_minus_proxy8")
    s["dict8_decoder_concentration_median"] = s.pop(
        "support8_decoder_concentration_median"
    )
    s["dict8_center_spread_median"] = s.pop("support8_center_spread_median")

    slot_counts = [0, 0, 0]
    for row in rows:
        for slot in row["dict8_meta"]["selected_width_slots"]:
            slot_counts[slot] += 1
    s["dict8_scale_slot_counts"] = {
        "S0_0p22": int(slot_counts[0]),
        "S1_0p44": int(slot_counts[1]),
        "S2_0p88": int(slot_counts[2]),
    }

    delta = s["dict8_minus_proxy8"]["median"]
    win = s["dict8_minus_proxy8"]["win_rate"]
    if delta <= 0.0 and win >= 0.50:
        regime = "ROBUST"
    elif delta > 0.02 and win < 0.25:
        regime = "OVER_CAPACITY"
    elif (0.0 < delta <= 0.02) or (0.25 <= win < 0.50):
        regime = "TRANSITION"
    else:
        regime = "MIXED_UNCLASSIFIED"
    s["mechanical_regime"] = regime
    return s


def run_condition(p3, label, k, start):
    p2 = p3.load_p2()
    base = p2.load_base()
    base.WORLD_START = start
    base.WORLD_COUNT = WORLD_COUNT
    base.source_params = lambda rng: source_params_k(base, rng, k)
    base.latent_recruit = lambda dx, dy, hx, hy: p3.multiscale_dictionary_recruit(
        base, dx, dy, hx, hy
    )

    obj = base.run()
    rows = p2.transform_rows(obj["rows"])
    rows = rename_rows_to_dict(rows)
    for row in rows:
        row["condition"] = label
        row["source_shared_factors"] = int(k)

    summary = summarize_dict(p2, rows)
    summary["source_shared_factors"] = int(k)
    summary["seed_start"] = int(start)
    summary["seed_end"] = int(start + WORLD_COUNT - 1)
    return rows, summary


def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def run():
    p3 = load_p3()
    rows = []
    conditions = {}
    for label, k, start in CONDITIONS:
        cr, cs = run_condition(p3, label, k, start)
        rows.extend(cr)
        conditions[label] = cs

    return {
        "schema": "yggdrasil.h191-p4-dict8-capacity-stress.v1",
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
