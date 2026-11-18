"""WSP161: source-free direct-weight repair orthogonal to witnessed anchors.

This is projected recursive least squares (a conventional constrained
estimator), not a new type of learning. No simulator imports, original-world
actions, oracle dynamics, hidden model-family labels or source control rights.
"""
from __future__ import annotations
import hashlib
import hmac
import json
import math

from direct_weights import (
    ProgrammedPublicDynamics, WIDTH, OUTPUTS, MAX_ROWS,
    _features, _state, _check_internal
)

SCHEMA = "yggdrasil.wsp161.projected-public-weight-repair.v1"
MAGIC = b"YPR1"
MAX_Q = 8
MAX_ANCHORS = 16
MAX_CHECKPOINT_BYTES = 16384
TOL = 1e-10


def _dot(a, b):
    return math.fsum(x*y for x, y in zip(a, b))


def _basis(anchors):
    if type(anchors) not in (tuple, list) or not 1 <= len(anchors) <= MAX_ANCHORS:
        raise ValueError("WSP161_ANCHOR_COUNT")
    basis = []
    for item in anchors:
        if type(item) not in (tuple, list) or len(item) != 2:
            raise ValueError("WSP161_ANCHOR_FORMAT")
        _, x = _features(item[0], item[1])
        v = list(x)
        for _ in range(2):
            for q in basis:
                coeff = _dot(q, v)
                v = [v[i] - coeff*q[i] for i in range(WIDTH)]
        norm = math.sqrt(_dot(v, v))
        if norm > TOL:
            if len(basis) == MAX_Q:
                raise ValueError("WSP161_ANCHOR_RANK_LIMIT")
            basis.append(tuple(a/norm for a in v))
    if not basis:
        raise ValueError("WSP161_EMPTY_ANCHOR_SPAN")
    return tuple(basis)


def _project(x, q_basis):
    v = list(x)
    for _ in range(2):
        for q in q_basis:
            c = _dot(q, v)
            v = [v[i] - c*q[i] for i in range(WIDTH)]
    if not all(math.isfinite(z) for z in v):
        raise ValueError("WSP161_PROJECT_NONFINITE")
    return tuple(v)


def _validate(base, q_basis, weights, inverse, count):
    if not isinstance(base, ProgrammedPublicDynamics):
        raise ValueError("WSP161_BASE_INVALID")
    if type(count) is not int or not 0 <= count <= MAX_ROWS:
        raise ValueError("WSP161_COUNT_INVALID")
    if not 1 <= len(q_basis) <= MAX_Q or any(len(q) != WIDTH for q in q_basis):
        raise ValueError("WSP161_BASIS_INVALID")
    if not all(math.isfinite(x) for q in q_basis for x in q):
        raise ValueError("WSP161_BASIS_NONFINITE")
    for i, q in enumerate(q_basis):
        for j, other in enumerate(q_basis):
            expected = 1.0 if i == j else 0.0
            if abs(_dot(q, other) - expected) > 1e-7:
                raise ValueError("WSP161_BASIS_NOT_ORTHONORMAL")
    _check_internal(weights, inverse)
    for w in weights:
        for q in q_basis:
            if abs(_dot(w, q)) > 1e-7:
                raise ValueError("WSP161_REPAIR_TOUCHES_PROTECTED_SPAN")


class ProjectedWeightRepair:
    """One immutable frozen base plus one constrained residual coefficient edit.

    The new model predicts base(state,action)+residual(projected_features).
    Public anchors define a protected feature subspace; edits cannot alter
    predictions within that span. If an alias contradiction occupies only a
    protected feature direction, no public-distinguishing edit is possible.
    """
    __slots__ = ("_base", "_basis", "_weights", "_inverse", "_seen")

    def __init__(self, base, anchors):
        q_basis = _basis(anchors)
        weights = tuple((0.0,)*WIDTH for _ in range(OUTPUTS))
        inverse = tuple(tuple(float(i == j) for j in range(WIDTH))
                        for i in range(WIDTH))
        _validate(base, q_basis, weights, inverse, 0)
        self._base = ProgrammedPublicDynamics.restore(base.checkpoint())
        self._basis = q_basis
        self._weights = weights
        self._inverse = inverse
        self._seen = 0

    @classmethod
    def _from_state(cls, base, q_basis, weights, inverse, count):
        _validate(base, q_basis, weights, inverse, count)
        obj = object.__new__(cls)
        obj._base = base
        obj._basis = q_basis
        obj._weights = tuple(tuple(row) for row in weights)
        obj._inverse = tuple(tuple(row) for row in inverse)
        obj._seen = count
        return obj

    @property
    def seen(self):
        return self._seen

    @property
    def protected_rank(self):
        return len(self._basis)

    def projected_features(self, observation, action):
        _, phi = _features(observation, action)
        return _project(phi, self._basis)

    def predict(self, observation, action):
        base_out = self._base.predict(observation, action)
        z = self.projected_features(observation, action)
        result = tuple(base_out[k] + _dot(self._weights[k], z)
                       for k in range(OUTPUTS))
        if not all(math.isfinite(v) for v in result):
            raise ValueError("WSP161_PREDICT_NONFINITE")
        return result

    def observe(self, observation, action, next_observation):
        if self._seen >= MAX_ROWS:
            raise ValueError("WSP161_REPAIR_BUDGET")
        state, _ = _features(observation, action)
        nxt = _state(next_observation, "NEXT")
        base_prediction = self._base.predict(state, action)
        y = tuple(nxt[k] - base_prediction[k] for k in range(OUTPUTS))
        if not all(math.isfinite(v) for v in y):
            raise ValueError("WSP161_TARGET_NONFINITE")
        z = self.projected_features(state, action)
        if _dot(z, z) < 1e-20:
            if max(abs(y[k]) for k in range(OUTPUTS)) > 1e-6:
                return self, "UNIDENTIFIABLE"
            return self, "NO_NEW_DIRECTION"
        inv_z = tuple(_dot(row, z) for row in self._inverse)
        denom = 1.0 + _dot(z, inv_z)
        if not math.isfinite(denom) or denom <= 0:
            raise ValueError("WSP161_DENOM_INVALID")
        gain = tuple(q/denom for q in inv_z)
        residual = tuple(y[k] - _dot(self._weights[k], z)
                         for k in range(OUTPUTS))
        weights = tuple(tuple(self._weights[k][j] + gain[j]*residual[k]
                              for j in range(WIDTH)) for k in range(OUTPUTS))
        inverse = tuple(tuple(self._inverse[i][j] - inv_z[i]*inv_z[j]/denom
                              for j in range(WIDTH)) for i in range(WIDTH))
        return self._from_state(self._base, self._basis, weights, inverse,
                                self._seen+1), "UPDATED"

    def checkpoint(self):
        obj = {
            "schema": SCHEMA,
            "base_hex": self._base.checkpoint().hex(),
            "q": [list(row) for row in self._basis],
            "w": [list(row) for row in self._weights],
            "inv": [list(row) for row in self._inverse],
            "seen": self._seen,
        }
        payload = json.dumps(obj, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode("ascii")
        raw = MAGIC + len(payload).to_bytes(4, "big") + payload
        raw += hashlib.sha256(raw).digest()
        if len(raw) > MAX_CHECKPOINT_BYTES:
            raise ValueError("WSP161_CHECKPOINT_LIMIT")
        return raw

    @classmethod
    def restore(cls, raw):
        if type(raw) is not bytes or not 40 < len(raw) <= MAX_CHECKPOINT_BYTES:
            raise ValueError("WSP161_CHECKPOINT_SIZE")
        if (raw[:4] != MAGIC or int.from_bytes(raw[4:8], "big") != len(raw)-40
                or not hmac.compare_digest(hashlib.sha256(raw[:-32]).digest(), raw[-32:])):
            raise ValueError("WSP161_CHECKPOINT_INTEGRITY")
        try:
            obj = json.loads(raw[8:-32].decode("ascii"))
            if type(obj) is not dict or set(obj) != {
                    "schema", "base_hex", "q", "w", "inv", "seen"} or obj["schema"] != SCHEMA:
                raise ValueError("WSP161_CHECKPOINT_SCHEMA")
            base = ProgrammedPublicDynamics.restore(bytes.fromhex(obj["base_hex"]))
            q_basis = tuple(tuple(q) for q in obj["q"])
            weights = tuple(tuple(w) for w in obj["w"])
            inverse = tuple(tuple(row) for row in obj["inv"])
            candidate = cls._from_state(base, q_basis, weights, inverse, obj["seen"])
        except (KeyError, ValueError, TypeError, OverflowError, UnicodeError) as exc:
            raise ValueError("WSP161_CHECKPOINT_FIELDS") from exc
        if candidate.checkpoint() != raw:
            raise ValueError("WSP161_CHECKPOINT_NONCANONICAL")
        return candidate
