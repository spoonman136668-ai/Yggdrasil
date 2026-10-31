"""MR32 diagonal Bayesian linear consequence predictor.

A conventional conjugate Gaussian model with independent coefficient priors
for each public feature/action coordinate. It is an intentionally transparent
baseline, not a full Bayesian network or optimal model-based agent.
"""
from __future__ import annotations
import hashlib
import json
import math
from typing import Iterable
from residual_belief import FEATURES, TARGETS, Prediction, _vector

ACTIONS = 3
DIM = FEATURES + ACTIONS + 1
PRIOR_PRECISION = 1.0
OBSERVATION_VARIANCE = 0.25


class DiagonalBayesControl:
    def __init__(self):
        # Independent Normal-Gaussian posterior for each output/feature weight.
        self.precision = [[PRIOR_PRECISION] * DIM for _ in range(TARGETS)]
        self.weighted_sum = [[0.0] * DIM for _ in range(TARGETS)]
        self.steps = 0
        self.pending = None

    @staticmethod
    def _phi(features: Iterable[float], selected_action: int) -> tuple[float, ...]:
        x = _vector(features, FEATURES, "FEATURES")
        if isinstance(selected_action, bool) or selected_action not in range(ACTIONS):
            raise ValueError("SELECTED_ACTION_OUT_OF_RANGE")
        return (1.0,) + x + tuple(1.0 if i == selected_action else 0.0 for i in range(ACTIONS))

    def predict(self, public_features: Iterable[float], selected_action: int) -> Prediction:
        if self.pending is not None:
            raise RuntimeError("PENDING_OUTCOME_MUST_BE_RESOLVED")
        phi = self._phi(public_features, selected_action)
        means = []
        variance = OBSERVATION_VARIANCE
        for k in range(TARGETS):
            row = self.precision[k]
            coeff = [self.weighted_sum[k][j] / row[j] for j in range(DIM)]
            means.append(max(-1.0, min(1.0, sum(a*b for a, b in zip(coeff, phi)))))
            variance += sum((phi[j] * phi[j]) / row[j] for j in range(DIM)) / TARGETS
        prediction = Prediction(tuple(means), math.sqrt(max(0.0, variance)), self.steps > 0)
        self.pending = phi
        return prediction

    def observe_selected_outcome(self, actual_outcome: Iterable[float]) -> None:
        if self.pending is None:
            raise RuntimeError("NO_PENDING_SELECTED_ACTION")
        y = _vector(actual_outcome, TARGETS, "OUTCOME")
        phi = self.pending
        self.pending = None
        inv_noise = 1.0 / OBSERVATION_VARIANCE
        for k, target in enumerate(y):
            for j, feature in enumerate(phi):
                self.precision[k][j] += feature * feature * inv_noise
                self.weighted_sum[k][j] += feature * target * inv_noise
        self.steps += 1

    def snapshot(self) -> bytes:
        if self.pending is not None:
            raise RuntimeError("CANNOT_CHECKPOINT_PENDING_OUTCOME")
        payload = {
            "schema": "yggdrasil.mr32.diagonal-bayes.v1",
            "dimensions": {"features": FEATURES, "actions": ACTIONS, "outputs": TARGETS, "parameters": DIM},
            "prior_precision": PRIOR_PRECISION,
            "observation_variance": OBSERVATION_VARIANCE,
            "precision": self.precision,
            "weighted_sum": self.weighted_sum,
            "steps": self.steps,
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        envelope = {"payload": payload, "sha256": hashlib.sha256(canonical).hexdigest()}
        return json.dumps(envelope, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()

    @classmethod
    def restore(cls, raw: bytes) -> "DiagonalBayesControl":
        try:
            envelope = json.loads(raw.decode("utf-8"))
            payload = envelope["payload"]
            canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        except Exception as exc:
            raise ValueError("CHECKPOINT_FORMAT") from exc
        if hashlib.sha256(canonical).hexdigest() != envelope.get("sha256"):
            raise ValueError("CHECKPOINT_HASH_MISMATCH")
        expected = {"features": FEATURES, "actions": ACTIONS, "outputs": TARGETS, "parameters": DIM}
        if payload.get("schema") != "yggdrasil.mr32.diagonal-bayes.v1" or payload.get("dimensions") != expected:
            raise ValueError("CHECKPOINT_SCHEMA_OR_DIMENSIONS")
        if payload.get("prior_precision") != PRIOR_PRECISION or payload.get("observation_variance") != OBSERVATION_VARIANCE:
            raise ValueError("CHECKPOINT_HYPERPARAMETERS")
        precision = payload.get("precision")
        weighted = payload.get("weighted_sum")
        if not isinstance(precision, list) or len(precision) != TARGETS or not isinstance(weighted, list) or len(weighted) != TARGETS:
            raise ValueError("CHECKPOINT_ROWS")
        model = cls()
        p_rows, w_rows = [], []
        for p, w in zip(precision, weighted):
            if not isinstance(p, list) or len(p) != DIM or not isinstance(w, list) or len(w) != DIM:
                raise ValueError("CHECKPOINT_ROW_DIMENSION")
            try:
                p_row = [float(v) for v in p]
                w_row = [float(v) for v in w]
            except (TypeError, ValueError) as exc:
                raise ValueError("CHECKPOINT_ROW_NUMERIC") from exc
            if not all(math.isfinite(v) and v > 0 for v in p_row):
                raise ValueError("CHECKPOINT_PRECISION")
            if not all(math.isfinite(v) for v in w_row):
                raise ValueError("CHECKPOINT_WEIGHTED_SUM")
            p_rows.append(p_row)
            w_rows.append(w_row)
        if not isinstance(payload.get("steps"), int) or payload["steps"] < 0:
            raise ValueError("CHECKPOINT_STEPS")
        model.precision, model.weighted_sum, model.steps = p_rows, w_rows, payload["steps"]
        return model

    def state_bytes(self) -> bytes:
        return self.snapshot()
