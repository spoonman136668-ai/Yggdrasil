"""WSP126 independent optimized symbolic causal row-space comparator.

No import from numeric or source. Full first-eight rows are independently
reduced over GF2, then each new row is constrained by the paid four-pivot
outcomes. If rank is not identified, abstain instead of extrapolating.
"""
from __future__ import annotations
import random


def _independent_span(rows):
    """Canonical row-space generator via iterative reduction, not direct weights."""
    basis=[]
    for observed in rows:
        remainder=observed
        for vector in sorted(basis,reverse=True):
            remainder=min(remainder,remainder^vector)
        if remainder:
            basis.append(remainder)
    return sorted(basis,reverse=True)


class OptimizedSymbolic:
    def __init__(self):
        self.cells={}
        self.seen=set()
        self.cache={}

    def observe(self,view,source):
        if (getattr(view,"cohort",None)!="fit" or
                view.seed!=132000+view.law_id or
                source.seed!=view.seed or source.law_id!=view.law_id or
                type(source.subject) is not int or source.subject not in view.legal or
                view.pair(source.subject)!=(source.left,source.right) or
                type(source.effect) is not int or source.effect not in (0,1)):
            raise ValueError("WSP126_SYMBOLIC_SOURCE_UNVERIFIED")
        pair=(view.seed,source.subject)
        if pair in self.seen or (source.left,source.right) in self.cells.get(view.law_id,{}):
            raise ValueError("WSP126_SYMBOLIC_DUPLICATE_SOURCE")
        self.seen.add(pair)
        self.cells.setdefault(view.law_id,{})[(source.left,source.right)]=source.effect
        self.cache.pop(view.law_id,None)

    def _compile(self,law):
        evidence=self.cells.get(law,{})
        complete={}
        for a in range(8):
            if all((a,b) in evidence for b in range(16)):
                complete[a]=sum(evidence[a,b]<<b for b in range(16))
        span=_independent_span(complete.values())
        # At rank<4 an unseen independent causal direction may exist, so
        # an unqueried late-row target MUST abstain.
        results={}
        for a in range(8):
            if a in complete:
                for b in range(16):
                    results[a,b]=(complete[a]>>b)&1
        if len(span)==4:
            all_rows=[]
            for select in range(16):
                mask=0
                for j,v in enumerate(span):
                    if select & (1<<j):
                        mask^=v
                all_rows.append(mask)
            for a in range(8,16):
                constraints=[(b,v) for (x,b),v in evidence.items() if x==a]
                candidates=[mask for mask in all_rows
                            if all(((mask>>b)&1)==value for b,value in constraints)]
                if not candidates:
                    raise ValueError("WSP126_SYMBOLIC_OUTSIDE_PRESET_RANK4")
                for b in range(16):
                    p={(mask>>b)&1 for mask in candidates}
                    if len(p)==1:
                        results[a,b]=next(iter(p))
        self.cache[law]=results

    def infer(self,view,subject):
        a,b=view.pair(subject)
        law=view.law_id
        if law not in self.cache:
            self._compile(law)
        return self.cache[law].get((a,b),
                                  self.cells.get(law,{}).get((a,b)))

    def known(self,law):
        if law not in self.cache:
            self._compile(law)
        return len(self.cache[law])


class RankOneAblation:
    """Only one observed row basis; deliberately no subsequent rank growth."""
    def __init__(self):
        self.cells={}
        self.row=None
        self.by_law={}

    def observe(self,view,source):
        law=view.law_id
        self.cells.setdefault(law,{})[(source.left,source.right)]=source.effect
        if source.left==0:
            row=self.cells[law]
            if all((0,b) in row for b in range(16)):
                self.by_law[law]=sum(row[0,b]<<b for b in range(16))

    def infer(self,view,subject):
        a,b=view.pair(subject)
        row=self.cells.get(view.law_id,{})
        if (a,b) in row:
            return row[a,b]
        base=self.by_law.get(view.law_id)
        if base is None:
            return None
        if a<8:
            # Only learn first row, do not generalize source's other rows.
            return None
        for col in range(16):
            if base & (1<<col) and (a,col) in row:
                return row[a,col]*((base>>b)&1)
        return None


class MemoOnly:
    def __init__(self):
        self.events={}
    def observe(self,view,source):
        self.events[source.subject]=source.effect
    def infer(self,view,subject):
        return self.events.get(subject)


class NoUpdate:
    def observe(self,view,source):
        return None
    def infer(self,view,subject):
        return None


def passive_actions(view):
    if view.cohort!="fit":
        raise PermissionError("WSP126_PASSIVE_REQUIRES_FIT")
    ids=list(view.legal)
    random.Random(126889+view.law_id*17).shuffle(ids)
    return tuple(ids[:160])
