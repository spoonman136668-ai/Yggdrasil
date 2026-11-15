"""Source-blind public delayed-effect program induction, research development only.

No source simulator import, oracle, private law ID or FKP17 first use.
The *generic* 4096-program grammar is declared in the frozen preregistration;
this does NOT invent primitives outside its supplied algebra.
"""
from __future__ import annotations

import hashlib
import json
import math

ACTIONS = 8
PROGRAMS = 4096
CAPACITY = 1048576
MAX_OBSERVATIONS = 40
STEP_FIELDS = ("before", "action", "after", "reward", "done", "history")
OLD_FIELDS = ("before", "action", "reward", "after", "done")


def _state(state):
    if type(state) not in (tuple, list) or len(state) != 8 or any(
        type(v) is not int or not 0 <= v < 16 for v in state
    ):
        raise ValueError("SFI02_PUBLIC_STATE")
    return tuple(state)


def _action(action):
    if type(action) is not int or not 0 <= action < ACTIONS:
        raise ValueError("SFI02_PUBLIC_ACTION")
    return action


def _history(history, before):
    if type(history) is not tuple or len(history) > 16:
        raise ValueError("SFI02_PUBLIC_HISTORY")
    for i, item in enumerate(history):
        if tuple(getattr(item, "_fields", ())) != OLD_FIELDS:
            raise ValueError("SFI02_PRIVATE_HISTORY")
        _state(item.before)
        _state(item.after)
        _action(item.action)
        if type(item.reward) not in (int, float) or not math.isfinite(item.reward) or item.reward not in (-.25, 0, .25, 1.0):
            raise ValueError("SFI02_HISTORY_REWARD")
        if type(item.done) is not bool:
            raise ValueError("SFI02_HISTORY_DONE")
        if i and history[i-1].after != item.before:
            raise ValueError("SFI02_HISTORY_GAP")
    if history and history[-1].after != before:
        raise ValueError("SFI02_HISTORY_BEFORE_GAP")
    return history


def public_row(row):
    if tuple(getattr(row, "_fields", ())) != STEP_FIELDS:
        raise ValueError("SFI02_PUBLIC_ONLY_STEP")
    before = _state(row.before)
    action = _action(row.action)
    after = _state(row.after)
    if type(row.reward) not in (float, int) or not math.isfinite(row.reward) or row.reward not in (0, .25, -.25, 1.0):
        raise ValueError("SFI02_EARNED_REWARD")
    if type(row.done) is not bool or (row.done and row.reward != 1.0):
        raise ValueError("SFI02_TERMINATION")
    history = _history(row.history, before)
    if len(history) < 3 and row.reward != 0:
        raise ValueError("SFI02_UNEARNED_WARMUP_REWARD")
    if len(history) >= 3 and row.reward == 0:
        raise ValueError("SFI02_MISSING_DELAYED_REWARD")
    credit = None
    if len(history) >= 3:
        eligible = history[-2]
        credit = (history[-3].action,
                  history[-4].action if len(history) >= 4 else 0,
                  eligible.before[0] & 1, eligible.action,
                  row.reward > 0)
    # Exact serialized public-custody event; no future or private law fields.
    old = [[list(x.before), x.action, float(x.reward), list(x.after), x.done] for x in history]
    normalized = json.dumps([list(before), action, list(after), float(row.reward), row.done, old],
                            separators=(",", ":"), allow_nan=False).encode("ascii")
    return credit, len(normalized).to_bytes(4, "little") + normalized


def _op(op, a, b):
    if op == 0:
        return (a + b) & 7
    if op == 1:
        return (a - b) & 7
    if op == 2:
        return (b - a) & 7
    if op == 3:
        return a ^ b
    raise AssertionError("SFI02_OPERATOR")


def _catalog():
    # Generic low-depth programs, not source family or shift labels.
    # 2 outer terminals x 2 inner terminals x 4 x 4 operators x 8 literals x 8 gains.
    return tuple((lhs, rhs, outer, inner, k, gain)
                 for lhs in range(2) for rhs in range(2)
                 for outer in range(4) for inner in range(4)
                 for k in range(8) for gain in range(8))


CATALOG = _catalog()
assert len(CATALOG) == PROGRAMS


def execute_program(p, previous, older, context):
    lhs, rhs, outer, inner, k, gain = p
    left = previous if lhs == 0 else older
    right = older if rhs == 0 else 0
    return (_op(outer, left, _op(inner, right, k)) + gain * context) & 7


class DirectMicrofeedback:
    """Unsigned direct-written eligibility mask, one byte per grammar program."""

    raw_parameter_bytes = PROGRAMS

    def __init__(self):
        self.enabled = bytearray([1]) * PROGRAMS
        self.received = 0
        self.digest = hashlib.sha256()

    def observe_public(self, row):
        if self.received >= MAX_OBSERVATIONS:
            raise ValueError("SFI02_OBSERVATION_BUDGET")
        credit, canonical = public_row(row)
        if credit is not None:
            prev, older, context, action, positive = credit
            changes = bytearray(self.enabled)
            for i, p in enumerate(CATALOG):
                if changes[i] and ((execute_program(p, prev, older, context) == action) != positive):
                    changes[i] = 0
            if not any(changes):
                raise ValueError("SFI02_CONTRADICTORY_EVIDENCE")
        else:
            changes = self.enabled
        # All validation/capacity and evidence checks before state mutation.
        self.enabled = changes
        self.digest.update(canonical)
        self.received += 1

    def choose_public(self, state, history):
        before = _state(state)
        past = _history(history, before)
        prev = past[-1].action if past else 0
        older = past[-2].action if len(past) >= 2 else 0
        context = before[0] & 1
        votes = [0] * ACTIONS
        for i, p in enumerate(CATALOG):
            if self.enabled[i]:
                votes[execute_program(p, prev, older, context)] += 1
        # Deterministic: smallest tied action.
        return max(range(ACTIONS), key=lambda a: (votes[a], -a))

    def state_receipt(self):
        h = hashlib.sha256()
        h.update(b"SFI02-DIRECT-MICROFEEDBACK-v1")
        h.update(self.enabled)
        h.update(self.digest.digest())
        h.update(self.received.to_bytes(2, "little"))
        return h.hexdigest()

    @property
    def hypothesis_count(self):
        return self.enabled.count(1)


class ConventionalExactSymbolic:
    """Separate exact consistent-program posterior with identical public DSL."""

    raw_parameter_bytes = PROGRAMS * 2

    def __init__(self):
        self.remaining = set(range(PROGRAMS))
        self.received = 0
        self.digest = hashlib.sha256()

    @staticmethod
    def _symbolic_eval(program, p, q, c):
        lhs, rhs, f, g, n, slope = program
        a = p if lhs == 0 else q
        b = q if rhs == 0 else 0
        def fn(k, x, y):
            return ((x + y) & 7) if k == 0 else (((x - y) & 7) if k == 1
                   else (((y - x) & 7) if k == 2 else x ^ y))
        return (fn(f, a, fn(g, b, n)) + slope * c) & 7

    def observe_public(self, row):
        if self.received >= MAX_OBSERVATIONS:
            raise ValueError("SFI02_SYMBOLIC_BUDGET")
        credit, canonical = public_row(row)
        new = self.remaining
        if credit is not None:
            p, q, c, action, positive = credit
            new = {i for i in self.remaining
                   if (self._symbolic_eval(CATALOG[i], p, q, c) == action) == positive}
            if not new:
                raise ValueError("SFI02_SYMBOLIC_CONTRADICTION")
        self.remaining = new
        self.digest.update(canonical)
        self.received += 1

    def choose_public(self, state, history):
        before = _state(state)
        past = _history(history, before)
        p = past[-1].action if past else 0
        q = past[-2].action if len(past) >= 2 else 0
        c = before[0] & 1
        votes = [0] * ACTIONS
        for i in self.remaining:
            votes[self._symbolic_eval(CATALOG[i], p, q, c)] += 1
        return max(range(ACTIONS), key=lambda a: (votes[a], -a))

    def state_receipt(self):
        h = hashlib.sha256()
        h.update(b"SFI02-INDEPENDENT-EXACT-SYMBOLIC-v1")
        h.update(bytes(int(i in self.remaining) for i in range(PROGRAMS)))
        h.update(self.digest.digest())
        h.update(self.received.to_bytes(2, "little"))
        return h.hexdigest()

    @property
    def hypothesis_count(self):
        return len(self.remaining)


class ExactContextTable:
    """Strong non-compositional case-memory reference, same public experiences."""

    raw_parameter_ceiling_bytes = 8 * 8 * 2 * 8 * (4 + 8)

    def __init__(self):
        self.table = {}
        self.received = 0
        self.digest = hashlib.sha256()

    def observe_public(self, row):
        if self.received >= MAX_OBSERVATIONS:
            raise ValueError("SFI02_TABLE_BUDGET")
        credit, canonical = public_row(row)
        if credit is not None:
            p, q, c, action, positive = credit
            key = (p, q, c, action)
            n, total = self.table.get(key, (0, 0.0))
            self.table[key] = (n + 1, total + (1.0 if positive else -0.25))
        self.digest.update(canonical)
        self.received += 1

    def choose_public(self, state, history):
        before = _state(state)
        past = _history(history, before)
        p = past[-1].action if past else 0
        q = past[-2].action if len(past) >= 2 else 0
        c = before[0] & 1
        return max(range(ACTIONS), key=lambda a: (
            self.table[(p, q, c, a)][1] / self.table[(p, q, c, a)][0]
            if (p, q, c, a) in self.table else -0.25, -a))


class WrongCredit:
    """Negative: credits reward to immediate action instead of action two earlier."""

    raw_parameter_bytes = ACTIONS * 12

    def __init__(self):
        self.totals = [0.0] * ACTIONS
        self.counts = [0] * ACTIONS
        self.received = 0
        self.digest = hashlib.sha256()

    def observe_public(self, row):
        if self.received >= MAX_OBSERVATIONS:
            raise ValueError("SFI02_WRONG_BUDGET")
        _, canonical = public_row(row)
        self.totals[row.action] += float(row.reward)
        self.counts[row.action] += 1
        self.received += 1
        self.digest.update(canonical)

    def choose_public(self, state, history):
        before = _state(state)
        _history(history, before)
        return max(range(ACTIONS), key=lambda a: (
            self.totals[a] / self.counts[a] if self.counts[a] else -0.25, -a))
