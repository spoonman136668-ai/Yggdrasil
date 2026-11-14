"""Independent synthetic observation source for novel relational worlds.

Public paid observations are the ONLY model-facing inputs. Evaluator truth
is not used by weights or the independent graph control.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import random


@dataclass(frozen=True)
class Observation:
    relation: str
    source: str
    target: str
    present: bool = True


@dataclass(frozen=True)
class World:
    seed: int
    entities_a: tuple[str, ...]
    entities_b: tuple[str, ...]
    relations_a: tuple[str, ...]
    relations_b: tuple[str, ...]
    stage_a: tuple[Observation, ...]
    stage_b: tuple[Observation, ...]
    truth_a: frozenset[tuple[str, str, str]]
    truth_b: frozenset[tuple[str, str, str]]


def digest_text(seed: int, kind: str, index: int) -> str:
    raw = hashlib.sha256(
        f"WSP87|UNREGISTERED|{seed}|{kind}|{index}|v1".encode("ascii")
    ).digest()
    alphabet = "bcdfghjklmnpqrstvwxz"
    return "".join(alphabet[b % len(alphabet)] for b in raw[:12]) + "-" + str(index)


def path(seed: int, slot: int, count: int) -> tuple[int, ...]:
    raw = hashlib.sha256(f"WSP87|ORDER|{seed}|{slot}|v1".encode("ascii")).digest()
    rng = random.Random(int.from_bytes(raw[:8], "big"))
    result = list(range(count))
    rng.shuffle(result)
    return tuple(result)


def make_world(seed: int) -> World:
    if not isinstance(seed, int) or seed < 1:
        raise ValueError("valid positive synthetic world seed required")
    names = tuple(digest_text(seed, "entity", i) for i in range(16))
    relations = tuple(digest_text(seed, "relation", i) for i in range(3))
    p0, p1 = path(seed, 0, 12), path(seed, 1, 12)
    p2 = path(seed, 2, 16)

    def edges(p: tuple[int, ...], relation: str):
        return [Observation(relation, names[a], names[b])
                for a, b in zip(p, p[1:])]

    a = edges(p0, relations[0]) + edges(p1, relations[1])
    b = edges(p2, relations[2])
    extension = (p0[-1], 12, 13, 14, 15)
    b += edges(extension, relations[0])
    for i, j in ((2, 8), (7, 3)):
        b.append(Observation(relations[1], names[p1[i]], names[p1[i + 1]], False))
        b.append(Observation(relations[1], names[p1[i]], names[p1[j]], True))

    original = {(o.relation, o.source, o.target) for o in a}
    updated = set(original)
    for obs in b:
        key = (obs.relation, obs.source, obs.target)
        if obs.present:
            updated.add(key)
        else:
            updated.discard(key)
    assert len(a) == 22 and len(b) == 23 and len(names) == len(set(names))
    return World(seed, names[:12], names, relations[:2], relations,
                 tuple(a), tuple(b), frozenset(original), frozenset(updated))


def oracle(edges: frozenset[tuple[str, str, str]],
           relation: str, source: str, target: str, hops: int) -> bool:
    if hops == 1:
        return (relation, source, target) in edges
    if hops == 2:
        return any(r == relation and a == source and
                   (relation, b, target) in edges for r, a, b in edges)
    raise ValueError("unsupported exact-hop query")
