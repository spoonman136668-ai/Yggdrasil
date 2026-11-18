"""WSP-182: source-free explicit causal edge programming and sparse memory repair.

Identifies a 4-variable *linear additive* lower-triangular mechanism using
matched-public-exogenous interventional contrasts. Matched-exogenous pairs are
an artificial DEVELOPMENT input capability, NOT automatically available from
any genuine upstream world; no protected source imports or first-use calls.
No model receives source adjacency, graph labels, source seed or future rows.
A fully trained conventional inverse-response estimator has identical data
and must tie: structural recovery alone does not prove scientific superiority.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import hmac
import json
import math
import re

N = 4
MAGIC = b"YCS1"
SCHEMA = "yggdrasil.wsp182.direct-causal-edges.v1"
MAX_WIRE = 16384
MAX_NUM = 1 << 40
MAX_DEN = 1 << 64


def _value(x: object) -> Fraction:
    if type(x) is Fraction:
        v = x
    elif type(x) is int:
        v = Fraction(x)
    elif type(x) is float and math.isfinite(x):
        v = Fraction.from_float(x)
    else:
        raise ValueError("WSP182_PUBLIC_RATIONAL")
    if abs(v.numerator) > MAX_NUM * v.denominator or v.denominator > MAX_DEN:
        raise ValueError("WSP182_VALUE_BOUNDS")
    return v


def _vec(x: object) -> tuple[Fraction, ...]:
    if type(x) not in (tuple, list) or len(x) != N:
        raise ValueError("WSP182_PUBLIC_VECTOR")
    return tuple(_value(v) for v in x)


def _ratio(v: Fraction) -> str:
    return str(v.numerator) + "/" + str(v.denominator)


def _parse(s: object) -> Fraction:
    if type(s) is not str or len(s) > 160 or re.fullmatch(
            r"-?(?:0|[1-9][0-9]*)/[1-9][0-9]*", s) is None:
        raise ValueError("WSP182_RATIO")
    n, d = s.split("/")
    v = Fraction(int(n), int(d))
    if _ratio(v) != s:
        raise ValueError("WSP182_NONCANONICAL_RATIO")
    return _value(v)


@dataclass(frozen=True, slots=True)
class PublicContrast:
    """One already observed matched-exogenous do-effect; NOT an action request."""

    action: int
    baseline: tuple[Fraction, ...]
    intervened: tuple[Fraction, ...]
    commanded_delta: Fraction

    def __post_init__(self):
        if type(self.action) is not int or not 0 <= self.action < N:
            raise ValueError("WSP182_PUBLIC_ACTION")
        a, b, d = _vec(self.baseline), _vec(self.intervened), _value(self.commanded_delta)
        if not d or b[self.action] - a[self.action] != d:
            raise ValueError("WSP182_PUBLIC_INTERVENTION")
        if any(b[k] != a[k] for k in range(self.action)):
            raise ValueError("WSP182_FUTURE_TO_PAST")
        object.__setattr__(self, "baseline", a)
        object.__setattr__(self, "intervened", b)
        object.__setattr__(self, "commanded_delta", d)

    def response(self) -> tuple[Fraction, ...]:
        d = self.commanded_delta
        return tuple((b-a)/d for a, b in zip(self.baseline, self.intervened))


@dataclass(frozen=True, slots=True)
class CausalEdges:
    """Direct weights A[j,i] in x[j] = sum_{i<j} A[j,i]x[i] + u[j]."""

    weights: tuple[tuple[Fraction, ...], ...]

    def __post_init__(self):
        if type(self.weights) not in (tuple, list) or len(self.weights) != N:
            raise ValueError("WSP182_GRAPH_SHAPE")
        matrix = tuple(_vec(row) for row in self.weights)
        if any(matrix[j][i] != 0 for j in range(N) for i in range(j, N)):
            raise ValueError("WSP182_CYCLIC_OR_DIAGONAL")
        object.__setattr__(self, "weights", matrix)

    @classmethod
    def from_public_fit(cls, contrasts: object) -> "CausalEdges":
        """Two independent public contrast strengths per intervention.

        A duplicated action at different strength provides a nonlinearity /
        nonstationarity negative control. No FIT record reveals source graph.
        """
        if type(contrasts) not in (tuple, list) or len(contrasts) != 2*N:
            raise ValueError("WSP182_FIT_EIGHT_REQUIRED")
        buckets = {i: [] for i in range(N)}
        for c in contrasts:
            if type(c) is not PublicContrast:
                raise ValueError("WSP182_PUBLIC_WITNESS_REQUIRED")
            buckets[c.action].append(c)
        total = [[Fraction(int(j == i)) for i in range(N)] for j in range(N)]
        for i in range(N):
            pairs = buckets[i]
            if len(pairs) != 2 or pairs[0].commanded_delta == pairs[1].commanded_delta:
                raise ValueError("WSP182_TWO_LEVELS")
            a, b = pairs[0].response(), pairs[1].response()
            if a != b:
                raise ValueError("WSP182_NONLINEAR_OR_DRIFT")
            if a[i] != 1 or any(a[j] != 0 for j in range(i)):
                raise ValueError("WSP182_CONTRAST_CUSTODY")
            for j in range(i+1,N):
                total[j][i] = a[j]
        # Invert lower-triangular total-effects map (I-A)^-1 without ever
        # using the evaluator's true graph. Descending intervention index
        # recovers each DIRECT edge after subtracting known indirect paths.
        direct = [[Fraction(0) for _ in range(N)] for _ in range(N)]
        for j in range(1,N):
            for i in range(j-1,-1,-1):
                indirect = sum((direct[j][k]*total[k][i]
                                for k in range(i+1,j)), Fraction(0))
                direct[j][i] = _value(total[j][i]-indirect)
        return cls(tuple(tuple(row) for row in direct))

    def response(self, action: int, delta: object = 1) -> tuple[Fraction, ...]:
        if type(action) is not int or action not in range(N):
            raise ValueError("WSP182_ACTION")
        d = _value(delta)
        if not d:
            raise ValueError("WSP182_ZERO_DELTA")
        out = [Fraction(0) for _ in range(N)]
        out[action] = d
        for j in range(action+1,N):
            out[j] = sum((self.weights[j][k]*out[k] for k in range(action,j)),
                         Fraction(0))
        return tuple(out)

    def checkpoint(self) -> bytes:
        data = {"schema": SCHEMA,
                "weights": [[_ratio(v) for v in row] for row in self.weights]}
        encoded = json.dumps(data,sort_keys=True,separators=(",",":"),allow_nan=False).encode("ascii")
        msg = MAGIC+len(encoded).to_bytes(4,"big")+encoded
        wire = msg+hashlib.sha256(msg).digest()
        if len(wire) > MAX_WIRE:
            raise ValueError("WSP182_CHECKPOINT_TOO_LARGE")
        return wire

    @classmethod
    def restore(cls, wire: bytes) -> "CausalEdges":
        if type(wire) is not bytes or not 40<len(wire)<=MAX_WIRE:
            raise ValueError("WSP182_CHECKPOINT_SIZE")
        if wire[:4] != MAGIC or int.from_bytes(wire[4:8],"big") != len(wire)-40 or not hmac.compare_digest(hashlib.sha256(wire[:-32]).digest(),wire[-32:]):
            raise ValueError("WSP182_CHECKPOINT_INTEGRITY")
        def unique(items):
            d = {}
            for key,val in items:
                if key in d:
                    raise ValueError("WSP182_DUPLICATE_FIELD")
                d[key] = val
            return d
        try:
            data = json.loads(wire[8:-32].decode("ascii"),object_pairs_hook=unique)
            if type(data) is not dict or set(data)!={"schema","weights"} or data["schema"] != SCHEMA:
                raise ValueError("WSP182_SCHEMA")
            obj = cls(tuple(tuple(_parse(v) for v in row) for row in data["weights"]))
        except (ValueError,TypeError,KeyError,OverflowError,UnicodeError) as exc:
            raise ValueError("WSP182_CHECKPOINT_FIELDS") from exc
        if obj.checkpoint() != wire:
            raise ValueError("WSP182_CHECKPOINT_NONCANONICAL")
        return obj


class RetainedCausalRepair:
    """Cold-preserved old graph + one verified, bounded causal edge patch.

    No hidden family label. For prediction, only an already witnessed public
    contrast selects the better model; absent/ambiguous evidence uses OLD.
    """

    def __init__(self, old: CausalEdges, current: CausalEdges):
        if type(old) is not CausalEdges or type(current) is not CausalEdges:
            raise ValueError("WSP182_MODELS_REQUIRED")
        changes = [(j,i) for j in range(N) for i in range(j)
                   if old.weights[j][i] != current.weights[j][i]]
        if len(changes) != 1:
            raise ValueError("WSP182_NOT_ONE_SPARSE_REPAIR")
        self._old = CausalEdges.restore(old.checkpoint())
        self._current = CausalEdges.restore(current.checkpoint())
        self.changed_direct_edge = changes[0]
        self.old_sha256 = hashlib.sha256(old.checkpoint()).hexdigest()
        self.new_sha256 = hashlib.sha256(current.checkpoint()).hexdigest()

    @classmethod
    def from_public_repair(cls, old: CausalEdges, new_fit: object):
        if type(old) is not CausalEdges:
            raise ValueError("WSP182_OLD_REQUIRED")
        new = CausalEdges.from_public_fit(new_fit)
        return cls(old,new)

    def choose(self, history: object = ()) -> str:
        if type(history) not in (tuple,list) or len(history)>1:
            raise ValueError("WSP182_HISTORY_WINDOW")
        if not history:
            return "old"
        previous = history[0]
        if type(previous) is not PublicContrast:
            raise ValueError("WSP182_PUBLIC_HISTORY_ONLY")
        observed = tuple(b-a for a,b in zip(previous.baseline,previous.intervened))
        def loss(m):
            forecast = m.response(previous.action,previous.commanded_delta)
            return sum(((forecast[k]-observed[k])**2 for k in range(N)),Fraction(0))
        return "new" if loss(self._current)<loss(self._old) else "old"

    def predict(self, action: int, delta: object=1, history: object=()) -> tuple[Fraction,...]:
        m = self._current if self.choose(history) == "new" else self._old
        return m.response(action,delta)

    def cold_restore(self):
        return type(self)(CausalEdges.restore(self._old.checkpoint()),
                          CausalEdges.restore(self._current.checkpoint()))
