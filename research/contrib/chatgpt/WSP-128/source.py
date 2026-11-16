"""WSP128 source-only changed-causal-law engineering worlds.

Learners NEVER import this module. All three conditions have identical public
shape/cohort and are deterministically scrambled across 192 opaque seeds.
Original/protected first-use remains denied before source generation.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
import random
import sys

_parent_path=Path(__file__).resolve().parents[1]/"WSP-127"/"source.py"
_spec=spec_from_file_location("_wsp127_public_development_source_for_wsp128",_parent_path)
P=module_from_spec(_spec)
sys.modules[_spec.name]=P
_spec.loader.exec_module(P)

ALLOWED=frozenset(range(139000,139192))
DENIED=(frozenset(range(131000,131064)) |
        frozenset(range(131800,131864)) |
        frozenset(range(135800,135864)) |
        frozenset(range(138800,138864)) |
        frozenset(range(120800,120864)) |
        frozenset(range(121800,121864)) |
        frozenset(range(122800,122864)) |
        frozenset(range(123800,123864)) |
        frozenset(range(125800,125864)) |
        frozenset(range(127800,127864)))

def _canon(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"))

def _digest(obj):
    return sha256(_canon(obj).encode("utf8")).hexdigest()

def _seed(prefix,law):
    return int.from_bytes(sha256((prefix+str(law)).encode("ascii")).digest(),"big")

@lru_cache(maxsize=1)
def _assignment():
    assignments=[(law,cond) for law in range(64)
                 for cond in ("unchanged","rank9","rank10")]
    random.Random(_seed("WSP128|WORLD_ASSIGNMENT|",128)).shuffle(assignments)
    return tuple(assignments)

@lru_cache(maxsize=64)
def _patch_rows(law,condition):
    if type(law) is not int or not 0<=law<64:
        raise PermissionError("WSP128_SOURCE_UNREGISTERED_LAW")
    old=P._rows(law)
    if condition=="unchanged":
        return old
    if condition not in ("rank9","rank10"):
        raise PermissionError("WSP128_SOURCE_UNREGISTERED_PHYSICS")
    count=1 if condition=="rank9" else 2
    rng=random.Random(_seed("WSP128|PATCH9|" if count==1 else
                           "WSP128|PATCH10|",law))
    for _ in range(1000):
        left=[rng.getrandbits(64) for _ in range(count)]
        right=[rng.getrandbits(64) for _ in range(count)]
        if not all(left) or not all(right):
            continue
        rows=list(old)
        for a in range(64):
            for i in range(count):
                if left[i] & (1<<a):
                    rows[a]^=right[i]
        if P.rank(rows)==8+count:
            return tuple(rows)
    raise AssertionError("WSP128_SOURCE_CHANGED_RANK_GENERATION_FAILED")

@dataclass(frozen=True)
class PublicView:
    seed:int
    law_id:int
    cohort:str
    records:tuple
    legal:frozenset
    by_subject:dict
    by_pair:dict

    def pair(self,subject):
        if type(subject) is not int or subject not in self.by_subject:
            raise ValueError("WSP128_UNKNOWN_ACTION")
        return self.by_subject[subject]

    def subject(self,a,b):
        if (type(a) is not int or type(b) is not int or
                not 0<=a<64 or not 0<=b<64):
            raise ValueError("WSP128_INVALID_TYPED_ACTION")
        return self.by_pair[(a,b)]

    def fingerprint(self):
        return _digest([self.seed,self.law_id,self.cohort,self.records])

@lru_cache(maxsize=5)
def world(seed):
    if type(seed) is not int or seed not in ALLOWED or seed in DENIED:
        raise PermissionError("WSP128_PROTECTED_OR_UNREGISTERED_SOURCE_DENIED")
    law,condition=_assignment()[seed-139000]
    rng=random.Random(seed)
    ids=rng.sample(range(seed*10000,seed*10000+10000),4096)
    records=[(ids[a*64+b],a,b) for a in range(64) for b in range(64)]
    rng.shuffle(records)
    return PublicView(seed,law,"probe",tuple(records),
                      frozenset(s for s,_,_ in records),
                      {s:(a,b) for s,a,b in records},
                      {(a,b):s for s,a,b in records})

def training_view(law):
    if type(law) is not int or not 0<=law<64:
        raise PermissionError("WSP128_INVALID_TRAIN_LAW")
    return P.world(135000+law)

def training_custodian(view):
    return P.Custodian(view)

def open_original(seed):
    raise PermissionError("WSP128_SCIENTIFIC_FIRST_USE_NOT_AUTHORIZED")

@dataclass(frozen=True)
class Evidence:
    seed:int
    law_id:int
    subject:int
    left:int
    right:int
    effect:int
    receipt:str

class Custodian:
    def __init__(self,view):
        if (type(view) is not PublicView or
                view.seed not in ALLOWED or view is not world(view.seed)):
            raise PermissionError("WSP128_SOURCE_VIEW_MISMATCH")
        self.view=view
        self._condition=_assignment()[view.seed-139000][1]
        self._rows=_patch_rows(view.law_id,self._condition)
        self.budget=512
        self.seen=set()
        self.events=[]
        self.receipt=_digest([view.fingerprint(),"begin"])
        self.scored=False

    def query(self,subject):
        if (self.scored or type(subject) is not int or
                subject not in self.view.legal or subject in self.seen or
                len(self.events)>=self.budget):
            raise PermissionError("WSP128_INVALID_DUPLICATE_OR_OVERBUDGET_ACTION")
        a,b=self.view.pair(subject)
        bit=(self._rows[a]>>b)&1
        self.seen.add(subject)
        self.events.append([self.view.seed,self.view.law_id,subject,a,b,bit])
        self.receipt=_digest([self.receipt,self.events[-1]])
        return Evidence(*self.events[-1],self.receipt)

    def held(self):
        return ((s,a,b) for s,a,b in self.view.records if s not in self.seen)

    def score_once(self,predictions):
        if self.scored or len(self.events)!=self.budget:
            raise PermissionError("WSP128_SCORE_REPLAY_OR_BUDGET_INVALID")
        if type(predictions) is not dict or len(predictions)!=3584:
            raise ValueError("WSP128_HELD_PREDICTIONS_MISSING")
        correct=wrong=abstained=0
        for subject,a,b in self.held():
            if subject not in predictions:
                raise ValueError("WSP128_MISSING_HELD_SUBJECT")
            p=predictions[subject]
            if p is None:
                abstained+=1
            elif type(p) is not int or p not in (0,1):
                raise ValueError("WSP128_BAD_PREDICTION")
            elif p==((self._rows[a]>>b)&1):
                correct+=1
            else:
                wrong+=1
        self.scored=True
        return {"condition":self._condition,"correct":correct,
                "wrong_confident":wrong,"abstained":abstained,
                "held":3584,"source_calls":512}
