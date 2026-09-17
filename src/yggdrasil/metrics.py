from __future__ import annotations
import math
from collections.abc import Sequence
import torch
from torch import Tensor

def morphology_mse(state: Tensor, target: Tensor, *, visible_channels: int=4) -> Tensor:
    _validate_pair(state, target)
    if visible_channels <= 0 or visible_channels > state.shape[1]:
        raise ValueError('visible_channels is outside the state vector')
    return torch.mean((state[:, :visible_channels] - target[:, :visible_channels]) ** 2)

def foreground_morphology_mse(state: Tensor, target: Tensor, *, visible_channels: int=4, alpha_channel: int=3, foreground_threshold: float=0.1) -> Tensor:
    _validate_pair(state, target)
    if visible_channels <= 0 or visible_channels > state.shape[1]:
        raise ValueError('visible_channels is outside the state vector')
    if not 0 <= alpha_channel < target.shape[1]:
        raise ValueError('alpha_channel is outside the target state vector')
    foreground = target[:, alpha_channel:alpha_channel + 1] > foreground_threshold
    if not bool(foreground.any()):
        raise ValueError('target contains no foreground pixels')
    squared_error = (state[:, :visible_channels] - target[:, :visible_channels]) ** 2
    return squared_error.masked_select(foreground.expand(-1, visible_channels, -1, -1)).mean()

def background_alpha_mse(state: Tensor, target: Tensor, *, alpha_channel: int=3, foreground_threshold: float=0.1) -> Tensor:
    _validate_pair(state, target)
    if not 0 <= alpha_channel < target.shape[1]:
        raise ValueError('alpha_channel is outside the target state vector')
    background = target[:, alpha_channel:alpha_channel + 1] <= foreground_threshold
    if not bool(background.any()):
        raise ValueError('target contains no background pixels')
    alpha_squared = state[:, alpha_channel:alpha_channel + 1] ** 2
    return alpha_squared.masked_select(background).mean()

def far_field_background_alpha_mse(state: Tensor, target: Tensor, *, alpha_channel: int=3, foreground_threshold: float=0.1, support_radius: int=1) -> Tensor:
    _validate_pair(state, target)
    if not 0 <= alpha_channel < target.shape[1]:
        raise ValueError('alpha_channel is outside the target state vector')
    if support_radius <= 0:
        raise ValueError('support_radius must be positive')
    foreground = target[:, alpha_channel:alpha_channel + 1] > foreground_threshold
    if not bool(foreground.any()):
        raise ValueError('target contains no foreground pixels')
    k = 2 * support_radius + 1
    support = torch.nn.functional.max_pool2d(foreground.to(dtype=state.dtype), kernel_size=k, stride=1, padding=support_radius) > 0
    far_field = ~foreground & ~support
    if not bool(far_field.any()):
        raise ValueError('target contains no far-field background pixels')
    alpha2 = state[:, alpha_channel:alpha_channel + 1] ** 2
    return alpha2.masked_select(far_field).mean()

def background_alive_margin_loss(state: Tensor, target: Tensor, *, alpha_channel: int=3, foreground_threshold: float=0.1, margin_floor: float=0.05, alive_threshold: float=0.1) -> Tensor:
    _validate_pair(state, target)
    if not 0 <= alpha_channel < target.shape[1]:
        raise ValueError('alpha_channel is outside the target state vector')
    if not 0.0 <= margin_floor < alive_threshold:
        raise ValueError('margin_floor must be non-negative and below alive_threshold')
    background = target[:, alpha_channel:alpha_channel + 1] <= foreground_threshold
    if not bool(background.any()):
        raise ValueError('target contains no background pixels')
    margin_width = alive_threshold - margin_floor
    alpha = state[:, alpha_channel:alpha_channel + 1]
    normalized_margin = torch.relu(alpha - margin_floor) / margin_width
    return (normalized_margin ** 2).masked_select(background).mean()

def balanced_morphology_mse(state: Tensor, target: Tensor, *, visible_channels: int=4, alpha_channel: int=3, foreground_threshold: float=0.1, foreground_weight: float=0.5) -> Tensor:
    _validate_pair(state, target)
    if visible_channels <= 0 or visible_channels > state.shape[1]:
        raise ValueError('visible_channels is outside the state vector')
    if not 0 <= alpha_channel < target.shape[1]:
        raise ValueError('alpha_channel is outside the target state vector')
    if not 0.0 < foreground_weight < 1.0:
        raise ValueError('foreground_weight must be in (0, 1)')
    foreground = target[:, alpha_channel:alpha_channel + 1] > foreground_threshold
    background = ~foreground
    if not bool(foreground.any()):
        raise ValueError('target contains no foreground pixels')
    if not bool(background.any()):
        raise ValueError('target contains no background pixels')
    squared_error = (state[:, :visible_channels] - target[:, :visible_channels]) ** 2
    fg = squared_error.masked_select(foreground.expand(-1, visible_channels, -1, -1)).mean()
    bg = squared_error.masked_select(background.expand(-1, visible_channels, -1, -1)).mean()
    return foreground_weight * fg + (1.0 - foreground_weight) * bg

def active_cell_count(state: Tensor, *, alive_channel: int=3, alive_threshold: float=0.1) -> int:
    _validate_state(state)
    if not 0 <= alive_channel < state.shape[1]:
        raise ValueError('alive_channel is outside the state vector')
    return int((state[:, alive_channel] > alive_threshold).sum().item())

def mean_update_magnitude(before: Tensor, after: Tensor) -> float:
    _validate_pair(before, after)
    return float(torch.mean(torch.abs(after - before)).item())

def recovery_fraction(*, pre_error: float, post_damage_error: float, recovered_error: float, eps: float=1e-12) -> float:
    lost = post_damage_error - pre_error
    if lost <= eps:
        return math.nan
    return (post_damage_error - recovered_error) / lost

def normalized_recovery_fraction(*, pre_error: float, post_damage_error: float, recovered_error: float, eps: float=1e-12) -> float:
    raw = recovery_fraction(pre_error=pre_error, post_damage_error=post_damage_error, recovered_error=recovered_error, eps=eps)
    if math.isnan(raw):
        return raw
    return min(1.0, max(0.0, raw))

def recovery_threshold_step(errors: Sequence[float], *, pre_error: float, post_damage_error: float, fraction: float, eps: float=1e-12) -> int | None:
    if not 0.0 < fraction <= 1.0:
        raise ValueError('fraction must be in (0, 1]')
    lost = post_damage_error - pre_error
    if lost <= eps:
        return None
    target = post_damage_error - fraction * lost
    for index, error in enumerate(errors):
        if error <= target:
            return index
    return None

def stable_recovery_threshold_step(errors: Sequence[float], *, pre_error: float, post_damage_error: float, fraction: float, eps: float=1e-12) -> int | None:
    if not 0.0 < fraction <= 1.0:
        raise ValueError('fraction must be in (0, 1]')
    lost = post_damage_error - pre_error
    if lost <= eps:
        return None
    target = post_damage_error - fraction * lost
    for index in range(len(errors)):
        if all((error <= target for error in errors[index:])):
            return index
    return None

def normalized_recovery_auc(errors: Sequence[float], *, pre_error: float, post_damage_error: float, eps: float=1e-12) -> float:
    if len(errors) == 0:
        raise ValueError('errors must not be empty')
    lost = post_damage_error - pre_error
    if lost <= eps:
        return math.nan
    fractions = [min(1.0, max(0.0, (post_damage_error - error) / lost)) for error in errors]
    if len(fractions) == 1:
        return fractions[0]
    return sum((0.5 * (l + r) for l, r in zip(fractions, fractions[1:]))) / (len(fractions) - 1)

def ensure_finite(state: Tensor) -> None:
    _validate_state(state)
    if not torch.isfinite(state).all():
        raise FloatingPointError('non-finite values detected in phenotype state')

def _validate_pair(left: Tensor, right: Tensor) -> None:
    _validate_state(left)
    _validate_state(right)
    if left.shape != right.shape:
        raise ValueError('tensors must have identical shape')
    if left.dtype != right.dtype:
        raise TypeError('tensors must have identical dtype')
    if left.device != right.device:
        raise ValueError('tensors must be on the same device')

def _validate_state(state: Tensor) -> None:
    if state.ndim != 4:
        raise ValueError('state must have shape [batch, channels, height, width]')
    if not state.is_floating_point():
        raise TypeError('state must use a floating-point dtype')
