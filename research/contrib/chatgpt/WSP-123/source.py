"""WSP123 source-only development causal factor worlds; no original first use.

Hidden effects live here, never imported by numeric or symbolic learners.
The source is inspectable development code, NOT sealed science custody.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
import random

FIT = frozenset(range(123900, 123904))
TRANSFER = frozenset(range(124000, 124256))
OFFFAMILY = frozenset(range(124400, 124464))
ALLOWED = FIT | TRANSFER | OFFFAMILY
ORIGINAL = frozenset(range(123000, 123064))
PROTECTED = (frozenset(range(123800, 123864)) |
             frozenset(range(122800, 122864)) |
             frozenset(range(121800, 121864)) |
             frozenset(range(120800, 120864)))
WIDTH = 8


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value):
    return sha256(canonical(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class PublicWorld:
    # The seed and its cohort remain engineering-public, never a sealed source.
    seed: int
    domain: int
    records: tuple[tuple[int, int, int], ...]
    legal: tuple[int, ...]
    held: tuple[int, ...]

    def pair(self, subject: int) -> tuple[int, int]:
        if type(subject) is not int:
            raise ValueError("WSP123_UNKNOWN_SUBJECT")
        for identifier, a, b in self.records:
            if identifier == subject:
                return (a, b)
        raise ValueError("WSP123_UNKNOWN_SUBJECT")

    def fingerprint(self):
        return digest([self.domain, self.records, self.legal, self.held])


@dataclass(frozen=True)
class VerifiedEffect:
    seed: int
    domain: int
    subject: int
    left: int
    right: int
    effect: int
    source_sha256: str


def world(seed: int) -> PublicWorld:
    # Original and protected cohorts are denied BEFORE any graph construction.
    if type(seed) is not int or seed not in ALLOWED:
        raise PermissionError("WSP123_ORIGINAL_OR_PROTECTED_SOURCE_DENIED")
    if seed in FIT:
        domain, is_fit = seed - 123900, True
    elif seed in TRANSFER:
        domain, is_fit = (seed - 124000) // 64, False
    else:
        domain, is_fit = (seed - 124400) // 16, False
    rng = random.Random(seed)
    identifiers = rng.sample(range(seed * 1000, seed * 1000 + 999), 64)
    records = list(zip(identifiers, (a for a in range(WIDTH) for _ in range(WIDTH)),
                       (b for _ in range(WIDTH) for b in range(WIDTH))))
    rng.shuffle(records)
    legal = tuple(x for x, a, b in records if is_fit and
                  not (a >= 4 and b >= 4))
    held = tuple(x for x, a, b in records
                 if not is_fit or (a >= 4 and b >= 4))
    if (len(records),len(legal),len(held)) != (
            (64,48,16) if is_fit else (64,0,64)):
        raise AssertionError("WSP123_SPLIT_INVALID")
    return PublicWorld(seed, domain, tuple(records), legal, held)


def open_original(seed):
    raise PermissionError("WSP123_ORIGINAL_FIRST_USE_NOT_INSTALLED")


def _hidden_effect(seed: int, domain: int, left: int, right: int):
    # Evaluator-only composition; no learner imports this function.
    a = sha256(f"WSP123|CAUSAL|V1|{domain}|LEFT|{left}".encode()).digest()[0] & 7
    b = sha256(f"WSP123|CAUSAL|V1|{domain}|RIGHT|{right}".encode()).digest()[0] & 7
    value = a ^ b
    if seed in OFFFAMILY and left >= 4 and right >= 4:
        value ^= 1  # independently disclosed off-class negative, never fitted
    return value


class Custodian:
    def __init__(self, public: PublicWorld):
        if type(public) is not PublicWorld or public.seed not in ALLOWED:
            raise PermissionError("WSP123_CUSTODY_SOURCE_ONLY")
        if public != world(public.seed):
            raise ValueError("WSP123_PUBLIC_VIEW_DRIFT")
        self.public = public
        self.budget = 15 if public.seed in FIT else 0
        self._seen = set()
        self._events = []
        self._scored = False

    @property
    def calls(self):
        return len(self._events)

    @property
    def receipt(self):
        return digest([self.public.fingerprint(), self._events])

    def query(self, subject: int):
        if (self._scored or type(subject) is not int
                or subject not in self.public.legal or subject in self._seen
                or self.calls >= self.budget):
            raise PermissionError("WSP123_QUERY_HELD_DUPLICATE_OR_BUDGET")
        a, b = self.public.pair(subject)
        observed = _hidden_effect(self.public.seed, self.public.domain, a, b)
        self._events.append([subject, a, b, observed])
        self._seen.add(subject)
        return VerifiedEffect(self.public.seed, self.public.domain,
                              subject, a, b, observed, self.receipt)

    def score_once(self, predictions):
        if self._scored or self.calls != self.budget:
            raise PermissionError("WSP123_HELD_SCORE_NOT_READY_OR_REPLAY")
        if type(predictions) is not dict or set(predictions) != set(self.public.held):
            raise ValueError("WSP123_HELD_PREDICTION_SET_INVALID")
        if any(x is not None and (type(x) is not int or not 0 <= x < 8)
               for x in predictions.values()):
            raise ValueError("WSP123_HELD_PREDICTION_VALUE_INVALID")
        correct = wrong = abstain = 0
        for subject in self.public.held:
            p = predictions[subject]
            if p is None:
                abstain += 1
            elif p == _hidden_effect(self.public.seed, self.public.domain,
                                     *self.public.pair(subject)):
                correct += 1
            else:
                wrong += 1
        self._scored = True
        return {"seed": self.public.seed, "domain": self.public.domain,
                "public_sha256": self.public.fingerprint(),
                "source_sha256": self.receipt,
                "source_calls": self.calls,
                "held": len(self.public.held), "correct": correct,
                "wrong_confident": wrong, "abstained": abstain,
                "scientific_pass": False, "source_first_use": False,
                "native_admission": False}
