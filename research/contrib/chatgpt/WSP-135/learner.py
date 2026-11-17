"""WSP-135: direct latent two-pair feature allocation from public consequences.

All 17,640 potential two-pair *feature layouts* are source independent.
Four-input outcome lookup tables are learned from effects, not enumerated as
pre-existing completed relationships. This is a supplied universal factor prior,
not the invention of new computational primitives or proven causal laws.
"""
from hashlib import sha256
from itertools import combinations
from functools import lru_cache
import json

SCHEMA='wsp135.latent-factor-inference.v1'
def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':'))
def digest(v):return sha256(canon(v).encode()).hexdigest()

def schedule():
    return tuple(sorted(range(64),key=lambda x:(sha256(('WSP135|ACTIONS|'+str(x)).encode()).digest(),x))[:32])

def _pairs():
    for a in combinations(range(6),2):
        remaining=tuple(x for x in range(6) if x not in a)
        for b in combinations(remaining,2):
            if a>=b:continue
            left=tuple(x for x in remaining if x not in b)
            for c,d in (left,left[::-1]):yield a,b,c,d

@lru_cache(maxsize=1)
def templates():
    result=[]
    for a,b,c,d in _pairs():
        for g in range(1,15):
            for h in range(1,15):
                codes=[]
                for x in range(64):
                    ai=((x>>a[0])&1)*2+((x>>a[1])&1)
                    bi=((x>>b[0])&1)*2+((x>>b[1])&1)
                    codes.append((((g>>ai)&1)<<3)|(((h>>bi)&1)<<2)|(((x>>c)&1)<<1)|((x>>d)&1))
                result.append(bytes(codes))
    if len(result)!=17640:raise AssertionError(('TEMPLATE_COUNT',len(result)))
    return tuple(result)

def fit(rows):
    if len(rows)!=32 or len({x for x,y in rows})!=32:raise ValueError('INCOMPLETE_TRAINING')
    best=None;chosen=[]
    for idx,codes in enumerate(templates()):
        lut=[-1]*16
        valid=True
        for x,y in rows:
            c=codes[x]
            z=lut[c]
            if z!=-1 and z!=y:
                valid=False;break
            lut[c]=y
        if not valid:continue
        count=sum(q!=-1 for q in lut)
        if best is None or count<best:
            best=count;chosen=[]
        if count==best and len(chosen)<64:
            chosen.append([idx,lut])
    return chosen

def predict(chosen,x):
    if not chosen:return None
    votes=[]
    lookup=templates()
    for index,lut in chosen:
        y=lut[lookup[index][x]]
        if y!=-1:votes.append(y)
    if len(votes)*5<len(chosen)*4:return None
    ones=sum(votes)
    if max(ones,len(votes)-ones)*10<len(votes)*9:return None
    return int(ones*2>=len(votes))

class LatentInducer:
    def __init__(self):self.states={}
    def observe(self,view,e):
        if view.cohort!='probe' or type(e.input) is not int or e.input!=view.input(e.subject) or type(e.effect) is not int or e.effect not in (0,1) or e.law_id!=view.law_id:
            raise ValueError('BAD_PUBLIC_EVIDENCE')
        st=self.states.setdefault(view.law_id,{'fingerprint':view.fingerprint(),'events':[],'receipt':digest([view.fingerprint(),'begin']),'chosen':[]})
        if st['fingerprint']!=view.fingerprint():raise ValueError('VIEW_DRIFT')
        if len(st['events'])>=32 or any(row[2]==e.input for row in st['events']):raise ValueError('DUPLICATE_OR_OVERBUDGET')
        if e.input!=schedule()[len(st['events'])]:raise ValueError('QUERY_ORDER_DRIFT')
        row=[e.law_id,e.subject,e.input,e.effect]
        if digest([st['receipt'],row])!=e.receipt:raise ValueError('BAD_RECEIPT')
        st['events'].append(row)
        st['receipt']=e.receipt
        if len(st['events'])==32:st['chosen']=fit(tuple((row[2],row[3]) for row in st['events']))
    def infer(self,view,subject):
        st=self.states.get(view.law_id)
        return None if not st or len(st['events'])!=32 else predict(st['chosen'],view.input(subject))
    def snapshot(self):
        body={'schema':SCHEMA,'states':{str(k):v for k,v in sorted(self.states.items())}}
        return canon({'payload':body,'sha256':digest(body)})
    @classmethod
    def restore(cls,snap,views):
        obj=json.loads(snap);body=obj['payload']
        if obj['sha256']!=digest(body) or body['schema']!=SCHEMA:raise ValueError('INVALID_SNAPSHOT')
        out=cls()
        for k in sorted(body['states'],key=int):
            if str(int(k))!=k or int(k) not in views:raise ValueError('FORGED_WORLD')
            view=views[int(k)]
            item=body['states'][k]
            if item['fingerprint']!=view.fingerprint():raise ValueError('BAD_FINGERPRINT')
            for row in item['events']:
                from types import SimpleNamespace
                st=out.states.get(view.law_id)
                start=digest([view.fingerprint(),'begin']) if st is None else st['receipt']
                e=SimpleNamespace(law_id=row[0],subject=row[1],input=row[2],effect=row[3],receipt=digest([start,row]))
                out.observe(view,e)
            if out.states[view.law_id]!=item:raise ValueError('FORGED_LEARNED_WEIGHTS')
        if out.snapshot()!=snap:raise ValueError('NONCANONICAL_SNAPSHOT')
        return out
