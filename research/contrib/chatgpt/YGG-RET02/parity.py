"""Cross-OS exact-structure and bounded-numeric retention receipt audit.

Source and labels must match identically. Computed IEEE754 floats may differ
by <=1e-12 absolute, disclosed with counts and SHA256 for both originals.
No future outcomes, threshold tuning, new training or source modifications.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

TOLERANCE = 1e-12

def parity(a, b):
    differences = []
    count = 0
    maximum = 0.0
    def check(x, y, path="$"):
        nonlocal count, maximum
        if type(x) is not type(y):
            raise ValueError("RET02_PARITY_TYPE:" + path)
        if type(x) is dict:
            if set(x) != set(y):
                raise ValueError("RET02_PARITY_KEYS:" + path)
            for key in sorted(x):
                check(x[key], y[key], path + "." + str(key))
        elif type(x) is list:
            if len(x) != len(y):
                raise ValueError("RET02_PARITY_COUNT:" + path)
            for i, (z, w) in enumerate(zip(x, y)):
                check(z, w, path + "[" + str(i) + "]")
        elif type(x) is float:
            if not math.isfinite(x) or not math.isfinite(y):
                raise ValueError("RET02_PARITY_NONFINITE:" + path)
            delta = abs(x - y)
            if delta > TOLERANCE:
                raise ValueError("RET02_PARITY_NUMERIC:" + path +
                                 " delta=" + repr(delta))
            if delta:
                count += 1
                maximum = max(maximum, delta)
                if len(differences) < 5:
                    differences.append({"field": path, "abs_delta": delta})
        elif x != y:
            raise ValueError("RET02_PARITY_EXACT:" + path)
    check(a, b)
    return {"different_float_count": count, "max_abs_delta": maximum,
            "first_five_numeric_deltas": differences}

def compare_bytes(left, right):
    a = json.loads(left)
    b = json.loads(right)
    result = parity(a, b)
    result.update({
        "schema": "yggdrasil.ret02.linux-windows-parity.v1",
        "absolute_numeric_tolerance": TOLERANCE,
        "left_sha256": hashlib.sha256(left).hexdigest(),
        "right_sha256": hashlib.sha256(right).hexdigest(),
        "exact_nonfloat_source_and_verdict": True,
        "science_pass": False,
    })
    return result

def main():
    p = argparse.ArgumentParser()
    p.add_argument("left", type=Path)
    p.add_argument("right", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = compare_bytes(args.left.read_bytes(), args.right.read_bytes())
    encoded = json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    print("RET02_CROSS_OS_NUMERIC_PARITY_PASS",
          "different_floats", result["different_float_count"],
          "max_abs_delta", result["max_abs_delta"],
          "source_labels_verdict_exact", True)

if __name__ == "__main__":
    main()
