"""O22-Q: minimal independent source-public action/observation Beta controls.

Observes only authenticated chosen original action and its returned next state.
No native model import and no MiniGrid reset/step. Results are INTERNAL FIT.
"""
from __future__ import annotations
import hashlib
import json
import math

SCHEMA = "optimizer.o22q.parsimonious-beta.v1"
MAX_EVENTS = 4096
MAX_KEYS = 64


def _input(b, a):
    if (type(b) is not list or len(b) != 6 or
        any(type(v) is not int for v in b) or
        not (0 <= b[0] <= 64 and 0 <= b[1] <= 64 and
             b[2] in range(4) and 0 <= b[3] <= 64 and
             0 <= b[4] <= 64 and b[5] in (0, 1)) or
        type(a) is not int or a not in (0, 1, 2)):
        raise ValueError("O22Q_ONLY_LEGAL_ORIGINAL_PUBLIC_INPUT")
    return b


def _outcome(b, a, after):
    _input(b, a)
    _input(after, a)
    return (after[5], int((b[0], b[1]) != (after[0], after[1])))


class MinimalSourceBeta:
    """A separately programmed conditional empirical Bernoulli model."""

    def __init__(self, mode="action_front"):
        if mode not in ("action_front", "action", "front"):
            raise ValueError("O22Q_MODE")
        self.mode = mode
        self.counts = {}
        self.events = 0
        self.actions = {"0": 0, "1": 0, "2": 0}

    def _key(self, before, action):
        _input(before, action)
        if self.mode == "action_front":
            return str(action) + ":" + str(before[5])
        if self.mode == "action":
            return str(action)
        return str(before[5])

    def predict(self, before, action):
        k = self._key(before, action)
        total, positive_front, positive_move = self.counts.get(k, (0, 0, 0))
        return ((1 + positive_front) / (2 + total),
                (1 + positive_move) / (2 + total))

    def learn(self, before, action, after):
        labels = _outcome(before, action, after)
        if self.events >= MAX_EVENTS:
            raise ValueError("O22Q_FIT_EVENT_CAP")
        k = self._key(before, action)
        total, front, move = self.counts.get(k, (0, 0, 0))
        if total == 0 and len(self.counts) >= MAX_KEYS:
            raise ValueError("O22Q_CONTEXT_CAP")
        self.counts[k] = [total + 1, front + labels[0], move + labels[1]]
        self.events += 1
        self.actions[str(action)] += 1

    def checkpoint(self):
        data = {"schema": SCHEMA, "mode": self.mode, "counts": self.counts,
                "events": self.events, "actions": self.actions}
        text = json.dumps(data, sort_keys=True, separators=(",", ":"),
                          allow_nan=False).encode()
        return json.dumps({"body": data, "sha256": hashlib.sha256(text).hexdigest()},
                          sort_keys=True, separators=(",", ":")).encode()

    @classmethod
    def restore(cls, wire):
        try:
            if type(wire) is not bytes or not 0 < len(wire) < 32000:
                raise ValueError("O22Q_BAD_CHECKPOINT_BYTES")
            v = json.loads(wire)
            if type(v) is not dict or set(v) != {"body", "sha256"}:
                raise ValueError("O22Q_BAD_CHECKPOINT_ENVELOPE")
            data = v["body"]
            if type(data) is not dict or set(data) != {
                "schema", "mode", "counts", "events", "actions"
            } or data["schema"] != SCHEMA:
                raise ValueError("O22Q_BAD_CHECKPOINT_SCHEMA")
            raw = json.dumps(data, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode()
            if hashlib.sha256(raw).hexdigest() != v["sha256"]:
                raise ValueError("O22Q_BAD_CHECKPOINT_HASH")
            out = cls(data["mode"])
            if (type(data["events"]) is not int or
                not 0 <= data["events"] <= MAX_EVENTS or
                type(data["actions"]) is not dict or
                set(data["actions"]) != {"0", "1", "2"} or
                any(type(x) is not int or x < 0 for x in data["actions"].values()) or
                sum(data["actions"].values()) != data["events"] or
                type(data["counts"]) is not dict or
                len(data["counts"]) > MAX_KEYS):
                raise ValueError("O22Q_CHECKPOINT_ACTION_COUNTS")
            total_rows = 0
            for key, counts in data["counts"].items():
                if (type(key) is not str or len(key) > 16 or
                    type(counts) is not list or len(counts) != 3 or
                    any(type(v) is not int or v < 0 or v > MAX_EVENTS for v in counts) or
                    counts[0] < 1 or counts[1] > counts[0] or counts[2] > counts[0]):
                    raise ValueError("O22Q_CHECKPOINT_CONTEXT_COUNTS")
                if out.mode == "action_front" and key not in (
                    "0:0", "0:1", "1:0", "1:1", "2:0", "2:1"):
                    raise ValueError("O22Q_CONTEXT_KEY")
                if out.mode == "action" and key not in ("0", "1", "2"):
                    raise ValueError("O22Q_CONTEXT_KEY")
                if out.mode == "front" and key not in ("0", "1"):
                    raise ValueError("O22Q_CONTEXT_KEY")
                total_rows += counts[0]
            if total_rows != data["events"]:
                raise ValueError("O22Q_EVENTS_DRIFT")
            out.actions = data["actions"]
            out.counts = data["counts"]
            out.events = data["events"]
            return out
        except (TypeError, ValueError, KeyError, OverflowError) as e:
            raise ValueError("O22Q_UNTRUSTED_CHECKPOINT") from e
