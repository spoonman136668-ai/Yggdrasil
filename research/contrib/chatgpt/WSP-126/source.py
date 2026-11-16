"""WSP126 independent inspectable development-only hidden causal source.

No primary first use exists. The numerical and symbolic learners do not import
this file; only the evaluator exercises it. All opaque identities disjoint.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
import json
import random

FIT = frozenset(range(132000,132128))
TRANSFER = frozenset(range(133000,133256))
NEGATIVE = frozenset(range(134000,134064))
ALLOWED = FIT | TRANSFER | NEGATIVE
ORIGINAL = frozenset(range(131000,131064))
PROTECTED = (frozenset(range(131800,131864)) |
             frozenset(range(125800,125864)) |
             frozenset(range(127800,127864)) |
             frozenset(range(123800,123864)) |
             frozenset(range(122800,122864)) |
             frozenset(range(121800,121864)) |
             frozenset(range(120800,120864)))


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",",":"))


def digest(data):
    return sha256(canonical(data).encode("utf-8")).hexdigest()


def _rank(vectors):
    pivots = {}
    for vec in vectors:
        work = vec
        while work:
            bit = work.bit_length()-1
            if bit not in pivots:
                pivots[bit] = work
                break
            work ^= pivots[bit]
    return len(pivots)


@dataclass(frozen=True)
class PublicWorld:
    seed: int
    law_id: int
    cohort: str
    records: tuple[tuple[int,int,int], ...]
    legal: tuple[int, ...]

    def pair(self, subject):
        if type(subject) is not int:
            raise ValueError("WSP126_ACTION_TYPE")
        for identifier,a,b in self.records:
            if identifier == subject:
                return (a,b)
        raise ValueError("WSP126_UNKNOWN_ACTION")

    def subject(self,a,b):
        if (type(a) is not int or type(b) is not int or
                not 0<=a<16 or not 0<=b<16):
            raise ValueError("WSP126_PUBLIC_PAIR")
        for identifier,x,y in self.records:
            if (x,y)==(a,b):
                return identifier
        raise ValueError("WSP126_PUBLIC_PAIR_NOT_FOUND")

    def fingerprint(self):
        return digest([self.seed,self.law_id,self.cohort,self.records,self.legal])


@dataclass(frozen=True)
class ObservedConsequence:
    seed: int
    law_id: int
    subject: int
    left: int
    right: int
    effect: int
    source_sha256: str


def world(seed):
    if type(seed) is not int or seed not in ALLOWED:
        raise PermissionError("WSP126_ORIGINAL_OR_UNREGISTERED_SOURCE_DENIED")
    if seed in FIT:
        law_id,cohort=seed-132000,"fit"
    elif seed in TRANSFER:
        law_id,cohort=(seed-133000)//2,"transfer"
    else:
        law_id,cohort=seed-134000,"negative"
    rng=random.Random(seed)
    # 10000 slots with >=9000 spacing; all seeds are distinct.
    ids=rng.sample(range(seed*10000,seed*10000+9000),256)
    records=[(ids[a*16+b],a,b) for a in range(16) for b in range(16)]
    rng.shuffle(records)
    legal=tuple(s for s,_,_ in records) if cohort=="fit" else ()
    return PublicWorld(seed,law_id,cohort,tuple(records),legal)


def open_original(seed):
    raise PermissionError("WSP126_FIRST_USE_NOT_AUTHORIZED")


@lru_cache(maxsize=128)
def _hidden_rows(law_id):
    if type(law_id) is not int or not 0<=law_id<128:
        raise PermissionError("WSP126_SOURCE_LAW_NOT_REGISTERED")
    rng=random.Random(int.from_bytes(sha256(
        ("WSP126|SOURCE-RANK4|"+str(law_id)).encode("ascii")
    ).digest(),"big"))
    # Reject samples until EXACT GF2 rank 4. The source-generated
    # factors/labels are never returned to a learner.
    for _ in range(1000):
        left=[rng.getrandbits(16) for _ in range(4)]
        right=[rng.getrandbits(16) for _ in range(4)]
        if not all(left) or not all(right):
            continue
        rows=[0]*16
        for a in range(16):
            for factor in range(4):
                if left[factor] & (1<<a):
                    rows[a]^=right[factor]
        if _rank(rows)==4:
            return tuple(rows)
    raise AssertionError("WSP126_SOURCE_FAILED_RANK4_GENERATION")


@lru_cache(maxsize=64)
def _negative_extra(law_id):
    baseline=list(_hidden_rows(law_id))
    rng=random.Random(int.from_bytes(sha256(
        ("WSP126|SOURCE-RANK5-NEGATIVE|"+str(law_id)).encode("ascii")
    ).digest(),"big"))
    for _ in range(1000):
        left=rng.getrandbits(16)
        right=rng.getrandbits(16)
        if not left or not right:
            continue
        altered=[value^(right if left & (1<<a) else 0)
                 for a,value in enumerate(baseline)]
        if _rank(altered)==5:
            return tuple(altered)
    raise AssertionError("WSP126_SOURCE_FAILED_RANK5_NEGATIVE")


def _effect(law_id,a,b,negative=False):
    rows=(_negative_extra(law_id) if negative else _hidden_rows(law_id))
    return (rows[a]>>b)&1


class Custodian:
    def __init__(self,view):
        if type(view) is not PublicWorld or view.seed not in ALLOWED or view!=world(view.seed):
            raise PermissionError("WSP126_CUSTODY_PUBLIC_VIEW_DRIFT")
        self.view=view
        self.budget=160 if view.cohort=="fit" else 0
        self._seen=set()
        self._events=[]
        self._scored=False

    @property
    def calls(self):
        return len(self._events)

    @property
    def held(self):
        return tuple(subject for subject,_,_ in self.view.records
                     if subject not in self._seen)

    @property
    def receipt(self):
        return digest([self.view.fingerprint(),self._events])

    def query(self,subject):
        if (self._scored or type(subject) is not int or
                subject not in self.view.legal or
                subject in self._seen or self.calls>=self.budget):
            raise PermissionError("WSP126_QUERY_HELD_DUPLICATE_OR_OVER_BUDGET")
        a,b=self.view.pair(subject)
        outcome=_effect(self.view.law_id,a,b)
        self._seen.add(subject)
        self._events.append([subject,a,b,outcome])
        return ObservedConsequence(
            self.view.seed,self.view.law_id,subject,a,b,outcome,self.receipt)

    def score_once(self,predictions):
        if self._scored or self.calls!=self.budget:
            raise PermissionError("WSP126_SCORE_SOURCE_BUDGET_OR_REPLAY")
        if type(predictions) is not dict or set(predictions)!=set(self.held):
            raise ValueError("WSP126_HELD_PREDICTION_SET")
        if any(p is not None and (type(p) is not int or p not in (0,1))
               for p in predictions.values()):
            raise ValueError("WSP126_HELD_PREDICTION_VALUE")
        correct=wrong=abstain=0
        for subject in self.held:
            p=predictions[subject]
            if p is None:
                abstain+=1
            elif p==_effect(self.view.law_id,*self.view.pair(subject),
                            negative=self.view.cohort=="negative"):
                correct+=1
            else:
                wrong+=1
        self._scored=True
        return {
            "seed":self.view.seed,"law_id":self.view.law_id,
            "public_sha256":self.view.fingerprint(),
            "source_sha256":self.receipt,
            "prediction_sha256":digest(sorted(predictions.items())),
            "held":len(self.held),"correct":correct,
            "wrong_confident":wrong,"abstained":abstain,
            "source_calls":self.calls,
            "scientific_pass":False,"source_first_use":False,
            "native_admission":False,
        }
