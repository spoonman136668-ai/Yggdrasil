"""WSP-213 numerical parity and scientific classification verification.

Read-only audit of two platform receipts; no model training or source labels.
"""
import json
import math
from pathlib import Path
import sys

SCHEMA = "wsp213.matched-direct-weight.source-free.v1"
PREREG = "8b8f8deaf14ea256a311690e4ca59d4cc4110caa"
WORLDS = ((21301, "hub", 24), (21302, "complete", 12),
          (21303, "hub", 24), (21304, "complete", 12))
MODES = ("contradiction", "surprise", "random", "always", "no_update",
         "full_refit")
NUMERIC = ("objective", "b0_mse")
ARM_METRICS = ("held_rmse", "b3_b0_mse")
ABS_TOL = 1e-8
REL_TOL = 1e-8


def compare_metric(label, a, b):
    if type(a) not in (float, int) or type(b) not in (float, int):
        raise ValueError(label + ": nonnumeric")
    if not math.isfinite(a) or not math.isfinite(b):
        raise ValueError(label + ": nonfinite")
    if not math.isclose(a, b, abs_tol=ABS_TOL, rel_tol=REL_TOL):
        raise ValueError(f"{label}: cross-OS numerical drift {a!r} vs {b!r}")


def _identity(name, a, b):
    if a != b:
        raise ValueError(name + ": cross-OS identity divergence")


def _hash(s, label):
    if not isinstance(s, str) or len(s) != 64 or any(
            x not in "0123456789abcdef" for x in s):
        raise ValueError(label + ": invalid sha256 receipt")


def _one_world(w, idx):
    if tuple(w["world"]) != WORLDS[idx] or w["status"] != "VALID":
        raise ValueError("invalid world identity or incomplete learning")
    if w["stages_completed"] != 4:
        raise ValueError("missing stage")
    if w["original_gfp_accessed"] or w["reserved_labels_generated"]:
        raise ValueError("forbidden source access")
    if w["fit_groups"] <= 0 or w["held_groups"] <= 0:
        raise ValueError("empty distinct pair groups")
    _hash(w["fit_source_sha256"], "fit")
    _hash(w["held_source_sha256"], "held")
    compare_metric("zero held", w["zero_held_rmse"], w["zero_held_rmse"])
    if set(w["trace"]) != set(MODES) or set(w["arms"]) != set(MODES):
        raise ValueError("missing comparison arm")
    for m in MODES:
        if len(w["trace"][m]) != 4:
            raise ValueError("incomplete arm trajectory")
        if set(w["arms"][m]) != {
                "held_rmse", "b3_b0_mse", "total_coordinate_solves",
                "total_address_writes", "total_wall_ns"}:
            raise ValueError("incomplete arm metrics")
        for s, row in enumerate(w["trace"][m]):
            if row["stage"] != s or row["new_rows"] < 1:
                raise ValueError("stage or row mismatch")
            _hash(row["fit_sha256"], "fit stage")
            _hash(row["checkpoint_sha256"], "cold checkpoint")
            for x in NUMERIC:
                compare_metric(m+"."+x, row[x], row[x])
        a = w["arms"][m]
        if (sum(x["coordinate_solves"] for x in w["trace"][m])
                != a["total_coordinate_solves"]):
            raise ValueError("solve-cost accounting mismatch")
        if (sum(x["address_writes"] for x in w["trace"][m])
                != a["total_address_writes"]):
            raise ValueError("address-count accounting mismatch")
        compare_metric(m+".held", a["held_rmse"], a["held_rmse"])
        compare_metric(m+".retention", a["b3_b0_mse"], w["trace"][m][-1]["b0_mse"])
    for s in range(1, 4):
        matched = w["trace"]["contradiction"][s]["address_writes"]
        for control in ("surprise", "random"):
            if w["trace"][control][s]["address_writes"] != matched:
                raise ValueError("unmatched stage writing budget")
    c = w["arms"]["contradiction"]
    r = w["arms"]["full_refit"]
    best = min(w["arms"][x]["held_rmse"] for x in ("surprise", "random"))
    success = (c["b3_b0_mse"] <= 1.05*r["b3_b0_mse"] and
               c["held_rmse"] <= .95*r["held_rmse"] and
               c["held_rmse"] <= .95*best and
               c["total_coordinate_solves"] < r["total_coordinate_solves"])
    if type(w["world_direct_gain"]) is not bool or w["world_direct_gain"] != success:
        raise ValueError("incorrect prespecified world classification")


def compare_receipts(linux, windows):
    for name in ("schema", "prereg_commit", "classification",
                 "wsp210_211_212_cohorts_reused",
                 "original_gfp_labels_accessed",
                 "reserved_labels_accessed",
                 "native_amalgam_accessed", "research_only"):
        _identity(name, linux.get(name), windows.get(name))
    if linux.get("schema") != SCHEMA or linux.get("prereg_commit") != PREREG:
        raise ValueError("source/prereg is not frozen")
    if linux.get("classification") not in ("DIRECT_GAIN", "NO_GAIN"):
        raise ValueError("INVALID or incomplete primary")
    if (linux.get("wsp210_211_212_cohorts_reused") or
            linux.get("original_gfp_labels_accessed") or
            linux.get("reserved_labels_accessed") or
            linux.get("native_amalgam_accessed") or
            not linux.get("research_only")):
        raise ValueError("source/owner fence violation")
    if len(linux.get("worlds", [])) != 4 or len(windows.get("worlds", [])) != 4:
        raise ValueError("missing preregistered world")
    for idx, (a, b) in enumerate(zip(linux["worlds"], windows["worlds"])):
        _one_world(a, idx)
        _one_world(b, idx)
        for key in ("world", "status", "stages_completed", "fit_groups",
                    "held_groups", "fit_source_sha256", "held_source_sha256",
                    "world_direct_gain", "original_gfp_accessed",
                    "reserved_labels_generated"):
            _identity(f"world{idx}.{key}", a[key], b[key])
        compare_metric(f"world{idx}.zero", a["zero_held_rmse"], b["zero_held_rmse"])
        for mode in MODES:
            for metric in ARM_METRICS:
                compare_metric(f"world{idx}.{mode}.{metric}",
                               a["arms"][mode][metric], b["arms"][mode][metric])
            for counter in ("total_coordinate_solves", "total_address_writes"):
                _identity(f"world{idx}.{mode}.{counter}",
                          a["arms"][mode][counter], b["arms"][mode][counter])
            for s, (x, y) in enumerate(zip(a["trace"][mode], b["trace"][mode])):
                for key in ("stage", "new_rows", "cumulative_rows", "address_writes",
                            "coordinate_solves", "fit_sha256"):
                    _identity(f"world{idx}.{mode}.stage{s}.{key}", x[key], y[key])
                for num in NUMERIC:
                    compare_metric(f"world{idx}.{mode}.stage{s}.{num}",
                                   x[num], y[num])
    expected = ("DIRECT_GAIN" if sum(w["world_direct_gain"]
                for w in linux["worlds"]) >= 3 else "NO_GAIN")
    if linux["classification"] != expected:
        raise ValueError("post-hoc classification drift")
    return expected


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: verify_parity.py linux.json windows.json")
    linux = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    windows = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    result = compare_receipts(linux, windows)
    print("WSP213_CROSS_OS_PARITY=PASS CLASSIFICATION="+result)
