from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib
import math, time
from typing import Literal
import torch
from torch import Tensor
from .damage import center_lesion
from .metrics import active_cell_count, background_alive_margin_loss, background_alpha_mse, balanced_morphology_mse, ensure_finite, foreground_morphology_mse, far_field_background_alpha_mse, graded_background_alpha_mse, homeostasis_background_velocity_loss, homeostasis_mature_sample_mask, homeostasis_trajectory_velocity_loss, morphology_mse, mean_update_magnitude, normalized_recovery_auc, normalized_recovery_fraction, recovery_fraction, recovery_threshold_step, stable_recovery_threshold_step
from .nca import NeuralCellularAutomaton
from .pool import StatePool
from .resources import snapshot_resources
TrainingVariant = Literal['growth_only', 'persistence', 'regeneration']
TrainingLossMode = Literal['global_mse', 'balanced_fg_bg', 'global_plus_foreground', 'global_plus_foreground_bg_alpha', 'global_plus_foreground_bg_alive_margin', 'global_plus_foreground_farfield_bg_alpha', 'global_plus_foreground_graded_bg_alpha', 'global_plus_foreground_bg_alpha_homeostasis', 'global_plus_foreground_bg_alpha_homeostasis_t16', 'global_plus_foreground_bg_alpha_attractor_t16', 'global_plus_foreground_bg_alpha_attractor_t16_ceil800', 'global_plus_foreground_bg_alpha_attractor_t16_ceil800_traceceil800', 'global_plus_foreground_bg_alpha_attractor_t16_ceil800_alloc_balanced_hard', 'global_plus_foreground_bg_alpha_attractor_t16_life4_ceil800', 'global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800', 'global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800_visanchor_r1', 'global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800_causal_latent_dropout25_prune_t16', 'global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800_causal_latent_dropout25_prune_t16_domainsep']
HOME_T16_PROBE_STEPS = 16
FORMATION_OCCUPANCY_CEILING = 800
LIFE_VIABILITY_FLOOR = 113
CAUSAL_LATENT_DROPOUT_FRACTION = 0.25
CAUSAL_PROBE_RNG_DOMAIN = b'DG1A_P0_STAB18_R1_CAUSAL_PROBE_V1'

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
        if self.loss_mode not in {'global_mse', 'balanced_fg_bg', 'global_plus_foreground', 'global_plus_foreground_bg_alpha', 'global_plus_foreground_bg_alive_margin', 'global_plus_foreground_farfield_bg_alpha', 'global_plus_foreground_graded_bg_alpha', 'global_plus_foreground_bg_alpha_homeostasis', 'global_plus_foreground_bg_alpha_homeostasis_t16', 'global_plus_foreground_bg_alpha_attractor_t16', 'global_plus_foreground_bg_alpha_attractor_t16_ceil800', 'global_plus_foreground_bg_alpha_attractor_t16_ceil800_traceceil800', 'global_plus_foreground_bg_alpha_attractor_t16_ceil800_alloc_balanced_hard', 'global_plus_foreground_bg_alpha_attractor_t16_life4_ceil800', 'global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800', 'global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800_visanchor_r1', 'global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800_causal_latent_dropout25_prune_t16', 'global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800_causal_latent_dropout25_prune_t16_domainsep'}:
            raise ValueError(f'unsupported training loss mode: {self.loss_mode}')
        if not 0 < self.visible_channels <= model.config.state_channels:
            raise ValueError('visible_channels is outside model state')
        if self.record_every <= 0:
            raise ValueError('record_every must be positive')
        if self.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_life4_ceil800':
            if model.config.alive_channel != 4:
                raise ValueError('STAB-15 requires model alive_channel 4')
            if self.visible_channels != 4:
                raise ValueError('STAB-15 requires exactly four visible morphology channels')
        if self.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800':
            if model.config.alive_channel != 4:
                raise ValueError('STAB-16 requires model alive_channel 4')
            if self.visible_channels != 4:
                raise ValueError('STAB-16 requires exactly four visible morphology channels')
        if self.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800_visanchor_r1':
            if model.config.alive_channel != 4:
                raise ValueError('STAB-17 requires model alive_channel 4')
            if self.visible_channels != 4:
                raise ValueError('STAB-17 requires exactly four visible morphology channels')
        if self.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800_causal_latent_dropout25_prune_t16':
            if model.config.alive_channel != 4:
                raise ValueError('STAB-18 requires model alive_channel 4')
            if self.visible_channels != 4:
                raise ValueError('STAB-18 requires exactly four visible morphology channels')
        if self.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800_causal_latent_dropout25_prune_t16_domainsep':
            if model.config.alive_channel != 4:
                raise ValueError('STAB-18-R1 requires model alive_channel 4')
            if self.visible_channels != 4:
                raise ValueError('STAB-18-R1 requires exactly four visible morphology channels')

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

def training_morphology_loss(*, result: Tensor, target: Tensor, config: TrainingConfig, homeostasis_loss: Tensor | None = None, attractor_loss: Tensor | None = None, occupancy_loss: Tensor | None = None, trace_occupancy_loss: Tensor | None = None, allocation_loss: Tensor | None = None, frontier_floor_loss: Tensor | None = None, visible_anchor_loss: Tensor | None = None, causal_prune_loss: Tensor | None = None) -> Tensor:
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
    if config.loss_mode == 'global_plus_foreground_bg_alpha_homeostasis':
        if homeostasis_loss is None:
            raise ValueError('HOME-1 requires homeostasis_loss')
        return morphology_mse(result, target, visible_channels=config.visible_channels) + foreground_morphology_mse(result, target, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1) + background_alpha_mse(result, target, alpha_channel=3, foreground_threshold=0.1) + homeostasis_loss
    if config.loss_mode == 'global_plus_foreground_bg_alpha_homeostasis_t16':
        if homeostasis_loss is None:
            raise ValueError('HOME-T16 requires homeostasis_loss')
        return morphology_mse(result, target, visible_channels=config.visible_channels) + foreground_morphology_mse(result, target, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1) + background_alpha_mse(result, target, alpha_channel=3, foreground_threshold=0.1) + homeostasis_loss
    if config.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16':
        if attractor_loss is None:
            raise ValueError('ATTRACT-16 requires attractor_loss')
        return morphology_mse(result, target, visible_channels=config.visible_channels) + foreground_morphology_mse(result, target, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1) + background_alpha_mse(result, target, alpha_channel=3, foreground_threshold=0.1) + attractor_loss
    if config.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_ceil800':
        if attractor_loss is None:
            raise ValueError('STAB-12 requires attractor_loss')
        if occupancy_loss is None:
            raise ValueError('STAB-12 requires occupancy_loss')
        return morphology_mse(result, target, visible_channels=config.visible_channels) + foreground_morphology_mse(result, target, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1) + background_alpha_mse(result, target, alpha_channel=3, foreground_threshold=0.1) + attractor_loss + occupancy_loss
    if config.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_ceil800_alloc_balanced_hard':
        if attractor_loss is None:
            raise ValueError('STAB-14 requires attractor_loss')
        if occupancy_loss is None:
            raise ValueError('STAB-14 requires occupancy_loss')
        if allocation_loss is None:
            raise ValueError('STAB-14 requires allocation_loss')
        return morphology_mse(result, target, visible_channels=config.visible_channels) + foreground_morphology_mse(result, target, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1) + background_alpha_mse(result, target, alpha_channel=3, foreground_threshold=0.1) + attractor_loss + occupancy_loss + allocation_loss
    if config.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_ceil800_traceceil800':
        if attractor_loss is None:
            raise ValueError('STAB-13 requires attractor_loss')
        if occupancy_loss is None:
            raise ValueError('STAB-13 requires occupancy_loss')
        if trace_occupancy_loss is None:
            raise ValueError('STAB-13 requires trace_occupancy_loss')
        return morphology_mse(result, target, visible_channels=config.visible_channels) + foreground_morphology_mse(result, target, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1) + background_alpha_mse(result, target, alpha_channel=3, foreground_threshold=0.1) + attractor_loss + occupancy_loss + trace_occupancy_loss
    if config.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_life4_ceil800':
        if attractor_loss is None:
            raise ValueError('STAB-15 requires attractor_loss')
        if occupancy_loss is None:
            raise ValueError('STAB-15 requires occupancy_loss')
        return morphology_mse(result, target, visible_channels=config.visible_channels) + foreground_morphology_mse(result, target, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1) + background_alpha_mse(result, target, alpha_channel=3, foreground_threshold=0.1) + attractor_loss + occupancy_loss
    if config.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800':
        if attractor_loss is None:
            raise ValueError('STAB-16 requires attractor_loss')
        if occupancy_loss is None:
            raise ValueError('STAB-16 requires occupancy_loss')
        if frontier_floor_loss is None:
            raise ValueError('STAB-16 requires frontier_floor_loss')
        return morphology_mse(result, target, visible_channels=config.visible_channels) + foreground_morphology_mse(result, target, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1) + background_alpha_mse(result, target, alpha_channel=3, foreground_threshold=0.1) + attractor_loss + occupancy_loss + frontier_floor_loss
    if config.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800_visanchor_r1':
        if attractor_loss is None:
            raise ValueError('STAB-17 requires attractor_loss')
        if occupancy_loss is None:
            raise ValueError('STAB-17 requires occupancy_loss')
        if frontier_floor_loss is None:
            raise ValueError('STAB-17 requires frontier_floor_loss')
        if visible_anchor_loss is None:
            raise ValueError('STAB-17 requires visible_anchor_loss')
        return morphology_mse(result, target, visible_channels=config.visible_channels) + foreground_morphology_mse(result, target, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1) + background_alpha_mse(result, target, alpha_channel=3, foreground_threshold=0.1) + attractor_loss + occupancy_loss + frontier_floor_loss + visible_anchor_loss
    if config.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800_causal_latent_dropout25_prune_t16':
        if attractor_loss is None:
            raise ValueError('STAB-18 requires attractor_loss')
        if occupancy_loss is None:
            raise ValueError('STAB-18 requires occupancy_loss')
        if frontier_floor_loss is None:
            raise ValueError('STAB-18 requires frontier_floor_loss')
        if causal_prune_loss is None:
            raise ValueError('STAB-18 requires causal_prune_loss')
        return morphology_mse(result, target, visible_channels=config.visible_channels) + foreground_morphology_mse(result, target, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1) + background_alpha_mse(result, target, alpha_channel=3, foreground_threshold=0.1) + attractor_loss + occupancy_loss + frontier_floor_loss + causal_prune_loss
    if config.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800_causal_latent_dropout25_prune_t16_domainsep':
        if attractor_loss is None:
            raise ValueError('STAB-18-R1 requires attractor_loss')
        if occupancy_loss is None:
            raise ValueError('STAB-18-R1 requires occupancy_loss')
        if frontier_floor_loss is None:
            raise ValueError('STAB-18-R1 requires frontier_floor_loss')
        if causal_prune_loss is None:
            raise ValueError('STAB-18-R1 requires causal_prune_loss')
        return morphology_mse(result, target, visible_channels=config.visible_channels) + foreground_morphology_mse(result, target, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1) + background_alpha_mse(result, target, alpha_channel=3, foreground_threshold=0.1) + attractor_loss + occupancy_loss + frontier_floor_loss + causal_prune_loss
    raise ValueError(f'unsupported training loss mode: {config.loss_mode}')

def _rng_neutral_homeostasis_probe(*, model: NeuralCellularAutomaton, result: Tensor, generator: torch.Generator) -> Tensor:
    rng_state = generator.get_state().clone()
    try:
        probe = model.step(result, generator=generator)
    finally:
        generator.set_state(rng_state)
    return probe

def _rng_neutral_homeostasis_trajectory(*, model: NeuralCellularAutomaton, result: Tensor, generator: torch.Generator) -> tuple[Tensor, ...]:
    rng_state = generator.get_state().clone()
    states = [result]
    current = result
    try:
        for _ in range(HOME_T16_PROBE_STEPS):
            current = model.step(current, generator=generator)
            ensure_finite(current)
            states.append(current)
    finally:
        generator.set_state(rng_state)
    return tuple(states)

def attractor_trajectory_loss(states: tuple[Tensor, ...], target: Tensor, *, visible_channels: int=4) -> Tensor:
    if len(states) != HOME_T16_PROBE_STEPS:
        raise ValueError(f'ATTRACT-16 requires exactly {HOME_T16_PROBE_STEPS} future states')
    losses = []
    for state in states:
        ensure_finite(state)
        losses.append(
            morphology_mse(state, target, visible_channels=visible_channels)
            + foreground_morphology_mse(state, target, visible_channels=visible_channels, alpha_channel=3, foreground_threshold=0.1)
            + background_alpha_mse(state, target, alpha_channel=3, foreground_threshold=0.1)
        )
    return torch.stack(losses).mean()

def attractor_trajectory_loss_per_sample(states: tuple[Tensor, ...], target: Tensor, *, visible_channels: int=4) -> Tensor:
    if len(states) != HOME_T16_PROBE_STEPS:
        raise ValueError(f'ATTRACT-16 requires exactly {HOME_T16_PROBE_STEPS} future states')
    if target.ndim != 4:
        raise ValueError('target must have shape [batch, channels, height, width]')
    if visible_channels <= 0 or visible_channels > target.shape[1]:
        raise ValueError('visible_channels is outside the state vector')
    foreground = target[:, 3:4] > 0.1
    background = ~foreground
    foreground_counts = foreground.expand(-1, visible_channels, -1, -1).flatten(1).sum(dim=1)
    background_counts = background.flatten(1).sum(dim=1)
    if bool((foreground_counts == 0).any()):
        raise ValueError('target contains a sample with no foreground pixels')
    if bool((background_counts == 0).any()):
        raise ValueError('target contains a sample with no background pixels')
    per_step = []
    for state in states:
        ensure_finite(state)
        if state.shape != target.shape:
            raise ValueError('state and target must have identical shape')
        squared = (state[:, :visible_channels] - target[:, :visible_channels]) ** 2
        global_loss = squared.flatten(1).mean(dim=1)
        fg_loss = (squared * foreground.expand(-1, visible_channels, -1, -1).to(dtype=state.dtype)).flatten(1).sum(dim=1) / foreground_counts.to(dtype=state.dtype)
        alpha_squared = state[:, 3:4] ** 2
        bg_loss = (alpha_squared * background.to(dtype=state.dtype)).flatten(1).sum(dim=1) / background_counts.to(dtype=state.dtype)
        per_step.append(global_loss + fg_loss + bg_loss)
    return torch.stack(per_step, dim=0).mean(dim=0)

def causal_latent_probe_mask(state: Tensor, *, generator: torch.Generator, life_channel: int=4, alive_threshold: float=0.1, fraction: float=CAUSAL_LATENT_DROPOUT_FRACTION) -> Tensor:
    if state.ndim != 4:
        raise ValueError('state must have shape [batch, channels, height, width]')
    if not state.is_floating_point():
        raise TypeError('state must use a floating-point dtype')
    if not 0 <= life_channel < state.shape[1]:
        raise ValueError('life_channel is outside the state vector')
    if not 0.0 <= fraction <= 1.0:
        raise ValueError('fraction must be in [0, 1]')
    hard_alive = state[:, life_channel:life_channel + 1] > alive_threshold
    rng_state = generator.get_state().clone()
    try:
        random_values = torch.rand(hard_alive.shape, device=state.device, dtype=state.dtype, generator=generator)
    finally:
        generator.set_state(rng_state)
    return hard_alive & (random_values < fraction)

def causal_probe_domain_seed(generator: torch.Generator) -> int:
    state_bytes = bytes(generator.get_state().cpu().tolist())
    digest = hashlib.sha256(state_bytes + CAUSAL_PROBE_RNG_DOMAIN).digest()
    return int.from_bytes(digest[:8], byteorder='big', signed=False) & 0x7FFFFFFFFFFFFFFF

def causal_latent_probe_mask_domain_separated(state: Tensor, *, generator: torch.Generator, life_channel: int=4, alive_threshold: float=0.1, fraction: float=CAUSAL_LATENT_DROPOUT_FRACTION) -> Tensor:
    if state.ndim != 4:
        raise ValueError('state must have shape [batch, channels, height, width]')
    if not state.is_floating_point():
        raise TypeError('state must use a floating-point dtype')
    if not 0 <= life_channel < state.shape[1]:
        raise ValueError('life_channel is outside the state vector')
    if not 0.0 <= fraction <= 1.0:
        raise ValueError('fraction must be in [0, 1]')
    hard_alive = state[:, life_channel:life_channel + 1] > alive_threshold
    probe_generator = torch.Generator(device=state.device)
    probe_generator.manual_seed(causal_probe_domain_seed(generator))
    random_values = torch.rand(hard_alive.shape, device=state.device, dtype=state.dtype, generator=probe_generator)
    return hard_alive & (random_values < fraction)

def apply_latent_probe_intervention(state: Tensor, probe_mask: Tensor, *, visible_channels: int=4) -> Tensor:
    if state.ndim != 4:
        raise ValueError('state must have shape [batch, channels, height, width]')
    if probe_mask.shape != (state.shape[0], 1, state.shape[2], state.shape[3]):
        raise ValueError('probe_mask must have shape [batch, 1, height, width]')
    if probe_mask.dtype != torch.bool:
        raise TypeError('probe_mask must use bool dtype')
    if not 0 < visible_channels < state.shape[1]:
        raise ValueError('visible_channels must leave at least one latent channel')
    result = state.clone()
    latent = result[:, visible_channels:]
    result[:, visible_channels:] = latent.masked_fill(probe_mask.expand(-1, latent.shape[1], -1, -1), 0)
    return result

def causal_latent_prune_terms(state: Tensor, probe_mask: Tensor, causal_delta: Tensor, *, life_channel: int=4, alive_threshold: float=0.1, maturity_floor: int=LIFE_VIABILITY_FLOOR) -> tuple[Tensor, Tensor, Tensor, Tensor, Tensor, Tensor]:
    if state.ndim != 4:
        raise ValueError('state must have shape [batch, channels, height, width]')
    if not state.is_floating_point():
        raise TypeError('state must use a floating-point dtype')
    if probe_mask.shape != (state.shape[0], 1, state.shape[2], state.shape[3]):
        raise ValueError('probe_mask must have shape [batch, 1, height, width]')
    if probe_mask.dtype != torch.bool:
        raise TypeError('probe_mask must use bool dtype')
    if causal_delta.shape != (state.shape[0],):
        raise ValueError('causal_delta must have shape [batch]')
    if maturity_floor <= 0:
        raise ValueError('maturity_floor must be positive')
    if not 0 <= life_channel < state.shape[1]:
        raise ValueError('life_channel is outside the state vector')
    life = state[:, life_channel:life_channel + 1]
    hard_alive = life > alive_threshold
    hard_counts = hard_alive.flatten(1).sum(dim=1)
    mature = hard_counts >= maturity_floor
    dropped = probe_mask & hard_alive
    dropped_counts = dropped.flatten(1).sum(dim=1)
    classified = mature & (dropped_counts > 0)
    detached_delta = causal_delta.detach()
    nonbeneficial = classified & (detached_delta <= 0)
    denom = hard_counts.to(dtype=state.dtype).clamp_min(1.0)
    hard_fraction = nonbeneficial.to(dtype=state.dtype) * dropped_counts.to(dtype=state.dtype) / denom
    correction = ((life - life.detach()) * dropped.to(dtype=state.dtype).detach() * nonbeneficial[:, None, None, None].to(dtype=state.dtype).detach()).flatten(1).sum(dim=1) / denom.detach()
    per_sample = hard_fraction.detach() + correction
    if bool(mature.any()):
        loss = per_sample[mature].mean()
    else:
        loss = state.sum() * 0.0
    actual_drop_fraction = dropped_counts.to(dtype=state.dtype) / denom
    return loss, mature, classified, nonbeneficial, dropped_counts.detach(), actual_drop_fraction.detach()

def formation_hard_active_counts(state: Tensor, *, alpha_channel: int=3, alive_threshold: float=0.1) -> Tensor:
    if state.ndim != 4:
        raise ValueError('state must have shape [batch, channels, height, width]')
    if not state.is_floating_point():
        raise TypeError('state must use a floating-point dtype')
    if not 0 <= alpha_channel < state.shape[1]:
        raise ValueError('alpha_channel is outside the state vector')
    return (state[:, alpha_channel:alpha_channel + 1] > alive_threshold).flatten(1).sum(dim=1)

def formation_occupancy_ceiling_loss(result: Tensor, target: Tensor, *, alpha_channel: int=3, foreground_threshold: float=0.1, alive_threshold: float=0.1, occupancy_ceiling: int=FORMATION_OCCUPANCY_CEILING) -> Tensor:
    if result.shape != target.shape:
        raise ValueError('result and target must have identical shape')
    if result.dtype != target.dtype:
        raise TypeError('result and target must have identical dtype')
    if result.device != target.device:
        raise ValueError('result and target must be on the same device')
    if occupancy_ceiling <= 0:
        raise ValueError('occupancy_ceiling must be positive')
    if not 0 <= alpha_channel < result.shape[1]:
        raise ValueError('alpha_channel is outside the state vector')
    alpha = result[:, alpha_channel:alpha_channel + 1]
    hard_alive = (alpha > alive_threshold).to(dtype=result.dtype)
    hard_counts = hard_alive.flatten(1).sum(dim=1)
    background = target[:, alpha_channel:alpha_channel + 1] <= foreground_threshold
    active_background = hard_alive * background.to(dtype=result.dtype)
    surrogate_correction = ((alpha - alpha.detach()) * active_background.detach()).flatten(1).sum(dim=1)
    ste_counts = hard_counts + surrogate_correction
    normalized_excess = torch.relu(ste_counts - float(occupancy_ceiling)) / float(occupancy_ceiling)
    return torch.mean(normalized_excess ** 2)

def decoupled_mature_sample_mask(state: Tensor, target: Tensor, *, state_alive_channel: int, target_alpha_channel: int=3, foreground_threshold: float=0.1, alive_threshold: float=0.1) -> Tensor:
    if state.shape != target.shape:
        raise ValueError('state and target must have identical shape')
    if not 0 <= state_alive_channel < state.shape[1]:
        raise ValueError('state_alive_channel is outside the state vector')
    if not 0 <= target_alpha_channel < target.shape[1]:
        raise ValueError('target_alpha_channel is outside the target vector')
    hard_alive = state[:, state_alive_channel:state_alive_channel + 1] > alive_threshold
    foreground = target[:, target_alpha_channel:target_alpha_channel + 1] > foreground_threshold
    active_counts = hard_alive.flatten(1).sum(dim=1)
    target_counts = foreground.flatten(1).sum(dim=1)
    return active_counts >= target_counts

def decoupled_life_occupancy_ceiling_loss(result: Tensor, target: Tensor, *, state_alive_channel: int, target_alpha_channel: int=3, foreground_threshold: float=0.1, alive_threshold: float=0.1, occupancy_ceiling: int=FORMATION_OCCUPANCY_CEILING) -> Tensor:
    if result.shape != target.shape:
        raise ValueError('result and target must have identical shape')
    if result.dtype != target.dtype:
        raise TypeError('result and target must have identical dtype')
    if result.device != target.device:
        raise ValueError('result and target must be on the same device')
    if occupancy_ceiling <= 0:
        raise ValueError('occupancy_ceiling must be positive')
    if not 0 <= state_alive_channel < result.shape[1]:
        raise ValueError('state_alive_channel is outside the state vector')
    if not 0 <= target_alpha_channel < target.shape[1]:
        raise ValueError('target_alpha_channel is outside the target vector')
    life = result[:, state_alive_channel:state_alive_channel + 1]
    hard_alive = (life > alive_threshold).to(dtype=result.dtype)
    hard_counts = hard_alive.flatten(1).sum(dim=1)
    background = target[:, target_alpha_channel:target_alpha_channel + 1] <= foreground_threshold
    active_background = hard_alive * background.to(dtype=result.dtype)
    surrogate_correction = ((life - life.detach()) * active_background.detach()).flatten(1).sum(dim=1)
    ste_counts = hard_counts + surrogate_correction
    normalized_excess = torch.relu(ste_counts - float(occupancy_ceiling)) / float(occupancy_ceiling)
    return torch.mean(normalized_excess ** 2)

def hidden_life_growth_frontier(state: Tensor, *, life_channel: int=4, alive_threshold: float=0.1) -> Tensor:
    if state.ndim != 4:
        raise ValueError('state must have shape [batch, channels, height, width]')
    if not state.is_floating_point():
        raise TypeError('state must use a floating-point dtype')
    if not 0 <= life_channel < state.shape[1]:
        raise ValueError('life_channel is outside the state vector')
    life = state[:, life_channel:life_channel + 1]
    hard_alive = life > alive_threshold
    live_neighborhood = torch.nn.functional.max_pool2d(
        hard_alive.to(dtype=state.dtype), kernel_size=3, stride=1, padding=1
    ) > 0
    return live_neighborhood & (~hard_alive)

def frontier_life_floor_loss(state: Tensor, *, life_channel: int=4, alive_threshold: float=0.1, viability_floor: int=LIFE_VIABILITY_FLOOR) -> tuple[Tensor, Tensor]:
    if viability_floor <= 0:
        raise ValueError('viability_floor must be positive')
    frontier = hidden_life_growth_frontier(state, life_channel=life_channel, alive_threshold=alive_threshold)
    life = state[:, life_channel:life_channel + 1]
    hard_alive = (life > alive_threshold).to(dtype=state.dtype)
    hard_counts = hard_alive.flatten(1).sum(dim=1)
    frontier_correction = ((life - life.detach()) * frontier.to(dtype=state.dtype).detach()).flatten(1).sum(dim=1)
    ste_counts = hard_counts + frontier_correction
    normalized_deficit = torch.relu(float(viability_floor) - ste_counts) / float(viability_floor)
    loss = torch.mean(normalized_deficit ** 2)
    frontier_counts = frontier.flatten(1).sum(dim=1)
    return loss, frontier_counts


def current_visible_r1_neighborhood(state: Tensor, *, visible_alpha_channel: int=3, visible_threshold: float=0.1) -> Tensor:
    if state.ndim != 4:
        raise ValueError('state must have shape [batch, channels, height, width]')
    if not state.is_floating_point():
        raise TypeError('state must use a floating-point dtype')
    if not 0 <= visible_alpha_channel < state.shape[1]:
        raise ValueError('visible_alpha_channel is outside the state vector')
    visible = state[:, visible_alpha_channel:visible_alpha_channel + 1]
    hard_visible = visible > visible_threshold
    return torch.nn.functional.max_pool2d(hard_visible.to(dtype=state.dtype), kernel_size=3, stride=1, padding=1) > 0


def mature_visible_anchor_terms(state: Tensor, *, life_channel: int=4, visible_alpha_channel: int=3, alive_threshold: float=0.1, visible_threshold: float=0.1, maturity_floor: int=LIFE_VIABILITY_FLOOR) -> tuple[Tensor, Tensor, Tensor, Tensor]:
    if state.ndim != 4:
        raise ValueError('state must have shape [batch, channels, height, width]')
    if not state.is_floating_point():
        raise TypeError('state must use a floating-point dtype')
    if maturity_floor <= 0:
        raise ValueError('maturity_floor must be positive')
    if not 0 <= life_channel < state.shape[1]:
        raise ValueError('life_channel is outside the state vector')
    if not 0 <= visible_alpha_channel < state.shape[1]:
        raise ValueError('visible_alpha_channel is outside the state vector')
    life = state[:, life_channel:life_channel + 1]
    hard_alive = life > alive_threshold
    visible_neighborhood = current_visible_r1_neighborhood(state, visible_alpha_channel=visible_alpha_channel, visible_threshold=visible_threshold)
    hard_counts = hard_alive.flatten(1).sum(dim=1)
    mature = hard_counts >= maturity_floor
    unanchored = hard_alive & (~visible_neighborhood)
    unanchored_counts = unanchored.flatten(1).sum(dim=1).to(dtype=state.dtype)
    denominators = hard_counts.to(dtype=state.dtype).clamp_min(1.0)
    hard_fractions = unanchored_counts / denominators
    correction = ((life - life.detach()) * unanchored.to(dtype=state.dtype).detach()).flatten(1).sum(dim=1) / denominators.detach()
    per_sample = hard_fractions.detach() + correction
    if bool(mature.any()):
        loss = per_sample[mature].mean()
    else:
        loss = state.sum() * 0.0
    return loss, mature, hard_fractions.detach(), unanchored_counts.detach()

def trace_occupancy_ceiling_loss(states: tuple[Tensor, ...], target: Tensor, *, alpha_channel: int=3, foreground_threshold: float=0.1, alive_threshold: float=0.1, occupancy_ceiling: int=FORMATION_OCCUPANCY_CEILING) -> Tensor:
    if len(states) != HOME_T16_PROBE_STEPS:
        raise ValueError(f'TRACE-CEIL-800 requires exactly {HOME_T16_PROBE_STEPS} future states')
    losses = [
        formation_occupancy_ceiling_loss(
            state,
            target,
            alpha_channel=alpha_channel,
            foreground_threshold=foreground_threshold,
            alive_threshold=alive_threshold,
            occupancy_ceiling=occupancy_ceiling,
        )
        for state in states
    ]
    return torch.stack(losses).mean()

def balanced_hard_support_allocation_terms(result: Tensor, target: Tensor, *, alpha_channel: int=3, foreground_threshold: float=0.1, alive_threshold: float=0.1) -> tuple[Tensor, Tensor, Tensor, Tensor]:
    if result.shape != target.shape:
        raise ValueError('result and target must have identical shape')
    if result.dtype != target.dtype:
        raise TypeError('result and target must have identical dtype')
    if result.device != target.device:
        raise ValueError('result and target must be on the same device')
    if not 0 <= alpha_channel < result.shape[1]:
        raise ValueError('alpha_channel is outside the state vector')
    alpha = result[:, alpha_channel:alpha_channel + 1]
    hard_alive = alpha > alive_threshold
    foreground = target[:, alpha_channel:alpha_channel + 1] > foreground_threshold
    background = ~foreground
    if not bool(foreground.any()) or not bool(background.any()):
        raise ValueError('target requires both foreground and background')
    fp = hard_alive & background
    fn = (~hard_alive) & foreground
    tp = hard_alive & foreground
    fg_count = foreground.flatten(1).sum(dim=1).to(dtype=result.dtype)
    bg_count = background.flatten(1).sum(dim=1).to(dtype=result.dtype)
    fp_rate = fp.flatten(1).sum(dim=1).to(dtype=result.dtype) / bg_count
    fn_rate = fn.flatten(1).sum(dim=1).to(dtype=result.dtype) / fg_count
    hard_error = 0.5 * fp_rate + 0.5 * fn_rate
    zero_forward = alpha - alpha.detach()
    fp_correction = (zero_forward * fp.to(dtype=result.dtype).detach()).flatten(1).sum(dim=1) / bg_count
    fn_correction = -(zero_forward * fn.to(dtype=result.dtype).detach()).flatten(1).sum(dim=1) / fg_count
    loss = torch.mean(hard_error.detach() + 0.5 * fp_correction + 0.5 * fn_correction)
    tp_mean = tp.flatten(1).sum(dim=1).to(dtype=result.dtype).mean().detach()
    return loss, fp_rate.mean().detach(), fn_rate.mean().detach(), tp_mean

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
        homeostasis_loss = None
        homeostasis_mature_samples = 0
        attractor_loss = None
        attractor_mature_samples = 0
        occupancy_loss = None
        formation_active_cells_mean = 0.0
        formation_active_cells_max = 0
        trace_occupancy_loss = None
        trace_active_cells_mean = 0.0
        trace_active_cells_max = 0
        allocation_loss = None
        support_false_positive_rate = 0.0
        support_false_negative_rate = 0.0
        support_true_positive_cells_mean = 0.0
        frontier_floor_loss = None
        frontier_cells_mean = 0.0
        visible_anchor_loss = None
        anchor_mature_samples = 0
        unanchored_life_fraction_mean = 0.0
        unanchored_life_cells_mean = 0.0
        causal_prune_loss = None
        causal_probe_mature_samples = 0
        causal_probe_classified_samples = 0
        causal_probe_nonbeneficial_samples = 0
        causal_probe_nonbeneficial_fraction = 0.0
        causal_probe_dropped_cells_mean = 0.0
        causal_probe_actual_drop_fraction_mean = 0.0
        causal_delta_mean = 0.0
        causal_delta_min = 0.0
        causal_delta_max = 0.0
        causal_intact_future_loss_mean = 0.0
        causal_counterfactual_future_loss_mean = 0.0
        if config.loss_mode == 'global_plus_foreground_bg_alpha_homeostasis':
            mature_mask = homeostasis_mature_sample_mask(result, target_batch, alpha_channel=3, foreground_threshold=0.1, alive_threshold=model.config.alive_threshold)
            homeostasis_mature_samples = int(mature_mask.sum().item())
            if homeostasis_mature_samples > 0:
                mature_result = result[mature_mask]
                mature_target = target_batch[mature_mask]
                probe = _rng_neutral_homeostasis_probe(model=model, result=mature_result, generator=device_rng)
                ensure_finite(probe)
                homeostasis_loss = homeostasis_background_velocity_loss(mature_result, probe, mature_target, alpha_channel=3, foreground_threshold=0.1, alive_threshold=model.config.alive_threshold)
            else:
                homeostasis_loss = result.sum() * 0.0
        elif config.loss_mode == 'global_plus_foreground_bg_alpha_homeostasis_t16':
            mature_mask = homeostasis_mature_sample_mask(result, target_batch, alpha_channel=3, foreground_threshold=0.1, alive_threshold=model.config.alive_threshold)
            homeostasis_mature_samples = int(mature_mask.sum().item())
            if homeostasis_mature_samples > 0:
                mature_result = result[mature_mask]
                mature_target = target_batch[mature_mask]
                trajectory = _rng_neutral_homeostasis_trajectory(model=model, result=mature_result, generator=device_rng)
                homeostasis_loss = homeostasis_trajectory_velocity_loss(trajectory, mature_target, alpha_channel=3, foreground_threshold=0.1, alive_threshold=model.config.alive_threshold)
            else:
                homeostasis_loss = result.sum() * 0.0
        elif config.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16':
            mature_mask = homeostasis_mature_sample_mask(result, target_batch, alpha_channel=3, foreground_threshold=0.1, alive_threshold=model.config.alive_threshold)
            attractor_mature_samples = int(mature_mask.sum().item())
            if attractor_mature_samples > 0:
                mature_result = result[mature_mask]
                mature_target = target_batch[mature_mask]
                trajectory = _rng_neutral_homeostasis_trajectory(model=model, result=mature_result, generator=device_rng)
                attractor_loss = attractor_trajectory_loss(trajectory[1:], mature_target, visible_channels=config.visible_channels)
            else:
                attractor_loss = result.sum() * 0.0
        elif config.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_ceil800':
            mature_mask = homeostasis_mature_sample_mask(result, target_batch, alpha_channel=3, foreground_threshold=0.1, alive_threshold=model.config.alive_threshold)
            attractor_mature_samples = int(mature_mask.sum().item())
            if attractor_mature_samples > 0:
                mature_result = result[mature_mask]
                mature_target = target_batch[mature_mask]
                trajectory = _rng_neutral_homeostasis_trajectory(model=model, result=mature_result, generator=device_rng)
                attractor_loss = attractor_trajectory_loss(trajectory[1:], mature_target, visible_channels=config.visible_channels)
            else:
                attractor_loss = result.sum() * 0.0
            occupancy_loss = formation_occupancy_ceiling_loss(result, target_batch, alpha_channel=3, foreground_threshold=0.1, alive_threshold=model.config.alive_threshold)
            formation_counts = formation_hard_active_counts(result, alpha_channel=3, alive_threshold=model.config.alive_threshold)
            formation_active_cells_mean = float(formation_counts.to(dtype=torch.float32).mean().detach().item())
            formation_active_cells_max = int(formation_counts.max().detach().item())
        elif config.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_ceil800_traceceil800':
            mature_mask = homeostasis_mature_sample_mask(result, target_batch, alpha_channel=3, foreground_threshold=0.1, alive_threshold=model.config.alive_threshold)
            attractor_mature_samples = int(mature_mask.sum().item())
            if attractor_mature_samples > 0:
                mature_result = result[mature_mask]
                mature_target = target_batch[mature_mask]
                trajectory = _rng_neutral_homeostasis_trajectory(model=model, result=mature_result, generator=device_rng)
                future_states = trajectory[1:]
                attractor_loss = attractor_trajectory_loss(future_states, mature_target, visible_channels=config.visible_channels)
                trace_occupancy_loss = trace_occupancy_ceiling_loss(future_states, mature_target, alpha_channel=3, foreground_threshold=0.1, alive_threshold=model.config.alive_threshold)
                trace_counts = torch.stack([formation_hard_active_counts(state, alpha_channel=3, alive_threshold=model.config.alive_threshold) for state in future_states], dim=0)
                trace_active_cells_mean = float(trace_counts.to(dtype=torch.float32).mean().detach().item())
                trace_active_cells_max = int(trace_counts.max().detach().item())
            else:
                attractor_loss = result.sum() * 0.0
                trace_occupancy_loss = result.sum() * 0.0
            occupancy_loss = formation_occupancy_ceiling_loss(result, target_batch, alpha_channel=3, foreground_threshold=0.1, alive_threshold=model.config.alive_threshold)
            formation_counts = formation_hard_active_counts(result, alpha_channel=3, alive_threshold=model.config.alive_threshold)
            formation_active_cells_mean = float(formation_counts.to(dtype=torch.float32).mean().detach().item())
            formation_active_cells_max = int(formation_counts.max().detach().item())
        elif config.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_ceil800_alloc_balanced_hard':
            mature_mask = homeostasis_mature_sample_mask(result, target_batch, alpha_channel=3, foreground_threshold=0.1, alive_threshold=model.config.alive_threshold)
            attractor_mature_samples = int(mature_mask.sum().item())
            if attractor_mature_samples > 0:
                mature_result = result[mature_mask]
                mature_target = target_batch[mature_mask]
                trajectory = _rng_neutral_homeostasis_trajectory(model=model, result=mature_result, generator=device_rng)
                attractor_loss = attractor_trajectory_loss(trajectory[1:], mature_target, visible_channels=config.visible_channels)
            else:
                attractor_loss = result.sum() * 0.0
            occupancy_loss = formation_occupancy_ceiling_loss(result, target_batch, alpha_channel=3, foreground_threshold=0.1, alive_threshold=model.config.alive_threshold)
            formation_counts = formation_hard_active_counts(result, alpha_channel=3, alive_threshold=model.config.alive_threshold)
            formation_active_cells_mean = float(formation_counts.to(dtype=torch.float32).mean().detach().item())
            formation_active_cells_max = int(formation_counts.max().detach().item())
            allocation_loss, fp_rate, fn_rate, tp_mean = balanced_hard_support_allocation_terms(result, target_batch, alpha_channel=3, foreground_threshold=0.1, alive_threshold=model.config.alive_threshold)
            support_false_positive_rate = float(fp_rate.item())
            support_false_negative_rate = float(fn_rate.item())
            support_true_positive_cells_mean = float(tp_mean.item())
        elif config.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_life4_ceil800':
            mature_mask = decoupled_mature_sample_mask(result, target_batch, state_alive_channel=model.config.alive_channel, target_alpha_channel=3, foreground_threshold=0.1, alive_threshold=model.config.alive_threshold)
            attractor_mature_samples = int(mature_mask.sum().item())
            if attractor_mature_samples > 0:
                mature_result = result[mature_mask]
                mature_target = target_batch[mature_mask]
                trajectory = _rng_neutral_homeostasis_trajectory(model=model, result=mature_result, generator=device_rng)
                attractor_loss = attractor_trajectory_loss(trajectory[1:], mature_target, visible_channels=config.visible_channels)
            else:
                attractor_loss = result.sum() * 0.0
            occupancy_loss = decoupled_life_occupancy_ceiling_loss(result, target_batch, state_alive_channel=model.config.alive_channel, target_alpha_channel=3, foreground_threshold=0.1, alive_threshold=model.config.alive_threshold)
            formation_counts = formation_hard_active_counts(result, alpha_channel=model.config.alive_channel, alive_threshold=model.config.alive_threshold)
            formation_active_cells_mean = float(formation_counts.to(dtype=torch.float32).mean().detach().item())
            formation_active_cells_max = int(formation_counts.max().detach().item())
        elif config.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800':
            mature_mask = decoupled_mature_sample_mask(result, target_batch, state_alive_channel=model.config.alive_channel, target_alpha_channel=3, foreground_threshold=0.1, alive_threshold=model.config.alive_threshold)
            attractor_mature_samples = int(mature_mask.sum().item())
            if attractor_mature_samples > 0:
                mature_result = result[mature_mask]
                mature_target = target_batch[mature_mask]
                trajectory = _rng_neutral_homeostasis_trajectory(model=model, result=mature_result, generator=device_rng)
                attractor_loss = attractor_trajectory_loss(trajectory[1:], mature_target, visible_channels=config.visible_channels)
            else:
                attractor_loss = result.sum() * 0.0
            occupancy_loss = decoupled_life_occupancy_ceiling_loss(result, target_batch, state_alive_channel=model.config.alive_channel, target_alpha_channel=3, foreground_threshold=0.1, alive_threshold=model.config.alive_threshold)
            formation_counts = formation_hard_active_counts(result, alpha_channel=model.config.alive_channel, alive_threshold=model.config.alive_threshold)
            formation_active_cells_mean = float(formation_counts.to(dtype=torch.float32).mean().detach().item())
            formation_active_cells_max = int(formation_counts.max().detach().item())
            frontier_floor_loss, frontier_counts = frontier_life_floor_loss(result, life_channel=model.config.alive_channel, alive_threshold=model.config.alive_threshold, viability_floor=LIFE_VIABILITY_FLOOR)
            frontier_cells_mean = float(frontier_counts.to(dtype=torch.float32).mean().detach().item())
        elif config.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800_visanchor_r1':
            mature_mask = decoupled_mature_sample_mask(result, target_batch, state_alive_channel=model.config.alive_channel, target_alpha_channel=3, foreground_threshold=0.1, alive_threshold=model.config.alive_threshold)
            attractor_mature_samples = int(mature_mask.sum().item())
            if attractor_mature_samples > 0:
                mature_result = result[mature_mask]
                mature_target = target_batch[mature_mask]
                trajectory = _rng_neutral_homeostasis_trajectory(model=model, result=mature_result, generator=device_rng)
                attractor_loss = attractor_trajectory_loss(trajectory[1:], mature_target, visible_channels=config.visible_channels)
            else:
                attractor_loss = result.sum() * 0.0
            occupancy_loss = decoupled_life_occupancy_ceiling_loss(result, target_batch, state_alive_channel=model.config.alive_channel, target_alpha_channel=3, foreground_threshold=0.1, alive_threshold=model.config.alive_threshold)
            formation_counts = formation_hard_active_counts(result, alpha_channel=model.config.alive_channel, alive_threshold=model.config.alive_threshold)
            formation_active_cells_mean = float(formation_counts.to(dtype=torch.float32).mean().detach().item())
            formation_active_cells_max = int(formation_counts.max().detach().item())
            frontier_floor_loss, frontier_counts = frontier_life_floor_loss(result, life_channel=model.config.alive_channel, alive_threshold=model.config.alive_threshold, viability_floor=LIFE_VIABILITY_FLOOR)
            frontier_cells_mean = float(frontier_counts.to(dtype=torch.float32).mean().detach().item())
            visible_anchor_loss, anchor_mature_mask, anchor_fractions, anchor_counts = mature_visible_anchor_terms(result, life_channel=model.config.alive_channel, visible_alpha_channel=3, alive_threshold=model.config.alive_threshold, visible_threshold=0.1, maturity_floor=LIFE_VIABILITY_FLOOR)
            anchor_mature_samples = int(anchor_mature_mask.sum().item())
            if anchor_mature_samples > 0:
                unanchored_life_fraction_mean = float(anchor_fractions[anchor_mature_mask].mean().item())
                unanchored_life_cells_mean = float(anchor_counts[anchor_mature_mask].mean().item())
        elif config.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800_causal_latent_dropout25_prune_t16':
            mature_mask = decoupled_mature_sample_mask(result, target_batch, state_alive_channel=model.config.alive_channel, target_alpha_channel=3, foreground_threshold=0.1, alive_threshold=model.config.alive_threshold)
            attractor_mature_samples = int(mature_mask.sum().item())
            causal_probe_mature_samples = attractor_mature_samples
            if attractor_mature_samples > 0:
                mature_result = result[mature_mask]
                mature_target = target_batch[mature_mask]
                intact_trajectory = _rng_neutral_homeostasis_trajectory(model=model, result=mature_result, generator=device_rng)
                intact_future = intact_trajectory[1:]
                attractor_loss = attractor_trajectory_loss(intact_future, mature_target, visible_channels=config.visible_channels)
                probe_mask = causal_latent_probe_mask(mature_result.detach(), generator=device_rng, life_channel=model.config.alive_channel, alive_threshold=model.config.alive_threshold, fraction=CAUSAL_LATENT_DROPOUT_FRACTION)
                counterfactual_start = apply_latent_probe_intervention(mature_result.detach(), probe_mask, visible_channels=config.visible_channels)
                with torch.no_grad():
                    counterfactual_trajectory = _rng_neutral_homeostasis_trajectory(model=model, result=counterfactual_start, generator=device_rng)
                    intact_per_sample = attractor_trajectory_loss_per_sample(tuple(x.detach() for x in intact_future), mature_target.detach(), visible_channels=config.visible_channels)
                    counterfactual_per_sample = attractor_trajectory_loss_per_sample(counterfactual_trajectory[1:], mature_target.detach(), visible_channels=config.visible_channels)
                    causal_delta = (counterfactual_per_sample - intact_per_sample).detach()
                causal_prune_loss, _, classified_mask, nonbeneficial_mask, dropped_counts, actual_drop_fractions = causal_latent_prune_terms(mature_result, probe_mask, causal_delta, life_channel=model.config.alive_channel, alive_threshold=model.config.alive_threshold, maturity_floor=LIFE_VIABILITY_FLOOR)
                causal_probe_classified_samples = int(classified_mask.sum().item())
                causal_probe_nonbeneficial_samples = int(nonbeneficial_mask.sum().item())
                causal_probe_nonbeneficial_fraction = causal_probe_nonbeneficial_samples / causal_probe_classified_samples if causal_probe_classified_samples > 0 else 0.0
                causal_probe_dropped_cells_mean = float(dropped_counts.to(dtype=torch.float32).mean().item())
                causal_probe_actual_drop_fraction_mean = float(actual_drop_fractions.to(dtype=torch.float32).mean().item())
                if causal_probe_classified_samples > 0:
                    classified_delta = causal_delta[classified_mask]
                    causal_delta_mean = float(classified_delta.mean().item())
                    causal_delta_min = float(classified_delta.min().item())
                    causal_delta_max = float(classified_delta.max().item())
                    causal_intact_future_loss_mean = float(intact_per_sample[classified_mask].mean().item())
                    causal_counterfactual_future_loss_mean = float(counterfactual_per_sample[classified_mask].mean().item())
            else:
                attractor_loss = result.sum() * 0.0
                causal_prune_loss = result.sum() * 0.0
            occupancy_loss = decoupled_life_occupancy_ceiling_loss(result, target_batch, state_alive_channel=model.config.alive_channel, target_alpha_channel=3, foreground_threshold=0.1, alive_threshold=model.config.alive_threshold)
            formation_counts = formation_hard_active_counts(result, alpha_channel=model.config.alive_channel, alive_threshold=model.config.alive_threshold)
            formation_active_cells_mean = float(formation_counts.to(dtype=torch.float32).mean().detach().item())
            formation_active_cells_max = int(formation_counts.max().detach().item())
            frontier_floor_loss, frontier_counts = frontier_life_floor_loss(result, life_channel=model.config.alive_channel, alive_threshold=model.config.alive_threshold, viability_floor=LIFE_VIABILITY_FLOOR)
            frontier_cells_mean = float(frontier_counts.to(dtype=torch.float32).mean().detach().item())        elif config.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800_causal_latent_dropout25_prune_t16_domainsep':
            mature_mask = decoupled_mature_sample_mask(result, target_batch, state_alive_channel=model.config.alive_channel, target_alpha_channel=3, foreground_threshold=0.1, alive_threshold=model.config.alive_threshold)
            attractor_mature_samples = int(mature_mask.sum().item())
            causal_probe_mature_samples = attractor_mature_samples
            if attractor_mature_samples > 0:
                mature_result = result[mature_mask]
                mature_target = target_batch[mature_mask]
                intact_trajectory = _rng_neutral_homeostasis_trajectory(model=model, result=mature_result, generator=device_rng)
                intact_future = intact_trajectory[1:]
                attractor_loss = attractor_trajectory_loss(intact_future, mature_target, visible_channels=config.visible_channels)
                probe_mask = causal_latent_probe_mask_domain_separated(mature_result.detach(), generator=device_rng, life_channel=model.config.alive_channel, alive_threshold=model.config.alive_threshold, fraction=CAUSAL_LATENT_DROPOUT_FRACTION)
                counterfactual_start = apply_latent_probe_intervention(mature_result.detach(), probe_mask, visible_channels=config.visible_channels)
                with torch.no_grad():
                    counterfactual_trajectory = _rng_neutral_homeostasis_trajectory(model=model, result=counterfactual_start, generator=device_rng)
                    intact_per_sample = attractor_trajectory_loss_per_sample(tuple(x.detach() for x in intact_future), mature_target.detach(), visible_channels=config.visible_channels)
                    counterfactual_per_sample = attractor_trajectory_loss_per_sample(counterfactual_trajectory[1:], mature_target.detach(), visible_channels=config.visible_channels)
                    causal_delta = (counterfactual_per_sample - intact_per_sample).detach()
                causal_prune_loss, _, classified_mask, nonbeneficial_mask, dropped_counts, actual_drop_fractions = causal_latent_prune_terms(mature_result, probe_mask, causal_delta, life_channel=model.config.alive_channel, alive_threshold=model.config.alive_threshold, maturity_floor=LIFE_VIABILITY_FLOOR)
                causal_probe_classified_samples = int(classified_mask.sum().item())
                causal_probe_nonbeneficial_samples = int(nonbeneficial_mask.sum().item())
                causal_probe_nonbeneficial_fraction = causal_probe_nonbeneficial_samples / causal_probe_classified_samples if causal_probe_classified_samples > 0 else 0.0
                causal_probe_dropped_cells_mean = float(dropped_counts.to(dtype=torch.float32).mean().item())
                causal_probe_actual_drop_fraction_mean = float(actual_drop_fractions.to(dtype=torch.float32).mean().item())
                if causal_probe_classified_samples > 0:
                    classified_delta = causal_delta[classified_mask]
                    causal_delta_mean = float(classified_delta.mean().item())
                    causal_delta_min = float(classified_delta.min().item())
                    causal_delta_max = float(classified_delta.max().item())
                    causal_intact_future_loss_mean = float(intact_per_sample[classified_mask].mean().item())
                    causal_counterfactual_future_loss_mean = float(counterfactual_per_sample[classified_mask].mean().item())
            else:
                attractor_loss = result.sum() * 0.0
                causal_prune_loss = result.sum() * 0.0
            occupancy_loss = decoupled_life_occupancy_ceiling_loss(result, target_batch, state_alive_channel=model.config.alive_channel, target_alpha_channel=3, foreground_threshold=0.1, alive_threshold=model.config.alive_threshold)
            formation_counts = formation_hard_active_counts(result, alpha_channel=model.config.alive_channel, alive_threshold=model.config.alive_threshold)
            formation_active_cells_mean = float(formation_counts.to(dtype=torch.float32).mean().detach().item())
            formation_active_cells_max = int(formation_counts.max().detach().item())
            frontier_floor_loss, frontier_counts = frontier_life_floor_loss(result, life_channel=model.config.alive_channel, alive_threshold=model.config.alive_threshold, viability_floor=LIFE_VIABILITY_FLOOR)
            frontier_cells_mean = float(frontier_counts.to(dtype=torch.float32).mean().detach().item())
        morph = training_morphology_loss(result=result, target=target_batch, config=config, homeostasis_loss=homeostasis_loss, attractor_loss=attractor_loss, occupancy_loss=occupancy_loss, trace_occupancy_loss=trace_occupancy_loss, allocation_loss=allocation_loss, frontier_floor_loss=frontier_floor_loss, visible_anchor_loss=visible_anchor_loss, causal_prune_loss=causal_prune_loss)
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
            if config.loss_mode == 'global_plus_foreground_bg_alpha_homeostasis':
                item['foreground_morphology_mse'] = float(foreground_morphology_mse(result, target_batch, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['background_alpha_mse'] = float(background_alpha_mse(result, target_batch, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['homeostasis_background_velocity_loss'] = float(homeostasis_loss.detach().item()) if homeostasis_loss is not None else 0.0
                item['homeostasis_mature_samples'] = homeostasis_mature_samples
            if config.loss_mode == 'global_plus_foreground_bg_alpha_homeostasis_t16':
                item['foreground_morphology_mse'] = float(foreground_morphology_mse(result, target_batch, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['background_alpha_mse'] = float(background_alpha_mse(result, target_batch, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['homeostasis_trajectory_velocity_loss'] = float(homeostasis_loss.detach().item()) if homeostasis_loss is not None else 0.0
                item['homeostasis_mature_samples'] = homeostasis_mature_samples
                item['homeostasis_probe_steps'] = HOME_T16_PROBE_STEPS
            if config.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16':
                item['foreground_morphology_mse'] = float(foreground_morphology_mse(result, target_batch, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['background_alpha_mse'] = float(background_alpha_mse(result, target_batch, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['attractor_trajectory_loss'] = float(attractor_loss.detach().item()) if attractor_loss is not None else 0.0
                item['attractor_mature_samples'] = attractor_mature_samples
                item['attractor_probe_steps'] = HOME_T16_PROBE_STEPS
            if config.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_ceil800':
                item['foreground_morphology_mse'] = float(foreground_morphology_mse(result, target_batch, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['background_alpha_mse'] = float(background_alpha_mse(result, target_batch, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['attractor_trajectory_loss'] = float(attractor_loss.detach().item()) if attractor_loss is not None else 0.0
                item['attractor_mature_samples'] = attractor_mature_samples
                item['attractor_probe_steps'] = HOME_T16_PROBE_STEPS
                item['formation_occupancy_ceiling_loss'] = float(occupancy_loss.detach().item()) if occupancy_loss is not None else 0.0
                item['formation_active_cells_mean'] = formation_active_cells_mean
                item['formation_active_cells_max'] = formation_active_cells_max
                item['formation_occupancy_ceiling'] = FORMATION_OCCUPANCY_CEILING
            if config.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_ceil800_traceceil800':
                item['foreground_morphology_mse'] = float(foreground_morphology_mse(result, target_batch, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['background_alpha_mse'] = float(background_alpha_mse(result, target_batch, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['attractor_trajectory_loss'] = float(attractor_loss.detach().item()) if attractor_loss is not None else 0.0
                item['attractor_mature_samples'] = attractor_mature_samples
                item['attractor_probe_steps'] = HOME_T16_PROBE_STEPS
                item['formation_occupancy_ceiling_loss'] = float(occupancy_loss.detach().item()) if occupancy_loss is not None else 0.0
                item['formation_active_cells_mean'] = formation_active_cells_mean
                item['formation_active_cells_max'] = formation_active_cells_max
                item['formation_occupancy_ceiling'] = FORMATION_OCCUPANCY_CEILING
                item['trace_occupancy_ceiling_loss'] = float(trace_occupancy_loss.detach().item()) if trace_occupancy_loss is not None else 0.0
                item['trace_active_cells_mean'] = trace_active_cells_mean
                item['trace_active_cells_max'] = trace_active_cells_max
                item['trace_occupancy_ceiling'] = FORMATION_OCCUPANCY_CEILING
            if config.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_ceil800_alloc_balanced_hard':
                item['foreground_morphology_mse'] = float(foreground_morphology_mse(result, target_batch, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['background_alpha_mse'] = float(background_alpha_mse(result, target_batch, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['attractor_trajectory_loss'] = float(attractor_loss.detach().item()) if attractor_loss is not None else 0.0
                item['attractor_mature_samples'] = attractor_mature_samples
                item['attractor_probe_steps'] = HOME_T16_PROBE_STEPS
                item['formation_occupancy_ceiling_loss'] = float(occupancy_loss.detach().item()) if occupancy_loss is not None else 0.0
                item['formation_active_cells_mean'] = formation_active_cells_mean
                item['formation_active_cells_max'] = formation_active_cells_max
                item['formation_occupancy_ceiling'] = FORMATION_OCCUPANCY_CEILING
                item['support_allocation_loss'] = float(allocation_loss.detach().item()) if allocation_loss is not None else 0.0
                item['support_false_positive_rate'] = support_false_positive_rate
                item['support_false_negative_rate'] = support_false_negative_rate
                item['support_true_positive_cells_mean'] = support_true_positive_cells_mean
            if config.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_life4_ceil800':
                item['foreground_morphology_mse'] = float(foreground_morphology_mse(result, target_batch, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['background_alpha_mse'] = float(background_alpha_mse(result, target_batch, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['attractor_trajectory_loss'] = float(attractor_loss.detach().item()) if attractor_loss is not None else 0.0
                item['attractor_mature_samples'] = attractor_mature_samples
                item['attractor_probe_steps'] = HOME_T16_PROBE_STEPS
                item['formation_occupancy_ceiling_loss'] = float(occupancy_loss.detach().item()) if occupancy_loss is not None else 0.0
                item['formation_active_cells_mean'] = formation_active_cells_mean
                item['formation_active_cells_max'] = formation_active_cells_max
                item['formation_occupancy_ceiling'] = FORMATION_OCCUPANCY_CEILING
                item['life_channel'] = model.config.alive_channel
                item['visible_alpha_channel'] = 3
            if config.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800':
                item['foreground_morphology_mse'] = float(foreground_morphology_mse(result, target_batch, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['background_alpha_mse'] = float(background_alpha_mse(result, target_batch, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['attractor_trajectory_loss'] = float(attractor_loss.detach().item()) if attractor_loss is not None else 0.0
                item['attractor_mature_samples'] = attractor_mature_samples
                item['attractor_probe_steps'] = HOME_T16_PROBE_STEPS
                item['formation_occupancy_ceiling_loss'] = float(occupancy_loss.detach().item()) if occupancy_loss is not None else 0.0
                item['formation_active_cells_mean'] = formation_active_cells_mean
                item['formation_active_cells_max'] = formation_active_cells_max
                item['formation_occupancy_ceiling'] = FORMATION_OCCUPANCY_CEILING
                item['frontier_floor_loss'] = float(frontier_floor_loss.detach().item()) if frontier_floor_loss is not None else 0.0
                item['frontier_cells_mean'] = frontier_cells_mean
                item['life_viability_floor'] = LIFE_VIABILITY_FLOOR
                item['life_channel'] = model.config.alive_channel
                item['visible_alpha_channel'] = 3
            if config.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800_visanchor_r1':
                item['foreground_morphology_mse'] = float(foreground_morphology_mse(result, target_batch, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['background_alpha_mse'] = float(background_alpha_mse(result, target_batch, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['attractor_trajectory_loss'] = float(attractor_loss.detach().item()) if attractor_loss is not None else 0.0
                item['attractor_mature_samples'] = attractor_mature_samples
                item['attractor_probe_steps'] = HOME_T16_PROBE_STEPS
                item['formation_occupancy_ceiling_loss'] = float(occupancy_loss.detach().item()) if occupancy_loss is not None else 0.0
                item['formation_active_cells_mean'] = formation_active_cells_mean
                item['formation_active_cells_max'] = formation_active_cells_max
                item['formation_occupancy_ceiling'] = FORMATION_OCCUPANCY_CEILING
                item['frontier_floor_loss'] = float(frontier_floor_loss.detach().item()) if frontier_floor_loss is not None else 0.0
                item['frontier_cells_mean'] = frontier_cells_mean
                item['life_viability_floor'] = LIFE_VIABILITY_FLOOR
                item['mature_visible_anchor_loss'] = float(visible_anchor_loss.detach().item()) if visible_anchor_loss is not None else 0.0
                item['anchor_mature_samples'] = anchor_mature_samples
                item['unanchored_life_fraction_mean'] = unanchored_life_fraction_mean
                item['unanchored_life_cells_mean'] = unanchored_life_cells_mean
                item['life_channel'] = model.config.alive_channel
                item['visible_alpha_channel'] = 3
            if config.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800_causal_latent_dropout25_prune_t16':
                item['foreground_morphology_mse'] = float(foreground_morphology_mse(result, target_batch, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['background_alpha_mse'] = float(background_alpha_mse(result, target_batch, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['attractor_trajectory_loss'] = float(attractor_loss.detach().item()) if attractor_loss is not None else 0.0
                item['attractor_mature_samples'] = attractor_mature_samples
                item['attractor_probe_steps'] = HOME_T16_PROBE_STEPS
                item['formation_occupancy_ceiling_loss'] = float(occupancy_loss.detach().item()) if occupancy_loss is not None else 0.0
                item['formation_active_cells_mean'] = formation_active_cells_mean
                item['formation_active_cells_max'] = formation_active_cells_max
                item['formation_occupancy_ceiling'] = FORMATION_OCCUPANCY_CEILING
                item['frontier_floor_loss'] = float(frontier_floor_loss.detach().item()) if frontier_floor_loss is not None else 0.0
                item['frontier_cells_mean'] = frontier_cells_mean
                item['causal_latent_prune_loss'] = float(causal_prune_loss.detach().item()) if causal_prune_loss is not None else 0.0
                item['causal_probe_mature_samples'] = causal_probe_mature_samples
                item['causal_probe_classified_samples'] = causal_probe_classified_samples
                item['causal_probe_nonbeneficial_samples'] = causal_probe_nonbeneficial_samples
                item['causal_probe_nonbeneficial_fraction'] = causal_probe_nonbeneficial_fraction
                item['causal_probe_dropped_cells_mean'] = causal_probe_dropped_cells_mean
                item['causal_probe_actual_drop_fraction_mean'] = causal_probe_actual_drop_fraction_mean
                item['causal_delta_mean'] = causal_delta_mean
                item['causal_delta_min'] = causal_delta_min
                item['causal_delta_max'] = causal_delta_max
                item['causal_intact_future_loss_mean'] = causal_intact_future_loss_mean
                item['causal_counterfactual_future_loss_mean'] = causal_counterfactual_future_loss_mean
                item['causal_dropout_fraction'] = CAUSAL_LATENT_DROPOUT_FRACTION
                item['causal_probe_steps'] = HOME_T16_PROBE_STEPS
                item['life_viability_floor'] = LIFE_VIABILITY_FLOOR
                item['life_channel'] = model.config.alive_channel
                item['visible_alpha_channel'] = 3            if config.loss_mode == 'global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800_causal_latent_dropout25_prune_t16_domainsep':
                item['foreground_morphology_mse'] = float(foreground_morphology_mse(result, target_batch, visible_channels=config.visible_channels, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['background_alpha_mse'] = float(background_alpha_mse(result, target_batch, alpha_channel=3, foreground_threshold=0.1).detach().item())
                item['attractor_trajectory_loss'] = float(attractor_loss.detach().item()) if attractor_loss is not None else 0.0
                item['attractor_mature_samples'] = attractor_mature_samples
                item['attractor_probe_steps'] = HOME_T16_PROBE_STEPS
                item['formation_occupancy_ceiling_loss'] = float(occupancy_loss.detach().item()) if occupancy_loss is not None else 0.0
                item['formation_active_cells_mean'] = formation_active_cells_mean
                item['formation_active_cells_max'] = formation_active_cells_max
                item['formation_occupancy_ceiling'] = FORMATION_OCCUPANCY_CEILING
                item['frontier_floor_loss'] = float(frontier_floor_loss.detach().item()) if frontier_floor_loss is not None else 0.0
                item['frontier_cells_mean'] = frontier_cells_mean
                item['causal_latent_prune_loss'] = float(causal_prune_loss.detach().item()) if causal_prune_loss is not None else 0.0
                item['causal_probe_mature_samples'] = causal_probe_mature_samples
                item['causal_probe_classified_samples'] = causal_probe_classified_samples
                item['causal_probe_nonbeneficial_samples'] = causal_probe_nonbeneficial_samples
                item['causal_probe_nonbeneficial_fraction'] = causal_probe_nonbeneficial_fraction
                item['causal_probe_dropped_cells_mean'] = causal_probe_dropped_cells_mean
                item['causal_probe_actual_drop_fraction_mean'] = causal_probe_actual_drop_fraction_mean
                item['causal_delta_mean'] = causal_delta_mean
                item['causal_delta_min'] = causal_delta_min
                item['causal_delta_max'] = causal_delta_max
                item['causal_intact_future_loss_mean'] = causal_intact_future_loss_mean
                item['causal_counterfactual_future_loss_mean'] = causal_counterfactual_future_loss_mean
                item['causal_dropout_fraction'] = CAUSAL_LATENT_DROPOUT_FRACTION
                item['causal_probe_steps'] = HOME_T16_PROBE_STEPS
                item['life_viability_floor'] = LIFE_VIABILITY_FLOOR
                item['life_channel'] = model.config.alive_channel
                item['visible_alpha_channel'] = 3
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
