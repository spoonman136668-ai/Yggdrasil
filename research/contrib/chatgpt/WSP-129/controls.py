"""WSP129 independent exact symbolic grammar comparator and converged
convex ridge benchmark, with no imports from source or numeric learner.
"""
from __future__ import annotations

def _parity(a,mask):
    return bin(a&mask).count("1")%2

def _effect(a,b,mode,left,right,flip):
    x=_parity(a,left); y=_parity(b,right)
    if mode=="XOR":
        v=(x+y)%2
    elif mode=="AND":
        v=x*y
    elif mode=="OR":
        v=int(bool(x or y))
    else:
        raise ValueError("WSP129_SYMBOLIC_UNRECOGNIZED_OP")
    return v^flip

def _all_hypotheses():
    return [(mode,l,r,c) for mode in ("XOR","AND","OR")
            for l in range(1,16) for r in range(1,16)
            for c in range(2)]

class _State:
    def __init__(self,view):
        self.view=view
        self.events={}
        self.candidates=_all_hypotheses()

class OptimizedSymbolic:
    def __init__(self):
        self.states={}

    def _state(self,view,create=False):
        if (getattr(view,"cohort",None) not in ("probe","transfer") or
                type(getattr(view,"law_id",None)) is not int or
                not 0<=view.law_id<128):
            raise ValueError("WSP129_CONTROL_VIEW_INVALID")
        if view.law_id not in self.states and create:
            self.states[view.law_id]=_State(view)
        return self.states.get(view.law_id)

    def observe(self,view,evidence):
        if (view.cohort!="probe" or
                getattr(evidence,"seed",None)!=view.seed or
                getattr(evidence,"law_id",None)!=view.law_id or
                getattr(evidence,"subject",None) not in view.legal or
                view.pair(evidence.subject)!=
                (getattr(evidence,"left",None),getattr(evidence,"right",None)) or
                type(getattr(evidence,"effect",None)) is not int or
                evidence.effect not in (0,1)):
            raise ValueError("WSP129_CONTROL_SOURCE_INVALID")
        s=self._state(view,True)
        a,b=view.pair(evidence.subject)
        if (a,b) in s.events:
            raise ValueError("WSP129_CONTROL_DUPLICATE")
        s.events[a,b]=evidence.effect
        s.candidates=[model for model in s.candidates
                      if _effect(a,b,*model)==evidence.effect]

    def infer(self,view,subject):
        state=self._state(view)
        if state is None or not state.candidates:
            return None
        a,b=view.pair(subject)
        first=_effect(a,b,*state.candidates[0])
        if any(_effect(a,b,*c)!=first for c in state.candidates[1:]):
            return None
        return first

    def operator(self,view):
        st=self._state(view)
        if st is None or not st.candidates:
            return None
        modes={m[0] for m in st.candidates}
        return next(iter(modes)) if len(modes)==1 else None

    def exhausted(self,view):
        st=self._state(view)
        return st is None or not st.candidates

def _features(a,b):
    la=[(a>>i)&1 for i in range(4)]
    rb=[(b>>i)&1 for i in range(4)]
    return [1.0]+[float(v) for v in la+rb]+[
        float(la[i]*rb[j]) for i in range(4) for j in range(4)]

def _ridge_solution(samples):
    # Exact deterministic global convex optimum for quadratic ridge loss,
    # not an SGD/MLP model. 25 parametrized features.
    n=25
    coeff=[[0.0]*(n+1) for _ in range(n)]
    for (a,b),bit in samples:
        x=_features(a,b)
        y=2.0*bit-1.0
        for i in range(n):
            coeff[i][n]+=x[i]*y
            for j in range(n):
                coeff[i][j]+=x[i]*x[j]
    for i in range(n):
        coeff[i][i]+=0.01
    for j in range(n):
        k=max(range(j,n),key=lambda row:abs(coeff[row][j]))
        coeff[j],coeff[k]=coeff[k],coeff[j]
        pivot=coeff[j][j]
        if abs(pivot)<1e-13:
            raise ArithmeticError("WSP129_RIDGE_SINGULAR_PIVOT")
        for col in range(j,n+1):
            coeff[j][col]/=pivot
        for row in range(j+1,n):
            factor=coeff[row][j]
            if factor:
                for col in range(j,n+1):
                    coeff[row][col]-=factor*coeff[j][col]
    result=[0.0]*n
    for row in reversed(range(n)):
        result[row]=coeff[row][n]-sum(
            coeff[row][col]*result[col] for col in range(row+1,n))
    return tuple(result)

class FullFitRidge:
    def __init__(self):
        self.states={}

    def observe(self,view,evidence):
        if (view.cohort!="probe" or
                getattr(evidence,"seed",None)!=view.seed or
                getattr(evidence,"law_id",None)!=view.law_id or
                getattr(evidence,"subject",None) not in view.legal or
                view.pair(evidence.subject)!=
                (getattr(evidence,"left",None),getattr(evidence,"right",None)) or
                type(getattr(evidence,"effect",None)) is not int or
                evidence.effect not in (0,1)):
            raise ValueError("WSP129_RIDGE_EVIDENCE_INVALID")
        state=self.states.setdefault(view.law_id,{"samples":{},"weights":None})
        pair=view.pair(evidence.subject)
        if pair in state["samples"]:
            raise ValueError("WSP129_RIDGE_DUPLICATE")
        state["samples"][pair]=evidence.effect
        state["weights"]=None

    def fit(self,view):
        state=self.states[view.law_id]
        if len(state["samples"])!=24:
            raise ValueError("WSP129_RIDGE_NOT_FULL_24")
        state["weights"]=_ridge_solution(sorted(state["samples"].items()))

    def raw(self,view,subject):
        state=self.states[view.law_id]
        if state["weights"] is None:
            raise ValueError("WSP129_RIDGE_NOT_TRAINED")
        a,b=view.pair(subject)
        return sum(v*x for v,x in zip(state["weights"],_features(a,b)))

    def infer(self,view,subject):
        return int(self.raw(view,subject)>=0)

    def training_correct(self,view):
        s=self.states[view.law_id]
        return sum(int(self.infer(view,view.subject(a,b))==y)
                   for (a,b),y in s["samples"].items())

class NoUpdate:
    def observe(self,view,evidence):
        return None

    def infer(self,view,subject):
        return None
