"""WSP-163: one bounded public-history residual direct-weight program.

A four-output, four-input classical recursive least-squares (RLS) edit
learns to predict the next public residual from the *previous observed*
public transition. No hidden regime, oracle family label or source-private
data; no original external simulator import/execution. A conventional
independent batch lag-ridge is an essential equal-information comparator.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import math

from direct_weights import ProgrammedPublicDynamics
from public_boundary import PublicTransition

SCHEMA = "yggdrasil.wsp163.public-history-weights.v1"
MAGIC = b"YHW1"
DIMS = 4
MAX_OBSERVATIONS = 2048
MAX_BYTES = 8192


def _dot(xs, ys):
    return math.fsum(x*y for x, y in zip(xs, ys))


def _check_state(base, weights, inverse, seen):
    if type(base) is not ProgrammedPublicDynamics:
        raise ValueError("WSP163_BASE_INVALID")
    if type(seen) is not int or not 0 <= seen <= MAX_OBSERVATIONS:
        raise ValueError("WSP163_ROW_COUNT")
    if (type(weights) not in (list, tuple) or len(weights) != DIMS or
            type(inverse) not in (list, tuple) or len(inverse) != DIMS):
        raise ValueError("WSP163_SHAPE")
    for matrix in (weights, inverse):
        if any(type(row) not in (list, tuple) or len(row) != DIMS for row in matrix):
            raise ValueError("WSP163_SHAPE")
        if any(type(x) not in (float, int) or not math.isfinite(x)
               for row in matrix for x in row):
            raise ValueError("WSP163_NONFINITE")
    for i in range(DIMS):
        if inverse[i][i] <= 0:
            raise ValueError("WSP163_BAD_COVARIANCE")
        for j in range(i):
            if abs(inverse[i][j] - inverse[j][i]) > 1e-10:
                raise ValueError("WSP163_ASYMMETRIC")


def _parse_no_dupes(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("WSP163_DUPLICATE_FIELD")
        out[key] = value
    return out


class PublicHistoryWeights:
    """One immutable base plus one directly updated 4x4 lag residual mapping.

    No per-regime model bank. Every update uses only a previously and newly
    observed public transition in the *same* episode. On first step, history
    is absent and the program must return the static base prediction.
    """

    __slots__ = ("_base", "_w", "_inv", "_seen")

    def __init__(self, trained_static_base):
        if type(trained_static_base) is not ProgrammedPublicDynamics:
            raise ValueError("WSP163_BASE_INVALID")
        self._base = ProgrammedPublicDynamics.restore(trained_static_base.checkpoint())
        self._w = tuple((0.,) * DIMS for _ in range(DIMS))
        self._inv = tuple(tuple(float(i == j) for j in range(DIMS))
                          for i in range(DIMS))
        self._seen = 0

    @classmethod
    def _new(cls, base, weights, inverse, seen):
        _check_state(base, weights, inverse, seen)
        inst = object.__new__(cls)
        inst._base = base
        inst._w = tuple(tuple(row) for row in weights)
        inst._inv = tuple(tuple(row) for row in inverse)
        inst._seen = seen
        return inst

    @property
    def seen(self):
        return self._seen

    def static_predict(self, public_state, chosen_action):
        return self._base.predict(public_state, chosen_action)

    def _previous_residual(self, previous_public):
        if type(previous_public) is not PublicTransition:
            raise ValueError("WSP163_PREVIOUS_PUBLIC_REQUIRED")
        if previous_public.terminated or previous_public.truncated:
            raise ValueError("WSP163_EPISODE_RESET_REQUIRED")
        pred = self._base.predict(previous_public.observation, previous_public.action)
        r = tuple(previous_public.next_observation[k] - pred[k]
                  for k in range(DIMS))
        if not all(map(math.isfinite, r)):
            raise ValueError("WSP163_HISTORY_NONFINITE")
        return r

    def predict(self, public_state, chosen_action, previous_public=None):
        # Both base and historical transition are strictly source-free public.
        base = self._base.predict(public_state, chosen_action)
        if previous_public is None:
            return base
        lag = self._previous_residual(previous_public)
        result = tuple(base[k] + _dot(self._w[k], lag)
                       for k in range(DIMS))
        if not all(map(math.isfinite, result)):
            raise ValueError("WSP163_PREDICT_NONFINITE")
        return result

    def observe_pair(self, previous_public, newly_observed_public):
        if self._seen >= MAX_OBSERVATIONS:
            raise ValueError("WSP163_ROW_CAP")
        z = self._previous_residual(previous_public)
        if type(newly_observed_public) is not PublicTransition:
            raise ValueError("WSP163_NEW_PUBLIC_REQUIRED")
        pred = self._base.predict(
            newly_observed_public.observation, newly_observed_public.action)
        y = tuple(newly_observed_public.next_observation[k] - pred[k]
                  for k in range(DIMS))
        if not all(map(math.isfinite, y)):
            raise ValueError("WSP163_TARGET_NONFINITE")
        q = tuple(_dot(row, z) for row in self._inv)
        denom = 1.0 + _dot(z, q)
        if not math.isfinite(denom) or denom <= 0:
            raise ValueError("WSP163_DENOM_INVALID")
        gain = tuple(x / denom for x in q)
        residual = tuple(y[k] - _dot(self._w[k], z) for k in range(DIMS))
        w = tuple(tuple(self._w[k][j] + gain[j]*residual[k]
                        for j in range(DIMS)) for k in range(DIMS))
        inv = tuple(tuple(self._inv[i][j] - q[i]*q[j]/denom
                          for j in range(DIMS)) for i in range(DIMS))
        return self._new(self._base, w, inv, self._seen + 1)

    def checkpoint(self):
        data = {
            "schema": SCHEMA,
            "base_hex": self._base.checkpoint().hex(),
            "weight": [list(row) for row in self._w],
            "inverse": [list(row) for row in self._inv],
            "seen": self._seen,
        }
        payload = json.dumps(data, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode("ascii")
        raw = MAGIC + len(payload).to_bytes(4, "big") + payload
        raw += hashlib.sha256(raw).digest()
        if len(raw) > MAX_BYTES:
            raise ValueError("WSP163_WIRE_LIMIT")
        return raw

    @classmethod
    def restore(cls, raw):
        if type(raw) is not bytes or not 40 < len(raw) <= MAX_BYTES:
            raise ValueError("WSP163_CHECKPOINT_SIZE")
        if (raw[:4] != MAGIC or
                int.from_bytes(raw[4:8], "big") != len(raw) - 40 or
                not hmac.compare_digest(hashlib.sha256(raw[:-32]).digest(), raw[-32:])):
            raise ValueError("WSP163_CHECKPOINT_DIGEST")
        try:
            obj = json.loads(raw[8:-32].decode("ascii"), object_pairs_hook=_parse_no_dupes)
            if type(obj) is not dict or set(obj) != {
                    "schema", "base_hex", "weight", "inverse", "seen"} or obj["schema"] != SCHEMA:
                raise ValueError("WSP163_CHECKPOINT_SCHEMA")
            base = ProgrammedPublicDynamics.restore(bytes.fromhex(obj["base_hex"]))
            m = cls._new(base, obj["weight"], obj["inverse"], obj["seen"])
        except (ValueError, UnicodeError, OverflowError, TypeError, KeyError) as exc:
            raise ValueError("WSP163_CHECKPOINT_FIELDS") from exc
        if m.checkpoint() != raw:
            raise ValueError("WSP163_CHECKPOINT_NONCANONICAL")
        return m
