"""Independent public WSP-09 truth-table fixtures and strong controls.

This module is NOT imported by the new weight-programmed circuit. The new
circuit only accepts raw 4-bit input vectors and observed outcome bits.
"""
from __future__ import annotations

import hashlib
import math
import random

from slot_graph import INPUT_BITS

FIXED_4_MASKS = (0x0000, 0xffff, 0x6996, 0x9669,
                 0xaaaa, 0x5555, 0xcccc, 0x3333)
FUNCTIONS_3 = tuple(range(256))


def functions4() -> tuple[int, ...]:
    masks = list(FIXED_4_MASKS)
    seen = set(masks)
    candidate = 0
    while len(masks) < 72:
        material = ("WSP09-mask|seed=" + str(candidate)).encode("ascii")
        mask = int.from_bytes(hashlib.sha256(material).digest()[:2], "little")
        if mask not in seen:
            seen.add(mask)
            masks.append(mask)
        candidate += 1
    return tuple(masks)


FUNCTIONS_4 = functions4()


def to_bits(pattern: int, number_bits: int) -> tuple[int, ...]:
    if (type(pattern) is not int or
            type(number_bits) is not int or
            number_bits not in (3, 4) or
            not 0 <= pattern < (1 << number_bits)):
        raise ValueError("WSP09_PATTERN_OUT_OF_DOMAIN")
    return tuple((pattern >> i) & 1 for i in range(INPUT_BITS))


def exposure_order(mask: int, number_bits: int) -> tuple[int, ...]:
    if (type(mask) is not int or type(number_bits) is not int or
            number_bits not in (3, 4) or
            not 0 <= mask < 1 << (1 << number_bits)):
        raise ValueError("WSP09_INVALID_FUNCTION_MASK")
    patterns = list(range(1 << number_bits))
    random.Random(0xC0FFEE + mask * 131 + number_bits * 1000003).shuffle(patterns)
    return tuple(patterns)


def observed_events(mask: int, number_bits: int) -> tuple[tuple[tuple[int, ...], int], ...]:
    return tuple((to_bits(p, number_bits), (mask >> p) & 1)
                 for p in exposure_order(mask, number_bits))


class ExactAssociative:
    """Fully observed symbolic associative map, independent of the neural VM."""
    def __init__(self):
        self.seen: dict[tuple[int, ...], int] = {}
        self.fault = False

    def observe(self, bits: tuple[int, ...], reward: int) -> None:
        if (bits in self.seen and self.seen[bits] != reward):
            self.fault = True
        else:
            self.seen[bits] = reward

    def predict(self, bits: tuple[int, ...]) -> int | None:
        return None if self.fault else self.seen.get(bits)


class TrainedOneHotLogistic:
    """Converged-gradient comparator: 16 learned logistic-output weights.

    Inputs are full four-bit vectors. A 16-dimensional deterministic one-hot
    feature encoder selects the input pattern; output weights are trained by
    full-batch Adam, not directly programmed. This comparator has the same
    observed outcomes and equivalent memorization bias, but fewer weights.
    """
    SEED = 17
    PARAMETERS = 16
    MAX_EPOCHS = 3000
    LR = 0.05
    STOP_BCE = 0.02

    def __init__(self):
        self.weights = [0.0] * self.PARAMETERS
        self.steps = 0
        self.loss: float | None = None
        self.converged = False

    @staticmethod
    def _index(bits: tuple[int, ...]) -> int:
        if type(bits) is not tuple or len(bits) != INPUT_BITS or any(
                type(x) is not int or x not in (0, 1) for x in bits):
            raise ValueError("WSP09_BASELINE_INVALID_INPUT")
        return sum(value << i for i, value in enumerate(bits))

    def prob(self, bits: tuple[int, ...]) -> float:
        score = max(-40.0, min(40.0, self.weights[self._index(bits)]))
        return 1.0 / (1.0 + math.exp(-score))

    def fit(self, examples: tuple[tuple[tuple[int, ...], int], ...]) -> None:
        if (type(examples) is not tuple or len(examples) != 16 or
                {self._index(bits) for bits, _ in examples} != set(range(16)) or
                any(type(label) is not int or label not in (0, 1)
                    for _, label in examples)):
            raise ValueError("WSP09_BASELINE_DATA_BUDGET_INVALID")
        m = [0.0] * self.PARAMETERS
        v = [0.0] * self.PARAMETERS
        for step in range(1, self.MAX_EPOCHS + 1):
            grad = [0.0] * self.PARAMETERS
            loss = 0.0
            for bits, target in examples:
                index = self._index(bits)
                prob = min(1.0 - 1e-12, max(1e-12, self.prob(bits)))
                loss += -(target * math.log(prob) +
                          (1-target) * math.log(1-prob)) / 16
                grad[index] += (prob-target) / 16
            self.loss = loss
            self.steps = step-1
            if loss <= self.STOP_BCE:
                self.converged = True
                break
            for i, value in enumerate(grad):
                m[i] = .9*m[i] + .1*value
                v[i] = .999*v[i] + .001*value*value
                moment = m[i] / (1 - .9**step)
                variance = v[i] / (1 - .999**step)
                self.weights[i] -= self.LR*moment/(math.sqrt(variance)+1e-8)
            self.steps = step
        if not self.converged:
            self.loss = sum(
                - (target*math.log(max(1e-12, self.prob(bits))) +
                   (1-target)*math.log(max(1e-12,1-self.prob(bits)))) / 16
                for bits, target in examples)
            self.converged = self.loss <= self.STOP_BCE

    def predict(self, bits: tuple[int, ...]) -> int:
        return int(self.prob(bits) >= 0.5)
