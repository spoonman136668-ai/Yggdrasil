"""SFI-03 generic bitwise-operator admission from observed delayed microfeedback.

No source simulator, hidden family, private shift, alternate outcomes or source
law function is imported. Both learners have exactly the same 32768 generic
hypotheses; this cannot prove autonomous invention outside that grammar.
"""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
import math

ACTIONS = 8
PROGRAMS = 32768  # 16^3 public two-input bit truth tables x 8 XOR offsets
MAX_WORLD_ROWS = 40
HISTORY_LIMIT = 16
STEP_FIELDS = ("before", "action", "after", "reward", "done", "history")
PRIOR_FIELDS = ("before", "action", "reward", "after", "done")


def _state(state):
    if type(state) not in (tuple, list) or len(state) != 8 or any(
        type(x) is not int or not 0 <= x < 16 for x in state
    ):
        raise ValueError("SFI03_PUBLIC_STATE")
    return tuple(state)


def _action(action):
    if type(action) is not int or not 0 <= action < ACTIONS:
        raise ValueError("SFI03_PUBLIC_ACTION")
    return action


def _history(history, state):
    if type(history) is not tuple or len(history) > HISTORY_LIMIT:
        raise ValueError("SFI03_PUBLIC_HISTORY")
    for i, event in enumerate(history):
        if tuple(getattr(event, "_fields", ())) != PRIOR_FIELDS:
            raise ValueError("SFI03_PRIVATE_HISTORY")
        _state(event.before)
        _state(event.after)
        _action(event.action)
        if type(event.reward) not in (int, float) or not math.isfinite(event.reward) or event.reward not in (-.25, 0., .25, 1.):
            raise ValueError("SFI03_HISTORY_REWARD")
        if type(event.done) is not bool:
            raise ValueError("SFI03_HISTORY_DONE")
        if i and history[i - 1].after != event.before:
            raise ValueError("SFI03_HISTORY_DISCONTINUITY")
    if history and history[-1].after != state:
        raise ValueError("SFI03_HISTORY_STATE_MISMATCH")
    return history


def _public(row):
    if tuple(getattr(row, "_fields", ())) != STEP_FIELDS:
        raise ValueError("SFI03_PUBLIC_STEP_REQUIRED")
    before, action, after, reward, done, history = row
    before, after, action = _state(before), _state(after), _action(action)
    if type(reward) not in (float, int) or not math.isfinite(reward) or reward not in (-.25, 0., .25, 1.):
        raise ValueError("SFI03_PUBLIC_REWARD")
    if type(done) is not bool or (done and reward != 1.):
        raise ValueError("SFI03_PUBLIC_DONE")
    history = _history(history, before)
    if (len(history) < 3 and reward != 0.) or (len(history) >= 3 and reward == 0.):
        raise ValueError("SFI03_DELAYED_CREDIT_MISMATCH")
    credit = None
    if len(history) >= 3:
        eligible = history[-2]
        credit = (history[-3].action,
                  history[-4].action if len(history) >= 4 else 0,
                  eligible.before[0] & 1, eligible.action, reward > 0.)
    h = [[list(x.before), x.action, float(x.reward), list(x.after), x.done] for x in history]
    blob = json.dumps([list(before), action, list(after), float(reward), done, h],
                      separators=(",", ":"), allow_nan=False).encode("ascii")
    return credit, len(blob).to_bytes(4, "little") + blob


@lru_cache(maxsize=128)
def _predictions(prev, older, context):
    """32,768 action outputs for a source-independent generic truth-bit bank."""
    _action(prev)
    _action(older)
    if context not in (0, 1):
        raise ValueError("SFI03_PUBLIC_CONTEXT")
    indices = tuple(((prev >> b & 1) << 1) | (older >> b & 1) for b in range(3))
    bank = bytearray(PROGRAMS)
    for code in range(4096):
        out = sum(((code >> (4 * b + indices[b])) & 1) << b for b in range(3))
        start = code * 8
        for shift in range(8):
            bank[start + shift] = out ^ shift ^ (4 if context else 0)
    return bytes(bank)


class DirectMicrofeedbackExpansion:
    """Direct written generic relation capacity, 32768-byte candidate mask."""

    learned_bytes = PROGRAMS

    def __init__(self):
        self.mask = bytearray([1]) * PROGRAMS
        self.rows = 0
        self.digest = sha256()

    def observe_public(self, row):
        if self.rows >= MAX_WORLD_ROWS:
            raise ValueError("SFI03_MODEL_BUDGET")
        credit, original = _public(row)
        new = self.mask
        if credit is not None:
            prev, older, ctx, action, positive = credit
            predictions = _predictions(prev, older, ctx)
            new = bytearray(self.mask)
            for i, enabled in enumerate(self.mask):
                if enabled and ((predictions[i] == action) != positive):
                    new[i] = 0
            if not any(new):
                raise ValueError("SFI03_NO_COMPATIBLE_GENERIC_HYPOTHESIS")
        # Commit state only after verifying entire public row and evidence.
        self.mask = new
        self.digest.update(original)
        self.rows += 1

    def choose_public(self, state, history):
        before = _state(state)
        past = _history(history, before)
        previous = past[-1].action if past else 0
        older = past[-2].action if len(past) >= 2 else 0
        pred = _predictions(previous, older, before[0] & 1)
        votes = [0] * ACTIONS
        for i, enabled in enumerate(self.mask):
            if enabled:
                votes[pred[i]] += 1
        return max(range(ACTIONS), key=lambda a: (votes[a], -a))

    @property
    def hypotheses(self):
        return self.mask.count(1)

    def receipt(self):
        h = sha256()
        h.update(b"SFI03-DIRECT-BITTRUTH-v1")
        h.update(self.mask)
        h.update(self.digest.digest())
        h.update(self.rows.to_bytes(2, "little"))
        return h.hexdigest()


class IndependentExactBoolean:
    """Separate conventional symbolic enumerator over the same generic bank."""

    learned_bytes = PROGRAMS * 2

    def __init__(self):
        self.eligible = set(range(PROGRAMS))
        self.rows = 0
        self.digest = sha256()

    @staticmethod
    def _evaluate(hypothesis, prev, older, context):
        # Standalone symbolic interpreter; does NOT call candidate readout.
        table, offset = divmod(hypothesis, 8)
        result = 0
        for bit in range(3):
            p = (prev >> bit) & 1
            q = (older >> bit) & 1
            selected = (table >> (bit * 4 + p * 2 + q)) & 1
            result |= selected << bit
        return result ^ offset ^ (4 if context else 0)

    def observe_public(self, row):
        if self.rows >= MAX_WORLD_ROWS:
            raise ValueError("SFI03_SYMBOLIC_BUDGET")
        credit, original = _public(row)
        if credit is None:
            keep = self.eligible
        else:
            p, q, context, action, positive = credit
            keep = {i for i in self.eligible
                    if (self._evaluate(i, p, q, context) == action) == positive}
            if not keep:
                raise ValueError("SFI03_SYMBOLIC_CONTRADICTION")
        self.eligible = keep
        self.digest.update(original)
        self.rows += 1

    def choose_public(self, state, history):
        before = _state(state)
        past = _history(history, before)
        p = past[-1].action if past else 0
        q = past[-2].action if len(past) >= 2 else 0
        ctx = before[0] & 1
        votes = [0] * ACTIONS
        for i in self.eligible:
            votes[self._evaluate(i, p, q, ctx)] += 1
        return max(range(ACTIONS), key=lambda a: (votes[a], -a))

    @property
    def hypotheses(self):
        return len(self.eligible)

    def receipt(self):
        h = sha256()
        h.update(b"SFI03-EXACT-SYMBOLIC-v1")
        h.update(bytes(int(i in self.eligible) for i in range(PROGRAMS)))
        h.update(self.digest.digest())
        h.update(self.rows.to_bytes(2, "little"))
        return h.hexdigest()
