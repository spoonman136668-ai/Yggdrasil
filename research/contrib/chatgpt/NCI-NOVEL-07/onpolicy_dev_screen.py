"""NCI07-ONPOLICY-DEV01 frozen source-free DEV falsifier; NOT SCIENCE.

See onpolicy-dev-freeze.md at prereg-first commit 56a4bd3c5a7ceb...
These worlds are developer-exposed after evaluation. No original-world seed,
source label, phase, outcome probability or counterfactual reaches the learner.
"""
from __future__ import annotations

import hashlib
import json
import math

from aba_recall import (BoundedCausalRecall, ExactGridSwitchBayes,
                        EpisodicTwoWindowControl, WindowBetaControl)
from protocol_guard import canonical_public_tape, AuditError

TOTAL_STEPS = 384
PHASE_STEPS = 128
PROBE_MODULUS = 16
COLD_STEP = 200
OBSERVATION = 7
PREFIX = b"NCI07-ONPOLICY-DEV01:"
CASES = {
    "REV94": ((.94, .06), (.06, .94), (.94, .06)),
    "REV80": ((.80, .20), (.20, .80), (.80, .20)),
    "STATIONARY": ((.94, .06), (.94, .06), (.94, .06)),
    "NEUTRAL_THIRD": ((.94, .06), (.50, .50), (.94, .06)),
    "UNIDENTIFIABLE_ACTION0": ((.50, .90), (.50, .10), (.50, .90)),
}
ARM_NAMES = ("candidate", "grid_hmm", "episodic", "window8", "full_history")
PHASE_NAMES = ("first", "middle", "return")


def probability(world, step, action):
    if world not in CASES or type(step) is not int or not 0 <= step < TOTAL_STEPS:
        raise AuditError("NCI07_ONPOLICY_WORLD_OR_TIME_INVALID")
    if type(action) is not int or action not in (0, 1):
        raise AuditError("NCI07_ONPOLICY_ACTION_INVALID")
    return CASES[world][step // PHASE_STEPS][action]


def consequence(world, step, action):
    """Evaluator-only potential outcome; caller must pass executed action."""
    p = probability(world, step, action)
    key = PREFIX + world.encode("ascii") + b":" + str(step).encode("ascii") + b":" + str(action).encode("ascii")
    shock = int.from_bytes(hashlib.sha256(key).digest()[:4], "big") / 2**32
    return int(shock < p)


def eligible_action(model, step, world):
    if world == "UNIDENTIFIABLE_ACTION0":
        return 0, "forced-unidentifiable"
    if step % PROBE_MODULUS in (0, 1):
        return step % PROBE_MODULUS, "fixed-probe"
    suggestion = model.choose(OBSERVATION)
    if suggestion is None:
        return 0, "abstention-fallback"
    if type(suggestion) is not int or suggestion not in (0, 1):
        raise AuditError("NCI07_ONPOLICY_SUGGESTION_INVALID")
    return suggestion, "policy"


def expected_brier(p, forecast):
    return p * (1.0 - forecast) ** 2 + (1.0 - p) * forecast ** 2


def new_arms():
    return {
        "candidate": BoundedCausalRecall(),
        "grid_hmm": ExactGridSwitchBayes(),
        "episodic": EpisodicTwoWindowControl(),
        "window8": WindowBetaControl(window=8),
        "full_history": WindowBetaControl(),
    }


def blank_stats():
    return dict(steps=0, realized_reward=0, expected_reward=0.0,
                expected_regret=0.0, onpolicy_brier=0.0,
                two_action_expected_brier=0.0, probes=0, fallbacks=0)


def finalize(x):
    n = x["steps"]
    if n == 0:
        raise AuditError("NCI07_ONPOLICY_EMPTY_PHASE")
    return {
        "steps": n,
        "realized_reward": x["realized_reward"],
        "realized_reward_rate": round(x["realized_reward"] / n, 9),
        "expected_reward_rate": round(x["expected_reward"] / n, 9),
        "expected_regret_per_step": round(x["expected_regret"] / n, 9),
        "prequential_chosen_action_brier": round(x["onpolicy_brier"] / n, 9),
        "comparable_two_action_expected_brier": round(x["two_action_expected_brier"] / n, 9),
        "probes": x["probes"], "fallbacks": x["fallbacks"]
    }


def one_world(world):
    models = new_arms()
    totals = {name: blank_stats() for name in models}
    phases = {name: [blank_stats() for _ in range(3)] for name in models}
    tapes = {name: [] for name in models}
    first_a = None
    post_interference = None
    cold_roundtrip_drift = None
    cold_bytes = None
    return_detection_delay = None
    last_middle_slot = None
    for t in range(TOTAL_STEPS):
        phase_id = t // PHASE_STEPS  # evaluator-only, never given to a model
        for name in ARM_NAMES:
            model = models[name]
            if name == "candidate":
                if t == PHASE_STEPS:
                    first_a = {a: model.retained_predict(0, a) for a in (0, 1)}
                if t == COLD_STEP:
                    post_interference = {a: model.retained_predict(0, a) for a in (0, 1)}
                    cp = model.snapshot()
                    cold_bytes = len(cp)
                    models[name] = model = BoundedCausalRecall.restore(cp)
                    cold_roundtrip_drift = max(
                        abs(model.retained_predict(0, a) - post_interference[a]) for a in (0, 1))
                    if cp != model.snapshot():
                        raise AuditError("NCI07_ONPOLICY_COLD_CHECKPOINT_DRIFT")
                if t == 2 * PHASE_STEPS:
                    last_middle_slot = model.active
            forecasts = (model.predict(0, OBSERVATION), model.predict(1, OBSERVATION))
            if any(type(q) not in (int, float) or not math.isfinite(q) or not 0 <= q <= 1
                   for q in forecasts):
                raise AuditError("NCI07_ONPOLICY_PREDICTION_INVALID")
            action, reason = eligible_action(model, t, world)
            p0, p1 = probability(world, t, 0), probability(world, t, 1)
            observed = consequence(world, t, action)
            witnessed = {"observation": OBSERVATION, "action": action, "outcome": observed}
            canonical_public_tape([witnessed])
            model.observe(witnessed)
            tapes[name].append((action, observed))
            for dest in (totals[name], phases[name][phase_id]):
                dest["steps"] += 1
                dest["realized_reward"] += observed
                dest["expected_reward"] += (p0, p1)[action]
                dest["expected_regret"] += max(p0, p1) - (p0, p1)[action]
                dest["onpolicy_brier"] += (forecasts[action] - observed) ** 2
                dest["two_action_expected_brier"] += (
                    expected_brier(p0, forecasts[0]) + expected_brier(p1, forecasts[1])) / 2
                dest["probes"] += reason == "fixed-probe"
                dest["fallbacks"] += reason == "abstention-fallback"
            if name == "candidate" and t >= 2 * PHASE_STEPS and last_middle_slot == 1:
                if return_detection_delay is None and model.active == 0:
                    return_detection_delay = t - 2 * PHASE_STEPS + 1
    if first_a is None or post_interference is None or cold_bytes is None or cold_roundtrip_drift != 0:
        raise AuditError("NCI07_ONPOLICY_COLD_INTEGRITY_FAIL")
    if set(tapes) != set(ARM_NAMES) or any(len(tape) != TOTAL_STEPS for tape in tapes.values()):
        raise AuditError("NCI07_ONPOLICY_ACTION_BUDGET_MISMATCH")
    # Public traces differ with policy. No fraudulent equal-tape assertion.
    digests = {
        name: hashlib.sha256(json.dumps(tapes[name], separators=(",", ":")).encode("ascii")).hexdigest()
        for name in ARM_NAMES}
    candidate = models["candidate"]
    results = {name: {"all": finalize(totals[name]),
                      "phases": {label: finalize(phases[name][i])
                                 for i, label in enumerate(PHASE_NAMES)}}
               for name in ARM_NAMES}
    return {
        "models": results,
        "own_witness_tape_sha256": digests,
        "candidate": {
            "slot_count": len(candidate.slots), "transitions": candidate.transitions,
            "final_active_slot": candidate.active, "slot_before_return": last_middle_slot,
            "first_return_detection_delay": return_detection_delay,
            "old_A_forecast_drift_after_B_before_cold": round(max(
                abs(first_a[a] - post_interference[a]) for a in (0, 1)), 9),
            "snapshot_restore_forecast_drift": cold_roundtrip_drift,
            "checkpoint_bytes": cold_bytes,
        },
        "fixed_opportunities": TOTAL_STEPS,
        "public_tapes_identical": len(set(digests.values())) == 1,
        "source_id_given_to_model": False,
    }


def evaluate():
    worlds = {world: one_world(world) for world in CASES}
    comparisons = {}
    directional_go = True
    for world in ("REV94", "REV80"):
        arms = worlds[world]["models"]
        a = arms["candidate"]["all"]
        best_brier = min(arms[name]["all"]["comparable_two_action_expected_brier"]
                         for name in ARM_NAMES if name != "candidate")
        best_reward = max(arms[name]["all"]["expected_reward_rate"]
                          for name in ARM_NAMES if name != "candidate")
        qualifies = (a["comparable_two_action_expected_brier"] <= .95 * best_brier
                     and a["expected_reward_rate"] >= best_reward + .02)
        directional_go &= qualifies
        comparisons[world] = {
            "candidate_two_action_expected_brier": a["comparable_two_action_expected_brier"],
            "best_non_oracle_two_action_expected_brier": best_brier,
            "candidate_expected_reward_rate": a["expected_reward_rate"],
            "best_non_oracle_expected_reward_rate": best_reward,
            "both_frozen_dev_thresholds_pass": qualifies,
        }
    directional_go &= worlds["STATIONARY"]["candidate"]["transitions"] == 0
    if any(world["candidate"]["snapshot_restore_forecast_drift"] != 0 for world in worlds.values()):
        raise AuditError("NCI07_ONPOLICY_COLD_INTEGRITY_FAIL")
    return {
        "schema": "yggdrasil.nci07.onpolicy-source-free-dev.v1",
        "classification": ("DEV_DIRECTIONAL_GO_TO_FRESH_SOURCE_DESIGN_ONLY" if directional_go
                           else "DEV_NEGATIVE_NO_PAIRED_GAIN"),
        "scientific_gain_verified": False,
        "native_model_updated": False,
        "original_world_first_use": False,
        "fully_fitted_general_world_baselines": False,
        "worlds": worlds,
        "frozen_dev_comparisons": comparisons,
        "learner_action_opportunities": len(CASES) * len(ARM_NAMES) * TOTAL_STEPS,
        "distinct_evaluator_only_worlds": list(CASES),
        "all_dev_worlds_now_exposed": True,
    }


def main():
    first = evaluate()
    second = evaluate()  # development-only deterministic reexecution, never fresh science
    if first != second:
        raise RuntimeError("NCI07_ONPOLICY_REPLAY_NONDETERMINISTIC")
    payload = json.dumps(first, sort_keys=True, separators=(",", ":"), allow_nan=False)
    print("NCI07_ONPOLICY_DEV_SHA256=" + hashlib.sha256(payload.encode("ascii")).hexdigest())
    print("NCI07_ONPOLICY_DEV_RESULT=" + payload)
    print("NCI07_ONPOLICY_SOURCE_FREE_DEV_COMPLETE")


if __name__ == "__main__":
    main()
