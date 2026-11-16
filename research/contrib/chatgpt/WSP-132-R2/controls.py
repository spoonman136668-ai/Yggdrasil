"""Independent exhaustive semantic-challenger symbolic control for WSP132-R2.

The 22,320 hypotheses are evaluated as explicit (permutation,shear) tuples;
the numeric experiment independently writes packed bit weights and never
imports this symbolic solver. Supports matching feedback, zero-data views,
and a frozen source-blind static information-probe schedule.
"""
from __future__ import annotations
from itertools import permutations

PERMS=tuple(permutations(range(6)))
PAIRS=tuple((i,j) for i in range(6) for j in range(6) if i!=j)

class _Old:
    cohort="transfer"
    def __init__(self,law):self.law_id=law
    def input(self,x):return x

class _Models:
    def __init__(self,warm,law):
        view=_Old(law)
        self.base=tuple(warm.infer(view,x) for x in range(256))
        if any(x not in (0,1) for x in self.base):
            raise ValueError("WSP132R2_SYMBOLIC_WARM_INCOMPLETE")
        self.transforms=tuple((p,a,b)
            for p in PERMS for a,b in ((-1,-1),*PAIRS))
        if len(self.transforms)!=22320:
            raise AssertionError("WSP132R2_SYMBOLIC_CAPACITY_DRIFT")
        self.mapped=tuple(bytes(self._value(x,t) for x in range(256))
                          for t in self.transforms)
    def _value(self,x,transform):
        perm,a,b=transform
        low=0
        for k,position in enumerate(perm):
            if (x>>k)&1:
                low|=1<<position
        if a>=0:
            low^=((low>>b)&1)<<a
        return self.base[(x&192)|low]

class _World:
    def __init__(self,view,bank):
        self.view=view
        self.bank=bank
        self.survivors=list(range(len(bank.transforms)))
        self.seen=set()
    def observe(self,x,bit):
        if x in self.seen:raise ValueError("WSP132R2_SYMBOLIC_DUPLICATE")
        self.seen.add(x)
        self.survivors=[k for k in self.survivors
                        if self.bank.mapped[k][x]==bit]
    def infer(self,x):
        survivors=self.survivors
        if not survivors:return None
        one=self.bank.mapped[survivors[0]][x]
        if any(self.bank.mapped[k][x]!=one for k in survivors[1:]):
            return None
        return one

class ExactChallengerSymbolic:
    def __init__(self,old):
        self.old=old
        self.banks={}
        self.worlds={}
        self.first_by_law={}
    def bank(self,law):
        if law not in self.banks:
            self.banks[law]=_Models(self.old,law)
        return self.banks[law]
    def state(self,view,create=False):
        if view.cohort=="transfer":
            return self.first_by_law.get(view.law_id)
        st=self.worlds.get(view.seed)
        if st is None and create:
            st=_World(view,self.bank(view.law_id))
            self.worlds[view.seed]=st
            self.first_by_law.setdefault(view.law_id,st)
        elif (st is not None and st.view is not view and
              st.view.fingerprint()!=view.fingerprint()):
            raise ValueError("WSP132R2_SYMBOLIC_SOURCE_VIEW_DRIFT")
        return st
    def observe(self,view,evidence):
        if (view.cohort!="probe" or evidence.seed!=view.seed or
            evidence.law_id!=view.law_id or
            evidence.subject not in view.legal or
            view.input(evidence.subject)!=evidence.input or
            type(evidence.effect) is not int or evidence.effect not in (0,1)):
            raise ValueError("WSP132R2_SYMBOLIC_SOURCE_INVALID")
        self.state(view,True).observe(evidence.input,evidence.effect)
    def infer(self,view,subject):
        st=self.state(view)
        return None if st is None else st.infer(view.input(subject))
    def remaining(self,view):
        st=self.state(view)
        return None if st is None else len(st.survivors)

class FixedChallengerSchedule:
    def __init__(self,reference):
        self.reference=reference
        self.plans={}
    def plan(self,view):
        law=view.law_id
        if law not in self.plans:
            bank=self.reference.bank(law)
            n=len(bank.transforms)
            # Static source-blind *marginal* balance. Does not use target
            # observations and is not falsely called optimal full partition.
            balance=[]
            for x in range(256):
                positive=sum(row[x] for row in bank.mapped)
                balance.append((min(positive,n-positive),x))
            balance.sort(key=lambda e:(-e[0],e[1]))
            self.plans[law]=tuple(x for b,x in balance[:32])
        return self.plans[law]
    def choose(self,view,used):
        return next((view.subject(x) for x in self.plan(view)
                     if x not in used),None)

class NoUpdate:
    def observe(self,view,e):return None
    def infer(self,view,subject):return None
