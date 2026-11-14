"""H02 synthetic DEV-only causal world generator; evaluator owns hidden law.

Source policies see only observation/reward from reset/step (cooperative
boundary, not security against Python introspection). This module MUST NOT be
imported by the independently implemented symbolic model.
"""
from __future__ import annotations
import hashlib

DEV_IDS = tuple(range(16))
PROBES = (3, 5, 7, 11, 13, 17, 19, 23, 29, 37, 43, 53)
HELDOUT = (1, 2, 4, 6, 8, 10, 12, 15, 21, 25, 33, 51)
assert not set(PROBES).intersection(HELDOUT)


def _rank(tag: str, world: int, extra: int = 0) -> int:
    if type(world) is not int or world not in DEV_IDS:
        raise PermissionError("H02 DEV IDs only; original scientific worlds forbidden")
    return int.from_bytes(hashlib.sha256(
        f"WSP101-H02|DEV|{tag}|{world}|{extra}".encode("ascii")).digest(), "big")


def _hidden(world: int) -> tuple[int, int]:
    return _rank("FAMILY", world) % 4, 1 + _rank("MASK", world) % 63


def _effect(family: int, mask: int, probe: int) -> int:
    if type(probe) is not int or not 1 <= probe < 64:
        raise ValueError("H02_INVALID_PROBE")
    n = (probe & mask).bit_count()
    if family == 0:
        return n % 2
    if family == 1:
        return int(n >= 2)
    if family == 2:
        return (n % 2) ^ int((probe & 3) == 3)
    if family == 3:
        return int(n == 1)
    raise ValueError("H02_INVALID_FAMILY")


class _Evaluator:
    def __init__(self, world: int):
        self._world = world
        self._family, self._mask = _hidden(world)
        self._episode = 0
        self.reset()

    def reset(self):
        self._episode += 1
        self._pending = 0
        self._steps = 0
        self._probe = 0
        return 0

    def step(self, action: int) -> dict:
        if type(action) is not int or not 0 <= action < 64:
            raise ValueError("H02_INVALID_ACTION")
        if self._steps >= 2:
            raise ValueError("H02_EPISODE_STEP_LIMIT")
        if self._steps == 0:
            y = 0
            if action != 0:
                self._pending = _effect(self._family, self._mask, action)
                self._probe = action
        else:
            if action != 0:
                raise ValueError("H02_READOUT_ACTION_ZERO_ONLY")
            # A new fixed, domain-separated observation noise draw on every
            # reset. Source sees one noisy *consequence* per intervention.
            noisy = _rank("NOISE", self._world, self._probe * 65536 + self._episode) % 8 == 0
            y = self._pending ^ int(noisy and self._probe != 0)
        self._steps += 1
        return {"observation": y, "reward": y}


class PublicObserver:
    __slots__ = ("reset", "step")
    def __init__(self, instance: _Evaluator):
        self.reset = instance.reset
        self.step = instance.step


def observer(world: int):
    """Observer-facing API; oracle world/family/mask never returned."""
    if type(world) is not int or world not in DEV_IDS:
        raise PermissionError("original WSP101 cohorts are disallowed")
    return PublicObserver(_Evaluator(world))


def collect_active(world: int) -> tuple[tuple[int, int], ...]:
    endpoint = observer(world)
    rows = []
    for probe in PROBES:
        if endpoint.reset() != 0:
            raise ValueError("H02_RESET_LEAK")
        initial = endpoint.step(probe)
        final = endpoint.step(0)
        if initial != {"observation": 0, "reward": 0}:
            raise ValueError("H02_IMMEDIATE_CAUSAL_LEAK")
        if final["observation"] not in (0, 1) or final["reward"] != final["observation"]:
            raise ValueError("H02_INVALID_PUBLIC_RESULT")
        rows.append((probe, final["observation"]))
    return tuple(rows)


def collect_passive(world: int) -> tuple[tuple[int, int], ...]:
    endpoint = observer(world)
    rows = []
    for _ in PROBES:
        endpoint.reset()
        initial, final = endpoint.step(0), endpoint.step(0)
        if initial != {"observation": 0, "reward": 0} or final != initial:
            raise ValueError("H02_PASSIVE_LEAK")
        rows.append((0, final["observation"]))
    return tuple(rows)


def truth_for_auditor_only(world: int, probe: int) -> int:
    return _effect(*_hidden(world), probe)
