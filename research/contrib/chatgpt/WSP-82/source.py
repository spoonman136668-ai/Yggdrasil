"""WSP82 evaluator-private unregistered history-dependency worlds.

No learner/policy/strong control may import this module. All source/private
transition truths remain unavailable to training; session.step charges one
nonreset physical action. Protected WSP80 seeds never admitted here.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from itertools import product

COHORT = {
    9701: "equal_lag_two", 9702: "equal_lag_two",
    9703: "memoryless_control", 9704: "memoryless_control",
}
ACTIONS = tuple(range(6))
STATES = tuple(product((0, 1), repeat=6))
PAID = 384
CONTEXTS = ((), (0, 1), (1, 1), (4, 4))


@dataclass(frozen=True)
class Experience:
    before: tuple
    action: int
    after: tuple
    action_cost: int = 1


class World:
    def __init__(self, seed):
        if type(seed) is not int or seed not in COHORT:
            raise PermissionError("only four frozen WSP82 unregistered DEV worlds")
        self.seed = seed
        self.family = COHORT[seed]
        digest = sha256(f"WSP82|DEV|{seed}|offset-v1".encode("ascii")).digest()
        self._offset = 1 + int.from_bytes(digest, "big") % 5

    def _transition(self, before, action, history):
        if (type(before) is not tuple or before not in STATES
                or type(action) is not int or action not in ACTIONS
                or type(history) not in (tuple, list)
                or any(type(a) is not int or a not in ACTIONS for a in history)):
            raise ValueError("evaluator-only transition input invalid")
        out = list(before)
        out[action] ^= 1
        if (self.family == "equal_lag_two" and len(history) >= 2
                and history[-2] == history[-1]):
            out[(action + self._offset) % 6] ^= 1
        return tuple(out)

    def _truth(self, context, before, action):
        return self._transition(before, action, context)

    def session(self):
        return Session(self)

    def private_receipt(self):
        from json import dumps
        obj = {"seed": self.seed, "family": self.family, "offset": self._offset}
        return sha256(dumps(obj, sort_keys=True,
                            separators=(",", ":")).encode("ascii")).hexdigest()


class Session:
    def __init__(self, world):
        self._world = world
        self.current = (0,) * 6
        self.actions = []
        self.ledger = []

    def step(self, action):
        if (type(action) is not int or action not in ACTIONS
                or len(self.ledger) >= PAID):
            raise ValueError("unpaid or overbudget physical action")
        before = self.current
        after = self._world._transition(before, action, self.actions)
        row = Experience(before, action, after)
        self.actions.append(action)
        self.ledger.append(row)
        self.current = after
        return row


def fixed_action(seed, step):
    if (type(seed) is not int or seed not in COHORT
            or type(step) is not int or not 0 <= step < PAID):
        raise PermissionError("out-of-cohort or out-of-budget action")
    digest = sha256(f"WSP82|DEV|{seed}|action|{step}".encode("ascii")).digest()
    return int.from_bytes(digest[:8], "big") % 6
