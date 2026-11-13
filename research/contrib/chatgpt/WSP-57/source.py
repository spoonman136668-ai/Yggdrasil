"""WSP57 evaluator-only causal physics. No learner import or oracle exposure.

Four source-hidden unknown non-affine permutations over physical state 0..6.
The public interface releases one charged action-consequence observation at a
time, after the experimental arm chooses its intervention. SELFTEST only.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from random import Random
import json

SEEDS = (2301, 2302, 2303, 2304, 2305, 2306)
UNARY_INPUTS = (0, 2, 4)
OP_COUNT = 4
STATE_COUNT = 7


@dataclass(frozen=True)
class Observation:
    kind: str
    first: int
    second: int | None
    before: int
    after: int
    action_cost: int = 1


def _nonaffine(f):
    return all(any(f[x] != (a * x + b) % 7 for x in range(7))
               for a in range(7) for b in range(7))


def _ops(seed):
    digest = sha256(f"WSP57|SELFTEST|operators|{seed}".encode("ascii")).digest()
    r = Random(int.from_bytes(digest, "big"))
    ops = []
    for attempt in range(10000):
        candidate = list(range(STATE_COUNT))
        r.shuffle(candidate)
        t = tuple(candidate)
        if not _nonaffine(t) or t in ops:
            continue
        ops.append(t)
        if len(ops) == OP_COUNT:
            return tuple(ops)
    raise RuntimeError("unable to sample nonlinear physics")


@dataclass(frozen=True)
class World:
    seed: int
    _operators: tuple[tuple[int, ...], ...]

    def unary(self):
        return tuple(
            Observation("unary", op, None, x, self._operators[op][x])
            for op in range(OP_COUNT) for x in UNARY_INPUTS
        )

    def query(self, first, second, x):
        if (type(first) is not int or type(second) is not int or
                type(x) is not int or first == second or
                not (0 <= first < OP_COUNT and 0 <= second < OP_COUNT
                     and 0 <= x < STATE_COUNT)):
            raise ValueError("invalid pair intervention")
        after = self._operators[second][self._operators[first][x]]
        return Observation("pair", first, second, x, after)

    def receipt(self):
        data = {"seed": self.seed, "tables": self._operators}
        return {
            "schema": "wsp57.source.v1", "seed": self.seed,
            "source_sha256": sha256(json.dumps(data, sort_keys=True).encode("ascii")).hexdigest(),
            "unary_actions": len(self.unary()),
            "possible_pair_queries": OP_COUNT * (OP_COUNT - 1) * STATE_COUNT
        }

    def audit(self):
        assert len(self._operators) == 4
        assert all(sorted(p) == list(range(STATE_COUNT)) and _nonaffine(p)
                   for p in self._operators)
        assert len(set(self._operators)) == 4
        assert self.receipt()["unary_actions"] == 12


def build_world(seed, cohort="SELFTEST"):
    if cohort != "SELFTEST" or type(seed) is not int or seed not in SEEDS:
        raise PermissionError("WSP57 source is SELFTEST only")
    result = World(seed, _ops(seed))
    result.audit()
    return result
