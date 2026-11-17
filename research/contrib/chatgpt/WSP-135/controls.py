"""Independently written symbolic factor inference and conventional fitted CART.

Neither imports the candidate or generator. The exact symbolic solver is
purposefully equally expressive; a tie defeats a unique-numeric-learning claim.
"""
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
import json

def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':'))
def digest(v):return sha256(canon(v).encode()).hexdigest()
def action_order():return tuple(sorted(range(64),key=lambda v:(sha256(('WSP135|ACTIONS|'+str(v)).encode()).digest(),v))[:32])

@lru_cache(maxsize=1)
def codebooks():
    books=[]
    for first in combinations(range(6),2):
        for second in combinations((k for k in range(6) if k not in first),2):
            if second<=first:continue
            left=[k for k in range(6) if k not in first and k not in second]
            for singles in (left,list(reversed(left))):
                for u in range(1,15):
                    for v in range(1,15):
                        table=[]
                        for bits in range(64):
                            f=(bits>>first[0]&1)*2+(bits>>first[1]&1)
                            g=(bits>>second[0]&1)*2+(bits>>second[1]&1)
                            output=8*(u>>f&1)+4*(v>>g&1)+2*(bits>>singles[0]&1)+(bits>>singles[1]&1)
                            table.append(output)
                        books.append(bytes(table))
    assert len(books)==17640
    return tuple(books)

class ExactSymbolicFactor:
    def __init__(self):self.events={}
    def observe(self,view,e):
        if view.cohort!='probe' or e.law_id!=view.law_id or e.input!=view.input(e.subject) or type(e.effect)!=int or e.effect not in (0,1):raise ValueError('SYMBOLIC_BAD_EVIDENCE')
        entry=self.events.setdefault(view.law_id,{'fingerprint':view.fingerprint(),'samples':[],'receipt':digest([view.fingerprint(),'begin']),'survivors':[]})
        if entry['fingerprint']!=view.fingerprint() or len(entry['samples'])>=32 or e.input!=action_order()[len(entry['samples'])]:raise ValueError('SYMBOLIC_DRIFT')
        row=[e.law_id,e.subject,e.input,e.effect]
        if digest([entry['receipt'],row])!=e.receipt:raise ValueError('SYMBOLIC_RECEIPT')
        entry['receipt']=e.receipt
        entry['samples'].append(row)
        if len(entry['samples'])==32:
            lowest=17
            for idx,book in enumerate(codebooks()):
                evidence={}
                for r in entry['samples']:
                    tag=book[r[2]]
                    if tag in evidence and evidence[tag]!=r[3]:break
                    evidence[tag]=r[3]
                else:
                    if len(evidence)<lowest:
                        lowest=len(evidence);entry['survivors']=[]
                    if len(evidence)==lowest and len(entry['survivors'])<64:
                        ledger=[evidence.get(i,-1) for i in range(16)]
                        entry['survivors'].append((idx,ledger))
    def infer(self,view,subject):
        st=self.events.get(view.law_id)
        if st is None or len(st['samples'])!=32:return None
        x=view.input(subject)
        selected=st['survivors']
        if not selected:return None
        total=0;zero=0;one=0
        for idx,lut in selected:
            value=lut[codebooks()[idx][x]]
            if value==0:zero+=1
            if value==1:one+=1
        total=zero+one
        if 5*total<4*len(selected) or 10*max(zero,one)<9*total:return None
        return int(one>=zero)

class FullyFitCART:
    def __init__(self):self.examples={};self.models={}
    def observe(self,view,e):
        if e.input!=view.input(e.subject) or e.law_id!=view.law_id or e.effect not in (0,1):raise ValueError('CART_INPUT')
        d=self.examples.setdefault(view.law_id,{})
        if e.input in d or len(d)>=32:raise ValueError('CART_BUDGET')
        d[e.input]=e.effect
    @staticmethod
    def _tree(rows,features):
        n=len(rows);pos=sum(y for x,y in rows)
        vote=int(2*pos>n)
        if pos==0 or pos==n or not features:return ('leaf',vote)
        best=None
        baseline=pos*(n-pos)/n
        for f in features:
            a=[(x,y) for x,y in rows if (x>>f)&1==0]
            b=[(x,y) for x,y in rows if (x>>f)&1==1]
            if not a or not b:continue
            ap=sum(y for x,y in a);bp=sum(y for x,y in b)
            loss=ap*(len(a)-ap)/len(a)+bp*(len(b)-bp)/len(b)
            if loss>=baseline-1e-10:continue
            if best is None or (loss,f)<(best[0],best[1]):best=(loss,f,a,b)
        if best is None:return ('leaf',vote)
        _,f,a,b=best
        other=tuple(k for k in features if k!=f)
        return ('split',f,FullyFitCART._tree(a,other),FullyFitCART._tree(b,other))
    def fit(self,view):
        rows=self.examples[view.law_id]
        if len(rows)!=32:raise ValueError('CART_NOT_FULLY_TRAINED')
        self.models[view.law_id]=self._tree(tuple(rows.items()),tuple(range(6)))
    def infer(self,view,subject):
        t=self.models.get(view.law_id)
        if t is None:return None
        x=view.input(subject)
        while t[0]=='split':t=t[2+((x>>t[1])&1)]
        return t[1]
    def training_errors(self,view):
        return sum(self.infer(view,view.subject(x))!=y for x,y in self.examples[view.law_id].items())
