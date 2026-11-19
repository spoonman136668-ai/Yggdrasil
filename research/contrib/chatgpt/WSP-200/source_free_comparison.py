"""WSP-208: complete fabricated-only comparison. Not an original GFP evaluator.

Bounded external research qualification: all eight frozen learner arms, four
cumulative FIT stages, the identical held group read, B0 readout retention,
warm refit convergence, cold restores and per-arm cost. Source-specific first
use is explicitly not implemented; real genes/digests are rejected upstream.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import math
import random
import time
import tracemalloc

from learner import Learner
from source_free_partition import SYNTHETIC_DIGEST, StructuralManifest
from source_free_targets import SyntheticOneLook, group_weighted_rmse

SCHEMA = "wsp208.fabricated-comparison.v1"
ARMS = (("contradiction", 4), ("full_refit", 4), ("full_refit", 8),
        ("always", 4), ("surprise", 4), ("random", 4),
        ("no_update", 4), ("shuffled_negative", 4))


def _mse(rows, model):
    return sum((model.predict(r.left, r.right) -
                (r.target-model.mean)/model.sd)**2 for r in rows)/len(rows)


def _paired_bootstrap(held, models, seed=20041, iterations=2000):
    """Bootstrap whole site-pair groups, never individual alternate alleles."""
    by_group = defaultdict(list)
    for row in held:
        by_group[row.group].append(row)
    groups = sorted(by_group)
    if len(groups) < 2:
        return None
    rng = random.Random(seed)
    per_group = {}
    for name, model in models.items():
        per_group[name] = [
            sum((model.predict(row.left, row.right) -
                 (row.target-model.mean)/model.sd)**2
                for row in by_group[g])/len(by_group[g]) for g in groups
        ]
    gains = []
    for _ in range(iterations):
        indices = [rng.randrange(len(groups)) for _ in groups]
        cand = math.sqrt(sum(per_group["contradiction_r4"][i]
                             for i in indices)/len(groups))
        ref = math.sqrt(sum(per_group["full_refit_r4"][i]
                            for i in indices)/len(groups))
        if ref <= 1e-12:
            raise ValueError("degenerate matched comparator bootstrap")
        gains.append(1-cand/ref)
    gains.sort()
    return {"seed":seed, "resamples":iterations, "unit":"site_pair_group",
            "gain_95pct": [gains[int(iterations*.025)],
                           gains[min(iterations-1,int(iterations*.975))]]}


def evaluate_fabricated(manifest: StructuralManifest, labels,
                        wildtype_receipt: str, *, source_digest: str) -> dict:
    if source_digest != SYNTHETIC_DIGEST:
        raise ValueError("real or unpinned outcome source forbidden")
    if not isinstance(manifest, StructuralManifest):
        raise ValueError("unrecognized structural manifest")
    if len({r.gene for r in manifest.eligible}) != 1:
        raise ValueError("must evaluate separate fabricated background models")
    gate = SyntheticOneLook(manifest, wildtype_receipt, labels,
                            source_digest=source_digest)
    models = {mode+"_r"+str(rank):Learner(source_digest,mode,rank)
              for mode,rank in ARMS}
    timings = {key:[] for key in models}
    b0 = None
    b0_initial_predictions = {}
    consumed_fit_ids = set()
    for stage in range(4):
        read_start = time.perf_counter_ns()
        batch = gate.fit_stage(stage)
        read_ns = time.perf_counter_ns()-read_start
        if consumed_fit_ids.intersection(row.sample_id for row in batch):
            raise ValueError("replayed FIT identity")
        consumed_fit_ids.update(row.sample_id for row in batch)
        if stage == 0:
            b0 = tuple(batch)
        for name, model in models.items():
            kwargs = {}
            if stage and name in ("surprise_r4", "random_r4"):
                kwargs["reference_write_count"] = len(
                    models["contradiction_r4"].changed_by_stage[-1])
            tracemalloc.start()
            start_cpu = time.process_time_ns()
            start_wall = time.perf_counter_ns()
            receipt = model.advance(stage, batch, **kwargs)
            chk = model.checkpoint()
            cold = Learner.restore(chk, source_digest)
            elapsed_ns = time.perf_counter_ns()-start_wall
            cpu_ns = time.process_time_ns()-start_cpu
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            if chk != cold.checkpoint() or any(
                model.predict(x.left,x.right) != cold.predict(x.left,x.right)
                    for x in b0):
                raise ValueError("cold restore mismatch")
            timings[name].append({
                "stage":stage, "fit_rows":len(batch),
                "shared_source_read_ns":read_ns,
                "model_and_cold_wall_ns":elapsed_ns,
                "model_and_cold_cpu_ns":cpu_ns,
                "python_traced_peak_bytes":peak,
                "checkpoint_bytes":len(chk),
                "changed_addresses":receipt["address_writes"],
                "cumulative_solves":receipt["solves"],
                "converged":model.convergence[-1]["converged"]})
            if stage == 0:
                b0_initial_predictions[name] = [
                    model.predict(row.left,row.right) for row in b0]
    if b0 is None or gate.invalid:
        raise ValueError("incomplete synthetic FIT intake")
    # Exactly one held read, after model fitting and cold validation.
    held = gate.public_dev_once()
    output = {"schema":SCHEMA,
              "authority":"FABRICATED_ONLY_NO_REAL_SOURCE_FIRST_USE",
              "classification":"SOURCE_FREE_DIAGNOSTIC_NOT_SCIENTIFIC_RESULT",
              "reserved_outcomes_accessed":False,
              "held_public_dev_reads":1,
              "fit_observation_receipts":len(consumed_fit_ids),
              "held_groups":len({row.group for row in held}), "arms":{}}
    for name, model in models.items():
        if model.stage!=3 or len(model.receipts)!=len(consumed_fit_ids):
            raise ValueError("arm not fully cumulative")
        if name.startswith("full_refit") and not all(
                t["converged"] is True for t in timings[name]):
            raise ValueError("conventional comparator failed convergence")
        b0_final = _mse(b0, model)
        original = b0_initial_predictions[name]
        b0_drift = sum((model.predict(row.left,row.right)-old)**2
                       for row,old in zip(b0,original))/len(b0)
        output["arms"][name] = {
            "dev_group_weighted_rmse":group_weighted_rmse(
                held, model.predict, model.mean, model.sd),
            "b0_mse_after_b3":b0_final,
            "b0_prediction_drift_mse":b0_drift,
            "stage_costs":timings[name],
            "all_stage_wall_ms":round(sum(
                row["shared_source_read_ns"]+
                row["model_and_cold_wall_ns"] for row in timings[name])/1e6,3),
            "all_stage_cpu_ms":round(sum(
                row["model_and_cold_cpu_ns"] for row in timings[name])/1e6,3),
            "checkpoint_sha256":hashlib.sha256(model.checkpoint()).hexdigest(),
            "factor_coordinates":sum(len(w) for w in model.weights.values())}
    candidate = output["arms"]["contradiction_r4"]
    comparator = output["arms"]["full_refit_r4"]
    score_ratio = candidate["dev_group_weighted_rmse"] / comparator["dev_group_weighted_rmse"]
    retention_ratio = (candidate["b0_mse_after_b3"] /
                       comparator["b0_mse_after_b3"]) if comparator["b0_mse_after_b3"]>1e-12 else None
    cost_ratio = comparator["all_stage_wall_ms"]/candidate["all_stage_wall_ms"]
    output["readout_only"] = {
        "dev_group_weighted_rmse":math.sqrt(sum(
            sum(((row.target-models["contradiction_r4"].mean)/
                 models["contradiction_r4"].sd)**2
                for row in held if row.group==g)/
            sum(row.group==g for row in held)
            for g in sorted({row.group for row in held})) /
            len({row.group for row in held}))}
    output["paired_comparison"] = {
        "cost_ratio":cost_ratio,
        "held_rmse_ratio":score_ratio,
        "b0_retention_mse_ratio":retention_ratio,
        "frozen_thresholds": {"min_cost_ratio":2.0,
                              "max_held_rmse_ratio":1.02,
                              "max_retention_mse_ratio":1.05},
        "diagnostic_thresholds_met":bool(cost_ratio>=2 and score_ratio<=1.02
                                       and retention_ratio is not None
                                       and retention_ratio<=1.05)}
    output["bootstrap"] = _paired_bootstrap(held,models)
    if not gate.dev_opened or gate.invalid:
        raise ValueError("held first-use state inconsistent")
    return output
