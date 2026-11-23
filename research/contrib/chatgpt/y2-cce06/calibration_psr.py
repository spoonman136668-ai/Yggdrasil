"""CCE06 public-only predictive-state representation with learned operators.

This comparator is a TRAIN-only observable-operator model, not the Yggdrasil
candidate, an oracle, or a scientifically validated strongest control.
No imports from calibration_worlds or evaluator modules.
"""
from __future__ import annotations

import math

from calibration_controls import validated, code

ACTIONS = (0, 1, 2)
OUTCOMES = (0, 1, 2, 3)
TESTS = tuple((a, o) for o in OUTCOMES for a in ACTIONS)


def _solve(matrix, rhs):
    """Deterministic partial-pivot solve; fitted ridge must be positive."""
    n = len(rhs)
    rows = [list(matrix[i]) + [rhs[i]] for i in range(n)]
    for k in range(n):
        pivot = max(range(k, n), key=lambda i: (abs(rows[i][k]), -i))
        if abs(rows[pivot][k]) < 1e-11:
            raise ValueError('CCE06_PSR_SINGULAR_OPERATOR')
        rows[k], rows[pivot] = rows[pivot], rows[k]
        p = rows[k][k]
        for j in range(k, n + 1):
            rows[k][j] /= p
        for i in range(k + 1, n):
            v = rows[i][k]
            for j in range(k + 1, n + 1):
                rows[i][j] -= v * rows[k][j]
            rows[i][k] = 0.0
    result = [0.0] * n
    for k in range(n - 1, -1, -1):
        result[k] = rows[k][n] - sum(rows[k][j] * result[j] for j in range(k + 1, n))
    if not all(math.isfinite(x) for x in result):
        raise ValueError('CCE06_PSR_NONFINITE_SOLVE')
    return result


class LearnedOperatorPSR:
    """Finite-dimensional recurrent observable-operator predictive state.

    A predictive state has 1 constant test and k one-step interventional tests.
    On TRAIN only, public suffix counts ESTIMATE test predictions per observed
    history; ridge regression then learns 12 action-observation operators
    E[1{next_obs=o} state_after | state_before, action=a]. The lookup
    estimator is discarded after fitting. During prediction, only fitted
    matrices and a recurrent state are used, *never* suffix lookup.

    This is a learned finite-test operator PSR, not a spectral consistency proof.
    Clipping and normalization keep extrapolation well formed; report this
    approximation and compare it with strong HMM and learned neural controls.
    """
    def __init__(self, tests=6, depth=2, ridge=0.05):
        if (type(tests) is not int or tests not in (3, 6, 9, 12)
                or type(depth) is not int or not 1 <= depth <= 4
                or type(ridge) not in (int, float) or not math.isfinite(ridge)
                or not 0 < ridge <= 10):
            raise ValueError('CCE06_PSR_BAD_CAPACITY')
        self.tests = TESTS[:tests]
        self.depth = depth
        self.ridge = float(ridge)
        self.dim = len(self.tests) + 1
        self.fitted = False
        self.operators = {}
        self.initial = None
        self.witnesses = {a: 0 for a in ACTIONS}
        self.events = 0

    @staticmethod
    def _root_counts(data, depth):
        counts = {}
        for events in data:
            obs, acts = validated(events)
            history = []
            for a, outcome in zip(acts, obs[1:]):
                for n in range(min(depth, len(history)) + 1):
                    ctx = tuple(history[-n:]) if n else ()
                    key = (ctx, a)
                    slot = counts.setdefault(key, [0] * 4)
                    slot[outcome] += 1
                history.append((a, outcome))
        return counts

    def _basis(self, counts, history):
        out = [1.0]
        for a, o in self.tests:
            sample = None
            for n in range(min(self.depth, len(history)), -1, -1):
                ctx = tuple(history[-n:]) if n else ()
                sample = counts.get((ctx, a))
                if sample is not None:
                    break
            if sample is None:
                out.append(0.25)
            else:
                out.append((sample[o] + 1) / (sum(sample) + 4))
        return out

    def fit(self, datasets):
        if self.fitted or type(datasets) not in (tuple, list) or not datasets:
            raise ValueError('CCE06_PSR_INVALID_FIT')
        samples = [tuple(events) for events in datasets]
        for events in samples:
            validated(events)
        counts = self._root_counts(samples, self.depth)
        d = self.dim
        xx = {a: [[0.0] * d for _ in range(d)] for a in ACTIONS}
        yx = {(a, o): [[0.0] * d for _ in range(d)] for a in ACTIONS for o in OUTCOMES}
        starts = [0.0] * d
        for events in samples:
            history = []
            for event in events:
                a = event['action']
                o = code(event['next_observation'])
                old_state = self._basis(counts, history)
                history.append((a, o))
                next_state = self._basis(counts, history)
                self.witnesses[a] += 1
                self.events += 1
                for i in range(d):
                    starts[i] += old_state[i]
                    for j in range(d):
                        xx[a][i][j] += old_state[i] * old_state[j]
                        yx[a, o][i][j] += next_state[i] * old_state[j]
        if any(n < d for n in self.witnesses.values()):
            raise ValueError('CCE06_PSR_UNDERSAMPLED_ACTION')
        self.initial = tuple(v / self.events for v in starts)
        for a in ACTIONS:
            gram = [[xx[a][i][j] + (self.ridge if i == j else 0.0)
                     for j in range(d)] for i in range(d)]
            for o in OUTCOMES:
                self.operators[a, o] = tuple(tuple(_solve(gram, row))
                                             for row in yx[a, o])
        self.fitted = True
        return self

    def new_state(self):
        if not self.fitted:
            raise ValueError('CCE06_PSR_NOT_FITTED')
        return self.initial

    def _raw(self, state, action, outcome):
        if (not self.fitted or type(action) is not int or action not in ACTIONS
                or type(outcome) is not int or outcome not in OUTCOMES
                or type(state) not in (tuple, list) or len(state) != self.dim
                or any(type(v) not in (int, float) or not math.isfinite(v) for v in state)):
            raise ValueError('CCE06_PSR_INVALID_STATE_ACTION')
        return tuple(sum(x * y for x, y in zip(row, state))
                     for row in self.operators[action, outcome])

    def forecast(self, state, action):
        # Each first row of the learned operator estimates P(o|do(a),h).
        masses = [max(1e-8, self._raw(state, action, o)[0]) for o in OUTCOMES]
        total = sum(masses)
        return tuple(p / total for p in masses)

    def advance(self, state, action, observed):
        o = code(observed) if type(observed) is list else observed
        raw = self._raw(state, action, o)
        # Prevent unstable extrapolation; never use evaluator latent truth.
        scale = max(raw[0], 1e-8)
        return (1.0,) + tuple(min(1.0, max(0.0, v / scale)) for v in raw[1:])

    def predict(self, past_events, action):
        state = self.new_state()
        if past_events:
            validated(past_events)
            for event in past_events:
                state = self.advance(state, event['action'], event['next_observation'])
        return self.forecast(state, action)


def score_streaming_psr(model, datasets):
    """Score frozen model before outcomes; history/state updated only afterward."""
    from calibration_controls import multichannel_brier
    if not model.fitted:
        raise ValueError('CCE06_PSR_NOT_FITTED')
    error, n = 0.0, 0
    for events in datasets:
        validated(events)
        state = model.new_state()
        for event in events:
            prob = model.forecast(state, event['action'])
            error += multichannel_brier(prob, event['next_observation'])
            state = model.advance(state, event['action'], event['next_observation'])
            n += 1
    return error / n
