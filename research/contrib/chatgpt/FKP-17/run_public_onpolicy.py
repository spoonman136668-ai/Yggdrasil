"""FKP-17 eight-arm source-safe TRAIN-only on-policy diagnostic.

The only imported simulator is the inspectable public TRAIN fixture. Strictly
NO fresh DEV, reserved TRANSFER, owner-private source, or native promotion.
This result has ZERO inferential weight for original unfamiliar-law science.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import time

import blind_public_harness as blind
import portable_recurrent as portable
import public_policies as direct
import recurrent_control as gru
import source_fixture as fixture
import strong_controls as independent

TRAIN_SAFE_SEED = 978100


def build_and_run_public_training(checkpoint_file, seed=TRAIN_SAFE_SEED):
    if type(seed) is not int or fixture.cohort(seed) != "TRAIN":
        raise PermissionError("FKP17_DIAGNOSTIC_TRAIN_SEED_ONLY")
    start = time.perf_counter()
    facts = tuple(row for _, _, row in fixture.foundation_facts())
    if len(facts) != direct.FOUNDATION_EXPECTED:
        raise ValueError("FKP17_DIAGNOSTIC_INCOMPLETE_FOUNDATION")
    candidates = [direct.PublicRelationArm(name).fit_public_foundation(facts)
                  for name in direct.ARMS]
    common_digest = direct.assert_equal_public_foundation(candidates)
    controls = [independent.SymbolicBayes().fit_public_foundation(facts),
                independent.CountRetrieval().fit_public_foundation(facts)]
    independent.assert_strong_public_information(controls, common_digest)
    recurrent = portable.restore_public_gru(checkpoint_file, common_digest)
    gru.assert_science_ready(recurrent, common_digest)
    policies = {arm.variant: arm for arm in candidates}
    policies.update({"BAYES_SYMBOLIC": controls[0], "COUNT_RETRIEVAL": controls[1],
                     "RECURRENT": recurrent})
    exact_actions = fixture.public_actions(seed, blind.EXPLORATION_STEPS)
    result = blind.evaluate_training_fixture(
        lambda: fixture.PublicSession(seed), exact_actions, policies, seed)
    if set(result["arms"]) != set(blind.ARMS):
        raise AssertionError("FKP17_DIAGNOSTIC_EIGHT_ARMS_INCOMPLETE")
    if any(x["scored_steps"] != 16 for x in result["arms"].values()):
        raise AssertionError("FKP17_DIAGNOSTIC_NOT_16_CONSEQUENTIAL_ACTIONS")
    # Outcome is deliberately training-family diagnostic, not experimental DEV.
    return {
        "schema": "fkp17.public-train-eight-arm-diagnostic.v1",
        "classification": "PUBLIC_TRAIN_DIAGNOSTIC_ONLY_NOT_SCIENCE",
        "source_seed": seed,
        "shared_foundation_sha256": common_digest,
        "shared_exploration_sha256": result["identical_exploration_sha256"],
        "exploration_steps_per_arm": blind.EXPLORATION_STEPS,
        "scored_steps_per_arm": blind.SCORING_STEPS,
        "actual_reward_by_arm": {
            name: result["arms"][name]["actual_public_reward"]
            for name in blind.ARMS
        },
        "committed_actions_by_arm": {
            name: result["arms"][name]["selected_actions"]
            for name in blind.ARMS
        },
        "source_observation_receipt_by_arm": {
            name: result["arms"][name]["chosen_outcome_sha256"]
            for name in blind.ARMS
        },
        "model_state_receipt_by_arm": {
            name: result["arms"][name]["parameter_receipt_after"]
            for name in blind.ARMS
        },
        "elapsed_wall_seconds": time.perf_counter() - start,
        "dev_opened": False, "transfer_opened": False,
        "science_pass": False, "native_promoted": False,
    }


def main():
    arg = argparse.ArgumentParser()
    arg.add_argument("checkpoint_file")
    args = arg.parse_args()
    report = build_and_run_public_training(args.checkpoint_file)
    print("FKP17_PUBLIC_TRAIN_BLIND_DIAGNOSTIC=" +
          json.dumps(report, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
