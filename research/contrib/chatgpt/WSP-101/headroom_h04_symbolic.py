"""H04 independent strong symbolic ANF inference, same evidence and degree prior.

Never import the evaluator or the packed weight-programming implementation.
"""
from __future__ import annotations

BITS = 10
ACTIONS = ((0,) + tuple(1 << i for i in range(BITS))
           + tuple((1 << i) | (1 << j)
                   for i in range(BITS) for j in range(i + 1, BITS)))


class SymbolicPolynomial:
    def __init__(self, observations):
        if type(observations) not in (tuple, list) or len(observations) != len(ACTIONS):
            raise ValueError("H04 symbolic missing observations")
        rows = []
        for i, pair in enumerate(observations):
            if type(pair) is not tuple or len(pair) != 2:
                raise ValueError("H04 symbolic row malformed")
            x, y = pair
            if type(x) is not int or x != ACTIONS[i] or type(y) is not int or y not in (0, 1):
                raise ValueError("H04 symbolic invalid data")
            rows.append(y)
        terms = []
        c0 = rows[0]
        if c0:
            terms.append(())
        singles = []
        for i in range(BITS):
            coef = rows[i + 1] ^ c0
            singles.append(coef)
            if coef:
                terms.append((i,))
        k = 1 + BITS
        for i in range(BITS):
            for j in range(i + 1, BITS):
                coefficient = rows[k] ^ singles[i] ^ singles[j] ^ c0
                if coefficient:
                    terms.append((i, j))
                k += 1
        self.terms = tuple(terms)
        if any(self.predict(x) != y for x, y in observations):
            raise ValueError("H04 symbolic contradictory source")

    def predict(self, action):
        if type(action) is not int or not 0 <= action < (1 << BITS):
            raise ValueError("H04 symbolic invalid action")
        result = 0
        for term in self.terms:
            if all((action >> bit) & 1 for bit in term):
                result ^= 1
        return result
