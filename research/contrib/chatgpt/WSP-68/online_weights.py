"""WSP68: direct experience -> online edits of real neural readout weights.

This is NOT a symbolic compiler. No causal hypothesis grammar, predicate
enumeration, hidden physical role, source import, or target lookup. A fixed,
source-independent random 8->32 ReLU feature map feeds a 41-dimensional
skip-connected neural readout with 4 real-valued sensor outputs. A rank-one
recursive ridge least-squares update edits all four readout weight rows after
EACH charged public action/consequence. Inference uses only learned neural
matrices and their covariance-based epistemic abstention, never training rows.

Readout-only edits limit expressivity: frozen hidden features do not learn.
A closed-form converged same-feature batch control tests numerical correctness,
not independent neural superiority. No gradients or token objectives.
"""
from __future__ import annotations
from hashlib import sha256
from itertools import product
from math import isfinite
from random import Random
import json

STATES = tuple(product((0, 1), repeat=4))
ACTIONS = tuple(range(4))
INPUTS = 8
HIDDEN = 32
FEATURES = 1 + INPUTS + HIDDEN
OUTPUTS = 4
RIDGE_LAMBDA = 0.5
FEATURE_SEED = 68182026
MARGIN_THRESHOLD = 0.27
LEVERAGE_THRESHOLD = 2.0
TRAIN_CHARGES = 96
SNAPSHOT_CAP = 1000000


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def check(state, action):
    if type(state) is not tuple or state not in STATES or (
            type(action) is not int or action not in ACTIONS):
        raise ValueError("invalid public state/action")
    return state


def fixed_feature_weights():
    """Untrained, source-independent numeric ReLU feature network."""
    r = Random(FEATURE_SEED)
    w = [[r.uniform(-0.65, 0.65) for _ in range(INPUTS)]
         for _ in range(HIDDEN)]
    b = [r.uniform(-0.3, 0.3) for _ in range(HIDDEN)]
    return w, b


def neural_features(w_hidden, b_hidden, state, action):
    check(state, action)
    x = [float(v) for v in state] + [
        float(action == j) for j in ACTIONS
    ]
    relu = [max(0.0, sum(a*v for a, v in zip(row, x)) + bias)
            for row, bias in zip(w_hidden, b_hidden)]
    return [1.0] + x + relu


def _check_mat(matrix, rows, cols):
    if type(matrix) is not list or len(matrix) != rows:
        raise ValueError("invalid weight matrix height")
    for row in matrix:
        if (type(row) is not list or len(row) != cols or
                any(type(v) not in (float, int) or not isfinite(v)
                    for v in row)):
            raise ValueError("invalid/nonfinite neural matrix")


class OnlineNeuralWeightEditor:
    gradient_updates = 0

    def __init__(self):
        self.w_hidden, self.b_hidden = fixed_feature_weights()
        self.w_readout = [[0.0] * FEATURES for _ in range(OUTPUTS)]
        self.inverse_covariance = [
            [((1.0 / RIDGE_LAMBDA) if i == j else 0.0)
             for j in range(FEATURES)] for i in range(FEATURES)
        ]
        self.charged_actions = 0
        # The training-session continuity guard is transient; it is NOT
        # copied into the inference snapshot, which contains only numeric
        # neural parameters/uncertainty state.
        self.current = (0, 0, 0, 0)

    def _features(self, state, action):
        return neural_features(self.w_hidden, self.b_hidden, state, action)

    def _forward(self, state, action):
        f = self._features(state, action)
        raw = tuple(sum(row[k] * f[k] for k in range(FEATURES))
                    for row in self.w_readout)
        cov_f = [sum(self.inverse_covariance[i][k] * f[k]
                     for k in range(FEATURES)) for i in range(FEATURES)]
        leverage = sum(f[i] * cov_f[i] for i in range(FEATURES))
        if not isfinite(leverage) or leverage < -1e-7:
            raise ArithmeticError("bad learned uncertainty covariance")
        return raw, max(0.0, leverage)

    def raw(self, state, action):
        return self._forward(state, action)[0]

    def leverage(self, state, action):
        return self._forward(state, action)[1]

    def predict(self, state, action, force=False):
        if type(force) is not bool:
            raise ValueError("invalid prediction mode")
        raw, leverage = self._forward(state, action)
        if not force and (leverage > LEVERAGE_THRESHOLD or
                          any(abs(v - 0.5) < MARGIN_THRESHOLD for v in raw)):
            return None
        return tuple(int(v >= 0.5) for v in raw)

    def charge(self, observation):
        before = observation.before
        action = observation.action
        after = observation.after
        check(before, action)
        check(after, action)
        if (before != self.current or
                type(observation.action_cost) is not int or
                observation.action_cost != 1 or
                self.charged_actions >= TRAIN_CHARGES):
            raise ValueError("illegal no-reset physical observation/charge")
        f = self._features(before, action)
        cov_f = [sum(self.inverse_covariance[i][j] * f[j]
                     for j in range(FEATURES)) for i in range(FEATURES)]
        den = 1.0 + sum(f[i] * cov_f[i] for i in range(FEATURES))
        if not isfinite(den) or den <= 0:
            raise ArithmeticError("unstable numerical edit denominator")
        gain = [v / den for v in cov_f]
        for j in range(OUTPUTS):
            predicted = sum(self.w_readout[j][k] * f[k]
                            for k in range(FEATURES))
            residual = after[j] - predicted
            for k in range(FEATURES):
                self.w_readout[j][k] += residual * gain[k]
        for i in range(FEATURES):
            for j in range(FEATURES):
                self.inverse_covariance[i][j] -= gain[i] * cov_f[j]
        self.charged_actions += 1
        self.current = after

    def learned_weights_changed(self, earlier):
        return sum(abs(self.w_readout[j][k] - earlier.w_readout[j][k]) > 1e-12
                   for j in range(OUTPUTS) for k in range(FEATURES))

    def parameter_count(self):
        return HIDDEN * (INPUTS + 1) + OUTPUTS * FEATURES

    def nonzero_learned_weights(self):
        return sum(abs(v) > 1e-12 for row in self.w_readout for v in row)

    def snapshot(self):
        """No charged experience ledger and no symbolic rules stored here."""
        self._validate()
        payload = {
            "schema": "wsp68.online-neural-matrices.v1",
            "w_hidden": self.w_hidden,
            "b_hidden": self.b_hidden,
            "w_readout": self.w_readout,
            "inverse_covariance": self.inverse_covariance,
            "charged_actions": self.charged_actions
        }
        fingerprint = sha256(canonical(payload).encode("ascii")).hexdigest()
        result = canonical({"payload": payload, "sha256": fingerprint})
        if len(result) > SNAPSHOT_CAP:
            raise OverflowError("neural snapshot size limit")
        return result

    def _validate(self):
        _check_mat(self.w_hidden, HIDDEN, INPUTS)
        _check_mat(self.w_readout, OUTPUTS, FEATURES)
        _check_mat(self.inverse_covariance, FEATURES, FEATURES)
        if (type(self.b_hidden) is not list or len(self.b_hidden) != HIDDEN or
                any(type(v) not in (float, int) or not isfinite(v)
                    for v in self.b_hidden)):
            raise ValueError("invalid neural biases")
        if (type(self.charged_actions) is not int or
                not 0 <= self.charged_actions <= TRAIN_CHARGES):
            raise ValueError("invalid number of charged actions")

    @classmethod
    def restore(cls, raw):
        if type(raw) is not str or len(raw) > SNAPSHOT_CAP:
            raise ValueError("bad neural snapshot")
        try:
            envelope = json.loads(raw)
            if type(envelope) is not dict or set(envelope) != {"payload", "sha256"}:
                raise ValueError("bad snapshot envelope")
            p = envelope["payload"]
            if type(p) is not dict or set(p) != {
                "schema", "w_hidden", "b_hidden", "w_readout",
                "inverse_covariance", "charged_actions"
            } or p["schema"] != "wsp68.online-neural-matrices.v1":
                raise ValueError("bad snapshot schema")
            if (sha256(canonical(p).encode("ascii")).hexdigest() !=
                    envelope["sha256"]):
                raise ValueError("snapshot checksum violation")
            model = cls()
            model.w_hidden = p["w_hidden"]
            model.b_hidden = p["b_hidden"]
            model.w_readout = p["w_readout"]
            model.inverse_covariance = p["inverse_covariance"]
            model.charged_actions = p["charged_actions"]
            model._validate()
            if model.snapshot() != raw:
                raise ValueError("noncanonical neural weights")
            # Restored object is for inference, not charge updates:
            # its transient state is not a physical session credential.
            return model
        except (ValueError, TypeError, KeyError, UnicodeError,
                json.JSONDecodeError, OverflowError) as e:
            raise ValueError("invalid or tampered weight snapshot") from e

    def weight_bytes(self):
        return len(self.snapshot().encode("ascii"))
