from __future__ import annotations

import torch
from torch import Tensor


class StatePool:
    """Finite detached phenotype-state pool for persistence/regeneration curricula."""

    def __init__(self, seed_state: Tensor, *, capacity: int) -> None:
        if seed_state.ndim != 4 or seed_state.shape[0] != 1:
            raise ValueError("seed_state must have shape [1, channels, height, width]")
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if not seed_state.is_floating_point():
            raise TypeError("seed_state must use a floating-point dtype")

        self._capacity = capacity
        self._storage = seed_state.detach().cpu().repeat(capacity, 1, 1, 1).clone()

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def sample_shape(self) -> tuple[int, ...]:
        return tuple(self._storage.shape[1:])

    def sample(
        self,
        batch_size: int,
        *,
        generator: torch.Generator,
        device: torch.device | str,
    ) -> tuple[Tensor, Tensor]:
        if not 0 < batch_size <= self._capacity:
            raise ValueError("batch_size must be in [1, capacity]")
        indices = torch.randperm(self._capacity, generator=generator)[:batch_size]
        batch = self._storage.index_select(0, indices).to(device=device).clone()
        return indices, batch

    def update(self, indices: Tensor, states: Tensor) -> None:
        if indices.ndim != 1:
            raise ValueError("indices must be one-dimensional")
        if states.ndim != 4 or states.shape[0] != indices.numel():
            raise ValueError("states batch dimension must match indices")
        if tuple(states.shape[1:]) != self.sample_shape:
            raise ValueError("states do not match pool sample shape")
        if indices.numel() == 0:
            return
        if int(indices.min().item()) < 0 or int(indices.max().item()) >= self._capacity:
            raise IndexError("pool index out of range")
        self._storage.index_copy_(0, indices.cpu(), states.detach().cpu())

    def reset(self, indices: Tensor, seed_state: Tensor) -> None:
        if seed_state.ndim != 4 or seed_state.shape[0] != 1:
            raise ValueError("seed_state must have shape [1, channels, height, width]")
        reset_states = seed_state.detach().cpu().repeat(indices.numel(), 1, 1, 1)
        self.update(indices, reset_states)
