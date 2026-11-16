"""Independent WSP123 symbolic path-inference comparator and negatives.

The strongest control uses the SAME verified observations and implements
weighted bipartite XOR constraints, not a deliberately weakened table.
"""
from __future__ import annotations
from collections import deque
import random


class StrongSymbolicFactors:
    def __init__(self):
        self.adj={d:{i:{} for i in range(16)} for d in range(4)}
        self._seen=set()

    def observe(self, view, evidence):
        if (view.seed != evidence.seed or view.domain != evidence.domain
                or view.seed not in range(123900,123904)
                or evidence.subject not in view.legal
                or view.pair(evidence.subject) != (evidence.left,evidence.right)
                or type(evidence.effect) is not int or not 0 <= evidence.effect < 8):
            raise ValueError("WSP123_SYMBOLIC_BAD_SOURCE")
        key=(view.seed,evidence.subject)
        if key in self._seen:
            raise ValueError("WSP123_SYMBOLIC_DUPLICATE")
        a,b=evidence.left,8+evidence.right
        predicted=self._relation(view.domain,a,b)
        if predicted is not None and predicted != evidence.effect:
            raise ValueError("WSP123_SYMBOLIC_CAUSAL_CONTRADICTION")
        self.adj[view.domain][a][b]=evidence.effect
        self.adj[view.domain][b][a]=evidence.effect
        self._seen.add(key)

    def _relation(self,domain,start,target):
        visited={start:0}
        pending=deque([start])
        while pending:
            node=pending.popleft()
            if node==target:
                return visited[node]
            for nxt,value in self.adj[domain][node].items():
                if nxt not in visited:
                    visited[nxt]=visited[node]^value
                    pending.append(nxt)
        return None

    def infer(self,view,subject):
        a,b=view.pair(subject)
        return self._relation(view.domain,a,8+b)

    def choose(self,view,available):
        by_pair={view.pair(s):s for s in available if s in view.legal}
        for pair in ([(0,b) for b in range(8)]+[(a,0) for a in range(1,8)]):
            s=by_pair.get(pair)
            if s is not None and (view.seed,s) not in self._seen:
                return s
        return None


class MemoOnly:
    def __init__(self):
        self.table={}
    def observe(self,view,evidence):
        if evidence.subject in self.table:
            raise ValueError("WSP123_MEMO_DUPLICATE")
        self.table[evidence.subject]=evidence.effect
    def infer(self,view,subject):
        return self.table.get(subject)


class NoUpdate:
    def observe(self,view,evidence):
        return None
    def infer(self,view,subject):
        return None


def passive_selection(view,ordinal):
    rng=random.Random(123777+view.domain*31+ordinal)
    pool=list(view.legal)
    rng.shuffle(pool)
    return tuple(pool[:15])
