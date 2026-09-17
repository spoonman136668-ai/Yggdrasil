from __future__ import annotations
from dataclasses import asdict, dataclass
import math, time
from typing import Literal
import torch
from torch import Tensor
from .damage import center_lesion
from .metrics import active_cell_count, background_alive_margin_loss, background_alpha_mse, balanced_morphology_mse, ensure_finite, foreground_morphology_mse, far_field_background_alpha_mse, graded_background_alpha_mse, morphology_mse, mean_update_magnitude, normalized_recovery_auc, normalized_recovery_fraction, recovery_fraction, recovery_threshold_step, stable_recovery_threshold_step
from .nca import NeuralCellularAutomaton
from .pool import StatePool
from .resources import snapshot_resources
TrainingVariant = Literal['growth_only', 'persistence', 'regeneration']
TrainingLossMode = Literal['global_mse', 'balanced_fg_bg', 'global_plus_foreground', 'global_plus_foreground_bg_alpha', 'global_plus_foreground_bg_alive_margin', 'global_plus_foreground_farfield_bg_alpha', 'global_plus_foreground_graded_bg_alpha']

@dataclass(frozen=True)
class TrainingConfig:
    variant: TrainingVariant = 'growth_only'
    iterations: int = 200
    learning_rate: float = 0.001
    steps_min: int = 64
    steps_max: int = 96
    batch_size: int = 8
    pool_size: int = 64
    damage_probability: float = 0.5
    damage_height_fraction: float = 0.35
    damage_width_fraction: float = 0.35
    damage_min_active_cells: int = 16
    gradient_clip_norm: float = 1.0
    hidden_state_l2_weight: float = 1e-05
    loss_mode: TrainingLossMode = 'global_mse'
    visible_channels: int = 4
    record_every: int = 10
    seed: int = 0

    def validate(self, model: NeuralCellularAutomaton) -> None:
        if self.variant not in {'growth_only', 'persistence', 'regeneration'}:
            raise ValueError(f'unsupported training variant: {self.variant}')
        if self.iterations <= 0:
            raise ValueError('iterations must be positive')
        if self.learning_rate <= 0:
            raise ValueError('learning_rate must be positive')
        if not 0 < self.steps_min <= self.steps_max <= model.config.max_steps:
            raise ValueError('training step range exceeds model development limit')
        if self.batch_size <= 0:
            raise ValueError('batch_size must be positive')
        if self.pool_size < self.batch_size:
            raise ValueError('pool_size must be at least batch_size')
        if not 0.0 <= self.damage_probability <= 1.0:
            raise ValueError('damage_probability must be in [0, 1]')
        if not 0.0 < self.damage_height_fraction <= 1.0:
            raise ValueError('damage_height_fraction must be in (0, 1]')
        if not 0.0 < self.damage_width_fraction <= 1.0:
            raise ValueError('damage_width_fraction must be in (0, 1]')
        if self.damage_min_active_cells <= 0:
            raise ValueError('damage_min_active_cells must be positive')
        if self.gradient_clip_norm <= 0:
            raise ValueError('gradient_clip_norm must be positive')
        if self.hidden_state_l2_weight < 0:
            raise ValueError('hidden_state_l2_weight must be non-negative')
        if self.loss_mode not in {'global_mse', 'balanced_fg_bg', 'global_plus_foreground', 'global_plus_foreground_bg_alpha', 'global_plus_foreground_bg_alive_margin', 'global_plus_foreground_farfield_bg_alpha', 'global_plus_foreground_graded_bg_alpha'}:
            raise ValueError(f'unsupported training loss mode: {self.loss_mode}')
        if not 0 < self.visible_channels <= model.config.state_channels:
            raise ValueError('visible_channels is outside model state')
        if self.record_every <= 0:
            raise ValueError('record_every must be positive')

@dataclass(frozen=True)
class TrainingSummary:
    variant: str
    loss_mode: str
    iterations: int
    initial_recorded_loss: float
    final_recorded_loss: float
    minimum_recorded_loss: float
    elapsed_seconds: float
    history: tuple[dict[str, float | int], ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

def training_morphology_loss(*, result: Tensor, target: Tensor, config: TrainingConfig) -> Tensor:
    if config.loss_mode == 'global_mse':
        return morphology_mse(result, target, visible_channels=config.visible_channels)
    if config.loss_mode == 'balanced_fg_bg':
        return balanced_morphology_mse(result, target, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1, foreground_weight=0.5)
    if config.loss_mode == 'global_plus_foreground':
        return morphology_mse(result, target, visible_channels=config.visible_channels) + foreground_morphology_mse(result, target, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1)
    if config.loss_mode == 'global_plus_foreground_bg_alpha':
        return morphology_mse(result, target, visible_channels=config.visible_channels) + foreground_morphology_mse(result, target, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1) + background_alpha_mse(result, target, alpha_channel=3, foreground_threshold=0.1)
    if config.loss_mode == 'global_plus_foreground_bg_alive_margin':
        return morphology_mse(result, target, visible_channels=config.visible_channels) + foreground_morphology_mse(result, target, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1) + background_alive_margin_loss(result, target, alpha_channel=3, foreground_threshold=0.1, margin_floor=0.05, alive_threshold=0.1)
    if config.loss_mode == 'global_plus_foreground_farfield_bg_alpha':
        return morphology_mse(result, target, visible_channels=config.visible_channels) + foreground_morphology_mse(result, target, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1) + far_field_background_alpha_mse(result, target, alpha_channel=3, foreground_threshold=0.1, support_radius=1)
    if config.loss_mode == 'global_plus_foreground_graded_bg_alpha':
        return morphology_mse(result, target, visible_channels=config.visible_channels) + foreground_morphology_mse(result, target, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1) + graded_background_alpha_mse(result, target, alpha_channel=3, foreground_threshold=0.1)
    raise ValueError(f'unsupported training loss mode: {config.loss_mode}')

def train(*, model: NeuralCellularAutomaton, seed_state: Tensor, target: Tensor, config: TrainingConfig) -> TrainingSummary:
    config.validate(model)
    _validate_seed_target(seed_state, target, model)
    device = seed_state.device
    if target.device != device:
        raise ValueError('seed_state and target must be on the same device')
    cpu_rng = torch.Generator(device='cpu').manual_seed(config.seed)
    device_rng = torch.Generator(device=device.type).manual_seed(config.seed)
    optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
    pool = StatePool(seed_state, capacity=config.pool_size) if config.variant != 'growth_only' else None
    target_batch = target.repeat(config.batch_size, 1, 1, 1)
    history = []
    start = time.perf_counter()
    for iteration in range(config.iterations):
        if pool is None:
            states = seed_state.repeat(config.batch_size, 1, 1, 1)
            indices = None
        else:
            indices, states = pool.sample(config.batch_size, generator=cpu_rng, device=device)
            states[0] = seed_state[0]
            if config.variant == 'regeneration' and float(torch.rand((), generator=cpu_rng).item()) < config.damage_probability:
                candidates = states[1:].clone()
                for candidate_index in range(candidates.shape[0]):
                    candidate = candidates[candidate_index:candidate_index + 1]
                    live_cells = active_cell_count(candidate, alive_channel=model.config.alive_channel, alive_threshold=model.config.alive_threshold)
                    if live_cells >= config.damage_min_active_cells:
                        candidates[candidate_index:candidate_index + 1] = center_lesion(candidate, height_fraction=config.damage_height_fraction, width_fraction=config.damage_width_fraction, alive_channel=model.config.alive_channel, alive_threshold=model.config.alive_threshold)
                states = torch.cat((states[:1], candidates), dim=0)
        steps = int(torch.randint(config.steps_min, config.steps_max + 1, (1,), generator=cpu_rng).item())
        optimizer.zero_grad(set_to_none=True)
        result = model.run(states, steps=steps, generator=device_rng)
        ensure_finite(result)
        global_mse = morphology_mse(result, target_batch, visible_channels=config.visible_channels)
        morph = training_morphology_loss(result=result, target=target_batch, config=config)
        hidden = torch.mean(result[:, config.visible_channels:] ** 2) if config.visible_channels < result.shape[1] else torch.zeros((), device=device, dtype=result.dtype)
        loss = morph + config.hidden_state_l2_weight * hidden
        if not torch.isfinite(loss):
            raise FloatingPointError('non-finite training loss')
        loss.backward()
        grad_norm = float(torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=config.gradient_clip_norm).item())
        optimizer.step()
        if pool is not None:
            assert indices is not None
            pool.update(indices, result)
        if iteration == 0 or iteration == config.iterations - 1 or (iteration + 1) % config.record_every == 0:
            item = {'iteration': iteration + 1, 'steps': steps, 'loss': float(loss.detach().item()), 'morphology_loss': float(morph.detach().item()), 'global_morphology_mse': float(global_mse.detach().item()), 'hidden_penalty': float(hidden.detach().item()), 'gradient_norm': grad_norm}
            if config.loss_mode == 'global_plus_foreground_bg_alpha':
                item['foreground_morphology_mse'] = float(foreground_morphology_mse(result, target_batch, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['background_alpha_mse'] = float(background_alpha_mse(result, target_batch, alpha_channel=3, foreground_threshold=0.1).detach().item())
            if config.loss_mode == 'global_plus_foreground_bg_alive_margin':
                item['foreground_morphology_mse'] = float(foreground_morphology_mse(result, target_batch, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['background_alive_margin_loss'] = float(background_alive_margin_loss(result, target_batch, alpha_channel=3, foreground_threshold=0.1, margin_floor=0.05, alive_threshold=0.1).detach().item())
            if config.loss_mode == 'global_plus_foreground_farfield_bg_alpha':
                item['foreground_morphology_mse'] = float(foreground_morphology_mse(result, target_batch, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['far_field_background_alpha_mse'] = float(far_field_background_alpha_mse(result, target_batch, alpha_channel=3, foreground_threshold=0.1, support_radius=1).detach().item())
            if config.loss_mode == 'global_plus_foreground_graded_bg_alpha':
                item['foreground_morphology_mse'] = float(foreground_morphology_mse(result, target_batch, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['graded_background_alpha_mse'] = float(graded_background_alpha_mse(result, target_batch, alpha_channel=3, foreground_threshold=0.1).detach().item())
            history.append(item)
    elapsed = time.perf_counter() - start
    losses = [float(x['loss']) for x in history]
    return TrainingSummary(config.variant, config.loss_mode, config.iterations, losses[0], losses[-1], min(losses), elapsed, tuple(history))

def evaluate_growth_and_recovery(*, model: NeuralCellularAutomaton, seed_state: Tensor, target: Tensor, growth_steps: int, recovery_steps: int, seed: int, lesion_height_fraction: float, lesion_width_fraction: float, visible_channels: int=4) -> dict[str, object]:
    _validate_seed_target(seed_state, target, model)
    if not 0 <= growth_steps <= model.config.max_steps:
        raise ValueError('growth_steps exceeds model development limit')
    if not 0 <= recovery_steps <= model.config.max_steps:
        raise ValueError('recovery_steps exceeds model development limit')
    rng = torch.Generator(device=seed_state.device.type).manual_seed(seed)
    started = time.perf_counter()
    with torch.no_grad():
        grown = model.run(seed_state, steps=growth_steps, generator=rng)
        ensure_finite(grown)
        pre_error = float(morphology_mse(grown, target, visible_channels=visible_channels).item())
        pre_active = active_cell_count(grown, alive_channel=model.config.alive_channel, alive_threshold=model.config.alive_threshold)
        damaged = center_lesion(grown, height_fraction=lesion_height_fraction, width_fraction=lesion_width_fraction, alive_channel=model.config.alive_channel, alive_threshold=model.config.alive_threshold)
        post = float(morphology_mse(damaged, target, visible_channels=visible_channels).item())
        post_active = active_cell_count(damaged, alive_channel=model.config.alive_channel, alive_threshold=model.config.alive_threshold)
        errors = [post]
        active_cells = [post_active]
        current = damaged
        for _ in range(recovery_steps):
            current = model.step(current, generator=rng)
            ensure_finite(current)
            errors.append(float(morphology_mse(current, target, visible_channels=visible_channels).item()))
            active_cells.append(active_cell_count(current, alive_channel=model.config.alive_channel, alive_threshold=model.config.alive_threshold))
    elapsed = time.perf_counter() - started
    final_error = errors[-1]
    t50 = recovery_threshold_step(errors, pre_error=pre_error, post_damage_error=post, fraction=0.5)
    t90 = recovery_threshold_step(errors, pre_error=pre_error, post_damage_error=post, fraction=0.9)
    st50 = stable_recovery_threshold_step(errors, pre_error=pre_error, post_damage_error=post, fraction=0.5)
    st90 = stable_recovery_threshold_step(errors, pre_error=pre_error, post_damage_error=post, fraction=0.9)
    active = active_cells[-1]
    resources = snapshot_resources(model=model, state=current, active_cells=active)
    damage_effect = post - pre_error
    relative = damage_effect / max(pre_error, 1e-12)
    removed = max(0, pre_active - post_active) / max(pre_active, 1)
    raw = recovery_fraction(pre_error=pre_error, post_damage_error=post, recovered_error=final_error)
    rec = normalized_recovery_fraction(pre_error=pre_error, post_damage_error=post, recovered_error=final_error)
    auc = normalized_recovery_auc(errors, pre_error=pre_error, post_damage_error=post)
    return {'growth_steps': growth_steps, 'recovery_steps': recovery_steps, 'pre_error': pre_error, 'post_damage_error': post, 'final_recovery_error': final_error, 'damage_effect': damage_effect, 'relative_damage_effect': relative, 'pre_damage_active_cells': pre_active, 'post_damage_active_cells': post_active, 'active_cell_removal_fraction': removed, 'recovery_fraction': _finite_or_none(rec), 'recovery_fraction_raw': _finite_or_none(raw), 't50_first_crossing_steps': t50, 't90_first_crossing_steps': t90, 't50_stable_steps': st50, 't90_stable_steps': st90, 'normalized_recovery_auc': _finite_or_none(auc), 'recovery_error_curve': errors, 'recovery_active_cell_curve': active_cells, 'active_cells_final': active, 'elapsed_seconds': elapsed, 'resources': resources.to_dict()}

def evaluate_persistence(*, model: NeuralCellularAutomaton, seed_state: Tensor, target: Tensor, growth_steps: int, persistence_steps: int, seed: int, visible_channels: int=4) -> dict[str, object]:
    _validate_seed_target(seed_state, target, model)
    if not 0 <= growth_steps <= model.config.max_steps:
        raise ValueError('growth_steps exceeds model development limit')
    if not 0 <= persistence_steps <= model.config.max_steps:
        raise ValueError('persistence_steps exceeds model development limit')
    rng = torch.Generator(device=seed_state.device.type).manual_seed(seed)
    started = time.perf_counter()
    with torch.no_grad():
        grown = model.run(seed_state, steps=growth_steps, generator=rng)
        ensure_finite(grown)
        initial_error = float(morphology_mse(grown, target, visible_channels=visible_channels).item())
        initial_active = active_cell_count(grown, alive_channel=model.config.alive_channel, alive_threshold=model.config.alive_threshold)
        errors = [initial_error]
        active_cells = [initial_active]
        mags = []
        current = grown
        for _ in range(persistence_steps):
            nxt = model.step(current, generator=rng)
            ensure_finite(nxt)
            mags.append(mean_update_magnitude(current, nxt))
            current = nxt
            errors.append(float(morphology_mse(current, target, visible_channels=visible_channels).item()))
            active_cells.append(active_cell_count(current, alive_channel=model.config.alive_channel, alive_threshold=model.config.alive_threshold))
    elapsed = time.perf_counter() - started
    final_error = errors[-1]
    final_active = active_cells[-1]
    drift = float(torch.mean((current[:, :visible_channels] - grown[:, :visible_channels]) ** 2).item())
    resources = snapshot_resources(model=model, state=current, active_cells=final_active)
    return {'growth_steps': growth_steps, 'persistence_steps': persistence_steps, 'initial_error': initial_error, 'final_error': final_error, 'error_degradation': final_error - initial_error, 'max_error_degradation': max(errors) - initial_error, 'initial_active_cells': initial_active, 'final_active_cells': final_active, 'active_cell_drift': final_active - initial_active, 'visible_state_drift_mse': drift, 'mean_step_update_magnitude': sum(mags) / len(mags) if mags else 0.0, 'error_curve': errors, 'active_cell_curve': active_cells, 'elapsed_seconds': elapsed, 'resources': resources.to_dict()}

def _validate_seed_target(seed_state: Tensor, target: Tensor, model: NeuralCellularAutomaton) -> None:
    if seed_state.ndim != 4 or seed_state.shape[0] != 1:
        raise ValueError('seed_state must have batch size 1')
    if target.shape != seed_state.shape:
        raise ValueError('target must have the same shape as seed_state')
    if seed_state.shape[1] != model.config.state_channels:
        raise ValueError('seed_state channels do not match model')
    if seed_state.dtype != target.dtype:
        raise TypeError('seed_state and target must have identical dtype')

def _finite_or_none(value: float) -> float | None:
    return value if math.isfinite(value) else None
