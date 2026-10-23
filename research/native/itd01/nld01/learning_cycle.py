"""ITD-01 NLD-01: existing R9 smoke-source native learning + retention audit.

Development-only reinspection of the already-public R9 smoke seed 3.
Original R9 source and official first-used seeds are not modified or replayed.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import pathlib
import sys

R9_DIR = pathlib.Path(__file__).resolve().parents[1] / "r9"
sys.path.insert(0, str(R9_DIR))
from action_cells import (  # noqa: E402
    LocalActionColony, PairwisePerceptron, EpisodicActionMemory,
    CurrentOnlyZero, canonical, evaluate, train_equal_public_interventions,
)

SCHEMA = "itd01.nld01.r9-native-dev-learning-retention.v1"
SMOKE_SEED = 3
FIT_PER_FAMILY = 128
EVAL_PER_ROLE = 64
ALL_PATTERNS = tuple(itertools.product((False, True), repeat=4))


def parameter_hash(native):
    """Ignore non-learning inference instrumentation counters."""
    return hashlib.sha256(canonical({
        "family_cells": {
            f: [(c.fast, c.slow, c.public_updates) for c in native.cells[f]]
            for f in ("A", "B", "C")
        },
        "bias": native.bias,
        "feedback_updates": native.feedback_updates,
        "weight_changes": native.weight_changes,
    })).hexdigest()


def cold_restart_and_decisions(native):
    """Exact SHA-authenticated restore and all-16-pattern decision equivalence."""
    original = native.save()
    restored = LocalActionColony.restore(original)
    if restored.save() != original:
        raise AssertionError("NLD01_COLD_RESTORE_BYTES")
    decisions = {}
    for family in ("A", "B"):
        before = tuple(native.choose(family, sensors) for sensors in ALL_PATTERNS)
        after = tuple(restored.choose(family, sensors) for sensors in ALL_PATTERNS)
        if before != after or not set(before).issubset({0, 1}):
            raise AssertionError("NLD01_COLD_DECISIONS_DIFFER")
        decisions[family] = before
    if restored.save() != native.save():
        raise AssertionError("NLD01_COLD_INFERENCE_COUNTERS_DIFFER")
    return {"checkpoint_sha256": hashlib.sha256(original).hexdigest(),
            "checkpoint_bytes": len(original),
            "matching_public_decisions": len(ALL_PATTERNS) * 2,
            "cold_restore_exact": True,
            "decision_digest": hashlib.sha256(canonical(decisions)).hexdigest()}


def paired_state_ablation(native):
    """Legality-preserving inference-only reset, without training or source use."""
    trained = LocalActionColony.restore(native.save())
    reset = LocalActionColony()
    return {
        family: sum(trained.choose(family, s) != reset.choose(family, s)
                    for s in ALL_PATTERNS)
        for family in ("A", "B")
    }


def smoke_cycle(seed=SMOKE_SEED):
    if type(seed) is not int or seed != SMOKE_SEED:
        raise ValueError("NLD01_ONLY_EXISTING_PUBLIC_R9_SMOKE_SEED_3")
    native = LocalActionColony()
    pair = PairwisePerceptron()
    episodic = EpisodicActionMemory()
    agents = [native, pair, episodic]
    comparison = agents + [CurrentOnlyZero()]
    untouched = parameter_hash(native)
    a_pre = evaluate(comparison, seed, "VALID_A_PRE", "A", EVAL_PER_ROLE)
    assert parameter_hash(native) == untouched, "NLD01_PREFIT_EVAL_MUTATED"
    fit_a = train_equal_public_interventions(agents, seed, "FIT_A", "A", FIT_PER_FAMILY)
    if any(a.feedback_updates != FIT_PER_FAMILY for a in agents):
        raise AssertionError("NLD01_FIT_A_INFO_PARITY")
    after_a = cold_restart_and_decisions(native)
    after_a_hash = parameter_hash(native)
    a_post = evaluate(comparison, seed, "VALID_A_POST", "A", EVAL_PER_ROLE)
    if parameter_hash(native) != after_a_hash:
        raise AssertionError("NLD01_A_POST_EVAL_UPDATED_MODEL")
    fit_b = train_equal_public_interventions(agents, seed, "FIT_B", "B", FIT_PER_FAMILY)
    if any(a.feedback_updates != FIT_PER_FAMILY * 2 for a in agents):
        raise AssertionError("NLD01_FIT_B_INFO_PARITY")
    after_b = cold_restart_and_decisions(native)
    after_b_hash = parameter_hash(native)
    a_retained = evaluate(comparison, seed, "DEV_A_RETAINED", "A", EVAL_PER_ROLE)
    b_post = evaluate(comparison, seed, "VALID_B", "B", EVAL_PER_ROLE)
    if parameter_hash(native) != after_b_hash:
        raise AssertionError("NLD01_RETENTION_EVAL_UPDATED_MODEL")
    disagreements = paired_state_ablation(native)
    native_name = native.name
    role = {"a_untrained": a_pre, "a_trained": a_post,
            "a_after_b": a_retained, "b_trained": b_post}
    score = {name: {
        "native_accuracy": item["success"][native_name],
        "pairwise_accuracy": item["success"][pair.name],
        "episodic_accuracy": item["success"][episodic.name],
        "current_only_accuracy": item["success"]["untrained-current-only-zero"],
        "erased_native_accuracy": item["native_erased_state_success"],
        "no_neighbor_native_accuracy": item["native_no_neighbor_success"],
        "native_neighbor_action_disagreement": item["native_neighbor_action_disagreement"],
        "all_actions_legal": item["all_actions_legal"],
        "feedback_parameter_updates": item["eval_parameter_updates"],
        "evaluation_role_sha256": item["public_observation_seed_sha256"],
        "evaluation_episodes": item["n"],
    } for name, item in role.items()}
    learned_gain = score["a_trained"]["native_accuracy"] - score["a_untrained"]["native_accuracy"]
    retention_gain = (score["a_after_b"]["native_accuracy"] -
                      score["a_after_b"]["erased_native_accuracy"])
    policy_changes = disagreements["A"] + disagreements["B"]
    pass_smoke = (native.weight_changes > 0 and
                  learned_gain > 0 and retention_gain > 0 and
                  policy_changes > 0 and
                  score["a_after_b"]["native_accuracy"] >=
                  score["a_trained"]["native_accuracy"] and
                  all(x["all_actions_legal"] and x["feedback_parameter_updates"] == 0
                      for x in score.values()))
    return {
        "schema": SCHEMA, "source_parent_r9_sha":
            "b60453d7a5100eea037dfb77b3660783139d11dd",
        "public_smoke_seed": seed,
        "role_reuse": "EXISTING_R9_SMOKE_DEVELOPMENT_ONLY_NOT_FRESH_FIRST_USE",
        "fit_per_public_family": FIT_PER_FAMILY,
        "eval_per_public_role": EVAL_PER_ROLE,
        "fit_public_traces": [fit_a, fit_b],
        "fitted_arms_equal_public_delayed_feedback": True,
        "fitted_arm_update_counts": {a.name: a.feedback_updates for a in agents},
        "native_weight_changes": native.weight_changes,
        "native_state_changed_vs_initial": after_a_hash != untouched,
        "native_state_changed_during_b_fit": after_b_hash != after_a_hash,
        "cold_after_a": after_a,
        "cold_after_b": after_b,
        "checkpoint_bytes": {a.name: len(a.save()) for a in agents},
        "state_ablation_disagreements_across_16_patterns": disagreements,
        "role_scores": score,
        "observed_native_gain_a_after_public_fit": learned_gain,
        "observed_native_retention_benefit_vs_erased_a": retention_gain,
        "observed_native_a_retention_after_b": score["a_after_b"]["native_accuracy"],
        "narrow_sourcefree_native_smoke_pass": bool(pass_smoke),
        "representation": "SMOKE_DECISION_RELEVANT_STATE" if learned_gain > 0 and policy_changes > 0 else "NOT_SHOWN",
        "retention": "SMOKE_A_RETAINED_AFTER_B" if retention_gain > 0 and score["a_after_b"]["native_accuracy"] >= score["a_trained"]["native_accuracy"] else "NOT_SHOWN",
        "causal_composition": "NOT_TESTED_KNOWN_FAMILY_ID_AND_PAIR_FEATURES",
        "unfamiliar_transfer": "NOT_TESTED_ORIGINAL_R9_ZERO_SHOT_NO_GO",
        "native_better_than_trained_conventional_baselines": "NOT_CLAIMED",
        "isolated_per_model_cpu_rss_parity": False,
        "independent_source_first_use": False,
        "original_r9_seeds_101_211_307_replayed": False,
        "original_H1_H2_accessed": False,
        "ckb_admission": "NOT_OBSERVED",
        "disposition": "NLD01_NATIVE_SMOKE_POSITIVE_NARROW" if pass_smoke
                       else "NLD01_NATIVE_SMOKE_NO_GO_RETAIN_NEGATIVE",
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true", required=True)
    p.parse_args()
    print(json.dumps(smoke_cycle(), sort_keys=True, separators=(",", ":"),
                     allow_nan=False))
