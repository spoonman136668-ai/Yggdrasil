"""Gate28 independent *diagnostic* score audit: never a scientific result.

Consumes evaluator summaries, not hidden worlds or learners. It rejects
missing cohorts, reserved seeds, missing arms, impossible metrics, and budget
mislabeling; it deliberately does NOT authorize a primary first-use, infer a
paired confidence interval from one diagnostic world, or select a winning
architecture. Its three diagnostic worlds provide falsification cues only.
"""
from __future__ import annotations

import math
import re

SCHEMA = "yggdrasil.gate28.diagnostic-score-audit.v1"
COHORTS = ("diagnostic_shifted", "stationary", "independent_noise")
ARMS = ("adaptive", "fixed", "causal_bayes_reward",
        "sparse_causal_reward", "dense_causal_reward", "dense_causal_nullmix",
        "full_reference_reward")
MATCHED_CONTROLS = ("fixed", "causal_bayes_reward",
                    "sparse_causal_reward", "dense_causal_reward",
                    "dense_causal_nullmix")
REFERENCE = "full_reference_reward"
RULE_CAP = 8192
CHECKPOINT_CAP = 16384
NOISE_CHANCE_BRIER = 0.25
NOISE_EXCESS_THRESHOLD = 0.02


def _require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError("G28_AUDIT_FAIL_CLOSED:" + reason)


def _real(value: object, name: str, low: float, high: float) -> float:
    _require(type(value) in (int, float), name + "_TYPE")
    val = float(value)
    _require(math.isfinite(val) and low <= val <= high, name + "_RANGE")
    return val


def _receipt(record: dict) -> None:
    _require(type(record) is dict, "RECORD_TYPE")
    _require(record.get("status") ==
             "G28_EQUAL_EXPOSURE_CONTROL_DIAGNOSTIC_ONLY", "RECORD_KIND")
    _require(record.get("scientific_primary_scored") is False and
             record.get("original_world_first_use") is False and
             record.get("independent_reproduction") is False,
             "PRIMARY_OR_REPRODUCTION_FLAG")
    _require(record.get("full_reference_is_unconstrained") is True and
             record.get("strongest_matched_control_adequacy") == "UNVERIFIED",
             "UNQUALIFIED_CONTROL_MISREPRESENTED")
    _require(type(record.get("seed")) is int and
             900000 <= record["seed"] <= 909999, "RESERVED_SEED")
    _require(record.get("cohort") in COHORTS, "INVALID_COHORT")
    _require(type(record.get("models")) is list and
             tuple(record["models"]) == ARMS, "MISSING_OR_EXTRA_ARMS")
    p = record.get("phases")
    _require(type(p) is dict and set(p) == {"A", "B", "R"},
             "MISSING_PHASE")
    for phase, length in (("A", 96), ("B", 64), ("R", 64)):
        obs = p[phase]
        _require(type(obs) is dict and
                 obs.get("public_exposures") == length, "EXPOSURE_COUNT")
        _require(type(obs.get("public_exposure_sha256")) is str and
                 re.fullmatch("[0-9a-f]{64}",
                              obs["public_exposure_sha256"]) is not None,
                 "EXPOSURE_DIGEST")
        if phase == "A":
            continue
        scores = obs.get("scores")
        _require(type(scores) is dict and set(scores) == set(ARMS),
                 "ARM_SCORE_SET")
        full_brier = _real(scores[REFERENCE].get("equal_action_held_brier"),
                           "FULL_HELD_BRIER", 0, 1)
        for arm in ARMS:
            item = scores[arm]
            _require(type(item) is dict, "ARM_SCORE_TYPE")
            held = _real(item.get("equal_action_held_brier"),
                         "HELD_BRIER", 0, 1)
            _real(item.get("prequential_brier"), "PREQUENTIAL", 0, 1)
            _real(item.get("cpu_ms_accumulated"), "CPU_MS", 0, 1e12)
            _require(type(item.get("selected_held_reward")) is int and
                     0 <= item["selected_held_reward"] <= 32,
                     "HELD_REWARD")
            bytes_ = item.get("checkpoint_bytes")
            work = item.get("peak_rule_work")
            _require(type(bytes_) is int and 0 < bytes_ <= 100000000,
                     "CHECKPOINT_BYTES")
            _require(type(work) is int and 0 <= work <= 100000000,
                     "RULE_EVALUATIONS")
            _require(abs(_real(item.get("delta_brier_vs_full"),
                               "DELTA_SIGN", -1, 1) -
                         (full_brier - held)) <= 2.1e-9,
                     "DELTA_BRIER_ARITHMETIC")
            if arm == REFERENCE:
                _require(bytes_ > CHECKPOINT_CAP and
                         work > RULE_CAP, "UNCONSTRAINED_REFERENCE_FALSE")
            else:
                _require(bytes_ <= CHECKPOINT_CAP and
                         work <= RULE_CAP, "MATCHED_BUDGET_VIOLATION")


def audit(records: list[dict]) -> dict:
    """Reject false positive scientific interpretations of 3 diagnostic worlds."""
    _require(type(records) is list and len(records) == 3,
             "COHORT_COMPLETENESS")
    for record in records:
        _receipt(record)
    by_cohort = {r["cohort"]: r for r in records}
    _require(set(by_cohort) == set(COHORTS), "COHORT_DUPLICATION")
    _require(len({r["seed"] for r in records}) == 3, "REUSED_WORLD_SEED")
    # Record diagnostic descriptive differences only, NOT a winner chosen
    # after looking at primary scores or an independently qualified control.
    shifted = by_cohort["diagnostic_shifted"]
    differences = {}
    for phase in ("B", "R"):
        scores = shifted["phases"][phase]["scores"]
        best = min(MATCHED_CONTROLS,
                   key=lambda arm: (scores[arm]["equal_action_held_brier"], arm))
        differences[phase] = {
            "descriptive_best_matched_control": best,
            "adaptive_minus_best_control_brier": round(
                scores["adaptive"]["equal_action_held_brier"] -
                scores[best]["equal_action_held_brier"], 9),
            "no_pairwise_CI_one_diagnostic_world": True}
    noise = by_cohort["independent_noise"]["phases"]["R"]["scores"]
    excess = {arm: round(noise[arm]["equal_action_held_brier"] -
                         NOISE_CHANCE_BRIER, 9) for arm in ARMS}
    alerts = [arm for arm in ARMS if excess[arm] > NOISE_EXCESS_THRESHOLD]
    return {
        "schema": SCHEMA,
        "status": "G28_DIAGNOSTIC_AUDIT_COMPLETE_SCIENCE_UNVERIFIED",
        "cohorts": list(COHORTS), "seed_count": 3,
        "primary_seeds_consumed": False, "scientific_gain_verified": False,
        "matched_control_adequacy": "UNVERIFIED",
        "strongest_control_qualification": "NOT_ESTABLISHED",
        "source_cold_function_for_all_arms": "NOT_PROVEN_BY_THIS_AUDIT",
        "per_arm_forced_exposure_hash_parity": "NOT_PROVEN_BY_THIS_AUDIT",
        "stationary_spurious_rewire_fraction": "NOT_REPORTED_BY_RUNNER",
        "paired_confidence_interval": "NOT_ESTIMABLE_FROM_ONE_SHIFTED_WORLD",
        "shifted_descriptive": differences,
        "noise_R_held_brier_excess_over_chance": excess,
        "diagnostic_noise_threshold_exceeders": alerts,
        "noise_diagnostic_flag": ("WARNING_EXCEEDS_0_02" if alerts else
                                  "NO_EXCESS_OBSERVED_IN_THIS_SMALL_SAMPLE"),
        "classification": "NO_SCIENTIFIC_FIRST_USE_OR_PROMOTION",
    }


# Frozen by source commit cc73f5686228d2bd97a12a0bc3cbe5007e69a97c.
# This score audit is descriptive, not a primary scientific qualification.
NULL_FRESH_SEEDS = {
    "diagnostic_shifted": (900111, 900112, 900113),
    "stationary": (900121, 900122, 900123),
    "independent_noise": (900131, 900132, 900133),
}
NULL_BASE = "dense_causal_reward"
NULL_CANDIDATE = "dense_causal_nullmix"


def audit_null_calibration(records: list[dict]) -> dict:
    """Independent, fail-closed, preregistered *diagnostic* comparison.

    Nine never-before-scored diagnostic seed identities were committed ahead
    of this source. Do NOT elevate thresholds or selected cohorts after seeing
    results. A negative threshold verdict is a valid ENGINEERING PASS.
    """
    _require(type(records) is list and len(records) == 9, "NULL_NINE_WORLDS")
    for record in records:
        _receipt(record)
    observed = {}
    for record in records:
        cohort = record["cohort"]
        seed = record["seed"]
        _require(seed in NULL_FRESH_SEEDS[cohort], "NULL_UNFROZEN_SEED")
        _require((cohort, seed) not in observed, "NULL_DUPLICATE_WORLD")
        observed[(cohort, seed)] = record
    _require(set(observed) == {
        (cohort, seed)
        for cohort, seeds in NULL_FRESH_SEEDS.items() for seed in seeds
    }, "NULL_MISSING_WORLD")

    rewards_equal = True
    summaries = {}
    for cohort, seeds in NULL_FRESH_SEEDS.items():
        rows = [observed[(cohort, seed)] for seed in seeds]
        details = {}
        for phase in ("B", "R"):
            parts = [r["phases"][phase]["scores"] for r in rows]
            base_brier = sum(x[NULL_BASE]["equal_action_held_brier"]
                             for x in parts) / len(parts)
            null_brier = sum(x[NULL_CANDIDATE]["equal_action_held_brier"]
                             for x in parts) / len(parts)
            rewards_equal &= all(
                x[NULL_BASE]["selected_held_reward"] ==
                x[NULL_CANDIDATE]["selected_held_reward"] for x in parts)
            details[phase] = {
                "base_mean_brier": round(base_brier, 9),
                "null_mean_brier": round(null_brier, 9),
                "null_minus_base_brier": round(null_brier - base_brier, 9),
                "per_seed": [{
                    "seed": seed,
                    "base_brier": part[NULL_BASE]["equal_action_held_brier"],
                    "null_brier": part[NULL_CANDIDATE]["equal_action_held_brier"],
                    "base_held_reward": part[NULL_BASE]["selected_held_reward"],
                    "null_held_reward": part[NULL_CANDIDATE]["selected_held_reward"],
                    "null_checkpoint_bytes": part[NULL_CANDIDATE]["checkpoint_bytes"],
                    "null_peak_rule_work": part[NULL_CANDIDATE]["peak_rule_work"]
                } for seed, part in zip(seeds, parts)],
            }
        summaries[cohort] = details
    noise = summaries["independent_noise"]["R"]
    noise_pass = noise["null_mean_brier"] <= 0.270 and (
        noise["null_mean_brier"] < noise["base_mean_brier"])
    losses = {}
    for cohort in ("diagnostic_shifted", "stationary"):
        values = [summaries[cohort][phase]["null_minus_base_brier"]
                  for phase in ("B", "R")]
        losses[cohort] = round(sum(values) / len(values), 9)
    transfer_pass = all(loss <= 0.015 for loss in losses.values())
    outcome_pass = noise_pass and transfer_pass and rewards_equal
    return {
        "schema": "yggdrasil.gate28.null-mixture-diagnostic-score.v1",
        "status": ("G28_NULL_DIAGNOSTIC_TARGETS_MET_NOT_SCIENCE"
                   if outcome_pass else "G28_NULL_DIAGNOSTIC_NO_GO"),
        "prereg_commit": "cc73f5686228d2bd97a12a0bc3cbe5007e69a97c",
        "source_primary_consumed": False,
        "scientific_gain_verified": False,
        "matched_control_adequacy": "UNVERIFIED",
        "independent_reproduction": False,
        "seed_count": 9,
        "per_arm_forced_exposure_hash_parity": "NOT_PROVEN_BY_SCORE_AUDIT",
        "source_function_cold_parity": "NOT_PROVEN_BY_SCORE_AUDIT",
        "noise_R_target_met": noise_pass,
        "structured_preservation_met": transfer_pass,
        "action_reward_exact_parity": rewards_equal,
        "all_preregistered_diagnostic_targets_met": outcome_pass,
        "cohort_summary": summaries,
        "structured_mean_B_R_degradation": losses,
        "classification": "NO_SCIENTIFIC_FIRST_USE_OR_PROMOTION",
    }
