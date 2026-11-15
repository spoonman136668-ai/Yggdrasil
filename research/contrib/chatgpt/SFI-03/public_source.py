"""SFI-03 PUBLIC diagnostic source owner: novel forms relative to SFI-02's DSL.

Private family/shift are never included in the six-field public transition.
This is synthetic public-development evidence, NOT a blinded scientific evaluator.
"""
from collections import namedtuple
from hashlib import sha256
import random

ACTIONS = 8
EXPLORE = 24
SCORE = 16
WORLD_SEEDS = tuple(range(880300, 880332))
Prior = namedtuple("Prior", "before action reward after done")
Step = namedtuple("Step", "before action after reward done history")


def _rng(seed, label):
    return random.Random(int.from_bytes(
        sha256(f"SFI03-PUBLIC-v1/{seed}/{label}".encode()).digest()[:16], "big"))


def _family_op(family, prev, older):
    if family == 0:
        return prev & older
    if family == 1:
        return prev | older
    if family == 2:
        return prev & (~older & 7)
    if family == 3:
        return ~(prev & older) & 7
    raise ValueError("SFI03_UNKNOWN_PRIVATE_FAMILY")


def target(family, shift, prev, older, context):
    return _family_op(family, prev, older) ^ shift ^ (4 if context else 0)


def exploration(seed):
    if type(seed) is not int or seed not in WORLD_SEEDS:
        raise PermissionError("SFI03_ONLY_PUBLIC_DEVELOPMENT_SEEDS")
    rng = _rng(seed, "EXPLORATION")
    return tuple(rng.randrange(ACTIONS) for _ in range(EXPLORE))


class PublicWorld:
    __slots__ = ("_family", "_shift", "_contexts", "_noise", "_events",
                 "_streak", "_steps", "state")

    def __init__(self, seed):
        if type(seed) is not int or seed not in WORLD_SEEDS:
            raise PermissionError("SFI03_ONLY_PUBLIC_DEVELOPMENT_SEEDS")
        index = seed - WORLD_SEEDS[0]
        self._family, self._shift = divmod(index, 8)
        rng, noise = _rng(seed, "CONTEXT"), _rng(seed, "PUBLIC-NOISE")
        self._contexts = tuple(rng.randrange(2) for _ in range(EXPLORE + SCORE + 1))
        self._noise = tuple(tuple(noise.randrange(16) for _ in range(4))
                            for _ in range(EXPLORE + SCORE + 1))
        self._events = []
        self._streak = 0
        self._steps = 0
        self.state = self._state()

    def _state(self):
        return ((self._contexts[self._steps], self._streak,
                 self._events[-1].action if self._events else 15,
                 self._events[-2].action if len(self._events) >= 2 else 15)
                + self._noise[self._steps])

    def public_history(self):
        return tuple(self._events[-16:])

    def step(self, action):
        if type(action) is not int or not 0 <= action < ACTIONS:
            raise ValueError("SFI03_ACTION")
        if self._steps >= EXPLORE + SCORE:
            raise ValueError("SFI03_WORLD_BUDGET")
        before, history = self.state, self.public_history()
        if len(self._events) < 3:
            reward, done = 0., False
        else:
            eligible, older = self._events[-2], self._events[-3].action
            older2 = self._events[-4].action if len(self._events) >= 4 else 0
            match = eligible.action == target(
                self._family, self._shift, older, older2, eligible.before[0] & 1)
            self._streak = self._streak + 1 if match else 0
            done = self._streak >= 3
            reward = 1. if done else (.25 if match else -.25)
        self._steps += 1
        if done:
            self._streak = 0
            self._events.clear()
        else:
            self._events.append(Prior(before, action, reward, (), False))
        after = self._state()
        if not done:
            self._events[-1] = Prior(before, action, reward, after, False)
        self.state = after
        return Step(before, action, after, reward, done, history)


def oracle_action(world):
    history = world.public_history()
    if not history:
        return 0
    return target(world._family, world._shift, history[-1].action,
                  history[-2].action if len(history) >= 2 else 0,
                  world.state[0] & 1)
