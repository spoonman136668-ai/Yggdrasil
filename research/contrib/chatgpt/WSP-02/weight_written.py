"""WSP-02: directly compiled causal interaction network, public DEV only.

3,072 immutable binary weights encode a pre-specified 64-rule causal family.
Public observations update 64 recurrent hypothesis bits; no gradient training.
This implements known structural inference, not unfamiliar-world intelligence.
"""
from __future__ import annotations
import hashlib
import math
import random

SPEC = (
    "WSP02:v1|h=(mask:3,interaction:1,flip:1,bias:1)|"
    "reward=parity(mask&context)^bias^(action&flip)^"
    "(action&context_bit2&interaction)|"
    "observe=(0,0),(1,0),(2,0),(4,0),(0,1),(4,1)|"
    "transfer=3,5,6,7|ood=reward^(context_bit0&context_bit1)|"
    "ood_witness=(3,0)|h=0..63"
)
SPEC_SHA256 = "17fd933168b069dcb2161c0a8c9a92a7231a2845582780bc2fd5aaf34b44f7d9"
OBSERVATIONS = ((0, 0), (1, 0), (2, 0), (4, 0), (0, 1), (4, 1))
TRANSFER_CONTEXTS = (3, 5, 6, 7)


def _bit(value: int, name: str) -> int:
    if type(value) is not int or value not in (0, 1):
        raise ValueError("WSP02_" + name + "_INVALID")
    return value


def _context(value: int) -> int:
    if type(value) is not int or not 0 <= value < 8:
        raise ValueError("WSP02_CONTEXT_INVALID")
    return value


def public_rule(hypothesis: int, context: int, action: int, *, ood: bool = False) -> int:
    if type(hypothesis) is not int or not 0 <= hypothesis < 64:
        raise ValueError("WSP02_HYPOTHESIS_INVALID")
    _context(context)
    _bit(action, "ACTION")
    if type(ood) is not bool:
        raise ValueError("WSP02_OOD_FLAG_INVALID")
    mask = hypothesis >> 3
    interaction = (hypothesis >> 2) & 1
    flip = (hypothesis >> 1) & 1
    bias = hypothesis & 1
    reward = ((mask & context).bit_count() & 1) ^ bias ^ (action & flip)
    reward ^= action & ((context >> 2) & 1) & interaction
    if ood:
        reward ^= int((context & 3) == 3)
    return reward


def oracle_choice(hypothesis: int, context: int, *, ood: bool = False) -> int | None:
    zero = public_rule(hypothesis, context, 0, ood=ood)
    one = public_rule(hypothesis, context, 1, ood=ood)
    return None if zero == one else int(one > zero)


class WeightWrittenNetwork:
    """Fixed 64x32 compatibility matrix and 8x2x64 vote matrix."""
    __slots__ = ("_compat", "_votes", "_state")
    MAGIC = b"WS02"
    STATE_BITS = 64
    STATIC_WEIGHT_COUNT = 64 * 32 + 8 * 2 * 64
    TRAINABLE_WEIGHTS = 0
    CHECKPOINT_BYTES = 4 + 8 + 32

    def __init__(self) -> None:
        self._compat = tuple(tuple(
            int(public_rule(h, c, a) == reward)
            for c in range(8) for a in (0, 1) for reward in (0, 1)
        ) for h in range(64))
        self._votes = tuple(tuple(tuple(
            int(oracle_choice(h, c) == action)
            for h in range(64)) for action in (0, 1)) for c in range(8))
        self._state = (1,) * 64

    def observe(self, context: int, action: int, public_outcome: int) -> None:
        _context(context)
        _bit(action, "ACTION")
        _bit(public_outcome, "OUTCOME")
        slot = (context * 2 + action) * 2 + public_outcome
        self._state = tuple(int(active + row[slot] == 2)
                            for active, row in zip(self._state, self._compat))

    def choose(self, context: int) -> int | None:
        _context(context)
        live = sum(self._state)
        if not live:
            return None
        for action in (0, 1):
            votes = sum(bit * weight for bit, weight in
                        zip(self._state, self._votes[context][action]))
            if votes == live:
                return action
        return None

    def predict_outcome(self, context: int, action: int) -> int | None:
        """Reward prediction via compiled compatibility weights only."""
        _context(context)
        _bit(action, "ACTION")
        live = sum(self._state)
        if not live:
            return None
        base = (context * 2 + action) * 2
        zero = sum(active * row[base] for active, row in zip(self._state, self._compat))
        one = sum(active * row[base + 1] for active, row in zip(self._state, self._compat))
        return 0 if zero == live else (1 if one == live else None)

    @property
    def remaining(self) -> int:
        return sum(self._state)

    def static_weight_hash(self) -> str:
        data = bytes(v for row in self._compat for v in row)
        data += bytes(v for context in self._votes for row in context for v in row)
        assert len(data) == self.STATIC_WEIGHT_COUNT
        return hashlib.sha256(data).hexdigest()

    def snapshot(self) -> bytes:
        state_mask = sum(bit << h for h, bit in enumerate(self._state))
        prefix = self.MAGIC + state_mask.to_bytes(8, "big")
        return prefix + hashlib.sha256(prefix).digest()

    @classmethod
    def restore(cls, blob: bytes) -> "WeightWrittenNetwork":
        if (type(blob) is not bytes or len(blob) != cls.CHECKPOINT_BYTES or
                blob[:4] != cls.MAGIC or
                hashlib.sha256(blob[:-32]).digest() != blob[-32:]):
            raise ValueError("WSP02_CHECKPOINT_REJECTED")
        new = cls()
        bits = int.from_bytes(blob[4:12], "big")
        new._state = tuple((bits >> h) & 1 for h in range(64))
        return new


class SymbolicControl:
    """Exact hypothesis enumeration, independent of connection weights."""
    def __init__(self) -> None:
        self.candidates = set(range(64))

    def observe(self, context: int, action: int, outcome: int) -> None:
        _context(context)
        _bit(action, "ACTION")
        _bit(outcome, "OUTCOME")
        self.candidates = {h for h in self.candidates
                           if public_rule(h, context, action) == outcome}

    @property
    def remaining(self) -> int:
        return len(self.candidates)

    def choose(self, context: int) -> int | None:
        _context(context)
        if not self.candidates:
            return None
        choices = {oracle_choice(h, context) for h in self.candidates}
        return next(iter(choices)) if len(choices) == 1 else None


class TabularControl:
    """Matched public outcomes, without programmed cross-context composition."""
    def __init__(self) -> None:
        self.counts = [[[0, 0] for _ in range(2)] for _ in range(8)]

    def observe(self, context: int, action: int, outcome: int) -> None:
        _context(context)
        _bit(action, "ACTION")
        _bit(outcome, "OUTCOME")
        self.counts[context][action][outcome] += 1

    def choose(self, context: int) -> int | None:
        _context(context)
        (f0, s0), (f1, s1) = self.counts[context]
        n0, n1 = f0 + s0, f1 + s1
        if not n0 or not n1:
            return None
        diff = s1 * n0 - s0 * n1
        return 1 if diff > 0 else (0 if diff < 0 else None)


class ConventionalMLPControl:
    """Fixed-seed, 512-step trained 6-8-1 tanh/sigmoid conventional control.

    65 floating scalar trainable parameters, full-batch cross entropy.
    No invented posthoc tie/abstention threshold. Fixed features are context
    bits, action, action*bit0, action*bit2.
    """
    INPUTS = 6
    HIDDEN = 8
    TRAINABLE_WEIGHTS = 65
    STEPS = 512
    LR = 0.05
    SEED = 17

    def __init__(self) -> None:
        rng = random.Random(self.SEED)
        self.w = [[rng.uniform(-0.25, 0.25) for _ in range(6)] for _ in range(8)]
        self.b = [0.0] * 8
        self.v = [rng.uniform(-0.25, 0.25) for _ in range(8)]
        self.bias = 0.0
        self.fit_loss = None

    @staticmethod
    def features(context: int, action: int) -> tuple[float, ...]:
        _context(context)
        _bit(action, "ACTION")
        b0, b1, b2 = (context >> i & 1 for i in range(3))
        return tuple(float(v) for v in (b0, b1, b2, action, b0 * action, b2 * action))

    def forward(self, features: tuple[float, ...]) -> tuple[list[float], float]:
        z = [math.tanh(sum(w * x for w, x in zip(row, features)) + bias)
             for row, bias in zip(self.w, self.b)]
        score = sum(w * val for w, val in zip(self.v, z)) + self.bias
        prob = 1 / (1 + math.exp(-max(-40.0, min(40.0, score))))
        return z, prob

    def fit(self, examples: tuple[tuple[int, int, int], ...]) -> None:
        if len(examples) != len(OBSERVATIONS):
            raise ValueError("WSP02_MLP_DATA_BUDGET_INVALID")
        if any((c, a) != OBSERVATIONS[i] or type(y) is not int or y not in (0, 1)
               for i, (c, a, y) in enumerate(examples)):
            raise ValueError("WSP02_MLP_OBSERVATIONS_INVALID")
        n = len(examples)
        for _ in range(self.STEPS):
            gw = [[0.0] * 6 for _ in range(8)]
            gb = [0.0] * 8
            gv = [0.0] * 8
            go = 0.0
            for c, a, y in examples:
                x = self.features(c, a)
                z, p = self.forward(x)
                err = (p - y) / n
                go += err
                for j in range(8):
                    gv[j] += err * z[j]
                    delta = err * self.v[j] * (1 - z[j] ** 2)
                    gb[j] += delta
                    for k in range(6):
                        gw[j][k] += delta * x[k]
            for j in range(8):
                self.v[j] -= self.LR * gv[j]
                self.b[j] -= self.LR * gb[j]
                for k in range(6):
                    self.w[j][k] -= self.LR * gw[j][k]
            self.bias -= self.LR * go
        def bce(c: int, a: int, y: int) -> float:
            p = self.forward(self.features(c, a))[1]
            return -y * math.log(max(1e-12, p)) - (1 - y) * math.log(max(1e-12, 1 - p))
        self.fit_loss = sum(bce(*sample) for sample in examples) / n

    def choose(self, context: int) -> int:
        _context(context)
        p0 = self.forward(self.features(context, 0))[1]
        p1 = self.forward(self.features(context, 1))[1]
        return int(p1 > p0)
