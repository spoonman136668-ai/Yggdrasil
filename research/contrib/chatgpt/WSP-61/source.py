"""WSP61 evaluator-only no-reset physical action-consequence world.

Training may step ONLY from a live session's current physical state, never
request arbitrary-state consequences. The evaluator has private oracle state
methods exclusively to generate heldout tasks and audit predictions.
No WSP59/60 source reuse; SELFTEST seeds 2701..2712 only.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from random import Random
import json

SEEDS = tuple(range(2701, 2713))
STATES = tuple(product((0, 1), repeat=4))
CHANNELS = tuple(range(4))
INITIAL = (0, 0, 0, 0)
TRAIN_ACTIONS = 80
TASKS_PER_WORLD = 32


def _rng(seed, label):
    digest = sha256(f"WSP61|SELFTEST|{seed}|{label}".encode("ascii")).digest()
    return Random(int.from_bytes(digest, "big"))


@dataclass(frozen=True)
class PublicExperience:
    before: tuple[int, ...]
    action: int
    after: tuple[int, ...]
    action_cost: int = 1


@dataclass(frozen=True)
class Task:
    start: tuple[int, ...]
    target: tuple[int, ...]
    _oracle_shortest: int


@dataclass(frozen=True)
class World:
    seed: int
    family: str
    _role_bits: tuple[int, ...]
    _channel_roles: tuple[int, ...]

    def _step_oracle(self, before, channel):
        if (type(before) is not tuple or before not in STATES or
                type(channel) is not int or channel not in CHANNELS):
            raise ValueError("invalid physical state/action")
        role = self._channel_roles[channel]
        b = list(before)
        bits = self._role_bits
        if role == 0:
            flip = True
        elif role == 1:
            flip = bool(before[bits[0]])
        elif role == 2:
            if self.family == "chain":
                flip = bool(before[bits[1]])
            else:
                flip = bool(before[bits[0]] ^ before[bits[1]] ^ before[bits[3]])
        elif role == 3:
            if self.family == "chain":
                flip = bool(before[bits[2]])
            else:
                flip = bool(before[bits[0]] ^ before[bits[1]] ^ before[bits[2]])
        else:
            raise RuntimeError("invalid private action role")
        if flip:
            b[bits[role]] ^= 1
        return tuple(b)

    def training_session(self):
        return Session(self)

    def _shortest(self, start, target, horizon=6):
        if start == target:
            return 0
        frontier = deque([(start, 0)])
        visited = {start}
        while frontier:
            state, steps = frontier.popleft()
            if steps >= horizon:
                continue
            for channel in CHANNELS:
                follow = self._step_oracle(state, channel)
                if follow == target:
                    return steps + 1
                if follow not in visited:
                    visited.add(follow)
                    frontier.append((follow, steps+1))
        return None

    def tasks(self):
        r = _rng(self.seed, "heldout-reachable-goals")
        candidates = []
        for start in STATES:
            for target in STATES:
                distance = self._shortest(start, target)
                if distance is not None and 2 <= distance <= 6:
                    candidates.append(Task(start, target, distance))
        if len(candidates) < TASKS_PER_WORLD:
            raise RuntimeError("insufficient 2-6 step reachable tasks")
        r.shuffle(candidates)
        return tuple(candidates[:TASKS_PER_WORLD])

    def evaluate(self, task, sequence):
        if sequence is None or type(sequence) not in (tuple, list) or len(sequence) > 6:
            return False
        state = task.start
        for channel in sequence:
            state = self._step_oracle(state, channel)
        return state == task.target

    def receipt(self):
        private = {
            "seed": self.seed, "family": self.family,
            "role_bits": self._role_bits, "channel_roles": self._channel_roles
        }
        tests = [[t.start, t.target, t._oracle_shortest] for t in self.tasks()]
        def digest(v):
            return sha256(json.dumps(v, separators=(",", ":"),
                                     sort_keys=True).encode("ascii")).hexdigest()
        return {
            "schema": "wsp61.no-reset-world.v1", "seed": self.seed,
            "family": self.family, "source_hash": digest(private),
            "heldout_task_hash": digest(tests), "tasks": len(tests),
            "actions_per_arm": TRAIN_ACTIONS,
            "arbitrary_state_training_reset": False
        }


class Session:
    """Stateful training interface: no reset or arbitrary-state query method."""
    def __init__(self, world):
        self._world = world
        self.state = INITIAL
        self.ledger = []

    def step(self, action):
        if len(self.ledger) >= TRAIN_ACTIONS:
            raise ValueError("charged no-reset physical action budget exceeded")
        before = self.state
        after = self._world._step_oracle(before, action)
        self.state = after
        result = PublicExperience(before, action, after)
        self.ledger.append(result)
        return result


def build_world(seed, cohort="SELFTEST"):
    if type(seed) is not int or seed not in SEEDS or cohort != "SELFTEST":
        raise PermissionError("WSP61 protected/unregistered world blocked")
    family = "chain" if seed <= 2706 else "triple_xor"
    rng = _rng(seed, "hidden-role-maps")
    roles = list(CHANNELS)
    channels = list(CHANNELS)
    rng.shuffle(roles)
    rng.shuffle(channels)
    world = World(seed, family, tuple(roles), tuple(channels))
    assert len(world.tasks()) == TASKS_PER_WORLD
    assert len(set(world._role_bits)) == 4
    assert len(set(world._channel_roles)) == 4
    return world
