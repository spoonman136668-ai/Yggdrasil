"""RET03: two-action strictly staged public native causal forecast, engineering only.

Preserves one already-trained RET02 cumulative native+six-specialist learner,
its original immutable archived readout and its source custody. The adapter
never acts on an environment and never treats an event ID as owner consent.
No truth from a later stage enters an earlier-stage prediction.
"""
from __future__ import annotations

import json
from math import exp, isfinite

from yggdrasil.native_context_basis import canonical, digest, pin, require
from yggdrasil.native_temporal_context import (
    NativeTemporalContextReadout, MAX_NEW_EVENTS,
)

SCHEMA = "yggdrasil.ret03.staged-prequential-native-shadow.v1"
MAX_COLD_BYTES = 6_000_000


def _bit(value):
    require(type(value) is int and value in (0, 1), "RET03_PUBLIC_BIT")
    return value


def _views(views):
    require(type(views) is tuple and len(views) == 2 and
            all(type(v) is tuple and len(v) == 2 and len(v) == 2 and
                all(type(x) is int and x in (0, 1) for x in v)
                for v in views), "RET03_PUBLIC_VIEWS")
    return views


def _uniquekeys(pairs):
    result = {}
    for key, val in pairs:
        require(key not in result, "RET03_DUPLICATE_JSON_FIELD")
        result[key] = val
    return result


class StagedTemporalReadout:
    """An opt-in timing boundary around the unmodified RET02 learner.

    begin: current public observations + first chosen action -> P(s2)
    record_transition: public witnessed s2 (no native update)
    choose_second: second chosen action -> P(y | s2, actions)
    complete: terminal witnessed y -> original single native admission/update

    There is at most ONE pending source, with no implicit cancellation or
    re-use. For independently verified source permission see issue #426.
    """

    def __init__(self, archived_raw, latest_raw):
        self.archive_raw = archived_raw
        self.initial_raw = latest_raw
        self.native = NativeTemporalContextReadout(archived_raw, latest_raw)
        self.pending = None

    def _weight(self, views, x1, x2):
        # A neutral dummy outcome is supplied to RET02's read-only feature
        # builder, which explicitly ignores current s2/y. x2 is set to 0 at
        # the first stage because the real second action is still unknown.
        row = {"s1": views[0][0], "x1": x1,
               "s2": 0, "x2": x2, "y": 0}
        f = self.native.features(views, row)
        z = sum(w*v for w, v in zip(self.native.weights, f))
        require(isfinite(z), "RET03_WEIGHT_NONFINITE")
        w = 1/(1+exp(-max(-30., min(30., z))))
        return max(1/32, min(31/32, w))

    def begin(self, source_id, views, x1):
        """Return first-stage forecast BEFORE s2, x2, or reward exist here."""
        require(self.pending is None, "RET03_PENDING_UNRESOLVED")
        require(pin(source_id), "RET03_NEW_EVENT_ID")
        _views(views)
        _bit(x1)
        require(len(self.native.events) < MAX_NEW_EVENTS,
                "RET03_NEW_SOURCE_BUDGET")
        require(source_id not in
                self.native.reader.current.original.base.native._ids and
                not any(e["source_id"] == source_id for e in self.native.events),
                "RET03_SOURCE_ID_ALREADY_CONSUMED")
        archived = self.native.reader.archived.base.native
        current = self.native.reader.current.original.base.native
        a = float(archived.context_forecast(views[0], x1))
        b = float(current.context_forecast(views[0], x1))
        require(all(isfinite(p) and 0 <= p <= 1 for p in (a, b)),
                "RET03_TRANSITION_PROB")
        w = self._weight(views, x1, 0)
        pred = {"archive": a, "live": b,
                "temporal": w*a+(1-w)*b, "archive_weight": w}
        self.pending = {"source_id": source_id,
                        "views": [list(v) for v in views],
                        "x1": x1, "stage": "first",
                        "transition": pred}
        return dict(pred)

    def record_transition(self, source_id, observed_s2):
        """Admit a public first-stage consequence; DO NOT update weights."""
        require(self.pending is not None and
                self.pending["stage"] == "first" and
                source_id == self.pending["source_id"],
                "RET03_TRANSITION_SEQUENCE")
        _bit(observed_s2)
        self.pending["observed_s2"] = observed_s2
        self.pending["stage"] = "transition"
        return None

    def choose_second(self, source_id, x2):
        """Return P(y) after witnessed s2 and chosen x2, but BEFORE y."""
        require(self.pending is not None and
                self.pending["stage"] == "transition" and
                source_id == self.pending["source_id"],
                "RET03_SECOND_ACTION_SEQUENCE")
        _bit(x2)
        pending = self.pending
        views = tuple(tuple(v) for v in pending["views"])
        x1, s2 = pending["x1"], pending["observed_s2"]
        archived = self.native.reader.archived.base.native
        current = self.native.reader.current.original.base.native
        a = float(archived.context_forecast(views[0], x1, s2, x2))
        b = float(current.context_forecast(views[0], x1, s2, x2))
        require(all(isfinite(p) and 0 <= p <= 1 for p in (a, b)),
                "RET03_REWARD_PROB")
        w = self._weight(views, x1, x2)
        pred = {"archive": a, "live": b,
                "temporal": w*a+(1-w)*b, "archive_weight": w}
        pending["x2"] = x2
        pending["reward"] = pred
        pending["stage"] = "second"
        return dict(pred)

    def complete(self, source_id, observed_y):
        """Only the terminal witness admits the FULL two-action native event."""
        require(self.pending is not None and
                self.pending["stage"] == "second" and
                self.pending["source_id"] == source_id,
                "RET03_TERMINAL_SEQUENCE")
        _bit(observed_y)
        old = self.pending
        views = tuple(tuple(v) for v in old["views"])
        row = {"s1": views[0][0], "x1": old["x1"],
               "s2": old["observed_s2"], "x2": old["x2"],
               "y": observed_y}
        # This original RET02 admission performs its old valid replay and
        # then learns one update. No forecast made in begin/choose_second
        # could have accessed this not-yet-observed reward.
        result = self.native.observe(source_id, views, row)
        require(result is not None, "RET03_REPEATED_NATIVE_SOURCE")
        self.pending = None
        return {"transition": dict(old["transition"]),
                "reward": dict(old["reward"])}

    def checkpoint(self):
        original = self.native.checkpoint()
        data = {"schema": SCHEMA,
                "archive_sha256": digest(self.archive_raw),
                "initial_native_sha256": digest(self.initial_raw),
                "native_sha256": digest(original),
                "native_ascii": original.decode("ascii"),
                "pending": self.pending,
                "scientific_pass": False,
                "accepted_native": False}
        raw = canonical(data)
        require(len(raw) <= MAX_COLD_BYTES, "RET03_COLD_CAP")
        return raw

    @classmethod
    def restore(cls, raw, expected_sha256, archived_raw, latest_raw):
        require(type(raw) is bytes and len(raw) <= MAX_COLD_BYTES and
                pin(expected_sha256) and digest(raw) == expected_sha256,
                "RET03_CHECKPOINT_PIN")
        try:
            data = json.loads(raw.decode("ascii"), object_pairs_hook=_uniquekeys)
            require(type(data) is dict and set(data) ==
                    {"schema", "archive_sha256", "initial_native_sha256",
                     "native_sha256", "native_ascii", "pending",
                     "scientific_pass", "accepted_native"} and
                    data["schema"] == SCHEMA and
                    data["archive_sha256"] == digest(archived_raw) and
                    data["initial_native_sha256"] == digest(latest_raw) and
                    data["scientific_pass"] is False and
                    data["accepted_native"] is False and
                    canonical(data) == raw, "RET03_COLD_SHAPE")
            original = data["native_ascii"].encode("ascii")
            require(digest(original) == data["native_sha256"],
                    "RET03_NATIVE_BYTES")
            value = cls(archived_raw, latest_raw)
            value.native = NativeTemporalContextReadout.restore(
                original, data["native_sha256"], archived_raw, latest_raw)
            pend = data["pending"]
            if pend is not None:
                require(type(pend) is dict and
                        {"source_id", "views", "x1", "stage", "transition"}
                        <= set(pend), "RET03_PENDING_FIELDS")
                identifier = pend["source_id"]
                views = tuple(tuple(v) for v in pend["views"])
                value.begin(identifier, views, pend["x1"])
                if pend["stage"] in ("transition", "second"):
                    value.record_transition(identifier, pend["observed_s2"])
                if pend["stage"] == "second":
                    value.choose_second(identifier, pend["x2"])
                require(value.pending == pend, "RET03_PENDING_REPLAY")
            require(value.checkpoint() == raw,
                    "RET03_EXACT_COLD_RECONSTRUCTION")
            return value
        except (ValueError, TypeError, AttributeError, KeyError,
                IndexError, UnicodeError, OverflowError) as exc:
            raise ValueError("YGG_RET03_COLD_RESTORE_REJECTED") from exc
