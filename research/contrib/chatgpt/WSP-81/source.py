"""WSP81 evaluator-private non-Markov worlds. UNREGISTERED developer ONLY.

The learner must never import this module. Hidden parameters and latent mode
are private to the evaluator; only physically charged public transitions may
reach the learner. No reset inside the 384-step physical session.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from random import Random
import json

STATES = tuple(product((0, 1), repeat=6))
ACTIONS = tuple(range(6))
STAGE_A = 144
CHARGES = 384
COHORT = {9401: "hidden_two_mode", 9402: "hidden_two_mode",
          9403: "hidden_two_mode", 9404: "hidden_two_mode",
          9405: "memoryless_control", 9406: "memoryless_control"}


@dataclass(frozen=True)
class Experience:
    before: tuple
    action: int
    after: tuple
    action_cost: int = 1


@dataclass(frozen=True)
class World:
    seed: int
    family: str
    _trigger: int
    _offset: int

    @classmethod
    def developer(cls, seed):
        if type(seed) is not int or seed not in COHORT:
            raise PermissionError("WSP81 only admits frozen unregistered development seeds")
        hidden_seed = sha256(
            f"WSP81|DEV|{seed}|private-params-v1".encode("ascii")).digest()
        rng = Random(int.from_bytes(hidden_seed, "big"))
        return cls(seed, COHORT[seed], rng.randrange(6), rng.randrange(1, 6))

    def _transition(self, state, action, mode):
        if (type(state) is not tuple or state not in STATES
                or type(action) is not int or action not in ACTIONS
                or type(mode) is not int or mode not in (0, 1)):
            raise ValueError("evaluator-private invalid state/action/mode")
        out = list(state)
        out[action] ^= 1
        if (self.family == "hidden_two_mode" and mode == 1
                and action != self._trigger):
            out[(action + self._offset) % 6] ^= 1
        next_mode = (
            mode ^ int(action == self._trigger)
            if self.family == "hidden_two_mode" else 0)
        return tuple(out), next_mode

    def _truth_for_context(self, context, state, action):
        if type(context) not in (tuple, list) or any(
                type(a) is not int or a not in ACTIONS for a in context):
            raise ValueError("invalid evaluator-only history")
        mode = 0
        for previous_action in context:
            mode = self._transition((0,) * 6, previous_action, mode)[1]
        return self._transition(state, action, mode)[0]

    def session(self):
        return Session(self)

    def private_receipt(self):
        private = {
            "seed": self.seed, "family": self.family,
            "trigger": self._trigger, "offset": self._offset,
        }
        return sha256(json.dumps(private, sort_keys=True,
                                 separators=(",", ":")).encode("ascii")).hexdigest()


class Session:
    def __init__(self, world):
        self._world = world
        self.current = (0,) * 6
        self._mode = 0
        self.ledger = []

    def step(self, action):
        if (type(action) is not int or action not in ACTIONS
                or len(self.ledger) >= CHARGES):
            raise ValueError("invalid or overbudget charged action")
        before = self.current
        after, new_mode = self._world._transition(before, action, self._mode)
        self.current, self._mode = after, new_mode
        row = Experience(before, action, after)
        self.ledger.append(row)
        return row


def fixed_action(seed, step):
    if type(seed) is not int or seed not in COHORT or type(step) is not int or not 0 <= step < CHARGES:
        raise PermissionError("unregistered frozen paid action only")
    stage = "stageA" if step < STAGE_A else "stageB"
    digest = sha256(f"WSP81|DEV|{seed}|{stage}|{step}".encode("ascii")).digest()
    return int.from_bytes(digest[:8], "big") % 6
