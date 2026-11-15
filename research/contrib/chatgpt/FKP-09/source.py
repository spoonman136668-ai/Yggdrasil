"""FKP-09 source owner: actual public 64-bit interventions, no hidden-law fitting.

Original DEV cohorts 900..923, 940..947, 980..987 must NOT be run
before independently pinned source/algorithm/tests and qualification.
Fixtures 700..703 are safe for preflight. Protected cohorts require
an independent owner key; no protected labels are distributed here.
"""
from __future__ import annotations

import hashlib
import hmac
import random
from dataclasses import dataclass

N_BITS = 64
PAID = 128
HELD = 512
FIXTURES = tuple(range(700, 704))
ORIGINALS = tuple(range(900, 924))
REVISIONS = tuple(range(940, 948))
NEGATIVES = tuple(range(980, 988))
PROTECTED = tuple(range(1900, 1980))
DEV_KEY = hashlib.sha256(b"FKP-09-PUBLIC-DEVELOPMENT-ONLY-NEVER-PROTECTED").digest()


def cohort(seed: int) -> str:
    if type(seed) is not int:
        raise ValueError("FKP09_SEED_TYPE")
    if seed in FIXTURES:
        return "fixture"
    if seed in ORIGINALS:
        return "original"
    if seed in REVISIONS:
        return "revision"
    if seed in NEGATIVES:
        return "negative"
    if seed in PROTECTED:
        return "protected"
    raise ValueError("FKP09_UNKNOWN_SOURCE")


def context_slot(seed: int) -> int:
    kind = cohort(seed)
    if kind == "original":
        return seed - 900
    if kind == "revision":
        return seed - 940
    raise ValueError("FKP09_CONTEXT_MAPPING_NOT_APPLICABLE")


@dataclass(frozen=True)
class PublicView:
    seed: int
    choices: tuple[int, ...]
    held: tuple[int, ...]


class Source:
    """Source-owned HMAC causal laws; public consumer sees view/observe only."""

    __slots__ = ("_owner_key", "_paid")

    def __init__(self, *, protected_key: bytes | None = None):
        if protected_key is not None and (
            type(protected_key) is not bytes or len(protected_key) < 32
        ):
            raise PermissionError("FKP09_BAD_PROTECTED_KEY")
        self._owner_key = protected_key
        self._paid: dict[int, set[int]] = {}

    def _digest(self, seed: int, purpose: str) -> bytes:
        kind = cohort(seed)
        if kind == "protected" and self._owner_key is None:
            raise PermissionError("FKP09_PROTECTED_OWNER_REQUIRED")
        key = self._owner_key if kind == "protected" else DEV_KEY
        return hmac.new(
            key, f"FKP09:{seed}:{purpose}".encode("utf-8"), hashlib.sha256
        ).digest()

    def _law(self, seed: int) -> tuple[int, int, bool, int]:
        mask = int.from_bytes(
            self._digest(seed, "causal-mask") +
            self._digest(seed, "causal-mask-second"),
            "big",
        ) & ((1 << N_BITS) - 1)
        # Avoid degenerate masks; every world has a substantial dependency set.
        mask |= (1 << (seed % N_BITS))
        bias = self._digest(seed, "causal-bias")[0] & 1
        nonlinear = seed in NEGATIVES or seed == 702
        threshold = max(1, mask.bit_count() // 2)
        return mask, bias, nonlinear, threshold

    def _effect(self, seed: int, action: int) -> int:
        mask, bias, nonlinear, threshold = self._law(seed)
        active = (mask & action).bit_count()
        return (int(active >= threshold) if nonlinear else (active & 1)) ^ bias

    def view(self, seed: int) -> PublicView:
        self._digest(seed, "preflight")  # fence owner-private source
        rnd = random.Random(
            int.from_bytes(self._digest(seed, "public-split"), "big")
        )
        unique: set[int] = set()
        actions = []
        while len(actions) < PAID + HELD:
            candidate = rnd.getrandbits(N_BITS)
            if candidate not in unique:
                unique.add(candidate)
                actions.append(candidate)
        return PublicView(seed, tuple(actions[:PAID]), tuple(actions[PAID:]))

    def observe(self, seed: int, action: int) -> int:
        view = self.view(seed)
        if type(action) is not int or action not in view.choices:
            raise ValueError("FKP09_ACTION_NOT_PUBLIC")
        seen = self._paid.setdefault(seed, set())
        if action in seen:
            raise PermissionError("FKP09_DUPLICATE_PAID_ACTION")
        if len(seen) >= PAID:
            raise PermissionError("FKP09_SOURCE_BUDGET")
        seen.add(action)
        return self._effect(seed, action)

    def held_dev(self, seed: int, actions: tuple[int, ...]) -> tuple[int, ...]:
        kind = cohort(seed)
        if kind not in ("original", "revision", "negative"):
            raise PermissionError("FKP09_HELD_DEV_ONLY")
        view = self.view(seed)
        if type(actions) is not tuple or actions != view.held:
            raise ValueError("FKP09_HELD_SPLIT_DRIFT")
        return tuple(self._effect(seed, a) for a in actions)

    def charged(self, seed: int) -> int:
        return len(self._paid.get(seed, ()))
