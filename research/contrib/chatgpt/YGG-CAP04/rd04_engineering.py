"""RD04 prospective *synthetic* A-B-A research comparison, never science.

This source was frozen before implementation in RD04-FROZEN-ROUTER-EXPERIMENT.md.
All readouts receive the exact same observed public action-consequence stream.
No canonical model, original first-use, registered DEV source or runner owner.
"""
from __future__ import annotations
import hashlib
import json
import math
import time

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_predictive_state_split import (
    PredictiveStateSplit, FEATURES, RECENT_WINDOW, RECENT_LOG_GATE,
)
from yggdrasil.native_predictive_state_controls import (
    MatchedHistoryControls, ARMS as CONTROL_NAMES,
)

SCHEMA = "yggdrasil.cap04.rd04.synthetic-source.recent32.v1"
SOURCE_IDS = ("cap04-rd04-source-a", "cap04-rd04-source-b")
ARMS = ((0, 0), (0, 1), (1, 0), (1, 1))
MODEL_NAMES = ("recent32", "recent32_sham", "direct", "xor")
ALL_ARMS = MODEL_NAMES + CONTROL_NAMES
PHASES = {"novel": (96, 192), "a_return": (192, 256),
          "pooled": (96, 256)}
N = 256
FROZEN_PROTOCOL = "research/contrib/chatgpt/YGG-CAP04/RD04-FROZEN-ROUTER-EXPERIMENT.md"


def require(ok, code):
    if not ok:
        raise ValueError("CAP04_RD04_" + code)


def byte(name):
    return hashlib.sha256(name.encode("ascii")).digest()[0]


def source(name):
    require(type(name) is str and name in SOURCE_IDS, "SOURCE_ID")
    u, v, w = (byte(f"cap04/rd04/{name}/start/{i}") & 1
               for i in range(3))
    previous_action = (0, 0)
    rows = []
    for t in range(N):
        views = ((u, v), (v, w))
        action = ARMS[byte(f"cap04/rd04/{name}/{t}/action") & 3]
        s2 = byte(f"cap04/rd04/{name}/{t}/intermediate") & 1
        history_bit = previous_action[int(name == SOURCE_IDS[1])]
        y = (s2 ^ history_bit) if 64 <= t < 192 else s2
        post = (v ^ action[0], s2, w ^ action[1])
        ident = hashlib.sha256(
            f"cap04/rd04/{name}/witness/{t}".encode("ascii")
        ).hexdigest()
        rows.append({"id": ident, "views": views, "action": action,
                     "s2": s2, "y": y, "post": post})
        u, v, w = post
        previous_action = action
    require(len(rows) == N and len({r["id"] for r in rows}) == N,
            "SOURCE_UNIQUE")
    return tuple(rows)


def identifiability(records):
    pairs = set()
    cells = {}
    for t in range(96, 192):
        previous, row = records[t - 1]["action"], records[t]
        pairs.add((previous, row["action"]))
        key = (row["views"], row["action"], row["s2"])
        cells.setdefault(key, set()).add(previous)
    contrasts = sum(len(v) >= 2 for v in cells.values())
    require(len(pairs) == 16 and contrasts >= 4,
            "SOURCE_IDENTIFIABILITY_INVALID")
    return {"ordered_prior_current_pairs": len(pairs),
            "contrasting_public_cells": contrasts}


def probability(value):
    require(type(value) is float and math.isfinite(value)
            and 0 <= value <= 1, "PREDICTION")
    return value


def models():
    return {
        "recent32": PredictiveStateSplit(
            reward_mode="direct", routing_mode="recent32"),
        "recent32_sham": PredictiveStateSplit(
            reward_mode="direct", routing_mode="recent32", sham=True),
        "direct": PredictiveStateSplit(reward_mode="direct"),
        "xor": PredictiveStateSplit(),
        "controls": MatchedHistoryControls(),
    }


def forecast_all(learners, event):
    views, action, s2 = event["views"], event["action"], event["s2"]
    pins = {k: model.checkpoint() for k, model in learners.items()}
    first = {k: probability(learners[k].forecast(
        views, action, "transition")) for k in MODEL_NAMES}
    first.update({k: probability(v) for k, v in learners["controls"]
                 .forecast(views, action, "transition").items()})
    second = {k: probability(learners[k].forecast(
        views, action, "residual", s2)) for k in MODEL_NAMES}
    second.update({k: probability(v) for k, v in learners["controls"]
                  .forecast(views, action, "residual", s2).items()})
    require(set(first) == set(second) == set(ALL_ARMS), "ALL_ARMS")
    require(pins == {k: model.checkpoint() for k, model in learners.items()},
            "PREQUENTIAL_MUTATION")
    chosen = {
        k: (learners[k].selected_feature("residual") or "none")
        for k in ("recent32", "recent32_sham")
    }
    return first, second, chosen


def old_skill_queries(learners, fixed):
    result = {}
    for k in ("recent32", "direct", "xor"):
        model = learners[k]
        before = model.checkpoint()
        result[k] = math.fsum(
            (model.forecast(views, action, "residual", s2) - s2) ** 2
            for views, action, s2 in fixed
        ) / len(fixed)
        require(model.checkpoint() == before, "OLD_PROBE_MUTATION")
    return result


def checkpoint(learners, fixed):
    pinning = {}
    for name, model in learners.items():
        raw = model.checkpoint()
        cls = MatchedHistoryControls if name == "controls" else PredictiveStateSplit
        cold = cls.restore(raw, digest(raw))
        require(raw == cold.checkpoint(), "COLD_PIN")
        for views, action, s2 in fixed:
            if name == "controls":
                for kind in ("transition", "residual"):
                    a = model.forecast(views, action, kind,
                                       None if kind == "transition" else s2)
                    b = cold.forecast(views, action, kind,
                                     None if kind == "transition" else s2)
                    require(a == b, "COLD_CONTROL_READ")
            else:
                require(model.forecast(views, action, "residual", s2) ==
                        cold.forecast(views, action, "residual", s2),
                        "COLD_SHADOW_READ")
        pinning[name] = {"sha256": digest(raw), "bytes": len(raw),
                         "events": model.count}
    return {"models": pinning, "old_probe_brier": old_skill_queries(learners, fixed)}


def metrics(rows):
    require(len(rows) == N, "ROW_COUNT")
    result = {}
    for phase, (start, stop) in PHASES.items():
        window = rows[start:stop]
        part = {}
        for name in ALL_ARMS:
            first = math.fsum((row["first"][name] - row["s2"]) ** 2
                              for row in window) / len(window)
            terminal = math.fsum((row["second"][name] - row["y"]) ** 2
                                 for row in window) / len(window)
            part[name] = {"two_stage": (first + terminal) / 2,
                          "terminal": terminal}
        for name in ("recent32", "recent32_sham"):
            part[name]["feature_count"] = {
                feat: sum(row["feature"][name] == feat for row in window)
                for feat in ("none",) + FEATURES
            }
            require(sum(part[name]["feature_count"].values()) ==
                    len(window), "FEATURE_COUNT")
        result[phase] = part
    return result


def decide(measures, snaps):
    failure = []
    for phase, code in (("novel", "NOVEL"), ("a_return", "RETURN"),
                        ("pooled", "POOLED")):
        m = measures[phase]
        best = min(CONTROL_NAMES, key=lambda k: (m[k]["two_stage"], k))
        m["best_control"] = best
        delta = m["recent32"]["two_stage"] - m[best]["two_stage"]
        m["candidate_minus_best"] = delta
        if phase == "pooled" and delta > -0.005 + 1e-12:
            failure.append("POOLED_CONTROL")
        if phase != "pooled" and delta > 0.010 + 1e-12:
            failure.append(code + "_NONINFERIORITY")
    novel = measures["novel"]
    pooled = measures["pooled"]
    if (novel["recent32"]["terminal"] -
            novel["recent32_sham"]["terminal"] > -0.005 + 1e-12):
        failure.append("HISTORY_SHAM")
    if (pooled["recent32"]["two_stage"] -
            pooled["direct"]["two_stage"] > -0.005 + 1e-12):
        failure.append("CUMULATIVE_ABLATION")
    anchor = snaps["a_anchor"]["old_probe_brier"]["recent32"]
    for stage, name in (("b_endpoint", "POST_B_OLD_A"),
                        ("a_return_endpoint", "RETURN_OLD_A")):
        if snaps[stage]["old_probe_brier"]["recent32"] - anchor > .020 + 1e-12:
            failure.append(name)
    if novel["recent32"]["feature_count"]["previous_pair"] < 16:
        failure.append("PREVIOUS_PAIR_ACTIVATION")
    return ("RD04_ENGINEERING_FEASIBLE" if not failure else
            "RD04_ENGINEERING_NO_GO"), failure


def run(name):
    records = source(name)
    source_properties = identifiability(records)
    learners = models()
    rows = []
    snaps = {}
    probes = ()
    for t, event in enumerate(records):
        require(all(model.count == t for model in learners.values()),
                "PUBLIC_CLOCK")
        first, second, feature = forecast_all(learners, event)
        rows.append({"t": t, "id": event["id"], "views": event["views"],
                     "action": event["action"], "s2": event["s2"],
                     "y": event["y"], "post": event["post"],
                     "first": first, "second": second,
                     "feature": feature})
        for model in learners.values():
            model.observe(event["id"], event["views"], event["action"],
                          event["s2"], event["y"], event["post"])
        if t == 63:
            probes = tuple((r["views"], r["action"], r["s2"])
                           for r in records[:16])
            snaps["a_anchor"] = checkpoint(learners, probes)
        elif t == 191:
            snaps["b_endpoint"] = checkpoint(learners, probes)
        elif t == 255:
            snaps["a_return_endpoint"] = checkpoint(learners, probes)
    measure = metrics(rows)
    outcome, failed = decide(measure, snaps)
    return {"schema": SCHEMA, "evidence_class": "SYNTHETIC_ENGINEERING_ONLY",
            "source": name, "source_sha256": digest(canonical(records)),
            "source_events": N, "source_properties": source_properties,
            "frozen_protocol": FROZEN_PROTOCOL,
            "original_source_actions": 0,
            "phase_bounds": {k: list(v) for k, v in PHASES.items()},
            "rows": rows, "phase_metrics": measure,
            "snapshots": snaps,
            "status": outcome, "failed_clauses": failed,
            "scientific_pass": False, "accepted_native_modified": False}


def audit(raw):
    """Independent deterministic reproduction, rejects altered source or score."""
    require(type(raw) is bytes and len(raw) < 2000000, "AUDIT_SIZE")
    try:
        doc = json.loads(raw.decode("ascii"))
        require(canonical(doc) == raw and type(doc) is dict,
                "AUDIT_CANONICAL")
        require(set(doc) == {"schema", "evidence_class", "source",
                            "source_sha256", "source_events",
                            "source_properties", "frozen_protocol",
                            "original_source_actions", "phase_bounds",
                            "rows", "phase_metrics", "snapshots", "status",
                            "failed_clauses", "scientific_pass",
                            "accepted_native_modified"}, "AUDIT_FIELDS")
        require(doc["schema"] == SCHEMA
                and doc["evidence_class"] == "SYNTHETIC_ENGINEERING_ONLY"
                and doc["original_source_actions"] == 0
                and doc["scientific_pass"] is False
                and doc["accepted_native_modified"] is False
                and doc["frozen_protocol"] == FROZEN_PROTOCOL,
                "AUDIT_SCOPE")
        ref = run(doc["source"])
        require(raw == canonical(ref), "AUDIT_EXACT_REPLAY")
        return {"source": doc["source"], "source_sha256": doc["source_sha256"],
                "receipt_sha256": digest(raw), "status": doc["status"],
                "failed_clauses": doc["failed_clauses"],
                "events": N, "scientific_pass": False}
    except (ValueError, TypeError, KeyError, IndexError,
            UnicodeError, ArithmeticError, OverflowError) as err:
        raise ValueError("CAP04_RD04_AUDIT_REJECTED") from err


def concise(doc, checked):
    def phase(name):
        s = doc["phase_metrics"][name]
        best = s["best_control"]
        return {"candidate": s["recent32"]["two_stage"],
                "candidate_terminal": s["recent32"]["terminal"],
                "sham_terminal": s["recent32_sham"]["terminal"],
                "cumulative": s["direct"]["two_stage"],
                "best_control": best,
                "best_control_brier": s[best]["two_stage"],
                "candidate_minus_best": s["candidate_minus_best"],
                "features": s["recent32"].get("feature_count", {})}
    return {"source": doc["source"], "source_sha256": doc["source_sha256"],
            "receipt_sha256": checked["receipt_sha256"],
            "source_properties": doc["source_properties"],
            "novel": phase("novel"),
            "a_return": phase("a_return"),
            "pooled": phase("pooled"),
            "old_a_probe": {name: doc["snapshots"][name]["old_probe_brier"]
                            for name in ("a_anchor", "b_endpoint",
                                         "a_return_endpoint")},
            "checkpoint_sha256": {
                k: doc["snapshots"][k]["models"]["recent32"]["sha256"]
                for k in ("a_anchor", "b_endpoint", "a_return_endpoint")},
            "status": doc["status"], "failed_clauses": doc["failed_clauses"],
            "scientific_pass": False, "accepted_native_modified": False}


if __name__ == "__main__":
    for name in SOURCE_IDS:
        start = time.perf_counter()
        doc = run(name)
        raw = canonical(doc)
        checked = audit(raw)
        elapsed = time.perf_counter() - start
        print("CAP04_RD04_RESULT=" +
              canonical(concise(doc, checked)).decode("ascii"), flush=True)
        print("CAP04_RD04_WALL_SECONDS=" +
              canonical({"source": name, "seconds": round(elapsed, 6),
                         "scope": "run_plus_exact_replay_audit"}).decode("ascii"),
              flush=True)
