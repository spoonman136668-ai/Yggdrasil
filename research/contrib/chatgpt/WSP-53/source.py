"""WSP-53 deterministic, SOURCE-ONLY physics worlds. No learner or science run.

Every learning arm receives only public Observation records. SourceWorld, hidden
codebooks, role orders and semantic triples remain evaluator-owned. This module
is an implementation substrate, NOT scientific evidence or first-use authority.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from itertools import permutations, product

FAMILIES = ("anchored_effect", "noncommuting_order")
ENCODINGS = ("identity", "permuted", "rotated")
SEEDS = {"SELFTEST": (9901, 9902), "DEV": (3101, 3109, 3119),
         "PRIMARY": (5101, 5107, 5113, 5119)}
ORDERS = tuple(permutations((0, 1, 2)))
A_COUNT, B_COUNT = 48, 12


@dataclass(frozen=True)
class Observation:
    before: tuple[int, ...]
    acoustic_bits: str
    after: tuple[int, ...]
    action_cost: int = 1
    reset_cost: int = 0


class _Keyed:
    def __init__(self, family: str, cohort: str, seed: int, encoding: str):
        self.key = f"WSP53|{family}|{cohort}|{seed}|{encoding}|"

    def below(self, label: str, n: int, limit: int) -> int:
        if limit <= 0:
            raise ValueError("empty candidate space")
        cutoff = (1 << 256) - ((1 << 256) % limit)
        for nonce in range(1024):
            message = f"{self.key}{label}|{n}|{nonce}".encode("ascii")
            value = int.from_bytes(sha256(message).digest(), "big")
            if value < cutoff:
                return value % limit
        raise RuntimeError("SHA256 rejection bound exceeded")

    def shuffle(self, values: tuple, label: str, n: int = 0) -> tuple:
        out = list(values)
        for i in range(len(out) - 1, 0, -1):
            j = self.below(label, n * 256 + i, i + 1)
            out[i], out[j] = out[j], out[i]
        return tuple(out)


def _codebook(rng: _Keyed, family: str, encoding: str) -> tuple[str, ...]:
    lengths = ([4] * 2 + [5] * 7 + [6] * 6 if family == "anchored_effect"
               else [4] * 2 + [5] * 6 + [6] * 4)
    selected = []
    for i, length in enumerate(lengths):
        candidates = (format(x, f"0{length}b") for x in range(1 << length))
        available = [word for word in candidates if all(
            not word.startswith(old) and not old.startswith(word)
            for old in selected)]
        selected.append(available[rng.below("codeword", i, len(available))])
    shuffled = rng.shuffle(tuple(selected), "assign-lexicon")
    if encoding == "identity":
        mask = (0,) * 6
    elif encoding == "permuted":
        mask = tuple(rng.below("code-mask", i, 2) for i in range(6))
    else:
        rotate = rng.below("code-rotate", 0, 2)
        mask = tuple((i + rotate) % 2 for i in range(6))
    return tuple("".join(str(int(bit) ^ mask[j]) for j, bit in
                         enumerate(word)) for word in shuffled)


def _apply(family: str, before: tuple[int, ...],
           triple: tuple[int, int, int]) -> tuple[int, ...]:
    entity, first, second = triple
    out = list(before)
    if family == "anchored_effect":
        # Eight positions plus eight independent orientation registers.
        out[entity] = (first + second) % 4
        out[8 + entity] = (before[8 + entity] + second + 1) % 3
    elif family == "noncommuting_order":
        value = before[entity]
        def operate(v: int, op: int) -> int:
            return ((v + 1) % 7, (2 * v) % 7, 2, (-v) % 7)[op]
        out[entity] = operate(operate(value, first), second)
    else:
        raise ValueError("invalid source family")
    return tuple(out)


def _utterance(family: str, triple: tuple[int, int, int],
               words: tuple[str, ...], order: tuple[int, ...]) -> str:
    entity, first, second = triple
    if family == "anchored_effect":
        pieces = (words[entity], words[8 + first], words[12 + second])
    else:
        pieces = (words[entity], words[8 + first], words[8 + second])
    return "".join(pieces[i] for i in order)


def _hash_rows(rows: tuple[Observation, ...]) -> str:
    msg = "".join(f"{r.before}|{r.acoustic_bits}|{r.after}|"
                  f"{r.action_cost}|{r.reset_cost}\n" for r in rows)
    return sha256(msg.encode("ascii")).hexdigest()


@dataclass(frozen=True)
class SourceWorld:
    """Evaluator-only context. Never send this object to a learner."""
    family: str
    cohort: str
    seed: int
    encoding: str
    phase_a: tuple[Observation, ...]
    phase_b: tuple[Observation, ...]
    heldout_a: tuple[Observation, ...]
    heldout_b: tuple[Observation, ...]
    _codebook: tuple[str, ...]
    _orders: tuple[tuple[int, ...], tuple[int, ...]]
    _initial: tuple[int, ...]
    _a_triples: tuple[tuple[int, int, int], ...]
    _b_triples: tuple[tuple[int, int, int], ...]
    _all_triples: tuple[tuple[int, int, int], ...]

    def source_receipt(self) -> dict:
        return {
            "schema": "wsp53.source-receipt.v1", "family": self.family,
            "cohort": self.cohort, "seed": self.seed, "encoding": self.encoding,
            "phase_a": (len(self.phase_a), _hash_rows(self.phase_a)),
            "phase_b": (len(self.phase_b), _hash_rows(self.phase_b)),
            "heldout_a": (len(self.heldout_a), _hash_rows(self.heldout_a)),
            "heldout_b": (len(self.heldout_b), _hash_rows(self.heldout_b)),
            "charged_actions": sum(x.action_cost for x in
                                   self.phase_a + self.phase_b),
            "charged_resets": sum(x.reset_cost for x in
                                  self.phase_a + self.phase_b),
        }

    def order_counterworld_audit(self) -> dict:
        if self.family != "noncommuting_order":
            raise ValueError("order pairs apply only to noncommuting world")
        heldout = set(self._all_triples) - set(self._b_triples)
        eligible, differing = 0, 0
        for entity, first, second in sorted(heldout):
            swapped = (entity, second, first)
            if first < second and swapped in heldout:
                eligible += 1
                differing += (_apply(self.family, self._initial,
                                      (entity, first, second)) !=
                              _apply(self.family, self._initial, swapped))
        return {"eligible_pairs": eligible, "distinguishable_pairs": differing}

    def audit(self) -> None:
        expected = 15 if self.family == "anchored_effect" else 12
        assert len(self._codebook) == len(set(self._codebook)) == expected
        assert all(not a.startswith(b) for a in self._codebook
                   for b in self._codebook if a != b)
        assert self._orders[0] in ORDERS and self._orders[1] in ORDERS
        assert self._orders[0] != self._orders[1]
        assert len(self.phase_a) == len(self._a_triples) == A_COUNT
        assert len(self.phase_b) == len(self._b_triples) == B_COUNT
        assert len(self.heldout_a) == len(self._all_triples) - A_COUNT
        assert len(self.heldout_b) == len(self._all_triples) - B_COUNT
        assert not set(self._a_triples) & set(self._b_triples)
        assert not ({x.acoustic_bits for x in self.phase_a} &
                    {x.acoustic_bits for x in self.heldout_a})
        assert not ({x.acoustic_bits for x in self.phase_b} &
                    {x.acoustic_bits for x in self.heldout_b})
        assert all(x.action_cost == 1 and x.reset_cost == 0 for x in
                   self.phase_a + self.phase_b)
        assert self.source_receipt()["charged_actions"] == 60
        assert self.source_receipt()["charged_resets"] == 0
        for triples, rows, order in (
            (self._a_triples, self.phase_a, self._orders[0]),
            (self._b_triples, self.phase_b, self._orders[1])):
            assert len(triples) == len(set(triples))
            for triple, row in zip(triples, rows):
                assert row.acoustic_bits == _utterance(
                    self.family, triple, self._codebook, order)
                assert row.after == _apply(self.family, row.before, triple)
        if self.family == "noncommuting_order":
            contrasts = self.order_counterworld_audit()
            assert contrasts["eligible_pairs"] > 0
            assert contrasts["distinguishable_pairs"] * 4 >= contrasts["eligible_pairs"]


def build_world(family: str, cohort: str, seed: int, encoding: str,
                *, primary_admitted: bool = False) -> SourceWorld:
    if family not in FAMILIES or cohort not in SEEDS:
        raise ValueError("invalid family/cohort")
    if type(seed) is not int or seed not in SEEDS[cohort]:
        raise ValueError("unregistered seed")
    if encoding not in ENCODINGS:
        raise ValueError("unregistered encoding")
    if cohort == "DEV":
        raise PermissionError("DEV locked until complete comparator qualification and admission")
    if cohort == "PRIMARY" and not primary_admitted:
        raise PermissionError("PRIMARY first-use requires separately admitted evidence")
    rng = _Keyed(family, cohort, seed, encoding)
    codebook = _codebook(rng, family, encoding)
    order_a = ORDERS[rng.below("order-a", 0, len(ORDERS))]
    delta = 1 + rng.below("order-b", 0, len(ORDERS) - 1)
    order_b = ORDERS[(ORDERS.index(order_a) + delta) % len(ORDERS)]
    triples = (tuple(product(range(8), range(4), range(3))) if
               family == "anchored_effect" else
               tuple((e, a, b) for e in range(8) for a in range(4)
                     for b in range(4) if a != b))
    chosen_a = None
    for attempt in range(1024):
        candidate = rng.shuffle(triples, "A-coverage", attempt)[:A_COUNT]
        if all(min(Counter(t[i] for t in candidate).values()) >= 2 for i
               in range(3)) and len(set(candidate)) == A_COUNT:
            chosen_a = candidate
            break
    if chosen_a is None:
        raise RuntimeError("cannot cover training meanings")
    remaining = tuple(t for t in triples if t not in set(chosen_a))
    chosen_b = rng.shuffle(remaining, "B-additional")[:B_COUNT]
    modulus = 4 if family == "anchored_effect" else 7
    initial = tuple(rng.below("state", i, modulus) for i in range(8))
    if family == "anchored_effect":
        initial += tuple(rng.below("orientation", i, 3) for i in range(8))
    cursor = initial
    def demonstrate(selected, order):
        nonlocal cursor
        observations = []
        for triple in selected:
            after = _apply(family, cursor, triple)
            observations.append(Observation(cursor, _utterance(
                family, triple, codebook, order), after))
            cursor = after
        return tuple(observations)
    def heldout(exclude, order):
        return tuple(Observation(initial, _utterance(family, t, codebook, order),
                                 _apply(family, initial, t))
                     for t in triples if t not in set(exclude))
    world = SourceWorld(
        family, cohort, seed, encoding,
        demonstrate(chosen_a, order_a), demonstrate(chosen_b, order_b),
        heldout(chosen_a, order_a), heldout(chosen_b, order_b),
        codebook, (order_a, order_b), initial, chosen_a, chosen_b, triples)
    world.audit()
    return world
