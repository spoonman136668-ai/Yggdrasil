"""WSP-213 — frozen direct-weight vs conventional comparison (synthetic only).

No original GFP data, Yggdrasil runtime, real model, or prior WSP cohort is read.
Preregistration commit: 8b8f8deaf14ea256a311690e4ca59d4cc4110caa.
The primary evaluator is ONLY called after source-only CI preflight.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
sys.path.insert(0, str(BASE / "WSP-200"))
sys.path.insert(0, str(BASE / "WSP-210"))
sys.path.insert(0, str(BASE / "WSP-211"))

from learner import Learner, Sample, pair_group, group_bucket, fit_stage
from source_free_partition import SYNTHETIC_DIGEST
from source_free_targets import group_weighted_rmse
# WSP-210 and WSP-213 both have a file named study.py. Import the exact
# inherited WSP-210 source under a private name, then bind its names only for
# WSP-211's unchanged qualified comparator import. Restore the original
# "study" module immediately; do not shadow this WSP-213 evaluator globally.
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "wsp210_study_for_wsp213", BASE / "WSP-210" / "study.py")
if _spec is None or _spec.loader is None:
    raise RuntimeError("pinned conventional source unavailable")
_parent = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_parent)
_pairs = _parent._pairs
_mse = _parent._mse
_zero_score = _parent._zero_score
ridge_scope = _parent.ridge_scope
_previous_study = sys.modules.get("study")
sys.modules["study"] = _parent
try:
    from calibration import BlockedFullRefit
finally:
    if _previous_study is None:
        del sys.modules["study"]
    else:
        sys.modules["study"] = _previous_study

SCHEMA = "wsp213.matched-direct-weight.source-free.v1"
PREREG_SHA = "8b8f8deaf14ea256a311690e4ca59d4cc4110caa"
WORLDS = ((21301, "hub", 24), (21302, "complete", 12),
          (21303, "hub", 24), (21304, "complete", 12))
FORBIDDEN = frozenset((21011, 21012, 21013, 21014,
                       21101, 21102, 21201, 21202, 21203, 21204))
MODES = ("contradiction", "surprise", "random", "always", "no_update",
         "full_refit")
RIDGE = 0.2
RANK = 4


def metadata(world):
    if world not in WORLDS or world[0] in FORBIDDEN:
        raise ValueError("world not in frozen WSP213 primary cohort")
    seed, topology, n = world
    gene = f"FABRICATED_WSP213_{seed}"
    groups = defaultdict(list)
    for i, j in _pairs(topology, n):
        group = pair_group(gene, i, j)
        bucket = group_bucket(group)
        if bucket == "FIT":
            groups[(bucket, fit_stage(group))].append((i, j, group))
        elif bucket == "PUBLIC_DEV":
            groups[(bucket, None)].append((i, j, group))
    if any(not groups[("FIT", s)] for s in range(4)):
        raise ValueError("empty frozen FIT stage")
    if not groups[("PUBLIC_DEV", None)]:
        raise ValueError("empty frozen held pair group")
    return gene, groups


def _factor(seed, allele, pos, k):
    if seed not in {w[0] for w in WORLDS} or allele not in ("C", "D") or k not in range(RANK) or pos < 1:
        raise ValueError("forbidden synthetic source")
    key = f"WSP213\0{seed}\0{allele}\0{pos}\0{k}".encode("utf-8")
    return hashlib.sha256(key).digest()[0] % 7 - 3


def _target(seed, i, j, allele):
    return sum(_factor(seed, allele, i, k) * _factor(seed, allele, j, k)
               for k in range(RANK)) / 9.0


def _samples(seed, gene, pair_rows):
    for i, j, group in pair_rows:
        for alt in ("C", "D"):
            yield Sample(f"{seed}_{i}_{j}_{alt}", group,
                         f"{gene}\0{i}\0A\0{alt}",
                         f"{gene}\0{j}\0A\0{alt}",
                         _target(seed, i, j, alt))


def _digest(rows):
    return hashlib.sha256(json.dumps(
        [(s.sample_id, s.group, s.left, s.right, s.target) for s in rows],
        sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")).hexdigest()


def _cold(model, first):
    checkpoint = model.checkpoint()
    cls = BlockedFullRefit if isinstance(model, BlockedFullRefit) else Learner
    cold = cls.restore(checkpoint, SYNTHETIC_DIGEST)
    if cold.checkpoint() != checkpoint:
        raise ValueError("cold checkpoint bytes changed")
    if any(cold.predict(s.left, s.right) != model.predict(s.left, s.right)
           for s in first):
        raise ValueError("cold historical function changed")
    return hashlib.sha256(checkpoint).hexdigest()


def run_world(world):
    gene, groups = metadata(world)
    arms = {mode: (BlockedFullRefit(SYNTHETIC_DIGEST, "full_refit", RANK)
                   if mode == "full_refit" else
                   Learner(SYNTHETIC_DIGEST, mode, RANK))
            for mode in MODES}
    first = None
    observed = set()
    fit_groups = set()
    trace = {mode: [] for mode in MODES}
    for stage in range(4):
        batch = sorted(_samples(world[0], gene, groups[("FIT", stage)]),
                       key=lambda s: s.sample_id)
        if stage == 0:
            first = tuple(batch)
        ids = {s.sample_id for s in batch}
        group_ids = {s.group for s in batch}
        if len(ids) != len(batch) or ids.intersection(observed):
            raise ValueError("duplicate or replayed FIT observations")
        if group_ids.intersection(fit_groups):
            raise ValueError("repeated FIT pair group")
        observed.update(ids)
        fit_groups.update(group_ids)
        receipts = {}
        # Run the fully qualified conventional control FIRST; on failure, no
        # candidate result is evaluated or held labels generated.
        for mode in ("full_refit", "contradiction", "surprise",
                     "random", "always", "no_update"):
            model = arms[mode]
            before = model.solves
            start = time.perf_counter_ns()
            try:
                with ridge_scope(RIDGE):
                    if mode in ("surprise", "random") and stage:
                        write_count = receipts["contradiction"]["address_writes"]
                        receipt = model.advance(stage, batch,
                                                reference_write_count=write_count)
                    else:
                        receipt = model.advance(stage, batch)
                    objective = model._objective()
                    checkpoint_sha = _cold(model, first)
            except ArithmeticError as exc:
                if mode != "full_refit":
                    raise
                return {
                    "world": world, "status": "INVALID",
                    "reason": "conventional full-refit unqualified: " + str(exc),
                    "stages_completed": stage, "trace": trace,
                    "original_gfp_accessed": False,
                    "reserved_labels_generated": False
                }
            elapsed = time.perf_counter_ns() - start
            receipts[mode] = receipt
            if mode == "full_refit":
                cv = model.convergence[-1]
                expected = 8 * cv["sweeps"]
                if not cv["converged"] or model.solves-before != expected * len(model.weights):
                    raise AssertionError("full-refit stage convergence accounting")
            if stage and mode in ("surprise", "random"):
                if receipt["address_writes"] != receipts["contradiction"]["address_writes"]:
                    raise AssertionError("matched write-budget violation")
            if not math.isfinite(objective):
                raise ArithmeticError("nonfinite staged objective")
            b0 = _mse(first, model.predict, model.mean, model.sd)
            if not math.isfinite(b0):
                raise ArithmeticError("nonfinite historical MSE")
            trace[mode].append({
                "stage": stage,
                "new_rows": len(batch),
                "cumulative_rows": len(model.samples),
                "address_writes": receipt["address_writes"],
                "coordinate_solves": model.solves - before,
                "objective": objective, "b0_mse": b0,
                "checkpoint_sha256": checkpoint_sha,
                "fit_sha256": _digest(model.samples),
                "wall_ns": elapsed,
            })
        # Freeze a complete same-information record for every fitted arm.
        if len({_digest(arms[mode].samples) for mode in MODES}) != 1:
            raise ValueError("not all arms received identical FIT evidence")
        if len({(arms[m].mean, arms[m].sd) for m in MODES}) != 1:
            raise ValueError("B0 scaler mismatch across matched evidence")
    # Only now materialize pair-group held targets.
    held = list(_samples(world[0], gene, groups[("PUBLIC_DEV", None)]))
    if fit_groups.intersection(x.group for x in held):
        raise ValueError("leak between FIT and held group")
    metrics = {}
    for mode in MODES:
        model = arms[mode]
        metrics[mode] = {
            "held_rmse": group_weighted_rmse(
                held, model.predict, model.mean, model.sd),
            "b3_b0_mse": trace[mode][-1]["b0_mse"],
            "total_coordinate_solves": sum(x["coordinate_solves"]
                                            for x in trace[mode]),
            "total_address_writes": sum(x["address_writes"]
                                        for x in trace[mode]),
            "total_wall_ns": sum(x["wall_ns"] for x in trace[mode])
        }
    zero_rmse = _zero_score(held, arms["full_refit"].mean,
                           arms["full_refit"].sd)
    if not all(math.isfinite(m["held_rmse"]) for m in metrics.values()):
        raise ArithmeticError("nonfinite held score")
    c = metrics["contradiction"]
    r = metrics["full_refit"]
    best_gated = min(metrics["surprise"]["held_rmse"],
                     metrics["random"]["held_rmse"])
    pass_world = (
        c["b3_b0_mse"] <= 1.05 * r["b3_b0_mse"] and
        c["held_rmse"] <= .95 * r["held_rmse"] and
        c["held_rmse"] <= .95 * best_gated and
        c["total_coordinate_solves"] < r["total_coordinate_solves"]
    )
    return {"world": world, "status": "VALID", "stages_completed": 4,
            "fit_groups": len(fit_groups),
            "held_groups": len({s.group for s in held}),
            "fit_source_sha256": _digest(arms["full_refit"].samples),
            "held_source_sha256": _digest(held),
            "trace": trace, "arms": metrics,
            "zero_held_rmse": zero_rmse,
            "world_direct_gain": pass_world,
            "original_gfp_accessed": False,
            "reserved_labels_generated": False}


def run_primary():
    worlds = [run_world(world) for world in WORLDS]
    if any(w["status"] != "VALID" for w in worlds):
        result = "INVALID"
    elif sum(w["world_direct_gain"] for w in worlds) >= 3:
        result = "DIRECT_GAIN"
    else:
        result = "NO_GAIN"
    return {"schema": SCHEMA, "prereg_commit": PREREG_SHA,
            "classification": result, "worlds": worlds,
            "wsp210_211_212_cohorts_reused": False,
            "original_gfp_labels_accessed": False,
            "reserved_labels_accessed": False,
            "native_amalgam_accessed": False,
            "research_only": True}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = run_primary()
    Path(args.output).write_text(
        json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8")
    print("WSP213_CLASSIFICATION=" + result["classification"])
    for w in result["worlds"]:
        print("WSP213_WORLD=" + str(w["world"]) +
              " STATUS=" + w["status"] +
              " DIRECT_GAIN=" + str(w.get("world_direct_gain", False)))
