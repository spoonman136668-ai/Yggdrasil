"""MH-08 source-free three-factor Hebbian mechanism; NOT trained Yggdrasil.

No world generator, source import, regime/phase key, bank oracle, protected
first use, or accepted-model mutation. Tests use authored fixed numeric packets.
"""
from __future__ import annotations

import json
import math

SCHEMA = "yggdrasil.mh08.local-plasticity.eng.v1"
N_FEATURES, N_HEADS = 4, 3
MAX_WEIGHT, MAX_IMPORTANCE = 4.0, 16.0
LR, IMPORTANCE_RATE = 0.125, 0.125


def _numbers(values: object, count: int, limit: float) -> tuple[float, ...]:
    if not isinstance(values, (tuple, list)) or len(values) != count:
        raise ValueError("MH08_BAD_VECTOR_SHAPE")
    result = []
    for value in values:
        if type(value) not in (int, float) or not math.isfinite(value) or abs(value) > limit:
            raise ValueError("MH08_BAD_VECTOR_VALUE")
        result.append(float(value))
    return tuple(result)


class LocalPlasticity:
    """Deterministic standalone online three-factor rule, source blind.

    Eligibility e_ji = x_i * (1 + 0.5*tanh(yhat_j)); the causal
    post-feedback modulator m_j = clamp(target_j-yhat_j,-2,2).
    Delta w_ji = LR * e_ji * m_j / (1+importance_ji) (if protected),
    clipped to [-4,4]. Importance increments from witnessed local activity
    only AFTER the update. No fitting claim or bank selection is made.
    """

    def __init__(self, *, metaplastic: bool = True, modulated: bool = True):
        if type(metaplastic) is not bool or type(modulated) is not bool:
            raise ValueError("MH08_BAD_ABLATION_FLAG")
        self.metaplastic = metaplastic
        self.modulated = modulated
        self.weights = [[0.0] * N_FEATURES for _ in range(N_HEADS)]
        self.importance = [[0.0] * N_FEATURES for _ in range(N_HEADS)]
        self.next_event_id = 0
        self._pending = None

    def predict(self, features: object) -> tuple[float, ...]:
        x = _numbers(features, N_FEATURES, 1.0)
        return tuple(sum(w * xi for w, xi in zip(row, x)) for row in self.weights)

    def begin(self, event_id: int, features: object) -> tuple[float, ...]:
        if self._pending is not None:
            raise ValueError("MH08_UNFINISHED_EVENT")
        if type(event_id) is not int or event_id != self.next_event_id:
            raise ValueError("MH08_OUT_OF_ORDER_EVENT")
        x = _numbers(features, N_FEATURES, 1.0)
        forecast = self.predict(x)
        self._pending = (event_id, x, forecast)
        return forecast

    def feedback(self, event_id: int, outcome: object) -> None:
        if self._pending is None or type(event_id) is not int or event_id != self._pending[0]:
            raise ValueError("MH08_FEEDBACK_WITHOUT_MATCHED_FORECAST")
        target = _numbers(outcome, N_HEADS, 2.0)
        _, x, yhat = self._pending
        # Nothing changes on a malformed outcome, allowing valid retry.
        if self.modulated:
            for j in range(N_HEADS):
                local_post = 1.0 + 0.5 * math.tanh(yhat[j])
                consequence = max(-2.0, min(2.0, target[j] - yhat[j]))
                for i in range(N_FEATURES):
                    eligibility = x[i] * local_post
                    protect = 1.0 + self.importance[j][i] if self.metaplastic else 1.0
                    delta = LR * eligibility * consequence / protect
                    self.weights[j][i] = max(-MAX_WEIGHT, min(MAX_WEIGHT, self.weights[j][i] + delta))
                    if self.metaplastic:
                        self.importance[j][i] = min(MAX_IMPORTANCE, self.importance[j][i] + IMPORTANCE_RATE * abs(eligibility))
        self._pending = None
        self.next_event_id += 1

    def checkpoint(self) -> bytes:
        if self._pending is not None:
            raise ValueError("MH08_MID_EVENT_SNAPSHOT")
        record = {
            "schema": SCHEMA,
            "metaplastic": self.metaplastic,
            "modulated": self.modulated,
            "next_event_id": self.next_event_id,
            "weights": self.weights,
            "importance": self.importance,
        }
        return json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")

    @classmethod
    def restore(cls, raw: bytes) -> "LocalPlasticity":
        if type(raw) is not bytes or len(raw) > 8192:
            raise ValueError("MH08_INVALID_CHECKPOINT")
        try:
            record = json.loads(raw.decode("ascii"))
        except (ValueError, UnicodeError) as exc:
            raise ValueError("MH08_INVALID_CHECKPOINT") from exc
        if type(record) is not dict or set(record) != {"schema", "metaplastic", "modulated", "next_event_id", "weights", "importance"} or record["schema"] != SCHEMA:
            raise ValueError("MH08_INVALID_CHECKPOINT_SCHEMA")
        if type(record["next_event_id"]) is not int or not (0 <= record["next_event_id"] <= 10**8):
            raise ValueError("MH08_INVALID_CHECKPOINT_CLOCK")
        state = cls(metaplastic=record["metaplastic"], modulated=record["modulated"])
        if type(record["weights"]) is not list or type(record["importance"]) is not list or len(record["weights"]) != N_HEADS or len(record["importance"]) != N_HEADS:
            raise ValueError("MH08_INVALID_CHECKPOINT_LAYOUT")
        state.weights = [list(_numbers(row, N_FEATURES, MAX_WEIGHT)) for row in record["weights"]]
        state.importance = [list(_numbers(row, N_FEATURES, MAX_IMPORTANCE)) for row in record["importance"]]
        if any(v < 0 for row in state.importance for v in row) or (not state.metaplastic and any(v != 0 for row in state.importance for v in row)):
            raise ValueError("MH08_INVALID_IMPORTANCE")
        if not state.modulated and any(v != 0 for row in state.weights for v in row):
            raise ValueError("MH08_INVALID_ABLATION_STATE")
        state.next_event_id = record["next_event_id"]
        if state.checkpoint() != raw:
            raise ValueError("MH08_NONCANONICAL_CHECKPOINT")
        return state
