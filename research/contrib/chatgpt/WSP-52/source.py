"""WSP52 deterministic *source only*: no learner, evaluation, or PRIMARY execution.

Public synthetic worlds use a prefix-free, undelimited binary acoustic language.
The learner-facing view contains only raw streams and observed physical states.
Never pass a SourceWorld instance, a latent triple, or a codebook to a learner.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import permutations, product
from collections import Counter

ENTITIES, DESTINATIONS, VERBS = 8, 4, 3
TRIPLES = tuple(product(range(ENTITIES), range(DESTINATIONS), range(VERBS)))
ORDERS = tuple(permutations(range(3)))
ENCODINGS = ("identity", "permuted", "rotated")
VALID_SEEDS = {"DEV": (101, 103, 107), "PRIMARY": (1201, 1213, 1237, 1249)}
TEST_COHORT = "SELFTEST"  # Fixture-only cohort; never score as DEV or PRIMARY.


@dataclass(frozen=True)
class Observation:
    """The entire learner-visible source record; no token or role labels."""
    before: tuple[int, ...]
    acoustic_bits: str
    after: tuple[int, ...]
    action_cost: int = 1
    reset_cost: int = 0


@dataclass(frozen=True)
class SourceWorld:
    """Evaluator-owned object: keep all fields inaccessible to learner code."""
    cohort: str
    seed: int
    encoding: str
    phase_a: tuple[Observation, ...]
    phase_b: tuple[Observation, ...]
    heldout_a: tuple[Observation, ...]
    heldout_b: tuple[Observation, ...]
    # These latent fields are evaluator-only and MUST NOT be serialized to learner.
    _codebook: tuple[str, ...]
    _orders: tuple[tuple[int, ...], tuple[int, ...]]
    _train_a_triples: tuple[tuple[int, int, int], ...]
    _train_b_triples: tuple[tuple[int, int, int], ...]

    def source_receipt(self) -> dict:
        """Safe metadata, never the hidden grammar or lexical mapping."""
        def digest(rows: tuple[Observation, ...]) -> str:
            lines = (f"{r.before}|{r.acoustic_bits}|{r.after}|{r.action_cost}|{r.reset_cost}\n" for r in rows)
            return sha256("".join(lines).encode("ascii")).hexdigest()
        return {"cohort": self.cohort, "seed": self.seed, "encoding": self.encoding,
                "train_a_count": len(self.phase_a), "train_b_count": len(self.phase_b),
                "heldout_a_count": len(self.heldout_a), "heldout_b_count": len(self.heldout_b),
                "train_a_sha256": digest(self.phase_a), "train_b_sha256": digest(self.phase_b),
                "heldout_a_sha256": digest(self.heldout_a), "heldout_b_sha256": digest(self.heldout_b),
                "exposed_actions": len(self.phase_a) + len(self.phase_b),
                "exposed_resets": sum(o.reset_cost for o in self.phase_a + self.phase_b)}

    def audit(self) -> None:
        assert len(self._codebook) == 15 == len(set(self._codebook))
        assert sorted(map(len, self._codebook)) == sorted([4] * 2 + [5] * 7 + [6] * 6)
        assert all(not a.startswith(b) for a in self._codebook for b in self._codebook if a != b)
        assert self._orders[0] != self._orders[1] and self._orders[0] in ORDERS and self._orders[1] in ORDERS
        assert len(self.phase_a) == len(set(self._train_a_triples)) == 36
        assert len(self.phase_b) == len(set(self._train_b_triples)) == 6
        assert len(self.heldout_a) == 60 and len(self.heldout_b) == 90
        counts = [Counter(t[i] for t in self._train_a_triples) for i in range(3)]
        assert all(min(c.values()) >= 2 for c in counts)
        assert [len(c) for c in counts] == [8, 4, 3]
        assert len({o.acoustic_bits for o in self.phase_a + self.heldout_a}) == 96
        assert len({o.acoustic_bits for o in self.phase_b + self.heldout_b}) == 96
        assert not ({o.acoustic_bits for o in self.phase_a} & {o.acoustic_bits for o in self.heldout_a})
        assert not ({o.acoustic_bits for o in self.phase_b} & {o.acoustic_bits for o in self.heldout_b})
        assert set(o.action_cost for o in self.phase_a + self.phase_b) == {1}
        assert sum(o.action_cost for o in self.phase_a + self.phase_b) == 42
        assert sum(o.reset_cost for o in self.phase_a + self.phase_b) == 0


class _Keyed:
    def __init__(self, cohort: str, seed: int, encoding: str):
        self.key = f"WSP52|{cohort}|{seed}|{encoding}|"

    def below(self, component: str, index: int, limit: int) -> int:
        if limit < 1:
            raise ValueError("invalid bound")
        threshold = (1 << 256) - ((1 << 256) % limit)
        for counter in range(1000):  # byte-counter rejection removes modulo bias
            raw = f"{self.key}{component}/{index}|{counter}".encode("ascii")
            value = int.from_bytes(sha256(raw).digest(), "big")
            if value < threshold:
                return value % limit
        raise RuntimeError("unreachable keyed PRNG rejection cap")

    def shuffle(self, values: tuple, component: str, attempt: int = 0) -> tuple:
        result = list(values)
        for i in range(len(result) - 1, 0, -1):
            j = self.below(component, attempt * 128 + i, i + 1)
            result[i], result[j] = result[j], result[i]
        return tuple(result)


def _codebook(rng: _Keyed, encoding: str) -> tuple[str, ...]:
    chosen: list[str] = []
    for position, length in enumerate([4] * 2 + [5] * 7 + [6] * 6):
        possible = [f"{x:0{length}b}" for x in range(1 << length)]
        possible = [w for w in possible if all(not w.startswith(s) and not s.startswith(w) for s in chosen)]
        selected = possible[rng.below("word", position, len(possible))]
        chosen.append(selected)
    chosen = list(rng.shuffle(tuple(chosen), "lexical-address"))
    if encoding == "permuted":
        mask = tuple(rng.below("mask", i, 2) for i in range(6))
    elif encoding == "rotated":
        shift = rng.below("depth-shift", 0, 2)
        mask = tuple((i + shift) % 2 for i in range(6))
    else:
        mask = (0,) * 6
    return tuple("".join(str(int(bit) ^ mask[i]) for i, bit in enumerate(word)) for word in chosen)


def _apply(before: tuple[int, ...], triple: tuple[int, int, int]) -> tuple[int, ...]:
    entity, destination, verb = triple
    updated = list(before)
    updated[entity] = (destination + verb) % 4
    return tuple(updated)


def _utterance(triple: tuple[int, int, int], words: tuple[str, ...], order: tuple[int, ...]) -> str:
    entity, destination, verb = triple
    names = (words[entity], words[8 + destination], words[12 + verb])
    return "".join(names[i] for i in order)


def build_world(cohort: str, seed: int, encoding: str, *, primary_admitted: bool = False) -> SourceWorld:
    """Only prepare source. The PRIMARY gate defaults closed; no learning is run here."""
    if cohort not in (*VALID_SEEDS, TEST_COHORT):
        raise ValueError("unregistered cohort")
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise ValueError("invalid seed")
    if cohort in VALID_SEEDS and seed not in VALID_SEEDS[cohort]:
        raise ValueError("unregistered seed")
    if cohort == TEST_COHORT and seed not in (9001, 9002):
        raise ValueError("SELFTEST is restricted to two non-study fixture seeds")
    if cohort == "PRIMARY" and not primary_admitted:
        raise PermissionError("PRIMARY first-use requires separately recorded project-owner admission")
    if encoding not in ENCODINGS:
        raise ValueError("invalid encoding")
    rng = _Keyed(cohort, seed, encoding)
    words = _codebook(rng, encoding)
    order_a = ORDERS[rng.below("order-a", 0, len(ORDERS))]
    order_b = ORDERS[(ORDERS.index(order_a) + 1 + rng.below("order-b", 0, 5)) % 6]
    train_a = None
    for attempt in range(1024):
        tentative = rng.shuffle(TRIPLES, "a-examples", attempt)[:36]
        if all(len({t[i] for t in tentative}) == n and
               min(Counter(t[i] for t in tentative).values()) >= 2
               for i, n in enumerate((8, 4, 3))):
            train_a = tentative
            break
    if train_a is None:
        raise RuntimeError("failed to construct covered training source")
    train_b = rng.shuffle(TRIPLES, "b-examples")[:6]
    initial = tuple(rng.below("initial-state", i, 4) for i in range(8))
    cursor = initial
    def evidence(triples, order, sequential):
        nonlocal cursor
        rows = []
        for triple in triples:
            before = cursor if sequential else initial
            after = _apply(before, triple)
            rows.append(Observation(before, _utterance(triple, words, order), after))
            if sequential:
                cursor = after
        return tuple(rows)
    phase_a = evidence(train_a, order_a, True)
    heldout_a = evidence(tuple(t for t in TRIPLES if t not in set(train_a)), order_a, False)
    phase_b = evidence(train_b, order_b, True)
    heldout_b = evidence(tuple(t for t in TRIPLES if t not in set(train_b)), order_b, False)
    world = SourceWorld(cohort, seed, encoding, phase_a, phase_b, heldout_a,
                        heldout_b, words, (order_a, order_b), train_a, train_b)
    world.audit()
    return world


def identifiability_warning() -> str:
    """Known simulator observational symmetry; do not claim separately learned concepts."""
    return ("Location effects depend only on (destination+verb) mod 4. "
            "Without independently grounded anchors, destination/verb semantics "
            "are not uniquely identifiable even with all physical outcomes.")
