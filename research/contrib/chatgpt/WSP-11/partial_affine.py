"""WSP-11: conditional Boolean generalization from four witnesses (public DEV).

The GF(2) affine inductive bias is PROGRAMMED IN PYTHON, not discovered by
the neural circuit. Only the inferred function's numeric crossbar synapses
are directly programmed. No gradient update and no runtime truth-table mask.
"""
from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "WSP-10"))
from crossbar import DirectCrossbar, checked_bits

BASIS = (0, 1, 2, 4)
HOLDOUT = (3, 5, 6, 7)
GRADIENT_STEPS = 0


def bits(index: int) -> tuple[int, int, int]:
    if type(index) is not int or not 0 <= index < 8:
        raise ValueError("WSP11_INVALID_CONTEXT")
    return tuple((index >> j) & 1 for j in range(3))


def index_of(context: tuple[int, int, int]) -> int:
    checked_bits(context, 3)
    return sum(v << j for j, v in enumerate(context))


def affine_truth(code: int, index: int) -> int:
    """Evaluator only; NEVER passed to the four-witness weight compiler."""
    if type(code) is not int or not 0 <= code < 16:
        raise ValueError("WSP11_INVALID_AFFINE_CODE")
    return (code & 1) ^ sum(((code >> (j + 1)) & 1) * ((index >> j) & 1)
                            for j in range(3)) % 2


def validate_observations(observations: tuple) -> dict[int, int]:
    if type(observations) is not tuple or len(observations) != 4:
        raise ValueError("WSP11_INVALID_OBSERVATIONS")
    known: dict[int, int] = {}
    for pair in observations:
        if type(pair) is not tuple or len(pair) != 2:
            raise ValueError("WSP11_INVALID_OBSERVATIONS")
        x, y = pair
        k = index_of(x)
        if k in known or type(y) is not int or y not in (0, 1):
            raise ValueError("WSP11_INVALID_OBSERVATIONS")
        known[k] = y
    if set(known) != set(BASIS):
        raise ValueError("WSP11_INVALID_BASIS")
    return known


class PartialAffineCircuit:
    """Four observed labels -> inferred affine rule -> numeric crossbar edges.

    Input completion and rule inference are external programmed software;
    a numeric weighted threshold network performs subsequent inference.
    """
    def __init__(self, observations: tuple):
        known = validate_observations(observations)
        bias = known[0]
        coefficient = tuple(known[1 << j] ^ bias for j in range(3))
        inferred_mask = 0
        for i in range(8):
            y = bias ^ (sum(coefficient[j] * ((i >> j) & 1)
                            for j in range(3)) % 2)
            inferred_mask |= y << i
        self.circuit = DirectCrossbar.from_spec(3, inferred_mask)
        self.fault = False

    def predict(self, x: tuple[int, int, int]) -> int | None:
        checked_bits(x, 3)
        if self.fault:
            return None
        return self.circuit.evaluate(x)

    def observe_verification(self, x: tuple[int, int, int], label: int) -> bool:
        checked_bits(x, 3)
        if type(label) is not int or label not in (0, 1):
            raise ValueError("WSP11_INVALID_LABEL")
        if self.fault or self.circuit.evaluate(x) != label:
            self.fault = True
            return False
        return True

    def snapshot(self) -> bytes:
        if self.fault:
            raise ValueError("WSP11_FAULTED_SNAPSHOT")
        return self.circuit.snapshot()

    @classmethod
    def restore(cls, raw: bytes) -> "PartialAffineCircuit":
        c = DirectCrossbar.restore(raw)
        if c.n != 3:
            raise ValueError("WSP11_INVALID_CHECKPOINT_DIMENSION")
        result = cls.__new__(cls)
        result.circuit = c
        result.fault = False
        return result


def symbolic_gf2(observations: tuple, x: tuple[int, int, int]) -> int:
    """Separate 4x4 GF(2) eliminator, equally informed exact control."""
    known = validate_observations(observations)
    checked_bits(x, 3)
    rows = [[1, *bits(i), known[i]] for i in BASIS]
    for k in range(4):
        pivot = next((r for r in range(k, 4) if rows[r][k]), None)
        if pivot is None:
            raise ValueError("WSP11_UNDERSPECIFIED")
        r = pivot
        rows[k], rows[r] = rows[r], rows[k]
        for j in range(4):
            if j != k and rows[j][k]:
                rows[j] = [a ^ b for a, b in zip(rows[j], rows[k])]
    coef = [row[-1] for row in rows]
    return coef[0] ^ sum(coef[j+1] * x[j] for j in range(3)) % 2


def observed_only_crossbar(observations: tuple) -> DirectCrossbar:
    """Matched information, no structural extrapolation to unseen contexts."""
    known = validate_observations(observations)
    mask = sum(known[i] << i for i in BASIS)
    return DirectCrossbar.from_spec(3, mask)
