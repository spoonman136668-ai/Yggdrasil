"""WSP-03 public DEV: construct binary conjunction gates directly from outcomes.

This is NOT a trained general neural model. A fixed, bounded monomial grammar
allows new connection weights for previously absent AND cells to be written
from actual public action/outcome residuals. It uses no gradient optimizer.
The grammar, source code, observations, and synthetic evaluation are public.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import dataclass

PROTOCOL_SHA256 = "0399ed5c5ffcc4eb88acac6c8c16be78d1c1543ae56ccaf1a991fcf0526f3752"
BASIS = (0, 1, 2, 4, 8, 3, 5, 6, 9, 10, 12)
TRIPLES = (7, 11, 13, 14)
SEEDS = tuple(range(16))
TRANSFER = 15


def _ctx(c: int) -> int:
    if type(c) is not int or not 0 <= c < 16:
        raise ValueError("WSP03_CONTEXT_INVALID")
    return c


def _bit(x: int, label: str) -> int:
    if type(x) is not int or x not in (0, 1):
        raise ValueError("WSP03_" + label + "_INVALID")
    return x


def _seed(s: int) -> int:
    if type(s) is not int or s not in SEEDS:
        raise ValueError("WSP03_SEED_INVALID")
    return s


def coefficient(seed: int, action: int, mask: int) -> int:
    """Only the public DEV world generator calls this hidden-to-model source."""
    _seed(seed)
    _bit(action, "ACTION")
    if type(mask) is not int or mask not in BASIS:
        raise ValueError("WSP03_GENERATOR_MASK_INVALID")
    raw = ("WSP03-baseline|seed=" + str(seed) +
           "|action=" + str(action) + "|mask=" + str(mask))
    return hashlib.sha256(raw.encode("utf-8")).digest()[0] & 1


def world_reward(seed: int, triple: int, novel: int, context: int,
                 action: int, *, fourth_order: bool = False) -> int:
    _seed(seed)
    if type(triple) is not int or triple not in TRIPLES:
        raise ValueError("WSP03_TRIPLE_INVALID")
    _bit(novel, "NOVEL")
    _ctx(context)
    _bit(action, "ACTION")
    if type(fourth_order) is not bool:
        raise ValueError("WSP03_NEGATIVE_FLAG_INVALID")
    val = 0
    for mask in BASIS:
        if mask & context == mask:
            val ^= coefficient(seed, action, mask)
    if novel and action == 1 and (context & triple) == triple:
        val ^= 1
    if fourth_order and action == 1 and context == TRANSFER:
        val ^= 1
    return val


def true_choice(seed: int, triple: int, novel: int, context: int,
                *, fourth_order: bool = False) -> int | None:
    p0 = world_reward(seed, triple, novel, context, 0,
                      fourth_order=fourth_order)
    p1 = world_reward(seed, triple, novel, context, 1,
                      fourth_order=fourth_order)
    return None if p0 == p1 else (1 if p1 > p0 else 0)


def samples(seed: int, triple: int, novel: int) -> tuple[tuple[int, int, int], ...]:
    return tuple((c, a, world_reward(seed, triple, novel, c, a))
                 for c in BASIS for a in (0, 1))


@dataclass(frozen=True)
class AndCell:
    """A binary four-input threshold neuron with directly programmed weights."""
    mask: int
    weights: tuple[int, int, int, int]
    threshold: int

    @classmethod
    def compile(cls, mask: int) -> "AndCell":
        _ctx(mask)
        if mask.bit_count() > 3:
            raise ValueError("WSP03_UNSUPPORTED_DEGREE")
        weights = tuple((mask >> bit) & 1 for bit in range(4))
        return cls(mask, weights, sum(weights))

    def fires(self, context: int) -> bool:
        _ctx(context)
        return sum(w * ((context >> bit) & 1)
                   for bit, w in enumerate(self.weights)) >= self.threshold


class DirectWeightCircuit:
    """Bounded online feature creation; no preenumerated complete hypotheses.

    A public observation's GF(2) residual creates a new AND threshold cell
    (four newly specified input weights + a parity readout edge).
    Unsupported degree or contradictory repeated observations fail closed.
    """

    MAGIC = b"W3S1"
    MAX_GATES_PER_ACTION = 15
    GRADIENT_STEPS = 0

    def __init__(self, *, max_degree: int = 3) -> None:
        if type(max_degree) is not int or max_degree not in (2, 3):
            raise ValueError("WSP03_DEGREE_BUDGET_INVALID")
        self.max_degree = max_degree
        self._cells: list[dict[int, AndCell]] = [{}, {}]
        self._events: list[tuple[int, int, int]] = []
        self._observed: dict[tuple[int, int], int] = {}
        self._unsafe = False

    def _parity(self, context: int, action: int) -> int:
        return sum(int(cell.fires(context))
                   for cell in self._cells[action].values()) & 1

    def _basis_ready(self, context: int, action: int, *,
                     observing: bool = False) -> bool:
        return all((mask, action) in self._observed
                   for mask in BASIS
                   if (mask & context) == mask and
                   not (observing and mask == context))

    def observe(self, context: int, action: int, outcome: int) -> None:
        _ctx(context)
        _bit(action, "ACTION")
        _bit(outcome, "OUTCOME")
        key = (context, action)
        if key in self._observed:
            if self._observed[key] != outcome:
                self._unsafe = True
                self._events.append((context, action, outcome))
            return
        if self._unsafe:
            return
        if not self._basis_ready(context, action, observing=True):
            raise ValueError("WSP03_LOWER_ORDER_EVIDENCE_MISSING")
        mismatch = self._parity(context, action) ^ outcome
        if mismatch:
            if context.bit_count() > self.max_degree or (
                    len(self._cells[action]) >= self.MAX_GATES_PER_ACTION):
                self._unsafe = True
            else:
                self._cells[action][context] = AndCell.compile(context)
        self._observed[key] = outcome
        self._events.append((context, action, outcome))

    def predict_reward(self, context: int, action: int) -> int | None:
        _ctx(context)
        _bit(action, "ACTION")
        if self._unsafe or not self._basis_ready(context, action):
            return None
        return self._parity(context, action)

    def choose(self, context: int) -> int | None:
        _ctx(context)
        p0 = self.predict_reward(context, 0)
        p1 = self.predict_reward(context, 1)
        return None if p0 is None or p1 is None or p0 == p1 else (
            1 if p1 > p0 else 0)

    @property
    def unsafe(self) -> bool:
        return self._unsafe

    @property
    def gate_count(self) -> int:
        return sum(map(len, self._cells))

    @property
    def new_triple_gates(self) -> int:
        return sum(mask.bit_count() == 3
                   for arm in self._cells for mask in arm)

    def weights_sha256(self) -> str:
        packed = bytearray()
        for action in (0, 1):
            for mask, cell in sorted(self._cells[action].items()):
                packed.extend((action, mask, *cell.weights, cell.threshold, 1))
        return hashlib.sha256(packed).hexdigest()

    def snapshot(self) -> bytes:
        state = {
            "schema": "wsp03.direct-weight-state.v1",
            "max_degree": self.max_degree,
            "gates": [sorted(arm) for arm in self._cells],
            "events": self._events,
            "unsafe": self._unsafe,
        }
        payload = json.dumps(state, sort_keys=True,
                             separators=(",", ":")).encode("ascii")
        if len(payload) > 4096:
            raise ValueError("WSP03_CHECKPOINT_CAPACITY")
        prefix = self.MAGIC + len(payload).to_bytes(4, "big") + payload
        return prefix + hashlib.sha256(prefix).digest()

    @classmethod
    def restore(cls, blob: bytes) -> "DirectWeightCircuit":
        if (type(blob) is not bytes or len(blob) < 43 or len(blob) > 4136 or
                blob[:4] != cls.MAGIC or
                int.from_bytes(blob[4:8], "big") != len(blob) - 40 or
                hashlib.sha256(blob[:-32]).digest() != blob[-32:]):
            raise ValueError("WSP03_CHECKPOINT_REJECTED")
        try:
            data = json.loads(blob[8:-32].decode("ascii"))
            if (type(data) is not dict or
                    set(data) != {"schema", "max_degree", "gates",
                                  "events", "unsafe"} or
                    data["schema"] != "wsp03.direct-weight-state.v1" or
                    type(data["unsafe"]) is not bool or
                    type(data["events"]) is not list or
                    len(data["events"]) > 128):
                raise ValueError("BAD_SCHEMA")
            model = cls(max_degree=data["max_degree"])
            for event in data["events"]:
                if (type(event) is not list or len(event) != 3):
                    raise ValueError("BAD_EVENT")
                model.observe(*event)
            if model.snapshot() != blob:
                raise ValueError("NONCANONICAL_OR_INCONSISTENT")
            return model
        except (ValueError, TypeError, KeyError, UnicodeError, OverflowError):
            raise ValueError("WSP03_CHECKPOINT_REJECTED") from None


class ExactSymbolicANF:
    """Strong independent ANF solver (no connection-weight cells)."""
    def __init__(self, *, max_degree: int = 3) -> None:
        self.max_degree = max_degree
        self._coef: list[dict[int, int]] = [{}, {}]
        self._seen: set[tuple[int, int]] = set()
        self._unsafe = False

    def observe(self, context: int, action: int, reward: int) -> None:
        _ctx(context)
        _bit(action, "ACTION")
        _bit(reward, "OUTCOME")
        if self._unsafe:
            return
        if any((m, action) not in self._seen for m in BASIS
               if (m & context) == m and m != context):
            raise ValueError("WSP03_SYMBOLIC_LOWER_MISSING")
        predicted = sum(coef for m, coef in self._coef[action].items()
                        if (m & context) == m) & 1
        if predicted != reward:
            if context.bit_count() > self.max_degree:
                self._unsafe = True
            else:
                self._coef[action][context] = 1
        self._seen.add((context, action))

    def predict_reward(self, context: int, action: int) -> int | None:
        _ctx(context)
        _bit(action, "ACTION")
        if self._unsafe or any((m, action) not in self._seen
                               for m in BASIS if (m & context) == m):
            return None
        return sum(coeff for m, coef in self._coef[action].items()
                   if (m & context) == m) & 1

    def choose(self, context: int) -> int | None:
        a, b = self.predict_reward(context, 0), self.predict_reward(context, 1)
        return None if a is None or b is None or a == b else (1 if b > a else 0)


class TrainedMLPControl:
    """Frozen-budget 5-10-1 tanh/sigmoid conventional control; not strong science."""
    HIDDEN = 10
    PARAMS = 71
    STEPS = 512
    LR = 0.05
    SEED = 17

    def __init__(self) -> None:
        rng = random.Random(self.SEED)
        self.w = [[rng.uniform(-0.25, 0.25) for _ in range(5)]
                  for _ in range(self.HIDDEN)]
        self.b = [0.0] * self.HIDDEN
        self.v = [rng.uniform(-0.25, 0.25)
                  for _ in range(self.HIDDEN)]
        self.bias = 0.0
        self.fit_loss: float | None = None

    @staticmethod
    def features(context: int, action: int) -> tuple[int, ...]:
        _ctx(context)
        _bit(action, "ACTION")
        return tuple((context >> i) & 1 for i in range(4)) + (action,)

    def forward(self, x: tuple[int, ...]) -> tuple[list[float], float]:
        h = [math.tanh(sum(v * bit for v, bit in zip(row, x)) + bias)
             for row, bias in zip(self.w, self.b)]
        z = sum(v * cell for v, cell in zip(self.v, h)) + self.bias
        z = max(-40.0, min(40.0, z))
        return h, 1.0 / (1.0 + math.exp(-z))

    def fit(self, examples: tuple[tuple[int, int, int], ...],
            triple: int) -> None:
        if (type(triple) is not int or triple not in TRIPLES or
                len(examples) != 23 or
                any(type(c) is not int or type(a) is not int or
                    type(r) is not int or r not in (0, 1) or
                    (c, a) != (BASIS[i // 2], i % 2)
                    for i, (c, a, r) in enumerate(examples[:22])) or
                examples[22][:2] != (triple, 1) or
                type(examples[22][2]) is not int or
                examples[22][2] not in (0, 1)):
            raise ValueError("WSP03_TRAINED_CONTROL_BUDGET_INVALID")
        n = len(examples)
        xs = [(self.features(c, a), y) for c, a, y in examples]
        for _ in range(self.STEPS):
            gw = [[0.0] * 5 for _ in range(self.HIDDEN)]
            gb = [0.0] * self.HIDDEN
            gv = [0.0] * self.HIDDEN
            g_bias = 0.0
            for x, y in xs:
                h, p = self.forward(x)
                err = (p - y) / n
                g_bias += err
                for j in range(self.HIDDEN):
                    gv[j] += err * h[j]
                    delta = err * self.v[j] * (1.0 - h[j] ** 2)
                    gb[j] += delta
                    for k in range(5):
                        gw[j][k] += delta * x[k]
            self.bias -= self.LR * g_bias
            for j in range(self.HIDDEN):
                self.v[j] -= self.LR * gv[j]
                self.b[j] -= self.LR * gb[j]
                for k in range(5):
                    self.w[j][k] -= self.LR * gw[j][k]
        self.fit_loss = sum(
            -y * math.log(max(1e-12, self.forward(x)[1])) -
            (1-y) * math.log(max(1e-12, 1.0 - self.forward(x)[1]))
            for x, y in xs) / n

    def choose(self, context: int) -> int:
        _ctx(context)
        p0 = self.forward(self.features(context, 0))[1]
        p1 = self.forward(self.features(context, 1))[1]
        return int(p1 > p0)
