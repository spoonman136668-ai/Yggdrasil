"""WSP128 independently derived symbolic residual comparator and ablations.

No import from repair or source. A separate exact symbolic constraint
reconstruction guards against treating numeric coefficients as unique gains.
"""
from __future__ import annotations

class _Book:
    def __init__(self,view):
        self.view=view
        self.cells={}
        self.residual={}
        self.cache=None

class _EvidenceBook:
    def __init__(self,prior=None):
        self.prior=prior
        self.views={}

    def _state(self,view):
        if (getattr(view,"cohort",None)!="probe" or
                type(getattr(view,"law_id",None)) is not int or
                not 0<=view.law_id<64):
            raise PermissionError("WSP128_CONTROL_VIEW")
        if view.seed not in self.views:
            self.views[view.seed]=_Book(view)
        st=self.views[view.seed]
        if st.view is not view:
            raise ValueError("WSP128_CONTROL_VIEW_DRIFT")
        return st

    def observe(self,view,evidence):
        if (getattr(evidence,"seed",None)!=view.seed or
                getattr(evidence,"law_id",None)!=view.law_id or
                getattr(evidence,"subject",None) not in view.legal or
                view.pair(evidence.subject)!=
                    (getattr(evidence,"left",None),getattr(evidence,"right",None)) or
                type(getattr(evidence,"effect",None)) is not int or
                evidence.effect not in (0,1)):
            raise ValueError("WSP128_CONTROL_BAD_EVIDENCE")
        st=self._state(view)
        key=(evidence.left,evidence.right)
        if key in st.cells:
            raise ValueError("WSP128_CONTROL_DUPLICATE_ACTION")
        st.cells[key]=evidence.effect
        if self.prior is not None:
            old=self.prior.infer(view,evidence.subject)
            if old is not None:
                st.residual[key]=old^evidence.effect
        st.cache=None

class SymbolicExact(_EvidenceBook):
    """Independent constraint propagation over a single residual outer product."""
    def _constraints(self,st):
        if st.cache is not None:
            return st.cache
        view=st.view
        anchor=None
        for a in range(6):
            if (all((a,b) in st.cells for b in range(64)) and
                    any(st.residual.get((a,b))==1 for b in range(64)) and
                    all((a,b) in st.residual for b in range(64))):
                anchor=a
                break
        contradicted=any(v==1 for v in st.residual.values())
        if anchor is None:
            st.cache=("SUSPECT" if contradicted else "UNCHANGED",None,{})
            return st.cache
        vector=tuple(st.residual[anchor,b] for b in range(64))
        row_bits={}
        contradictory=False
        for a in range(64):
            constraints=set()
            for b in range(64):
                observed=st.residual.get((a,b))
                if observed is not None and vector[b]==1:
                    constraints.add(observed)
            if len(constraints)>1:
                contradictory=True
            elif constraints:
                row_bits[a]=next(iter(constraints))
        for (a,b),observed in st.residual.items():
            if a in row_bits and observed!=row_bits[a]*vector[b]:
                contradictory=True
        if row_bits.get(anchor)!=1:
            contradictory=True
        st.cache=("INVALID" if contradictory else "REPAIRED",
                  vector,row_bits)
        return st.cache

    def infer(self,view,subject):
        a,b=view.pair(subject)
        state=self._state(view)
        if (a,b) in state.cells:
            return state.cells[a,b]
        old=self.prior.infer(view,subject)
        kind,vector,rows=self._constraints(state)
        if kind=="UNCHANGED":
            return old
        if kind!="REPAIRED" or old is None or a not in rows:
            return None
        return old^(vector[b]*rows[a])

class SafeAbort(_EvidenceBook):
    def infer(self,view,subject):
        a,b=view.pair(subject)
        st=self._state(view)
        if (a,b) in st.cells:
            return st.cells[a,b]
        if any(x==1 for x in st.residual.values()):
            return None
        return self.prior.infer(view,subject)

class StalePrior(_EvidenceBook):
    def infer(self,view,subject):
        a,b=view.pair(subject)
        st=self._state(view)
        if (a,b) in st.cells:
            return st.cells[a,b]
        return self.prior.infer(view,subject)

class NoUpdate(_EvidenceBook):
    def infer(self,view,subject):
        return None
