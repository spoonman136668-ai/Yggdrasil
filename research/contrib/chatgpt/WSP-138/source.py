"""WSP-138 independent prospective synthetic-source custodian only. Never import in learners."""
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
import json, random

KNOWN=frozenset(range(202000,202012))
UNFAMILIAR=frozenset(range(203000,203012))
TRANSFER=frozenset(range(204000,204006))
OFF=frozenset(range(205000,205008))
ALLOWED=KNOWN|UNFAMILIAR|TRANSFER|OFF
PROTECTED=frozenset().union(*(frozenset(range(k,k+64)) for k in (202800,203800,204800,205800)))
OPS=("AND","OR","XOR","XNOR")

def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':'))
def digest(v):return sha256(canon(v).encode()).hexdigest()
def _guard(seed):
    if type(seed) is not int or seed not in ALLOWED or seed in PROTECTED:
        raise PermissionError("WSP138_SOURCE_FIRST_USE_OR_UNREGISTERED_DENIED")
def _base(seed): return 202000+seed-204000 if seed in TRANSFER else seed
def _kind(seed):
    if seed in KNOWN:return 'KNOWN'
    if seed in UNFAMILIAR:return 'UNFAMILIAR'
    if seed in OFF:return 'OFF'
    raise PermissionError('WSP138_BAD_KIND')
def _rng(kind,seed):
    return random.Random(int.from_bytes(sha256(('WSP138|'+kind+'|'+str(seed)).encode()).digest(),'big'))
def _gate(op,a,b):
    if op=='AND':return a&b
    if op=='OR':return a|b
    if op=='XOR':return a^b
    if op=='XNOR':return 1^(a^b)
    raise AssertionError('BAD_OP')
@lru_cache(maxsize=32)
def _truth(seed):
    _guard(seed)
    base=_base(seed)
    kind=_kind(base)
    rng=_rng(kind,base)
    p=list(range(6));rng.shuffle(p)
    g1,g2=rng.choice(OPS),rng.choice(OPS)
    final=rng.choice(OPS) if kind=='KNOWN' else None
    out=[]
    for x in range(64):
        b=tuple((x>>i)&1 for i in range(6))
        if kind=='OFF':
            v=(b[p[0]]&b[p[2]])^(b[p[1]]&b[p[3]])^(b[p[0]]&b[p[4]])^(b[p[1]]&b[p[5]])^b[p[4]]^b[p[5]]
        else:
            a=_gate(g1,b[p[0]],b[p[1]])
            c=_gate(g2,b[p[2]],b[p[3]])
            if kind=='KNOWN': v=_gate(final,a,c)^((b[p[4]]&b[p[5]]) if base%2==0 else b[p[4]])
            else: v=((a&c)|(a&b[p[4]])|(c&b[p[4]]))^b[p[5]]
        out.append(v)
    return tuple(out)

@dataclass(frozen=True)
class View:
    law_id:int
    cohort:str
    records:tuple
    legal:frozenset
    by_x:dict
    by_subject:dict
    def subject(self,x):
        if type(x) is not int or x not in self.by_x:raise ValueError('BAD_TYPED_ACTION')
        return self.by_x[x]
    def input(self,subject):
        if type(subject) is not int or subject not in self.by_subject:raise ValueError('BAD_ACTION')
        return self.by_subject[subject]
    def fingerprint(self): return digest([self.law_id,self.cohort,self.records])
@lru_cache(maxsize=40)
def world(seed):
    _guard(seed)
    base=_base(seed)
    law=int.from_bytes(sha256(('WSP138|LAW|'+str(base)).encode()).digest()[:8],'big')
    rr=random.Random(seed)
    ids=rr.sample(range(seed*1000,seed*1000+1000),64)
    records=[(ids[x],x) for x in range(64)]
    rr.shuffle(records)
    cohort='transfer' if seed in TRANSFER else 'probe'
    return View(law,cohort,tuple(records),frozenset(ids) if cohort=='probe' else frozenset(),{x:s for s,x in records},{s:x for s,x in records})
@dataclass(frozen=True)
class Evidence:
    law_id:int
    subject:int
    input:int
    effect:int
    receipt:str
class Custodian:
    def __init__(self,view,seed):
        _guard(seed)
        if type(view) is not View or view is not world(seed):raise PermissionError('SOURCE_VIEW_MISMATCH')
        self.view=view
        self.truth=_truth(seed)
        self.budget=0 if view.cohort=='transfer' else 32
        self.receipt=digest([view.fingerprint(),'begin'])
        self.events=[]
        self.seen=set()
        self.scored=False
    def query(self,subject):
        if (self.scored or len(self.events)>=self.budget or type(subject) is not int
            or subject not in self.view.legal or subject in self.seen):
            raise PermissionError('WSP138_UNAUTHORIZED_EFFECT')
        x=self.view.input(subject)
        row=[self.view.law_id,subject,x,self.truth[x]]
        self.receipt=digest([self.receipt,row])
        self.seen.add(subject)
        self.events.append(row)
        return Evidence(*row,self.receipt)
    def held(self):return tuple((s,x) for s,x in self.view.records if s not in self.seen)
    def score_once(self,pred):
        if self.scored or len(self.events)!=self.budget or set(pred)!={s for s,x in self.held()}:
            raise PermissionError('WSP138_SCORE_REPLAY_BUDGET_OR_MISSING')
        correct=wrong=abstained=0
        for s,x in self.held():
            y=pred[s]
            if y is None:abstained+=1
            elif type(y) is not int or y not in (0,1):raise ValueError('BAD_PRED')
            elif y==self.truth[x]:correct+=1
            else:wrong+=1
        self.scored=True
        return {'correct':correct,'wrong_confident':wrong,'abstained':abstained,'held':len(pred),'source_calls':self.budget}

def open_original(seed):raise PermissionError('WSP138_ORIGINAL_SCIENCE_FIRST_USE_DENIED')
