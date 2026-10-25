"""O22-P FIT-only source-public action-effect learners, NOT an original R2 replacement.

NativePlasticCells: bounded local slow/fast action-conditioned error-driven cells.
BayesianEffects: independently coded conventional smoothed conditional counts.
Only public six-field before/action/returned-after from source FIT are permitted.
"""
from __future__ import annotations
import hashlib
import json
import math

MAX_EVENTS = 4096
MAX_BYTES = 180000
LABELS = ("front_blocked_after", "physical_translation")


def _public(before, action, after):
    if (type(before) is not list or type(after) is not list or
        len(before) != 6 or len(after) != 6 or
        any(type(x) is not int for x in before + after) or
        not all(0 <= x <= 64 for x in before[:5] + after[:5]) or
        before[2] not in (0, 1, 2, 3) or after[2] not in (0, 1, 2, 3) or
        before[5] not in (0, 1) or after[5] not in (0, 1) or
        type(action) is not int or action not in (0, 1, 2)):
        raise ValueError("O22P_PUBLIC_ACTION_OR_RETURN_INVALID")
    return (after[5], int((before[0], before[1]) != (after[0], after[1])))


def _features(b, a):
    if not (type(b) is list and len(b) == 6 and all(type(x) is int for x in b)
            and b[2] in range(4) and b[5] in (0, 1)
            and type(a) is int and a in (0, 1, 2)):
        raise ValueError("O22P_SOURCE_PUBLIC_FEATURES")
    return (f"a{a}", f"front{b[5]}", f"heading{b[2]}",
            f"action{a}-front{b[5]}", f"action{a}-heading{b[2]}")


def _clip(v):
    return max(0.001, min(0.999, v))


def _wire(body):
    data = json.dumps(body, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return json.dumps({"body": body, "sha256": hashlib.sha256(data).hexdigest()},
                      sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _unwire(raw, schema):
    try:
        if type(raw) is not bytes or not 0 < len(raw) <= MAX_BYTES:
            raise ValueError("O22P_CHECKPOINT_SIZE")
        w = json.loads(raw)
        if type(w) is not dict or set(w) != {"body", "sha256"}:
            raise ValueError("O22P_CHECKPOINT_ENVELOPE")
        body = w["body"]
        if type(body) is not dict or body.get("schema") != schema:
            raise ValueError("O22P_CHECKPOINT_SCHEMA")
        encoded = json.dumps(body, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode()
        if hashlib.sha256(encoded).hexdigest() != w["sha256"]:
            raise ValueError("O22P_CHECKPOINT_DIGEST")
        if type(body.get("events")) is not int or not 0 <= body["events"] <= MAX_EVENTS:
            raise ValueError("O22P_CHECKPOINT_EVENTS")
        return body
    except (ValueError, TypeError, OverflowError, KeyError) as e:
        raise ValueError("O22P_UNTRUSTED_CHECKPOINT") from e


class NativePlasticCells:
    """Continuous local two-timescale prediction-error cells; exploratory surrogate."""

    SCHEMA = "optimizer.o22p.local-cell.v1"

    def __init__(self):
        self.slow = {y: {} for y in LABELS}
        self.fast = {y: {} for y in LABELS}
        self.actions = {"0": 0, "1": 0, "2": 0}
        self.events = 0

    def predict(self, before, action):
        features = _features(before, action)
        out = []
        for label in LABELS:
            slow = _clip(0.5 + sum(self.slow[label].get(k, 0.0)
                                    for k in features) / len(features))
            fast = _clip(0.5 + sum(self.fast[label].get(k, 0.0)
                                    for k in features) / len(features))
            out.append(_clip(0.30 * slow + 0.70 * fast))
        return tuple(out)

    def learn(self, before, action, after):
        result = _public(before, action, after)
        if self.events >= MAX_EVENTS:
            raise ValueError("O22P_TRAIN_BUDGET")
        observed = self.predict(before, action)
        keys = _features(before, action)
        for j, label in enumerate(LABELS):
            err = result[j] - observed[j]
            for rate, weights in ((0.08, self.slow[label]),
                                  (0.35, self.fast[label])):
                for k in keys:
                    weights[k] = max(-0.5, min(0.5,
                                     weights.get(k, 0.0) + rate * err))
        self.events += 1
        self.actions[str(action)] += 1

    def proposal(self, before):
        # Only a hypothetical source-public TURN preference, no source action.
        if not (self.actions["0"] and self.actions["1"]):
            return None
        p0, p1 = self.predict(before, 0)[0], self.predict(before, 1)[0]
        if abs(p0 - p1) < 0.03:
            return None
        return 0 if p0 < p1 else 1

    def checkpoint(self):
        return _wire({"schema": self.SCHEMA, "slow": self.slow,
                      "fast": self.fast, "actions": self.actions,
                      "events": self.events})

    @classmethod
    def restore(cls, raw):
        v = _unwire(raw, cls.SCHEMA)
        if (set(v) != {"schema", "slow", "fast", "actions", "events"}
            or type(v["actions"]) is not dict
            or set(v["actions"]) != {"0", "1", "2"}
            or any(type(q) is not int or q < 0 for q in v["actions"].values())
            or sum(v["actions"].values()) != v["events"]):
            raise ValueError("O22P_NATIVE_CHECKPOINT_COUNT")
        for field in ("slow", "fast"):
            if type(v[field]) is not dict or set(v[field]) != set(LABELS):
                raise ValueError("O22P_NATIVE_CHECKPOINT_HEADS")
            for rows in v[field].values():
                if type(rows) is not dict or len(rows) > 100:
                    raise ValueError("O22P_NATIVE_CHECKPOINT_WIDTH")
                for key, value in rows.items():
                    if (type(key) is not str or not 0 < len(key) < 40 or
                        type(value) not in (int, float) or
                        not math.isfinite(value) or not -0.5 <= value <= 0.5):
                        raise ValueError("O22P_NATIVE_CHECKPOINT_WEIGHT")
        m = cls()
        m.events = v["events"]
        m.actions, m.slow, m.fast = v["actions"], v["slow"], v["fast"]
        return m


class ConventionalBayesianEffects:
    """Separately implemented Beta-smoothed observed action-effect frequency."""

    SCHEMA = "optimizer.o22p.conventional-beta.v1"

    def __init__(self):
        self.context = {}
        self.backoff = {}
        self.events = 0
        self.actions = {"0": 0, "1": 0, "2": 0}

    @staticmethod
    def _keys(before, action):
        _features(before, action)
        return f"{action}:{before[5]}:{before[2]}", f"{action}:{before[5]}"

    def learn(self, before, action, after):
        y = _public(before, action, after)
        if self.events >= MAX_EVENTS:
            raise ValueError("O22P_TRAIN_BUDGET")
        full, back = self._keys(before, action)
        for book, key in ((self.context, full), (self.backoff, back)):
            if key not in book:
                book[key] = [0, 0, 0]
            data = book[key]
            data[0] += 1
            data[1] += y[0]
            data[2] += y[1]
        self.events += 1
        self.actions[str(action)] += 1

    def predict(self, before, action):
        exact, general = self._keys(before, action)
        fallback = self.backoff.get(general)
        prior = [(1 + fallback[i]) / (2 + fallback[0]) for i in (1, 2)] \
            if fallback else [0.5, 0.5]
        row = self.context.get(exact)
        if not row:
            return tuple(prior)
        # independently learned empirical Beta with backoff pseudo-counts
        return tuple((2 * prior[i] + row[i + 1]) / (2 + row[0])
                     for i in (0, 1))

    def proposal(self, before):
        if not (self.actions["0"] and self.actions["1"]):
            return None
        a, b = self.predict(before, 0)[0], self.predict(before, 1)[0]
        return None if abs(a - b) < 0.03 else (0 if a < b else 1)

    def checkpoint(self):
        return _wire({"schema": self.SCHEMA, "context": self.context,
                      "backoff": self.backoff, "actions": self.actions,
                      "events": self.events})

    @classmethod
    def restore(cls, raw):
        o = _unwire(raw, cls.SCHEMA)
        if (set(o) != {"schema", "context", "backoff", "actions", "events"}
            or type(o["actions"]) is not dict
            or set(o["actions"]) != {"0", "1", "2"}
            or any(type(x) is not int or x < 0 for x in o["actions"].values())
            or sum(o["actions"].values()) != o["events"]):
            raise ValueError("O22P_CONVENTIONAL_CHECKPOINT_COUNTS")
        for source in ("context", "backoff"):
            if type(o[source]) is not dict or len(o[source]) > 256:
                raise ValueError("O22P_CONVENTIONAL_CHECKPOINT_WIDTH")
            for key, row in o[source].items():
                if (type(key) is not str or len(key) > 24
                    or type(row) is not list or len(row) != 3
                    or any(type(v) is not int or not 0 <= v <= o["events"] for v in row)
                    or row[1] > row[0] or row[2] > row[0]):
                    raise ValueError("O22P_CONVENTIONAL_CHECKPOINT_VALUES")
        m = cls()
        m.context, m.backoff = o["context"], o["backoff"]
        m.events, m.actions = o["events"], o["actions"]
        return m
