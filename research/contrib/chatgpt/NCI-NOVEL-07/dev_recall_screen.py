"""Exposed 72-witness engineering sanity screen, not prospective science.

This is exactly the same hand-authored test fixture as test_aba_recall.py;
there is NO untouched held set or independent source-world first use. Scorer
knows fabricated A/B/A positions but never exposes them to model methods.
"""
from __future__ import annotations

from hashlib import sha256
import json

from aba_recall import (BoundedCausalRecall, ExactGridSwitchBayes,
                        EpisodicTwoWindowControl, WindowBetaControl)
from protocol_guard import assert_paired_evidence, assert_cold_functional_retention
from test_aba_recall import A, B


def evaluate():
    arms = {
        "candidate": BoundedCausalRecall(),
        "grid_hmm": ExactGridSwitchBayes(),
        "episodic": EpisodicTwoWindowControl(),
        "window8": WindowBetaControl(window=8),
        "full_history": WindowBetaControl(),
    }
    sections = (("A_initial", A), ("B_interference", B), ("A_return", A))
    scores = {name: {} for name in arms}
    tapes = {name: [] for name in arms}
    old = None
    cold_bytes = None
    pre_return_drift = None
    for label, rows in sections:
        for name, model in arms.items():
            brier = 0.0
            policy_rewards = 0
            abstentions = 0
            for witness in rows:
                q = model.predict(witness["action"], witness["observation"])
                brier += (q - witness["outcome"]) ** 2
                choice = model.choose(witness["observation"])
                abstentions += (choice is None)
                # Evaluator-only deterministic potential outcomes: a=0 correct
                # in A, a=1 correct in B. Not sent to any learner.
                policy_rewards += int(choice is not None and
                                      choice == (1 if label == "B_interference" else 0))
                model.observe(dict(witness))
                tapes[name].append(dict(witness))
            scores[name][label] = {"prequential_brier": round(brier / len(rows), 12),
                                   "correct_policy_decisions": policy_rewards,
                                   "abstentions": abstentions,
                                   "opportunities": len(rows)}
        if label == "A_initial":
            candidate = arms["candidate"]
            old = {a: candidate.retained_predict(0, a) for a in (0, 1)}
        elif label == "B_interference":
            candidate = arms["candidate"]
            cold_bytes = len(candidate.snapshot())
            arms["candidate"] = BoundedCausalRecall.restore(candidate.snapshot())
            pre_return_drift = assert_cold_functional_retention(
                old, {a: arms["candidate"].retained_predict(0, a) for a in (0, 1)},
                tolerance=0.0)
    candidate = arms["candidate"]
    return {
        "schema": "yggdrasil.nci07.exposed-development-screen.v1",
        "classification": "EXPOSED_DEV_ENGINEERING_ONLY_NOT_SCIENCE",
        "source_world_first_use": False,
        "tape_proof": assert_paired_evidence(tapes, tuple(arms), max_witnesses=72),
        "scores": scores,
        "candidate_pre_return_cold_A_forecast_drift": pre_return_drift,
        "candidate_cold_checkpoint_bytes_after_B": cold_bytes,
        "candidate_cold_restore_before_A_return": True,
        "candidate_switch_count": candidate.transitions,
        "candidate_final_active_slot": candidate.active,
        "controls_are_fully_trained_general_world_models": False,
        "scientific_gain_verified": False,
    }


def main():
    first, second = evaluate(), evaluate()
    if first != second:
        raise RuntimeError("NCI07_DEV_DIAGNOSTIC_NONDETERMINISTIC")
    payload = json.dumps(first, sort_keys=True, separators=(",", ":"), allow_nan=False)
    print("NCI07_DEV_SCREEN_SHA256=" + sha256(payload.encode("ascii")).hexdigest())
    print("NCI07_DEV_SCREEN=" + payload)
    print("NCI07_EXPOSED_DEV_INTEGRITY_PASS")


if __name__ == "__main__":
    main()
