"""WSP69 evaluator-only unfamiliar causal physics, zero-training-reset sessions.

No learner or neural baseline may import this file or receive shuffled source
roles, hidden transitions, intermediate states, or heldout answers. Training
is one 96-action physically continuous source session, with Stage A at 48.
All scoring after training uses evaluator-only full audits and compositions.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from random import Random
import json

SEEDS = tuple(range(4301, 4313))
STATES = tuple(product((0, 1), repeat=4))
ACTIONS = tuple(range(4))
STAGE_A = 48
TRAIN_ACTIONS = 96
COMPOSITIONS = 32


def _rng(seed, kind):
    b = sha256(f"WSP69|SELFTEST|{seed}|{kind}".encode("ascii")).digest()
    return Random(int.from_bytes(b, "big"))


@dataclass(frozen=True)
class Experience:
    before: tuple[int, ...]
    action: int
    after: tuple[int, ...]
    action_cost: int = 1


@dataclass(frozen=True)
class Composite:
    start: tuple[int, ...]
    actions: tuple[int, int]
    _middle: tuple[int, ...]
    _finish: tuple[int, ...]


@dataclass(frozen=True)
class World:
    seed: int
    family: str
    _roles: tuple[int, ...]
    _channels: tuple[int, ...]

    def _step_oracle(self, before, action):
        if (type(before) is not tuple or before not in STATES or
                type(action) is not int or action not in ACTIONS):
            raise ValueError("evaluator physical input invalid")
        role = self._channels[action]
        r = self._roles
        b = list(before)
        if role == 0:
            b[r[0]] ^= 1
        elif role == 1:
            if self.family == "parity":
                flip = before[r[0]] ^ before[r[2]]
            elif self.family == "and3":
                flip = before[r[0]] & before[r[2]] & before[r[3]]
            else:
                flip = before[r[0]] ^ before[r[2]]
            b[r[1]] ^= flip
        elif role == 2:
            if self.family == "parity":
                flip = before[r[0]] ^ before[r[1]] ^ before[r[3]]
            elif self.family == "and3":
                flip = before[r[0]]
            else:
                flip = before[r[0]] & (1 ^ before[r[1]]) & before[r[3]]
            b[r[2]] ^= flip
        elif role == 3:
            if self.family == "parity":
                flip = before[r[1]] ^ before[r[2]]
            elif self.family == "and3":
                flip = before[r[0]] & before[r[2]]
            else:
                flip = before[r[0]] ^ before[r[1]] ^ before[r[2]]
                b[r[0]] ^= before[r[1]] & (1 ^ before[r[2]])
            b[r[3]] ^= flip
        else:
            raise RuntimeError("invalid private role")
        return tuple(b)

    def training_session(self):
        return Session(self)

    def composition_tests(self):
        r = _rng(self.seed, "fresh-two-action-compositions")
        candidates = list(product(STATES, ACTIONS, ACTIONS))
        r.shuffle(candidates)
        selected = []
        for start, a, b in candidates[:COMPOSITIONS]:
            middle = self._step_oracle(start, a)
            finish = self._step_oracle(middle, b)
            selected.append(Composite(start, (a, b), middle, finish))
        return tuple(selected)

    def receipt(self):
        hidden = {"seed": self.seed, "family": self.family,
                  "roles": self._roles, "channels": self._channels}
        labels = [
            [list(c.start), list(c.actions), list(c._middle), list(c._finish)]
            for c in self.composition_tests()
        ]
        def digest(obj):
            return sha256(json.dumps(obj, sort_keys=True,
                                      separators=(",", ":")).encode("ascii")).hexdigest()
        return {"schema": "wsp69.weight-edit-world.v1", "seed": self.seed,
                "family": self.family, "hidden_source_sha256": digest(hidden),
                "composites_sha256": digest(labels), "test_composites": len(labels),
                "charged_training_actions": TRAIN_ACTIONS,
                "stage_a_charges": STAGE_A,
                "training_reset_allowed": False}


class Session:
    def __init__(self, world):
        self._world = world
        self.state = (0, 0, 0, 0)
        self.ledger = []

    def step(self, action):
        if len(self.ledger) >= TRAIN_ACTIONS:
            raise ValueError("physical action budget exceeded")
        prior = self.state
        next_state = self._world._step_oracle(prior, action)
        self.state = next_state
        row = Experience(prior, action, next_state)
        self.ledger.append(row)
        return row


def build_world(seed, cohort="SELFTEST"):
    if type(seed) is not int or seed not in SEEDS or cohort != "SELFTEST":
        raise PermissionError("unregistered/protected source blocked")
    family = ("parity" if seed <= 4304 else
              "and3" if seed <= 4308 else "mixed")
    r = _rng(seed, "shuffled-sensor-and-action-roles")
    roles, channels = list(ACTIONS), list(ACTIONS)
    r.shuffle(roles)
    r.shuffle(channels)
    world = World(seed, family, tuple(roles), tuple(channels))
    assert len(set(world._roles)) == 4
    assert len(set(world._channels)) == 4
    assert len(world.composition_tests()) == COMPOSITIONS
    return world
