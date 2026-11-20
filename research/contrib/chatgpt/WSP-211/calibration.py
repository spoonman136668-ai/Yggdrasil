"""WSP-211: fresh, source-free convergence qualification; no WSP-210 cohort reuse.

The WSP-210 frozen primary was invalid and MUST NOT be evaluated from here.
This module accepts only WSP-211's disjoint synthetic development worlds.
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
import learner as core
from learner import Learner, pair_group, group_bucket, fit_stage
from source_free_partition import SYNTHETIC_DIGEST
from source_free_targets import group_weighted_rmse
from study import AdamRank4, _pairs, _samples, _mse, _zero_score, ridge_scope

CALIBRATION = ((21101, "hub", 24), (21102, "complete", 12))
RIDGE = 0.2
SWEEPS_PER_BLOCK = 8
MAX_BLOCKS = 100
SCHEMA = "wsp211.convergence-calibration.source-free.v1"
FORBIDDEN = frozenset((21011, 21012, 21013, 21014))


class BlockedFullRefit(Learner):
    """Same exact normal equations and objective; 8 sweeps per loss check.

    Unlike the WSP-210 historical 100-sweep cap, this *new* comparator
    permits 100 blocks (800 actual coordinate sweeps) with the inherited
    three-check relative-objective plateau rule. No new fit information.
    """

    def _sweep(self, active: set[str]) -> None:
        for _ in range(SWEEPS_PER_BLOCK):
            super()._sweep(active)


def metadata(world):
    if world not in CALIBRATION or world[0] in FORBIDDEN:
        raise ValueError("non-calibration world forbidden; WSP210 cannot be replayed")
    seed, topology, n = world
    gene = "FABRICATED_WSP211_" + str(seed)
    out = defaultdict(list)
    for i, j in _pairs(topology, n):
        group = pair_group(gene, i, j)
        bucket = group_bucket(group)
        if bucket in ("FIT", "PUBLIC_DEV"):
            stage = fit_stage(group) if bucket == "FIT" else None
            out[(bucket, stage)].append((i, j, group))
    if not all(out[("FIT", s)] for s in range(4)):
        raise ValueError("empty frozen development stage")
    if not out[("PUBLIC_DEV", None)]:
        raise ValueError("no source-free development groups")
    return gene, out


def run_world(world):
    gene, groups = metadata(world)
    refit = BlockedFullRefit(SYNTHETIC_DIGEST, "full_refit", 4)
    adam = AdamRank4(RIDGE)
    seen = set()
    first = None
    trace = []
    for stage in range(4):
        batch = list(_samples(world[0], gene, groups[("FIT", stage)]))
        if stage == 0:
            first = tuple(batch)
        ids = {s.sample_id for s in batch}
        if len(ids) != len(batch) or seen.intersection(ids):
            raise ValueError("sample replay")
        seen.update(ids)

        # The WSP-200 objective is evaluated only while the temporary
        # scalar ridge is in effect; it is restored before Adam starts.
        start = time.perf_counter_ns()
        old_solves = refit.solves
        try:
            with ridge_scope(RIDGE):
                receipt = refit.advance(stage, batch)
                objective = refit._objective()
                chk = refit.checkpoint()
                restored = BlockedFullRefit.restore(chk, SYNTHETIC_DIGEST)
                if restored.checkpoint() != chk:
                    raise ValueError("non-byte-identical refit cold restore")
                if any(restored.predict(x.left, x.right) !=
                       refit.predict(x.left, x.right) for x in first):
                    raise ValueError("cold refit function drift")
        except ArithmeticError as exc:
            return {"world": world, "status": "CONTROL_UNQUALIFIED",
                    "reason": "refit:" + str(exc), "stages_completed": stage,
                    "trace": trace, "reserved_labels_generated": False,
                    "original_source_accessed": False}
        actual_sweeps = (refit.solves - old_solves) // len(refit.weights)
        if (actual_sweeps !=
                SWEEPS_PER_BLOCK * refit.convergence[-1]["sweeps"] or
                not refit.convergence[-1]["converged"]):
            raise AssertionError("actual sweep accounting or plateau mismatch")
        refit_time = time.perf_counter_ns() - start
        adam_hist = adam.advance(stage, batch)
        cold_adam = AdamRank4.cold(adam.checkpoint())
        if any(cold_adam.predict(x.left, x.right) !=
               adam.predict(x.left, x.right) for x in first):
            raise ValueError("conventional Adam cold function drift")
        trace.append({
            "stage": stage,
            "fit_rows": len(batch),
            "cumulative_rows": len(refit.samples),
            "refit_actual_sweeps": actual_sweeps,
            "refit_objective": objective,
            "refit_b0_mse": _mse(first, refit.predict, refit.mean, refit.sd),
            "refit_wall_ns": refit_time,
            "refit_checkpoint_sha256": hashlib.sha256(chk).hexdigest(),
            "adam_epochs": adam_hist["epochs"],
            "adam_plateau": adam_hist["plateau"],
            "adam_objective": adam_hist["objective"],
            "adam_b0_mse": _mse(first, adam.predict, adam.mean, adam.sd),
            "adam_checkpoint_sha256": hashlib.sha256(adam.checkpoint()).hexdigest()
        })
        if not adam_hist["plateau"]:
            return {"world": world, "status": "CONTROL_UNQUALIFIED",
                    "reason": "Adam failed to plateau", "stages_completed": stage+1,
                    "trace": trace, "reserved_labels_generated": False,
                    "original_source_accessed": False}

    # No held label is computed until both conventional models have stopped.
    held = list(_samples(world[0], gene, groups[("PUBLIC_DEV", None)]))
    fit_groups = {s.group for s in refit.samples}
    if fit_groups.intersection(s.group for s in held):
        raise ValueError("FIT and PUBLIC_DEV group leakage")
    if refit.mean != adam.mean or refit.sd != adam.sd:
        raise AssertionError("conventional scaling parity failed")
    return {
        "world": world, "status": "CONTROL_QUALIFIED",
        "stages_completed": 4, "trace": trace,
        "zero_held_rmse": _zero_score(held, refit.mean, refit.sd),
        "refit_held_rmse": group_weighted_rmse(
            held, refit.predict, refit.mean, refit.sd),
        "adam_held_rmse": group_weighted_rmse(
            held, adam.predict, adam.mean, adam.sd),
        "held_groups": len({s.group for s in held}),
        "original_source_accessed": False,
        "reserved_labels_generated": False
    }


def run_calibration():
    results = [run_world(world) for world in CALIBRATION]
    qualified = all(w["status"] == "CONTROL_QUALIFIED" for w in results)
    return {
        "schema": SCHEMA,
        "classification": "CONTROL_QUALIFIED" if qualified else "CONTROL_UNQUALIFIED",
        "research_only": True,
        "wsp210_primary_reused": False,
        "original_gfp_labels_accessed": False,
        "reserved_labels_accessed": False,
        "worlds": results
    }


if __name__ == "__main__":
    print("WSP211_SOURCE_FREE_CALIBRATION=" +
          json.dumps(run_calibration(), sort_keys=True, separators=(",", ":")))
