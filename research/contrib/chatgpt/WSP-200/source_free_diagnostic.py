"""WSP-202 fabricated-only qualification diagnostic; NEVER opens original source.

Run: python research/contrib/chatgpt/WSP-200/source_free_diagnostic.py
Figures are tiny-fixture engineering observations, not WSP-200 scientific results.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import time
import tracemalloc

from learner import Learner, Sample, fit_stage, group_bucket, pair_group

DIGEST = "f" * 64  # synthetic sentinel, deliberately not original dataset hash
GENE = "FABRICATED_WSP202"


def fixture():
    streams: dict[int, list[Sample]] = {s: [] for s in range(4)}
    held: list[Sample] = []
    for i in range(1, 14):
        for j in range(i + 1, 14):
            group = pair_group(GENE, i, j)
            bucket = group_bucket(group)
            for allele in ("B", "C"):
                a, b = f"{GENE}\0{i}\0A\0B", f"{GENE}\0{j}\0A\0{allele}"
                # Fixed synthetic latent targets; no original protein measurements.
                y = ((i * 7 + j * 11 + (3 if allele == "C" else 0)) % 19 - 9) / 2
                obs = Sample(f"s_{i}_{j}_{allele}", group, a, b, float(y))
                if bucket == "FIT":
                    streams[fit_stage(group)].append(obs)
                elif bucket == "PUBLIC_DEV":
                    held.append(obs)
    if not all(streams.values()) or not held:
        raise RuntimeError("fabricated group split incomplete")
    return streams, held


def group_rmse(model: Learner | None, held: list[Sample], scale: tuple[float, float]):
    mean, sd = scale
    by_group = defaultdict(list)
    for s in held:
        normalized = (s.target - mean) / sd
        predicted = model.predict(s.left, s.right) if model is not None else 0.0
        by_group[s.group].append((predicted - normalized)**2)
    return math.sqrt(sum(sum(vals) / len(vals) for vals in by_group.values()) / len(by_group))


def one_stage(model: Learner, stage: int, batch: list[Sample], matched: int | None):
    tracemalloc.start()
    start_w, start_c = time.perf_counter_ns(), time.process_time_ns()
    receipt = model.advance(stage, batch, **(
        {"reference_write_count": matched} if matched is not None else {}))
    checkpoint = model.checkpoint()
    restored = Learner.restore(checkpoint, DIGEST)
    if restored.checkpoint() != checkpoint:
        raise RuntimeError("non-canonical restored state")
    if any(restored.predict(s.left, s.right) != model.predict(s.left, s.right) for s in batch):
        raise RuntimeError("cold-restored prediction changed")
    duration_w, duration_c = time.perf_counter_ns() - start_w, time.process_time_ns() - start_c
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {"stage": stage, "wall_ns": duration_w, "cpu_ns": duration_c,
            "peak_python_traced_bytes": peak, "checkpoint_bytes": len(checkpoint),
            "address_writes": receipt["address_writes"], "solves_total": receipt["solves"],
            "converged": model.convergence[-1]["converged"]}


def main():
    streams, held = fixture()
    arms = [("contradiction", 4), ("full_refit", 4), ("full_refit", 8),
            ("always", 4), ("surprise", 4), ("random", 4),
            ("no_update", 4), ("shuffled_negative", 4)]
    models = {f"{mode}_r{rank}": Learner(DIGEST, mode, rank) for mode, rank in arms}
    result = {"schema": "wsp202.synthetic-engineering-diagnostic.v1",
              "source": "FABRICATED_ONLY; NO_GFP_OUTCOME_ACCESS",
              "warning": "Engineering diagnostics only; not scientific evidence",
              "python_version": os.sys.version.split()[0],
              "fixture_counts": {"B" + str(k): len(v) for k, v in streams.items()},
              "held_rows": len(held), "arms": {}, "readout_only": {}}
    for key in models:
        result["arms"][key] = {"stages": []}
    witnesses = {}
    for stage, batch in streams.items():
        for key, model in models.items():
            count = None
            if stage and key in ("surprise_r4", "random_r4"):
                count = len(models["contradiction_r4"].changed_by_stage[-1])
            receipt = one_stage(model, stage, batch, count)
            result["arms"][key]["stages"].append(receipt)
            if stage == 0:
                witnesses[key] = [(s, model.predict(s.left, s.right)) for s in batch]
        if stage:
            for key in ("surprise_r4", "random_r4"):
                assert result["arms"][key]["stages"][-1]["address_writes"] == result["arms"]["contradiction_r4"]["stages"][-1]["address_writes"]
    for key, model in models.items():
        expected = witnesses[key]
        saved = model.checkpoint()
        mse = sum((model.predict(s.left, s.right) - (s.target-model.mean)/model.sd)**2 for s, _ in expected) / len(expected)
        prior_mse = sum((pred - (s.target-model.mean)/model.sd)**2 for s, pred in expected) / len(expected)
        entry = result["arms"][key]
        entry["b0_mse_at_b0"] = prior_mse
        entry["b0_mse_after_b3"] = mse
        entry["dev_group_weighted_rmse"] = group_rmse(model, held, (model.mean, model.sd))
        entry["total_wall_ms"] = round(sum(x["wall_ns"] for x in entry["stages"]) / 1e6, 3)
        entry["total_cpu_ms"] = round(sum(x["cpu_ns"] for x in entry["stages"]) / 1e6, 3)
        entry["rank_parameters"] = sum(len(x) for x in model.weights.values())
        entry["held_prediction_max_abs"] = max(abs(model.predict(s.left, s.right)) for s in held)
        entry["held_near_zero_readout"] = entry["held_prediction_max_abs"] < 1e-5
        entry["state_sha256"] = hashlib.sha256(saved).hexdigest()
        if any(s.sample_id in model.receipts for s in held):
            raise RuntimeError("held group leaked into learner")
    # Readout-only B0 zero interaction residual, no trained factors.
    zero_model = models["contradiction_r4"]
    result["readout_only"] = {"dev_group_weighted_rmse": group_rmse(None, held, (zero_model.mean, zero_model.sd))}
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
