"""WSP-120 comparison plumbing: disjoint engineering fixture only.

This module refuses the public first-use cohort. Its scores diagnose the
harness, not scientific accuracy or permission for original-source evaluation.
No new workflow, model admission or runtime control is introduced.
"""
from __future__ import annotations

from hashlib import sha256
import json
import time

import structural_growth as S


ARMS = ("NUMERIC_GROW_ACTIVE", "NUMERIC_GROW_PASSIVE",
        "NUMERIC_FIXED3", "SYMBOLIC_ACTIVE", "NO_UPDATE")


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


def _score(learner, subjects, truth, *, batched=False):
    # The conventional GRU accepts a sequence; structural learners take one subject.
    predicted = (tuple(learner.infer(subjects)) if batched else
                 tuple(learner.infer(s) for s in subjects))
    if len(predicted) != len(subjects):
        raise RuntimeError("WSP120_SCORE_SHAPE_MISMATCH")
    return {
        "correct": sum(p == y for p, y in zip(predicted, truth)),
        "wrong_confident": sum(p is not None and p != y
                               for p, y in zip(predicted, truth)),
        "abstained": sum(p is None for p in predicted),
        "held": len(subjects),
        "predictions": list(predicted),
    }


def run_fixture(*, tier=384, family=0, exposure=4, include_gru=False):
    """Exercise every arm on the sole permitted engineering seed 120900.

    The independently coded symbolic arm can choose its own legal queries.
    Fixed3, passive numeric and no-update use the same source-blind order;
    active numeric and symbolic select under identical query budgets.
    Held answers are used only after all query/weight updates are complete.
    """
    if tier not in S.TIERS or type(family) is not int or family not in range(3):
        raise ValueError("WSP120_INVALID_FIXTURE_CONFIGURATION")
    if type(exposure) is not int or exposure not in S.EXPOSURES:
        raise ValueError("WSP120_INVALID_EXPOSURE")
    if type(include_gru) is not bool or (include_gru and exposure != 32):
        raise ValueError("WSP120_GRU_REQUIRES_32_OBSERVATIONS")
    world = S.engineering_fixture_world()
    if world.seed != S.ENGINEERING_SEED or world.seed in S.PUBLIC_SEEDS:
        raise PermissionError("WSP120_PRIMARY_FIRST_USE_DENIED")
    graph = world.public_graph(tier)
    pool = S.inquiry_pool(world)
    held = S.held_subjects(world)
    truth = tuple(S.walk(tuple(dict(enumerate(row)) for row in world.edges),
                         s, world.targets[family]) for s in held)
    learners = {name: _learner(name, graph) for name in ARMS}
    sources = {name: S.EvidenceSource(world, world.targets[family])
               for name in ARMS}
    result = {"schema": "wsp120.fixture-evaluation.v1", "scientific": False,
              "seed": world.seed, "tier": tier, "family": family,
              "exposure": exposure, "arms": {}}
    for name in ARMS:
        learner = learners[name]
        source = sources[name]
        start = time.monotonic()
        for _ in range(exposure):
            subject = learner.choose(pool)
            answer = source.query(subject)
            learner.observe(subject, answer)
        observations = tuple(learner.observed if isinstance(
            learner, S.NumericGrow) else learner.history)
        if len(observations) != exposure or source.count != exposure:
            raise RuntimeError("WSP120_BUDGET_MISMATCH")
        cold_ok = None
        if isinstance(learner, S.NumericGrow):
            snapshot = learner.snapshot()
            restored = S.NumericGrow.restore(graph, snapshot)
            cold_ok = (restored.snapshot() == snapshot and
                       all(restored.infer(s) == learner.infer(s) for s in held))
            if not cold_ok:
                raise RuntimeError("WSP120_COLD_MISMATCH")
        record = _score(learner, held, truth)
        record.update({
            "observations": [list(pair) for pair in observations],
            "source_calls": source.count,
            "source_sha256": source.receipt.hexdigest(),
            "cold_ok": cold_ok,
            "wall_seconds": time.monotonic() - start,
        })
        result["arms"][name] = record
    if include_gru:
        # Only exactly the same 32 passive observations, never held labels.
        import trained_gru as G
        passive = result["arms"]["NUMERIC_GROW_PASSIVE"]["observations"]
        comparison = G.train_conventional_gru(graph, passive)
        result["arms"]["TRAINED_GRU_PASSIVE"] = {
            **_score(comparison, held, truth, batched=True),
            "converged": comparison.converged,
            "epochs_by_seed": comparison.epochs_by_seed,
            "training_loss": comparison.training_loss,
            "training_accuracy": comparison.training_accuracy,
            "parameter_count": comparison.parameter_count,
            "wall_seconds": comparison.wall_seconds,
            "same_passive_observations": True,
            "scientifically_valid": comparison.converged,
        }
        if not comparison.converged:
            result["invalid_reason"] = "WSP120_TRAINED_GRU_DID_NOT_CONVERGE"
    # Stable evidence receipt excludes nondeterministic wall-clock timing.
    stable = json.loads(json.dumps(result))
    for record in stable["arms"].values():
        record.pop("wall_seconds", None)
    raw = json.dumps(stable, sort_keys=True, separators=(",", ":")).encode()
    result["receipt_sha256"] = sha256(raw).hexdigest()
    return result
