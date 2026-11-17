"""WSP135 source-only public synthetic intervention outcomes, not a learner import."""
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
import json
import random

KNOWN=frozenset(range(178000,178064))
UNFAMILIAR=frozenset(range(179000,179032))
ALLOWED=KNOWN|UNFAMILIAR
PROTECTED=frozenset(range(178800,178864))|frozenset(range(179800,179832))|frozenset(range(180000,180064))
OPS=("AND","OR","XOR","XNOR")

def canonical(v):return json.dumps(v,sort_keys=True,separators=(",",":"))
def digest(v):return sha256(canonical(v).encode()).hexdigest()
def validate(seed):
    if type(seed) is not int or seed not in ALLOWED or seed in PROTECTED:
        raise PermissionError("WSP135_PROTECTED_OR_UNREGISTERED_SOURCE")
def gate(name,a,b):
    if name=="AND":return a&b
    if name=="OR":return a|b
    if name=="XOR":return a^b
    if name=="XNOR":return 1^(a^b)
    raise ValueError("WSP135_BAD_SOURCE_GATE")

@lru_cache(maxsize=96)
def _truth(seed):
    validate(seed)
    class_name="KNOWN" if seed in KNOWN else "UNFAMILIAR"
    rng=random.Random(int.from_bytes(
        sha256(("WSP135|"+class_name+"|"+str(seed)).encode()).digest(),"big"))
    p=list(range(6))
    rng.shuffle(p)
    a,b=rng.choice(OPS),rng.choice(OPS)
    c=rng.choice(OPS) if class_name=="KNOWN" else None
    values=[]
    for x in range(64):
        bits=[(x>>i)&1 for i in range(6)]
        u=gate(a,bits[p[0]],bits[p[1]])
        v=gate(b,bits[p[2]],bits[p[3]])
        if class_name=="KNOWN":
            z=gate(c,u,v)^((bits[p[4]]&bits[p[5]]) if seed%2==0 else bits[p[4]])
        else:
            z=((u&v)|(u&bits[p[4]])|(v&bits[p[4]]))^bits[p[5]]
        values.append(z)
    return tuple(values)

@dataclass(frozen=True)
class View:
    law_id:int
    cohort:str
    records:tuple
    legal:frozenset
    by_input:dict
    by_subject:dict
    def subject(self,x):
        if type(x) is not int or x not in self.by_input:raise ValueError("WSP135_BAD_ACTION")
        return self.by_input[x]
    def input(self,subject):
        if type(subject) is not int or subject not in self.by_subject:
            raise ValueError("WSP135_BAD_OPAQUE_ID")
        return self.by_subject[subject]
    def fingerprint(self):return digest([self.law_id,self.cohort,self.records])

@lru_cache(maxsize=96)
def world(seed):
    validate(seed)
    # All six-bit inputs are PUBLIC BEFORE CHOICE. Only effects are hidden.
    law_id=int.from_bytes(sha256(("WSP135|ID|"+str(seed)).encode()).digest()[:8],"big")
    rng=random.Random(seed)
    ids=rng.sample(range(seed*1000,seed*1000+1000),64)
    rows=tuple((ids[x],x) for x in range(64))
    cohort="known" if seed in KNOWN else "unfamiliar"
    return View(law_id,cohort,rows,frozenset(ids),
                {x:s for s,x in rows},{s:x for s,x in rows})

def open_original(seed):
    raise PermissionError("WSP135_SCIENCE_FIRST_USE_FORBIDDEN")

@dataclass(frozen=True)
class Evidence:
    law_id:int
    subject:int
    input:int
    effect:int
    receipt:str

class Custodian:
    def __init__(self,view,seed):
        validate(seed)
        if type(view) is not View or view is not world(seed):
            raise PermissionError("WSP135_SOURCE_CUSTODY_INVALID")
        self.view=view
        self.truth=_truth(seed)
        self.events=[]
        self.seen=set()
        self.scored=False
        self.receipt=digest([view.fingerprint(),"begin"])
    def query(self,subject):
        if (self.scored or len(self.events)>=32 or type(subject) is not int
                or subject not in self.view.legal or subject in self.seen):
            raise PermissionError("WSP135_DUPLICATE_OR_OVERBUDGET")
        x=self.view.input(subject)
        row=[self.view.law_id,subject,x,self.truth[x]]
        self.receipt=digest([self.receipt,row])
        self.seen.add(subject)
        self.events.append(row)
        return Evidence(*row,self.receipt)
    def held(self):
        return tuple((s,x) for s,x in self.view.records if s not in self.seen)
    def score_once(self,outputs):
        if self.scored or len(self.events)!=32:
            raise PermissionError("WSP135_PREMATURE_OR_REPEAT_SCORE")
        held=self.held()
        if type(outputs) is not dict or set(outputs)!={s for s,x in held}:
            raise ValueError("WSP135_WRONG_HELD_SET")
        correct=wrong=abstained=0
        for s,x in held:
            y=outputs[s]
            if y is None:abstained+=1
            elif type(y) is not int or y not in (0,1):
                raise ValueError("WSP135_BAD_PREDICTION")
            elif y==self.truth[x]:correct+=1
            else:wrong+=1
        self.scored=True
        return {"correct":correct,"wrong_confident":wrong,"abstained":abstained,
                "held":32,"source_calls":32}
