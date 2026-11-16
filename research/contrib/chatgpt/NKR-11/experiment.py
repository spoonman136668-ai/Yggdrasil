"""NKR-11: frozen, paired-intervention causal-relation development experiment.

The environment contains a withheld mechanism per world. It returns only
the observed consequence of the chosen action to the learner. The learner
does not import this module. This is SYNTHETIC, not real-world intelligence.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from yggdrasil.native_intervention_repair import (
    BUNDLE_SCHEMA, SOURCE_KIND, SOURCE_MODE,
    IntegerCausalSignature, NativeInterventionRepair,
    canonical, digest,
)
from yggdrasil.public_causal_cells import PublicCausalCells

BASE_MASKS = (1, 2, 4, 8, 3, 5, 6, 9, 10, 12, 13, 14)
INTERACTION_MASKS = (3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 6)
TRAIN_CONTEXTS = (0, 1, 2, 4, 8, 3, 5, 10)
COLD_CONTEXTS = (6, 7, 9, 11, 12, 13, 14, 15)
WORLD_COUNT = 12
FEATURE_COUNT = 10


class ComputationalEnvironment:
    """Hidden deterministic action-consequence program; not model-facing."""
    __slots__ = ("world_id", "action_count")

    def __init__(self, world_id):
        if type(world_id) is not int or not 0 <= world_id < WORLD_COUNT:
            raise ValueError("NKR11_ENV_WORLD_ID_INVALID")
        self.world_id = world_id
        self.action_count = 0

    def intervene(self, context, action, *, old_mechanism=False):
        if type(context) is not int or not 0 <= context < 16:
            raise ValueError("NKR11_ENV_CONTEXT_INVALID")
        if type(action) is not int or action not in (0, 1):
            raise ValueError("NKR11_ENV_ACTION_INVALID")
        self.action_count += 1
        if old_mechanism:
            return ((context & (1 << (self.world_id % 4))).bit_count() & 1) ^ action
        base = ((context & BASE_MASKS[self.world_id]).bit_count() & 1)
        conditional = ((context & INTERACTION_MASKS[self.world_id]).bit_count() & 1)
        return base ^ (action & conditional)


def evidence(source_id, observations):
    return canonical({
        "schema": BUNDLE_SCHEMA,
        "source_id": source_id,
        "source_kind": SOURCE_KIND,
        "source_mode": SOURCE_MODE,
        "records": [list(item) for item in observations],
    })


def collect_warmup(env):
    return [
        (f"warm-world-{env.world_id:02d}-{index:02d}", x, action,
         env.intervene(x, action, old_mechanism=True))
        for index, (x, action) in enumerate(
            (x, action) for x in range(16) for action in (0, 1))
    ]


def collect_paired_interventions(env):
    queries = [(0, 1), (0, 0)] + [
        (context, action) for context in TRAIN_CONTEXTS[1:]
        for action in (0, 1)
    ]
    assert len(queries) == 16 and len(set(queries)) == 16
    return [
        (f"repair-world-{env.world_id:02d}-{index:02d}", x, action,
         env.intervene(x, action))
        for index, (x, action) in enumerate(queries)
    ]


def collect_passive(env):
    # Same 16 observations, same 8 training contexts, but no controlled
    # action variation; a=context bit0 on both repeated observations.
    return [
        (f"passive-world-{env.world_id:02d}-{index:02d}",
         context, context & 1, env.intervene(context, context & 1))
        for index, context in enumerate(TRAIN_CONTEXTS * 2)
    ]


def collect_random(env):
    # Reproducible, independent prespecified choice of one real public
    # action each time, without peeking at an outcome before acting.
    entries = []
    for index, x in enumerate(TRAIN_CONTEXTS * 2):
        seed = hashlib.sha256(
            f"nkr11:world={env.world_id}:ctx={x}:draw={index}".encode("ascii")
        ).digest()
        action = seed[0] & 1
        entries.append((f"random-world-{env.world_id:02d}-{index:02d}",
                        x, action, env.intervene(x, action)))
    return entries


def _independent_candidate_signature(signature, context, action):
    """Fully enumerated exact symbolic 10-feature theory, independent code."""
    main_mask = (signature >> 1) & 15
    action_mask = (signature >> 6) & 15
    effect = (signature >> 5) & 1
    result = ((signature & 1) ^ ((main_mask & context).bit_count() & 1))
    return result ^ (action & (effect ^ ((action_mask & context).bit_count() & 1)))


def independent_symbolic_fit(observations):
    # Conventional fully-fitted model selection: enumerate EVERY one of
    # 2**10 possible deterministic parity/intervention signatures.
    possible = []
    for signature in range(1 << FEATURE_COUNT):
        if all(_independent_candidate_signature(signature, x, a) == y
               for _, x, a, y in observations):
            possible.append(signature)
    return tuple(possible)


def independent_symbolic_predict(candidates, context, action):
    answers = {_independent_candidate_signature(s, context, action)
               for s in candidates}
    return next(iter(answers)) if len(answers) == 1 else None


def score(prediction, truth):
    return int(prediction is not None and prediction == truth)


def run_frozen():
    started = time.monotonic()
    original_native = PublicCausalCells().snapshot()
    total = {
        "native_correct": 0,
        "native_coverage": 0,
        "passive_correct": 0,
        "passive_coverage": 0,
        "random_correct": 0,
        "random_coverage": 0,
        "static_old_correct": 0,
        "exact_symbolic_correct": 0,
        "instant_reset_correct": 0,
        "old_retained_correct": 0,
        "contradiction_triggers": 0,
        "new_full_rank_signatures": 0,
        "worlds": WORLD_COUNT,
        "cold_queries": WORLD_COUNT * len(COLD_CONTEXTS) * 2,
        "old_retention_queries": WORLD_COUNT * 16 * 2,
        "public_observations_per_world": 16,
        "matched_action_budgets": True,
    }
    checkpoints = []
    worlds = []
    for world in range(WORLD_COUNT):
        env = ComputationalEnvironment(world)
        warm = collect_warmup(env)
        warm_raw = evidence(f"warm-bundle-world-{world:02d}", warm)
        model = NativeInterventionRepair.from_warmup(warm_raw, digest(warm_raw))
        old_bytes = model.checkpoint()
        repair = collect_paired_interventions(env)
        if not (model.prior(repair[0][1], repair[0][2]) != repair[0][3]):
            raise AssertionError("NKR11_PRESET_FIRST_CONTRADICTION_MISSING")
        repair_raw = evidence(f"repair-bundle-world-{world:02d}", repair)
        updated, receipt = model.stage_public_interventions(repair_raw,
                                                            digest(repair_raw))
        if receipt["new_events"] != 16 or not updated.change_detected:
            raise AssertionError("NKR11_ACTUAL_INTERVENTION_NOT_RECORDED")
        if old_bytes != model.checkpoint():
            raise AssertionError("NKR11_OLD_COGNITIVE_MEMORY_CHANGED")
        cold = NativeInterventionRepair(updated.checkpoint(),
                                        updated.checkpoint_sha256)
        if cold.checkpoint() != updated.checkpoint():
            raise AssertionError("NKR11_COLD_REPLAY_DIFFERENT")
        total["contradiction_triggers"] += int(cold.change_detected)
        total["new_full_rank_signatures"] += int(cold.new_rank == FEATURE_COUNT)
        checkpoints.append(cold.checkpoint_sha256)
        # Strong model is independent exhaustive binary-signature fitting and
        # receives exactly the same 16 intervention outcomes as native.
        symbolic_candidates = independent_symbolic_fit(repair)
        if not symbolic_candidates:
            raise AssertionError("NKR11_STRONG_SYMBOLIC_NO_CONSISTENT_SIGNATURE")
        reset_signature = IntegerCausalSignature(repair)
        # Both weaker action policies have the SAME number of observations
        # and train contexts, but may fail to identify causal action effects.
        passive = collect_passive(env)
        random_arm = collect_random(env)
        if not (len(passive) == len(random_arm) == len(repair) == 16):
            raise AssertionError("NKR11_UNEQUAL_INTERVENTION_BUDGET")
        passive_signature = IntegerCausalSignature(passive)
        random_signature = IntegerCausalSignature(random_arm)
        correct_world = 0
        for x in COLD_CONTEXTS:
            for action in (0, 1):
                outcome = env.intervene(x, action)
                predicted = cold.predict(x, action)
                if (predicted["native_accepted"] or predicted["scientific_pass"]
                        or predicted["can_write_causal_owner"]
                        or predicted["can_write_historical_facts"]):
                    raise AssertionError("NKR11_SYNTHETIC_EVIDENCE_PROMOTED")
                native = predicted["public_outcome"]
                conventional = independent_symbolic_predict(
                    symbolic_candidates, x, action)
                if native != conventional or native != reset_signature.predict(x, action):
                    raise AssertionError("NKR11_STRONG_CONTROL_PARITY_FAIL")
                total["native_correct"] += score(native, outcome)
                total["native_coverage"] += int(native is not None)
                total["exact_symbolic_correct"] += score(conventional, outcome)
                total["instant_reset_correct"] += score(
                    reset_signature.predict(x, action), outcome)
                total["passive_correct"] += score(
                    passive_signature.predict(x, action), outcome)
                total["passive_coverage"] += int(
                    passive_signature.predict(x, action) is not None)
                total["random_correct"] += score(
                    random_signature.predict(x, action), outcome)
                total["random_coverage"] += int(
                    random_signature.predict(x, action) is not None)
                total["static_old_correct"] += score(model.prior(x, action), outcome)
                correct_world += score(native, outcome)
        for x in range(16):
            for action in (0, 1):
                old_truth = env.intervene(x, action, old_mechanism=True)
                if cold.prior(x, action) != model.prior(x, action):
                    raise AssertionError("NKR11_COLD_OLD_SIGNATURE_CHANGED")
                total["old_retained_correct"] += score(
                    cold.prior(x, action), old_truth)
        worlds.append({
            "world": world,
            "cold_active_correct": correct_world,
            "repair_integer_rank": cold.new_rank,
            "warm_checkpoint_sha256": model.checkpoint_sha256,
            "repair_checkpoint_sha256": cold.checkpoint_sha256,
            "strong_symbolic_solution_count": len(symbolic_candidates),
            "public_action_observations": len(repair),
        })
    if PublicCausalCells().snapshot() != original_native:
        raise AssertionError("NKR11_LEGACY_YPC1_MUTATED")
    expected_cold = total["cold_queries"]
    expected_retention = total["old_retention_queries"]
    meets = (
        total["native_correct"] >= 173
        and total["native_correct"] - total["passive_correct"] >= 38
        and total["old_retained_correct"] == expected_retention
        and total["contradiction_triggers"] == WORLD_COUNT
        and total["exact_symbolic_correct"] == total["native_correct"]
    )
    return {
        "schema": "yggdrasil.nkr11.intervention-repair-dev-diagnostic.v1",
        "classification": (
            "SYNTHETIC_INTERVENTION_DEV_THRESHOLD_MET" if meets
            else "SYNTHETIC_INTERVENTION_DEV_NO_GO"),
        "source_kind": "deterministic_synthetic_public_actions",
        "source_authenticity": "NOT_AUTHENTIC_EXTERNAL_CAUSAL_EVIDENCE",
        "old_relations_preserved": total["old_retained_correct"] == expected_retention,
        "no_hidden_cold_labels_in_training": True,
        "novel_relation_family": "context_conditional_action_parity_not_initial_unary",
        "hypothesis_class_prespecified": True,
        "source_checkpoint_count": len(checkpoints),
        "sha256_checkpoints": checkpoints,
        "per_world": worlds,
        "totals": total,
        "frozen_development_threshold_met": meets,
        "strong_control_superiority": False,
        "scientific_pass": False,
        "new_authentic_real_world_facts": 0,
        "original_wikidata_source_reopened": False,
        "original_yggdrasil_causal_state_unchanged": True,
        "accepted_main_changed": False,
        "native_accepted": False,
        "elapsed_seconds": time.monotonic() - started,
    }


if __name__ == "__main__":
    print("NKR11_FROZEN_INTERVENTION_DEV=" + json.dumps(
        run_frozen(), separators=(",", ":"), sort_keys=True), flush=True)
