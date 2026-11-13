"""WSP62 evaluator-only selftest physics: no-reset multi-family Boolean worlds.

The learner sees only public charged chronological transitions. It must never
import this module or receive hidden role maps, oracle transitions, task
shortest paths or uncharged physical consequences during learning.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from random import Random
import json

SEEDS = tuple(range(2801, 2813))
STATES = tuple(product((0, 1), repeat=4))
ACTIONS = (0, 1, 2, 3)
INITIAL = (0, 0, 0, 0)
TRAIN_ACTIONS = 80
TASKS_PER_WORLD = 32


def _rng(seed, label):
    key = sha256(f"WSP62|SELFTEST|{seed}|{label}".encode("ascii")).digest()
    return Random(int.from_bytes(key, "big"))


@dataclass(frozen=True)
class Experience:
    before: tuple[int, ...]
    action: int
    after: tuple[int, ...]
    action_cost: int = 1


@dataclass(frozen=True)
class Task:
    start: tuple[int, ...]
    target: tuple[int, ...]
    _shortest: int


@dataclass(frozen=True)
class World:
    seed: int
    family: str
    _roles: tuple[int, ...]
    _channels: tuple[int, ...]

    def _step_oracle(self, state, action):
        if (type(state) is not tuple or state not in STATES or
                type(action) is not int or action not in ACTIONS):
            raise ValueError("invalid private source invocation")
        role = self._channels[action]
        bits = self._roles
        next_state = list(state)
        if role == 0:
            flip = 1
        elif role == 1:
            flip = state[bits[0]]
        elif role == 2:
            if self.family == "chain":
                flip = state[bits[1]]
            elif self.family == "triple_xor":
                flip = state[bits[0]] ^ state[bits[1]] ^ state[bits[3]]
            else:
                flip = state[bits[0]] ^ (state[bits[1]] & state[bits[3]])
        elif role == 3:
            if self.family == "chain":
                flip = state[bits[2]]
            elif self.family == "triple_xor":
                flip = state[bits[0]] ^ state[bits[1]] ^ state[bits[2]]
            else:
                flip = state[bits[1]] ^ (state[bits[0]] & state[bits[2]])
        else:
            raise RuntimeError("impossible hidden role")
        next_state[bits[role]] ^= flip
        return tuple(next_state)

    def training_session(self):
        return Session(self)

    def _shortest(self, start, target):
        if start == target:
            return 0
        queue = deque([(start, 0)])
        reached = {start}
        while queue:
            state, dist = queue.popleft()
            if dist >= 6:
                continue
            for action in ACTIONS:
                next_state = self._step_oracle(state, action)
                if next_state == target:
                    return dist + 1
                if next_state not in reached:
                    reached.add(next_state)
                    queue.append((next_state, dist + 1))
        return None

    def tasks(self):
        candidates = []
        for start in STATES:
            for target in STATES:
                shortest = self._shortest(start, target)
                if shortest is not None and 2 <= shortest <= 6:
                    candidates.append(Task(start, target, shortest))
        if len(candidates) < TASKS_PER_WORLD:
            raise RuntimeError("insufficient independently reachable goals")
        r = _rng(self.seed, "task-construction")
        r.shuffle(candidates)
        return tuple(candidates[:TASKS_PER_WORLD])

    def evaluate(self, task, actions):
        if actions is None or type(actions) not in (tuple, list) or len(actions) > 6:
            return False
        current = task.start
        for action in actions:
            current = self._step_oracle(current, action)
        return current == task.target

    def receipt(self):
        private = {"seed":self.seed,"family":self.family,
                   "roles":self._roles,"channels":self._channels}
        tasks = [[t.start, t.target, t._shortest] for t in self.tasks()]
        def digest(x):
            return sha256(json.dumps(x, sort_keys=True,
                          separators=(",", ":")).encode("ascii")).hexdigest()
        return {
            "schema":"wsp62.world-receipt.v1",
            "seed":self.seed,"family":self.family,
            "hidden_source_sha256":digest(private),
            "heldout_sha256":digest(tasks),
            "tasks":len(tasks), "charged_actions":TRAIN_ACTIONS,
            "arbitrary_state_training_reset":False
        }


class Session:
    def __init__(self, world):
        self._world = world
        self.state = INITIAL
        self.ledger = []

    def step(self, action):
        if len(self.ledger) >= TRAIN_ACTIONS:
            raise ValueError("training actions exceeded")
        before = self.state
        after = self._world._step_oracle(before, action)
        self.state = after
        result = Experience(before, action, after)
        self.ledger.append(result)
        return result


def build_world(seed, cohort="SELFTEST"):
    if cohort != "SELFTEST" or type(seed) is not int or seed not in SEEDS:
        raise PermissionError("WSP62 protected or unregistered world forbidden")
    family = ("chain" if seed <= 2804 else
              "triple_xor" if seed <= 2808 else "xor_conjunction")
    r = _rng(seed, "hidden-roles")
    roles, channels = list(ACTIONS), list(ACTIONS)
    r.shuffle(roles)
    r.shuffle(channels)
    world = World(seed, family, tuple(roles), tuple(channels))
    assert len(set(world._roles)) == len(set(world._channels)) == 4
    assert len(world.tasks()) == TASKS_PER_WORLD
    return world
