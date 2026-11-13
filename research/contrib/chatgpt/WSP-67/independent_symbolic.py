"""WSP67 independently implemented evidence-consistent symbolic control.

No neural compiler imports, no source simulator or hidden role import. Uses
the same *prospectively supplied* <=2-conjunctive effect hypothesis family.
Its independent consensus predictions are deliberately a strong comparator
to direct construction of neural matrices, not a post-hoc weak baseline.
"""
from __future__ import annotations
from itertools import combinations,product

ACTIONS=(0,1,2,3)
STATES=tuple(product((0,1),repeat=4))


def hypotheses():
    options=[("false",()),("true",())]
    for arity in (1,2):
        for dimensions in combinations(range(4),arity):
            for values in product((0,1),repeat=arity):
                options.append(("and",tuple(zip(dimensions,values))))
    return tuple(options)


FUNCTIONS=hypotheses()


def evaluate_function(rule,state):
    kind,clauses=rule
    if kind=="false":
        return 0
    if kind=="true":
        return 1
    return int(all(state[dim]==value for dim,value in clauses))


class IndependentSymbolic:
    def __init__(self,rows):
        self.tables={}
        for action in ACTIONS:
            evidence=[(before,after) for before,a,after in rows if a==action]
            bits=[]
            for bit in range(4):
                candidates=tuple(h for h in FUNCTIONS
                                 if all(evaluate_function(h,before)==
                                        (before[bit]^after[bit])
                                        for before,after in evidence))
                bits.append(candidates)
            self.tables[action]=tuple(bits)

    def predict(self,state,action):
        if type(state) is not tuple or state not in STATES or action not in ACTIONS:
            raise ValueError("invalid physical query")
        result=list(state)
        for bit,models in enumerate(self.tables[action]):
            predictions={evaluate_function(rule,state) for rule in models}
            if len(predictions)!=1:
                return None
            result[bit]^=next(iter(predictions))
        return tuple(result)


class ExactMemory:
    def __init__(self,rows):
        table={}
        for before,action,after in rows:
            table.setdefault((before,action),set()).add(after)
        self.table=table

    def predict(self,state,action):
        if type(state) is not tuple or state not in STATES or action not in ACTIONS:
            raise ValueError("invalid physical query")
        evidence=self.table.get((state,action),set())
        return next(iter(evidence)) if len(evidence)==1 else None
