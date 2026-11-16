"""WSP-120 original public synthetic cohort. Frozen learners; one-shot owner gate.

No scientific first-use occurs when this module is imported or fixture-tested.
A separate scope-specific operator approval and GitHub Actions gate are required.
No protected/reserved seeds, no native model changes, no hidden-label training.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import time

import structural_growth as S
import trained_gru as G

ROOT = Path(__file__).resolve().parent
ARM_NAMES = ("NUMERIC_GROW_ACTIVE", "NUMERIC_GROW_PASSIVE",
             "NUMERIC_FIXED3", "SYMBOLIC_ACTIVE", "NO_UPDATE")
PLATFORMS = ("Linux", "Windows")
SHARDS = 8
ORIGINAL_SEEDS = tuple(range(120000, 120024))
CHECKPOINTS = (0, 4, 8, 16, 32)


def _learner(name, graph):
    if name == "NUMERIC_GROW_ACTIVE":
        return S.NumericGrow(graph, active=True, grow=True)
    if name == "NUMERIC_GROW_PASSIVE":
        return S.NumericGrow(graph, active=False, grow=True)
    if name == "NUMERIC_FIXED3":
        return S.NumericGrow(graph, active=False, grow=False)
    if name == "SYMBOLIC_ACTIVE":
        return S.SymbolicGrow(graph)
    if name == "NO_UPDATE":
        return S.NumericGrow(graph, active=False, updates=False)
    raise ValueError("WSP120_UNKNOWN_ARM")


def _score(predictions, truth):
    if len(predictions) != len(truth):
        raise AssertionError("WSP120_HELD_SHAPE")
    correct = sum(p is not None and p == t
                  for p, t in zip(predictions, truth))
    wrong = sum(p is not None and p != t
                for p, t in zip(predictions, truth))
    abstained = sum(p is None for p in predictions)
    if correct + wrong + abstained != 24:
        raise AssertionError("WSP120_HELD_COUNT")
    return {"correct": correct, "wrong_confident": wrong,
            "abstained": abstained, "held": len(truth),
            "predictions": list(predictions)}


def run_world(world, *, tier, family, max_calls=32, include_gru=True):
    """Run one fixed world/family/coverage with held truth only in scorer.

    For engineering tests, call with world=engineering_fixture_world and
    max_calls=4, include_gru=False. Never use original worlds during tests.
    """
    if type(world.seed) is not int or world.seed not in (
            *ORIGINAL_SEEDS, S.ENGINEERING_SEED):
        raise PermissionError("WSP120_WORLD_NOT_AUTHORIZED")
    if tier not in S.TIERS or type(family) is not int or family not in range(3):
        raise ValueError("WSP120_BAD_CONFIGURATION")
    if type(max_calls) is not int or max_calls not in (4, 8, 16, 32):
        raise ValueError("WSP120_BAD_MAX_CALLS")
    if type(include_gru) is not bool or (include_gru and max_calls != 32):
        raise ValueError("WSP120_GRU_REQUIRES_32")
    graph = world.public_graph(tier)
    pool = S.inquiry_pool(world)
    held = S.held_subjects(world)
    if len(held) != 24 or len(pool) != 40 or set(held) & set(pool):
        raise AssertionError("WSP120_SOURCE_SPLIT")
    law = world.targets[family]
    learners = {name: _learner(name, graph) for name in ARM_NAMES}
    sources = {name: S.EvidenceSource(world, law) for name in ARM_NAMES}
    start = {name: time.monotonic() for name in ARM_NAMES}
    rows = []

    for step in range(max_calls + 1):
        if step in CHECKPOINTS:
            # Predictions and cold checkpoints must be fixed BEFORE looking
            # up any held truth. The latter is used only by the scoring owner.
            predicted = {}
            cold = {}
            for name in ARM_NAMES:
                learner = learners[name]
                if sources[name].count != step:
                    raise AssertionError("WSP120_SOURCE_BUDGET")
                if isinstance(learner, S.NumericGrow):
                    blob = learner.snapshot()
                    restored = S.NumericGrow.restore(graph, blob)
                    pred = tuple(learner.infer(subject) for subject in held)
                    cold[name] = (blob == restored.snapshot() and
                                  pred == tuple(restored.infer(s) for s in held))
                    if not cold[name]:
                        raise AssertionError("WSP120_COLD_RESTORE_FAILED")
                else:
                    pred = tuple(learner.infer(subject) for subject in held)
                    cold[name] = None
                predicted[name] = pred
            trained = None
            if step == 32 and include_gru:
                # Give conventional training the exact passive-arm evidence.
                # All three optimization seeds are trained and selected on
                # training loss ONLY; never use held labels for selection.
                observations = tuple(learners["NUMERIC_GROW_PASSIVE"].observed)
                trained = G.train_conventional_gru(graph, observations)
                predicted["TRAINED_GRU_PASSIVE"] = tuple(trained.infer(held))

            # Single dedicated scoring boundary AFTER all predictions.
            full_graph = tuple(dict(enumerate(row)) for row in world.edges)
            truth = tuple(S.walk(full_graph, subject, law) for subject in held)
            arms = {}
            for name in ARM_NAMES:
                learner, source = learners[name], sources[name]
                record = _score(predicted[name], truth)
                record.update({
                    "source_calls": source.count,
                    "source_sha256": source.receipt.hexdigest(),
                    "cold_ok": cold[name],
                    "wall_seconds": time.monotonic() - start[name],
                    "numeric_bytes": len(learner.weights) * 4
                                     if isinstance(learner, S.NumericGrow) else 0,
                    "law_declared": learner.law() is not None,
                })
                arms[name] = record
            if trained is not None:
                gru_record = _score(predicted["TRAINED_GRU_PASSIVE"], truth)
                gru_record.update({
                    "source_calls": step,
                    "source_sha256":
                        sources["NUMERIC_GROW_PASSIVE"].receipt.hexdigest(),
                    "same_passive_observations": True,
                    "converged": trained.converged,
                    "training_loss": trained.training_loss if trained.converged else None,
                    "training_accuracy": trained.training_accuracy,
                    "epochs_by_seed": trained.epochs_by_seed,
                    "winning_seed": trained.winning_seed,
                    "parameter_count": trained.parameter_count,
                    "model_parameter_bytes": trained.parameter_count * 4,
                    "wall_seconds": trained.wall_seconds,
                })
                arms["TRAINED_GRU_PASSIVE"] = gru_record
            passive_hash = arms["NUMERIC_GROW_PASSIVE"]["source_sha256"]
            for passive_name in ("NUMERIC_FIXED3", "NO_UPDATE"):
                if arms[passive_name]["source_sha256"] != passive_hash:
                    raise AssertionError("WSP120_PASSIVE_SOURCE_MISMATCH")
            rows.append({"seed": world.seed, "tier": tier, "family": family,
                         "exposure": step, "arms": arms})

        if step == max_calls:
            break
        for name in ARM_NAMES:
            learner = learners[name]
            subject = learner.choose(pool)  # Only public graph/evidence.
            answer = sources[name].query(subject)  # Real toy consequence.
            learner.observe(subject, answer)
    return rows


def _operator_authorized():
    info = json.loads((ROOT / "first_use_authorization.json").read_text())
    if not (info.get("scientific_first_use_approved") is True
            and info.get("allowed_seed_start") == 120000
            and info.get("allowed_seed_end") == 120023
            and info.get("reserved_seed_start") == 120800
            and info.get("reserved_seed_end") == 120863
            and info.get("native_mutation_approved") is False):
        raise PermissionError("WSP120_OPERATOR_SCOPE_INVALID")
    prereg = json.loads((ROOT / "prereg.json").read_text())
    if (prereg.get("experiment_id") != "WSP-120"
            or prereg.get("authority", {}).get("scientific_first_use") is not False
            or prereg.get("fresh_source", {}).get("seeds")
            != "120000..120023 inclusive"):
        raise PermissionError("WSP120_PREREG_DRIFT")
    if (os.environ.get("WSP120_FIRST_USE_ALLOWED") != "public-120000-120023"
            or os.environ.get("GITHUB_REPOSITORY")
            != "spoonman136668-ai/Yggdrasil"
            or os.environ.get("GITHUB_RUN_ATTEMPT") != "1"):
        raise PermissionError("WSP120_OWNER_CI_FIRST_USE_REQUIRED")


def run_original_shard(shard, platform):
    _operator_authorized()
    if (type(shard) is not int or shard not in range(SHARDS)
            or platform not in PLATFORMS):
        raise PermissionError("WSP120_SHARD_NOT_ALLOWED")
    chosen = ORIGINAL_SEEDS[shard::SHARDS]
    rows = []
    began = time.monotonic()
    for seed in chosen:
        if seed in S.RESERVED_SEEDS:
            raise PermissionError("WSP120_PROTECTED_SEED")
        world = S.source_safe_world(seed)
        for tier in S.TIERS:
            for family in range(3):
                rows.extend(run_world(world, tier=tier, family=family))
    if len(rows) != len(chosen) * len(S.TIERS) * 3 * len(CHECKPOINTS):
        raise RuntimeError("WSP120_INCOMPLETE_SHARD")
    return {
        "schema": "wsp120.original-public-shard.v1",
        "first_use": True,
        "native_model_modified": False,
        "protected_source_opened": False,
        "platform": platform, "shard": shard,
        "seed_list": list(chosen),
        "source_sha": os.environ.get("GITHUB_SHA", ""),
        "elapsed_seconds": time.monotonic() - began,
        "rows": rows,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--original", action="store_true", required=True)
    parser.add_argument("--shard", type=int, required=True)
    parser.add_argument("--platform", choices=PLATFORMS, required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = run_original_shard(args.shard, args.platform)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(result, sort_keys=True, separators=(",", ":"))
    out.write_text(body + "\n", encoding="utf-8")
    print("WSP120_ORIGINAL_SHARD=" + json.dumps({
        "sha256": sha256(body.encode()).hexdigest(),
        "source_sha": result["source_sha"],
        "platform": args.platform, "shard": args.shard,
        "seeds": result["seed_list"], "rows": len(result["rows"]),
        "elapsed_seconds": result["elapsed_seconds"],
        "protected_source_opened": False, "native_model_modified": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
