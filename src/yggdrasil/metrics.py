from __future__ import annotations

import math
from collections.abc import Sequence

import torch
from torch import Tensor


def morphology_mse(state: Tensor, target: Tensor, *, visible_channels: int = 4) -> Tensor:
    _validate_pair(state, target)
    if visible_channels <= 0 or visible_channels > state.shape[1]:
        raise ValueError("visible_channels is outside the state vector")
    return torch.mean((state[:, :visible_channels] - target[:, :visible_channels]) ** 2)


def active_cell_count(
    state: Tensor,
    *,
    alive_channel: int = 3,
    alive_threshold: float = 0.1,
) -> int:
    _validate_state(state)
    if not 0 <= alive_channel < state.shape[1]:
        raise ValueError("alive_channel is outside the state vector")
    return int((state[:, alive_channel] > alive_threshold).sum().item())


def mean_update_magnitude(before: Tensor, after: Tensor) -> float:
    _validate_pair(before, after)
    return float(torch.mean(torch.abs(after - before)).item())


def recovery_fraction(
    *,
    pre_error: float,
    post_damage_error: float,
    recovered_error: float,
    eps: float = 1e-12,
) -> float:
    """Raw recovery fraction for a lower-is-better error metric."""
    lost = post_damage_error - pre_error
    if lost <= eps:
        return math.nan
    recovered = post_damage_error - recovered_error
    return recovered / lost


def normalized_recovery_fraction(
    *,
    pre_error: float,
    post_damage_error: float,
    recovered_error: float,
    eps: float = 1e-12,
) -> float:
    """Bounded recovery fraction in [0, 1] for a lower-is-better error metric."""
    raw = recovery_fraction(
        pre_error=pre_error,
        post_damage_error=post_damage_error,
        recovered_error=recovered_error,
        eps=eps,
    )
    if math.isnan(raw):
        return raw
    return min(1.0, max(0.0, raw))


def recovery_threshold_step(
    errors: Sequence[float],
    *,
    pre_error: float,
    post_damage_error: float,
    fraction: float,
    eps: float = 1e-12,
) -> int | None:
    if not 0.0 < fraction <= 1.0:
        raise ValueError("fraction must be in (0, 1]")
    lost = post_damage_error - pre_error
    if lost <= eps:
        return None
    target = post_damage_error - fraction * lost
    for index, error in enumerate(errors):
        if error <= target:
            return index
    return None


def stable_recovery_threshold_step(
    errors: Sequence[float],
    *,
    pre_error: float,
    post_damage_error: float,
    fraction: float,
    eps: float = 1e-12,
) -> int | None:
    """Earliest threshold crossing that remains satisfied for the rest of the window."""
    if not 0.0 < fraction <= 1.0:
        raise ValueError("fraction must be in (0, 1]")
    lost = post_damage_error - pre_error
    if lost <= eps:
        return None
    target = post_damage_error - fraction * lost
    for index in range(len(errors)):
        if all(error <= target for error in errors[index:]):
            return index
    return None


def normalized_recovery_auc(
    errors: Sequence[float],
    *,
    pre_error: float,
    post_damage_error: float,
    eps: float = 1e-12,
) -> float:
    if len(errors) == 0:
        raise ValueError("errors must not be empty")
    lost = post_damage_error - pre_error
    if lost <= eps:
        return math.nan

    fractions = [
        min(1.0, max(0.0, (post_damage_error - error) / lost))
        for error in errors
    ]
    if len(fractions) == 1:
        return fractions[0]

    area = 0.0
    for left, right in zip(fractions, fractions[1:]):
        area += 0.5 * (left + right)
    return area / (len(fractions) - 1)


def ensure_finite(state: Tensor) -> None:
    _validate_state(state)
    if not torch.isfinite(state).all():
        raise FloatingPointError("non-finite values detected in phenotype state")


def _validate_pair(left: Tensor, right: Tensor) -> None:
    _validate_state(left)
    _validate_state(right)
    if left.shape != right.shape:
        raise ValueError("tensors must have identical shape")
    if left.dtype != right.dtype:
        raise TypeError("tensors must have identical dtype")
    if left.device != right.device:
        raise ValueError("tensors must be on the same device")


def _validate_state(state: Tensor) -> None:
    if state.ndim != 4:
        raise ValueError("state must have shape [batch, channels, height, width]")
    if not state.is_floating_point():
        raise TypeError("state must use a floating-point dtype")
