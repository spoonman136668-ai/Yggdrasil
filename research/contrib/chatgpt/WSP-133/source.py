"""WSP133 fresh source-only public synthetic semantic-role repair evaluation.

Source/evaluator imports WSP131 only to reuse publicly EXPOSED WSP130 warm laws,
not its previously scored target worlds. New target seed bands and random mapping
draws are disjoint and frozen by WSP133 prereg. No scientific original first-use.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import random
import json
import sys

name="_wsp131_public_source_for_wsp132"
sp=spec_from_file_location(name,Path(__file__).resolve().parents[1]/"WSP-131"/"source.py")
S=module_from_spec(sp);sys.modules[name]=S;sp.loader.exec_module(S)
PERMS=S.PERMS
ALLOWED=frozenset(range(169000,169064))|frozenset(range(170000,170032))|frozenset(range(171000,171016))
DENIED=S.PROTECTED | frozenset(range(165000,165064)) | frozenset(range(166000,166032)) | frozenset(range(167000,167016)) | frozenset(range(172000,172064))|frozenset(range(169800,169864))|frozenset(range(170800,170864))|frozenset(range(171800,171864))
assert not ALLOWED&DENIED
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"))
def digest(v):return sha256(canon(v).encode("utf8")).hexdigest()
def _seed(kind,i):
    return int.from_bytes(sha256(("WSP133|"+kind+"|"+str(i)).encode()).digest(),"big")

def _law_index(seed):
    if 169000<=seed<169064:return seed-169000,"known"
    if 170000<=seed<170032:return seed-170000,"shear"
    if 171000<=seed<171016:return seed-171000,"transfer"
    raise PermissionError("WSP133_UNREGISTERED_SEED")

@lru_cache(maxsize=96)
def _truth(seed):
    if type(seed) is not int or not (169000<=seed<169064 or 170000<=seed<170032):
        raise PermissionError("WSP133_SOURCE_TRUTH_UNREGISTERED")
    index,mode=_law_index(seed)
    law=S._origins()[index]
    base=S.P._law(law)["truth"]
    rng=random.Random(_seed("MAP",seed))
    p=PERMS[rng.randrange(720)]
    if mode=="known":
        return tuple(base[S._permute(x,p)] for x in range(256))
    existing={bytes(base[S._permute(x,q)] for x in range(256)) for q in PERMS}
    variants=[(i,j) for i in range(6) for j in range(6) if i!=j]
    rng.shuffle(variants)
    for i,j in variants:
        candidate=[]
        for x in range(256):
            z=S._permute(x,p)
            z^=((z>>j)&1)<<i
            candidate.append(base[z])
        if bytes(candidate) not in existing:
            return tuple(candidate)
    raise AssertionError("WSP133_SOURCE_SHEAR_COLLAPSED_TO_PURE_GRAMMAR")

@dataclass(frozen=True)
class View:
    seed:int
    law_id:int
    cohort:str
    records:tuple
    legal:frozenset
    by_subject:dict
    by_x:dict
    def subject(self,x):
        if type(x) is not int or not 0<=x<256:raise ValueError("WSP133_BAD_INPUT")
        return self.by_x[x]
    def input(self,subject):
        if type(subject) is not int or subject not in self.by_subject:
            raise ValueError("WSP133_BAD_SUBJECT")
        return self.by_subject[subject]
    def fingerprint(self):
        return digest([self.seed,self.law_id,self.cohort,self.records])

@lru_cache(maxsize=8)
def world(seed):
    if type(seed) is not int or seed not in ALLOWED or seed in DENIED:
        raise PermissionError("WSP133_SCIENCE_FIRST_USE_OR_UNREGISTERED_DENIED")
    index,mode=_law_index(seed)
    law=S._origins()[index]
    rng=random.Random(seed)
    ids=rng.sample(range(seed*1000,seed*1000+1000),256)
    rows=[(ids[x],x) for x in range(256)]
    rng.shuffle(rows)
    cohort="transfer" if mode=="transfer" else "probe"
    return View(seed,law,cohort,tuple(rows),
                frozenset(s for s,x in rows) if cohort=="probe" else frozenset(),
                {s:x for s,x in rows},{x:s for s,x in rows})

def open_original(seed):
    raise PermissionError("WSP133_SCIENCE_ORIGINAL_FIRST_USE_NOT_AUTHORIZED")
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
            raise PermissionError("WSP133_BAD_SOURCE_VIEW_CUSTODY")
        self.view=view
        self.budget=0 if view.cohort=="transfer" else 32
        parent=169000+(view.seed-171000) if view.cohort=="transfer" else view.seed
        self.truth=_truth(parent)
        self.events=[]
        self.seen=set()
        self.scored=False
        self.receipt=digest([view.fingerprint(),"begin"])
    def query(self,subject):
        if (self.scored or type(subject) is not int or
            subject not in self.view.legal or subject in self.seen or
            len(self.events)>=self.budget):
            raise PermissionError("WSP133_OVERBUDGET_REPLAY_OR_UNKNOWN_SOURCE")
        x=self.view.input(subject)
        row=[self.view.seed,self.view.law_id,subject,x,self.truth[x]]
        self.receipt=digest([self.receipt,row])
        self.events.append(row)
        self.seen.add(subject)
        return Evidence(*row,self.receipt)
    def held(self):
        return ((s,x) for s,x in self.view.records if s not in self.seen)
    def score_once(self,pred):
        if self.scored or len(self.events)!=self.budget:
            raise PermissionError("WSP133_EARLY_SCORE_OR_DUPLICATE")
        if type(pred) is not dict or len(pred)!=256-self.budget:
            raise ValueError("WSP133_PREDICTION_SET_INVALID")
        correct=wrong=abstain=0
        for subject,x in self.held():
            if subject not in pred:raise ValueError("WSP133_PREDICTION_MISSING")
            v=pred[subject]
            if v is None:abstain+=1
            elif type(v) is not int or v not in (0,1):
                raise ValueError("WSP133_PREDICTION_TYPE_INVALID")
            elif v==self.truth[x]:correct+=1
            else:wrong+=1
        self.scored=True
        mode="transfer" if self.view.cohort=="transfer" else _law_index(self.view.seed)[1]
        return {"mode":mode,"correct":correct,"wrong_confident":wrong,"abstained":abstain,
                "held":256-self.budget,"source_calls":self.budget}
