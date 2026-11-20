"""CAP04-RD02 independently frozen A-B-A engineering falsifier, never science.

Two deterministic fabricated sources only. No owner, protected world, model
promotion, first-use, registered DEV seed, or policy interaction is performed.
RD02-FROZEN-ENGINEERING.md was published before this implementation.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_predictive_state_controls import MatchedHistoryControls, ARMS as CONTROLS
from yggdrasil.native_predictive_state_split import PredictiveStateSplit

SCHEMA = "yggdrasil.cap04.rd02.synthetic-engineering.v1"
SOURCE_NAMES = ("cap04-rd02-source-a", "cap04-rd02-source-b")
ARMS = ((0, 0), (0, 1), (1, 0), (1, 1))
ACTION_CYCLE = (0, 0, 1, 0, 2, 0, 3, 1, 1, 2, 1, 3, 2, 2, 3, 3)
N = 256
WINDOWS = {"novel": (96, 192), "a_return": (192, 256), "pooled": (96, 256)}
CANDIDATES = ("direct", "xor", "direct_sham")
NAMES = CANDIDATES + CONTROLS
ENGINEERING_ONLY = "SYNTHETIC_ENGINEERING_ONLY"
FROZEN_PROTOCOL = "research/contrib/chatgpt/YGG-CAP04/RD02-FROZEN-ENGINEERING.md"


def require(condition, tag):
    if not condition:
        raise ValueError("CAP04_RD02_" + tag)


def hbit(text):
    return hashlib.sha256(text.encode("ascii")).digest()[0] & 1


def source(source_name):
    """Independent fixed public action/consequence generator; no models read it."""
    require(type(source_name) is str and source_name in SOURCE_NAMES,
            "SOURCE_NOT_REGISTERED_ENGINEERING")
    u, v, w = (hbit(f"cap04/rd02/{source_name}/start/{i}")
               for i in range(3))
    previous_actual_action = (0, 0)
    records = []
    shift = int(source_name == SOURCE_NAMES[1])
    for t in range(N):
        views = ((u, v), (v, w))
        action = ARMS[ACTION_CYCLE[(t + shift) % len(ACTION_CYCLE)]]
        s2 = hbit(f"cap04/rd02/{source_name}/{t}/public-intermediate")
        # This private, scored-ONLY phase is never a learner input.
        y = (previous_actual_action[0] & s2) if 64 <= t < 192 else s2
        post = (v ^ action[0], s2, w ^ action[1])
        identifier = hashlib.sha256(
            f"cap04/rd02/{source_name}/witness/{t}".encode("ascii")
        ).hexdigest()
        records.append({"id": identifier, "views": views, "action": action,
                        "s2": s2, "y": y, "post": post})
        u, v, w = post
        previous_actual_action = action
    require(len(records) == N and len({r["id"] for r in records}) == N,
            "SOURCE_IDENTITY")
    return tuple(records)


def probability(p):
    p = float(p)
    require(math.isfinite(p) and 0 <= p <= 1, "PROBABILITY")
    return p


def readouts(learners, views, action, s2):
    """Prequential: transition before s2; reward after s2, before y."""
    before = [learners[n].checkpoint() for n in CANDIDATES]
    before.append(learners["controls"].checkpoint())
    first = {
        name: probability(learners[name].forecast(views, action, "transition"))
        for name in CANDIDATES
    }
    first.update({
        name: probability(p)
        for name, p in learners["controls"].forecast(
            views, action, "transition").items()
    })
    second = {
        name: probability(
            learners[name].forecast(views, action, "residual", s2))
        for name in CANDIDATES
    }
    second.update({
        name: probability(p)
        for name, p in learners["controls"].forecast(
            views, action, "residual", s2).items()
    })
    require(set(first) == set(second) == set(NAMES), "MATCHED_ARMS")
    after = [learners[n].checkpoint() for n in CANDIDATES]
    after.append(learners["controls"].checkpoint())
    require(before == after, "FORECAST_MUTATION")
    return first, second


def phase_scores(rows):
    require(len(rows) == N, "ROWS")
    result = {}
    for phase, (start, stop) in WINDOWS.items():
        part = rows[start:stop]
        result[phase] = {}
        for name in NAMES:
            transition = math.fsum(
                (r["first"][name] - r["s2"]) ** 2 for r in part
            ) / len(part)
            terminal = math.fsum(
                (r["second"][name] - r["y"]) ** 2 for r in part
            ) / len(part)
            result[phase][name] = {
                "two_stage": (transition + terminal) / 2.0,
                "terminal": terminal,
            }
    return result


def fixed_old_probes(learners, queries):
    """Read a pinned A-skill query list, without obtaining any new labels."""
    scores = {}
    for name in ("direct", "xor"):
        raw_before = learners[name].checkpoint()
        scores[name] = math.fsum(
            (learners[name].forecast(views, action, "residual", s2) - s2) ** 2
            for views, action, s2 in queries
        ) / len(queries)
        require(learners[name].checkpoint() == raw_before,
                "PROBE_MUTATION")
    return scores


def snapshot(learners, queries):
    """Engineering-only per-model cold exact restore, not owner-held custody."""
    state = {}
    for name in CANDIDATES:
        model = learners[name]
        raw = model.checkpoint()
        cold = PredictiveStateSplit.restore(raw, digest(raw))
        require(raw == cold.checkpoint(), "COLD_RESTORE")
        for views, action, s2 in queries:
            require(
                model.forecast(views, action, "residual", s2) ==
                cold.forecast(views, action, "residual", s2),
                "COLD_READOUT")
        state[name] = {"sha256": digest(raw), "bytes": len(raw),
                       "events": model.count}
    m = learners["controls"]
    raw = m.checkpoint()
    cold = MatchedHistoryControls.restore(raw, digest(raw))
    require(cold.checkpoint() == raw, "CONTROL_COLD")
    state["controls"] = {"sha256": digest(raw), "bytes": len(raw),
                         "events": m.count}
    return {"models": state, "a_probe_brier": fixed_old_probes(learners, queries)}


def decision(scores, snaps):
    failures = []
    for name, label in (("novel", "B"), ("a_return", "RETURN"),
                        ("pooled", "POOLED")):
        s = scores[name]
        best = min(CONTROLS, key=lambda arm: (s[arm]["two_stage"], arm))
        s["best_control"] = best
        s["candidate_minus_best"] = (s["direct"]["two_stage"] -
                                     s[best]["two_stage"])
        if name == "pooled" and s["candidate_minus_best"] > -0.005 + 1e-12:
            failures.append("POOLED_BEST_CONTROL")
        if name != "pooled" and s["candidate_minus_best"] > 0.010 + 1e-12:
            failures.append(label + "_NONINFERIORITY")
    anchor = snaps["a_anchor"]["a_probe_brier"]["direct"]
    for snapname, code in (("b_endpoint", "POST_B_OLD_A"),
                           ("a_return_endpoint", "RETURN_OLD_A")):
        if snaps[snapname]["a_probe_brier"]["direct"] - anchor > .020 + 1e-12:
            failures.append(code)
    if (scores["novel"]["direct"]["terminal"] -
            scores["novel"]["direct_sham"]["terminal"] > -.005 + 1e-12):
        failures.append("B_HISTORY_SHAM")
    return (("RD02_ENGINEERING_FEASIBLE" if not failures else
             "RD02_ENGINEERING_NO_GO"), failures)


def run(source_name):
    records = source(source_name)
    learners = {
        "direct": PredictiveStateSplit(reward_mode="direct"),
        "xor": PredictiveStateSplit(),
        "direct_sham": PredictiveStateSplit(reward_mode="direct", sham=True),
        "controls": MatchedHistoryControls(),
    }
    queries = None
    snaps = {}
    rows = []
    for t, event in enumerate(records):
        require(all(model.count == t for model in learners.values()),
                "SEQUENTIAL_WITNESSES")
        views, action, s2 = event["views"], event["action"], event["s2"]
        first, second = readouts(learners, views, action, s2)
        rows.append({"t": t, "id": event["id"], "views": views,
                     "action": action, "post": event["post"],
                     "s2": s2, "y": event["y"],
                     "first": first, "second": second})
        for learner in learners.values():
            learner.observe(event["id"], views, action, s2, event["y"],
                            event["post"])
        if t == 63:
            queries = tuple((r["views"], r["action"], r["s2"])
                            for r in records[:16])
            snaps["a_anchor"] = snapshot(learners, queries)
        elif t == 191:
            snaps["b_endpoint"] = snapshot(learners, queries)
        elif t == 255:
            snaps["a_return_endpoint"] = snapshot(learners, queries)
    scores = phase_scores(rows)
    classification, failures = decision(scores, snaps)
    pair_set = {
        (records[i - 1]["action"], records[i]["action"])
        for i in range(64, 192)
    }
    require(len(pair_set) == 16, "IDENTIFIABILITY_COVERAGE")
    require(len(snaps) == 3, "SNAPSHOT_COUNT")
    return {
        "schema": SCHEMA, "evidence_class": ENGINEERING_ONLY,
        "source_name": source_name,
        "source_sha256": digest(canonical(records)),
        "protocol_path": FROZEN_PROTOCOL,
        "registered_original_source_actions": 0,
        "source_events": N,
        "prior_current_action_pairs_b": len(pair_set),
        "phase_windows": {k: list(v) for k, v in WINDOWS.items()},
        "rows": rows,
        "phase_scores": scores,
        "snapshots": snaps,
        "status": classification,
        "failed_clauses": failures,
        "scientific_pass": False,
        "canonical_model_modified": False,
    }


def audit(raw):
    """Independent fixed-source/recalculated-metric audit; no source actions."""
    require(type(raw) is bytes and len(raw) < 2000000, "AUDIT_BYTES")
    try:
        doc = json.loads(raw.decode("ascii"))
        require(canonical(doc) == raw, "AUDIT_CANONICAL")
        require(type(doc) is dict and
                set(doc) == {"schema", "evidence_class", "source_name",
                             "source_sha256", "protocol_path",
                             "registered_original_source_actions",
                             "source_events", "prior_current_action_pairs_b",
                             "phase_windows", "rows", "phase_scores",
                             "snapshots", "status", "failed_clauses",
                             "scientific_pass", "canonical_model_modified"},
                "AUDIT_FIELDS")
        require(doc["schema"] == SCHEMA and
                doc["evidence_class"] == ENGINEERING_ONLY and
                doc["scientific_pass"] is False and
                doc["canonical_model_modified"] is False and
                doc["registered_original_source_actions"] == 0 and
                doc["protocol_path"] == FROZEN_PROTOCOL, "AUDIT_SCOPE")
        records = source(doc["source_name"])
        require(doc["source_sha256"] == digest(canonical(records)) and
                doc["source_events"] == len(doc["rows"]) == N and
                doc["prior_current_action_pairs_b"] == 16 and
                doc["phase_windows"] == {k: list(v) for k, v in WINDOWS.items()},
                "AUDIT_SOURCE")
        for t, (row, event) in enumerate(zip(doc["rows"], records)):
            require(type(row) is dict and
                    set(row) == {"t", "id", "views", "action", "post",
                                 "s2", "y", "first", "second"} and
                    row["t"] == t and row["id"] == event["id"] and
                    row["views"] == [list(v) for v in event["views"]] and
                    row["action"] == list(event["action"]) and
                    row["post"] == list(event["post"]) and
                    row["s2"] == event["s2"] and row["y"] == event["y"],
                    "AUDIT_EVENT")
            for kind in ("first", "second"):
                require(type(row[kind]) is dict and
                        set(row[kind]) == set(NAMES), "AUDIT_PREDICTION_SET")
                for p in row[kind].values():
                    require(type(p) is float and math.isfinite(p)
                            and 0 <= p <= 1, "AUDIT_PROBABILITY")
        recomputed = phase_scores(doc["rows"])
        for phase in WINDOWS:
            for name in NAMES:
                for key in ("two_stage", "terminal"):
                    require(abs(doc["phase_scores"][phase][name][key] -
                                recomputed[phase][name][key]) < 1e-12,
                            "AUDIT_BRIER")
        decision_result, failures = decision(recomputed, doc["snapshots"])
        require(doc["status"] == decision_result and
                doc["failed_clauses"] == failures, "AUDIT_DECISION")
        return {"schema": SCHEMA,
                "class": ENGINEERING_ONLY,
                "source_name": doc["source_name"],
                "receipt_sha256": digest(raw),
                "rows_verified": N, "controls": len(CONTROLS),
                "status": decision_result, "failed_clauses": failures,
                "scientific_pass": False}
    except (ValueError, TypeError, KeyError, IndexError, OverflowError,
            UnicodeError, ArithmeticError) as exc:
        raise ValueError("CAP04_RD02_AUDIT_REJECTED") from exc


def concise(report, proof):
    return {
        "source": report["source_name"],
        "status": report["status"],
        "failed_clauses": report["failed_clauses"],
        "source_sha256": report["source_sha256"],
        "receipt_sha256": proof["receipt_sha256"],
        "source_events": N,
        "observed_action_pairs_b": report["prior_current_action_pairs_b"],
        "probe_a_brier": {
            k: report["snapshots"][k]["a_probe_brier"]
            for k in ("a_anchor", "b_endpoint", "a_return_endpoint")
        },
        "phase_scores": {
            phase: {
                "direct_two_stage": report["phase_scores"][phase]
                    ["direct"]["two_stage"],
                "direct_terminal": report["phase_scores"][phase]
                    ["direct"]["terminal"],
                "xor_two_stage": report["phase_scores"][phase]
                    ["xor"]["two_stage"],
                "direct_sham_two_stage": report["phase_scores"][phase]
                    ["direct_sham"]["two_stage"],
                "best_control": report["phase_scores"][phase]
                    ["best_control"],
                "best_control_two_stage": report["phase_scores"][phase][
                    report["phase_scores"][phase]["best_control"]
                ]["two_stage"],
                "candidate_minus_best": report["phase_scores"][phase]
                    ["candidate_minus_best"],
            }
            for phase in WINDOWS
        },
        "checkpoint_sha256": {
            stage: report["snapshots"][stage]["models"]["direct"]["sha256"]
            for stage in ("a_anchor", "b_endpoint", "a_return_endpoint")
        },
        "scientific_pass": False,
        "accepted_native_changed": False,
    }


if __name__ == "__main__":
    for source_name in SOURCE_NAMES:
        result = run(source_name)
        proof = audit(canonical(result))
        print("CAP04_RD02_ENGINEERING=" +
              canonical(concise(result, proof)).decode("ascii"), flush=True)
