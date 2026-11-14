"""WSP108 independent numeric, symbolic, and fully fit conventional controls.

No dependency on the private world oracle. Every method receives only the
identical observed path-feature/action consequence evidence.
"""
from __future__ import annotations

from hashlib import sha256
import json
import numpy as np

N_KINDS = 9
REGULARIZATION = 0.03
GRADIENT_TOLERANCE = 1e-9
MAX_NEWTON_STEPS = 100


def checked_features(features):
    f = tuple(features)
    if (len(f) != N_KINDS or
            any(type(x) not in (bool, int) or x not in (0, 1) for x in f)):
        raise ValueError("nine grounded binary relation-pair features required")
    return f


class NumericRuleWeights:
    """Direct *programming* of float32 3x3 rules, not gradient training."""

    def __init__(self):
        self.weights = {}
        self.observed = {}

    def program(self, context, features, observed_consequence):
        f = checked_features(features)
        if type(observed_consequence) is not bool:
            raise ValueError("observed consequence must be boolean")
        if sum(f) == 0:
            if observed_consequence:
                raise ValueError("impossible observed positive no-path consequence")
            return
        if sum(f) != 1:
            raise ValueError("direct rule programming needs identifiable single path")
        index = f.index(1)
        weights = self.weights.setdefault(context, np.zeros((3, 3), dtype=np.float32))
        seen = self.observed.setdefault(context, {})
        if index in seen and seen[index] != observed_consequence:
            raise ValueError("conflicting causal rule observations")
        weights.flat[index] = np.float32(int(observed_consequence))
        seen[index] = observed_consequence

    def complete(self, context):
        return context in self.observed and len(self.observed[context]) == N_KINDS

    def predict(self, context, features):
        f = checked_features(features)
        if not self.complete(context):
            raise ValueError("not all nine observable rules are known")
        strength = float(np.dot(self.weights[context].ravel(),
                                np.asarray(f, dtype=np.float32)))
        return strength >= 0.5

    def snapshot(self):
        payload = {
            context: {
                "weights": self.weights[context].tolist(),
                "observed": [[i, bool(v)]
                             for i, v in sorted(self.observed[context].items())],
            }
            for context in sorted(self.weights)
        }
        data = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True)
        envelope = {
            "schema": "wsp108.numeric-causal-rule-weights-snapshot.v1",
            "payload": payload, "sha256": sha256(data.encode("ascii")).hexdigest(),
        }
        return json.dumps(envelope, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True)

    @classmethod
    def restore(cls, document):
        envelope = json.loads(document)
        if envelope.get("schema") != "wsp108.numeric-causal-rule-weights-snapshot.v1":
            raise ValueError("unsupported weight snapshot")
        payload = envelope.get("payload")
        if not isinstance(payload, dict):
            raise ValueError("missing snapshot weights")
        original = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                              ensure_ascii=True)
        if sha256(original.encode("ascii")).hexdigest() != envelope.get("sha256"):
            raise ValueError("tampered numerical weight snapshot")
        restored = cls()
        for context, data in payload.items():
            rows = data["weights"]
            seen = data["observed"]
            if (not isinstance(context, str) or not context or
                len(rows) != 3 or any(len(r) != 3 for r in rows) or
                len(seen) != N_KINDS or
                [pair[0] for pair in seen] != list(range(N_KINDS))):
                raise ValueError("malformed numeric world record")
            w = np.asarray(rows, dtype=np.float32)
            if not np.all((w == 0.0) | (w == 1.0)):
                raise ValueError("invalid direct-program weight value")
            for index, v in seen:
                if type(v) is not bool or float(w.flat[index]) != float(v):
                    raise ValueError("snapshot weight and observations disagree")
            restored.weights[context] = w
            restored.observed[context] = {i: v for i, v in seen}
        return restored


class SymbolicRuleControl:
    """Independent set/dict-based exact rule control; never reads weight class."""

    def __init__(self):
        self.seen = {}
        self.true_pairs = {}

    def observe(self, context, relation_pair, observed_consequence):
        if (not isinstance(relation_pair, tuple) or len(relation_pair) != 2 or
                any(type(x) is not int or x not in (0, 1, 2)
                    for x in relation_pair) or
                type(observed_consequence) is not bool):
            raise ValueError("grounded symbolic action consequence required")
        values = self.seen.setdefault(context, {})
        if relation_pair in values and values[relation_pair] != observed_consequence:
            raise ValueError("conflicting symbolic observation")
        values[relation_pair] = observed_consequence
        true_pairs = self.true_pairs.setdefault(context, set())
        if observed_consequence:
            true_pairs.add(relation_pair)
        else:
            true_pairs.discard(relation_pair)

    def complete(self, context):
        return len(self.seen.get(context, ())) == N_KINDS

    def predict_edges(self, context, edges, source, target):
        """Compute path existence directly from graph edges, not shared vectors."""
        if not self.complete(context):
            raise ValueError("symbolic rule table incomplete")
        true = self.true_pairs[context]
        arrivals = {(r, middle) for r, middle, b in edges if b == target}
        for r1, a, middle in edges:
            if a != source:
                continue
            for r2 in range(3):
                if (r1, r2) in true and (r2, middle) in arrivals:
                    return True
        return False


class ConventionalLogistic:
    """Strongly-convex L2 logistic head optimized using exact Newton steps.

    Two preregistered prediction heads reuse the same *fully optimized*
    coefficients: standard pooled-feature logistic and learned max-OR pooled
    per-kind logistic. All training labels are observable singleton support.
    """

    def __init__(self):
        self.coefficients = {}
        self.diagnostics = {}

    @staticmethod
    def _objective(theta, X, y):
        logits = X @ theta
        return float(np.logaddexp(0, logits).mean() - np.dot(y, logits) / len(y)
                     + 0.5 * REGULARIZATION * np.dot(theta, theta))

    def fit(self, context, observations):
        if len(observations) != 10:
            raise ValueError("frozen support contains exactly ten observations")
        X = np.asarray(
            [list(checked_features(f)) + [1.0] for f, _ in observations],
            dtype=np.float64)
        y = np.asarray([float(value) for _, value in observations], dtype=np.float64)
        if (sorted(tuple(row[:N_KINDS]) for row in X) !=
            sorted([tuple(1.0 if i == j else 0.0 for i in range(N_KINDS))
                    for j in range(N_KINDS)] + [(0.0,) * N_KINDS])):
            raise ValueError("support must include all 9 singleton and one zero case")
        if not np.all(np.isin(y, [0., 1.])):
            raise ValueError("unknown supervision class")
        theta = np.zeros(N_KINDS + 1, dtype=np.float64)
        gradient_norm = None
        for step in range(1, MAX_NEWTON_STEPS + 1):
            logits = X @ theta
            probability = 1.0 / (1.0 + np.exp(-np.clip(logits, -40, 40)))
            grad = X.T @ (probability - y) / len(y) + REGULARIZATION * theta
            gradient_norm = float(np.max(np.abs(grad)))
            if gradient_norm <= GRADIENT_TOLERANCE:
                break
            curvature = probability * (1 - probability)
            H = (X.T * curvature) @ X / len(y)
            H += REGULARIZATION * np.eye(N_KINDS + 1)
            direction = np.linalg.solve(H, grad)
            previous = self._objective(theta, X, y)
            slope = float(grad @ direction)
            size = 1.0
            while size >= 2.0**-40:
                proposal = theta - size * direction
                if self._objective(proposal, X, y) <= (
                        previous - 0.0001 * size * slope):
                    theta = proposal
                    break
                size *= 0.5
            else:
                raise FloatingPointError("conventional optimizer line-search failure")
        if gradient_norm is None or gradient_norm > GRADIENT_TOLERANCE:
            raise FloatingPointError("conventional logistic head did not converge")
        fit_accuracy = float(np.mean((X @ theta >= 0) == (y != 0)))
        if fit_accuracy != 1.0:
            raise AssertionError("conventional learned control did not fit support")
        self.coefficients[context] = theta
        self.diagnostics[context] = {
            "newton_steps": step, "gradient_inf_norm": gradient_norm,
            "support_accuracy": fit_accuracy,
            "final_regularized_objective": self._objective(theta, X, y),
        }

    def predict(self, context, features, *, max_pool=False):
        f = checked_features(features)
        theta = self.coefficients[context]
        if max_pool:
            return any(theta[j] + theta[-1] >= 0 for j, on in enumerate(f) if on)
        return float(np.dot(theta[:N_KINDS], f) + theta[-1]) >= 0.0

    def cold_copy(self):
        clone = ConventionalLogistic()
        clone.coefficients = {k: v.copy() for k, v in self.coefficients.items()}
        clone.diagnostics = {k: dict(v) for k, v in self.diagnostics.items()}
        return clone
