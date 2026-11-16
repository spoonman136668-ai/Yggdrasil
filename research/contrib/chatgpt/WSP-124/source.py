"""WSP-124 independent *engineering-only* consequence source.

This is NOT a sealed scientific oracle. Learners must not import this module.
Public 8x8 actions are relabeled into fresh opaque identities for each world.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
import json
import random

FIT = frozenset(range(128900,128916))
TRANSFER = frozenset(range(129000,130024))
OFFFAMILY = frozenset(range(130100,130356))
ENGINEERING = FIT | TRANSFER | OFFFAMILY
ORIGINAL = frozenset(range(127000,127064))
PROTECTED = (frozenset(range(127800,127864)) |
             frozenset(range(123800,123864)) |
             frozenset(range(122800,122864)) |
             frozenset(range(121800,121864)) |
             frozenset(range(120800,120864)))
N = 8


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"))


def digest(value):
    return sha256(canonical(value).encode("utf-8")).hexdigest()


def _is_seed(seed):
    return type(seed) is int and seed in ENGINEERING


def _domain(seed):
    if seed in FIT:
        return seed-128900
    if seed in TRANSFER:
        return (seed-129000)//64
    return (seed-130100)//16


@dataclass(frozen=True)
class PublicView:
    seed: int
    domain: int
    records: tuple[tuple[int,int,int],...]
    legal: tuple[int,...]
    by_subject: dict[int,tuple[int,int]]
    by_pair: dict[tuple[int,int],int]

    def pair(self,subject):
        if type(subject) is not int or subject not in self.by_subject:
            raise ValueError("WSP124_UNKNOWN_SUBJECT")
        return self.by_subject[subject]

    def subject(self,left,right):
        return self.by_pair[left,right]

    def fingerprint(self):
        return digest([self.seed,self.domain,self.records,self.legal])


@dataclass(frozen=True)
class ObservedEffect:
    seed: int
    domain: int
    subject: int
    left: int
    right: int
    effect: int
    source_sha256: str


def world(seed):
    # First-use denied BEFORE calling any random generator.
    if not _is_seed(seed):
        raise PermissionError("WSP124_ORIGINAL_OR_PROTECTED_SOURCE_DENIED")
    d=_domain(seed)
    rng=random.Random(seed)
    subjects=rng.sample(range(seed*2048,seed*2048+4096),64)
    records=[(subjects[a*N+b],a,b) for a in range(N) for b in range(N)]
    rng.shuffle(records)
    legal=tuple(x for x,_,_ in records) if seed in FIT else ()
    return PublicView(seed,d,tuple(records),legal,
                      {s:(a,b) for s,a,b in records},
                      {(a,b):s for s,a,b in records})


def open_original(seed):
    raise PermissionError("WSP124_PRIMARY_FIRST_USE_NOT_INSTALLED")


@lru_cache(maxsize=16)
def _hidden_parameters(domain):
    if type(domain) is not int or not 0<=domain<16:
        raise PermissionError("WSP124_UNKNOWN_SOURCE_DOMAIN")
    def byte(label):
        return sha256(("WSP124-DEVELOPMENT-V1|"+str(domain)+"|"+label).
                      encode("ascii")).digest()[0]
    left=tuple(byte("L"+str(a))&7 for a in range(N))
    right=tuple(byte("R"+str(b))&7 for b in range(N))
    tx=2+byte("THRESHOLD-X")%6
    ty=2+byte("THRESHOLD-Y")%6
    delta=1+byte("INTERACTION-DELTA")%7
    return left,right,tx,ty,delta


def _outcome(domain,left,right,*,offfamily=False,repair=True):
    L,R,tx,ty,delta=_hidden_parameters(domain)
    effect=L[left]^R[right]
    if repair and left>=tx and right>=ty:
        effect^=delta
    if offfamily and left%2==1 and right%2==1:
        effect^=1
    return effect


class Custodian:
    def __init__(self,public):
        if (type(public) is not PublicView or not _is_seed(public.seed)
                or public!=world(public.seed)):
            raise PermissionError("WSP124_UNREGISTERED_PUBLIC_SOURCE")
        self.public=public
        self.budget=23 if public.seed in FIT else 0
        self._used=set()
        self._events=[]
        self._scored=False

    @property
    def count(self):
        return len(self._events)

    @property
    def receipt(self):
        return digest([self.public.fingerprint(),self._events])

    @property
    def held(self):
        return tuple(s for s,_,_ in self.public.records if s not in self._used)

    def query(self,subject):
        if (self._scored or type(subject) is not int
                or subject not in self.public.legal or subject in self._used
                or self.count>=self.budget):
            raise PermissionError("WSP124_HELD_DUPLICATE_OR_BUDGET_DENIED")
        a,b=self.public.pair(subject)
        y=_outcome(self.public.domain,a,b)
        self._used.add(subject)
        self._events.append([subject,a,b,y])
        return ObservedEffect(self.public.seed,self.public.domain,subject,a,b,
                              y,self.receipt)

    def score_once(self,predictions):
        if self._scored or self.count!=self.budget:
            raise PermissionError("WSP124_SCORE_NOT_READY_OR_REPLAY")
        if type(predictions) is not dict or set(predictions)!=set(self.held):
            raise ValueError("WSP124_BAD_HELD_PREDICTION_SET")
        if any(v is not None and (type(v) is not int or not 0<=v<8)
               for v in predictions.values()):
            raise ValueError("WSP124_BAD_HELD_PREDICTION_VALUE")
        ncorrect=nwrong=nabstain=0
        for subject in self.held:
            predicted=predictions[subject]
            if predicted is None:
                nabstain+=1
            elif predicted==_outcome(self.public.domain,
                                     *self.public.pair(subject),
                                     offfamily=self.public.seed in OFFFAMILY):
                ncorrect+=1
            else:
                nwrong+=1
        self._scored=True
        return {"seed":self.public.seed,"domain":self.public.domain,
                "source_sha256":self.receipt,
                "public_sha256":self.public.fingerprint(),
                "held":len(self.held),"correct":ncorrect,
                "wrong_confident":nwrong,"abstained":nabstain,
                "source_calls":self.count,
                "scientific_pass":False,"source_first_use":False,
                "native_admission":False}
