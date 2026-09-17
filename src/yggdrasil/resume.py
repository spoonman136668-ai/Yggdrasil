from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass
import time
import torch
from torch import Tensor
from .damage import center_lesion
from .metrics import active_cell_count, background_alive_margin_loss, background_alpha_mse, ensure_finite, foreground_morphology_mse, far_field_background_alpha_mse, graded_background_alpha_mse, homeostasis_background_velocity_loss, homeostasis_mature_sample_mask, morphology_mse
from .nca import NeuralCellularAutomaton
from .pool import StatePool
from .training import TrainingConfig, TrainingSummary, _rng_neutral_homeostasis_probe, training_morphology_loss

@dataclass
class ResumableTrainingSession:
    model: NeuralCellularAutomaton
    seed_state: Tensor
    target: Tensor
    config: TrainingConfig

    def __post_init__(self) -> None:
        self.config.validate(self.model)
        if self.seed_state.ndim != 4 or self.seed_state.shape[0] != 1:
            raise ValueError('seed_state must have batch size 1')
        if self.target.shape != self.seed_state.shape:
            raise ValueError('target must have the same shape as seed_state')
        if self.target.device != self.seed_state.device:
            raise ValueError('seed_state and target must be on the same device')
        if self.seed_state.dtype != self.target.dtype:
            raise TypeError('seed_state and target must have identical dtype')
        if self.seed_state.shape[1] != self.model.config.state_channels:
            raise ValueError('seed_state channels do not match model')
        self.device = self.seed_state.device
        self.cpu_rng = torch.Generator(device='cpu').manual_seed(self.config.seed)
        self.device_rng = torch.Generator(device=self.device.type).manual_seed(self.config.seed)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.config.learning_rate)
        self.pool = StatePool(self.seed_state, capacity=self.config.pool_size) if self.config.variant != 'growth_only' else None
        self.target_batch = self.target.repeat(self.config.batch_size, 1, 1, 1)
        self.iteration = 0
        self.history = []
        self.elapsed_seconds = 0.0

    @property
    def complete(self) -> bool:
        return self.iteration >= self.config.iterations

    def advance(self, iterations: int) -> None:
        if iterations < 0:
            raise ValueError('iterations must be non-negative')
        if self.iteration + iterations > self.config.iterations:
            raise ValueError('segment would exceed configured training iterations')
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
            indices, states = self.pool.sample(self.config.batch_size, generator=self.cpu_rng, device=self.device)
            states[0] = self.seed_state[0]
            if self.config.variant == 'regeneration':
                draw = float(torch.rand((), generator=self.cpu_rng).item())
                if draw < self.config.damage_probability:
                    candidates = states[1:].clone()
                    for i in range(candidates.shape[0]):
                        candidate = candidates[i:i + 1]
                        live = active_cell_count(candidate, alive_channel=self.model.config.alive_channel, alive_threshold=self.model.config.alive_threshold)
                        if live >= self.config.damage_min_active_cells:
                            candidates[i:i + 1] = center_lesion(candidate, height_fraction=self.config.damage_height_fraction, width_fraction=self.config.damage_width_fraction, alive_channel=self.model.config.alive_channel, alive_threshold=self.model.config.alive_threshold)
                    states = torch.cat((states[:1], candidates), dim=0)
        steps = int(torch.randint(self.config.steps_min, self.config.steps_max + 1, (1,), generator=self.cpu_rng).item())
        self.optimizer.zero_grad(set_to_none=True)
        result = self.model.run(states, steps=steps, generator=self.device_rng)
        ensure_finite(result)
        global_mse = morphology_mse(result, self.target_batch, visible_channels=self.config.visible_channels)
        homeostasis_loss = None
        homeostasis_mature_samples = 0
        if self.config.loss_mode == 'global_plus_foreground_bg_alpha_homeostasis':
            mature_mask = homeostasis_mature_sample_mask(result, self.target_batch, alpha_channel=3, foreground_threshold=0.1, alive_threshold=self.model.config.alive_threshold)
            homeostasis_mature_samples = int(mature_mask.sum().item())
            if homeostasis_mature_samples > 0:
                mature_result = result[mature_mask]
                mature_target = self.target_batch[mature_mask]
                probe = _rng_neutral_homeostasis_probe(model=self.model, result=mature_result, generator=self.device_rng)
                ensure_finite(probe)
                homeostasis_loss = homeostasis_background_velocity_loss(mature_result, probe, mature_target, alpha_channel=3, foreground_threshold=0.1, alive_threshold=self.model.config.alive_threshold)
            else:
                homeostasis_loss = result.sum() * 0.0
        morph = training_morphology_loss(result=result, target=self.target_batch, config=self.config, homeostasis_loss=homeostasis_loss)
        hidden = torch.mean(result[:, self.config.visible_channels:] ** 2) if self.config.visible_channels < result.shape[1] else torch.zeros((), device=self.device, dtype=result.dtype)
        loss = morph + self.config.hidden_state_l2_weight * hidden
        if not torch.isfinite(loss):
            raise FloatingPointError('non-finite training loss')
        loss.backward()
        grad = float(torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=self.config.gradient_clip_norm).item())
        self.optimizer.step()
        if self.pool is not None:
            assert indices is not None
            self.pool.update(indices, result)
        if iteration == 0 or iteration == self.config.iterations - 1 or (iteration + 1) % self.config.record_every == 0:
            item = {'iteration': iteration + 1, 'steps': steps, 'loss': float(loss.detach().item()), 'morphology_loss': float(morph.detach().item()), 'global_morphology_mse': float(global_mse.detach().item()), 'hidden_penalty': float(hidden.detach().item()), 'gradient_norm': grad}
            if self.config.loss_mode == 'global_plus_foreground_bg_alpha':
                item['foreground_morphology_mse'] = float(foreground_morphology_mse(result, self.target_batch, visible_channels=self.config.visible_channels, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['background_alpha_mse'] = float(background_alpha_mse(result, self.target_batch, alpha_channel=3, foreground_threshold=0.1).detach().item())
            if self.config.loss_mode == 'global_plus_foreground_bg_alive_margin':
                item['foreground_morphology_mse'] = float(foreground_morphology_mse(result, self.target_batch, visible_channels=self.config.visible_channels, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['background_alive_margin_loss'] = float(background_alive_margin_loss(result, self.target_batch, alpha_channel=3, foreground_threshold=0.1, margin_floor=0.05, alive_threshold=0.1).detach().item())
            if self.config.loss_mode == 'global_plus_foreground_farfield_bg_alpha':
                item['foreground_morphology_mse'] = float(foreground_morphology_mse(result, self.target_batch, visible_channels=self.config.visible_channels, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['far_field_background_alpha_mse'] = float(far_field_background_alpha_mse(result, self.target_batch, alpha_channel=3, foreground_threshold=0.1, support_radius=1).detach().item())
            if self.config.loss_mode == 'global_plus_foreground_graded_bg_alpha':
                item['foreground_morphology_mse'] = float(foreground_morphology_mse(result, self.target_batch, visible_channels=self.config.visible_channels, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['graded_background_alpha_mse'] = float(graded_background_alpha_mse(result, self.target_batch, alpha_channel=3, foreground_threshold=0.1).detach().item())
            if self.config.loss_mode == 'global_plus_foreground_bg_alpha_homeostasis':
                item['foreground_morphology_mse'] = float(foreground_morphology_mse(result, self.target_batch, visible_channels=self.config.visible_channels, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['background_alpha_mse'] = float(background_alpha_mse(result, self.target_batch, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['homeostasis_background_velocity_loss'] = float(homeostasis_loss.detach().item()) if homeostasis_loss is not None else 0.0
                item['homeostasis_mature_samples'] = homeostasis_mature_samples
            self.history.append(item)
        self.iteration += 1

    def summary(self) -> TrainingSummary:
        if not self.history:
            raise RuntimeError('training session has no recorded iterations')
        losses = [float(x['loss']) for x in self.history]
        return TrainingSummary(self.config.variant, self.config.loss_mode, self.iteration, losses[0], losses[-1], min(losses), self.elapsed_seconds, tuple(deepcopy(self.history)))

    def checkpoint_state(self) -> dict[str, object]:
        return {'version': 1, 'iteration': self.iteration, 'model_state_dict': deepcopy(self.model.state_dict()), 'optimizer_state_dict': deepcopy(self.optimizer.state_dict()), 'pool_state_dict': self.pool.state_dict() if self.pool is not None else None, 'cpu_rng_state': self.cpu_rng.get_state().clone(), 'device_rng_state': self.device_rng.get_state().clone(), 'history': deepcopy(self.history)}

    def load_checkpoint_state(self, state: dict[str, object]) -> None:
        required = {'version', 'iteration', 'model_state_dict', 'optimizer_state_dict', 'pool_state_dict', 'cpu_rng_state', 'device_rng_state', 'history'}
        if set(state) != required:
            raise ValueError('training checkpoint fields do not match expected schema')
        if int(state['version']) != 1:
            raise ValueError('unsupported training checkpoint version')
        iteration = int(state['iteration'])
        if not 0 <= iteration <= self.config.iterations:
            raise ValueError('checkpoint iteration outside configured range')
        self.model.load_state_dict(state['model_state_dict'])
        self.optimizer.load_state_dict(state['optimizer_state_dict'])
        self._move_optimizer_state_to_device()
        if self.pool is None:
            if state['pool_state_dict'] is not None:
                raise ValueError('growth-only checkpoint must not contain pool state')
        else:
            pool_state = state['pool_state_dict']
            if not isinstance(pool_state, dict):
                raise TypeError('pooled training checkpoint requires pool state')
            self.pool.load_state_dict(pool_state)
        self.cpu_rng.set_state(state['cpu_rng_state'])
        self.device_rng.set_state(state['device_rng_state'])
        history = state['history']
        if not isinstance(history, list):
            raise TypeError('checkpoint history must be a list')
        self.history = deepcopy(history)
        self.iteration = iteration

    def _move_optimizer_state_to_device(self) -> None:
        for optimizer_state in self.optimizer.state.values():
            for key, value in list(optimizer_state.items()):
                if isinstance(value, Tensor):
                    optimizer_state[key] = value.to(self.device)
