"""WSP109 independent direct posterior-weight programmer and symbolic Bayesian controls.

No learner calls a latent-law oracle or hidden query outcome. Numeric posterior
weights are programmed directly by observed action consequences, without SGD.
A genuinely independent symbolic enumerator provides matching/strong controls.
"""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
import math
import numpy as np

from world import HYPOTHESES, N_RULES, ACTION_BUDGET, feature_bits

PRIOR = tuple(HYPOTHESES)
L2 = 0.03
NEWTON_TOL = 1e-9
MAX_NEWTON_STEPS = 100


def _validate_feedback(kind, value):
    if type(kind) is not int or not 0 <= kind < N_RULES or type(value) is not bool:
        raise ValueError("expected one legal observed singleton intervention and Boolean consequence")


class DirectWeightPosterior:
    """36 directly written float32 hypothesis weights, not neural gradients."""

    def __init__(self):
        self.weights: dict[str, np.ndarray] = {}
        self.observed: dict[str, dict[int, bool]] = {}

    def start(self, context: str):
        if not isinstance(context, str) or not context or context in self.weights:
            raise ValueError("duplicate or empty world context")
        self.weights[context] = np.ones(len(PRIOR), dtype=np.float32)
        self.observed[context] = {}

    def program(self, context: str, kind: int, value: bool):
        _validate_feedback(kind, value)
        if context not in self.weights or kind in self.observed[context]:
            raise ValueError("uninitialized or repeatedly observed intervention")
        if len(self.observed[context]) >= ACTION_BUDGET:
            raise ValueError("three-intervention budget exhausted")
        old = self.weights[context]
        consistent = np.array(
            [bool(mask & (1 << kind)) == value for mask in PRIOR], dtype=np.bool_)
        updated = old * consistent.astype(np.float32)
        if not float(updated.sum()) > 0:
            raise ValueError("observed consequence inconsistent with frozen hypothesis family")
        self.weights[context] = updated
        self.observed[context][kind] = value

    def choose_greedy(self, context: str) -> int:
        observed = self.observed[context]
        if len(observed) >= ACTION_BUDGET:
            raise ValueError("cannot select fourth intervention")
        mass = float(self.weights[context].sum())
        best_kind = None
        best_gain = -1.0
        for kind in range(N_RULES):
            if kind in observed:
                continue
            positive = float(sum(float(weight) for mask, weight in
                                 zip(PRIOR, self.weights[context]) if mask & (1 << kind)))
            p = positive / mass
            gain = (-p * math.log2(p) if p > 0 else 0.0) + (
                -(1-p) * math.log2(1-p) if p < 1 else 0.0)
            if gain > best_gain + 1e-12:
                best_kind, best_gain = kind, gain
        if best_kind is None:
            raise AssertionError("no admissible untested intervention")
        return best_kind

    def posterior_count(self, context):
        return int(np.count_nonzero(self.weights[context]))

    def predict(self, context, features):
        query = feature_bits(features)
        weights = self.weights[context]
        hits = sum(float(weight) for mask, weight in
                   zip(PRIOR, weights) if mask & query)
        return 2 * hits >= float(weights.sum())

    def snapshot(self):
        body = {
            context: {
                "weights": [int(v) for v in self.weights[context]],
                "observations": [[k, v] for k, v in
                                 sorted(self.observed[context].items())],
            }
            for context in sorted(self.weights)
        }
        encoded = json.dumps(body, sort_keys=True, separators=(",", ":"))
        return json.dumps({
            "schema": "wsp109.direct-posterior-weights.v1",
            "payload": body,
            "sha256": sha256(encoded.encode("ascii")).hexdigest(),
        }, sort_keys=True, separators=(",", ":"))

    @classmethod
    def restore(cls, serialized):
        envelope = json.loads(serialized)
        if envelope.get("schema") != "wsp109.direct-posterior-weights.v1":
            raise ValueError("unknown direct-weight snapshot schema")
        payload = envelope.get("payload")
        if not isinstance(payload, dict):
            raise ValueError("snapshot requires a world mapping")
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        if sha256(encoded.encode("ascii")).hexdigest() != envelope.get("sha256"):
            raise ValueError("snapshot checksum mismatch")
        model = cls()
        for context, data in payload.items():
            model.start(context)
            seen = data["observations"]
            if (not isinstance(seen, list) or len(seen) > ACTION_BUDGET or
                [pair[0] for pair in seen] !=
                    sorted(set(pair[0] for pair in seen))):
                raise ValueError("invalid observed world action sequence")
            for kind, value in seen:
                model.program(context, kind, value)
            weights = data["weights"]
            if (not isinstance(weights, list) or len(weights) != len(PRIOR) or
                any(type(v) is not int or v not in (0, 1) for v in weights) or
                weights != [int(v) for v in model.weights[context]]):
                raise ValueError("snapshot posterior weights do not follow observations")
        return model


class SymbolicBayes:
    """Independent Python-set posterior, uses no numeric optimizer or weight memory."""

    def __init__(self):
        self.candidates: dict[str, set[int]] = {}
        self.observed: dict[str, dict[int, bool]] = {}

    def start(self, context: str):
        if not context or context in self.candidates:
            raise ValueError("invalid world context")
        self.candidates[context] = set(PRIOR)
        self.observed[context] = {}

    def observe(self, context: str, kind: int, value: bool):
        _validate_feedback(kind, value)
        if kind in self.observed[context] or len(self.observed[context]) >= ACTION_BUDGET:
            raise ValueError("duplicate or over-budget symbolic feedback")
        selected = {candidate for candidate in self.candidates[context]
                    if bool(candidate & (1 << kind)) is value}
        if not selected:
            raise ValueError("no consistent symbolic posterior")
        self.candidates[context] = selected
        self.observed[context][kind] = value

    def predict(self, context, features):
        f = feature_bits(features)
        possible = self.candidates[context]
        n_true = len([mask for mask in possible if mask & f])
        return 2 * n_true >= len(possible)

    def posterior_count(self, context):
        return len(self.candidates[context])

    def choose_depth3(self, context):
        used = set(self.observed[context])
        budget = ACTION_BUDGET - len(used)
        if budget < 1:
            raise ValueError("planning budget depleted")
        remaining = tuple(kind for kind in range(N_RULES) if kind not in used)
        pool = tuple(sorted(self.candidates[context]))
        best = None
        best_cost = math.inf
        for k in remaining:
            reduced = tuple(j for j in remaining if j != k)
            zeros = tuple(x for x in pool if not x & (1 << k))
            ones = tuple(x for x in pool if x & (1 << k))
            n = len(pool)
            cost = (len(zeros) / n * _expected_entropy(zeros, reduced, budget-1)
                    + len(ones) / n * _expected_entropy(ones, reduced, budget-1))
            if cost < best_cost - 1e-12:
                best, best_cost = k, cost
        if best is None:
            raise AssertionError("no expected entropy minimizer")
        return best


@lru_cache(maxsize=200000)
def _expected_entropy(candidates: tuple[int, ...],
                      remaining: tuple[int, ...], depth: int) -> float:
    if not candidates:
        return 0.0
    if depth <= 0 or len(candidates) == 1 or not remaining:
        return math.log2(len(candidates))
    n = len(candidates)
    optimum = math.inf
    for kind in remaining:
        rest = tuple(j for j in remaining if j != kind)
        zero = tuple(x for x in candidates if not x & (1 << kind))
        one = tuple(x for x in candidates if x & (1 << kind))
        cost = (len(zero)/n * _expected_entropy(zero, rest, depth-1)
                + len(one)/n * _expected_entropy(one, rest, depth-1))
        optimum = min(optimum, cost)
    return optimum


class ConventionalLogistic:
    """Fixed, strictly convex L2-logistic trained from only 3 observed outcomes."""

    def __init__(self):
        self.theta = {}
        self.gradients = {}
        self.steps = {}

    @staticmethod
    def _objective(theta, X, y):
        z = X @ theta
        return float(np.logaddexp(0, z).mean() - (y @ z)/len(y)
                     + L2/2 * float(theta@theta))

    def fit(self, context, observed):
        if len(observed) != ACTION_BUDGET or len(set(kind for kind,_ in observed)) != ACTION_BUDGET:
            raise ValueError("conventional control receives exactly 3 unique consequences")
        X = np.zeros((ACTION_BUDGET, N_RULES+1), dtype=np.float64)
        y = np.empty(ACTION_BUDGET, dtype=np.float64)
        for i,(kind,outcome) in enumerate(observed):
            _validate_feedback(kind,outcome)
            X[i,kind] = 1
            X[i,-1] = 1
            y[i] = int(outcome)
        theta = np.zeros(N_RULES+1, dtype=np.float64)
        for step in range(1, MAX_NEWTON_STEPS+1):
            z = X@theta
            probs = 1/(1+np.exp(-np.clip(z,-40,40)))
            grad = X.T@(probs-y)/ACTION_BUDGET + L2*theta
            residual = float(np.max(np.abs(grad)))
            if residual <= NEWTON_TOL:
                break
            curvature = probs*(1-probs)
            H = (X.T*curvature)@X/ACTION_BUDGET + L2*np.eye(N_RULES+1)
            direction = np.linalg.solve(H, grad)
            old = self._objective(theta,X,y)
            slope = float(grad@direction)
            step_size = 1.
            for _ in range(42):
                proposal = theta-step_size*direction
                if self._objective(proposal,X,y) <= old-0.0001*step_size*slope:
                    theta = proposal
                    break
                step_size *= .5
            else:
                raise FloatingPointError("conventional logistic line search failed")
        if residual > NEWTON_TOL:
            raise FloatingPointError("conventional control gradient not stationary")
        self.theta[context] = theta
        self.gradients[context] = residual
        self.steps[context] = step

    def predict(self, context, features):
        bits = feature_bits(features)
        f = np.array([bool(bits & (1<<i)) for i in range(N_RULES)] + [1.],
                     dtype=np.float64)
        return bool(float(self.theta[context]@f) >= 0.0)
