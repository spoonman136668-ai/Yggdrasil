"""WSP131 new semantic variable-rebinding source and scorer only.

Constructs publicly measured synthetic WSP130 consequence functions under
hidden six-variable feature permutations or non-permutation linear shears.
Learners and controls MUST NOT import source; cohort never exposes mode/shift.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import permutations
from pathlib import Path
import json
import random
import sys

_spec=spec_from_file_location("_wsp130_public_source_for_rebinding",
    Path(__file__).resolve().parents[1]/"WSP-130"/"source.py")
P=module_from_spec(_spec);sys.modules[_spec.name]=P;_spec.loader.exec_module(P)
PERMS=tuple(permutations(range(6)))
ALLOWED=frozenset(range(160000,160064))|frozenset(range(161000,161032))|frozenset(range(162000,162016))
PROTECTED=(frozenset(range(131000,131064))|frozenset(range(131800,131864))|
frozenset(range(135800,135864))|frozenset(range(138800,138864))|
frozenset(range(148800,148864))|frozenset(range(150800,150864))|
frozenset(range(154800,154864))|frozenset(range(155800,155864))|
frozenset(range(156000,156064))|frozenset(range(160800,160864))|
frozenset(range(161800,161864))|frozenset(range(162800,162864)))
assert len(PERMS)==720

def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"))
def digest(v):return sha256(canon(v).encode("utf8")).hexdigest()
def _seed(kind,v):
    return int.from_bytes(sha256(("WSP131|"+kind+"|"+str(v)).encode()).digest(),"big")
def _permute(x,p):
    y=x&0b11000000
    for bit in range(6): y|=((x>>bit)&1)<<p[bit]
    return y

@lru_cache(maxsize=1)
def _origins():
    high=[i for i,mode in enumerate(P._modes())
          if mode in ("quartic","quintic")]
    if len(high)!=64:raise AssertionError("WSP131_INHERITED_SOURCE_FAMILY_DRIFT")
    return tuple(sorted(high))

def warm_world(law):
    if type(law) is not int or law not in _origins():
        raise PermissionError("WSP131_INVALID_WARM_LAW")
    return P.world(154000+law)
def warm_custodian(view):return P.Custodian(view)

def _target_law(seed):
    if 160000<=seed<160064: return _origins()[seed-160000],"known",seed
    if 161000<=seed<161032:return _origins()[seed-161000],"shear",seed
    return _origins()[seed-162000],"transfer",160000+(seed-162000)

@lru_cache(maxsize=96)
def _physical_law(seed):
    if (type(seed) is not int or
        not (160000<=seed<160064 or 161000<=seed<161032)):
        raise PermissionError("WSP131_INVALID_PHYSICAL_SOURCE_SEED")
    law,kind,_=_target_law(seed)
    origin=P._law(law)["truth"]
    rng=random.Random(_seed("MAP",seed))
    p=PERMS[rng.randrange(len(PERMS))]
    if kind=="known":
        return {"mode":kind,"law":law,"permutation":p,"shear":None,
                "truth":tuple(origin[_permute(x,p)] for x in range(256))}
    known_tables={bytes(origin[_permute(x,q)] for x in range(256))
                  for q in PERMS}
    choices=[(i,j) for i in range(6) for j in range(6) if i!=j]
    rng.shuffle(choices)
    for i,j in choices:
        effects=[]
        for x in range(256):
            z=_permute(x,p);z^=((z>>j)&1)<<i
            effects.append(origin[z])
        if bytes(effects) not in known_tables:
            return {"mode":"shear","law":law,"permutation":p,
                    "shear":(i,j),"truth":tuple(effects)}
    raise AssertionError("WSP131_OFF_FAMILY_SHEAR_INDISTINGUISHABLE")

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
            raise ValueError("WSP131_UNKNOWN_SUBJECT")
        return self.by_subject[subject]
    def subject(self,x):
        if type(x) is not int or not 0<=x<256:
            raise ValueError("WSP131_INVALID_TYPED_INPUT")
        return self.by_x[x]
    def fingerprint(self):
        return digest([self.seed,self.law_id,self.cohort,self.records])

@lru_cache(maxsize=8)
def world(seed):
    if type(seed) is not int or seed not in ALLOWED or seed in PROTECTED:
        raise PermissionError("WSP131_PROTECTED_OR_UNREGISTERED_SOURCE_DENIED")
    law,kind,parent=_target_law(seed)
    rng=random.Random(seed)
    ids=rng.sample(range(seed*1000,seed*1000+1000),256)
    records=[(ids[x],x) for x in range(256)]
    rng.shuffle(records)
    return View(seed,law,"transfer" if kind=="transfer" else "probe",
                tuple(records),frozenset(s for s,x in records) if kind!="transfer" else frozenset(),
                {s:x for s,x in records},{x:s for s,x in records})

def open_original(seed):
    raise PermissionError("WSP131_SCIENTIFIC_FIRST_USE_NOT_AUTHORIZED")

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
            raise PermissionError("WSP131_SOURCE_CUSTODY_INVALID")
        self.view=view
        self.budget=32 if view.cohort=="probe" else 0
        self.parent=160000+(_origins().index(view.law_id)) if view.cohort=="transfer" else view.seed
        self.truth=_physical_law(self.parent)["truth"]
        self.seen=set();self.events=[];self.scored=False
        self.receipt=digest([view.fingerprint(),"begin"])
    def query(self,subject):
        if (self.scored or type(subject) is not int or
            subject not in self.view.legal or subject in self.seen or
            len(self.events)>=self.budget):
            raise PermissionError("WSP131_INVALID_OR_REPLAYED_INTERVENTION")
        x=self.view.input(subject)
        row=[self.view.seed,self.view.law_id,subject,x,self.truth[x]]
        self.receipt=digest([self.receipt,row])
        self.seen.add(subject);self.events.append(row)
        return Evidence(*row,self.receipt)
    def held(self):
        return ((s,x) for s,x in self.view.records if s not in self.seen)
    def score_once(self,checkpoint_predictions):
        if self.scored or len(self.events)!=self.budget:
            raise PermissionError("WSP131_SCORE_BEFORE_BUDGET_OR_REPLAY")
        if type(checkpoint_predictions) is not dict or set(checkpoint_predictions)!={0,4,8,16,32}:
            raise ValueError("WSP131_CHECKPOINTS_INCOMPLETE")
        held=tuple(self.held())
        result={}
        for stage,pred in checkpoint_predictions.items():
            if type(pred) is not dict or len(pred)!=256-self.budget:
                raise ValueError("WSP131_CHECKPOINT_HELD_SET_INVALID")
            good=bad=unknown=0
            for subject,x in held:
                if subject not in pred: raise ValueError("WSP131_MISSING_HELD_SUBJECT")
                v=pred[subject]
                if v is None: unknown+=1
                elif type(v) is not int or v not in (0,1):
                    raise ValueError("WSP131_INVALID_PREDICTION")
                elif v==self.truth[x]: good+=1
                else: bad+=1
            result[stage]={"correct":good,"wrong_confident":bad,
                           "abstained":unknown,"held":len(held),
                           "source_calls":self.budget}
        self.scored=True
        return {"condition":"transfer" if self.view.cohort=="transfer" else _physical_law(self.view.seed)["mode"],
                "stages":result}
