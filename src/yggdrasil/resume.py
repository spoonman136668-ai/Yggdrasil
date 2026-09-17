from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import time

import torch
from torch import Tensor

from .damage import center_lesion
from .metrics import active_cell_count, ensure_finite, morphology_mse
from .nca import NeuralCellularAutomaton
from .pool import StatePool
from .training import TrainingConfig, TrainingSummary, training_morphology_loss


@dataclass
class ResumableTrainingSession:
    model: NeuralCellularAutomaton
    seed_state: Tensor
    target: Tensor
    config: TrainingConfig

    def __post_init__(self) -> None:
        self.config.validate(self.model)
        if self.seed_state.ndim != 4 or self.seed_state.shape[0] != 1:
            raise ValueError("seed_state must have batch size 1")
        if self.target.shape != self.seed_state.shape:
            raise ValueError("target must have the same shape as seed_state")
        if self.target.device != self.seed_state.device:
            raise ValueError("seed_state and target must be on the same device")
        if self.seed_state.dtype != self.target.dtype:
            raise TypeError("seed_state and target must have identical dtype")
        if self.seed_state.shape[1] != self.model.config.state_channels:
            raise ValueError("seed_state channels do not match model")

        self.device = self.seed_state.device
        self.cpu_rng = torch.Generator(device="cpu").manual_seed(self.config.seed)
        self.device_rng = torch.Generator(device=self.device.type).manual_seed(self.config.seed)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.config.learning_rate)
        self.pool = (
            StatePool(self.seed_state, capacity=self.config.pool_size)
            if self.config.variant != "growth_only"
            else None
        )
        self.target_batch = self.target.repeat(self.config.batch_size, 1, 1, 1)
        self.iteration = 0
        self.history: list[dict[str, float | int]] = []
        self.elapsed_seconds = 0.0

    @property
    def complete(self) -> bool:
        return self.iteration >= self.config.iterations

    def advance(self, iterations: int) -> None:
        if iterations < 0:
            raise ValueError("iterations must be non-negative")
        if self.iteration + iterations > self.config.iterations:
            raise ValueError("segment would exceed configured training iterations")
        started = time.perf_counter()
        for _ in range(iterations):
            self._one_iteration()
        self.elapsed_seconds += time.perf_counter() - started

    def _one_iteration(self) -> None:
        iteration = self.iteration
        if self.pool is None:
            states = self.seed_state.repeat(self.config.batch_size, 1, 1, 1)
            indices = None
        else:
            indices, states = self.pool.sample(
                self.config.batch_size,
                generator=self.cpu_rng,
                device=self.device,
            )
            states[0] = self.seed_state[0]

            if self.config.variant == "regeneration":
                draw = float(torch.rand((), generator=self.cpu_rng).item())
                if draw < self.config.damage_probability:
                    candidates = states[1:].clone()
                    for candidate_index in range(candidates.shape[0]):
                        candidate = candidates[candidate_index : candidate_index + 1]
                        live_cells = active_cell_count(
                            candidate,
                            alive_channel=self.model.config.alive_channel,
                            alive_threshold=self.model.config.alive_threshold,
                        )
                        if live_cells >= self.config.damage_min_active_cells:
                            candidates[candidate_index : candidate_index + 1] = center_lesion(
                                candidate,
                                height_fraction=self.config.damage_height_fraction,
                                width_fraction=self.config.damage_width_fraction,
                                alive_channel=self.model.config.alive_channel,
                                alive_threshold=self.model.config.alive_threshold,
                            )
                    states = torch.cat((states[:1], candidates), dim=0)

        steps = int(
            torch.randint(
                self.config.steps_min,
                self.config.steps_max + 1,
                (1,),
                generator=self.cpu_rng,
            ).item()
        )
        self.optimizer.zero_grad(set_to_none=True)
        result = self.model.run(states, steps=steps, generator=self.device_rng)
        ensure_finite(result)
        global_morphology_mse = morphology_mse(
            result,
            self.target_batch,
            visible_channels=self.config.visible_channels,
        )
        morphology_loss = training_morphology_loss(
            result=result,
            target=self.target_batch,
            config=self.config,
        )
        hidden_penalty = (
            torch.mean(result[:, self.config.visible_channels :] ** 2)
            if self.config.visible_channels < result.shape[1]
            else torch.zeros((), device=self.device, dtype=result.dtype)
        )
        loss = morphology_loss + self.config.hidden_state_l2_weight * hidden_penalty
        if not torch.isfinite(loss):
            raise FloatingPointError("non-finite training loss")
        loss.backward()
        grad_norm = float(
            torch.nn.utils.clip_grad_norm_(
                self.model.parameters(),
                max_norm=self.config.gradient_clip_norm,
            ).item()
        )
        self.optimizer.step()
        if self.pool is not None:
            assert indices is not None
            self.pool.update(indices, result)

        if (
            iteration == 0
            or iteration == self.config.iterations - 1
            or (iteration + 1) % self.config.record_every == 0
        ):
            self.history.append(
                {
                    "iteration": iteration + 1,
                    "steps": steps,
                    "loss": float(loss.detach().item()),
                    "morphology_loss": float(morphology_loss.detach().item()),
                    "global_morphology_mse": float(global_morphology_mse.detach().item()),
                    "hidden_penalty": float(hidden_penalty.detach().item()),
                    "gradient_norm": grad_norm,
                }
            )
        self.iteration += 1

    def summary(self) -> TrainingSummary:
        if not self.history:
            raise RuntimeError("training session has no recorded iterations")
        losses = [float(item["loss"]) for item in self.history]
        return TrainingSummary(
            variant=self.config.variant,
            loss_mode=self.config.loss_mode,
            iterations=self.iteration,
            initial_recorded_loss=losses[0],
            final_recorded_loss=losses[-1],
            minimum_recorded_loss=min(losses),
            elapsed_seconds=self.elapsed_seconds,
            history=tuple(deepcopy(self.history)),
        )

    def checkpoint_state(self) -> dict[str, object]:
        return {
            "version": 1,
            "iteration": self.iteration,
            "model_state_dict": deepcopy(self.model.state_dict()),
            "optimizer_state_dict": deepcopy(self.optimizer.state_dict()),
            "pool_state_dict": self.pool.state_dict() if self.pool is not None else None,
            "cpu_rng_state": self.cpu_rng.get_state().clone(),
            "device_rng_state": self.device_rng.get_state().clone(),
            "history": deepcopy(self.history),
        }

    def load_checkpoint_state(self, state: dict[str, object]) -> None:
        required = {
            "version", "iteration", "model_state_dict", "optimizer_state_dict",
            "pool_state_dict", "cpu_rng_state", "device_rng_state", "history"
        }
        if set(state) != required:
            raise ValueError("training checkpoint fields do not match expected schema")
        if int(state["version"]) != 1:
            raise ValueError("unsupported training checkpoint version")
        iteration = int(state["iteration"])
        if not 0 <= iteration <= self.config.iterations:
            raise ValueError("checkpoint iteration outside configured range")
        self.model.load_state_dict(state["model_state_dict"])
        self.optimizer.load_state_dict(state["optimizer_state_dict"])
        self._move_optimizer_state_to_device()
        if self.pool is None:
            if state["pool_state_dict"] is not None:
                raise ValueError("growth-only checkpoint must not contain pool state")
        else:
            pool_state = state["pool_state_dict"]
            if not isinstance(pool_state, dict):
                raise TypeError("pooled training checkpoint requires pool state")
            self.pool.load_state_dict(pool_state)
        self.cpu_rng.set_state(state["cpu_rng_state"])
        self.device_rng.set_state(state["device_rng_state"])
        history = state["history"]
        if not isinstance(history, list):
            raise TypeError("checkpoint history must be a list")
        self.history = deepcopy(history)
        self.iteration = iteration

    def _move_optimizer_state_to_device(self) -> None:
        for optimizer_state in self.optimizer.state.values():
            for key, value in list(optimizer_state.items()):
                if isinstance(value, Tensor):
                    optimizer_state[key] = value.to(self.device)
