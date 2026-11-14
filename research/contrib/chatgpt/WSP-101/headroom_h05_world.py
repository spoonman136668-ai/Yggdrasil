"""WSP101 H05: new, separate synthetic delayed-causal DEV oracle.

The model-facing interface returns public observations/rewards ONLY. The
new coefficients and cubic correction indices are evaluator-only. This is
an API discipline, not a Python reflection security boundary.
"""
from __future__ import annotations
import hashlib
from itertools import combinations

from headroom_h04_world import _effect as _quadratic_effect, SOURCE_ACTIONS

DEV_IDS = tuple(range(32))
TRIPLES = tuple(combinations(range(10), 3))
REPAIR_ACTIONS = (
    932,710,430,811,316,617,702,890,756,371,662,941,803,574,856,842,
    468,335,923,62,692,462,623,254,620,527,315,159,822,1013,902,909,
    899,683,929,433,223,817,1012,1004,501,997,758,837,597,248,419,362
)
HELDOUT = tuple(x for x in range(1024)
                if x.bit_count() >= 3 and x not in REPAIR_ACTIONS)
READOUT = 1024
NOOP = 1025
assert len(TRIPLES) == 120 and len(REPAIR_ACTIONS) == 48 and len(HELDOUT) == 920
assert len(SOURCE_ACTIONS) == 56 and not set(REPAIR_ACTIONS) & set(SOURCE_ACTIONS)
assert not set(HELDOUT) & (set(REPAIR_ACTIONS) | set(SOURCE_ACTIONS))


def _world_seed(world, label, index=0):
    if type(world) is not int or world not in DEV_IDS:
        raise PermissionError("H05 only NEW DEV identities 0..31")
    data = f"WSP101-H05|DEV|{world}|{label}|{index}".encode("ascii")
    return hashlib.sha256(data).digest()


def _unknown_program(world):
    quadratic = int.from_bytes(_world_seed(world, "QUAD")[:7], "little")
    count = world % 3
    ranked = sorted(
        range(120), key=lambda i: (_world_seed(world, "CUBIC", i), i)
    )
    return quadratic, tuple(sorted(ranked[:count]))


def _result(quadratic, cubic_terms, action):
    if type(action) is not int or not 0 <= action < 1024:
        raise ValueError("H05 10-bit intervention required")
    y = _quadratic_effect(quadratic, action)
    for term in cubic_terms:
        mask = sum(1 << i for i in TRIPLES[term])
        y ^= int(action & mask == mask)
    return y


class _World:
    def __init__(self, world):
        self._quadratic, self._cubics = _unknown_program(world)
        self.reset()

    def reset(self):
        self._stage = 0
        self._pending = 0
        return 0

    def step(self, action):
        if type(action) is not int:
            raise ValueError("H05 integer action required")
        if self._stage >= 2:
            raise ValueError("H05 two-action episode exhausted")
        if self._stage == 0:
            if action == NOOP:
                self._pending = 0
            elif 0 <= action < 1024:
                self._pending = _result(self._quadratic, self._cubics, action)
            else:
                raise ValueError("H05 unknown intervention")
            observation = 0
        else:
            if action != READOUT:
                raise ValueError("H05 expected readout")
            observation = self._pending
        self._stage += 1
        return {"observation": observation, "reward": observation}


class PublicEndpoint:
    __slots__ = ("reset", "step")

    def __init__(self, world):
        self.reset = world.reset
        self.step = world.step


def observer(world):
    if type(world) is not int or world not in DEV_IDS:
        raise PermissionError("H05 original/protected world IDs unavailable")
    return PublicEndpoint(_World(world))


def _observed(world, actions):
    endpoint = observer(world)
    source = []
    for action in actions:
        if endpoint.reset() != 0:
            raise ValueError("H05 reset leaked truth")
        immediate = endpoint.step(action)
        delayed = endpoint.step(READOUT)
        if (immediate != {"observation": 0, "reward": 0}
            or type(delayed.get("observation")) is not int
            or delayed["observation"] not in (0, 1)
            or delayed.get("reward") != delayed["observation"]):
            raise ValueError("H05 malformed public outcome")
        source.append((action, delayed["observation"]))
    return tuple(source)


def observed_basis(world):
    return _observed(world, SOURCE_ACTIONS)


def observed_repair(world):
    return _observed(world, REPAIR_ACTIONS)


def observed_passive(world):
    endpoint = observer(world)
    endpoint.reset()
    a, b = endpoint.step(NOOP), endpoint.step(READOUT)
    if a != {"observation": 0, "reward": 0} or b != a:
        raise ValueError("H05 passive observation leak")
    return (a, b)


def evaluator_truth_only(world, action, *, unknown_tenway=False):
    q, cubic = _unknown_program(world)
    output = _result(q, cubic, action)
    if unknown_tenway:
        output ^= int(action == 1023)
    return output
