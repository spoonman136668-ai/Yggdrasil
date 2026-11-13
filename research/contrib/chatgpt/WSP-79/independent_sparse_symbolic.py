"""Independent same-prior six-bit sparse GF2 symbolic causal predictor.

Uses exactly the same PUBLIC degree<=3, <=3-monomial hypothesis space
and the exact same REAL paid rows as WSP79 numerical compiler, but does
not import its learner, matrices, confidence weights, or functions. This
is a STRONG symbolic causal control, not a deliberately weak baseline.
A tie prevents claims of neural predictive superiority over symbolic.
"""
from __future__ import annotations
from collections import defaultdict
from itertools import combinations,product

_ACTIONS=range(6)
_STATES=set(product((0,1),repeat=6))
_TERMS=[tuple(t) for k in range(4) for t in combinations(range(6),k)]
assert len(_TERMS)==42


def _signature(state):
    return sum((1<<j) for j,term in enumerate(_TERMS)
               if all(state[t] for t in term))


class IndependentSparseSymbolic:
    def __init__(self,public_charged_rows):
        paid=[{} for a in _ACTIONS]
        for state,action,out in public_charged_rows:
            if state not in _STATES or out not in _STATES or action not in _ACTIONS:
                raise ValueError("illegal independently charged public observation")
            if state in paid[action] and paid[action][state]!=out:
                raise ValueError("conflicting deterministic paid consequence")
            paid[action][state]=out
        self.hypotheses=[]
        for action in _ACTIONS:
            rows=tuple(sorted(paid[action].items()))
            observed=[0]*42
            targets=[0]*6
            for i,(before,after) in enumerate(rows):
                features=_signature(before)
                for j in range(42):
                    if features&(1<<j):
                        observed[j]|=1<<i
                for j in range(6):
                    if before[j]!=after[j]:
                        targets[j]|=1<<i
            equations=defaultdict(list)
            equations[0].append(0)
            for i in range(42):
                equations[observed[i]].append(1<<i)
            for k,j in combinations(range(42),2):
                equations[observed[k]^observed[j]].append((1<<k)|(1<<j))
            for k,j,i in combinations(range(42),3):
                equations[observed[k]^observed[j]^observed[i]].append(
                    (1<<k)|(1<<j)|(1<<i))
            self.hypotheses.append([tuple(equations.get(t,())) for t in targets])

    def predict(self,state,action):
        if state not in _STATES or action not in _ACTIONS:
            raise ValueError("invalid symbolic public query")
        feature=_signature(state)
        result=[]
        for candidates in self.hypotheses[action]:
            if not candidates:
                return None
            values={(mask&feature).bit_count()&1 for mask in candidates}
            if len(values)!=1:
                return None
            result.append(next(iter(values)))
        return tuple(state[j]^result[j] for j in range(6))
