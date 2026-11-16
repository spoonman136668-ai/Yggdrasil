"""Independent strong causal constraint solver and negative controls.

No import of the numeric learner or hidden source. Exhausts all candidate
threshold rectangles and nonzero 3-bit deltas with independent XOR graph
consistency. Honest abstention on nonidentifiable predictions.
"""
from __future__ import annotations
from collections import deque
import random

FIT=frozenset(range(128900,128916))
DOMAINS=16
UNSET=object()


class StrongSymbolic:
    def __init__(self):
        self.rows={d:[] for d in range(DOMAINS)}
        self._seen=set()
        self._cache={}

    def observe(self,view,event):
        if (getattr(view,"seed",None) not in FIT
                or view.domain!=view.seed-128900
                or event.seed!=view.seed or event.domain!=view.domain
                or type(event.subject) is not int
                or event.subject not in view.legal
                or view.pair(event.subject)!=(event.left,event.right)
                or type(event.effect) is not int or not 0<=event.effect<8):
            raise ValueError("WSP124_SYMBOLIC_UNVERIFIED_SOURCE")
        key=(view.seed,event.subject)
        if key in self._seen:
            raise ValueError("WSP124_SYMBOLIC_DUPLICATE")
        self._seen.add(key)
        self.rows[view.domain].append((event.left,event.right,event.effect))
        self._cache.pop(view.domain,None)

    @staticmethod
    def _solve(edges):
        # 16 bipartite nodes, XOR edge constraints for base row/column factors.
        graph=[[] for _ in range(16)]
        for a,b,value in edges:
            graph[a].append((8+b,value))
            graph[8+b].append((a,value))
        values=[None]*16
        components=[-1]*16
        component=0
        for root in range(16):
            if values[root] is not None:
                continue
            queue=deque([root])
            values[root]=0
            components[root]=component
            while queue:
                node=queue.popleft()
                for other,value in graph[node]:
                    inferred=values[node]^value
                    if values[other] is None:
                        values[other]=inferred
                        components[other]=component
                        queue.append(other)
                    elif values[other]!=inferred:
                        return None
            component+=1
        return values,components

    def _compile(self,domain):
        rows=self.rows[domain]
        stable=[UNSET]*64
        candidates=0
        for tx in range(2,8):
            for ty in range(2,8):
                for delta in range(1,8):
                    edges=[(a,b,value^(delta if a>=tx and b>=ty else 0))
                           for a,b,value in rows]
                    solution=self._solve(edges)
                    if solution is None:
                        continue
                    candidates+=1
                    values,components=solution
                    for a in range(8):
                        for b in range(8):
                            idx=8*a+b
                            predicted=(values[a]^values[8+b]^
                                      (delta if a>=tx and b>=ty else 0)
                                      if components[a]==components[8+b]
                                      else None)
                            if stable[idx] is UNSET:
                                stable[idx]=predicted
                            elif stable[idx]!=predicted:
                                stable[idx]=None
        if not candidates:
            raise ValueError("WSP124_SYMBOLIC_NO_CONSISTENT_CAUSAL_MODEL")
        # If any one candidate abstained, later candidates cannot override it.
        self._cache[domain]=(tuple(None if x is UNSET else x for x in stable),
                             candidates)

    def infer_pair(self,domain,left,right):
        if (type(domain) is not int or not 0<=domain<DOMAINS
                or type(left) is not int or not 0<=left<8
                or type(right) is not int or not 0<=right<8):
            raise ValueError("WSP124_SYMBOLIC_BAD_PUBLIC_PAIR")
        if domain not in self._cache:
            self._compile(domain)
        return self._cache[domain][0][left*8+right]

    def infer(self,view,subject):
        return self.infer_pair(view.domain,*view.pair(subject))

    def candidate_count(self,domain):
        if domain not in self._cache:
            self._compile(domain)
        return self._cache[domain][1]


class XorOnly:
    """Frozen separable prior; sees every paid effect but cannot repair."""
    def __init__(self):
        self.rows={d:{} for d in range(DOMAINS)}
        self._seen=set()

    def observe(self,view,event):
        if view.seed not in FIT or event.seed!=view.seed:
            raise ValueError("WSP124_XOR_SOURCE_DENIED")
        key=(view.seed,event.subject)
        if key in self._seen:
            raise ValueError("WSP124_XOR_DUPLICATE")
        self._seen.add(key)
        self.rows[view.domain][(event.left,event.right)]=event.effect

    def infer(self,view,subject):
        a,b=view.pair(subject)
        rows=self.rows[view.domain]
        if not all((0,i) in rows for i in range(8)) or not all(
                (i,0) in rows for i in range(1,8)):
            return None
        return rows[a,0]^rows[0,b]^rows[0,0]


class NoUpdate:
    def observe(self,view,event):
        return None
    def infer(self,view,subject):
        return None


def passive_order(view):
    rng=random.Random(124737+view.domain*1009)
    subjects=list(view.legal)
    rng.shuffle(subjects)
    return tuple(subjects[:23])
