"""WSP132 independently specified exact symbolic confidence repair.

This is a second implementation: explicit list/set search through the
possible permutation and single-shear *functions* rather than the numerical
packed WSP131 learner's weight bits. It must match every repaired prediction
on the same authenticated consequences, including OOD and cold transfer.
No source/evaluator/repair module imports.
"""
from __future__ import annotations
from itertools import permutations

class _KnownSignatures:
    def __init__(self,original,law):
        self.truth=tuple(original._known(law).truth)
        if len(self.truth)!=256 or any(bit not in (0,1) for bit in self.truth):
            raise ValueError("WSP132_SYMBOLIC_WARM_SOURCE_INCOMPLETE")

def apply_variables(input_value,role_perm):
    output=input_value&0xc0
    for bit in range(6):
        if input_value & (1<<bit):
            output|=1<<role_perm[bit]
    return output

def apply_linear_shear(packed_input,target_bit,source_bit):
    flip=(packed_input>>source_bit)&1
    return packed_input^ (flip<<target_bit)

class _World:
    def __init__(self,view,base,observations,original_remaining):
        self.view=view
        self.base=base
        self.perms=tuple(permutations((0,1,2,3,4,5)))
        if len(self.perms)!=720:
            raise AssertionError("WSP132_STRONG_CONTROL_GRAMMAR_DRIFT")
        self.prior_remaining=tuple(original_remaining)
        evidence=tuple(sorted(observations.items()))
        if len(evidence)!=32:
            raise ValueError("WSP132_STRONG_CONTROL_NOT_FULLY_TRAINED")
        self.alt=[]
        # Independent explicit exhaustive search, no access to numerical
        # packed weights or the challenger bank's cache/control code.
        for p_index,permutation in enumerate(self.perms):
            encoded=[(apply_variables(x,permutation),y)
                     for x,y in evidence]
            for to_bit in range(6):
                for from_bit in range(6):
                    if from_bit==to_bit:
                        continue
                    if all(base[apply_linear_shear(s,to_bit,from_bit)]==y
                           for s,y in encoded):
                        self.alt.append((p_index,to_bit,from_bit))
    def infer(self,x):
        possibilities=set()
        for p_index in self.prior_remaining:
            possibilities.add(self.base[apply_variables(x,self.perms[p_index])])
            if len(possibilities)>1:return None
        for p_index,to_bit,from_bit in self.alt:
            xprime=apply_variables(x,self.perms[p_index])
            possibilities.add(self.base[apply_linear_shear(xprime,to_bit,from_bit)])
            if len(possibilities)>1:return None
        return next(iter(possibilities)) if len(possibilities)==1 else None
    def counts(self):
        return {"pure_compatible":len(self.prior_remaining),
                "shear_compatible":len(self.alt)}

class IndependentSymbolicRepair:
    def __init__(self,original_symbolic):
        self.original=original_symbolic
        self.states={}
        self.first_by_law={}
    def fit(self,view):
        if view.cohort!="probe":
            raise PermissionError("WSP132_SYMBOLIC_TRANSFER_TRAINING_DENIED")
        original=self.original.states.get(view.seed)
        if original is None or len(original.events)!=32:
            raise ValueError("WSP132_SYMBOLIC_ORIGINAL_NOT_FITTED")
        truth=_KnownSignatures(self.original,view.law_id).truth
        state=_World(view,truth,original.events,original.candidates)
        self.states[view.seed]=state
        self.first_by_law.setdefault(view.law_id,state)
    def _state(self,view):
        if view.cohort=="transfer":
            return self.first_by_law.get(view.law_id)
        state=self.states.get(view.seed)
        if state is not None and state.view is not view and state.view.fingerprint()!=view.fingerprint():
            raise ValueError("WSP132_STRONG_CONTROL_CHANGED_PUBLIC_VIEW")
        return state
    def infer(self,view,subject):
        state=self._state(view)
        return None if state is None else state.infer(view.input(subject))
    def counts(self,view):
        state=self._state(view)
        return None if state is None else state.counts()
