"""WSP134 SOURCE ONLY: new synthetic causal effect worlds. Never import in learners."""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
import json
import random

KNOWN=frozenset(range(174000,174064))
UNFAMILIAR=frozenset(range(175000,175032))
TRANSFER=frozenset(range(176000,176016))
ALLOWED=KNOWN|UNFAMILIAR|TRANSFER
PROTECTED=frozenset(range(174800,174864))|frozenset(range(175800,175864))|frozenset(range(176800,176864))|frozenset(range(177000,177064))
assert not (ALLOWED & PROTECTED)
OPS=("AND","OR","XOR","XNOR")

def canon(o):
    return json.dumps(o,sort_keys=True,separators=(",",":"))
def digest(o):
    return sha256(canon(o).encode("utf8")).hexdigest()
def _check(seed):
    if type(seed) is not int or seed not in ALLOWED or seed in PROTECTED:
        raise PermissionError("WSP134_UNREGISTERED_OR_PROTECTED_SOURCE")
def _base(seed):
    return (174000+seed-176000) if seed in TRANSFER else seed
def _rng(seed):
    base=_base(seed)
    mode="KNOWN" if base in KNOWN else "UNFAMILIAR"
    return random.Random(int.from_bytes(
        sha256(("WSP134|"+mode+"|"+str(base)).encode()).digest(),"big"))
def _op(kind,a,b):
    if kind=="AND": return a&b
    if kind=="OR": return a|b
    if kind=="XOR": return a^b
    if kind=="XNOR": return 1^(a^b)
    raise ValueError("BAD_SOURCE_OPERATOR")
@lru_cache(maxsize=96)
def _truth(seed):
    _check(seed)
    base=_base(seed)
    rng=_rng(base)
    p=list(range(6));rng.shuffle(p)
    first,second=rng.choice(OPS),rng.choice(OPS)
    third=rng.choice(OPS) if base in KNOWN else None
    out=[]
    for x in range(64):
        b=[(x>>i)&1 for i in range(6)]
        a=_op(first,b[p[0]],b[p[1]])
        c=_op(second,b[p[2]],b[p[3]])
        if base in KNOWN:
            z=_op(third,a,c)
            z^=(b[p[4]]&b[p[5]]) if (base%2==0) else b[p[4]]
        else:
            z=((a&c)|(a&b[p[4]])|(c&b[p[4]]))^b[p[5]]
        out.append(z)
    return tuple(out)

@dataclass(frozen=True)
class View:
    law_id:int
    records:tuple
    legal:frozenset
    cohort:str
    by_x:dict
    by_subject:dict
    def subject(self,x):
        if type(x) is not int or x not in self.by_x:
            raise ValueError("WSP134_INVALID_TYPED_ACTION")
        return self.by_x[x]
    def input(self,subject):
        if type(subject) is not int or subject not in self.by_subject:
            raise ValueError("WSP134_UNRECOGNIZED_OPAQUE_ACTION")
        return self.by_subject[subject]
    def fingerprint(self):
        return digest([self.law_id,self.records,self.cohort])

@lru_cache(maxsize=112)
def world(seed):
    _check(seed) # BEFORE any RNG
    base=_base(seed)
    law_id=int.from_bytes(sha256(("WSP134|LAW|"+str(base)).encode()).digest()[:8],"big")
    rng=random.Random(seed)
    subjects=rng.sample(range(seed*1000,seed*1000+1000),64)
    rows=[(subjects[x],x) for x in range(64)]
    rng.shuffle(rows)
    probe=seed not in TRANSFER
    return View(law_id,tuple(rows),
                frozenset(s for s,x in rows) if probe else frozenset(),
                "probe" if probe else "transfer",
                {x:s for s,x in rows},{s:x for s,x in rows})

def open_original(seed):
    raise PermissionError("WSP134_ORIGINAL_SCIENCE_FIRST_USE_DENIED")

@dataclass(frozen=True)
class Evidence:
    law_id:int
    subject:int
    input:int
    effect:int
    receipt:str

class Custodian:
    def __init__(self,view,seed):
        _check(seed)
        if type(view) is not View or view is not world(seed):
            raise PermissionError("WSP134_SOURCE_CUSTODY_MISMATCH")
        self.view=view
        self.truth=_truth(seed)
        self.budget=0 if view.cohort=="transfer" else 32
        self.seen=set()
        self.receipt=digest([view.fingerprint(),"begin"])
        self.events=[]
        self.scored=False
    def query(self,subject):
        if (self.scored or self.budget==0 or len(self.events)>=self.budget
            or type(subject) is not int or subject not in self.view.legal
            or subject in self.seen):
            raise PermissionError("WSP134_DUPLICATE_OR_OVERBUDGET_EFFECT")
        x=self.view.input(subject)
        effect=self.truth[x]
        row=[self.view.law_id,subject,x,effect]
        self.receipt=digest([self.receipt,row])
        self.seen.add(subject)
        self.events.append(row)
        return Evidence(*row,self.receipt)
    def held(self):
        return tuple((s,x) for s,x in self.view.records if s not in self.seen)
    def score_once(self,outputs):
        if self.scored or len(self.events)!=self.budget:
            raise PermissionError("WSP134_EARLY_OR_REPEAT_SCORE")
        held=self.held()
        if (type(outputs) is not dict or set(outputs)!={s for s,x in held}):
            raise ValueError("WSP134_MISSING_OR_EXTRA_HELD_OUTPUT")
        correct=wrong=abstained=0
        for subject,x in held:
            y=outputs[subject]
            if y is None: abstained+=1
            elif type(y) is not int or y not in (0,1):
                raise ValueError("WSP134_INVALID_OUTCOME_TYPE")
            elif y==self.truth[x]: correct+=1
            else: wrong+=1
        self.scored=True
        return {"correct":correct,"wrong_confident":wrong,"abstained":abstained,
                "held":len(held),"source_calls":self.budget}
