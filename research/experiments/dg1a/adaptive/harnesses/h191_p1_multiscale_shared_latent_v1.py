#!/usr/bin/env python3
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np

BASE_NAME = "h191_p0_surrogate_mechanical_v1.py"
WORLD_START = 20260924290000
WORLD_COUNT = 40


def load_base():
    path = Path(__file__).resolve().parent / BASE_NAME
    spec = importlib.util.spec_from_file_location("h191_p0_base", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def multiscale_widths(pooled):
    d = np.sqrt(((pooled[:, None, :] - pooled[None, :, :]) ** 2).sum(axis=2))
    off = d[np.triu_indices(len(pooled), 1)]
    return np.asarray([
        0.22,
        float(np.quantile(off, 0.25)),
        float(np.quantile(off, 0.50)),
    ], dtype=np.float64)


def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    base = load_base()
    base.WORLD_START = WORLD_START
    base.WORLD_COUNT = WORLD_COUNT
    base.pooled_widths = multiscale_widths

    obj = base.run()
    obj["schema"] = "yggdrasil.h191-p1-surrogate.v1"
    raw = (encode(obj) + "\n").encode("utf-8")
    Path(args.out).write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    print(encode({"output": args.out, "sha256": digest, "summary": obj["summary"]}))


if __name__ == "__main__":
    main()
