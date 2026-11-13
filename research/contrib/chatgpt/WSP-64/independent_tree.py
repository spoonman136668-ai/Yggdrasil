"""Independent deterministic symbolic decision-tree diagnostic for WSP64.

Only charged state/action/consequence rows. No hidden evaluator source, no
sparse polynomial basis and no gradient optimizer. This is a standard
fully fitted finite binary tree control, not a strong pretrained neural
baseline or a matched total-compute conventional-model study.
"""
from __future__ import annotations
from collections import Counter
from math import log2


def _entropy(values):
    n=len(values)
    if not n:
        return 0.0
    totals=Counter(values)
    return -sum((count/n)*log2(count/n) for count in totals.values())


def _fit(rows, available):
    if not rows:
        return None
    labels=[y for state,y in rows]
    if len(set(labels))==1:
        return ("leaf",labels[0])
    if not available:
        return ("unknown",)
    n=len(rows)
    best=None
    for feature in available:
        left=[r for r in rows if r[0][feature]==0]
        right=[r for r in rows if r[0][feature]==1]
        if not left or not right:
            continue
        score=_entropy(labels)-(len(left)/n)*_entropy([y for s,y in left])-(
            len(right)/n)*_entropy([y for s,y in right])
        if best is None or score>best[0]+1e-12 or (
                abs(score-best[0])<1e-12 and feature<best[1]):
            best=(score,feature,left,right)
    if best is None:
        return ("unknown",)
    _,feature,left,right=best
    remaining=tuple(x for x in available if x!=feature)
    return ("branch",feature,_fit(left,remaining),_fit(right,remaining))


def _apply(tree,before):
    while tree is not None:
        if tree[0]=="leaf":
            return tree[1]
        if tree[0]=="unknown":
            return None
        tree=tree[2+before[tree[1]]]
    return None


class IndependentTreeControl:
    """Builds per-channel/output variable-width decision trees from public rows."""
    def __init__(self,ledger,bits):
        if bits not in (3,4,5):
            raise ValueError("invalid binary sensor width")
        self.bits=bits
        self.trees={}
        for action in range(4):
            rows=[(before,after) for before,a,after in ledger if a==action]
            self.trees[action]=tuple(
                _fit([(state,y[bit]) for state,y in rows],tuple(range(bits)))
                for bit in range(bits)
            )

    def predict(self,before,action):
        if type(before) is not tuple or len(before)!=self.bits or (
                type(action) is not int or action not in range(4)):
            raise ValueError("invalid physical query")
        output=tuple(_apply(tree,before) for tree in self.trees[action])
        return output if all(value is not None for value in output) else None
