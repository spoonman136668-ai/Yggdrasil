"""WSP127 inspectable development-only rank-eight consequence source.

No original scientific first-use. This module must NEVER be imported by the
learners. Its hidden factor generator and evaluator are source-side only.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
import json
import random

FIT = frozenset(range(135000, 135128))
TRANSFER = frozenset(range(136000, 136256))
NEGATIVE = frozenset(range(137000, 137064))
ALLOWED = FIT | TRANSFER | NEGATIVE
DENIED = (frozenset(range(131000, 131064)) |
          frozenset(range(131800, 131864)) |
          frozenset(range(135800, 135864)) |
          frozenset(range(138800, 138864)) |
          frozenset(range(120800, 120864)) |
          frozenset(range(121800, 121864)) |
          frozenset(range(122800, 122864)) |
          frozenset(range(123800, 123864)) |
          frozenset(range(125800, 125864)) |
          frozenset(range(127800, 127864)))

def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))

def digest(obj):
    return sha256(canon(obj).encode("utf8")).hexdigest()

def rank(vectors):
    pivots = {}
    for value in vectors:
        x = value
        while x:
            bit = x.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = x
                break
            x ^= pivots[bit]
    return len(pivots)

def _seed(tag, law):
    return int.from_bytes(sha256((tag + str(law)).encode("ascii")).digest(), "big")

@lru_cache(maxsize=128)
def _rows(law):
    if type(law) is not int or not 0 <= law < 128:
        raise PermissionError("WSP127_UNKNOWN_SOURCE_LAW")
    rng = random.Random(_seed("WSP127|SRC8|", law))
    for _ in range(1000):
        left = [rng.getrandbits(64) for _ in range(8)]
        right = [rng.getrandbits(64) for _ in range(8)]
        if not all(left) or not all(right):
            continue
        rows = []
        for a in range(64):
            mask = 0
            for j in range(8):
                if left[j] & (1 << a):
                    mask ^= right[j]
            rows.append(mask)
        if rank(rows) == 8:
            return tuple(rows)
    raise AssertionError("WSP127_SOURCE_RANK8_GENERATION_FAILED")

@lru_cache(maxsize=64)
def _negative_rows(law):
    original = _rows(law)
    rng = random.Random(_seed("WSP127|NEG9|", law))
    for _ in range(1000):
        left, right = rng.getrandbits(64), rng.getrandbits(64)
        if not left or not right:
            continue
        modified = tuple(row ^ (right if (left >> a) & 1 else 0)
                         for a, row in enumerate(original))
        if rank(modified) == 9:
            return modified
    raise AssertionError("WSP127_SOURCE_RANK9_GENERATION_FAILED")

@dataclass(frozen=True)
class View:
    seed: int
    law_id: int
    cohort: str
    records: tuple
    legal: tuple
    by_subject: dict
    by_pair: dict

    def pair(self, subject):
        if type(subject) is not int or subject not in self.by_subject:
            raise ValueError("WSP127_UNREGISTERED_ACTION")
        return self.by_subject[subject]

    def subject(self, a, b):
        if (type(a) is not int or type(b) is not int or
                not 0 <= a < 64 or not 0 <= b < 64):
            raise ValueError("WSP127_INVALID_PAIR")
        return self.by_pair[a, b]

    def fingerprint(self):
        return digest([self.seed, self.law_id, self.cohort, self.records])

@lru_cache(maxsize=6)
def world(seed):
    if type(seed) is not int or seed not in ALLOWED or seed in DENIED:
        raise PermissionError("WSP127_FIRST_USE_OR_UNREGISTERED_SOURCE_DENIED")
    if seed in FIT:
        law, cohort = seed - 135000, "fit"
    elif seed in TRANSFER:
        law, cohort = (seed - 136000) // 2, "transfer"
    else:
        law, cohort = seed - 137000, "negative"
    rng = random.Random(seed)
    ids = rng.sample(range(seed * 10000, seed * 10000 + 10000), 4096)
    records = [(ids[a * 64 + b], a, b)
               for a in range(64) for b in range(64)]
    rng.shuffle(records)
    return View(seed, law, cohort, tuple(records),
                frozenset(s for s, _, _ in records) if cohort == "fit" else frozenset(),
                {s: (a, b) for s, a, b in records},
                {(a, b): s for s, a, b in records})

def open_original(seed):
    raise PermissionError("WSP127_ORIGINAL_FIRST_USE_NOT_AUTHORIZED")

@dataclass(frozen=True)
class Evidence:
    seed: int
    law_id: int
    subject: int
    left: int
    right: int
    effect: int
    receipt: str

class Custodian:
    def __init__(self, view):
        if type(view) is not View or view.seed not in ALLOWED or view != world(view.seed):
            raise PermissionError("WSP127_INVALID_VIEW_CUSTODY")
        self.view = view
        self.budget = 1024 if view.cohort == "fit" else 0
        self.seen = set()
        self.events = []
        self.receipt = digest([view.fingerprint(), "begin"])
        self.scored = False

    def query(self, subject):
        if (self.scored or type(subject) is not int or
                subject not in self.view.legal or
                subject in self.seen or len(self.events) >= self.budget):
            raise PermissionError("WSP127_DUPLICATE_UNREGISTERED_OR_OVERBUDGET_ACTION")
        a, b = self.view.pair(subject)
        value = (_rows(self.view.law_id)[a] >> b) & 1
        self.seen.add(subject)
        event = [self.view.seed, self.view.law_id, subject, a, b, value]
        self.events.append(event)
        self.receipt = digest([self.receipt, event])
        return Evidence(*event, self.receipt)

    def held(self):
        return ((s, a, b) for s, a, b in self.view.records if s not in self.seen)

    def score_once(self, predictions):
        if self.scored or len(self.events) != self.budget:
            raise PermissionError("WSP127_SCORE_REPLAY_OR_BUDGET_INVALID")
        if type(predictions) is not dict:
            raise ValueError("WSP127_SCORE_NOT_MAPPING")
        true_rows = (_negative_rows(self.view.law_id)
                     if self.view.cohort == "negative" else _rows(self.view.law_id))
        held = 0
        correct = wrong = abstain = 0
        for subject, a, b in self.held():
            if subject not in predictions:
                raise ValueError("WSP127_MISSING_HELD_PREDICTION")
            guess = predictions[subject]
            if guess is None:
                abstain += 1
            elif type(guess) is int and guess in (0, 1):
                if guess == ((true_rows[a] >> b) & 1):
                    correct += 1
                else:
                    wrong += 1
            else:
                raise ValueError("WSP127_INVALID_PREDICTION")
            held += 1
        if len(predictions) != held:
            raise ValueError("WSP127_EXTRA_HELD_PREDICTIONS")
        self.scored = True
        return {"held": held, "correct": correct, "wrong_confident": wrong,
                "abstained": abstain, "source_calls": len(self.events)}
