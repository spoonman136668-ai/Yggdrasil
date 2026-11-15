"""FKP-17 research-only first-order public temporal reward comparator.

Not a native Yggdrasil component or a registered FKP-17 scientific arm.
Only an 8-action, one-step predecessor/action reward table. No source import,
held law access, language tokens, trained networks, or hidden outcomes.
"""
from __future__ import annotations

from array import array
import hashlib
import math
import struct

ACTIONS = 8
REGISTERS = 8
MAX_STEPS = 256
HISTORY_MAX = 16
PUBLIC_FIELDS = ("before", "action", "after", "reward", "done", "history")
HISTORY_FIELDS = ("before", "action", "reward", "after", "done")


def _action(x):
    if type(x) is not int or x not in range(ACTIONS):
        raise ValueError("FKP17_TEMP_ACTION")
    return x


def _state(x):
    if type(x) not in (list, tuple) or len(x) != REGISTERS or any(
        type(v) is not int or v not in range(16) for v in x
    ):
        raise ValueError("FKP17_TEMP_STATE")
    return tuple(x)


def _public_reward(value):
    if type(value) not in (int, float) or not math.isfinite(value) or not -1 <= value <= 1:
        raise ValueError("FKP17_TEMP_REWARD")
    return float(value)


def _previous(history, before):
    if type(history) is not tuple or len(history) > HISTORY_MAX:
        raise ValueError("FKP17_TEMP_HISTORY")
    for index, event in enumerate(history):
        if tuple(getattr(event, "_fields", ())) != HISTORY_FIELDS:
            raise ValueError("FKP17_TEMP_HISTORY_PRIVATE")
        _state(event.before)
        _action(event.action)
        _public_reward(event.reward)
        _state(event.after)
        if type(event.done) is not bool:
            raise ValueError("FKP17_TEMP_HISTORY_DONE")
        if index and _state(history[index - 1].after) != _state(event.before):
            raise ValueError("FKP17_TEMP_HISTORY_GAP")
    if history and _state(history[-1].after) != before:
        raise ValueError("FKP17_TEMP_PREDECESSOR_GAP")
    return history[-1].action if history else None


class TemporalRewardProbe:
    """One bounded predecessor-action conditional reward table.

    The 768-byte count/sum payload excludes Python runtime/object overhead.
    Abstains without observed choices from two different actions in context.
    No first-use, context switching, delayed-two-step or superiority claim.
    """

    LEARNED_BYTES = ACTIONS * ACTIONS * (4 + 8)

    def __init__(self):
        self._count = array("I", [0]) * (ACTIONS * ACTIONS)
        self._reward = array("d", [0.0]) * (ACTIONS * ACTIONS)
        self._steps = 0

    def begin_world(self):
        self.__init__()

    def observe_public(self, row):
        if tuple(getattr(row, "_fields", ())) != PUBLIC_FIELDS:
            raise ValueError("FKP17_TEMP_PRIVATE_ROW")
        before = _state(row.before)
        action = _action(row.action)
        _state(row.after)
        reward = _public_reward(row.reward)
        if type(row.done) is not bool:
            raise ValueError("FKP17_TEMP_DONE")
        prior = _previous(row.history, before)
        if self._steps >= MAX_STEPS:
            raise ValueError("FKP17_TEMP_BUDGET")
        if prior is not None and self._count[prior * ACTIONS + action] >= 65535:
            raise OverflowError("FKP17_TEMP_COUNT_OVERFLOW")
        # All validation and capacity checks precede all writes.
        if prior is not None:
            index = prior * ACTIONS + action
            self._count[index] += 1
            self._reward[index] += reward
        self._steps += 1

    def choose_public(self, state, history):
        before = _state(state)
        prior = _previous(history, before)
        if prior is None:
            return None
        row_start = prior * ACTIONS
        seen = [a for a in range(ACTIONS) if self._count[row_start + a]]
        if len(seen) < 2:
            return None
        means = [(self._reward[row_start + a] / self._count[row_start + a], a)
                 for a in seen]
        best_value = max(m for m, _ in means)
        if all(m == best_value for m, _ in means):
            return None
        return min(a for m, a in means if m == best_value)

    def state_receipt(self):
        digest = hashlib.sha256()
        digest.update(self._count.tobytes())
        digest.update(self._reward.tobytes())
        digest.update(struct.pack("<I", self._steps))
        return digest.hexdigest()
