"""Action-feature Bayesian linear control with explicit interaction terms.

Conjugate diagonal Normal-Gaussian posterior over bias, public features,
action indicators, and feature-by-action interactions. Conventional baseline;
not a causal graph learner or planner.
"""
from __future__ import annotations
import hashlib
import json
import math
from typing import Iterable
from residual_belief import FEATURES, TARGETS, Prediction, _vector

ACTIONS = 3
DIM = 1 + FEATURES + ACTIONS + FEATURES * ACTIONS
PRIOR_PRECISION = 1.0
OBSERVATION_VARIANCE = 0.25


class InteractionBayesControl:
    def __init__(self):
        self.precision = [[PRIOR_PRECISION] * DIM for _ in range(TARGETS)]
        self.weighted_sum = [[0.0] * DIM for _ in range(TARGETS)]
        self.steps = 0
        self.pending = None

    @staticmethod
    def _phi(features: Iterable[float], selected_action: int) -> tuple[float, ...]:
        x = _vector(features, FEATURES, "FEATURES")
        if isinstance(selected_action, bool) or selected_action not in range(ACTIONS):
            raise ValueError("SELECTED_ACTION_OUT_OF_RANGE")
        action = tuple(1.0 if i == selected_action else 0.0 for i in range(ACTIONS))
        interaction = tuple(value * flag for flag in action for value in x)
        return (1.0,) + x + action + interaction

    def predict(self, public_features: Iterable[float], selected_action: int) -> Prediction:
        if self.pending is not None:
            raise RuntimeError("PENDING_OUTCOME_MUST_BE_RESOLVED")
        phi = self._phi(public_features, selected_action)
        means, variance = [], OBSERVATION_VARIANCE
        for k in range(TARGETS):
            precisions = self.precision[k]
            coeff = [self.weighted_sum[k][j] / precisions[j] for j in range(DIM)]
            means.append(max(-1.0, min(1.0, sum(a*b for a,b in zip(coeff,phi)))))
            variance += sum(phi[j]*phi[j]/precisions[j] for j in range(DIM)) / TARGETS
        result = Prediction(tuple(means), math.sqrt(max(0.0,variance)), self.steps > 0)
        self.pending = phi
        return result

    def observe_selected_outcome(self, actual_outcome: Iterable[float]) -> None:
        if self.pending is None:
            raise RuntimeError("NO_PENDING_SELECTED_ACTION")
        y = _vector(actual_outcome, TARGETS, "OUTCOME")
        phi = self.pending
        self.pending = None
        inv_noise = 1.0 / OBSERVATION_VARIANCE
        for k, target in enumerate(y):
            for j, value in enumerate(phi):
                self.precision[k][j] += value*value*inv_noise
                self.weighted_sum[k][j] += value*target*inv_noise
        self.steps += 1

    def snapshot(self) -> bytes:
        if self.pending is not None:
            raise RuntimeError("CANNOT_CHECKPOINT_PENDING_OUTCOME")
        payload = {
            "schema":"yggdrasil.mr32.interaction-bayes.v1",
            "dimensions":{"features":FEATURES,"actions":ACTIONS,"outputs":TARGETS,"parameters":DIM},
            "prior_precision":PRIOR_PRECISION,"observation_variance":OBSERVATION_VARIANCE,
            "precision":self.precision,"weighted_sum":self.weighted_sum,"steps":self.steps
        }
        canonical=json.dumps(payload,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
        return json.dumps({"payload":payload,"sha256":hashlib.sha256(canonical).hexdigest()},
                          sort_keys=True,separators=(",",":"),allow_nan=False).encode()

    @classmethod
    def restore(cls, raw: bytes) -> "InteractionBayesControl":
        try:
            envelope=json.loads(raw.decode("utf-8"));payload=envelope["payload"]
            canonical=json.dumps(payload,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
        except Exception as exc:
            raise ValueError("CHECKPOINT_FORMAT") from exc
        if hashlib.sha256(canonical).hexdigest()!=envelope.get("sha256"):
            raise ValueError("CHECKPOINT_HASH_MISMATCH")
        dims={"features":FEATURES,"actions":ACTIONS,"outputs":TARGETS,"parameters":DIM}
        if payload.get("schema")!="yggdrasil.mr32.interaction-bayes.v1" or payload.get("dimensions")!=dims:
            raise ValueError("CHECKPOINT_SCHEMA_OR_DIMENSIONS")
        if payload.get("prior_precision")!=PRIOR_PRECISION or payload.get("observation_variance")!=OBSERVATION_VARIANCE:
            raise ValueError("CHECKPOINT_HYPERPARAMETERS")
        p,w=payload.get("precision"),payload.get("weighted_sum")
        if not isinstance(p,list) or len(p)!=TARGETS or not isinstance(w,list) or len(w)!=TARGETS:
            raise ValueError("CHECKPOINT_ROWS")
        pr,ws=[],[]
        for prow,wrow in zip(p,w):
            if not isinstance(prow,list) or len(prow)!=DIM or not isinstance(wrow,list) or len(wrow)!=DIM:
                raise ValueError("CHECKPOINT_ROW_DIMENSION")
            try:
                pp=[float(v) for v in prow];ww=[float(v) for v in wrow]
            except (TypeError,ValueError) as exc:
                raise ValueError("CHECKPOINT_ROW_NUMERIC") from exc
            if not all(math.isfinite(v) and v>0 for v in pp):
                raise ValueError("CHECKPOINT_PRECISION")
            if not all(math.isfinite(v) for v in ww):
                raise ValueError("CHECKPOINT_WEIGHTED_SUM")
            pr.append(pp);ws.append(ww)
        steps=payload.get("steps")
        if not isinstance(steps,int) or steps<0:
            raise ValueError("CHECKPOINT_STEPS")
        model=cls();model.precision=pr;model.weighted_sum=ws;model.steps=steps
        return model

    def state_bytes(self) -> bytes:
        return self.snapshot()
