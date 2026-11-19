"""CAP04-RD03 retrospective, read-only cause-of-NO_GO instrumentation.

Replays only known RD02 engineering fixtures. No fresh scientific scoring,
protected source-owner first use, model promotion, or hyperparameter tuning.
See the earlier frozen RD03-RETROSPECTIVE-DIAGNOSTIC.md contract.
"""
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_paired_causal_contrast import arm, state
from yggdrasil.native_predictive_state_split import (
    PredictiveStateSplit, FEATURES, LOG_PENALTY, MIN_EVIDENCE,
)

HERE = Path(__file__).resolve().parent
RD02_PATH = HERE / "rd02_engineering.py"
SCHEMA = "yggdrasil.cap04.rd03.retrospective-diagnostic.v1"
SOURCE_PINS = {
    "cap04-rd02-source-a":
        "1b859f00f466d9d20b20f078cc47a4ddb0baaa91ea54895df9b22017be06ed77",
    "cap04-rd02-source-b":
        "780e046fbcbec0f22dc9201eabbafafbe8777305a8bd8a135a0122c1e39c8ec0",
}
PUBLISHED_NOVEL_TERMINAL_BRIER = {
    "cap04-rd02-source-a": 0.1464878998506287,
    "cap04-rd02-source-b": 0.19896147453966154,
}
PHASES = {"a_acquisition": (0, 64), "b_adaptation": (64, 96),
          "b_scored": (96, 192), "a_return": (192, 256)}
FEATURE_NAMES = ("none",) + FEATURES
MODEL_NAMES = ("direct", "direct_sham")
METRICS = ("selected_terminal", "pooled_terminal",
           "forced_previous_pair_terminal")
BOUNDARIES = (64, 96, 192, 256)


def require(condition, code):
    if not condition:
        raise ValueError("CAP04_RD03_" + code)


def rd02():
    spec = importlib.util.spec_from_file_location("cap04_rd02_previous", RD02_PATH)
    require(spec is not None and spec.loader is not None, "SOURCE_MODULE")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def finite(value):
    require(type(value) is float and math.isfinite(value)
            and 0 <= value <= 1, "PROBABILITY")
    return value


def read_preterminal(model, event):
    """Inspect existing pre-observation state, not alter a selector or source."""
    before = model.checkpoint()
    chosen = model.selected_feature("residual")
    values = model._feature_values()
    context = model._conditioned_state(
        "residual", state(event["views"]), event["s2"])
    intervention = arm(event["action"])
    selected = finite(model.forecast(
        event["views"], event["action"], "residual", event["s2"]))
    pooled = finite(model._estimate(
        "residual", context, intervention, values, None))
    forced = finite(model._estimate(
        "residual", context, intervention, values, "previous_pair"))
    require(model.checkpoint() == before, "INSPECTION_MUTATED")
    require(chosen in FEATURES or chosen is None, "FEATURE_SET")
    return {"feature": chosen if chosen is not None else "none",
            "selected_terminal": selected, "pooled_terminal": pooled,
            "forced_previous_pair_terminal": forced,
            "qualified_events": model._qualified["residual"],
            "evidence": {name: float(model._evidence["residual"][name])
                         for name in FEATURES}}


def replay(source_name):
    require(type(source_name) is str and source_name in SOURCE_PINS,
            "SOURCE_ID")
    original = rd02()
    records = original.source(source_name)
    source_sha = digest(canonical(records))
    require(source_sha == SOURCE_PINS[source_name], "SOURCE_CHANGED")
    learners = {"direct": PredictiveStateSplit(reward_mode="direct"),
                "direct_sham": PredictiveStateSplit(
                    reward_mode="direct", sham=True)}
    rows = []
    snapshots = {}
    for t, event in enumerate(records):
        require(all(model.count == t for model in learners.values()),
                "CLOCK")
        predictions = {name: read_preterminal(model, event)
                       for name, model in learners.items()}
        rows.append({"t": t, "id": event["id"], "y": event["y"],
                     "predictions": predictions})
        for model in learners.values():
            model.observe(event["id"], event["views"], event["action"],
                          event["s2"], event["y"], event["post"])
        if t + 1 in BOUNDARIES:
            snapshots[str(t + 1)] = {}
            for name, model in learners.items():
                before = model.checkpoint()
                snapshots[str(t + 1)][name] = {
                    "checkpoint_sha256": digest(before),
                    "event_count": model.count,
                    "selected_feature": model.selected_feature("residual")
                        or "none",
                    "qualified_events": model._qualified["residual"],
                    "evidence": {f: float(model._evidence["residual"][f])
                                 for f in FEATURES},
                }
                require(model.checkpoint() == before, "SNAPSHOT_MUTATED")
    phases = {}
    for phase, (start, stop) in PHASES.items():
        part = rows[start:stop]
        phases[phase] = {}
        for name in MODEL_NAMES:
            counts = {feature: sum(
                row["predictions"][name]["feature"] == feature
                for row in part) for feature in FEATURE_NAMES}
            require(sum(counts.values()) == len(part), "COUNT")
            brier = {metric: math.fsum(
                (row["predictions"][name][metric] - row["y"]) ** 2
                for row in part) / len(part) for metric in METRICS}
            phases[phase][name] = {"selected_features": counts,
                                   "terminal_brier": brier}
    actual = phases["b_scored"]["direct"]["terminal_brier"]["selected_terminal"]
    require(abs(actual - PUBLISHED_NOVEL_TERMINAL_BRIER[source_name])
            <= 1e-12, "PRIOR_SCORE_MISMATCH")
    require(len(rows) == 256 and set(snapshots) == {
        str(x) for x in BOUNDARIES}, "ROWS")
    return {"schema": SCHEMA, "scope": "RETROSPECTIVE_ENGINEERING_ONLY",
            "source": source_name, "source_sha256": source_sha,
            "events": len(rows), "phase_bounds": {
                k: list(v) for k, v in PHASES.items()},
            "phase_results": phases,
            "boundary_evidence": snapshots,
            "old_rd02_status": "RD02_ENGINEERING_NO_GO",
            "prior_score_verified": True,
            "frozen_penalty": LOG_PENALTY,
            "frozen_min_evidence": MIN_EVIDENCE,
            "scientific_pass": False,
            "model_owner_changed": False}


def audit(raw):
    """Independent deterministic replay of same consumed engineering rows."""
    require(type(raw) is bytes and len(raw) < 200000, "AUDIT_SIZE")
    try:
        doc = json.loads(raw.decode("ascii"))
        require(type(doc) is dict and
                set(doc) == {"schema", "scope", "source", "source_sha256",
                             "events", "phase_bounds", "phase_results",
                             "boundary_evidence", "old_rd02_status",
                             "prior_score_verified", "frozen_penalty",
                             "frozen_min_evidence", "scientific_pass",
                             "model_owner_changed"} and
                doc.get("schema") == SCHEMA, "AUDIT_FIELDS")
        require(canonical(doc) == raw, "AUDIT_CANONICAL")
        # A post-hoc diagnostic never gets a scientific success status.
        require(doc["scientific_pass"] is False
                and doc["model_owner_changed"] is False,
                "AUDIT_SCOPE")
        require(canonical(replay(doc["source"])) == raw, "AUDIT_REPLAY")
        return {"source": doc["source"], "source_sha256": doc["source_sha256"],
                "receipt_sha256": digest(raw), "events": doc["events"],
                "status": doc["old_rd02_status"],
                "phase_results": doc["phase_results"],
                "boundary_evidence": doc["boundary_evidence"],
                "scientific_pass": False}
    except (KeyError, TypeError, ValueError, ArithmeticError, OverflowError,
            UnicodeError, IndexError) as exc:
        raise ValueError("CAP04_RD03_AUDIT_REJECTED") from exc


if __name__ == "__main__":
    for name in SOURCE_PINS:
        raw = canonical(replay(name))
        output = audit(raw)
        print("CAP04_RD03_RETROSPECTIVE=" +
              canonical(output).decode("ascii"), flush=True)
