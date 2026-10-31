"""MG94 development-only two-step public transition learner.

This is a conventional empirical history-conditioned control, not evidence of
novel cognition or an original-world result. No environment or oracle access.
"""
from __future__ import annotations

import hashlib
import json


class PublicHistoryTransitions:
    """Learn P(next_public_bit | previous_public_bit, current_bit, selected_action)."""

    def __init__(self):
        self._counts = {}  # key=(prior,current,selected_action); [next0,next1]
        self._prior = None
        self._current = None
        self._pending = None

    @staticmethod
    def bit(value):
        if type(value) is not int or value not in (0, 1):
            raise ValueError("MG94_INVALID_PUBLIC_BIT")
        return value

    def begin(self, observation):
        if self._pending is not None:
            raise ValueError("MG94_PENDING_ACTION")
        self._prior = None
        self._current = self.bit(observation)

    def select(self, action):
        if self._current is None or self._pending is not None:
            raise ValueError("MG94_SELECTION_ORDER")
        self._pending = (self._prior, self._current, self.bit(action))

    def feedback(self, next_public_bit):
        if self._pending is None:
            raise ValueError("MG94_FEEDBACK_WITHOUT_SELECTION")
        next_bit = self.bit(next_public_bit)
        key = self._pending
        self._counts.setdefault(key, [0, 0])[next_bit] += 1
        self._prior, self._current = self._current, next_bit
        self._pending = None

    def predict(self, action):
        if self._current is None or self._pending is not None:
            return None
        key = (self._prior, self._current, self.bit(action))
        counts = self._counts.get(key)
        if not counts:
            return None
        return (counts[1], counts[0] + counts[1])

    def snapshot(self):
        if self._pending is not None:
            raise ValueError("MG94_PENDING_SNAPSHOT")
        state = {"prior": self._prior, "current": self._current,
                 "counts": [[list(k), v] for k, v in sorted(
                     self._counts.items(), key=lambda item: str(item[0]))]}
        raw = json.dumps(state, separators=(",", ":"), sort_keys=True).encode()
        return raw + b"|" + hashlib.sha256(raw).hexdigest().encode()

    @classmethod
    def restore(cls, checkpoint):
        raw, sep, digest = checkpoint.rpartition(b"|")
        if not sep or hashlib.sha256(raw).hexdigest().encode() != digest:
            raise ValueError("MG94_CHECKPOINT_REJECTED")
        state = json.loads(raw)
        obj = cls()
        if state["current"] is not None:
            obj.bit(state["current"])
        if state["prior"] is not None:
            obj.bit(state["prior"])
        obj._prior, obj._current = state["prior"], state["current"]
        for key, counts in state["counts"]:
            if len(key) != 3 or any(v is not None and v not in (0, 1) for v in key):
                raise ValueError("MG94_BAD_CHECKPOINT_KEY")
            if len(counts) != 2 or any(type(v) is not int or v < 0 for v in counts):
                raise ValueError("MG94_BAD_CHECKPOINT_COUNT")
            obj._counts[tuple(key)] = counts
        return obj
