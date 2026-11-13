"""Source-blind independent same-expressivity symbolic WSP80 control.

Consumes public observations only: no simulator, source labels or numerical
weight editor imports. It is not a scientific result or neural advantage claim.
"""
from collections import defaultdict
from itertools import combinations, product

_STATES = frozenset(product((0, 1), repeat=6))
_ACTIONS = range(6)
_LOW = tuple(t for degree in range(4) for t in combinations(range(6), degree))
_HIGH = _LOW + tuple(combinations(range(6), 4))


def _valid(state):
    return type(state) is tuple and state in _STATES


def _solve(observations, terms):
    """XOR signatures independently enumerated without learner functions."""
    masks = []
    effects = [0] * 6
    for i, (before, after) in enumerate(observations):
        masks.append(tuple(int(all(before[b] for b in term)) for term in terms))
        for bit in range(6):
            if before[bit] != after[bit]:
                effects[bit] |= 1 << i
    signatures = [sum(row[j] << i for i, row in enumerate(masks))
                  for j in range(len(terms))]
    by_signature = defaultdict(list)
    by_signature[0].append(0)
    for width in (1, 2, 3):
        for picked in combinations(range(len(terms)), width):
            sig = 0
            bits = 0
            for j in picked:
                sig ^= signatures[j]
                bits |= 1 << j
            by_signature[sig].append(bits)
    return tuple(tuple(by_signature.get(mask, ())) for mask in effects)


class IndependentConditionalSymbolic:
    def __init__(self, public_rows):
        groups = [dict() for _ in _ACTIONS]
        self.paid_actions = None
        for before, action, after in public_rows:
            if not _valid(before) or not _valid(after) or type(action) is not int or action not in _ACTIONS:
                raise ValueError('invalid public observation')
            if before in groups[action] and groups[action][before] != after:
                raise ValueError('contradictory deterministic observation')
            groups[action][before] = after
        self.survivors = []
        self.terms = []
        self.incompatibilities = []
        for action, group in enumerate(groups):
            pairs = sorted(group.items())
            low = _solve(pairs, _LOW)
            high = _solve(pairs, _HIGH) if any(not c for c in low) else None
            self.terms.append(tuple(_HIGH if not low[b] else _LOW for b in range(6)))
            self.survivors.append(tuple(high[b] if not low[b] else low[b] for b in range(6)) if high else low)
            self.incompatibilities.extend((action, b) for b in range(6) if not low[b])

    @classmethod
    def from_paid_ledger(cls, experiences):
        ledger = tuple(experiences)
        if len(ledger) not in (144, 384):
            raise ValueError('incomplete charged StageA or StageB ledger')
        current = (0,) * 6
        rows = []
        for record in ledger:
            try:
                before, action, after, cost = record.before, record.action, record.after, record.action_cost
            except AttributeError as exc:
                raise ValueError('missing charged public observation') from exc
            if type(cost) is not int or cost != 1 or before != current:
                raise ValueError('noncontinuous or unpaid observation')
            rows.append((before, action, after))
            current = after
        result = cls(rows)
        result.paid_actions = len(rows)
        return result

    def predict(self, state, action):
        if not _valid(state) or type(action) is not int or action not in _ACTIONS:
            raise ValueError('invalid public query')
        prediction = []
        for bit in range(6):
            candidates = self.survivors[action][bit]
            if not candidates:
                return None
            terms = self.terms[action][bit]
            mask = sum(1 << j for j, term in enumerate(terms) if all(state[k] for k in term))
            votes = {((candidate & mask).bit_count() & 1) for candidate in candidates}
            if len(votes) != 1:
                return None
            prediction.append(state[bit] ^ next(iter(votes)))
        return tuple(prediction)
