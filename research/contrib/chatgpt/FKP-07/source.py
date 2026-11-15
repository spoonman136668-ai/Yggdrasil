"""FKP-07 public synthetic source owner. Hidden relationships never supplied to learners."""
from __future__ import annotations
from hashlib import sha256
from itertools import combinations
import random

N_BITS = 32
HIST_SEEDS = range(30000, 30512)
DEV_SEEDS = range(800, 824)
REV_SEEDS = range(840, 848)
NEG_SEEDS = range(900, 908)
HISTORY_PAID = 64
NEW_PAID = 12
# Generator-private DEV fixture; not an inferred relationship or a learner argument.
_PRIVATE_FAVORED = ((1, 6), (3, 10), (8, 17), (20, 29))
_PAIRS = tuple(combinations(range(N_BITS), 2))


def seeded(seed: int, domain: str) -> random.Random:
    data = sha256(f"FKP07_PUBLIC_DEV_ONLY|{domain}|{seed}".encode("ascii")).digest()
    return random.Random(int.from_bytes(data[:8], "big"))


def history_actions(seed: int) -> tuple[int, ...]:
    if seed not in HIST_SEEDS:
        raise ValueError("NOT_PUBLIC_HISTORY_SEED")
    rng = random.Random(707 ^ seed)
    selected = set()
    while len(selected) < HISTORY_PAID:
        selected.add(rng.getrandbits(N_BITS))
    return tuple(sorted(selected))


def _and2(pair: tuple[int,int], x: int) -> int:
    return ((x >> pair[0]) & 1) & ((x >> pair[1]) & 1)


def _xor_and(law: tuple[int,int,int,int], x: int) -> int:
    return _and2((law[0], law[1]), x) ^ _and2((law[2], law[3]), x)


class World:
    """The only source-facing learner interface is observe(public_action)."""
    def __init__(self, seed: int, mode: str, public_actions: tuple[int,...],
                 all_four_laws: tuple | list | None = None):
        if mode == "history" and seed in HIST_SEEDS:
            rng = seeded(seed, "history-law")
            self._law = (rng.choice(_PRIVATE_FAVORED) if rng.random() < .85
                         else rng.choice(_PAIRS))
        elif mode in ("new", "revision") and seed in (DEV_SEEDS if mode == "new" else REV_SEEDS):
            rng = seeded(seed, "four-parent-law")
            if rng.random() < .85:
                p, q = rng.sample(_PRIVATE_FAVORED, 2)
                self._law = p + q
            else:
                if all_four_laws is None or len(all_four_laws) != 107880:
                    raise ValueError("FOUR_PARENT_FAMILY_REQUIRED")
                self._law = rng.choice(all_four_laws)
        elif mode == "negative" and seed in NEG_SEEDS:
            self._law = tuple(seeded(seed, "five-parent-parity").sample(range(N_BITS), 5))
        else:
            raise ValueError("PROTECTED_OR_INVALID_SOURCE_WORLD")
        self._mode = mode
        self._allowed = frozenset(public_actions)
        if len(public_actions) != len(self._allowed):
            raise ValueError("DUPLICATE_PUBLIC_POOL")
        self._budget = HISTORY_PAID if mode == "history" else NEW_PAID
        self._charges: list[int] = []

    def observe(self, action: int) -> int:
        if type(action) is not int or not 0 <= action < (1 << N_BITS):
            raise ValueError("INVALID_ACTION")
        if action not in self._allowed:
            raise ValueError("NONPUBLIC_ACTION")
        if action in self._charges:
            raise ValueError("REPEATED_ACTION")
        if len(self._charges) >= self._budget:
            raise ValueError("ACTION_BUDGET_EXCEEDED")
        self._charges.append(action)
        return self._eval(action)

    def _eval(self, action: int) -> int:
        if self._mode == "history":
            return _and2(self._law, action)
        if self._mode == "negative":
            result = 0
            for i in self._law:
                result ^= (action >> i) & 1
            return result
        return _xor_and(self._law, action)

    def held_truth_after_seal(self, held: tuple[int,...]) -> tuple[int,...]:
        if len(self._charges) != self._budget:
            raise ValueError("UNSEALED_WORLD")
        if self._allowed.intersection(held):
            raise ValueError("HELD_ACTION_LEAK")
        return tuple(self._eval(x) for x in held)

    @property
    def charged(self) -> int:
        return len(self._charges)
