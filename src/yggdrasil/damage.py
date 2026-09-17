from __future__ import annotations

import torch
from torch import Tensor


def rectangular_lesion(
    state: Tensor,
    *,
    top: int,
    left: int,
    height: int,
    width: int,
) -> Tensor:
    _validate_state(state)
    grid_h, grid_w = state.shape[-2:]
    if height <= 0 or width <= 0:
        raise ValueError("lesion height and width must be positive")
    if top < 0 or left < 0 or top + height > grid_h or left + width > grid_w:
        raise ValueError("rectangular lesion lies outside the fixed grid")

    damaged = state.clone()
    damaged[:, :, top : top + height, left : left + width] = 0
    return damaged


def center_lesion(
    state: Tensor,
    *,
    height_fraction: float,
    width_fraction: float,
    alive_channel: int = 3,
    alive_threshold: float = 0.1,
) -> Tensor:
    _validate_state(state)
    _validate_fraction(height_fraction, "height_fraction")
    _validate_fraction(width_fraction, "width_fraction")
    if not 0 <= alive_channel < state.shape[1]:
        raise ValueError("alive_channel is outside the state vector")

    damaged = state.clone()
    for batch_index in range(state.shape[0]):
        live = state[batch_index, alive_channel] > alive_threshold
        coords = live.nonzero(as_tuple=False)
        if coords.numel() == 0:
            continue

        y_min = int(coords[:, 0].min().item())
        y_max = int(coords[:, 0].max().item())
        x_min = int(coords[:, 1].min().item())
        x_max = int(coords[:, 1].max().item())

        bbox_h = y_max - y_min + 1
        bbox_w = x_max - x_min + 1
        lesion_h = max(1, round(bbox_h * height_fraction))
        lesion_w = max(1, round(bbox_w * width_fraction))

        center_y = (y_min + y_max) // 2
        center_x = (x_min + x_max) // 2
        top = max(y_min, min(center_y - lesion_h // 2, y_max - lesion_h + 1))
        left = max(x_min, min(center_x - lesion_w // 2, x_max - lesion_w + 1))

        damaged[
            batch_index,
            :,
            top : top + lesion_h,
            left : left + lesion_w,
        ] = 0

    return damaged


def dropout_live_cells(
    state: Tensor,
    *,
    fraction: float,
    alive_channel: int = 3,
    alive_threshold: float = 0.1,
    generator: torch.Generator | None = None,
) -> Tensor:
    _validate_state(state)
    if not 0.0 <= fraction <= 1.0:
        raise ValueError("fraction must be in [0, 1]")
    if not 0 <= alive_channel < state.shape[1]:
        raise ValueError("alive_channel is outside the state vector")

    live = state[:, alive_channel : alive_channel + 1] > alive_threshold
    random_values = torch.rand(
        live.shape,
        device=state.device,
        dtype=state.dtype,
        generator=generator,
    )
    drop = live & (random_values < fraction)
    damaged = state.clone()
    return damaged.masked_fill(drop.expand_as(damaged), 0)


def _validate_fraction(value: float, name: str) -> None:
    if not 0.0 < value <= 1.0:
        raise ValueError(f"{name} must be in (0, 1]")


def _validate_state(state: Tensor) -> None:
    if state.ndim != 4:
        raise ValueError("state must have shape [batch, channels, height, width]")
    if not state.is_floating_point():
        raise TypeError("state must use a floating-point dtype")
