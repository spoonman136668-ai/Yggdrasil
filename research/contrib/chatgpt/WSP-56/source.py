"""WSP56 evaluator-only, deterministic non-affine physical worlds.

The learner must never import or receive this module, its codebooks, operation
tables, hidden grammar orders, source triples, or heldout outcomes.
SELFTEST fixtures only. No protected DEV/PRIMARY first use.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from itertools import permutations, product
from random import Random
import json

SEEDS = (2201, 2202)
ENCODINGS = ("identity", "permuted", "rotated")
REGISTERS = 8
MODULUS = 7
NUM_OPERATORS = 4
A_UNARY = 28
A_PAIRS = 20
B_PAIRS = 12
HELDOUT_EACH = 96


@dataclass(frozen=True)
class Observation:
    before: tuple[int, ...]
    acoustic_bits: str
    after: tuple[int, ...]
    action_cost: int = 1
    reset_cost: int = 0


def _rng(seed, encoding, label):
    digest = sha256(f"WSP56|SELFTEST|{seed}|{encoding}|{label}".encode("ascii")).digest()
    return Random(int.from_bytes(digest, "big"))


def _nonaffine(p):
    return all(any(p[x] != ((a * x + b) % MODULUS)
                   for x in range(MODULUS))
               for a in range(MODULUS) for b in range(MODULUS))


def _operators(seed, encoding):
    rng = _rng(seed, encoding, "operator-maps")
    out = []
    for _ in range(10000):
        candidate = list(range(MODULUS))
        rng.shuffle(candidate)
        t = tuple(candidate)
        if not _nonaffine(t) or any(t[x] == x for x in range(MODULUS)):
            continue
        if t in out:
            continue
        if any(sum(t[other[x]] != other[t[x]] for x in range(MODULUS)) < 3
               for other in out):
            continue
        out.append(t)
        if len(out) == NUM_OPERATORS:
            return tuple(out)
    raise RuntimeError("cannot construct four discriminable nonlinear maps")


def _codebook(seed, encoding):
    rng = _rng(seed, encoding, "codebook")
    codes = [format(i, "04b") for i in range(16)]
    rng.shuffle(codes)
    if encoding == "rotated":
        codes = [word[1:] + word[:1] for word in codes]
    elif encoding == "permuted":
        codes = [word[::-1] for word in codes]
    return tuple(codes[:12])


def _hash(rows):
    b = "\n".join(f"{r.before}|{r.acoustic_bits}|{r.after}|"
                  f"{r.action_cost}|{r.reset_cost}" for r in rows).encode("ascii")
    return sha256(b).hexdigest()


def _apply(operators, before, e, first, second=None):
    after = list(before)
    x = operators[first][before[e]]
    if second is not None:
        x = operators[second][x]
    after[e] = x
    return tuple(after)


@dataclass(frozen=True)
class World:
    seed: int
    encoding: str
    unary: tuple[Observation, ...]
    paired_a: tuple[Observation, ...]
    paired_b: tuple[Observation, ...]
    heldout_a: tuple[Observation, ...]
    heldout_b: tuple[Observation, ...]
    _operators: tuple[tuple[int, ...], ...]
    _codebook: tuple[str, ...]
    _unary_order: tuple[int, int]
    _a_order: tuple[int, int, int]
    _b_order: tuple[int, int, int]
    _pair_train_a: tuple[tuple[int, ...], ...]
    _pair_train_b: tuple[tuple[int, ...], ...]
    _heldout_a_tuples: tuple[tuple[int, ...], ...]
    _heldout_b_tuples: tuple[tuple[int, ...], ...]

    def receipt(self):
        return {
            "schema": "wsp56.selftest-source.v1", "seed": self.seed,
            "encoding": self.encoding, "unary": [len(self.unary), _hash(self.unary)],
            "paired_a": [len(self.paired_a), _hash(self.paired_a)],
            "paired_b": [len(self.paired_b), _hash(self.paired_b)],
            "heldout_a": [len(self.heldout_a), _hash(self.heldout_a)],
            "heldout_b": [len(self.heldout_b), _hash(self.heldout_b)],
            "charged_actions": len(self.unary) + len(self.paired_a) + len(self.paired_b)
        }

    def audit(self):
        assert len(self.unary) == A_UNARY
        assert len(self.paired_a) == A_PAIRS
        assert len(self.paired_b) == B_PAIRS
        assert len(self.heldout_a) == len(self.heldout_b) == HELDOUT_EACH
        assert all(_nonaffine(p) and all(p[x] != x for x in range(7))
                   for p in self._operators)
        assert len(set(self._codebook)) == 12
        assert self._a_order != self._b_order
        assert self.receipt()["charged_actions"] == 60
        assert not (set(self._pair_train_a) & set(self._pair_train_b))
        assert not (set(self._heldout_a_tuples) & set(self._pair_train_a))
        assert not (set(self._heldout_b_tuples) &
                    (set(self._pair_train_b) | set(self._pair_train_a)))
        for op in range(4):
            assert all(any(row.before[(op * 7 + x) % 8] == x
                           for row in self.unary[op*7:(op+1)*7])
                       for x in range(7))
        for rows in (self.unary, self.paired_a, self.paired_b,
                     self.heldout_a, self.heldout_b):
            assert all(r.action_cost == 1 and r.reset_cost == 0 for r in rows)


def build_world(seed, encoding, cohort="SELFTEST"):
    if cohort != "SELFTEST" or seed not in SEEDS or encoding not in ENCODINGS:
        raise PermissionError("WSP56 DEV and PRIMARY sealed")
    operators = _operators(seed, encoding)
    codes = _codebook(seed, encoding)
    entities, operation_codes = codes[:8], codes[8:]
    rng = _rng(seed, encoding, "actions-and-grammar")
    unary_order = rng.choice(tuple(permutations((0, 1))))
    pair_orders = tuple(permutations((0, 1, 2)))
    a_order = rng.choice(pair_orders)
    b_order = rng.choice(tuple(order for order in pair_orders if order != a_order))

    def before(e, x):
        state = [rng.randrange(7) for _ in range(8)]
        state[e] = x
        return tuple(state)

    def make_unary(op, x):
        e = (op * 7 + x) % 8
        state = before(e, x)
        pieces = (entities[e], operation_codes[op])
        raw = "".join(pieces[i] for i in unary_order)
        return Observation(state, raw, _apply(operators, state, e, op))

    def make_pair(spec, order):
        e, op1, op2, x = spec
        state = before(e, x)
        pieces = (entities[e], operation_codes[op1], operation_codes[op2])
        return Observation(state, "".join(pieces[i] for i in order),
                           _apply(operators, state, e, op1, op2))

    unary = tuple(make_unary(op, x) for op in range(4) for x in range(7))
    specs = [(e, a, b, x) for e in range(8) for a in range(4)
             for b in range(4) if a != b for x in range(7)]
    rng.shuffle(specs)
    train_a = tuple(specs[:A_PAIRS])
    train_b = tuple(specs[A_PAIRS:A_PAIRS+B_PAIRS])
    excluded = set(train_a) | set(train_b)

    def choose_heldout(order, cohort_tag, extra_excluded=()):
        other = excluded | set(extra_excluded)
        # Deliberately include swap-order discriminating contrast pairs.
        pool = []
        for e, a, b, x in specs:
            if a >= b:
                continue
            f = (e, a, b, x)
            swap = (e, b, a, x)
            if f in other or swap in other:
                continue
            first_out = operators[b][operators[a][x]]
            second_out = operators[a][operators[b][x]]
            if first_out != second_out:
                pool.append((f, swap))
        rng2 = _rng(seed, encoding, "heldout-" + cohort_tag)
        rng2.shuffle(pool)
        pairs = pool[:24]
        selected = [item for pair in pairs for item in pair]
        remaining = [t for t in specs if t not in other and t not in set(selected)]
        rng2.shuffle(remaining)
        selected.extend(remaining[:HELDOUT_EACH - len(selected)])
        assert len(selected) == HELDOUT_EACH
        return tuple(selected), tuple(make_pair(t, order) for t in selected)

    held_a_spec, held_a = choose_heldout(a_order, "A")
    held_b_spec, held_b = choose_heldout(b_order, "B", held_a_spec)
    world = World(seed, encoding, unary,
                  tuple(make_pair(t, a_order) for t in train_a),
                  tuple(make_pair(t, b_order) for t in train_b),
                  held_a, held_b, operators, codes, unary_order,
                  a_order, b_order, train_a, train_b,
                  held_a_spec, held_b_spec)
    world.audit()
    return world
