"""Exact seven-player counterfactual Shapley credit and Q16 quantization.

This module contains no task environment, hidden task state, or policy code.
It accepts only a complete integer coalition-value table and immutable player IDs.
"""
from __future__ import annotations

from math import factorial
from typing import Mapping, Sequence

Q16 = 65_536
PLAYER_COUNT = 7
COALITION_COUNT = 1 << PLAYER_COUNT
DENOMINATOR = factorial(PLAYER_COUNT)


class CoalitionContractError(ValueError):
    """Raised when the evaluator coalition receipt is incomplete or invalid."""


def _validate(
    player_ids: Sequence[int],
    coalition_values: Mapping[int, int],
) -> tuple[int, ...]:
    if len(player_ids) != PLAYER_COUNT:
        raise CoalitionContractError("PLAYER_COUNT_MUST_BE_SEVEN")
    if any(isinstance(x, bool) or not isinstance(x, int) or x < 0 for x in player_ids):
        raise CoalitionContractError("PLAYER_ID_INVALID")
    if len(set(player_ids)) != PLAYER_COUNT:
        raise CoalitionContractError("PLAYER_IDS_NOT_UNIQUE")
    expected = set(range(COALITION_COUNT))
    actual = set(coalition_values)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise CoalitionContractError(
            f"COALITION_MASK_SET_MISMATCH:missing={missing}:extra={extra}"
        )
    for mask, value in coalition_values.items():
        if isinstance(mask, bool) or not isinstance(mask, int) or mask not in expected:
            raise CoalitionContractError("COALITION_MASK_INVALID")
        if isinstance(value, bool) or not isinstance(value, int):
            raise CoalitionContractError("COALITION_VALUE_MUST_BE_INTEGER")
    return tuple(player_ids)


def exact_shapley_numerators(
    player_ids: Sequence[int],
    coalition_values: Mapping[int, int],
) -> tuple[tuple[int, ...], int]:
    """Return exact rational Shapley numerators over the common denominator 7!.

    Coalition mask bit j denotes player_ids[j]. The returned numerator tuple
    follows player_ids order. No floating-point arithmetic is used.
    """
    ids = _validate(player_ids, coalition_values)
    del ids  # validation is intentionally separate from bit ordering
    numerators: list[int] = []
    for player_index in range(PLAYER_COUNT):
        player_bit = 1 << player_index
        numerator = 0
        for mask in range(COALITION_COUNT):
            if mask & player_bit:
                continue
            size = mask.bit_count()
            weight = factorial(size) * factorial(PLAYER_COUNT - size - 1)
            marginal = (
                coalition_values[mask | player_bit] - coalition_values[mask]
            )
            numerator += weight * marginal
        numerators.append(numerator)
    full_delta = (
        coalition_values[COALITION_COUNT - 1] - coalition_values[0]
    )
    if sum(numerators) != DENOMINATOR * full_delta:
        raise CoalitionContractError("SHAPLEY_EFFICIENCY_INVARIANT")
    return tuple(numerators), full_delta


def shapley_q16_credits(
    player_ids: Sequence[int],
    coalition_values: Mapping[int, int],
) -> tuple[tuple[int, ...], tuple[int, ...], int]:
    """Return (Q16 credits, exact numerators, terminal delta).

    Each exact rational is floored to Q16. Since Shapley efficiency makes
    the unquantized sum an integer multiple of Q16, the residual is in
    [0, PLAYER_COUNT-1]. One residual unit is assigned to each player in
    ascending immutable player-ID order.
    """
    ids = _validate(player_ids, coalition_values)
    numerators, full_delta = exact_shapley_numerators(ids, coalition_values)
    credits = [
        (numerator * Q16) // DENOMINATOR
        for numerator in numerators
    ]
    residual = full_delta * Q16 - sum(credits)
    if not 0 <= residual < PLAYER_COUNT:
        raise CoalitionContractError("Q16_RESIDUAL_OUT_OF_RANGE")

    index_by_id = sorted(range(PLAYER_COUNT), key=lambda index: ids[index])
    for index in index_by_id[:residual]:
        credits[index] += 1

    if sum(credits) != full_delta * Q16:
        raise CoalitionContractError("Q16_SHAPLEY_EFFICIENCY_INVARIANT")
    return tuple(credits), numerators, full_delta


def uniform_q16_credits(
    player_ids: Sequence[int],
    coalition_values: Mapping[int, int],
) -> tuple[int, ...]:
    """Equal-share terminal delta with the same deterministic Q16 residual rule."""
    ids = _validate(player_ids, coalition_values)
    delta = coalition_values[COALITION_COUNT - 1] - coalition_values[0]
    base = (delta * Q16) // PLAYER_COUNT
    credits = [base] * PLAYER_COUNT
    residual = delta * Q16 - base * PLAYER_COUNT
    index_by_id = sorted(range(PLAYER_COUNT), key=lambda index: ids[index])
    for index in index_by_id[:residual]:
        credits[index] += 1
    if sum(credits) != delta * Q16:
        raise CoalitionContractError("Q16_UNIFORM_EFFICIENCY_INVARIANT")
    return tuple(credits)


def leave_one_out_q16_credits(
    player_ids: Sequence[int],
    coalition_values: Mapping[int, int],
) -> tuple[int, ...]:
    """Raw full-coalition leave-one-out marginals; intentionally non-additive."""
    _validate(player_ids, coalition_values)
    full_mask = COALITION_COUNT - 1
    full_value = coalition_values[full_mask]
    return tuple(
        (full_value - coalition_values[full_mask ^ (1 << index)]) * Q16
        for index in range(PLAYER_COUNT)
    )
