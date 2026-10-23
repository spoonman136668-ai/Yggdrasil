"""NLD04: infer previously learned context solely from public delayed probe outcomes.

Reuses already exposed R9 seed-3 DEV source. The scorer alone knows task A/B.
No new protected first-use, learned causal abstraction, or unfamiliar transfer.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "nld03"))
from cued_state import (CueNative, CuePerceptron, CueEpisodic, CUE, SEED,
                        FIT, EVAL, PATTERNS, train_public, checkpoint,
                        PublicSource, source_only_correct_action, digest)
from action_cells import DELAY, check_action, canonical

PROBES = 8
SCORED = EVAL - PROBES
SCHEMA = "itd01.nld04.public-delayed-history-context-dev.v1"


def infer_from_public_history(model, transcript):
    """Fixed two-hypothesis mismatch filter; no task ID, role or source object."""
    if len(transcript) != PROBES:
        raise ValueError("NLD04_EXACT_EIGHT_COMPLETED_PROBES_REQUIRED")
    mistakes = {-1: 0, 1: 0}
    informative = 0
    seen = set()
    for r in transcript:
        if set(r) != {"token", "sensors", "action", "success",
                      "action_tick", "feedback_tick"}:
            raise ValueError("NLD04_PUBLIC_TRANSCRIPT_SHAPE")
        if r["token"] in seen or r["feedback_tick"] - r["action_tick"] != DELAY:
            raise ValueError("NLD04_PUBLIC_TOKEN_OR_DELAY_INVALID")
        seen.add(r["token"])
        action, outcome = r["action"], r["success"]
        check_action(action)
        if type(outcome) is not bool:
            raise ValueError("NLD04_SUCCESS_MUST_BE_PUBLIC_BOOLEAN")
        correct = action if outcome else 1-action
        a = model.choose(tuple(r["sensors"]), -1)
        b = model.choose(tuple(r["sensors"]), 1)
        informative += int(a != b)
        mistakes[-1] += int(a != correct)
        mistakes[1] += int(b != correct)
    best = -1 if mistakes[-1] <= mistakes[1] else 1
    return {"chosen_public_context": best,
            "mismatch_scores_A_B": [mistakes[-1], mistakes[1]],
            "diagnostic_disagreements": informative,
            "ambiguous_tie": mistakes[-1] == mistakes[1],
            "diagnostic_delayed_outcomes": len(transcript)}


def evaluate_without_context(arms, family, role):
    """Private evaluator generates source consequences; selector sees public logs only."""
    if (family, role) not in (("A", "DEV_A_RETAINED"), ("B", "VALID_B")):
        raise ValueError("NLD04_UNAUTHORIZED_ROLE")
    generator = PublicSource(SEED, role, family)
    saved = {a.name: a.save() for a in arms}
    transcript, queue = [], {}
    for tick in range(PROBES + DELAY):
        for record in queue.pop(tick, []):
            if record["feedback_tick"] != tick:
                raise AssertionError("NLD04_CAUSAL_FEEDBACK_CLOCK")
            transcript.append(record)
        if tick >= PROBES:
            continue  # Flush delayed feedback without generating extra observations.
        sensors = generator.next_sensors()
        action = (sum(sensors) + tick) % 2
        check_action(action)
        success = bool(action == source_only_correct_action(family, sensors))
        token = f"NLD04-PUBLIC-{SEED}-{role}-{tick}"
        queue.setdefault(tick + DELAY, []).append({
            "token": token, "sensors": list(sensors), "action": action,
            "success": success, "action_tick": tick,
            "feedback_tick": tick + DELAY,
        })
    if queue or len(transcript) != PROBES or generator.calls != PROBES:
        raise AssertionError("NLD04_PROBE_DRAIN_FAILED")

    hypotheses = {a.name: infer_from_public_history(a, transcript) for a in arms}
    counts = {a.name: 0 for a in arms}
    counts["supplied_context_native_ORACLE"] = 0
    counts["erased_context_native"] = 0
    counts["always_A_context_native"] = 0
    blank = CueNative(True)
    oracle_native = next(a for a in arms if a.name == "native-shared-public-cue")
    for _ in range(SCORED):
        sensors = generator.next_sensors()
        truth = source_only_correct_action(family, sensors)
        for arm in arms:
            predicted = arm.choose(sensors, hypotheses[arm.name]["chosen_public_context"])
            check_action(predicted)
            counts[arm.name] += int(predicted == truth)
        oracle = oracle_native.choose(sensors, CUE[family])
        counts["supplied_context_native_ORACLE"] += int(oracle == truth)
        counts["erased_context_native"] += int(blank.choose(sensors, -1) == truth)
        counts["always_A_context_native"] += int(oracle_native.choose(sensors, -1) == truth)
    if generator.calls != EVAL or any(a.save() != saved[a.name] for a in arms):
        raise AssertionError("NLD04_SCORE_MUTATED_TRAINED_STATE")
    return {
        "source_role_for_private_audit_only": role,
        "source_family_for_private_audit_only": family,
        "public_role_steps": EVAL,
        "unscored_public_probe_cost": PROBES,
        "public_feedback_delay": DELAY,
        "scored_steps": SCORED,
        "probe_public_history_sha256": digest(transcript),
        "context_selection": hypotheses,
        "selection_correctness_evaluator_only": {
            a.name: hypotheses[a.name]["chosen_public_context"] == CUE[family]
            for a in arms},
        "correct_counts_over_56": counts,
        "native_accuracy_inferred_context": counts["native-shared-public-cue"] / SCORED,
        "native_accuracy_supplied_cue_oracle": counts["supplied_context_native_ORACLE"] / SCORED,
        "native_accuracy_blind": counts["native-shared-cue-blind"] / SCORED,
        "score_updates": 0,
    }


def run(seed=SEED):
    if type(seed) is not int or seed != SEED:
        raise ValueError("NLD04_ONLY_PREVIOUSLY_EXPOSED_R9_SMOKE_3")
    models = [CueNative(True), CueNative(False), CuePerceptron(True),
              CuePerceptron(False), CueEpisodic(True), CueEpisodic(False)]
    fa = train_public(models, "A")
    fb = train_public(models, "B")
    if any(m.feedback_updates != 2 * FIT for m in models):
        raise AssertionError("NLD04_TRAINED_ARM_PUBLIC_FEEDBACK_PARITY")
    checkpoint_native = checkpoint(models[0])
    a = evaluate_without_context(models, "A", "DEV_A_RETAINED")
    b = evaluate_without_context(models, "B", "VALID_B")
    return {
        "schema": SCHEMA,
        "parent_nld03_source_sha": "940662119e063eddc49fe6a5f78da399ba8f356b",
        "source_first_use": "REUSED_ALREADY_PUBLIC_R9_DEVELOPMENT_SEED_3",
        "protected_first_use_consumed": False,
        "original_r9_101_211_307_replayed": False,
        "source_episode_count_per_family": EVAL,
        "public_probe_count_per_family": PROBES,
        "scored_steps_per_family": SCORED,
        "fit_source_trace_receipts": [fa, fb],
        "equal_public_delayed_fit_feedback": {m.name: m.feedback_updates for m in models},
        "trained_model_checkpoint_bytes": {m.name: len(m.save()) for m in models},
        "native_cold_restart": checkpoint_native,
        "eval_a": a,
        "eval_b": b,
        "unfamiliar_transfer": "NOT_TESTED_ORIGINAL_R9_C_NEGATIVE_PRESERVED",
        "causal_composition": "NOT_TESTED_TWO_PREDECLARED_TASK_HYPOTHESES",
        "context_mechanism": "INTEGER_MISMATCH_SELECTOR_USING_FROZEN_LEARNED_CONTEXT_POLICIES",
        "learned_context_representation": False,
        "new_family_generation": False,
        "per_model_cpu_rss_parity": False,
        "ckb_scientific_admission": "NOT_OBSERVED",
        "disposition": "NLD04_PUBLIC_HISTORY_DEV_OBSERVATION_RETAIN_POSITIVE_AND_NEGATIVE",
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", required=True)
    ap.parse_args()
    print(json.dumps(run(), sort_keys=True, separators=(",", ":"), allow_nan=False))
