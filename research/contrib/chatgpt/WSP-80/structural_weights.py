"""WSP80 source-blind paid-contradiction-triggered numerical ReLU feature repair.

No physics/source/evaluator import. Training accepts only continuous charged rows.
Cold restore/predict uses numerical weights and biases, never symbolic candidates.
This is research development code, not a scientific acceptance result.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
from itertools import combinations, product
import json
import math

STATES = tuple(product((0, 1), repeat=6))
ACTIONS = tuple(range(6))
LOW = tuple(term for degree in range(4) for term in combinations(range(6), degree))
HIGH = LOW + tuple(combinations(range(6), 4))
assert len(LOW) == 42 and len(HIGH) == 57
SCHEMA = 'wsp80.paid-structural-numeric.v1'
MAX_SNAPSHOT_BYTES = 1100000


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False)


def relu(x):
    return max(0.0, x)


def valid_state(s):
    if type(s) is not tuple or s not in STATES:
        raise ValueError('invalid public state')


def _survivors(rows, terms):
    """Exact <=3-term parity explanations of actually supplied public observations."""
    observed = [0] * len(terms)
    targets = [0] * 6
    for row, (s, y) in enumerate(sorted(rows.items())):
        valid_state(s)
        valid_state(y)
        for j, term in enumerate(terms):
            if all(s[b] for b in term):
                observed[j] |= 1 << row
        for bit in range(6):
            if s[bit] ^ y[bit]:
                targets[bit] |= 1 << row
    by_signature = defaultdict(list)
    for size in range(4):
        for picked in combinations(range(len(terms)), size):
            signature = 0
            vector = 0
            for i in picked:
                signature ^= observed[i]
                vector |= 1 << i
            by_signature[signature].append(vector)
    return tuple(tuple(by_signature.get(t, ())) for t in targets)


def _confident(options, terms, s):
    if not options:
        return False
    query = sum(1 << i for i, term in enumerate(terms)
                if all(s[bit] for bit in term))
    answer = (options[0] & query).bit_count() & 1
    return all(((vector & query).bit_count() & 1) == answer
               for vector in options[1:])


def _exact_detector(s, action):
    # ReLU returns exactly 1 at this public state/action, 0 elsewhere.
    weights = [float(1 if bit else -1) for bit in s]
    weights.extend(float(j == action) for j in ACTIONS)
    bias = float(sum(1 for bit in s if not bit) - 6)
    return weights, bias


class PaidStructuralWeightEditor:
    def __init__(self):
        self.current = (0,) * 6
        self.charges = 0
        self._rows = [{} for _ in ACTIONS]
        self._payload = None
        self._diagnostic = None

    def charge(self, before, action, after, action_cost=1):
        valid_state(before)
        valid_state(after)
        if type(action) is not int or action not in ACTIONS:
            raise ValueError('invalid public action')
        if type(action_cost) is not int or action_cost != 1:
            raise ValueError('missing physical charge')
        if self._rows is None or before != self.current or self.charges >= 384:
            raise ValueError('noncontinuous, restored, or overbudget experience')
        previous = self._rows[action].get(before)
        if previous is not None and previous != after:
            raise ValueError('nondeterministic paid observation')
        self._rows[action][before] = after
        self.current = after
        self.charges += 1
        self._payload = None

    def compile(self):
        if self._rows is None or self.charges not in (144, 384):
            raise ValueError('only compile after full paid StageA or StageB')
        all_options = []
        contradictions = []
        action_terms = []
        for a, rows in enumerate(self._rows):
            low = _survivors(rows, LOW)
            failed = tuple(bit for bit in range(6) if not low[bit])
            if failed:
                high = _survivors(rows, HIGH)
                for bit in failed:
                    contradictions.append((a, bit))
                options = tuple((high[bit], HIGH) if bit in failed else
                                (low[bit], LOW) for bit in range(6))
                terms = HIGH
            else:
                options = tuple((low[bit], LOW) for bit in range(6))
                terms = LOW
            all_options.append(options)
            action_terms.append(terms)
        features = [(a, term) for a, terms in enumerate(action_terms)
                    for term in terms]
        hidden_w = []
        hidden_b = []
        for a, term in features:
            w = [float(bit in term) for bit in range(6)]
            w.extend(float(i == a) for i in ACTIONS)
            hidden_w.append(w)
            hidden_b.append(float(-len(term)))
        indices = {feature: i for i, feature in enumerate(features)}
        effect_w = [[0.0] * len(features) for _ in range(6)]
        for a, options in enumerate(all_options):
            for bit, (survivors, terms) in enumerate(options):
                if not survivors:
                    continue
                for j, term in enumerate(terms):
                    if survivors[0] >> j & 1:
                        effect_w[bit][indices[(a, term)]] = 1.0
        confidence_w = []
        confidence_b = []
        for s in STATES:
            for a, options in enumerate(all_options):
                if all(_confident(candidates, terms, s)
                       for candidates, terms in options):
                    w, b = _exact_detector(s, a)
                    confidence_w.append(w)
                    confidence_b.append(b)
        self._payload = {
            'schema': SCHEMA, 'charges': self.charges,
            'hidden_w': hidden_w, 'hidden_b': hidden_b,
            'effect_w': effect_w,
            'confidence_w': confidence_w, 'confidence_b': confidence_b,
        }
        self._diagnostic = {
            'charged_actions': self.charges,
            'paid_incompatible_action_outputs': tuple(contradictions),
            'paid_incompatible_action_channels': tuple(sorted({a for a, _ in contradictions})),
            'expanded_action_channels': sum(len(t) == 57 for t in action_terms),
            'learned_numerical_relu_features': len(features),
            'confident_public_queries': len(confidence_w),
            'numeric_parameters': len(features) * 13 + len(effect_w) * len(features)
                                  + len(confidence_w) * 13,
            'remaining_incompatible_outputs_after_expansion': sum(
                not candidates for options in all_options for candidates, _ in options),
        }
        return dict(self._diagnostic)

    def predict(self, s, action, force=False):
        valid_state(s)
        if type(action) is not int or action not in ACTIONS or type(force) is not bool:
            raise ValueError('invalid public prediction input')
        if self._payload is None:
            raise ValueError('not compiled')
        p = self._payload
        x = [float(v) for v in s] + [float(j == action) for j in ACTIONS]
        hidden = [relu(sum(v * w for v, w in zip(x, row)) + b)
                  for row, b in zip(p['hidden_w'], p['hidden_b'])]
        prediction = []
        for bit, row in enumerate(p['effect_w']):
            count = sum(v * w for v, w in zip(hidden, row))
            parity = count + sum((-2.0 if j % 2 else 2.0) * relu(count - j)
                                 for j in (1, 2, 3))
            value = x[bit] + parity - 2.0 * relu(x[bit] + parity - 1.0)
            if not math.isfinite(value) or abs(value - round(value)) > 1e-7:
                raise ArithmeticError('invalid numeric effect')
            prediction.append(int(round(value)))
        if force:
            return tuple(prediction)
        score = sum(relu(sum(v * w for v, w in zip(x, row)) + b)
                    for row, b in zip(p['confidence_w'], p['confidence_b']))
        if abs(score - round(score)) > 1e-7 or score > 1 + 1e-7:
            raise ArithmeticError('invalid numeric confidence')
        return tuple(prediction) if score > .5 else None

    def snapshot(self):
        if self._payload is None:
            raise ValueError('not compiled')
        checksum = sha256(canonical(self._payload).encode()).hexdigest()
        raw = canonical({'payload': self._payload, 'sha256': checksum})
        if len(raw) > MAX_SNAPSHOT_BYTES:
            raise ValueError('snapshot oversize')
        return raw

    @classmethod
    def restore(cls, raw):
        if type(raw) is not str or len(raw) > MAX_SNAPSHOT_BYTES:
            raise ValueError('invalid snapshot')
        try:
            obj = json.loads(raw)
            if set(obj) != {'payload', 'sha256'}:
                raise ValueError('bad envelope')
            p = obj['payload']
            if p['schema'] != SCHEMA or p['charges'] not in (144, 384):
                raise ValueError('bad schema or provenance')
            n = len(p['hidden_w'])
            if not 252 <= n <= 342 or len(p['hidden_b']) != n:
                raise ValueError('invalid numerical feature count')
            if len(p['effect_w']) != 6 or any(len(row) != n for row in p['effect_w']):
                raise ValueError('invalid numerical effect head')
            if any(len(row) != 12 for row in p['hidden_w']):
                raise ValueError('invalid numerical input shape')
            c = len(p['confidence_w'])
            if c > 384 or c != len(p['confidence_b']) or any(
                    len(row) != 12 for row in p['confidence_w']):
                raise ValueError('invalid numeric confidence head')
            arrays = [p['hidden_w'], p['hidden_b'], p['effect_w'],
                      p['confidence_w'], p['confidence_b']]
            def is_finite(a):
                if type(a) is list:
                    return all(is_finite(v) for v in a)
                return type(a) in (float, int) and math.isfinite(a)
            if not all(is_finite(a) for a in arrays):
                raise ValueError('nonfinite numerical weights')
            if sha256(canonical(p).encode()).hexdigest() != obj['sha256']:
                raise ValueError('numerical snapshot checksum')
            m = cls()
            m._rows = None
            m.charges = p['charges']
            m._payload = p
            if m.snapshot() != raw:
                raise ValueError('noncanonical numeric snapshot')
            return m
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            raise ValueError('invalid or tampered numerical snapshot') from exc
