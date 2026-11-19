"""CAP04 independent engineering-fixture receipt auditor, NEVER scientific scoring.

Registered DEV/pilot/primary seeds are neither imported nor generated here.
This module validates forecast-before-observe, matched per-arm information,
two-stage Brier arithmetic, phase windows, source provenance and cold replay.
Fixture scores are engineering diagnostics, never scientific efficacy evidence.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_predictive_state_split import PredictiveStateSplit
from yggdrasil.native_predictive_state_controls import MatchedHistoryControls, ARMS

SCHEMA = "yggdrasil.cap04.fixture-blind-audit.v1"
HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source_fixture.py"
PHASES = {"novel": (48, 72), "cold_return": (72, 96), "pooled": (48, 96)}
N = 96
ARMS_ALL = ("predictive_state_split",) + ARMS


def require(condition, reason):
    if not condition:
        raise ValueError("CAP04_AUDIT_" + reason)


def source_module():
    spec = importlib.util.spec_from_file_location("cap04_audit_fixture_only", SOURCE)
    require(spec is not None and spec.loader is not None, "SOURCE_MODULE")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    require(tuple(module.FIXTURE_IDS) ==
            ("engineering-history-01", "engineering-history-02"), "SOURCE_ONLY_FIXTURES")
    return module


def finite_probability(value):
    require(type(value) is float and math.isfinite(value)
            and 0.0 <= value <= 1.0, "FINITE_PROBABILITY")
    return value


def loss(prob, outcome):
    finite_probability(prob)
    require(type(outcome) is int and outcome in (0, 1), "BINARY_OUTCOME")
    return (prob - outcome) ** 2


def phase_means(rows):
    require(len(rows) == N, "ROW_COUNT")
    out = {}
    for name, (start, end) in PHASES.items():
        out[name] = {}
        for key in ARMS_ALL:
            s = math.fsum(
                (loss(row["pre_transition"][key], row["outcome"]["s2"]) +
                 loss(row["pre_reward"][key], row["outcome"]["y"])) / 2.0
                for row in rows[start:end])
            out[name][key] = s / (end - start)
    return out


def readout(model, controls, views, action, s2):
    before = model.checkpoint(), controls.checkpoint()
    transition = {"predictive_state_split":
                  finite_probability(model.forecast(views, action, "transition"))}
    transition.update(controls.forecast(views, action, "transition"))
    # The measured intermediate sensor s2 is only revealed at stage 2,
    # before revealing the terminal reward y to either predictor.
    reward = {"predictive_state_split":
              finite_probability(model.forecast(views, action, "residual", s2))}
    reward.update(controls.forecast(views, action, "residual", s2))
    require(set(transition) == set(reward) == set(ARMS_ALL), "COMPLETE_ARMS")
    for arm_name in ARMS_ALL:
        finite_probability(transition[arm_name])
        finite_probability(reward[arm_name])
    require(before == (model.checkpoint(), controls.checkpoint()), "READ_MUTATION")
    return transition, reward


def build_fixture_receipt(fixture_id):
    source = source_module()
    require(type(fixture_id) is str and fixture_id in source.FIXTURE_IDS,
            "REGISTERED_FIRST_USE_FORBIDDEN")
    events = source.generate(fixture_id, N)
    model = PredictiveStateSplit()
    controls = MatchedHistoryControls()
    rows = []
    for t, event in enumerate(events):
        require(set(event) == {"id", "views", "action", "s2", "y", "post"},
                "SOURCE_FIELDS")
        require(model.count == controls.count == t, "CHRONOLOGY")
        before = (digest(model.checkpoint()), digest(controls.checkpoint()))
        first, second = readout(model, controls, event["views"], event["action"],
                                event["s2"])
        require(before == (digest(model.checkpoint()), digest(controls.checkpoint())),
                "PREQUENTIAL")
        rows.append({
            "t": t, "id": event["id"],
            "views": event["views"], "action": event["action"],
            "pre_state_sha256": before,
            "pre_transition": first, "pre_reward": second,
            "outcome": {"s2": event["s2"], "y": event["y"], "post": event["post"]}
        })
        model.observe(event["id"], event["views"], event["action"], event["s2"],
                      event["y"], event["post"])
        controls.observe(event["id"], event["views"], event["action"], event["s2"],
                         event["y"], event["post"])
    source_sha256 = digest(canonical(events))
    payload = {"schema": SCHEMA, "evidence_class": "ENGINEERING_FIXTURE_ONLY",
               "fixture_id": fixture_id, "source_sha256": source_sha256,
               "row_count": N, "rows": rows, "phase_means": phase_means(rows),
               "final_state_sha256": [digest(model.checkpoint()),
                                      digest(controls.checkpoint())]}
    return canonical(payload)


def audit_fixture_receipt(raw):
    """Separate one-pass recomputation from exact fixture source and public priors."""
    require(type(raw) is bytes and len(raw) < 500000, "RAW_SIZE")
    try:
        doc = json.loads(raw.decode("ascii"))
        require(canonical(doc) == raw, "CANONICAL")
        require(set(doc) == {"schema", "evidence_class", "fixture_id",
                            "source_sha256", "row_count", "rows",
                            "phase_means", "final_state_sha256"},
                "RECEIPT_FIELDS")
        require(doc["schema"] == SCHEMA and
                doc["evidence_class"] == "ENGINEERING_FIXTURE_ONLY", "SCHEMA")
        source = source_module()
        require(type(doc["fixture_id"]) is str and
                doc["fixture_id"] in source.FIXTURE_IDS, "FIRST_USE_FORBIDDEN")
        events = source.generate(doc["fixture_id"], N)
        require(doc["source_sha256"] == digest(canonical(events)), "SOURCE_PIN")
        require(doc["row_count"] == len(doc["rows"]) == N, "ROW_COUNT")
        model = PredictiveStateSplit()
        controls = MatchedHistoryControls()
        for t, (row, event) in enumerate(zip(doc["rows"], events)):
            require(type(row) is dict and set(row) ==
                    {"t", "id", "views", "action", "pre_state_sha256",
                     "pre_transition", "pre_reward", "outcome"}, "ROW_FIELDS")
            require(type(row["t"]) is int and row["t"] == t and
                    row["id"] == event["id"] and
                    row["views"] == [list(x) for x in event["views"]] and
                    row["action"] == list(event["action"]), "ROW_SOURCE_CLOCK")
            require(row["outcome"] == {
                "s2": event["s2"], "y": event["y"],
                "post": list(event["post"])}, "ROW_OUTCOME")
            require(row["pre_state_sha256"] ==
                    [digest(model.checkpoint()), digest(controls.checkpoint())],
                    "PRE_STATE")
            first, second = readout(model, controls, event["views"],
                                    event["action"], event["s2"])
            for name in ARMS_ALL:
                require(type(row["pre_transition"][name]) is float and
                        type(row["pre_reward"][name]) is float and
                        abs(first[name] - row["pre_transition"][name]) <= 1e-12 and
                        abs(second[name] - row["pre_reward"][name]) <= 1e-12,
                        "FORECAST_MISMATCH")
            model.observe(event["id"], event["views"], event["action"],
                          event["s2"], event["y"], event["post"])
            controls.observe(event["id"], event["views"], event["action"],
                             event["s2"], event["y"], event["post"])
        require(doc["final_state_sha256"] ==
                [digest(model.checkpoint()), digest(controls.checkpoint())],
                "FINAL_COLD_STATE")
        for phase, metrics in phase_means(doc["rows"]).items():
            require(set(doc["phase_means"][phase]) == set(ARMS_ALL),
                    "PHASE_ARMS")
            for name, score in metrics.items():
                require(type(doc["phase_means"][phase][name]) is float and
                        abs(doc["phase_means"][phase][name] - score) <= 1e-12,
                        "BRIER_MISMATCH")
        require(set(doc["phase_means"]) == set(PHASES), "PHASE_WINDOWS")
        # No scientific pass/fail calculation is exposed on engineering fixtures.
        return {"schema": SCHEMA, "classification": "ENGINEERING_FIXTURE_ONLY",
                "fixture_id": doc["fixture_id"], "rows_verified": N,
                "receipt_sha256": digest(raw), "matched_controls": len(ARMS_ALL) - 1}
    except (ValueError, TypeError, KeyError, IndexError, UnicodeError,
            OverflowError, ArithmeticError) as exc:
        raise ValueError("YGG_CAP04_FIXTURE_AUDIT_REJECTED") from exc


def engineering_diagnostic(fixture_id, raw=None):
    """Reconcile old-world/novel/return Brier vs every existing fitted arm.

    This is exploratory *engineering fixture* scoring on already-known
    fabricated source, not a fresh DEV result or independently held science.
    Never turn fixture performance into SCIENTIFIC_PASS.
    """
    if raw is None:
        raw = build_fixture_receipt(fixture_id)
    proof = audit_fixture_receipt(raw)
    doc = json.loads(raw.decode("ascii"))
    require(doc["fixture_id"] == fixture_id, "DIAGNOSTIC_SOURCE")
    require(proof["classification"] == "ENGINEERING_FIXTURE_ONLY",
            "DIAGNOSTIC_SCOPE")
    rows = doc["rows"]
    # Stage zero is intentionally separated: the published novel and return
    # Brier windows are locked in the existing fixture audit.
    stage0 = phase_means(rows)
    phases = {}
    for phase in ("novel", "cold_return", "pooled"):
        scores = stage0[phase]
        candidates = [(scores[name], name) for name in ARMS]
        best_score, best_name = min(candidates)
        candidate = scores["predictive_state_split"]
        phases[phase] = {
            "candidate_brier": round(candidate, 9),
            "best_control": best_name,
            "best_control_brier": round(best_score, 9),
            "candidate_minus_best": round(candidate - best_score, 9),
            "candidate_better": candidate < best_score,
            "arms": {name: round(scores[name], 9) for name in ARMS_ALL},
        }
    # Necessary but not sufficient identifiability diagnostic: check whether
    # the *same observed public views and current action* can follow multiple
    # different previous witnessed actions in the novel stage.
    public_cells = {}
    ordered_pairs = set()
    for i in range(32, 72):
        current = rows[i]
        previous_action = tuple(rows[i - 1]["action"])
        action = tuple(current["action"])
        key = (tuple(tuple(view) for view in current["views"]), action)
        public_cells.setdefault(key, set()).add(previous_action)
        ordered_pairs.add((previous_action, action))
    return {
        "schema": "yggdrasil.cap04.engineering-diagnostic.v1",
        "evidence_class": "ENGINEERING_FIXTURE_ONLY",
        "fixture_id": fixture_id,
        "source_sha256": doc["source_sha256"],
        "receipt_sha256": proof["receipt_sha256"],
        "rows": N,
        "registered_source_actions": 0,
        "observed_previous_current_pairs": len(ordered_pairs),
        "potentially_history_distinguishing_public_cells":
            sum(len(previous) > 1 for previous in public_cells.values()),
        "novel_public_cells": len(public_cells),
        "phases": phases,
        "scientific_pass": False,
        "accepted_native_state_changed": False,
    }


if __name__ == "__main__":
    for fixture_id in source_module().FIXTURE_IDS:
        print("CAP04_ENGINEERING_DIAGNOSTIC=" +
              canonical(engineering_diagnostic(fixture_id)).decode("ascii"))
