"""WSP101 H04: unrelated DEV causal-world oracle with delayed consequences.

No original FIT/TRANSFER/NOVEL/RESERVED sources, donor model or other
projects. Never import this module into the independently coded solvers.
"""
from __future__ import annotations

import hashlib

DEV_IDS = tuple(range(32))
BITS = 10
SOURCE_ACTIONS = (
    (0,)
    + tuple(1 << i for i in range(BITS))
    + tuple((1 << i) | (1 << j)
            for i in range(BITS) for j in range(i + 1, BITS))
)
HELDOUT_ACTIONS = tuple(x for x in range(1 << BITS) if x.bit_count() >= 3)
READOUT = 1024
NOOP = 1025
assert len(SOURCE_ACTIONS) == 56
assert len(HELDOUT_ACTIONS) == 968
assert not set(SOURCE_ACTIONS) & set(HELDOUT_ACTIONS)


def _coefficients(world: int) -> int:
    if type(world) is not int or world not in DEV_IDS:
        raise PermissionError("H04 only NEW DEV world identities 0..31")
    return int.from_bytes(
        hashlib.sha256(
            f"WSP101-H04|DEV|{world}|COEFF".encode("ascii")
        ).digest()[:7], "little"
    )


def _effect(coeff: int, x: int) -> int:
    if type(coeff) is not int or not 0 <= coeff < (1 << 56):
        raise ValueError("H04 coefficient width")
    if type(x) is not int or not 0 <= x < (1 << BITS):
        raise ValueError("H04 intervention width")
    result = coeff & 1
    index = 1
    for i in range(BITS):
        result ^= ((coeff >> index) & 1) & ((x >> i) & 1)
        index += 1
    for i in range(BITS):
        for j in range(i + 1, BITS):
            result ^= ((coeff >> index) & 1) & ((x >> i) & 1) & ((x >> j) & 1)
            index += 1
    return result


class _Oracle:
    def __init__(self, world: int):
        self._coeff = _coefficients(world)
        self.reset()

    def reset(self):
        self._stage = 0
        self._pending = 0
        return 0

    def step(self, action: int) -> dict:
        if type(action) is not int:
            raise ValueError("H04 intervention must be integer")
        if self._stage >= 2:
            raise ValueError("H04 episode limit")
        if self._stage == 0:
            if action == NOOP:
                self._pending = 0
            elif 0 <= action < (1 << BITS):
                self._pending = _effect(self._coeff, action)
            else:
                raise ValueError("H04 expected action or NOOP")
            observed = 0
        else:
            if action != READOUT:
                raise ValueError("H04 second action must be READOUT")
            observed = self._pending
        self._stage += 1
        return {"observation": observed, "reward": observed}


class PublicEndpoint:
    """Cooperative source-facing interface; not reflection-proof."""
    __slots__ = ("reset", "step")

    def __init__(self, oracle):
        self.reset = oracle.reset
        self.step = oracle.step


def observer(world: int):
    if type(world) is not int or world not in DEV_IDS:
        raise PermissionError("H04 original WSP101 cohorts unavailable")
    return PublicEndpoint(_Oracle(world))


def observed_source(world: int):
    endpoint = observer(world)
    events = []
    for action in SOURCE_ACTIONS:
        if endpoint.reset() != 0:
            raise ValueError("H04 source reset leak")
        first = endpoint.step(action)
        second = endpoint.step(READOUT)
        if (first != {"observation": 0, "reward": 0}
            or type(second.get("observation")) is not int
            or second["observation"] not in (0, 1)
            or second.get("reward") != second["observation"]):
            raise ValueError("H04 invalid action consequence")
        events.append((action, second["observation"]))
    return tuple(events)


def observed_passive(world: int):
    endpoint = observer(world)
    endpoint.reset()
    a = endpoint.step(NOOP)
    b = endpoint.step(READOUT)
    if a != {"observation": 0, "reward": 0} or b != a:
        raise ValueError("H04 passive causal leak")
    return (a, b)


def evaluator_truth_only(world: int, action: int, *, cubic: bool = False):
    true_response = _effect(_coefficients(world), action)
    # A cubic term is provably invisible at every source weight<=2 mask.
    return true_response ^ (int((action & 0b111) == 0b111) if cubic else 0)
