"""Independent full 7261-hypothesis sparse symbolic causal control.

Consumes the exact same 56 quadratic basis events and 48 repair events. The
solver does not import H05 numerical writer or evaluator. It enumerates all
sparse symbolic explanations from public causal consequences.
"""
from __future__ import annotations
from itertools import combinations
from headroom_h04_symbolic import SymbolicPolynomial

ACTIONS = (
    932,710,430,811,316,617,702,890,756,371,662,941,803,574,856,842,
    468,335,923,62,692,462,623,254,620,527,315,159,822,1013,902,909,
    899,683,929,433,223,817,1012,1004,501,997,758,837,597,248,419,362
)
CUBIC_TERMS = tuple(combinations(range(10), 3))
TRIPLE_MASKS = tuple(sum(1 << b for b in triple) for triple in CUBIC_TERMS)
assert len(CUBIC_TERMS) == 120 and len(ACTIONS) == 48


class ExactSymbolicRepair:
    def __init__(self, basis, repair):
        self.base = SymbolicPolynomial(basis)
        if type(repair) not in (tuple, list) or len(repair) != len(ACTIONS):
            raise ValueError("H05 symbolic missing public evidence")
        residual = 0
        for idx, row in enumerate(repair):
            if type(row) is not tuple or len(row) != 2:
                raise ValueError("H05 symbolic malformed public row")
            action, response = row
            if (type(action) is not int or action != ACTIONS[idx] or
                type(response) is not int or response not in (0, 1)):
                raise ValueError("H05 symbolic invalid public consequence")
            residual |= (response ^ self.base.predict(action)) << idx

        # Independent symbolic enumeration, no numerical writer/codebook import.
        signatures = tuple(sum(int((action & mask) == mask) << idx
                               for idx, action in enumerate(ACTIONS))
                           for mask in TRIPLE_MASKS)
        matches = []
        if residual == 0:
            matches.append(())
        for i, sig in enumerate(signatures):
            if sig == residual:
                matches.append((i,))
        for i, first in enumerate(signatures):
            for j in range(i + 1, len(signatures)):
                if first ^ signatures[j] == residual:
                    matches.append((i, j))
        if len(matches) != 1:
            raise ValueError("H05 symbolic sparse explanation not identifiable")
        self.cubic_terms = tuple(CUBIC_TERMS[i] for i in matches[0])
        if any(self.predict(x) != y for x, y in repair):
            raise ValueError("H05 symbolic solution contradicts evidence")

    def predict(self, action):
        if type(action) is not int or not 0 <= action < 1024:
            raise ValueError("H05 symbolic invalid target action")
        result = self.base.predict(action)
        for triple in self.cubic_terms:
            result ^= int(all((action >> b) & 1 for b in triple))
        return result
