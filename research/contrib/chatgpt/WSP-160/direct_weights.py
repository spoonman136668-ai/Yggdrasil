"""WSP160: bounded gradient-free direct numerical weight programming.

SOURCE-FREE DEVELOPMENT: caller must pass only WSP159-whitelisted public
observations and the chosen public action, never a simulator/SCM/info object.
This is classical recursive least squares with a fixed action-conditioned
linear feature grammar, NOT novel causal discovery or scientific superiority.
"""
from __future__ import annotations

import hashlib
import hmac
import math
import struct

MAGIC = b"YDW1"
WIDTH = 10
OUTPUTS = 4
RIDGE = 1.0
MAX_ROWS = 2048
# 4 magic + 2 row count + 100 inverse-covariance doubles + 40 direct
# coefficient doubles + 32 integrity digest.
CHECKPOINT_BYTES = 4 + 2 + 8 * (WIDTH * WIDTH + OUTPUTS * WIDTH) + 32


def _state(raw, label):
    if type(raw) not in (list, tuple) or len(raw) != OUTPUTS:
        raise ValueError("WSP160_" + label + "_SHAPE")
    values = []
    for value in raw:
        if type(value) not in (int, float):
            raise ValueError("WSP160_" + label + "_TYPE")
        try:
            number = float(value)
        except (ValueError, OverflowError):
            raise ValueError("WSP160_" + label + "_RANGE") from None
        if not math.isfinite(number):
            raise ValueError("WSP160_" + label + "_NONFINITE")
        values.append(number)
    return tuple(values)


def _features(obs, action):
    if type(action) is not int or action not in (0, 1):
        raise ValueError("WSP160_ACTION_INVALID")
    state = _state(obs, "OBS")
    sign = 2 * action - 1
    phi = (1.0,) + state + (float(sign),) + tuple(sign * x for x in state)
    if not all(map(math.isfinite, phi)):
        raise ValueError("WSP160_FEATURE_NONFINITE")
    return state, phi


def _check_internal(weights, covariance):
    if (len(weights) != OUTPUTS or any(len(row) != WIDTH for row in weights)
            or len(covariance) != WIDTH or any(len(row) != WIDTH for row in covariance)):
        raise ValueError("WSP160_STATE_SHAPE")
    if not all(math.isfinite(v) for row in (*weights, *covariance) for v in row):
        raise ValueError("WSP160_STATE_NONFINITE")
    for i in range(WIDTH):
        if covariance[i][i] <= 0.0:
            raise ValueError("WSP160_STATE_DIAGONAL")
        for j in range(i):
            if abs(covariance[i][j] - covariance[j][i]) > 1e-10:
                raise ValueError("WSP160_STATE_ASYMMETRIC")


class ProgrammedPublicDynamics:
    """An immutable opt-in direct-written 4x10 coefficient program.

    Every witnessed public transition adjusts a 10x10 inverse normal matrix
    and 40 output weights directly, without any gradient or optimizer call.
    It implements classical RLS, with the regularized normal equations as
    an independent conventional comparator. The feature grammar is authored.
    """

    __slots__ = ("_weights", "_inverse", "_seen")

    def __init__(self):
        self._weights = tuple((0.0,) * WIDTH for _ in range(OUTPUTS))
        self._inverse = tuple(tuple(1.0 / RIDGE if i == j else 0.0
                                    for j in range(WIDTH)) for i in range(WIDTH))
        self._seen = 0

    @classmethod
    def _from_state(cls, weights, covariance, seen):
        obj = object.__new__(cls)
        obj._weights = tuple(tuple(row) for row in weights)
        obj._inverse = tuple(tuple(row) for row in covariance)
        obj._seen = seen
        return obj

    @property
    def seen(self):
        return self._seen

    def weights(self):
        return tuple(tuple(row) for row in self._weights)

    def predict(self, observation, action):
        state, phi = _features(observation, action)
        out = tuple(state[k] + math.fsum(self._weights[k][j] * phi[j]
                                        for j in range(WIDTH)) for k in range(OUTPUTS))
        if not all(map(math.isfinite, out)):
            raise ValueError("WSP160_PREDICTION_NONFINITE")
        return out

    def observe(self, observation, action, next_observation):
        """Apply exactly one source-blind public witness, return new model.

        The calling boundary must first validate the entire upstream record
        using WSP159 PublicTransition.from_public(...). No private source
        access or family label is possible through this method signature.
        """
        if self._seen >= MAX_ROWS:
            raise ValueError("WSP160_OBSERVATION_CAP")
        state, phi = _features(observation, action)
        nxt = _state(next_observation, "NEXT")
        y = tuple(nxt[i] - state[i] for i in range(OUTPUTS))
        if not all(map(math.isfinite, y)):
            raise ValueError("WSP160_DELTA_NONFINITE")
        q = tuple(math.fsum(self._inverse[i][j] * phi[j]
                            for j in range(WIDTH)) for i in range(WIDTH))
        denom = 1.0 + math.fsum(phi[j] * q[j] for j in range(WIDTH))
        if not math.isfinite(denom) or denom <= 0.0:
            raise ValueError("WSP160_UPDATE_DENOM")
        gain = tuple(v / denom for v in q)
        residual = tuple(y[i] - math.fsum(self._weights[i][j] * phi[j]
                                          for j in range(WIDTH))
                         for i in range(OUTPUTS))
        weights = tuple(tuple(self._weights[i][j] + gain[j] * residual[i]
                               for j in range(WIDTH)) for i in range(OUTPUTS))
        inverse = tuple(tuple(self._inverse[i][j] - q[i] * q[j] / denom
                               for j in range(WIDTH)) for i in range(WIDTH))
        _check_internal(weights, inverse)
        return self._from_state(weights, inverse, self._seen + 1)

    def checkpoint(self):
        values = tuple(v for row in self._inverse for v in row) + tuple(
            v for row in self._weights for v in row)
        payload = struct.pack(">4sH" + "d" * len(values), MAGIC, self._seen, *values)
        return payload + hashlib.sha256(payload).digest()

    @classmethod
    def restore(cls, raw):
        if (type(raw) is not bytes or len(raw) != CHECKPOINT_BYTES
                or raw[:4] != MAGIC or
                not hmac.compare_digest(hashlib.sha256(raw[:-32]).digest(), raw[-32:])):
            raise ValueError("WSP160_CHECKPOINT_INTEGRITY")
        unpacked = struct.unpack(">4sH" + "d" * (WIDTH * WIDTH + OUTPUTS * WIDTH),
                                 raw[:-32])
        seen = unpacked[1]
        if seen > MAX_ROWS:
            raise ValueError("WSP160_CHECKPOINT_CAP")
        flat = unpacked[2:]
        inverse = tuple(tuple(flat[i * WIDTH:(i+1) * WIDTH]) for i in range(WIDTH))
        start = WIDTH * WIDTH
        weights = tuple(tuple(flat[start + i * WIDTH:start + (i+1) * WIDTH])
                        for i in range(OUTPUTS))
        _check_internal(weights, inverse)
        obj = cls._from_state(weights, inverse, seen)
        if obj.checkpoint() != raw:
            raise ValueError("WSP160_CHECKPOINT_CANONICAL")
        return obj
