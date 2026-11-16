"""NKR-12: preregistered outside-GF(2) causal-operator capacity falsification.

Source-safe, deliberately synthetic actions. This DOES NOT add a new learner
or consume authentic hidden-source consequences. NKR-11 native candidate
and its frozen successful experiment are left unmodified.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from yggdrasil.native_intervention_repair import (
    BUNDLE_SCHEMA, SOURCE_KIND, SOURCE_MODE, NativeInterventionRepair,
    canonical, digest,
)
from yggdrasil.public_causal_cells import PublicCausalCells

BASE_MASKS = (1, 2, 4, 8, 3, 5, 6, 9, 10, 12, 13, 14)
GATES = (
    ("AND", 0, 1), ("AND", 0, 2), ("AND", 1, 3),
    ("OR", 0, 1), ("OR", 0, 2), ("OR", 1, 3),
)
TRAIN = (0, 1, 2, 4, 8, 3, 5, 10)
COLD = (6, 7, 9, 11, 12, 13, 14, 15)
WORLDS = 12


def parity(n):
    return n.bit_count() & 1


def gate_value(kind, first, second, context):
    a = (context >> first) & 1
    b = (context >> second) & 1
    return (a & b) if kind == "AND" else (a | b)


class InterventionWorld:
    """Oracle only: acts on a chosen public context and action."""
    __slots__ = ("world", "action_calls")

    def __init__(self, world):
        if type(world) is not int or not 0 <= world < WORLDS:
            raise ValueError("NKR12_INVALID_WORLD")
        self.world = world
        self.action_calls = 0

    def intervene(self, context, action, *, old=False):
        if type(context) is not int or not 0 <= context < 16:
            raise ValueError("NKR12_INVALID_CONTEXT")
        if type(action) is not int or action not in (0, 1):
            raise ValueError("NKR12_INVALID_ACTION")
        self.action_calls += 1
        if old:
            return parity(context & (1 << (self.world % 4))) ^ action
        kind, i, j = GATES[self.world % len(GATES)]
        return parity(context & BASE_MASKS[self.world]) ^ (
            action & gate_value(kind, i, j, context))


def bundle(source_id, observations):
    return canonical({
        "schema": BUNDLE_SCHEMA,
        "source_id": source_id,
        "source_kind": SOURCE_KIND,
        "source_mode": SOURCE_MODE,
        "records": [list(x) for x in observations],
    })


def warm_events(env):
    return tuple((
        f"old-nkr12-world-{env.world:02d}-{2*x+a:02d}", x, a,
        env.intervene(x, a, old=True)
    ) for x in range(16) for a in (0, 1))


def repair_events(env):
    actions = ((0, 1), (0, 0)) + tuple(
        (x, a) for x in TRAIN[1:] for a in (0, 1))
    assert len(actions) == 16 and len(set(actions)) == 16
    return tuple((
        f"shift-nkr12-world-{env.world:02d}-{index:02d}", x, a,
        env.intervene(x, a)
    ) for index, (x, a) in enumerate(actions))


def conventional_fit(observations):
    """Independent exhaustive conventional reference: 16 masks x 6 gates.

    Does not import native GF2 features, model fitting, or any hidden truth.
    Each complete signature matches only the 16 public action observations.
    """
    matching = []
    for mask in range(16):
        for kind, i, j in GATES:
            if all(
                parity(x & mask) ^ (a & gate_value(kind, i, j, x)) == y
                for _, x, a, y in observations
            ):
                matching.append((mask, kind, i, j))
    return tuple(matching)


def conventional_predict(matching, context, action):
    possible = {
        parity(context & mask) ^ (action & gate_value(kind, i, j, context))
        for mask, kind, i, j in matching
    }
    return next(iter(possible)) if len(possible) == 1 else None


def run_frozen():
    started = time.monotonic()
    native_before = PublicCausalCells().snapshot()
    totals = {
        "worlds": WORLDS,
        "old_public_actions": 0,
        "new_public_actions": 0,
        "cold_evaluation_actions": 0,
        "old_retention_evaluation_actions": 0,
        "first_public_contradictions": 0,
        "native_inconsistent_rejections": 0,
        "native_accepted_repairs": 0,
        "native_qualified_repair_coverage": 0,
        "native_unsupported_confident_predictions": 0,
        "old_retained_correct": 0,
        "old_retention_queries": WORLDS * 32,
        "strong_reference_correct": 0,
        "strong_reference_covered": 0,
        "static_old_correct": 0,
        "cold_queries": WORLDS * len(COLD) * 2,
        "strong_reference_unique_fits": 0,
        "native_checkpoint_cold_restores": 0,
    }
    worlds = []
    for world in range(WORLDS):
        env = InterventionWorld(world)
        old_observed = warm_events(env)
        warm_raw = bundle(f"nkr12-warm-world-{world:02d}", old_observed)
        native = NativeInterventionRepair.from_warmup(warm_raw, digest(warm_raw))
        prior_checkpoint = native.checkpoint()
        totals["old_public_actions"] += len(old_observed)

        changed_observed = repair_events(env)
        repair_raw = bundle(f"nkr12-repair-world-{world:02d}", changed_observed)
        totals["new_public_actions"] += len(changed_observed)
        if native.prior(0, 1) != changed_observed[0][3]:
            totals["first_public_contradictions"] += 1
        else:
            raise AssertionError("NKR12_FIRST_CONTRADICTION_MISSING")

        # The original 10-feature parity representation has no degree-two
        # action-context interaction. Incompatible public consequences must
        # produce no new accepted/learned checkpoint.
        candidate = None
        try:
            candidate, _ = native.stage_public_interventions(
                repair_raw, digest(repair_raw))
        except ValueError as exc:
            if str(exc) != "NKR11_CONTRADICTORY_SAME_EPOCH_EVIDENCE":
                raise
            totals["native_inconsistent_rejections"] += 1
        if candidate is not None:
            totals["native_accepted_repairs"] += int(candidate.change_detected)
        if native.checkpoint() != prior_checkpoint or native.change_detected:
            raise AssertionError("NKR12_ORIGINAL_PRIOR_MUTATED_AFTER_REJECTION")

        cold_prior = NativeInterventionRepair(
            prior_checkpoint, digest(prior_checkpoint))
        if cold_prior.checkpoint() != native.checkpoint():
            raise AssertionError("NKR12_COLD_RESTORED_PRIOR_DRIFT")
        totals["native_checkpoint_cold_restores"] += 1
        fitted = conventional_fit(changed_observed)
        totals["strong_reference_unique_fits"] += (len(fitted) == 1)
        # The scored reference gets no additional data, no oracle masks.
        strong_world_correct = 0
        old_world_correct = 0
        for x in COLD:
            for a in (0, 1):
                predicted = conventional_predict(fitted, x, a)
                # New source outcome is revealed only AFTER predicting.
                actual = env.intervene(x, a)
                totals["cold_evaluation_actions"] += 1
                totals["strong_reference_covered"] += (predicted is not None)
                match = predicted is not None and predicted == actual
                totals["strong_reference_correct"] += int(match)
                strong_world_correct += int(match)
                prior_is_right = native.prior(x, a) == actual
                totals["static_old_correct"] += int(prior_is_right)
                old_world_correct += int(prior_is_right)
                if candidate is not None and candidate.change_detected:
                    response = candidate.predict(x, a)
                    proposed = response.get("public_outcome")
                    totals["native_qualified_repair_coverage"] += int(
                        proposed is not None)
                    totals["native_unsupported_confident_predictions"] += int(
                        proposed is not None and proposed != actual)
        for x in range(16):
            for a in (0, 1):
                old_actual = env.intervene(x, a, old=True)
                totals["old_retention_evaluation_actions"] += 1
                totals["old_retained_correct"] += int(
                    native.prior(x, a) == old_actual
                    and cold_prior.prior(x, a) == old_actual)
        worlds.append({
            "world": world,
            "operator": GATES[world % len(GATES)][0],
            "operator_pair": list(GATES[world % len(GATES)][1:]),
            "first_public_contradiction": True,
            "native_repair_rejected": candidate is None,
            "strong_reference_fitted_candidates": len(fitted),
            "strong_cold_correct": strong_world_correct,
            "old_prior_cold_correct": old_world_correct,
            "warm_checkpoint_sha256": digest(prior_checkpoint),
            "new_public_bundle_sha256": digest(repair_raw),
        })
    if PublicCausalCells().snapshot() != native_before:
        raise AssertionError("NKR12_ACCEPTED_NATIVE_YPC1_DRIFT")
    engineering_safety = (
        totals["native_inconsistent_rejections"] == WORLDS
        and totals["native_accepted_repairs"] == 0
        and totals["native_unsupported_confident_predictions"] == 0
        and totals["old_retained_correct"] == WORLDS * 32
        and totals["native_checkpoint_cold_restores"] == WORLDS
        and totals["first_public_contradictions"] == WORLDS
        and totals["strong_reference_unique_fits"] == WORLDS
        and totals["strong_reference_correct"] == WORLDS * len(COLD) * 2
    )
    return {
        "schema": "yggdrasil.nkr12.offfamily-intervention-diagnostic.v1",
        "classification": (
            "OUTSIDE_FAMILY_NATIVE_REPRESENTATION_NO_GO_SAFE_REJECTION"
            if engineering_safety else "OUTSIDE_FAMILY_DIAGNOSTIC_UNQUALIFIED"),
        "source_kind": "ENGINEERING_FIXTURE_ONLY_OBSERVED_ACTIONS",
        "source_authenticity": "NOT_AUTHENTIC_EXTERNAL_CAUSAL_EVIDENCE",
        "hypothesis_family": "TWO_BIT_AND_OR_ACTION_GATES_OUTSIDE_GF2_LINEAR_CLASS",
        "totals": totals,
        "world_receipts": worlds,
        "frozen_engineering_safety_pass": engineering_safety,
        "outside_family_native_learning_success": False,
        "strong_control_also_frozen_predeclared_family": True,
        "original_scientific_first_use": False,
        "scientific_pass": False,
        "accepted_native": False,
        "historical_knowledge_source_opened": False,
        "original_yggdrasil_causal_state_unchanged": True,
        "wall_seconds": time.monotonic() - started,
    }


if __name__ == "__main__":
    print("NKR12_FROZEN_OFFFAMILY_DIAGNOSTIC=" +
          json.dumps(run_frozen(), sort_keys=True, separators=(",", ":")),
          flush=True)
