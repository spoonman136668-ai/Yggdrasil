"""RET02: opt-in learned temporal context for the existing Yggdrasil reader.

A small online readout of past *observed* public action/consequence history.
The sole cumulative NativeFutureStateLearner and pinned archived reader are
the same unmodified RET01 objects. This module never executes source actions,
uses hidden domain labels, or claims held scientific learning.
"""
from __future__ import annotations

import json
from math import exp, isfinite

from yggdrasil.native_context_basis import canonical, digest, pin, require
from yggdrasil.native_readout_retention import (
    ArchivedEvidenceReadout, _public, MAX_NEW_EVENTS,
)

SCHEMA = "yggdrasil.ret02.native-temporal-context-shadow.v1"
WIDTH = 17
HISTORY = 2
LR = 0.12
DECAY = 0.001
MAX_WEIGHT = 8.0
MAX_BYTES = 3_000_000


def _bits(values):
    return tuple(2 * x - 1 for x in values)


def _unique_pairs(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, "RET02_DUPLICATE_CHECKPOINT_FIELD")
        out[key] = value
    return out


class NativeTemporalContextReadout:
    """Cumulative native learner plus an opt-in, *unqualified* readout head.

    The native learner's public source ledger and all specialist weights are
    updated ONLY through RET01's original witness admission path. The small
    temporal readout sees prior public consequences and learns AFTER the next
    actual observed consequence; it never modifies the native source policy.
    """

    def __init__(self, archived_raw, latest_raw):
        require(type(archived_raw) is bytes and type(latest_raw) is bytes,
                "RET02_INPUT_CHECKPOINT_TYPE")
        self.archived_raw = archived_raw
        self.latest_raw = latest_raw
        self.archived_sha = digest(archived_raw)
        self.latest_sha = digest(latest_raw)
        self.reader = ArchivedEvidenceReadout(archived_raw, latest_raw)
        # Archive prior = sigmoid(log(1/7)). Exact cold restores use the
        # serialized double (do not infer trained source or hidden phase).
        self.weights = [-1.9459101490553132] + [0.0] * (WIDTH - 1)
        self.events = []

    def features(self, views, row, *, no_history=False):
        """17 numeric input features; never reads current s2/y truth.

        Uses a neutral s2=0 solely for a second-step disagreement feature,
        because the original RET01 baseline's reward readout conditions on
        actual s2. The latter remains a separate inherited evaluation caveat.
        """
        _public(views, row)
        require(type(no_history) is bool, "RET02_ABLATION_TYPE")
        present = [x for pair in views for x in pair]
        result = [1.0, *_bits(present), *_bits((row["x1"], row["x2"]))]
        recent = self.events[-HISTORY:]
        for step in range(HISTORY):
            if no_history or step >= len(recent):
                result.extend([0.0] * 4)
            else:
                old = recent[-1-step]["row"]
                result.extend(v/(step+1) for v in
                              _bits((old["x1"], old["s2"], old["x2"], old["y"])))
        view = views[0]
        old = self.reader.archived.base.native
        new = self.reader.current.original.base.native
        a = float(old.context_forecast(view, row["x1"]))
        b = float(new.context_forecast(view, row["x1"]))
        # Use a fixed, outcome-independent hypothetical second-stage state
        # for the FEATURE, not the actual current observed s2 label.
        c = float(old.context_forecast(view, row["x1"], 0, row["x2"]))
        d = float(new.context_forecast(view, row["x1"], 0, row["x2"]))
        result.extend([a - b, c - d])
        require(len(result) == WIDTH and
                all(isfinite(x) and abs(x) <= 1.0 for x in result),
                "RET02_FEATURE_RANGE")
        return tuple(result)

    def forecast(self, views, row, *, no_history=False):
        _public(views, row)
        x = self.features(views, row, no_history=no_history)
        raw = self.reader.forecast(views, row)
        z = sum(w * v for w, v in zip(self.weights, x))
        require(isfinite(z), "RET02_LOGIT_NONFINITE")
        p = 1.0 / (1.0 + exp(-max(-30.0, min(30.0, z))))
        p = max(1/32, min(31/32, p))
        mixed = tuple(p * a + (1 - p) * b for a, b in
                      zip(raw["archive"], raw["live"]))
        require(all(isfinite(v) and 0 <= v <= 1 for v in mixed),
                "RET02_PROBABILITY_RANGE")
        return {"archive": raw["archive"], "live": raw["live"],
                "ret01_gate": raw["gate"], "temporal": mixed,
                "weight_archived": p}

    def observe(self, identifier, views, row):
        """One previously unseen *public* witness; learned credit AFTER reveal.

        Source IDs identify immutable rows but do NOT authenticate an original
        source owner. This is opt-in source-only engineering, no source actor.
        """
        require(pin(identifier), "RET02_PUBLIC_SOURCE_ID")
        _public(views, row)
        event = {"source_id": identifier,
                 "views": [list(v) for v in views], "row": dict(row)}
        for seen in self.events:
            if seen["source_id"] == identifier:
                require(seen == event, "RET02_CONFLICTING_PUBLIC_WITNESS")
                return None
        require(identifier not in self.reader.current.original.base.native._ids,
                "RET02_OLD_SOURCE_REUSE")
        require(len(self.events) < MAX_NEW_EVENTS, "RET02_EVENT_BUDGET")
        x = self.features(views, row)
        pred = self.forecast(views, row)
        # Crucial order: only after the EXISTING native readout has accepted
        # and trained on the actual public witness may the optional head fit.
        actual = self.reader.observe(identifier, views, row)
        require(actual is not None, "RET02_NATIVE_ADMISSION_REJECTED")
        archive, live, mixed = pred["archive"], pred["live"], pred["temporal"]
        y = (row["s2"], row["y"])
        d_brier_dw = sum((mixed[i] - y[i]) * (archive[i] - live[i])
                         for i in range(2))
        w = pred["weight_archived"]
        grad = d_brier_dw * w * (1-w)
        next_weights = []
        for i, (old_weight, v) in enumerate(zip(self.weights, x)):
            updated = old_weight - LR * (grad*v +
                                          (DECAY*old_weight if i else 0.0))
            next_weights.append(max(-MAX_WEIGHT, min(MAX_WEIGHT, updated)))
        require(len(next_weights) == WIDTH and
                all(isfinite(x) for x in next_weights),
                "RET02_LEARNED_WEIGHT_FINITE")
        self.weights = next_weights
        self.events.append(event)
        return pred

    def checkpoint(self):
        base = self.reader.checkpoint()
        data = {"schema": SCHEMA, "archive_sha256": self.archived_sha,
                "initial_native_sha256": self.latest_sha,
                "base_sha256": digest(base),
                "base_ascii": base.decode("ascii"),
                "weights": list(self.weights), "events": self.events,
                "accepted_native": False, "scientific_pass": False}
        raw = canonical(data)
        require(len(raw) <= MAX_BYTES, "RET02_COLD_BYTES_LIMIT")
        return raw

    @classmethod
    def restore(cls, raw, expected_sha256, archived_raw, latest_raw):
        require(type(raw) is bytes and len(raw) <= MAX_BYTES and
                pin(expected_sha256) and digest(raw) == expected_sha256,
                "RET02_COLD_SOURCE_PIN")
        try:
            data = json.loads(raw.decode("ascii"), object_pairs_hook=_unique_pairs)
            require(type(data) is dict and set(data) == {
                "schema", "archive_sha256", "initial_native_sha256",
                "base_sha256", "base_ascii", "weights", "events",
                "accepted_native", "scientific_pass"
            } and data["schema"] == SCHEMA and
                    data["archive_sha256"] == digest(archived_raw) and
                    data["initial_native_sha256"] == digest(latest_raw) and
                    data["accepted_native"] is False and
                    data["scientific_pass"] is False and
                    type(data["weights"]) is list and
                    len(data["weights"]) == WIDTH and
                    all(type(w) is float and isfinite(w) and
                        abs(w) <= MAX_WEIGHT for w in data["weights"]) and
                    type(data["events"]) is list and
                    len(data["events"]) <= MAX_NEW_EVENTS and
                    canonical(data) == raw, "RET02_COLD_CONTRACT")
            state = cls(archived_raw, latest_raw)
            for event in data["events"]:
                require(type(event) is dict and set(event) ==
                        {"source_id", "views", "row"}, "RET02_COLD_EVENT")
                state.observe(event["source_id"],
                              tuple(tuple(x) for x in event["views"]),
                              event["row"])
            current = state.reader.checkpoint()
            require(digest(current) == data["base_sha256"] and
                    current.decode("ascii") == data["base_ascii"] and
                    state.weights == data["weights"] and
                    state.checkpoint() == raw,
                    "RET02_WITNESSED_NATIVE_COLD_REPLAY")
            return state
        except (ValueError, TypeError, KeyError, UnicodeError, OverflowError,
                AttributeError, IndexError) as exc:
            raise ValueError("YGG_RET02_COLD_RESTORE_REJECTED") from exc
