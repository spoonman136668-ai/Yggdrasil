"""WSP-212 frozen cross-OS numeric parity audit of ONE calibration per OS.

This never trains or generates labels; it compares two sealed source-free
receipts. Wall-clock measurements and checkpoint byte hashes are recorded but
not incorrectly treated as cross-platform invariant.
"""
from __future__ import annotations
import json
import math
from pathlib import Path
import sys

SCHEMA = "wsp212.full-refit-parity.source-free.v1"
ABS_TOL = 1e-8
REL_TOL = 1e-8
METRICS = ("objective", "b0_retention_mse", "b0_zero_mse")
WORLD_METRICS = ("zero_held_rmse", "refit_held_rmse")
STEP_KEYS = ("stage", "new_fit_rows", "cumulative_fit_rows",
             "cumulative_fit_groups", "actual_sweeps", "fit_source_sha256")
WORLD_KEYS = ("world", "status", "stages_completed", "fit_groups",
              "held_groups", "held_source_sha256",
              "original_source_accessed", "reserved_labels_generated")
ROOT_KEYS = ("schema", "classification", "original_gfp_labels_accessed",
             "reserved_labels_accessed", "wsp210_wsp211_cohorts_reused",
             "research_only")


def compare_metric(name, a, b):
    if type(a) not in (float, int) or type(b) not in (float, int):
        raise ValueError(f"{name}: nonnumeric metric")
    if not math.isfinite(a) or not math.isfinite(b):
        raise ValueError(f"{name}: nonfinite metric")
    if not math.isclose(a, b, rel_tol=REL_TOL, abs_tol=ABS_TOL):
        raise ValueError(f"{name}: cross-platform numerical drift {a!r} vs {b!r}")


def compare_receipts(linux, windows):
    for key in ROOT_KEYS:
        if linux.get(key) != windows.get(key):
            raise ValueError(f"root field disagreement: {key}")
    if linux.get("schema") != SCHEMA:
        raise ValueError("wrong source-free schema")
    if linux.get("classification") != "CONTROL_QUALIFIED":
        raise ValueError("CONTROL_UNQUALIFIED: comparator has not converged")
    if (linux.get("original_gfp_labels_accessed") or
        linux.get("reserved_labels_accessed") or
        linux.get("wsp210_wsp211_cohorts_reused") or
        not linux.get("research_only")):
        raise ValueError("source or owner boundary violation")
    if len(linux.get("worlds", [])) != 4 or len(windows.get("worlds", [])) != 4:
        raise ValueError("missing disjoint worlds")
    for i, (a, b) in enumerate(zip(linux["worlds"], windows["worlds"])):
        for key in WORLD_KEYS:
            if a.get(key) != b.get(key):
                raise ValueError(f"world {i} differs: {key}")
        if a["status"] != "CONTROL_QUALIFIED" or a["stages_completed"] != 4:
            raise ValueError(f"world {i}: incomplete comparator")
        if a["original_source_accessed"] or a["reserved_labels_generated"]:
            raise ValueError("original source or reserved labels accessed")
        if len(a.get("trace", [])) != 4 or len(b.get("trace", [])) != 4:
            raise ValueError(f"world {i}: incomplete stage trace")
        for key in WORLD_METRICS:
            compare_metric(f"world{i}.{key}", a.get(key), b.get(key))
        for s, (x, y) in enumerate(zip(a["trace"], b["trace"])):
            for key in STEP_KEYS:
                if x.get(key) != y.get(key):
                    raise ValueError(f"world{i}.stage{s}: {key} disagree")
            if x["stage"] != s or x["actual_sweeps"] > 800:
                raise ValueError("unqualified convergence accounting")
            if (len(x.get("checkpoint_sha256", "")) != 64 or
                len(y.get("checkpoint_sha256", "")) != 64):
                raise ValueError("missing local cold checkpoint hash")
            for key in METRICS:
                compare_metric(f"world{i}.stage{s}.{key}",
                               x.get(key), y.get(key))
    return True


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: verify_parity.py linux.json windows.json")
    a = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    b = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    compare_receipts(a, b)
    print("WSP212_CROSS_OS_PARITY=PASS CONTROL_QUALIFIED")
