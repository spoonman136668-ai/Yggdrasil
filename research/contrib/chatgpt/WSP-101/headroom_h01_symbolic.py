"""WSP101 H01: independent public-grammar symbolic headroom diagnostic.

Input is ONLY publicly observed passive/action/reward rows. This solver does
not import fixture generator, oracle, context IDs, hidden params or weights.
The experiment is post-manual DEV diagnosis, NOT original scientific first use.
"""
from __future__ import annotations

from itertools import product

ACTIONS = (0, 1, 2, 3)
TRIGGERS = (1, 2, 3)
MODES = (0, 1)
GRAMMAR = tuple(product(range(4), range(6), range(4)))
assert len(GRAMMAR) == 96


def _visible(observation):
    if type(observation) not in (tuple, list) or len(observation) != 6:
        raise ValueError("six observable channels required")
    if any(type(x) is not int or not 0 <= x < 4 for x in observation):
        raise ValueError("invalid public channel")
    return tuple(observation)


def _apply(op, a, b):
    if op == 0:
        return (a + b) % 4
    if op == 1:
        return a ^ b
    if op == 2:
        return a if b % 2 == 0 else 3 - a
    if op == 3:
        return (a * b + b) % 4
    raise ValueError("invalid public operator")


def _transition(x, h, action, visible_program, trigger, mode):
    """Reimplements only the published four-operator causal grammar."""
    x = _visible(x)
    if type(action) is not int or action not in ACTIONS:
        raise ValueError("invalid action")
    if type(h) is not tuple or len(h) != 2 or any(
        type(v) is not int or v not in ACTIONS for v in h
    ):
        raise ValueError("invalid hidden state shape")
    f, wiring, phase = visible_program
    if visible_program not in GRAMMAR or trigger not in TRIGGERS or mode not in MODES:
        raise ValueError("invalid candidate grammar")
    y = []
    for i in range(6):
        a, b = x[(i + wiring) % 6], x[(i + wiring + 2) % 6]
        base = (_apply((f + i % 4) % 4, a, b)
                + x[(i + 4) % 6] + phase * (i % 3)) % 4
        if i < 4:
            base = (base + h[i % 2]) % 4
        y.append(base)
    new_h = list(h)
    if action == trigger:
        new_h[0] = (h[0] + (1 if mode == 0 else 2)) % 4
        if (x[0] + phase) % 2 == 1:
            new_h[1] = (h[1] + 1) % 4
    if action == (trigger % 3) + 1:
        new_h[1] = (h[1] + 1 + x[5] % 2) % 4
    return tuple(y), tuple(new_h)


def _rows(episodes, *, require_passive):
    if type(episodes) not in (tuple, list) or not episodes:
        raise ValueError("missing public episodes")
    for episode in episodes:
        if type(episode) not in (tuple, list) or not 1 <= len(episode) <= 4:
            raise ValueError("bad episode length")
        last = None
        for row in episode:
            if type(row) not in (tuple, list) or len(row) != 4:
                raise ValueError("bad public row")
            x, action, y, reward = row
            x, y = _visible(x), _visible(y)
            if type(action) is not int or action not in ACTIONS or (require_passive and action != 0):
                raise ValueError("bad public action")
            if type(reward) is not int or reward != int((y[0] + y[1]) % 4 == 3):
                raise ValueError("public reward mismatch")
            if last is not None and x != last:
                raise ValueError("discontinuous public episode")
            last = y


def visible_candidates(passive):
    """96-grammar enumeration from passive public rows only."""
    _rows(passive, require_passive=True)
    survivors = []
    for program in GRAMMAR:
        fits = True
        for ep in passive:
            for x, _, observed, _ in ep:
                pred, _ = _transition(x, (0, 0), 0, program, 1, 0)
                if pred != tuple(observed):
                    fits = False
                    break
            if not fits:
                break
        if fits:
            survivors.append(program)
    return tuple(survivors)


def _public_trace(episodes, program, trigger, mode):
    for episode in episodes:
        x = _visible(episode[0][0])
        hidden = (0, 0)
        for row in episode:
            observed_x, action, y, reward = row
            if x != tuple(observed_x):
                return False
            predicted_y, hidden = _transition(x, hidden, action, program, trigger, mode)
            if predicted_y != tuple(y) or reward != int((predicted_y[0] + predicted_y[1]) % 4 == 3):
                return False
            x = predicted_y
    return True


def hidden_candidates(passive, active):
    """No mode/trigger oracle arguments: only public rows and published grammar."""
    _rows(active, require_passive=False)
    surviving_visible = visible_candidates(passive)
    solutions = []
    for program in surviving_visible:
        for trigger in TRIGGERS:
            for mode in MODES:
                if _public_trace(active, program, trigger, mode):
                    solutions.append((program, trigger, mode))
    return tuple(solutions)
