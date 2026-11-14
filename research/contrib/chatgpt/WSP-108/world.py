"""WSP108 prospective synthetic causal-world oracle, isolated from learners.

Only the evaluation harness invokes the private law oracle. Learners receive
public edge/action observations and 10 observed support consequences per world.
No external protected or historical benchmark data are read by this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import random

RELATIONS = (0, 1, 2)
KINDS = tuple((a, b) for a in RELATIONS for b in RELATIONS)
FIT_SEEDS = tuple(range(11001, 11013))
TRANSFER_SEEDS = tuple(range(21001, 21013))
QUERIES_PER_WORLD = 64
Edge = tuple[int, str, str]


def keyed_hash(kind: str, *parts: object) -> bytes:
    return sha256(("WSP108|" + kind + "|v1|" +
                   "|".join(str(p) for p in parts)).encode("ascii")).digest()


def entity(seed: int, scene: int, slot: object) -> str:
    return "e-" + keyed_hash("ENTITY", seed, scene, slot).hex()[:24]


def hidden_law(seed: int) -> frozenset[tuple[int, int]]:
    """Evaluator-only mechanism, never injected into learner modules."""
    if not isinstance(seed, int) or seed < 1:
        raise ValueError("positive world seed required")
    order = sorted(KINDS, key=lambda pair: (
        keyed_hash("LAW", seed, *pair), pair))
    return frozenset(order[:4])


@dataclass(frozen=True)
class Scene:
    seed: int
    scene_id: int
    source: str
    target: str
    before: tuple[Edge, ...]
    action: Edge
    add: bool

    def after(self) -> tuple[Edge, ...]:
        state = set(self.before)
        if self.add:
            if self.action in state:
                raise ValueError("action creates existing factual edge")
            state.add(self.action)
        else:
            if self.action not in state:
                raise ValueError("action retracts missing factual edge")
            state.remove(self.action)
        return tuple(sorted(state))


def support_scene(seed: int, i: int) -> Scene:
    """Nine isolated singleton action consequences plus no-path negative."""
    if i not in range(10):
        raise ValueError("support index must be 0..9")
    source, target = entity(seed, -i-1, "source"), entity(seed, -i-1, "target")
    middle = entity(seed, -i-1, "middle")
    if i < 9:
        r1, r2 = KINDS[i]
        return Scene(seed, -i-1, source, target,
                     ((r1, source, middle),),
                     (r2, middle, target), True)
    decoy = entity(seed, -i-1, "decoy")
    return Scene(seed, -i-1, source, target,
                 ((0, source, middle),),
                 (1, decoy, target), True)


def query_scene(seed: int, i: int) -> Scene:
    """Novel identities, 2..5 distinct mechanism paths, one causal action."""
    if i not in range(QUERIES_PER_WORLD):
        raise ValueError("query index out of frozen bound")
    rng = random.Random(int.from_bytes(keyed_hash("SCENE", seed, i), "big"))
    count = rng.randint(2, 5)
    kinds = rng.sample(KINDS, count)
    enabled = [bool(rng.getrandbits(1)) for _ in range(count)]
    toggle = rng.randrange(count)
    source, target = entity(seed, i, "source"), entity(seed, i, "target")
    edges: list[Edge] = []
    action: Edge | None = None
    for j, ((r1, r2), is_enabled) in enumerate(zip(kinds, enabled)):
        middle = entity(seed, i, j)
        edges.append((r1, source, middle))
        second = (r2, middle, target)
        if is_enabled:
            edges.append(second)
        if j == toggle:
            action = second
            add = not is_enabled
    assert action is not None
    return Scene(seed, i, source, target, tuple(sorted(edges)), action, add)


def path_features(edges: tuple[Edge, ...], source: str,
                  target: str) -> tuple[int, ...]:
    """Public observed edge-only, relation-pair two-hop existence indicators."""
    first: dict[str, set[int]] = {}
    second: dict[str, set[int]] = {}
    for relation, a, b in edges:
        if relation not in RELATIONS:
            raise ValueError("unexpected relation kind")
        if a == source:
            first.setdefault(b, set()).add(relation)
        if b == target:
            second.setdefault(a, set()).add(relation)
    found = set()
    for middle, left in first.items():
        for r1 in left:
            for r2 in second.get(middle, ()):
                found.add((r1, r2))
    return tuple(int(pair in found) for pair in KINDS)


def oracle(seed: int, edges: tuple[Edge, ...], source: str,
           target: str) -> bool:
    """Independent evaluator; only call on query data after predictions seal."""
    law = hidden_law(seed)
    first = [(r, mid) for r, a, mid in edges if a == source]
    following = {(r, a) for r, a, b in edges if b == target}
    return any((r1, r2) in law and (r2, mid) in following
               for r1, mid in first for r2 in RELATIONS)


def support_evidence(seed: int):
    """Ten observable action/outcome pairs, no access to private law bits."""
    result = []
    for i in range(10):
        scene = support_scene(seed, i)
        before = path_features(scene.before, scene.source, scene.target)
        after_edges = scene.after()
        after = path_features(after_edges, scene.source, scene.target)
        observed_consequence = oracle(seed, after_edges, scene.source, scene.target)
        if any(before):
            raise AssertionError("support scene leaked a pre-existing two-hop rule")
        if i < 9 and sum(after) != 1:
            raise AssertionError("singleton support not identifiable")
        if i == 9 and (sum(after) != 0 or observed_consequence):
            raise AssertionError("no-path negative support malformed")
        result.append((scene, before, after, observed_consequence))
    return tuple(result)
