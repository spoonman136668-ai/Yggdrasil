"""WSP134 independent symbolic and fully-fitted conventional controls.

Intentionally imports neither direct numerical graph nor source generator.
"""
from __future__ import annotations
from fractions import Fraction
from hashlib import sha256
import json

def digest(o):
    return sha256(json.dumps(o,sort_keys=True,separators=(",",":")).encode()).hexdigest()

class IndependentSymbolicTree:
    def __init__(self):
        self.states={}
    def _state(self,view,create=False):
        r=self.states.get(view.law_id)
        if r is None and create:
            r={"fingerprint":view.fingerprint(),"seen":{},"receipt":digest([view.fingerprint(),"begin"]),"graph":None}
            self.states[view.law_id]=r
        elif r is not None and view.cohort=="probe" and r["fingerprint"]!=view.fingerprint():
            raise ValueError("WSP134_SYMBOLIC_CHANGED_PUBLIC_VIEW")
        return r
    def _tree(self,pairs,remaining):
        if not pairs:return ("unknown",)
        outputs=[v for x,v in pairs]
        if min(outputs)==max(outputs):
            return ("leaf",outputs[0] if len(outputs)>=2 else None)
        choices=[]
        for f in remaining:
            groups=tuple(tuple((x,y) for x,y in pairs if ((x>>f)&1)==v) for v in (0,1))
            if not groups[0] or not groups[1]:continue
            penalty=sum((Fraction(sum(y for x,y in grp)*(len(grp)-sum(y for x,y in grp)),len(grp)) for grp in groups),Fraction())
            choices.append((penalty,f,groups))
        if not choices:return ("unknown",)
        penalty,f,groups=min(choices,key=lambda e:(e[0],e[1]))
        smaller=tuple(v for v in remaining if v!=f)
        return ("split",f,self._tree(groups[0],smaller),self._tree(groups[1],smaller))
    def observe(self,view,e):
        if view.cohort!="probe":
            raise PermissionError("WSP134_SYMBOLIC_TRANSFER_UPDATE")
        st=self._state(view,True)
        if (e.law_id!=view.law_id or type(e.input) is not int or
            e.input!=view.input(e.subject) or e.input in st["seen"] or
            type(e.effect) is not int or e.effect not in (0,1)
            or len(st["seen"])>=32):
            raise ValueError("WSP134_SYMBOLIC_INVALID_OBSERVATION")
        row=[e.law_id,e.subject,e.input,e.effect]
        if digest([st["receipt"],row])!=e.receipt:
            raise ValueError("WSP134_SYMBOLIC_BAD_EVIDENCE_RECEIPT")
        st["receipt"]=e.receipt
        st["seen"][e.input]=e.effect
        st["graph"]=self._tree(tuple(sorted(st["seen"].items())),tuple(range(6)))
    def infer(self,view,subject):
        st=self._state(view)
        if st is None:return None
        x=view.input(subject)
        if x in st["seen"]:return st["seen"][x]
        graph=st["graph"]
        while graph and graph[0]=="split":
            graph=graph[2+((x>>graph[1])&1)]
        return None if not graph or graph[0]=="unknown" else graph[1]
    def choose(self,view,available):
        if view.cohort!="probe":raise PermissionError("WSP134_SYMBOLIC_TRANSFER_ACTION")
        st=self._state(view,True)
        if len(st["seen"])==32:return None
        options=[x for x in range(64) if x not in st["seen"] and view.subject(x) in available]
        if len(options)!=64-len(st["seen"]):raise ValueError("WSP134_SYMBOLIC_SOURCE_ACTION_DRIFT")
        priorities=[]
        for x in options:
            unseen=self.infer(view,view.subject(x)) is None
            far=min((((x^a).bit_count()) for a in st["seen"]),default=6)
            priorities.append((unseen,far,-x,x))
        return view.subject(max(priorities)[-1])

class FullyFitCART:
    """Conventional greedily fitted depth-six binary tree; no abstention escape."""
    def __init__(self):
        self.samples={}
        self.trees={}
    def observe(self,view,e):
        if view.cohort!="probe" or e.law_id!=view.law_id or e.input!=view.input(e.subject):
            raise ValueError("WSP134_CART_BAD_SOURCE")
        d=self.samples.setdefault(view.law_id,{})
        if len(d)>=32 or e.input in d:raise ValueError("WSP134_CART_DUPLICATE")
        d[e.input]=e.effect
    def _fit(self,rows,remaining):
        pos=sum(y for x,y in rows)
        n=len(rows)
        winner=int(2*pos>n)
        if pos==0 or pos==n or not remaining:return ("leaf",winner)
        parent=Fraction(pos*(n-pos),n)
        eligible=[]
        for f in remaining:
            a=[r for r in rows if not ((r[0]>>f)&1)]
            b=[r for r in rows if ((r[0]>>f)&1)]
            if not a or not b:continue
            ap=sum(y for x,y in a);bp=sum(y for x,y in b)
            cost=Fraction(ap*(len(a)-ap),len(a))+Fraction(bp*(len(b)-bp),len(b))
            if cost<parent:eligible.append((cost,f,a,b))
        if not eligible:return ("leaf",winner)
        _,f,a,b=min(eligible,key=lambda r:(r[0],r[1]))
        rem=tuple(j for j in remaining if j!=f)
        return ("split",f,self._fit(a,rem),self._fit(b,rem))
    def fit(self,view):
        rows=tuple(sorted(self.samples[view.law_id].items()))
        if len(rows)!=32:raise ValueError("WSP134_CART_UNDERTRAINED")
        self.trees[view.law_id]=self._fit(rows,tuple(range(6)))
    def infer(self,view,subject):
        t=self.trees.get(view.law_id)
        if t is None:return None
        x=view.input(subject)
        while t[0]=="split":
            t=t[2+((x>>t[1])&1)]
        return t[1]
    def training_errors(self,view):
        samples=self.samples[view.law_id]
        return sum(self.infer(view,view.subject(x))!=y for x,y in samples.items())

class NoUpdate:
    def infer(self,view,subject):return None
