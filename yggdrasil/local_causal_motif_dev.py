"""Opt-in DG1-MC01 local causal-motif learning prototype (DEV only).

Not a replacement for the original developmental runtime. Each of four world
sites is represented by one of seven available active cells; nine retained
addresses remain reserved. The model learns *only* from before/action/after
public consequences, never from world rules or arbitrary-state oracle calls.

This is a fixed-topology, ordinary online logistic learner, not discovered
topology, general intelligence, or scientific first-use evidence.
"""
from __future__ import annotations

import hashlib
import math
import struct
from typing import Sequence


class LocalCausalMotifDev:
    NODES = 4
    ACTIVE_SLOTS = 7
    RETAINED_SLOTS = 9
    FEATURES = 4
    MAX_UPDATES = 64
    WEIGHTS = ACTIVE_SLOTS * FEATURES
    LEARNED_BYTES = WEIGHTS * 8
    RATE = 0.5
    MAGIC = b"YMC1"
    # mode byte + seven float64*4 rows + seven uint16 counts + sha256
    CHECKPOINT_BYTES = 4 + 1 + LEARNED_BYTES + 14 + 32

    __slots__ = ("_weights", "_count", "_neighbor_features")

    def __init__(self, *, neighbor_features: bool = True) -> None:
        if type(neighbor_features) is not bool:
            raise ValueError("MC01_FEATURE_MODE_INVALID")
        self._neighbor_features = neighbor_features
        self._weights = [[0.0] * self.FEATURES for _ in range(self.ACTIVE_SLOTS)]
        self._count = [0] * self.ACTIVE_SLOTS

    @staticmethod
    def _state_action(state: int, action: int) -> tuple[int, int]:
        if type(state) is not int or not 0 <= state < 16:
            raise ValueError("MC01_PUBLIC_STATE_INVALID")
        if type(action) is not int or not 0 <= action < 4:
            raise ValueError("MC01_PUBLIC_ACTION_INVALID")
        return state, action

    @classmethod
    def _features(cls, state: int, cell: int, *, neighbors: bool) -> tuple[float, ...]:
        if not neighbors:
            return (1.0, 0.0, 0.0, 0.0)
        left = (state >> ((cell - 1) % cls.NODES)) & 1
        right = (state >> ((cell + 1) % cls.NODES)) & 1
        return (1.0, float(left), float(right), float(left * right))

    @staticmethod
    def _sigmoid(score: float) -> float:
        if score >= 0.0:
            return 1.0 / (1.0 + math.exp(-score))
        exp_score = math.exp(score)
        return exp_score / (1.0 + exp_score)

    @property
    def updates(self) -> int:
        return sum(self._count)

    @property
    def neighbor_features(self) -> bool:
        return self._neighbor_features

    def observe(self, before: int, action: int, after: int) -> None:
        """Charge exactly one real public action-result; reject unsafe effects."""
        before, action = self._state_action(before, action)
        if type(after) is not int or not 0 <= after < 16:
            raise ValueError("MC01_PUBLIC_SUCCESSOR_INVALID")
        effect = before ^ after
        if effect not in (0, 1 << action):
            raise ValueError("MC01_NONLOCAL_EFFECT_REJECTED")
        if self.updates >= self.MAX_UPDATES:
            raise ValueError("MC01_ACTION_BUDGET_EXCEEDED")
        x = self._features(before, action, neighbors=self._neighbor_features)
        w = self._weights[action]
        p = self._sigmoid(sum(a * b for a, b in zip(x, w)))
        error = (1.0 if effect else 0.0) - p
        # Shared rule, local credit assignment; same four coefficients per cell.
        self._weights[action] = [
            max(-8.0, min(8.0, weight + self.RATE * error * feature))
            for weight, feature in zip(w, x)
        ]
        self._count[action] += 1

    def predict(self, state: int, action: int, *,
                ablate_neighbors: bool = False) -> int:
        state, action = self._state_action(state, action)
        if type(ablate_neighbors) is not bool:
            raise ValueError("MC01_ABLATION_INVALID")
        x = self._features(
            state, action, neighbors=self._neighbor_features and not ablate_neighbors
        )
        margin = sum(a * b for a, b in zip(x, self._weights[action]))
        # Default tie policy is no-change; no oracle or unseen answer is queried.
        return state ^ (1 << action) if margin > 0.0 else state

    def rollout(self, state: int, actions: Sequence[int]) -> int:
        if type(actions) not in (tuple, list) or len(actions) != 2:
            raise ValueError("MC01_ROLLOUT_LENGTH_INVALID")
        for action in actions:
            state = self.predict(state, action)
        return state

    def snapshot(self) -> bytes:
        payload = bytearray(self.MAGIC)
        payload.append(1 if self._neighbor_features else 0)
        for row in self._weights:
            for value in row:
                payload.extend(struct.pack(">d", value))
        for count in self._count:
            payload.extend(struct.pack(">H", count))
        return bytes(payload) + hashlib.sha256(payload).digest()

    @classmethod
    def restore(cls, snapshot: bytes) -> "LocalCausalMotifDev":
        if (type(snapshot) is not bytes or
                len(snapshot) != cls.CHECKPOINT_BYTES or
                snapshot[:4] != cls.MAGIC or
                snapshot[4] not in (0, 1) or
                hashlib.sha256(snapshot[:-32]).digest() != snapshot[-32:]):
            raise ValueError("MC01_CHECKPOINT_REJECTED")
        vals = struct.unpack(">" + "d" * cls.WEIGHTS + "H" * 7,
                             snapshot[5:-32])
        weights = vals[:cls.WEIGHTS]
        counts = vals[cls.WEIGHTS:]
        if (any(not math.isfinite(w) or abs(w) > 8 for w in weights) or
                sum(counts) > cls.MAX_UPDATES):
            raise ValueError("MC01_CHECKPOINT_STATE_INVALID")
        cells = cls(neighbor_features=(snapshot[4] == 1))
        cells._weights = [
            list(weights[i:i+cls.FEATURES])
            for i in range(0, cls.WEIGHTS, cls.FEATURES)
        ]
        cells._count = list(counts)
        return cells
