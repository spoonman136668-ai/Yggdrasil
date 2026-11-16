"""WSP125 inspectable engineering-only causal source (not sealed science).

The private support masks/delta live ONLY in this source module. Source uses
fresh opaque action identities across all fit, transfer and negative worlds.
No original/reserved source can be instantiated, even with an invalid bool ID.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
import json
import random

FIT=frozenset(range(125900,126028))
TRANSFER=frozenset(range(126200,126456))
NEGATIVE=frozenset(range(126500,126564))
ALLOWED=FIT|TRANSFER|NEGATIVE
ORIGINAL=frozenset(range(125000,125064))
PROTECTED=(frozenset(range(125800,125864))|
           frozenset(range(127800,127864))|
           frozenset(range(123800,123864))|
           frozenset(range(122800,122864))|
           frozenset(range(121800,121864))|
           frozenset(range(120800,120864)))


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"))


def digest(value):
    return sha256(canonical(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class PublicWorld:
    seed: int
    law_id: int
    cohort: str
    records: tuple[tuple[int,int,int],...]
    legal: tuple[int,...]

    def pair(self,subject):
        if type(subject) is not int:
            raise ValueError("WSP125_UNKNOWN_ACTION")
        for identity,a,b in self.records:
            if subject==identity:
                return a,b
        raise ValueError("WSP125_UNKNOWN_ACTION")

    def subject(self,left,right):
        if type(left) is not int or type(right) is not int:
            raise ValueError("WSP125_UNKNOWN_PUBLIC_PAIR")
        for identity,a,b in self.records:
            if a==left and b==right:
                return identity
        raise ValueError("WSP125_UNKNOWN_PUBLIC_PAIR")

    def fingerprint(self):
        return digest([self.seed,self.law_id,self.cohort,
                       self.records,self.legal])


@dataclass(frozen=True)
class ObservedEffect:
    seed: int
    law_id: int
    subject: int
    left: int
    right: int
    effect: int
    receipt_sha256: str


def world(seed):
    if type(seed) is not int or seed not in ALLOWED:
        raise PermissionError("WSP125_ORIGINAL_OR_UNKNOWN_SEED_DENIED")
    if seed in FIT:
        law_id=seed-125900
        cohort="fit"
    elif seed in TRANSFER:
        law_id=(seed-126200)//2
        cohort="transfer"
    else:
        law_id=seed-126500
        cohort="negative"
    rng=random.Random(seed)
    subjects=rng.sample(range(seed*4000,seed*4000+8000),64)
    records=[(subjects[a*8+b],a,b) for a in range(8) for b in range(8)]
    rng.shuffle(records)
    legal=tuple(subject for subject,_,_ in records) if cohort=="fit" else ()
    return PublicWorld(seed,law_id,cohort,tuple(records),legal)


def open_original(seed):
    raise PermissionError("WSP125_PRIMARY_FIRST_USE_UNAVAILABLE")


@lru_cache(maxsize=128)
def _hidden_law(law_id):
    if type(law_id) is not int or not 0<=law_id<128:
        raise PermissionError("WSP125_HIDDEN_LAW_OUTSIDE_ENGINEERING")
    value=int.from_bytes(sha256(
        f"WSP125|PRIVATE_DEVELOPMENT|{law_id}".encode("ascii")
    ).digest(),"big")
    rng=random.Random(value)
    left_size=rng.randrange(3,7)
    right_size=rng.randrange(3,7)
    left=sum(1<<a for a in rng.sample(range(8),left_size))
    right=sum(1<<b for b in rng.sample(range(8),right_size))
    delta=rng.randrange(1,8)
    return left,right,delta


def _hidden_effect(law_id,left,right,*,negative=False):
    left_mask,right_mask,delta=_hidden_law(law_id)
    result=left^right
    if (left_mask>>left)&1 and (right_mask>>right)&1:
        result^=delta
    if negative and left%2==1 and right%2==1:
        result^=1
    return result


class Custodian:
    def __init__(self,view):
        if (type(view) is not PublicWorld or view.seed not in ALLOWED or
                view!=world(view.seed)):
            raise PermissionError("WSP125_SOURCE_VIEW_NOT_REGISTERED")
        self.view=view
        self.budget=32 if view.seed in FIT else 0
        self.used=set()
        self.events=[]
        self.scored=False

    @property
    def calls(self):
        return len(self.events)

    @property
    def held(self):
        return tuple(subject for subject,_,_ in self.view.records
                     if subject not in self.used)

    @property
    def receipt(self):
        return digest([self.view.fingerprint(),self.events])

    def query(self,subject):
        if (self.scored or type(subject) is not int or
                subject not in self.view.legal or
                subject in self.used or self.calls>=self.budget):
            raise PermissionError("WSP125_QUERY_DUPLICATE_HELD_OR_BUDGET")
        a,b=self.view.pair(subject)
        effect=_hidden_effect(self.view.law_id,a,b)
        self.used.add(subject)
        self.events.append([subject,a,b,effect])
        return ObservedEffect(self.view.seed,self.view.law_id,subject,
                              a,b,effect,self.receipt)

    def score_once(self,predictions):
        if self.scored or self.calls!=self.budget:
            raise PermissionError("WSP125_SCORE_NOT_READY_OR_REPLAY")
        if type(predictions) is not dict or set(predictions)!=set(self.held):
            raise ValueError("WSP125_HELD_PREDICTION_SET_INVALID")
        if any(p is not None and (type(p) is not int or not 0<=p<8)
               for p in predictions.values()):
            raise ValueError("WSP125_HELD_PREDICTION_VALUE_INVALID")
        good=wrong=abstain=0
        for subject in self.held:
            proposed=predictions[subject]
            if proposed is None:
                abstain+=1
            elif proposed==_hidden_effect(
                    self.view.law_id,*self.view.pair(subject),
                    negative=self.view.cohort=="negative"):
                good+=1
            else:
                wrong+=1
        self.scored=True
        return {"seed":self.view.seed,"law_id":self.view.law_id,
                "public_sha256":self.view.fingerprint(),
                "source_sha256":self.receipt,
                "prediction_sha256":digest(sorted(predictions.items())),
                "held":len(self.held),"correct":good,
                "wrong_confident":wrong,"abstained":abstain,
                "source_calls":self.calls,"source_first_use":False,
                "scientific_pass":False,"native_admission":False}
