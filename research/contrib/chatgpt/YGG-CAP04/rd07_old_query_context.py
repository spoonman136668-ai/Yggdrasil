"""CAP04 RD07 retrospective fixed-full-input retention measurement.

Uses only previously consumed synthetic RD04 public witnesses. Does not
change any learned model or train a new algorithm, or score a fresh cohort.
Frozen protocol was committed prior to this implementation.
"""
from __future__ import annotations
import importlib.util
import json
import math
from pathlib import Path

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_predictive_state_split import (
    PredictiveStateSplit, FEATURES,
)

HERE = Path(__file__).resolve().parent
SCHEMA = "yggdrasil.cap04.rd07.retrospective-old-query-context.v1"
FROZEN_PROTOCOL = "research/contrib/chatgpt/YGG-CAP04/RD07-FROZEN-OLD-QUERY-CONTEXT-AUDIT.md"
SOURCE_SHA = {
    "cap04-rd04-source-a":
        "a3a06178c1bc0955bb7e5258284aaaa90691c556cd832310d146373f703339be",
    "cap04-rd04-source-b":
        "4ed6c8044fa88c4667c3b6194c93f74480ed18462e9720b0e1dba9a718a7cdf3",
}
N = 256
QUERY_COUNT = 16
STAGES = {64: "a_anchor", 192: "b_endpoint",
          256: "a_return_endpoint"}
MODES = ("recent32", "direct", "xor")


def require(value, tag):
    if not value:
        raise ValueError("CAP04_RD07_" + tag)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, HERE / path)
    require(spec is not None and spec.loader is not None, "SOURCE_MODULE")
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def original_rows(name):
    require(type(name) is str and name in SOURCE_SHA, "SOURCE_ID")
    # RD05 transcribes the original synthetic source independently of RD04.
    rd05 = load("rd05_source_support.py", "rd05_source_rd07")
    rows = rd05.source(name)
    require(len(rows) == N and digest(canonical(rows)) == SOURCE_SHA[name],
            "SOURCE_DRIFT")
    return rows


def learner_modes():
    return {
        "recent32": PredictiveStateSplit(
            reward_mode="direct", routing_mode="recent32"),
        "direct": PredictiveStateSplit(reward_mode="direct"),
        "xor": PredictiveStateSplit(),
    }


def assert_public_row(model, row, index):
    """The exact historical public event must be in the learner ledger."""
    require(type(index) is int and 0 <= index < model.count,
            "HISTORICAL_CLOCK")
    ledger = model._events[index]
    st = (row["views"][0][0], row["views"][0][1],
          row["views"][1][1])
    require(ledger[0] == row["id"] and ledger[1] == st
            and ledger[2] == row["action"] and ledger[3] == row["s2"]
            and ledger[4] == row["y"] and ledger[5] == row["post"],
            "SOURCE_LEDGER_MISMATCH")
    return ledger


def pinned_values(model, rows, index, *, claimed_id=None,
                  claimed_prev_id=None, claimed_prev_reward=None):
    """Original pre-observation context, witnessed and ledger-verified.

    Only publicly witnessed previous events may populate historical features.
    Does not read model's current last event or reveal future labels.
    """
    require(type(index) is int and 0 <= index < QUERY_COUNT,
            "OLD_A_QUERY")
    current = rows[index]
    assert_public_row(model, current, index)
    if claimed_id is not None:
        require(claimed_id == current["id"], "CLAIMED_SOURCE_ID")
    if index == 0:
        require(claimed_prev_id is None and claimed_prev_reward is None,
                "NO_PREVIOUS_WITNESS")
        return None
    old = rows[index - 1]
    prev = assert_public_row(model, old, index - 1)
    require(prev[0] != current["id"], "SOURCE_UNIQUE")
    if claimed_prev_id is not None:
        require(claimed_prev_id == prev[0], "CLAIMED_PREV_ID")
    if claimed_prev_reward is not None:
        require(type(claimed_prev_reward) is int and
                claimed_prev_reward == prev[4], "CLAIMED_PREV_REWARD")
    pair, post, reward = prev[2], prev[5], prev[4]
    return {"previous_pair": pair,
            "previous_post": post,
            "previous_reward": reward,
            "previous_pair_post": (pair, post)}


def frozen_prediction(model, rows, index):
    """Exact existing readout using pinned, actual old source history."""
    require(model.sham is False, "SHAM_LAG_UNSUPPORTED")
    current = rows[index]
    values = pinned_values(model, rows, index)
    original = model.checkpoint()
    st = (current["views"][0][0], current["views"][0][1],
          current["views"][1][1])
    conditioned = model._conditioned_state(
        "residual", st, current["s2"])
    feature = model._winner("residual", values)
    value = model._estimate(
        "residual", conditioned, current["action"], values, feature)
    if model.reward_mode == "xor" and current["s2"] == 1:
        value = 1.0 - value
    require(type(value) is float and math.isfinite(value)
            and 0 <= value <= 1, "PREDICTION")
    require(model.checkpoint() == original, "FROZEN_READ_MUTATION")
    return value


def stage_result(models, rows):
    """16 fixed A witness queries, same queries at each learned checkpoint."""
    outcome = {}
    for name, model in models.items():
        before = model.checkpoint()
        cold = PredictiveStateSplit.restore(before, digest(before))
        require(before == cold.checkpoint(), "COLD_RESTORE")
        mismatches = 0
        old_briers = []
        fixed_briers = []
        different_predictions = 0
        for i, event in enumerate(rows[:QUERY_COUNT]):
            require(event["y"] == event["s2"], "OLD_A_LABEL")
            values = pinned_values(model, rows, i)
            require(values == pinned_values(cold, rows, i),
                    "COLD_CONTEXT")
            if values != model._feature_values():
                mismatches += 1
            old = model.forecast(
                event["views"], event["action"], "residual", event["s2"])
            fixed = frozen_prediction(model, rows, i)
            require(abs(fixed - frozen_prediction(cold, rows, i)) < 1e-12,
                    "COLD_FROZEN_READOUT")
            require(0 <= old <= 1 and math.isfinite(old), "LEGACY_P")
            if abs(old - fixed) > 1e-12:
                different_predictions += 1
            old_briers.append((old - event["y"]) ** 2)
            fixed_briers.append((fixed - event["y"]) ** 2)
        require(before == model.checkpoint() == cold.checkpoint(),
                "STATE_MUTATED")
        outcome[name] = {
            "legacy_brier": math.fsum(old_briers) / QUERY_COUNT,
            "fixed_full_context_brier": math.fsum(fixed_briers) / QUERY_COUNT,
            "mismatched_public_history_contexts": mismatches,
            "changed_forecast_with_pinned_context": different_predictions,
            "checkpoint_sha256": digest(before),
            "checkpoint_bytes": len(before),
            "witnessed_events": model.count,
            "cold_exact": True,
        }
    return outcome


def run(name):
    rows = original_rows(name)
    models = learner_modes()
    stages = {}
    for t, event in enumerate(rows):
        require(all(m.count == t for m in models.values()),
                "WITNESS_CLOCK")
        for model in models.values():
            model.observe(event["id"], event["views"], event["action"],
                          event["s2"], event["y"], event["post"])
        if t+1 in STAGES:
            stages[STAGES[t+1]] = stage_result(models, rows)
    require(set(stages) == set(STAGES.values()), "STAGE_COUNT")
    # Directly verify previously published RD04 legacy score contracts,
    # without calling this a new science experiment.
    rd04 = load("rd04_engineering.py", "rd04_prior_rd07")
    old = rd04.run(name)
    require(old["status"] == "RD04_ENGINEERING_NO_GO",
            "ORIGINAL_RD04_STATUS")
    for stage in STAGES.values():
        for mode in MODES:
            expected = old["snapshots"][stage]["old_probe_brier"][mode]
            observed = stages[stage][mode]["legacy_brier"]
            require(abs(observed - expected) <= 1e-12,
                    "ORIGINAL_LEGACY_SCORE_MISMATCH")
    retention = {}
    for mode in MODES:
        anchor = stages["a_anchor"][mode]
        comparisons = {}
        for stage in ("b_endpoint", "a_return_endpoint"):
            current = stages[stage][mode]
            legacy_drift = current["legacy_brier"] - anchor["legacy_brier"]
            fixed_drift = (current["fixed_full_context_brier"] -
                           anchor["fixed_full_context_brier"])
            comparisons[stage] = {
                "legacy_brier_drift": legacy_drift,
                "fixed_full_context_brier_drift": fixed_drift,
                "retrospective_fixed_context_within_old_limit":
                    fixed_drift <= 0.020 + 1e-12,
            }
        retention[mode] = comparisons
    return {
        "schema": SCHEMA, "protocol": FROZEN_PROTOCOL,
        "evidence_class": "RETROSPECTIVE_CONSUMED_SYNTHETIC_ONLY",
        "source": name, "original_source_sha256": SOURCE_SHA[name],
        "source_events": N, "old_probe_count": QUERY_COUNT,
        "previous_rd04_verdict": old["status"],
        "previous_rd04_verdict_unchanged": True,
        "stages": stages, "functional_readout_drift": retention,
        "scientific_pass": False, "active_phase_identification_tested": False,
        "new_world_generalization_tested": False,
        "canonical_model_modified": False,
        "status": "RD07_RETROSPECTIVE_VALID",
    }


def audit(raw):
    require(type(raw) is bytes and len(raw) < 140000, "AUDIT_SIZE")
    try:
        doc = json.loads(raw.decode("ascii"))
        require(type(doc) is dict and canonical(doc) == raw and
                doc.get("schema") == SCHEMA and
                doc.get("evidence_class") ==
                    "RETROSPECTIVE_CONSUMED_SYNTHETIC_ONLY" and
                doc.get("scientific_pass") is False and
                doc.get("canonical_model_modified") is False and
                doc.get("previous_rd04_verdict_unchanged") is True and
                doc.get("active_phase_identification_tested") is False and
                doc.get("new_world_generalization_tested") is False,
                "AUDIT_SCOPE")
        require(canonical(run(doc["source"])) == raw, "AUDIT_REPLAY")
        return {
            "source": doc["source"],
            "source_sha256": doc["original_source_sha256"],
            "receipt_sha256": digest(raw),
            "status": doc["status"],
            "previous_rd04_verdict": doc["previous_rd04_verdict"],
            "old_probe_count": doc["old_probe_count"],
            "stages": doc["stages"],
            "functional_readout_drift": doc["functional_readout_drift"],
            "scientific_pass": False,
            "canonical_model_modified": False,
        }
    except (KeyError, TypeError, ValueError, ArithmeticError,
            OverflowError, UnicodeError, IndexError) as exc:
        raise ValueError("CAP04_RD07_DIAGNOSTIC_INVALID") from exc


def compact(report, checked):
    return {
        "source": report["source"],
        "source_sha256": report["original_source_sha256"],
        "receipt_sha256": checked["receipt_sha256"],
        "status": report["status"],
        "previous_rd04_verdict": report["previous_rd04_verdict"],
        "readout_drift": report["functional_readout_drift"],
        "stages": {
            stage: {
                model: {
                    "legacy": report["stages"][stage][model]["legacy_brier"],
                    "fixed": report["stages"][stage][model][
                        "fixed_full_context_brier"],
                    "mismatched_inputs": report["stages"][stage][model][
                        "mismatched_public_history_contexts"],
                    "changed_outputs": report["stages"][stage][model][
                        "changed_forecast_with_pinned_context"],
                    "checkpoint_sha256": report["stages"][stage][model][
                        "checkpoint_sha256"],
                    "checkpoint_bytes": report["stages"][stage][model][
                        "checkpoint_bytes"],
                }
                for model in MODES
            } for stage in STAGES.values()
        },
        "scientific_pass": False,
        "canonical_model_modified": False,
    }


if __name__ == "__main__":
    for source in SOURCE_SHA:
        v = run(source)
        check = audit(canonical(v))
        print("CAP04_RD07_RETROSPECTIVE=" +
              canonical(compact(v, check)).decode("ascii"), flush=True)
