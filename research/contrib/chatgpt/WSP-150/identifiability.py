"""WSP-150: source-free GF(2) version-space identifiability certificates.

The complete six-factor monomial basis memorizes every truth-table cell.
Only observed binary pairs are used; no source owner or held-out label.
"""
from __future__ import annotations

CONTEXTS = 64
MAX_WEIGHTS = 1 << CONTEXTS


def _context(x: int) -> int:
    if type(x) is not int or not 0 <= x < CONTEXTS:
        raise ValueError('WSP150_INVALID_CONTEXT')
    return x


def _weights(w: int) -> int:
    if type(w) is not int or not 0 <= w < MAX_WEIGHTS:
        raise ValueError('WSP150_INVALID_WEIGHTS')
    return w


def features(x: int) -> int:
    x = _context(x)
    return sum(1 << m for m in range(CONTEXTS) if (m & x) == m)


def readout(weights: int, x: int) -> int:
    return (_weights(weights) & features(x)).bit_count() & 1


def spike_weights(target: int) -> int:
    """Explicit delta whose complete 64-cell readout is 1 only at target."""
    target = _context(target)
    return sum(1 << m for m in range(CONTEXTS) if (m & target) == target)


def inverse_truth_table(outputs: tuple[int, ...]) -> int:
    """GF(2) Mobius inversion; independent of WSP149 elimination."""
    if type(outputs) not in (tuple, list) or len(outputs) != CONTEXTS or any(
            type(y) is not int or y not in (0, 1) for y in outputs):
        raise ValueError('WSP150_REQUIRES_64_BINARY_OUTPUTS')
    w = 0
    for m in range(CONTEXTS):
        parity = 0
        s = m
        while True:
            parity ^= outputs[s]
            if s == 0:
                break
            s = (s - 1) & m
        w |= parity << m
    return w


def fit_observed(rows: tuple[tuple[int, int], ...]) -> int:
    """Construct one interpolating vector from ONLY 32 observed binary pairs."""
    if type(rows) not in (tuple, list) or len(rows) != 32:
        raise ValueError('WSP150_REQUIRES_32_OBSERVATIONS')
    outputs = [0] * CONTEXTS
    seen: set[int] = set()
    for row in rows:
        if type(row) not in (tuple, list) or len(row) != 2:
            raise ValueError('WSP150_BAD_OBSERVATION')
        x, y = row
        _context(x)
        if type(y) is not int or y not in (0, 1) or x in seen:
            raise ValueError('WSP150_INVALID_OR_DUPLICATE_EFFECT')
        seen.add(x)
        outputs[x] = y
    weights = inverse_truth_table(tuple(outputs))
    if any(readout(weights, x) != y for x, y in rows):
        raise AssertionError('WSP150_FIT_IDENTITY_FAILED')
    return weights


def gf2_rank(rows: tuple[int, ...]) -> int:
    """Independent full-width Gaussian row rank; no evaluator dependency."""
    basis: dict[int, int] = {}
    for row in rows:
        w = _weights(row)
        while w:
            bit = w.bit_length() - 1
            if bit not in basis:
                basis[bit] = w
                break
            w ^= basis[bit]
    return len(basis)


def witness(rows: tuple[tuple[int, int], ...], held: int) -> tuple[int, int]:
    """Two programs fit all 32 observed effects and disagree at held."""
    held = _context(held)
    a = fit_observed(rows)
    if held in {x for x, _ in rows}:
        raise ValueError('WSP150_TARGET_ALREADY_OBSERVED')
    b = a ^ spike_weights(held)
    if readout(a, held) == readout(b, held):
        raise AssertionError('WSP150_NOT_OPPOSITE')
    if any(readout(a, x) != y or readout(b, x) != y for x, y in rows):
        raise AssertionError('WSP150_OBSERVED_ROWS_CHANGED')
    return a, b
