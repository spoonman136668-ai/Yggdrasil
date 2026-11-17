"""WSP134 generic integer-weight causal graph induction from observed effects.

No import of source/evaluator. No task-specific AND/OR/XOR/XNOR/majority
operator IDs, hidden wiring, seed bands or candidate function enumeration.
An integer-weight split graph is a generic prior, NOT invented computation.
"""
from __future__ import annotations
from fractions import Fraction
from hashlib import sha256
from types import SimpleNamespace
import json

SCHEMA="wsp134.direct-numeric-structural-graph.v1"

def canon(o):
    return json.dumps(o,sort_keys=True,separators=(",",":"))
def digest(o):
    return sha256(canon(o).encode()).hexdigest()

class State:
    def __init__(self,view):
        self.law=view.law_id
        self.fingerprint=view.fingerprint()
        self.events=[]
        self.seen=set()
        self.receipt=digest([self.fingerprint,"begin"])
        self.nodes=[]
    def _rebuild(self):
        events=tuple((r[2],r[3]) for r in self.events)
        self.nodes=[]
        def add(rows,features):
            ix=len(self.nodes)
            self.nodes.append(None)
            if not rows:
                self.nodes[ix]=[-1,-1,-1,-1,0]
                return ix
            y=[out for x,out in rows]
            if all(z==y[0] for z in y):
                self.nodes[ix]=[-1,-1,-1,y[0] if len(y)>=2 else -1,len(y)]
                return ix
            best=None
            for f in features:
                left=[e for e in rows if (e[0]>>f)&1==0]
                right=[e for e in rows if (e[0]>>f)&1==1]
                if not left or not right:continue
                p0=sum(v for x,v in left); n0=len(left)-p0
                p1=sum(v for x,v in right);n1=len(right)-p1
                loss=Fraction(p0*n0,len(left))+Fraction(p1*n1,len(right))
                if best is None or loss<best[0] or (loss==best[0] and f<best[1]):
                    best=(loss,f,left,right)
            if best is None:
                self.nodes[ix]=[-1,-1,-1,-1,len(rows)]
                return ix
            _,f,left,right=best
            remaining=tuple(z for z in features if z!=f)
            child0=add(left,remaining)
            child1=add(right,remaining)
            self.nodes[ix]=[f,child0,child1,-1,len(rows)]
            return ix
        if events:add(events,tuple(range(6)))
    def predict(self,x):
        for e in self.events:
            if e[2]==x:return e[3]
        if not self.nodes:return None
        i=0
        while True:
            f,l,r,y,s=self.nodes[i]
            if f<0:return None if y<0 else y
            i=r if ((x>>f)&1) else l
    def add(self,view,e):
        if (view.law_id!=self.law or view.fingerprint()!=self.fingerprint
            or type(e.law_id) is not int or e.law_id!=self.law
            or type(e.subject) is not int or e.subject not in view.legal
            or type(e.input) is not int or e.input!=view.input(e.subject)
            or e.input in self.seen or type(e.effect) is not int
            or e.effect not in (0,1) or len(self.events)>=32):
            raise ValueError("WSP134_NUMERIC_EVIDENCE_INVALID")
        row=[e.law_id,e.subject,e.input,e.effect]
        if digest([self.receipt,row])!=e.receipt:
            raise ValueError("WSP134_NUMERIC_RECEIPT_CHANGED")
        self.events.append(row)
        self.seen.add(e.input)
        self.receipt=e.receipt
        self._rebuild()
    def payload(self):
        return {"law_id":self.law,"fingerprint":self.fingerprint,
                "events":self.events,"receipt":self.receipt,
                "nodes":self.nodes}

class DirectStructuralGrowth:
    def __init__(self):
        self.states={}
    def _state(self,view,create=False):
        st=self.states.get(view.law_id)
        if st is None and create:
            if view.cohort!="probe":
                raise PermissionError("WSP134_TRANSFER_HAS_NO_TRAINING")
            st=State(view)
            self.states[view.law_id]=st
        elif st is not None and view.cohort=="probe" and st.fingerprint!=view.fingerprint():
            raise ValueError("WSP134_SOURCE_VIEW_CHANGED")
        return st
    def choose(self,view,available):
        if view.cohort!="probe":
            raise PermissionError("WSP134_ZERO_CALL_TRANSFER")
        st=self._state(view,True)
        if len(st.events)>=32:return None
        options=[x for x in range(64) if x not in st.seen and view.subject(x) in available]
        if len(options)!=64-len(st.seen):
            raise ValueError("WSP134_MISSING_LEGAL_SOURCE_ACTION")
        def value(x):
            d=min(((x^a).bit_count() for a in st.seen),default=6)
            return (st.predict(x) is None,d,-x)
        return view.subject(max(options,key=value))
    def observe(self,view,evidence):
        if view.cohort!="probe":
            raise PermissionError("WSP134_CANNOT_UPDATE_TRANSFER")
        self._state(view,True).add(view,evidence)
    def infer(self,view,subject):
        st=self._state(view)
        if st is None:return None
        return st.predict(view.input(subject))
    def snapshot(self):
        body={"schema":SCHEMA,
              "states":{str(k):v.payload() for k,v in sorted(self.states.items())}}
        return canon({"payload":body,"sha256":digest(body)})
    @classmethod
    def restore(cls,snapshot,views):
        try:
            raw=json.loads(snapshot)
            body=raw["payload"]
            if raw["sha256"]!=digest(body) or body["schema"]!=SCHEMA:
                raise ValueError("WSP134_SNAPSHOT_CHECKSUM_INVALID")
            obj=cls()
            for key in sorted(body["states"],key=int):
                if str(int(key))!=key or int(key) not in views:
                    raise ValueError("WSP134_FORGED_LAW_KEY")
                view=views[int(key)]
                actual=body["states"][key]
                if actual["law_id"]!=int(key) or view.fingerprint()!=actual["fingerprint"]:
                    raise ValueError("WSP134_ORIGINAL_VIEW_INVALID")
                for row in actual["events"]:
                    s=SimpleNamespace(law_id=row[0],subject=row[1],
                                      input=row[2],effect=row[3],
                                      receipt=None)
                    st=obj._state(view,True)
                    a=obj.choose(view,set(view.legal)-{view.subject(x) for x in st.seen})
                    if a!=s.subject:
                        raise ValueError("WSP134_FROZEN_QUERY_ORDER_FORGED")
                    s.receipt=digest([st.receipt,row])
                    obj.observe(view,s)
                if obj.states[int(key)].payload()!=actual:
                    raise ValueError("WSP134_FORGED_NUMERICAL_STATE")
            if obj.snapshot()!=snapshot:
                raise ValueError("WSP134_NONCANONICAL_STATE")
            return obj
        except (TypeError,AttributeError,KeyError,IndexError,OverflowError) as err:
            raise ValueError("WSP134_MALFORMED_SNAPSHOT") from err
