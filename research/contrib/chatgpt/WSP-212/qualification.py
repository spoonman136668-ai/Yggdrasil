"""WSP-212 frozen synthetic comparator qualification; NOT a native learner.

The four WSP-212 calibration seeds are source-free and disjoint from all WSP-210
and WSP-211 cohorts. This module does not read or call original GFP data.
Refer to prereg.json, committed separately BEFORE this implementation.
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
from learner import Sample, Learner, pair_group, group_bucket, fit_stage
from source_free_partition import SYNTHETIC_DIGEST
from source_free_targets import group_weighted_rmse
from study import _pairs, _mse, _zero_score, ridge_scope
from calibration import BlockedFullRefit

SCHEMA = "wsp212.full-refit-parity.source-free.v1"
WORLDS = ((21201, "hub", 24), (21202, "complete", 12),
          (21203, "hub", 24), (21204, "complete", 12))
FORBIDDEN = frozenset((21011, 21012, 21013, 21014, 21101, 21102))
RIDGE = 0.2
RANK = 4
SWEEPS_PER_BLOCK = 8
MAX_BLOCKS = 100


def metadata(world):
    if world not in WORLDS or world[0] in FORBIDDEN:
        raise ValueError("world not in frozen WSP212 source-free calibration")
    seed, topology, n = world
    gene = f"FABRICATED_WSP212_{seed}"
    groups = defaultdict(list)
    for i, j in _pairs(topology, n):
        group = pair_group(gene, i, j)
        bucket = group_bucket(group)
        # Held labels are not generated until after all FIT stages converge.
        if bucket in ("FIT", "PUBLIC_DEV"):
            stage = fit_stage(group) if bucket == "FIT" else None
            groups[(bucket, stage)].append((i, j, group))
    if any(not groups[("FIT", stage)] for stage in range(4)):
        raise ValueError("frozen world has empty FIT stage")
    if not groups[("PUBLIC_DEV", None)]:
        raise ValueError("frozen world has no PUBLIC_DEV groups")
    return gene, groups


def _component(seed: int, allele: str, pos: int, dim: int) -> int:
    if allele not in ("C", "D") or dim not in range(RANK) or pos < 1:
        raise ValueError("invalid frozen source-free component")
    key = f"WSP212\0{seed}\0{allele}\0{pos}\0{dim}".encode("utf-8")
    return (hashlib.sha256(key).digest()[0] % 7) - 3


def target(seed: int, i: int, j: int, allele: str) -> float:
    # Exact integer dot product before a single rational -> float conversion.
    # No OS-specific sin/cos, random generator, or teacher-model execution.
    return sum(_component(seed, allele, i, k) *
               _component(seed, allele, j, k) for k in range(RANK)) / 9.0


def samples(seed, gene, pairs):
    for i, j, group in pairs:
        for alt in ("C", "D"):
            yield Sample(f"{seed}_{i}_{j}_{alt}", group,
                         f"{gene}\0{i}\0A\0{alt}",
                         f"{gene}\0{j}\0A\0{alt}",
                         target(seed, i, j, alt))


def _identity_digest(rows) -> str:
    payload = [(r.sample_id, r.group, r.left, r.right, r.target)
               for r in rows]
    return hashlib.sha256(json.dumps(payload, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def run_world(world):
    gene, groups = metadata(world)
    refit = BlockedFullRefit(SYNTHETIC_DIGEST, "full_refit", RANK)
    first = None
    trace = []
    observed = set()
    seen_fit_groups = set()
    for stage in range(4):
        batch = sorted(samples(world[0], gene, groups[("FIT", stage)]),
                       key=lambda x: x.sample_id)
        if stage == 0:
            first = tuple(batch)
        ids = {x.sample_id for x in batch}
        group_ids = {x.group for x in batch}
        if (len(ids) != len(batch) or observed.intersection(ids) or
                seen_fit_groups.intersection(group_ids)):
            raise ValueError("replayed FIT rows or pair groups")
        observed.update(ids)
        seen_fit_groups.update(group_ids)
        start = time.perf_counter_ns()
        solves_before = refit.solves
        try:
            with ridge_scope(RIDGE):
                refit.advance(stage, batch)
                objective = refit._objective()
                checkpoint = refit.checkpoint()
                cold = BlockedFullRefit.restore(checkpoint, SYNTHETIC_DIGEST)
                if checkpoint != cold.checkpoint():
                    raise ValueError("non-byte-identical cold checkpoint")
                if any(cold.predict(s.left, s.right) !=
                       refit.predict(s.left, s.right) for s in first):
                    raise ValueError("cold restoration changed B0 function")
        except ArithmeticError as exc:
            return {"world": world, "status": "CONTROL_UNQUALIFIED",
                    "reason": str(exc), "stages_completed": stage,
                    "trace": trace, "original_source_accessed": False,
                    "reserved_labels_generated": False}
        sweeps = (refit.solves - solves_before) // len(refit.weights)
        expected = SWEEPS_PER_BLOCK * refit.convergence[-1]["sweeps"]
        if (sweeps != expected or sweeps > SWEEPS_PER_BLOCK * MAX_BLOCKS or
                not refit.convergence[-1]["converged"]):
            raise AssertionError("convergence and actual solve counts disagree")
        b0 = _mse(first, refit.predict, refit.mean, refit.sd)
        if not math.isfinite(objective) or not math.isfinite(b0):
            raise ArithmeticError("nonfinite comparator diagnostic")
        trace.append({
            "stage": stage,
            "new_fit_rows": len(batch),
            "cumulative_fit_rows": len(refit.samples),
            "cumulative_fit_groups": len(seen_fit_groups),
            "actual_sweeps": sweeps,
            "objective": objective,
            "b0_retention_mse": b0,
            "b0_zero_mse": _mse(first, lambda a,b: 0.0,
                               refit.mean, refit.sd),
            "checkpoint_sha256": hashlib.sha256(checkpoint).hexdigest(),
            "fit_source_sha256": _identity_digest(refit.samples),
            "elapsed_wall_ns": time.perf_counter_ns() - start
        })
    # Held labels are generated exactly once only after converged B3.
    held = list(samples(world[0], gene, groups[("PUBLIC_DEV", None)]))
    if seen_fit_groups.intersection(s.group for s in held):
        raise ValueError("held group FIT leakage")
    z = _zero_score(held, refit.mean, refit.sd)
    r = group_weighted_rmse(held, refit.predict, refit.mean, refit.sd)
    if not all(map(math.isfinite, (z, r))):
        raise ArithmeticError("nonfinite held diagnostic")
    return {
        "world": world, "status": "CONTROL_QUALIFIED", "stages_completed": 4,
        "trace": trace,
        "fit_groups": len(seen_fit_groups),
        "held_groups": len({s.group for s in held}),
        "held_source_sha256": _identity_digest(held),
        "zero_held_rmse": z, "refit_held_rmse": r,
        "original_source_accessed": False,
        "reserved_labels_generated": False
    }


def run_calibration():
    results = [run_world(w) for w in WORLDS]
    qualified = all(w["status"] == "CONTROL_QUALIFIED" for w in results)
    return {"schema": SCHEMA,
            "classification": "CONTROL_QUALIFIED" if qualified
                              else "CONTROL_UNQUALIFIED",
            "original_gfp_labels_accessed": False,
            "reserved_labels_accessed": False,
            "wsp210_wsp211_cohorts_reused": False,
            "research_only": True, "worlds": results}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = run_calibration()
    destination = Path(args.output)
    destination.write_text(json.dumps(result, sort_keys=True, indent=2,
                          allow_nan=False) + "\n", encoding="utf-8")
    print("WSP212_CONTROL_CLASSIFICATION=" + result["classification"])
    for w in result["worlds"]:
        print(f"WSP212_WORLD={w['world']} STATUS={w['status']} STAGES={w['stages_completed']}")
