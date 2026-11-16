"""WSP130 source-only causal consequence evaluator and first-use fences.

The learner and every strong control NEVER import this module. Hidden masks,
families, evaluator truth and stealth targets remain source-only.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
import json
import random

LOW=tuple(sorted((x for x in range(256) if x.bit_count()<=3),key=lambda x:(x.bit_count(),x)))
CORE=(255,)+tuple(255^(1<<i) for i in range(8))
HASH_AUDIT=tuple(sorted((x for x in range(256) if x not in set(LOW+CORE)),
    key=lambda x:(sha256(("WSP130|AUDIT|"+str(x)).encode()).digest(),x)))
MASKS4=tuple(x for x in range(256) if x.bit_count()==4)
MASKS5=tuple(x for x in range(256) if x.bit_count()==5)
ALLOWED=frozenset(range(154000,154128)) | frozenset(range(154500,154516)) | frozenset(range(155000,155032))
DENIED=(frozenset(range(131000,131064))|frozenset(range(131800,131864))|
        frozenset(range(135800,135864))|frozenset(range(138800,138864))|
        frozenset(range(148800,148864))|frozenset(range(150800,150864))|
        frozenset(range(154800,154864))|frozenset(range(155800,155864))|
        frozenset(range(156000,156064)))

assert len(LOW)==93 and len(CORE)==9 and len(HASH_AUDIT)==154
assert len(set(LOW+CORE+HASH_AUDIT))==256

def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"))

def digest(x):
    return sha256(canon(x).encode("utf8")).hexdigest()

def _seed(kind,index):
    return int.from_bytes(sha256(("WSP130|"+kind+"|"+str(index)).encode()).digest(),"big")

@lru_cache(maxsize=1)
def _modes():
    modes=["none"]*32+["quartic"]*32+["quintic"]*32+["double"]*32
    random.Random(_seed("ASSIGN",130)).shuffle(modes)
    return tuple(modes)

def _transfer_law_ids():
    modes=_modes()
    return (tuple(i for i in range(128) if modes[i]=="quartic")[:16]+
            tuple(i for i in range(128) if modes[i]=="quintic")[:16])

def _stealth_target(law):
    # Adversarial source-only witness, selected from the 128 unqueried
    # coordinates under an unchanged-world source-blind deterministic policy.
    probe=set(LOW+CORE+HASH_AUDIT[:26])
    held=[x for x in range(256) if x not in probe]
    if len(held)!=128:
        raise AssertionError("WSP130_BAD_STEALTH_PROBE_PLAN")
    return held[random.Random(_seed("STEALTH",law)).randrange(128)]

@lru_cache(maxsize=144)
def _law(law):
    if type(law) is not int or not 0<=law<144:
        raise PermissionError("WSP130_UNREGISTERED_HIDDEN_LAW")
    rng=random.Random(_seed("LAW",law))
    coef={x for x in LOW if rng.random()<0.25}
    if not coef:
        coef.add(0)
    if law>=128:
        mode="stealth"
        high=()
        target=_stealth_target(law)
    else:
        mode=_modes()[law]
        if mode=="none": high=()
        elif mode=="quartic": high=(rng.choice(MASKS4),)
        elif mode=="quintic": high=(rng.choice(MASKS5),)
        elif mode=="double":
            pool=MASKS4+MASKS5
            high=tuple(rng.sample(pool,2))
        else:
            raise AssertionError("WSP130_INVALID_SOURCE_KIND")
        target=None
    values=[]
    for x in range(256):
        bit=0
        for monomial in coef:
            if (x&monomial)==monomial:
                bit^=1
        for mask in high:
            if (x&mask)==mask:
                bit^=1
        if x==target:
            bit^=1
        values.append(bit)
    return {"mode":mode,"coefs":tuple(sorted(coef)),"high":high,
            "stealth_target":target,"truth":tuple(values)}

@dataclass(frozen=True)
class View:
    seed:int
    law_id:int
    cohort:str
    records:tuple
    legal:frozenset
    by_subject:dict
    by_x:dict

    def input(self,subject):
        if type(subject) is not int or subject not in self.by_subject:
            raise ValueError("WSP130_UNKNOWN_SUBJECT")
        return self.by_subject[subject]

    def subject(self,x):
        if type(x) is not int or not 0<=x<256:
            raise ValueError("WSP130_INVALID_TYPED_INPUT")
        return self.by_x[x]

    def fingerprint(self):
        return digest([self.seed,self.law_id,self.cohort,self.records])

@lru_cache(maxsize=8)
def world(seed):
    if type(seed) is not int or seed not in ALLOWED or seed in DENIED:
        raise PermissionError("WSP130_UNREGISTERED_OR_PROTECTED_SOURCE_DENIED")
    if 154000<=seed<154128:
        law=seed-154000
        cohort="probe"
    elif 154500<=seed<154516:
        law=128+(seed-154500)
        cohort="probe"
    else:
        law=_transfer_law_ids()[seed-155000]
        cohort="transfer"
    rng=random.Random(seed)
    ids=rng.sample(range(seed*1000,seed*1000+1000),256)
    records=[(ids[x],x) for x in range(256)]
    rng.shuffle(records)
    return View(seed,law,cohort,tuple(records),
                frozenset(s for s,x in records) if cohort=="probe" else frozenset(),
                {s:x for s,x in records},
                {x:s for s,x in records})

def open_original(seed):
    raise PermissionError("WSP130_INDEPENDENT_SCIENTIFIC_FIRST_USE_NOT_AUTHORIZED")

@dataclass(frozen=True)
class Evidence:
    seed:int
    law_id:int
    subject:int
    input:int
    effect:int
    receipt:str

class Custodian:
    def __init__(self,view):
        if type(view) is not View or view.seed not in ALLOWED or view is not world(view.seed):
            raise PermissionError("WSP130_SOURCE_VIEW_CUSTODY_INVALID")
        self.view=view
        self.budget=128 if view.cohort=="probe" else 0
        self.seen=set()
        self.events=[]
        self.receipt=digest([view.fingerprint(),"begin"])
        self.scored=False

    def query(self,subject):
        if (self.scored or type(subject) is not int or
                subject not in self.view.legal or
                subject in self.seen or len(self.events)>=self.budget):
            raise PermissionError("WSP130_INVALID_REPLAYED_OR_UNAUTHORIZED_ACTION")
        x=self.view.input(subject)
        bit=_law(self.view.law_id)["truth"][x]
        row=[self.view.seed,self.view.law_id,subject,x,bit]
        self.receipt=digest([self.receipt,row])
        self.seen.add(subject)
        self.events.append(row)
        return Evidence(*row,self.receipt)

    def held(self):
        return ((s,x) for s,x in self.view.records if s not in self.seen)

    def score_once(self,predictions):
        if self.scored or len(self.events)!=self.budget:
            raise PermissionError("WSP130_SCORING_EARLY_OR_REPLAYED")
        if type(predictions) is not dict or len(predictions)!=256-self.budget:
            raise ValueError("WSP130_WRONG_HELD_COUNT")
        law=_law(self.view.law_id)
        correct=wrong=abstain=0
        for s,x in self.held():
            if s not in predictions:
                raise ValueError("WSP130_HELD_SUBJECT_MISSING")
            p=predictions[s]
            if p is None:
                abstain+=1
            elif type(p) is not int or p not in (0,1):
                raise ValueError("WSP130_WRONG_TYPE_PREDICTION")
            elif p==law["truth"][x]:
                correct+=1
            else:
                wrong+=1
        self.scored=True
        return {"kind":law["mode"],"correct":correct,"wrong_confident":wrong,
                "abstained":abstain,"held":256-self.budget,
                "source_calls":self.budget}
