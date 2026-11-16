"""WSP132-R2 independent public-synthetic source-only semantic mapping worlds.

Already exposed WSP132 R1 worlds are available exclusively as development
diagnostics. Fresh R2 source is disjoint and hidden from candidate modules.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
import json,random,sys

sp=spec_from_file_location("_wsp132_r1_source_only_for_r2",
    Path(__file__).resolve().parents[1]/"WSP-132"/"source.py")
OLD=module_from_spec(sp);sys.modules[sp.name]=OLD;sp.loader.exec_module(OLD)
S=OLD.S
PERMS=S.PERMS
NEW=frozenset(range(169000,169064))|frozenset(range(170000,170032))|frozenset(range(171000,171016))
PROTECTED=OLD.DENIED|frozenset(range(172800,172864))|frozenset(range(169800,169864))|frozenset(range(170800,170864))|frozenset(range(171800,171864))
assert not NEW&PROTECTED

def canon(a):return json.dumps(a,sort_keys=True,separators=(",",":"))
def digest(a):return sha256(canon(a).encode("utf8")).hexdigest()
def _seed(kind,seed):
    return int.from_bytes(sha256(("WSP132R2|"+kind+"|"+str(seed)).encode("ascii")).digest(),"big")
def _family(seed):
    if 169000<=seed<169064:return seed-169000,"known"
    if 170000<=seed<170032:return seed-170000,"shear"
    if 171000<=seed<171016:return seed-171000,"transfer"
    raise PermissionError("WSP132R2_UNREGISTERED_SOURCE")
@lru_cache(maxsize=96)
def _truth(seed):
    if type(seed) is not int or not (169000<=seed<169064 or 170000<=seed<170032):
        raise PermissionError("WSP132R2_HIDDEN_SOURCE_UNREGISTERED")
    index,kind=_family(seed)
    law=S._origins()[index]
    base=S.P._law(law)["truth"]
    rng=random.Random(_seed("MAP",seed))
    mapping=PERMS[rng.randrange(720)]
    if kind=="known":
        return tuple(base[S._permute(x,mapping)] for x in range(256))
    pure={bytes(base[S._permute(x,p)] for x in range(256)) for p in PERMS}
    pairs=[(i,j) for i in range(6) for j in range(6) if i!=j]
    rng.shuffle(pairs)
    for i,j in pairs:
        sig=[]
        for x in range(256):
            z=S._permute(x,mapping)
            z^=((z>>j)&1)<<i
            sig.append(base[z])
        if bytes(sig) not in pure:
            return tuple(sig)
    raise AssertionError("WSP132R2_SHEAR_INDISTINGUISHABLE")

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
        if type(x) is not int or not 0<=x<256:raise ValueError("R2_BAD_TYPED_INPUT")
        return self.by_x[x]
    def input(self,s):
        if type(s) is not int or s not in self.by_subject:raise ValueError("R2_BAD_SUBJECT")
        return self.by_subject[s]
    def fingerprint(self):
        return digest([self.seed,self.law_id,self.cohort,self.records])

@lru_cache(maxsize=8)
def world(seed):
    if type(seed) is not int or seed not in NEW or seed in PROTECTED:
        raise PermissionError("WSP132R2_SOURCE_DENIED")
    index,kind=_family(seed)
    law=S._origins()[index]
    rng=random.Random(seed)
    ids=rng.sample(range(seed*1000,seed*1000+1000),256)
    rows=[(ids[x],x) for x in range(256)]
    rng.shuffle(rows)
    return View(seed,law,"transfer" if kind=="transfer" else "probe",
                tuple(rows),frozenset(s for s,x in rows) if kind!="transfer" else frozenset(),
                {s:x for s,x in rows},{x:s for s,x in rows})

def open_original(seed):
    raise PermissionError("WSP132R2_PROTECTED_FIRST_USE_NOT_AUTHORIZED")

@dataclass(frozen=True)
class Evidence:
    seed:int
    law_id:int
    subject:int
    input:int
    effect:int
    receipt:str

class Custodian:
    def __init__(self,v):
        if type(v) is not View or v.seed not in NEW or v is not world(v.seed):
            raise PermissionError("WSP132R2_SOURCE_VIEW_CUSTODY_INVALID")
        self.view=v
        self.budget=0 if v.cohort=="transfer" else 32
        self.truth=_truth(169000+v.seed-171000 if v.cohort=="transfer" else v.seed)
        self.events=[];self.seen=set();self.scored=False
        self.receipt=digest([v.fingerprint(),"begin"])
    def query(self,subject):
        if (self.scored or type(subject) is not int or
             subject not in self.view.legal or subject in self.seen or
             len(self.events)>=self.budget):
            raise PermissionError("WSP132R2_SOURCE_ACTION_OVERBUDGET")
        x=self.view.input(subject)
        row=[self.view.seed,self.view.law_id,subject,x,self.truth[x]]
        self.receipt=digest([self.receipt,row])
        self.events.append(row);self.seen.add(subject)
        return Evidence(*row,self.receipt)
    def held(self):
        return ((s,x) for s,x in self.view.records if s not in self.seen)
    def score_once(self,predictions):
        if self.scored or len(self.events)!=self.budget:
            raise PermissionError("WSP132R2_SCORE_WRONG_BUDGET_OR_REPLAY")
        if type(predictions) is not dict or len(predictions)!=256-self.budget:
            raise ValueError("WSP132R2_HELD_PREDICTIONS_NOT_COMPLETE")
        correct=wrong=abstain=0
        for s,x in self.held():
            if s not in predictions:raise ValueError("WSP132R2_PREDICTION_MISSING")
            bit=predictions[s]
            if bit is None:abstain+=1
            elif type(bit) is not int or bit not in (0,1):raise ValueError("WSP132R2_BAD_PREDICTION")
            elif bit==self.truth[x]:correct+=1
            else:wrong+=1
        self.scored=True
        return {"kind":_family(self.view.seed)[1],"correct":correct,
                "wrong_confident":wrong,"abstained":abstain,
                "held":256-self.budget,"source_calls":self.budget}
