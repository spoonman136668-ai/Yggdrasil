from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import Tensor, nn
from torch.nn import functional as F


@dataclass(frozen=True)
class NCAConfig:
    state_channels: int = 16
    hidden_channels: int = 128
    fire_rate: float = 0.5
    alive_channel: int = 3
    alive_threshold: float = 0.1
    max_steps: int = 256

    def validate(self) -> None:
        if self.state_channels < 4:
            raise ValueError("state_channels must be at least 4 for RGBA-visible state")
        if self.hidden_channels <= 0:
            raise ValueError("hidden_channels must be positive")
        if not 0.0 < self.fire_rate <= 1.0:
            raise ValueError("fire_rate must be in (0, 1]")
        if not 0 <= self.alive_channel < self.state_channels:
            raise ValueError("alive_channel is outside the state vector")
        if self.alive_threshold < 0.0:
            raise ValueError("alive_threshold must be non-negative")
        if self.max_steps <= 0:
            raise ValueError("max_steps must be positive")


class NeuralCellularAutomaton(nn.Module):
    """A bounded Growing-NCA-style shared local update rule.

    All grid cells use the same update network. The phenotype has no privileged
    global execution state and cannot dynamically resize its grid.
    """

    def __init__(self, config: NCAConfig | None = None) -> None:
        super().__init__()
        self.config = config or NCAConfig()
        self.config.validate()

        kernels = torch.tensor(
            [
                [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]],
                [[-1.0, 0.0, 1.0], [-2.0, 0.0, 2.0], [-1.0, 0.0, 1.0]],
                [[-1.0, -2.0, -1.0], [0.0, 0.0, 0.0], [1.0, 2.0, 1.0]],
            ],
            dtype=torch.float32,
        ).unsqueeze(1)
        kernels[1:] /= 8.0
        self.register_buffer("perception_kernels", kernels, persistent=False)

        perception_channels = self.config.state_channels * 3
        self.update_net = nn.Sequential(
            nn.Conv2d(perception_channels, self.config.hidden_channels, kernel_size=1),
            nn.ReLU(),
            nn.Conv2d(self.config.hidden_channels, self.config.state_channels, kernel_size=1, bias=False),
        )

        final_layer = self.update_net[-1]
        assert isinstance(final_layer, nn.Conv2d)
        nn.init.zeros_(final_layer.weight)

    def perceive(self, state: Tensor) -> Tensor:
        self._validate_state(state)
        channels = state.shape[1]
        kernels = self.perception_kernels.to(dtype=state.dtype, device=state.device)
        weights = kernels.repeat(channels, 1, 1, 1)
        return F.conv2d(state, weights, padding=1, groups=channels)

    def alive_mask(self, state: Tensor) -> Tensor:
        self._validate_state(state)
        alpha = state[:, self.config.alive_channel : self.config.alive_channel + 1]
        neighborhood_alpha = F.max_pool2d(alpha, kernel_size=3, stride=1, padding=1)
        return neighborhood_alpha > self.config.alive_threshold

    def step(self, state: Tensor, *, generator: torch.Generator | None = None) -> Tensor:
        self._validate_state(state)
        pre_alive = self.alive_mask(state)
        perception = self.perceive(state)
        delta = self.update_net(perception)

        if self.config.fire_rate < 1.0:
            mask = torch.rand(
                (state.shape[0], 1, state.shape[2], state.shape[3]),
                dtype=state.dtype,
                device=state.device,
                generator=generator,
            ) <= self.config.fire_rate
            delta = delta * mask.to(dtype=state.dtype)

        next_state = state + delta
        post_alive = self.alive_mask(next_state)
        living = (pre_alive & post_alive).to(dtype=state.dtype)
        return next_state * living

    def run(
        self,
        state: Tensor,
        steps: int,
        *,
        generator: torch.Generator | None = None,
    ) -> Tensor:
        self._validate_state(state)
        if not 0 <= steps <= self.config.max_steps:
            raise ValueError(f"steps must be between 0 and {self.config.max_steps}")
        result = state
        for _ in range(steps):
            result = self.step(result, generator=generator)
        return result

    def parameter_count(self) -> int:
        return sum(parameter.numel() for parameter in self.parameters())

    def _validate_state(self, state: Tensor) -> None:
        if state.ndim != 4:
            raise ValueError("state must have shape [batch, channels, height, width]")
        if state.shape[1] != self.config.state_channels:
            raise ValueError(
                f"state has {state.shape[1]} channels; expected {self.config.state_channels}"
            )
        if not state.is_floating_point():
            raise TypeError("state must use a floating-point dtype")


def make_seed_state(
    *,
    batch_size: int,
    channels: int,
    height: int,
    width: int,
    alive_channel: int = 3,
    device: torch.device | str | None = None,
    dtype: torch.dtype = torch.float32,
) -> Tensor:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if channels < 4:
        raise ValueError("channels must be at least 4")
    if height <= 0 or width <= 0:
        raise ValueError("height and width must be positive")
    if not 0 <= alive_channel < channels:
        raise ValueError("alive_channel is outside the state vector")

    state = torch.zeros((batch_size, channels, height, width), device=device, dtype=dtype)
    state[:, alive_channel, height // 2, width // 2] = 1.0
    return state
