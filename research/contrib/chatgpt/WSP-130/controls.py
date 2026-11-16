"""WSP130 independent complete symbolic and safe-abort controls.

No import of learner, source or source-only hidden law metadata.
Exactly 126 possible high supports plus unchanged are exhausted, and all
candidate effects must match the same paid transcript as the numeric learner.
"""
from __future__ import annotations

LOW=tuple(sorted((x for x in range(256) if x.bit_count()<=3),
                 key=lambda x:(x.bit_count(),x)))
CANDIDATES=(None,)+tuple(x for x in range(256) if x.bit_count() in (4,5))

def _base_from_observed(observations):
    if len(observations)<93:
        raise ValueError("WSP130_CONTROL_INCOMPLETE_LOWER_OBSERVATIONS")
    coeff={}
    for x in LOW:
        if x not in observations:
            raise ValueError("WSP130_CONTROL_MISSING_BASIS")
        v=observations[x]
        for mask,c in coeff.items():
            if x&mask==mask:
                v^=c
        coeff[x]=v
    # Distinct reference readout: evaluate complete polynomial directly.
    return tuple(sum(c for mask,c in coeff.items() if (x&mask)==mask)%2
                 for x in range(256))

class _State:
    def __init__(self,view):
        self.view=view
        self.observed={}
        self.base=None
        self.candidates=list(CANDIDATES)
        self.changed=False

    def add(self,x,bit):
        if x in self.observed:
            raise ValueError("WSP130_CONTROL_DUPLICATE")
        self.observed[x]=bit
        if len(self.observed)==93:
            self.base=_base_from_observed(self.observed)
        if self.base is not None and x not in LOW:
            self.changed |= self.base[x]!=bit
            self.candidates=[
                mask for mask in self.candidates
                if self.base[x]^(int(mask is not None and x&mask==mask))==bit
            ]

class _Control:
    def __init__(self):
        self.states={}

    def _state(self,view,create=False):
        if (getattr(view,"cohort",None) not in ("probe","transfer") or
                type(getattr(view,"law_id",None)) is not int or
                not 0<=view.law_id<144):
            raise PermissionError("WSP130_CONTROL_INVALID_VIEW")
        if view.law_id not in self.states and create:
            if view.cohort!="probe":
                raise PermissionError("WSP130_CONTROL_TRANSFER_TRAINING_DENIED")
            self.states[view.law_id]=_State(view)
        return self.states.get(view.law_id)

    def observe(self,view,evidence):
        if (view.cohort!="probe" or
                getattr(evidence,"seed",None)!=view.seed or
                getattr(evidence,"law_id",None)!=view.law_id or
                getattr(evidence,"subject",None) not in view.legal or
                view.input(evidence.subject)!=getattr(evidence,"input",None) or
                type(getattr(evidence,"effect",None)) is not int or
                evidence.effect not in (0,1)):
            raise ValueError("WSP130_CONTROL_SOURCE_INVALID")
        st=self._state(view,create=True)
        if st.view is not view:
            raise ValueError("WSP130_CONTROL_VIEW_REPLACEMENT")
        st.add(evidence.input,evidence.effect)

class ExactSymbolic(_Control):
    def infer(self,view,subject):
        state=self._state(view)
        if state is None or state.base is None or not state.candidates:
            return None
        x=view.input(subject)
        first=state.base[x]^int(
            state.candidates[0] is not None and
            x&state.candidates[0]==state.candidates[0])
        for mask in state.candidates[1:]:
            prediction=state.base[x]^int(mask is not None and x&mask==mask)
            if prediction!=first:
                return None
        return first

    def status(self,view):
        state=self._state(view)
        if state is None or state.base is None:
            return "UNTRAINED"
        if not state.candidates: return "UNSUPPORTED"
        if len(state.candidates)==1 and state.candidates[0] is None: return "NONE"
        if len(state.candidates)==1: return "SINGLE"
        return "AMBIGUOUS"

    def support(self,view):
        state=self._state(view)
        if state is None or len(state.candidates)!=1:
            return None
        return state.candidates[0]

class SafeAbort(_Control):
    def infer(self,view,subject):
        st=self._state(view)
        if st is None or st.base is None or st.changed:
            return None
        return st.base[view.input(subject)]

class StalePrior(_Control):
    def infer(self,view,subject):
        st=self._state(view)
        if st is None or st.base is None:
            return None
        return st.base[view.input(subject)]

class NoUpdate:
    def observe(self,view,evidence):
        return None

    def infer(self,view,subject):
        return None
