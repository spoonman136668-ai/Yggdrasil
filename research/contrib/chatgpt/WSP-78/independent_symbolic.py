"""INDEPENDENT same-expressive-prior symbolic control, paid rows only.

Unlike WSP78 numeric learner, this control does NOT materialize neural
weight matrices: it uses direct GF2 row-space elimination to predict a
query only when charged physical observations determine its effect.
A tie on heldout consequences means compilation, not predictive superiority
over an already valid same-prior symbolic causal learner.
"""
from __future__ import annotations
from itertools import combinations

_ACTIONS=tuple(range(6))
_STATES={tuple((n>>k)&1 for k in range(6)) for n in range(64)}


def _tokens(degree):
    return tuple(combination for size in range(degree+1)
                 for combination in combinations(range(6),size))


def _poly(state,terms):
    return sum((1<<i) for i,term in enumerate(terms)
               if all(state[k] for k in term))


class IndependentSymbolicCausal:
    def __init__(self,paid,degree=2):
        if degree not in (1,2):
            raise ValueError("invalid independent symbolic grammar")
        self.terms=_tokens(degree)
        self.charged=[[] for _ in _ACTIONS]
        for state,action,after in paid:
            if state not in _STATES or after not in _STATES or action not in _ACTIONS:
                raise ValueError("not a physically paid public input")
            self.charged[action].append((state,after))
        self.rows=[]
        self.contradiction=[]
        for samples in self.charged:
            # Independent Gauss-Jordan elimination, not WSP78's online basis.
            matrix=[[_poly(s,self.terms),
                     sum(int(s[k]!=y[k])<<k for k in range(6))]
                    for s,y in samples]
            inconsistent=False
            rank_rows=[]
            pivot_columns=[]
            for p in range(len(self.terms)-1,-1,-1):
                selected=next((i for i in range(len(rank_rows),len(matrix))
                              if matrix[i][0] & 1<<p),None)
                if selected is None:
                    continue
                row_index=len(rank_rows)
                matrix[row_index],matrix[selected]=matrix[selected],matrix[row_index]
                pivot_columns.append(p)
                for j in range(len(matrix)):
                    if j!=row_index and matrix[j][0]&1<<p:
                        matrix[j][0]^=matrix[row_index][0]
                        matrix[j][1]^=matrix[row_index][1]
                rank_rows.append(matrix[row_index])
            inconsistent=any(features==0 and effect!=0
                             for features,effect in matrix[len(rank_rows):])
            self.rows.append(tuple((pivot_columns[i],mask,rhs)
                                  for i,(mask,rhs) in enumerate(rank_rows)))
            self.contradiction.append(inconsistent)

    def predict(self,state,action):
        if state not in _STATES or action not in _ACTIONS:
            raise ValueError("invalid independently checked query")
        if self.contradiction[action]:
            return None
        mask=_poly(state,self.terms)
        xor=0
        for p,vector,rhs in self.rows[action]:
            if mask&(1<<p):
                mask^=vector
                xor^=rhs
        if mask:
            return None
        return tuple(state[i]^((xor>>i)&1) for i in range(6))
