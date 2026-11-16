"""WSP133 independent exact-symbolic R2 challenger-intervention comparison.

An independently written list-of-symbolic-expressions version of the same
preregistered 16 pure +16 active alternative intervention search. No imports
from WSP133 numeric learner, WSP133 source, or hidden evaluation labels.
"""
from __future__ import annotations
from itertools import permutations
from hashlib import sha256
import json

def _map_roles(value,roles):
    high=value&192
    for old_bit,new_bit in enumerate(roles):
        high|=(bool(value&(1<<old_bit)))<<new_bit
    return high
def _shear_input(z,write_bit,read_bit):
    return z^((bool(z&(1<<read_bit)))<<write_bit)
def _cjson(x):return json.dumps(x,sort_keys=True,separators=(",",":"))
def _sha(x):return sha256(_cjson(x).encode()).hexdigest()

class _OldView:
    cohort="transfer"
    def __init__(self,law_id):self.law_id=law_id
    def input(self,x):return x

class _SymbolicWorld:
    def __init__(self,view,warm_truth):
        self.view=view
        self.truth=tuple(warm_truth)
        if len(self.truth)!=256 or any(y not in (0,1) for y in self.truth):
            raise ValueError("WSP133_INDEPENDENT_PRIOR_NOT_QUALIFIED")
        self.permutations=tuple(permutations(range(6)))
        self.shears=tuple((a,b) for a in range(6)
                         for b in range(6) if a!=b)
        self.events={}
        self.receipt=_sha([view.fingerprint(),"begin"])
        self.pure=list(range(720))
        self.alternatives=None
    def projected(self,x,candidate):
        p,shift=candidate
        z=_map_roles(x,self.permutations[p])
        if shift is not None:
            i,j=self.shears[shift]
            z=_shear_input(z,i,j)
        return self.truth[z]
    def _choices(self):
        return ([(i,None) for i in self.pure] if self.alternatives is None
                else self.alternatives)
    def choose_x(self):
        if len(self.events)>=32:return None
        rem=self._choices()
        if len(rem)<2:
            return next(x for x in range(256) if x not in self.events)
        best=None;best_score=-1
        for x in range(256):
            if x in self.events:continue
            n1=sum(self.projected(x,c) for c in rem)
            score=min(n1,len(rem)-n1)
            if score>best_score:
                best_score=score;best=x
        return best
    def observe(self,event):
        if (self.view.subject(event.input)!=event.subject or
                event.seed!=self.view.seed or event.law_id!=self.view.law_id or
                type(event.effect) is not int or event.effect not in (0,1) or
                event.input in self.events or len(self.events)>=32):
            raise ValueError("WSP133_EXACT_SYMBOLIC_BAD_EVIDENCE")
        expected=self.choose_x()
        if expected!=event.input:
            raise ValueError("WSP133_EXACT_SYMBOLIC_ACTION_NONPARITY")
        body=[event.seed,event.law_id,event.subject,event.input,event.effect]
        if event.receipt!=_sha([self.receipt,body]):
            raise ValueError("WSP133_EXACT_SYMBOLIC_SOURCE_RECEIPT_INVALID")
        self.receipt=event.receipt
        self.events[event.input]=event.effect
        n=len(self.events)
        if n<16:
            self.pure=[i for i in self.pure
                       if self.projected(event.input,(i,None))==event.effect]
        elif n==16:
            self.pure=[i for i in self.pure
                       if self.projected(event.input,(i,None))==event.effect]
            alternatives=[]
            for index in range(720):
                for option in (None,*range(30)):
                    hypothesis=(index,option)
                    if all(self.projected(x,hypothesis)==y
                           for x,y in self.events.items()):
                        alternatives.append(hypothesis)
            self.alternatives=alternatives
        else:
            self.alternatives=[
                h for h in self.alternatives
                if self.projected(event.input,h)==event.effect]
    def infer(self,x):
        if self.alternatives is None or not self.alternatives:
            return None
        result=self.projected(x,self.alternatives[0])
        for hyp in self.alternatives[1:]:
            if self.projected(x,hyp)!=result:
                return None
        return result
    def count(self):
        return len(self.alternatives) if self.alternatives is not None else len(self.pure)

class IndependentAuditedSymbolic:
    def __init__(self,strong_warm_prior):
        self.warm_prior=strong_warm_prior
        self.base={}
        self.states={}
        self.first_by_law={}
    def _old(self,law):
        if law not in self.base:
            v=_OldView(law)
            self.base[law]=tuple(self.warm_prior.infer(v,x) for x in range(256))
        return self.base[law]
    def _state(self,view,create=False):
        if view.cohort=="transfer":return self.first_by_law.get(view.law_id)
        state=self.states.get(view.seed)
        if state is None and create:
            state=_SymbolicWorld(view,self._old(view.law_id))
            self.states[view.seed]=state
            self.first_by_law.setdefault(view.law_id,state)
        elif state is not None and state.view is not view and state.view.fingerprint()!=view.fingerprint():
            raise ValueError("WSP133_INDEPENDENT_CHANGED_SOURCE_VIEW")
        return state
    def choose(self,view,available):
        if view.cohort!="probe":
            raise PermissionError("WSP133_INDEPENDENT_TRANSFER_SOURCE_DENIED")
        state=self._state(view,True)
        x=state.choose_x()
        if x is None:return None
        subject=view.subject(x)
        if subject not in available:
            raise ValueError("WSP133_INDEPENDENT_DUPLICATE_ACTION")
        return subject
    def observe(self,view,event):
        if (view.cohort!="probe" or
                event.subject not in view.legal or
                view.input(event.subject)!=event.input):
            raise ValueError("WSP133_INDEPENDENT_UNAUTHORIZED_SOURCE")
        self._state(view,True).observe(event)
    def infer(self,view,subject):
        state=self._state(view)
        return None if state is None else state.infer(view.input(subject))
    def count(self,view):
        state=self._state(view)
        return None if state is None else state.count()
