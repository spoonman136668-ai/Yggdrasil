"""O22-R: separately implemented conditional Beta memory with/without decay.

Reads source-owned, actually selected public before/after action receipts only.
Independent of native cell predictor and original MiniGrid simulator.
"""
from __future__ import annotations
import hashlib
import json
import math

SCHEMA = "optimizer.o22r.temporal-beta.v1"
CAP = 4096


def _observed(b, action, after=None):
    if (type(b) is not list or len(b) != 6 or
        any(type(v) is not int for v in b) or
        b[2] not in (0, 1, 2, 3) or b[5] not in (0, 1) or
        any(v < 0 or v > 64 for v in b[:5]) or
        type(action) is not int or action not in (0, 1, 2)):
        raise ValueError("O22R_NOT_SELECTED_PUBLIC_EVENT")
    if after is None:
        return None
    if (type(after) is not list or len(after) != 6 or
        any(type(v) is not int for v in after) or
        after[2] not in (0, 1, 2, 3) or after[5] not in (0, 1) or
        any(v < 0 or v > 64 for v in after[:5])):
        raise ValueError("O22R_BAD_SOURCE_RETURN")
    return (after[5], int((b[0], b[1]) != (after[0], after[1])))


class TemporalBeta:
    """Context-conditional independent conventional categorical Beta predictor."""

    def __init__(self, mode="discounted"):
        if mode not in ("discounted", "cumulative", "phase_only"):
            raise ValueError("O22R_UNKNOWN_MEMORY_MODE")
        self.mode = mode
        self.decay = 0.92 if mode == "discounted" else 1.0
        self.context = {}
        self.actions = {"0": 0, "1": 0, "2": 0}
        self.events = 0

    def _key(self, before, action, step):
        _observed(before, action)
        if type(step) is not int or not 0 <= step <= 10000:
            raise ValueError("O22R_STEP_NOT_PUBLIC")
        if self.mode == "phase_only":
            phase = "0" if step < 8 else "1" if step < 24 else "2"
            return f"a{action}:phase{phase}"
        return f"a{action}:front{before[5]}"

    def predict(self, before, action, step):
        key = self._key(before, action, step)
        if key not in self.context:
            return (0.5, 0.5)
        counts = self.context[key]
        return tuple((1.0 + counts[2*i+1]) / (2.0 + counts[2*i]) for i in range(2))

    def learn(self, before, action, after, step):
        y = _observed(before, action, after)
        key = self._key(before, action, step)
        if self.events >= CAP:
            raise ValueError("O22R_TRAIN_CAP")
        if key not in self.context and len(self.context) >= 20:
            raise ValueError("O22R_CONTEXT_CAP")
        row = self.context.setdefault(key, [0.0, 0.0, 0.0, 0.0])
        for i in range(2):
            # Preregistered Beta prior (1,1) is NOT decayed.
            row[2*i] = self.decay*row[2*i] + 1.0
            row[2*i+1] = self.decay*row[2*i+1] + y[i]
        self.events += 1
        self.actions[str(action)] += 1

    def checkpoint(self):
        body = {"schema": SCHEMA, "mode": self.mode, "decay": self.decay,
                "context": self.context, "actions": self.actions, "events": self.events}
        raw = json.dumps(body, sort_keys=True, separators=(",", ":"),
                         allow_nan=False).encode()
        return json.dumps({"body": body, "sha256": hashlib.sha256(raw).hexdigest()},
                          sort_keys=True, separators=(",", ":"), allow_nan=False).encode()

    @classmethod
    def restore(cls, blob):
        try:
            if type(blob) is not bytes or not 0 < len(blob) < 40000:
                raise ValueError("O22R_CHECKPOINT_SIZE")
            outer = json.loads(blob)
            if type(outer) is not dict or set(outer) != {"body", "sha256"}:
                raise ValueError("O22R_CHECKPOINT_ENVELOPE")
            b = outer["body"]
            if (type(b) is not dict or set(b) != {
                "schema","mode","decay","context","actions","events"
            } or b["schema"] != SCHEMA):
                raise ValueError("O22R_CHECKPOINT_SCHEMA")
            raw = json.dumps(b, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode()
            if hashlib.sha256(raw).hexdigest() != outer["sha256"]:
                raise ValueError("O22R_CHECKPOINT_INTEGRITY")
            m = cls(b["mode"])
            if (b["decay"] != m.decay or type(b["events"]) is not int
                or not 0 <= b["events"] <= CAP or
                type(b["context"]) is not dict or len(b["context"]) > 20 or
                type(b["actions"]) is not dict or set(b["actions"]) != {"0","1","2"} or
                any(type(v) is not int or v < 0 for v in b["actions"].values()) or
                sum(b["actions"].values()) != b["events"]):
                raise ValueError("O22R_CHECKPOINT_INVALID_COUNTS")
            for k, row in b["context"].items():
                if (type(k) is not str or len(k) > 20 or
                    type(row) is not list or len(row) != 4 or
                    any(type(v) not in (int,float) or not math.isfinite(v) or
                        v < 0 or v > CAP+1 for v in row) or
                    row[1] > row[0] + 1e-9 or row[3] > row[2] + 1e-9):
                    raise ValueError("O22R_CHECKPOINT_CONTEXT_BAD")
                if m.mode == "phase_only":
                    valid = {f"a{a}:phase{p}" for a in range(3) for p in range(3)}
                else:
                    valid = {f"a{a}:front{s}" for a in range(3) for s in range(2)}
                if k not in valid:
                    raise ValueError("O22R_CHECKPOINT_CONTEXT_FORGED")
            m.context, m.actions, m.events = b["context"], b["actions"], b["events"]
            return m
        except (KeyError,TypeError,ValueError,OverflowError) as e:
            raise ValueError("O22R_UNTRUSTED_CHECKPOINT") from e
