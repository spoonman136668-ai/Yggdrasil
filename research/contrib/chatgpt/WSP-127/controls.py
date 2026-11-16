"""Independent optimized symbolic GF(2) row-space solver for WSP127.

NO import of numeric or source. This is a mathematically capable reference,
not a deliberately weak brute-force binary assignment enumerator.
"""
from __future__ import annotations

def _row_span(vectors):
    pivot = {}
    for value in vectors:
        x = value
        while x:
            highest = x.bit_length() - 1
            if highest in pivot:
                x ^= pivot[highest]
            else:
                pivot[highest] = x
                break
    return tuple(pivot[key] for key in sorted(pivot, reverse=True))

class _Law:
    def __init__(self):
        self.cells = [{} for _ in range(64)]
        self.seen = set()
        self.cache = None

    def _compile(self):
        full = {}
        for row in range(64):
            if len(self.cells[row]) == 64:
                full[row] = sum(value << b for b, value in self.cells[row].items())
        basis = _row_span(full.values())
        resolved = [None] * 64
        for row, mask in full.items():
            resolved[row] = mask
        if len(basis) == 8:
            # Independent exact linear-algebra reference: enumerate the
            # 2^8 row-space elements and retain only evidence-consistent ones.
            combinations = [0]
            for v in basis:
                combinations += [x ^ v for x in combinations]
            for row in range(64):
                observed = self.cells[row]
                if not observed or resolved[row] is not None:
                    continue
                fits = [candidate for candidate in combinations
                        if all(((candidate >> col) & 1) == bit
                               for col, bit in observed.items())]
                if len(fits) == 1:
                    resolved[row] = fits[0]
                elif len(fits) == 0:
                    raise ValueError("WSP127_STRONG_SYMBOLIC_RANK_CONTRADICTION")
        self.cache = resolved

    def infer(self, a, b):
        if b in self.cells[a]:
            return self.cells[a][b]
        if self.cache is None:
            self._compile()
        mask = self.cache[a]
        return None if mask is None else (mask >> b) & 1

class OptimizedSymbolic:
    def __init__(self):
        self.laws = {}

    def observe(self, view, evidence):
        if (getattr(view, "cohort", None) != "fit" or
                view.seed != 135000 + view.law_id or
                getattr(evidence, "seed", None) != view.seed or
                getattr(evidence, "law_id", None) != view.law_id or
                getattr(evidence, "subject", None) not in view.legal or
                view.pair(evidence.subject) !=
                    (getattr(evidence, "left", None), getattr(evidence, "right", None)) or
                type(getattr(evidence, "effect", None)) is not int or
                evidence.effect not in (0, 1)):
            raise ValueError("WSP127_SYMBOLIC_SOURCE_INVALID")
        st = self.laws.setdefault(view.law_id, _Law())
        a, b = evidence.left, evidence.right
        if (a, b) in st.seen:
            raise ValueError("WSP127_SYMBOLIC_DUPLICATE")
        st.seen.add((a, b))
        st.cells[a][b] = evidence.effect
        st.cache = None

    def infer(self, view, subject):
        a, b = view.pair(subject)
        return self.laws[view.law_id].infer(a, b)

class NoUpdate:
    def observe(self, view, evidence):
        return None

    def infer(self, view, subject):
        return None
