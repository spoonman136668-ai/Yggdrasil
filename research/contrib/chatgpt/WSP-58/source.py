"""WSP58 evaluator-only prospective 12-world SELFTEST generator.

New, disjoint WSP58 SHA256 seed namespace; same four-operator permutation
distribution as WSP57 for isolated early-budget action-policy comparison.
Neither this module nor private operation tables enter learner imports.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from random import Random
import json

SEEDS = tuple(range(2401, 2413))
STATES = tuple(range(7))
OPS = tuple(range(4))
UNARY_INPUTS = (0, 2, 4)


@dataclass(frozen=True)
class Observation:
    kind: str
    first: int
    second: int | None
    before: int
    after: int
    action_cost: int = 1


def _nonaffine(table):
    return all(any(table[x] != ((a * x + b) % 7) for x in STATES)
               for a in STATES for b in STATES)


def _sample(seed):
    seed_bytes = sha256(f"WSP58|SELFTEST|operator-family|{seed}".encode("ascii")).digest()
    rng = Random(int.from_bytes(seed_bytes, "big"))
    tables = []
    for _ in range(10000):
        t = list(STATES)
        rng.shuffle(t)
        p = tuple(t)
        if p in tables or not _nonaffine(p):
            continue
        tables.append(p)
        if len(tables) == 4:
            return tuple(tables)
    raise RuntimeError("failed to sample four nonlinear permutation tables")


@dataclass(frozen=True)
class World:
    seed: int
    _private_tables: tuple[tuple[int, ...], ...]

    def unary(self):
        return tuple(Observation("unary", i, None, x, self._private_tables[i][x])
                     for i in OPS for x in UNARY_INPUTS)

    def query(self, first, second, before):
        if (type(first) is not int or type(second) is not int or
                type(before) is not int or first == second or
                first not in OPS or second not in OPS or before not in STATES):
            raise ValueError("invalid physical action")
        a = self._private_tables[first][before]
        b = self._private_tables[second][a]
        return Observation("pair", first, second, before, b)

    def receipt(self):
        payload = json.dumps({"seed": self.seed, "tables": self._private_tables},
                             sort_keys=True, separators=(",", ":")).encode("ascii")
        return {"schema": "wsp58.source-receipt.v1",
                "seed": self.seed,
                "hidden_world_sha256": sha256(payload).hexdigest(),
                "initial_charged_actions": len(self.unary()),
                "available_pair_actions": 84}


def build_world(seed, cohort="SELFTEST"):
    if cohort != "SELFTEST" or type(seed) is not int or seed not in SEEDS:
        raise PermissionError("WSP58 protected cohort or unregistered seed")
    world = World(seed, _sample(seed))
    assert len(world.unary()) == 12
    assert all(sorted(table) == list(STATES) and _nonaffine(table)
               for table in world._private_tables)
    assert len(set(world._private_tables)) == 4
    return world
