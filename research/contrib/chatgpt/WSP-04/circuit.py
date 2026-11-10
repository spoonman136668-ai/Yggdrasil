"""WSP-04: bounded experiential construction of fourth-order binary weight cells.

DEV ONLY: Public synthetic generator, no tokenizer, gradients, new controller
or research first-use. A generic threshold compiler writes actual input weights
for observed monomial residuals, not a precompiled 120-world candidate library.
Sparse extrapolation outside observed basis is a fallible prior, not certainty.
"""
from __future__ import annotations
import hashlib
import json
import math
import random

N_INPUTS = 5
ALL_CONTEXTS = range(1 << N_INPUTS)
BASE = tuple(m for m in ALL_CONTEXTS if m.bit_count() <= 3)
FOURTH = (15, 23, 27, 29, 30)
PAIRS = ((15, 23), (15, 27), (23, 29), (27, 30), (29, 30))
SEEDS = tuple(range(8))
MODES = (0, 1, 2)
HELDOUT = 31
REPLAY = ((0, 0), (1, 1), (8, 0), (14, 1))


def _context(v: int) -> int:
    if type(v) is not int or not 0 <= v < 32:
        raise ValueError("WSP04_CONTEXT_INVALID")
    return v


def _bit(v: int, name: str) -> int:
    if type(v) is not int or v not in (0, 1):
        raise ValueError("WSP04_" + name + "_INVALID")
    return v


def _seed(s: int) -> int:
    if type(s) is not int or s not in SEEDS:
        raise ValueError("WSP04_SEED_INVALID")
    return s


def _world_args(s: int, pair: tuple[int, int], mode: int) -> None:
    _seed(s)
    if type(pair) is not tuple or pair not in PAIRS:
        raise ValueError("WSP04_PAIR_INVALID")
    if type(mode) is not int or mode not in MODES:
        raise ValueError("WSP04_MODE_INVALID")


def public_base_coefficient(seed: int, action: int, mask: int) -> int:
    """World generator only; the learner cannot call this to learn coefficients."""
    _seed(seed)
    _bit(action, "ACTION")
    if type(mask) is not int or mask not in BASE:
        raise ValueError("WSP04_GENERATOR_MASK_INVALID")
    x = f"WSP04|seed={seed}|action={action}|mask={mask}".encode("ascii")
    return hashlib.sha256(x).digest()[0] & 1


def public_reward(seed: int, pair: tuple[int, int], mode: int,
                  context: int, action: int, *, fifth_negative: bool = False) -> int:
    _world_args(seed, pair, mode)
    _context(context)
    _bit(action, "ACTION")
    if type(fifth_negative) is not bool:
        raise ValueError("WSP04_NEGATIVE_FLAG_INVALID")
    value = 0
    for mask in BASE:
        if (mask & context) == mask:
            value ^= public_base_coefficient(seed, action, mask)
    if action == 1:
        if mode >= 1 and (context & pair[0]) == pair[0]:
            value ^= 1
        if mode == 2 and (context & pair[1]) == pair[1]:
            value ^= 1
        if fifth_negative and context == HELDOUT:
            value ^= 1
    return value


def true_choice(seed: int, pair: tuple[int, int], mode: int,
                context: int, *, fifth_negative: bool = False) -> int | None:
    r0 = public_reward(seed, pair, mode, context, 0,
                       fifth_negative=fifth_negative)
    r1 = public_reward(seed, pair, mode, context, 1,
                       fifth_negative=fifth_negative)
    return None if r0 == r1 else (1 if r1 > r0 else 0)


def baseline_observations(seed: int, pair: tuple[int, int], mode: int
                          ) -> tuple[tuple[int, int, int], ...]:
    return tuple((c, a, public_reward(seed, pair, mode, c, a))
                 for c in BASE for a in (0, 1))


class WeightCell:
    """Five directly specified binary input connections and integer threshold."""
    __slots__ = ("mask", "weights", "threshold")

    def __init__(self, mask: int):
        self.mask = _context(mask)
        self.weights = tuple((mask >> j) & 1 for j in range(N_INPUTS))
        self.threshold = sum(self.weights)

    def fires(self, context: int) -> bool:
        _context(context)
        return sum((context >> i & 1) * w for i, w in
                   enumerate(self.weights)) >= self.threshold


class WeightWrittenCircuit:
    """Sparse generic monomial compiler; degree is not fixed at three.

    A positive public residual creates a new binary threshold gate. At a
    fifth-order witness a nonzero residual is NOT identifiable: three
    four-way subsets remain unobserved. It sets unsafe rather than invent
    a uniquely unsupported fifth-order cause.
    """
    MAGIC = b"WSP4"
    MAX_GATES_PER_ACTION = 32
    GRADIENT_STEPS = 0

    def __init__(self, max_degree: int = 5):
        if type(max_degree) is not int or max_degree not in (3, 5):
            raise ValueError("WSP04_BUDGET_INVALID")
        self.max_degree = max_degree
        self.gates: list[dict[int, WeightCell]] = [{}, {}]
        self.seen: dict[tuple[int, int], int] = {}
        self.events: list[tuple[int, int, int]] = []
        self.unsafe = False

    def _predict_known(self, c: int, a: int) -> int:
        return sum(int(g.fires(c)) for g in self.gates[a].values()) & 1

    def _all_base_seen(self, c: int, a: int) -> bool:
        return all((m, a) in self.seen for m in BASE if (m & c) == m)

    def _missing_lower(self, c: int, a: int) -> bool:
        return any((m, a) not in self.seen for m in range(c)
                   if (m & c) == m)

    def observe(self, context: int, action: int, outcome: int) -> None:
        c, a, y = _context(context), _bit(action, "ACTION"), _bit(outcome, "OUTCOME")
        old = self.seen.get((c, a))
        if old is not None:
            if old != y:
                self.unsafe = True
                self.events.append((c, a, y))
            return
        if self.unsafe:
            return
        if not self._all_base_seen(c, a) and c not in BASE:
            raise ValueError("WSP04_BASIS_INCOMPLETE")
        # Every strict subset must have a real observation for uniquely
        # assigning this residual to this particular ANF coefficient.
        missing = self._missing_lower(c, a)
        if missing and c in BASE:
            raise ValueError("WSP04_LOWER_EVIDENCE_MISSING")
        mismatch = self._predict_known(c, a) ^ y
        if mismatch:
            if (missing or c.bit_count() > self.max_degree or
                    len(self.gates[a]) >= self.MAX_GATES_PER_ACTION):
                self.unsafe = True
            else:
                self.gates[a][c] = WeightCell(c)
        self.seen[(c, a)] = y
        self.events.append((c, a, y))

    def predict_reward(self, context: int, action: int) -> int | None:
        c, a = _context(context), _bit(action, "ACTION")
        if self.unsafe or not self._all_base_seen(c, a):
            return None
        return self._predict_known(c, a)

    def choose(self, context: int) -> int | None:
        c = _context(context)
        zero = self.predict_reward(c, 0)
        one = self.predict_reward(c, 1)
        return None if zero is None or one is None or zero == one else (
            1 if one > zero else 0)

    @property
    def degree_four_gates(self) -> int:
        return sum(c.bit_count() == 4 for arm in self.gates for c in arm)

    @property
    def gate_count(self) -> int:
        return sum(len(arm) for arm in self.gates)

    def compiled_weights_sha256(self) -> str:
        raw = bytearray()
        for a in (0, 1):
            for c, gate in sorted(self.gates[a].items()):
                raw.extend((a, c, *gate.weights, gate.threshold, 1))
        return hashlib.sha256(raw).hexdigest()

    def snapshot(self) -> bytes:
        data = {"schema": "wsp04.weight-state.v1",
                "max_degree": self.max_degree,
                "events": self.events,
                "gates": [sorted(arm) for arm in self.gates],
                "unsafe": self.unsafe}
        raw = json.dumps(data, sort_keys=True,
                         separators=(",", ":")).encode("ascii")
        if len(raw) > 8192:
            raise ValueError("WSP04_STATE_TOO_LARGE")
        payload = self.MAGIC + len(raw).to_bytes(4, "big") + raw
        return payload + hashlib.sha256(payload).digest()

    @classmethod
    def restore(cls, blob: bytes) -> "WeightWrittenCircuit":
        if (type(blob) is not bytes or len(blob) < 42 or len(blob) > 8232 or
                blob[:4] != cls.MAGIC or
                int.from_bytes(blob[4:8], "big") != len(blob) - 40 or
                hashlib.sha256(blob[:-32]).digest() != blob[-32:]):
            raise ValueError("WSP04_CHECKPOINT_REJECTED")
        try:
            d = json.loads(blob[8:-32].decode("ascii"))
            if (type(d) is not dict or set(d) !=
                    {"schema", "max_degree", "events", "gates", "unsafe"} or
                    d["schema"] != "wsp04.weight-state.v1" or
                    type(d["unsafe"]) is not bool or
                    type(d["events"]) is not list or
                    len(d["events"]) > 100):
                raise ValueError("BAD_SCHEMA")
            model = cls(d["max_degree"])
            for event in d["events"]:
                if type(event) is not list or len(event) != 3:
                    raise ValueError("BAD_EVENT")
                model.observe(*event)
            if model.snapshot() != blob:
                raise ValueError("NONCANONICAL")
            return model
        except (TypeError, ValueError, KeyError, OverflowError, UnicodeError):
            raise ValueError("WSP04_CHECKPOINT_REJECTED") from None


class ExactSymbolicANF:
    """Independent non-network algebraic-normal-form evidence inversion."""
    def __init__(self):
        self.coef: list[dict[int, int]] = [{}, {}]
        self.seen: set[tuple[int, int]] = set()
        self.unsafe = False

    def observe(self, context: int, action: int, outcome: int) -> None:
        c, a, y = _context(context), _bit(action, "ACTION"), _bit(outcome, "OUTCOME")
        if self.unsafe:
            return
        if (c, a) in self.seen:
            if self.predict_reward(c, a) != y:
                self.unsafe = True
            return
        if any((m, a) not in self.seen for m in range(c) if (m & c) == m):
            raise ValueError("WSP04_SYMBOLIC_UNIDENTIFIED")
        residual = y ^ (sum(v for m, v in self.coef[a].items()
                             if (m & c) == m) & 1)
        if residual:
            self.coef[a][c] = 1
        self.seen.add((c, a))

    def predict_reward(self, context: int, action: int) -> int | None:
        c, a = _context(context), _bit(action, "ACTION")
        if self.unsafe or any((m, a) not in self.seen
                              for m in BASE if (m & c) == m):
            return None
        return sum(v for m, v in self.coef[a].items()
                   if (m & c) == m) & 1

    def choose(self, context: int) -> int | None:
        a, b = self.predict_reward(context, 0), self.predict_reward(context, 1)
        return None if a is None or b is None or a == b else (1 if b > a else 0)


class TrainedMLPControl:
    """Fixed-budget conventional control, not a fully converged strong baseline."""
    STEPS = 256
    LR = 0.05
    SEED = 17
    HIDDEN = 12
    PARAMETERS = (6 * 12) + 12 + 12 + 1

    def __init__(self) -> None:
        rand = random.Random(self.SEED)
        self.w = [[rand.uniform(-0.25, 0.25) for _ in range(6)]
                  for _ in range(self.HIDDEN)]
        self.b = [0.0] * self.HIDDEN
        self.v = [rand.uniform(-0.25, 0.25) for _ in range(self.HIDDEN)]
        self.out_bias = 0.0
        self.loss: float | None = None

    @staticmethod
    def features(c: int, a: int) -> tuple[float, ...]:
        _context(c)
        _bit(a, "ACTION")
        return tuple(float((c >> bit) & 1) for bit in range(5)) + (float(a),)

    def forward(self, x: tuple[float, ...]) -> tuple[list[float], float]:
        hidden = [math.tanh(sum(w * y for w, y in zip(row, x)) + bias)
                  for row, bias in zip(self.w, self.b)]
        score = sum(w * h for w, h in zip(self.v, hidden)) + self.out_bias
        score = max(-40.0, min(40.0, score))
        return hidden, 1 / (1 + math.exp(-score))

    def fit(self, events: tuple[tuple[int, int, int], ...],
            pair: tuple[int, int]) -> None:
        if (type(pair) is not tuple or pair not in PAIRS or
                len(events) != 54 or
                any(type(c) is not int or type(a) is not int or
                    type(r) is not int or r not in (0, 1) or
                    (c, a) != (BASE[i // 2], i % 2)
                    for i, (c, a, r) in enumerate(events[:52])) or
                events[52][:2] != (pair[0], 1) or
                events[53][:2] != (pair[1], 1) or
                any(type(r) is not int or r not in (0, 1)
                    for _, _, r in events[52:])):
            raise ValueError("WSP04_TRAINING_DATA_INVALID")
        xs = [(self.features(c, a), r) for c, a, r in events]
        n = len(xs)
        for _ in range(self.STEPS):
            gw = [[0.0] * 6 for _ in range(self.HIDDEN)]
            gb = [0.0] * self.HIDDEN
            gv = [0.0] * self.HIDDEN
            go = 0.0
            for x, y in xs:
                hidden, pred = self.forward(x)
                err = (pred - y) / n
                go += err
                for j in range(self.HIDDEN):
                    gv[j] += err * hidden[j]
                    d = err * self.v[j] * (1 - hidden[j] ** 2)
                    gb[j] += d
                    for k in range(6):
                        gw[j][k] += d * x[k]
            self.out_bias -= self.LR * go
            for j in range(self.HIDDEN):
                self.v[j] -= self.LR * gv[j]
                self.b[j] -= self.LR * gb[j]
                for k in range(6):
                    self.w[j][k] -= self.LR * gw[j][k]
        self.loss = sum(
            -r * math.log(max(1e-12, self.forward(x)[1])) -
            (1-r) * math.log(max(1e-12, 1 - self.forward(x)[1]))
            for x, r in xs) / n

    def choose(self, context: int) -> int:
        c = _context(context)
        p0 = self.forward(self.features(c, 0))[1]
        p1 = self.forward(self.features(c, 1))[1]
        return int(p1 > p0)
