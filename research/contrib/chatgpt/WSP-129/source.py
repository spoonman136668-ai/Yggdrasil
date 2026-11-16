"""WSP129 source-only public synthetic causal composition worlds.

Models must not import this generator, hidden family assignment, or labels.
Protected original-source access fails BEFORE any RNG / truth generation.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
import json
import random

FIT = frozenset(range(148000, 148128))
TRANSFER = frozenset(range(150000, 150032))
ALLOWED = FIT | TRANSFER
DENIED = (frozenset(range(131000,131064)) |
          frozenset(range(131800,131864)) |
          frozenset(range(135800,135864)) |
          frozenset(range(138800,138864)) |
          frozenset(range(148800,148864)) |
          frozenset(range(150800,150864)) |
          frozenset(range(120800,120864)) |
          frozenset(range(121800,121864)) |
          frozenset(range(122800,122864)) |
          frozenset(range(123800,123864)) |
          frozenset(range(125800,125864)) |
          frozenset(range(127800,127864)))

def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"))

def digest(x):
    return sha256(canon(x).encode("utf8")).hexdigest()

def _seed(prefix,index):
    return int.from_bytes(sha256((prefix+str(index)).encode("ascii")).digest(),"big")

def _p(x,mask):
    return (x&mask).bit_count()&1

def _effect(a,b,left,right,op,flip):
    x,y=_p(a,left),_p(b,right)
    if op=="XOR":
        z=x^y
    elif op=="AND":
        z=x&y
    elif op=="OR":
        z=x|y
    else:
        raise AssertionError("WSP129_SOURCE_UNKNOWN_OP")
    return z^flip

def _truth(left,right,op,flip):
    return sum(_effect(a,b,left,right,op,flip)<<(16*a+b)
               for a in range(16) for b in range(16))

@lru_cache(maxsize=1)
def _grammar_tables():
    return frozenset(_truth(l,r,op,flip)
        for op in ("XOR","AND","OR")
        for l in range(1,16) for r in range(1,16) for flip in (0,1))

@lru_cache(maxsize=1)
def _assign():
    # A separate permutation prevents law_id or seed windows from encoding
    # family; all 128 train views share cohort="probe".
    laws=list(range(128))
    modes=["XOR"]*32+["AND"]*32+["OR"]*32+["OFF"]*32
    rng=random.Random(_seed("WSP129|ASSIGN|",128))
    rng.shuffle(laws)
    rng.shuffle(modes)
    return tuple(zip(laws,modes))

@lru_cache(maxsize=128)
def _truth_law(law_id):
    if type(law_id) is not int or not 0<=law_id<128:
        raise PermissionError("WSP129_SOURCE_LAW_UNREGISTERED")
    mode=next(m for lid,m in _assign() if lid==law_id)
    rng=random.Random(_seed("WSP129|WORLD|",148000+law_id))
    if mode!="OFF":
        left,right=rng.randint(1,15),rng.randint(1,15)
        flip=rng.randrange(2)
        return _truth(left,right,mode,flip)
    grammar=_grammar_tables()
    for _ in range(1000):
        l1,r1,l2,r2=[rng.randint(1,15) for j in range(4)]
        flip=rng.randrange(2)
        truth=0
        for a in range(16):
            for b in range(16):
                z=(_p(a,l1)^_p(b,r1)^
                   (_p(a,l2)&_p(b,r2))^flip)
                truth|=z<<(16*a+b)
        if truth not in grammar:
            return truth
    raise AssertionError("WSP129_OFF_GRAMMAR_SOURCE_GENERATION_FAILED")

def _law_and_kind(seed):
    if seed in FIT:
        return _assign()[seed-148000]
    fit=sorted(law for law,kind in _assign() if kind!="OFF")
    return fit[seed-150000],"transfer"

@dataclass(frozen=True)
class View:
    seed:int
    law_id:int
    cohort:str
    records:tuple
    legal:frozenset
    by_subject:dict
    by_pair:dict

    def subject(self,a,b):
        if (type(a) is not int or type(b) is not int or
                not 0<=a<16 or not 0<=b<16):
            raise ValueError("WSP129_INVALID_ACTION_PAIR")
        return self.by_pair[(a,b)]

    def pair(self,subject):
        if type(subject) is not int or subject not in self.by_subject:
            raise ValueError("WSP129_UNKNOWN_SUBJECT")
        return self.by_subject[subject]

    def fingerprint(self):
        return digest([self.seed,self.law_id,self.cohort,self.records])

@lru_cache(maxsize=8)
def world(seed):
    if type(seed) is not int or seed not in ALLOWED or seed in DENIED:
        raise PermissionError("WSP129_PROTECTED_OR_UNREGISTERED_SOURCE_DENIED")
    law,kind=_law_and_kind(seed)
    rng=random.Random(seed)
    ids=rng.sample(range(seed*1000,seed*1000+1000),256)
    pairs=[(ids[16*a+b],a,b) for a in range(16) for b in range(16)]
    rng.shuffle(pairs)
    return View(seed,law,"probe" if seed in FIT else "transfer",
                tuple(pairs),frozenset(s for s,_,_ in pairs) if seed in FIT else frozenset(),
                {s:(a,b) for s,a,b in pairs},
                {(a,b):s for s,a,b in pairs})

def open_original(seed):
    raise PermissionError("WSP129_INDEPENDENT_SCIENTIFIC_FIRST_USE_DENIED")

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
        if type(view) is not View or view.seed not in ALLOWED or view is not world(view.seed):
            raise PermissionError("WSP129_BAD_SOURCE_VIEW")
        self.view=view
        self.budget=24 if view.cohort=="probe" else 0
        self.events=[]
        self.seen=set()
        self.receipt=digest([view.fingerprint(),"begin"])
        self.scored=False

    def query(self,subject):
        if (self.scored or type(subject) is not int or
                subject not in self.view.legal or subject in self.seen or
                len(self.events)>=self.budget):
            raise PermissionError("WSP129_DUPLICATE_INVALID_OR_OVERBUDGET")
        a,b=self.view.pair(subject)
        bit=(_truth_law(self.view.law_id)>>(16*a+b))&1
        self.seen.add(subject)
        row=[self.view.seed,self.view.law_id,subject,a,b,bit]
        self.events.append(row)
        self.receipt=digest([self.receipt,row])
        return Evidence(*row,self.receipt)

    def held(self):
        return ((subject,a,b) for subject,a,b in self.view.records
                if subject not in self.seen)

    def score_once(self,predictions):
        if self.scored or len(self.events)!=self.budget:
            raise PermissionError("WSP129_SCORE_REPLAY_OR_SOURCE_BUDGET")
        if type(predictions) is not dict or len(predictions)!=(256-self.budget):
            raise ValueError("WSP129_PREDICTION_SET_INVALID")
        truth=_truth_law(self.view.law_id)
        good=bad=unknown=0
        brier=0.0
        for subject,a,b in self.held():
            if subject not in predictions:
                raise ValueError("WSP129_HELD_SUBJECT_MISSING")
            val=predictions[subject]
            actual=(truth>>(16*a+b))&1
            if val is None:
                unknown+=1
            elif type(val) is int and val in (0,1):
                good+=int(val==actual)
                bad+=int(val!=actual)
            else:
                raise ValueError("WSP129_INVALID_PREDICTION")
        self.scored=True
        kind=next(kind for law,kind in _assign() if law==self.view.law_id)
        return {"kind":kind,"correct":good,"wrong_confident":bad,
                "abstained":unknown,"held":256-self.budget,
                "source_calls":self.budget}
