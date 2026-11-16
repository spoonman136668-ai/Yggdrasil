"""WSP127 engineering-only preregistered adaptive-intervention comparison.

No protected first use, result.json, native admission or scientific PASS.
Scoring labels are visible only inside the source custodian.
"""
from __future__ import annotations
import argparse
import random
import time

import source as S
import numeric as N
import controls as C

ARMS = ("ADAPTIVE_NUMERIC", "ADAPTIVE_OPTIMIZED_GF2",
        "FIXED_NUMERIC", "FIXED_OPTIMIZED_GF2", "NO_UPDATE")
FIELDS = ("held", "correct", "wrong_confident", "abstained", "source_calls")

def _zero():
    return {arm: {k: 0 for k in FIELDS} for arm in ARMS}

def _add(totals, arm, score):
    for field in FIELDS:
        totals[arm][field] += score[field]

def _models():
    return {
        "ADAPTIVE_NUMERIC": N.DirectRankEight("adaptive"),
        "ADAPTIVE_OPTIMIZED_GF2": C.OptimizedSymbolic(),
        "FIXED_NUMERIC": N.DirectRankEight("fixed"),
        "FIXED_OPTIMIZED_GF2": C.OptimizedSymbolic(),
        "NO_UPDATE": C.NoUpdate(),
    }

def _predict_all(model, view, held):
    return {subject: model.infer(view, subject) for subject, _, _ in held}

def _identical(a, b):
    return (a["correct"], a["wrong_confident"], a["abstained"]) == (
        b["correct"], b["wrong_confident"], b["abstained"])

def _train_and_score(models, worlds=128):
    totals = _zero()
    law_rows = []
    rank_histogram = {str(i): 0 for i in range(9)}
    transcript_receipts = []
    for law in range(worlds):
        view = S.world(135000 + law)
        custodians = {arm: S.Custodian(view) for arm in ARMS}
        available_adaptive = set(view.legal)
        available_fixed = set(view.legal)
        for step in range(1024):
            adaptive_action = models["ADAPTIVE_NUMERIC"].choose(
                view, available_adaptive)
            fixed_action = models["FIXED_NUMERIC"].choose(
                view, available_fixed)
            if (adaptive_action is None or fixed_action is None or
                    adaptive_action not in available_adaptive or
                    fixed_action not in available_fixed):
                raise AssertionError("WSP127_ACTION_POLICY_OVER_BUDGET_OR_DUPLICATE")
            available_adaptive.remove(adaptive_action)
            available_fixed.remove(fixed_action)
            for arm in ARMS:
                subject = (fixed_action if arm.startswith("FIXED")
                           else adaptive_action)
                evidence = custodians[arm].query(subject)
                models[arm].observe(view, evidence)
        for policy in ("ADAPTIVE", "FIXED"):
            native = policy + "_NUMERIC"
            strong = policy + "_OPTIMIZED_GF2"
            if custodians[native].receipt != custodians[strong].receipt:
                raise AssertionError("WSP127_STRONG_CONTROL_TRANSCRIPT_MISMATCH")
        if custodians["NO_UPDATE"].receipt != custodians["ADAPTIVE_NUMERIC"].receipt:
            raise AssertionError("WSP127_NO_UPDATE_ACTION_MISMATCH")
        per = {}
        for arm in ARMS:
            cust = custodians[arm]
            if len(cust.events) != 1024:
                raise AssertionError("WSP127_UNEQUAL_INTERVENTION_BUDGET")
            held = tuple(cust.held())
            if len(held) != 3072:
                raise AssertionError("WSP127_BAD_HELD_FIT_SET")
            predictions = _predict_all(models[arm], view, held)
            result = cust.score_once(predictions)
            _add(totals, arm, result)
            per[arm] = result
        if not _identical(per["ADAPTIVE_NUMERIC"],
                          per["ADAPTIVE_OPTIMIZED_GF2"]):
            raise AssertionError("WSP127_ADAPTIVE_SYMBOLIC_PARITY_FAIL")
        if not _identical(per["FIXED_NUMERIC"], per["FIXED_OPTIMIZED_GF2"]):
            raise AssertionError("WSP127_FIXED_SYMBOLIC_PARITY_FAIL")
        rank = models["ADAPTIVE_NUMERIC"]._state(law).rank()
        rank_histogram[str(rank)] += 1
        law_rows.append([law, per["ADAPTIVE_NUMERIC"]["correct"],
                         per["FIXED_OPTIMIZED_GF2"]["correct"],
                         per["ADAPTIVE_NUMERIC"]["abstained"],
                         per["FIXED_OPTIMIZED_GF2"]["abstained"]])
        transcript_receipts.append([law, custodians["ADAPTIVE_NUMERIC"].receipt,
                                    custodians["FIXED_NUMERIC"].receipt])
    if totals["ADAPTIVE_NUMERIC"]["source_calls"] != worlds * 1024:
        raise AssertionError("WSP127_SOURCE_CALLS_MISMATCH")
    return {"scores": totals, "law_rows": law_rows, "rank_histogram": rank_histogram,
            "transcript_sha256": S.digest(transcript_receipts)}

def _evaluate_zero_source(models, cohort, seeds):
    totals = _zero()
    receipts = []
    for seed in seeds:
        view = S.world(seed)
        per = {}
        for arm in ARMS:
            cust = S.Custodian(view)
            if cust.budget or cust.events or view.legal:
                raise AssertionError("WSP127_TRANSFER_SOURCE_NOT_ZERO")
            held = tuple(cust.held())
            if len(held) != 4096:
                raise AssertionError("WSP127_TRANSFER_INCOMPLETE")
            result = cust.score_once(_predict_all(models[arm], view, held))
            per[arm] = result
            _add(totals, arm, result)
        for policy in ("ADAPTIVE", "FIXED"):
            if not _identical(per[policy + "_NUMERIC"],
                              per[policy + "_OPTIMIZED_GF2"]):
                raise AssertionError("WSP127_TRANSFER_SYMBOLIC_PARITY_FAIL")
        receipts.append([seed, (per["ADAPTIVE_NUMERIC"]["correct"],
                                per["ADAPTIVE_NUMERIC"]["wrong_confident"],
                                per["ADAPTIVE_NUMERIC"]["abstained"]),
                         (per["FIXED_NUMERIC"]["correct"],
                          per["FIXED_NUMERIC"]["wrong_confident"],
                          per["FIXED_NUMERIC"]["abstained"])])
    return {"worlds": len(receipts), "scores": totals,
            "sha256": S.digest(receipts)}

def _bootstrap(law_rows):
    # Frozen 10,000 paired law-level resamples using seed 127. Scores are
    # gain in percentage points of 3072 withheld bits per source law.
    rng = random.Random(127)
    differences = [r[1] - r[2] for r in law_rows]
    n = len(differences)
    estimates = []
    for _ in range(10000):
        difference = sum(differences[rng.randrange(n)] for _ in range(n))
        estimates.append(100.0 * difference / (n * 3072))
    estimates.sort()
    return {"resamples": 10000, "seed": 127,
            "percentile_95_low": estimates[250],
            "percentile_95_high": estimates[9749]}

def run_engineering():
    start = time.perf_counter()
    if S.ALLOWED & S.DENIED:
        raise PermissionError("WSP127_PROTECTED_SOURCE_OVERLAP")
    models = _models()
    fit = _train_and_score(models)
    native = models["ADAPTIVE_NUMERIC"]
    snapshot = native.snapshot()
    cold = N.DirectRankEight.restore(snapshot)
    if snapshot != cold.snapshot():
        raise AssertionError("WSP127_COLD_REPLAY_DIFFER")
    for law in range(128):
        view = S.world(135000 + law)
        for a in range(64):
            for b in range(64):
                subject = view.subject(a, b)
                if cold.infer(view, subject) != native.infer(view, subject):
                    raise AssertionError("WSP127_OLD_LAW_COLD_RETENTION_FAILURE")
    transfer = _evaluate_zero_source(models, "transfer", range(136000, 136256))
    negative = _evaluate_zero_source(models, "negative", range(137000, 137064))
    for law in range(128):
        view = S.world(135000 + law)
        if cold._state(law).payload() != native._state(law).payload():
            raise AssertionError("WSP127_LATE_INTERFERENCE")
    native_fit = fit["scores"]["ADAPTIVE_NUMERIC"]
    baseline_fit = fit["scores"]["FIXED_OPTIMIZED_GF2"]
    gain_pp = 100 * (native_fit["correct"] - baseline_fit["correct"]) / 393216
    correct_rate = 100 * native_fit["correct"] / 393216
    off = negative["scores"]["ADAPTIVE_NUMERIC"]
    wrong_off_rate = 100 * off["wrong_confident"] / 262144
    policy_supported = (correct_rate >= 95 and gain_pp >= 8 and
                        native_fit["wrong_confident"] == 0)
    out_family_safe = wrong_off_rate <= 1.0
    classification = ("DEVELOPMENT_NO_GO" if not policy_supported else
                      "DEVELOPMENT_MIXED_POLICY_ONLY" if not out_family_safe else
                      "DEVELOPMENT_POLICY_SUPPORTED_NOT_UNIQUE_NUMERIC")
    return {
        "schema": "wsp127.engineering-only.v1",
        "status": classification,
        "scientific_pass": False,
        "original_first_use": False,
        "native_admission": False,
        "fit": {"scores": fit["scores"], "rank_histogram": fit["rank_histogram"],
                "transcript_sha256": fit["transcript_sha256"],
                "law_rows_sha256": S.digest(fit["law_rows"]),
                "adaptive_correct_percent": correct_rate,
                "gain_over_fixed_symbolic_pp": gain_pp,
                "paired_bootstrap": _bootstrap(fit["law_rows"])},
        "transfer": transfer,
        "out_family": negative,
        "rank9_wrong_confident_percent": wrong_off_rate,
        "cold_retention": True,
        "post_interference": True,
        "symbolic_matched": True,
        "strong_trained_conventional": "UNQUALIFIED_NOT_RUN",
        "whole_process_cost": {"elapsed_seconds_development_only": round(time.perf_counter()-start, 3),
                               "source_actions_per_arm": 131072,
                               "measurement_status": "INCOMPLETE_NO_CPU_RSS_ENERGY"},
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--engineering", action="store_true", required=True)
    args = parser.parse_args()
    print("WSP127_ENGINEERING_JSON=" + S.canon(run_engineering()))
