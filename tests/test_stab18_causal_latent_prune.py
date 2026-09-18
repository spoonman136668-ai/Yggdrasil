import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import torch
import yaml

from yggdrasil.config import load_config
from yggdrasil.metrics import background_alpha_mse, foreground_morphology_mse, morphology_mse
from yggdrasil.nca import NCAConfig, NeuralCellularAutomaton, make_seed_state
from yggdrasil.resume import ResumableTrainingSession
from yggdrasil.target import TargetSpec, make_target
from yggdrasil.training import (
    CAUSAL_LATENT_DROPOUT_FRACTION,
    FORMATION_OCCUPANCY_CEILING,
    HOME_T16_PROBE_STEPS,
    LIFE_VIABILITY_FLOOR,
    TrainingConfig,
    _rng_neutral_homeostasis_trajectory,
    apply_latent_probe_intervention,
    attractor_trajectory_loss,
    attractor_trajectory_loss_per_sample,
    causal_latent_probe_mask,
    causal_latent_prune_terms,
    train,
    training_morphology_loss,
)

ROOT = Path(__file__).resolve().parents[1]
MODE = "global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800_causal_latent_dropout25_prune_t16"


def _state(size: int = 8, channels: int = 8) -> torch.Tensor:
    return torch.zeros((1, channels, size, size), dtype=torch.float32)


def test_probe_mask_matches_fixed_quarter_threshold_and_restores_rng() -> None:
    state = _state()
    state[:, 4] = 0.2
    generator = torch.Generator(device="cpu").manual_seed(1234)
    before = generator.get_state().clone()

    shadow = torch.Generator(device="cpu")
    shadow.set_state(before.clone())
    random_values = torch.rand((1, 1, 8, 8), generator=shadow)
    expected = random_values < 0.25

    actual = causal_latent_probe_mask(state, generator=generator)

    assert CAUSAL_LATENT_DROPOUT_FRACTION == pytest.approx(0.25)
    assert torch.equal(actual, expected)
    assert torch.equal(generator.get_state(), before)


def test_probe_selects_only_hard_alive_life4_cells() -> None:
    state = _state()
    state[:, 4, :4] = 0.2
    generator = torch.Generator(device="cpu").manual_seed(5)
    mask = causal_latent_probe_mask(state, generator=generator)
    hard_alive = state[:, 4:5] > 0.1
    assert not bool((mask & ~hard_alive).any())


def test_latent_intervention_preserves_rgba_and_zeros_latent_only_at_probe() -> None:
    state = torch.arange(1 * 8 * 4 * 4, dtype=torch.float32).reshape(1, 8, 4, 4)
    mask = torch.zeros((1, 1, 4, 4), dtype=torch.bool)
    mask[:, :, 1, 2] = True

    result = apply_latent_probe_intervention(state, mask, visible_channels=4)

    assert torch.equal(result[:, :4], state[:, :4])
    assert torch.count_nonzero(result[:, 4:, 1, 2]) == 0
    unprobed = ~mask.expand(-1, 4, -1, -1)
    assert torch.equal(result[:, 4:][unprobed], state[:, 4:][unprobed])


def test_per_sample_future_loss_reduces_to_scalar_attractor_loss() -> None:
    target = make_target(batch_size=2, channels=8, height=9, width=9, spec=TargetSpec(radius=2))
    state = target.clone()
    state[0, 0, 0, 0] += 0.5
    state[1, 1, 8, 8] -= 0.25
    states = tuple(state.clone() for _ in range(HOME_T16_PROBE_STEPS))

    per_sample = attractor_trajectory_loss_per_sample(states, target, visible_channels=4)
    scalar = attractor_trajectory_loss(states, target, visible_channels=4)

    assert per_sample.shape == (2,)
    assert per_sample.mean().item() == pytest.approx(scalar.item(), rel=1e-6, abs=1e-7)


def test_rng_neutral_trajectories_are_matched_for_identical_starts() -> None:
    torch.manual_seed(17)
    model = NeuralCellularAutomaton(NCAConfig(state_channels=8, hidden_channels=16, fire_rate=0.5, alive_channel=4, max_steps=32))
    state = torch.randn((1, 8, 7, 7), dtype=torch.float32) * 0.05
    state[:, 4, 3, 3] = 0.2
    generator = torch.Generator(device="cpu").manual_seed(99)
    before = generator.get_state().clone()

    a = _rng_neutral_homeostasis_trajectory(model=model, result=state, generator=generator)
    middle = generator.get_state().clone()
    b = _rng_neutral_homeostasis_trajectory(model=model, result=state, generator=generator)

    assert torch.equal(before, middle)
    assert torch.equal(before, generator.get_state())
    assert all(torch.equal(x, y) for x, y in zip(a, b))


def test_immature_causal_prune_is_differentiable_zero() -> None:
    state = _state()
    state[:, 4].reshape(-1)[:3] = 0.2
    state.requires_grad_(True)
    mask = torch.zeros((1, 1, 8, 8), dtype=torch.bool)
    mask[:, :, 0, 0] = True
    delta = torch.tensor([-1.0])

    loss, mature, classified, nonbeneficial, _, _ = causal_latent_prune_terms(
        state, mask, delta, maturity_floor=4
    )

    assert mature.tolist() == [False]
    assert classified.tolist() == [False]
    assert nonbeneficial.tolist() == [False]
    assert loss.item() == pytest.approx(0.0)
    loss.backward()
    assert torch.count_nonzero(state.grad) == 0


def _mature_probe_fixture(delta_value: float):
    state = _state()
    state[:, 4].reshape(-1)[:4] = 0.2
    state.requires_grad_(True)
    mask = torch.zeros((1, 1, 8, 8), dtype=torch.bool)
    mask[:, :, 0, 0] = True
    mask[:, :, 0, 1] = True
    delta = torch.tensor([delta_value], dtype=torch.float32, requires_grad=True)
    return state, mask, delta


def test_positive_causal_delta_gets_zero_prune_gradient() -> None:
    state, mask, delta = _mature_probe_fixture(0.01)
    loss, mature, classified, nonbeneficial, _, _ = causal_latent_prune_terms(
        state, mask, delta, maturity_floor=4
    )
    assert mature.tolist() == [True]
    assert classified.tolist() == [True]
    assert nonbeneficial.tolist() == [False]
    assert loss.item() == pytest.approx(0.0)
    loss.backward()
    assert torch.count_nonzero(state.grad) == 0
    assert delta.grad is None


@pytest.mark.parametrize("delta_value", [0.0, -0.01])
def test_nonpositive_causal_delta_prunes_only_probed_life4(delta_value: float) -> None:
    state, mask, delta = _mature_probe_fixture(delta_value)
    loss, mature, classified, nonbeneficial, dropped_counts, actual_fraction = causal_latent_prune_terms(
        state, mask, delta, maturity_floor=4
    )

    assert mature.tolist() == [True]
    assert classified.tolist() == [True]
    assert nonbeneficial.tolist() == [True]
    assert dropped_counts.tolist() == [2]
    assert actual_fraction.tolist() == pytest.approx([0.5])
    assert loss.item() == pytest.approx(0.5)

    loss.backward()
    life_grad = state.grad[:, 4:5]
    hard_alive = state.detach()[:, 4:5] > 0.1
    assert torch.all(life_grad[mask] > 0.0)
    assert torch.all(life_grad[hard_alive & ~mask] == 0.0)
    assert torch.all(life_grad[~hard_alive] == 0.0)
    assert torch.count_nonzero(state.grad[:, :4]) == 0
    assert torch.count_nonzero(state.grad[:, 5:]) == 0
    assert delta.grad is None


def test_zero_probed_cells_fail_safe_to_zero_contribution() -> None:
    state = _state()
    state[:, 4].reshape(-1)[:4] = 0.2
    state.requires_grad_(True)
    mask = torch.zeros((1, 1, 8, 8), dtype=torch.bool)
    delta = torch.tensor([-1.0])

    loss, mature, classified, nonbeneficial, dropped_counts, _ = causal_latent_prune_terms(
        state, mask, delta, maturity_floor=4
    )
    assert mature.tolist() == [True]
    assert classified.tolist() == [False]
    assert nonbeneficial.tolist() == [False]
    assert dropped_counts.tolist() == [0]
    assert loss.item() == pytest.approx(0.0)
    loss.backward()
    assert torch.count_nonzero(state.grad) == 0


def test_stab18_full_objective_formula() -> None:
    result = torch.zeros((1, 8, 9, 9), dtype=torch.float32)
    target = make_target(batch_size=1, channels=8, height=9, width=9, spec=TargetSpec(radius=2))
    cfg = TrainingConfig(loss_mode=MODE, visible_channels=4)
    attractor = torch.tensor(0.25)
    occupancy = torch.tensor(0.125)
    floor = torch.tensor(0.375)
    causal = torch.tensor(0.5)

    actual = training_morphology_loss(
        result=result,
        target=target,
        config=cfg,
        attractor_loss=attractor,
        occupancy_loss=occupancy,
        frontier_floor_loss=floor,
        causal_prune_loss=causal,
    )
    expected = (
        morphology_mse(result, target, visible_channels=4)
        + foreground_morphology_mse(result, target, visible_channels=4)
        + background_alpha_mse(result, target)
        + attractor + occupancy + floor + causal
    )
    assert actual.item() == pytest.approx(expected.item())


def test_stab18_requires_causal_prune_auxiliary() -> None:
    result = torch.zeros((1, 8, 9, 9), dtype=torch.float32)
    target = make_target(batch_size=1, channels=8, height=9, width=9, spec=TargetSpec(radius=2))
    cfg = TrainingConfig(loss_mode=MODE, visible_channels=4)
    with pytest.raises(ValueError, match="causal_prune_loss"):
        training_morphology_loss(
            result=result,
            target=target,
            config=cfg,
            attractor_loss=torch.tensor(0.0),
            occupancy_loss=torch.tensor(0.0),
            frontier_floor_loss=torch.tensor(0.0),
        )


def _tiny_fixture():
    torch.manual_seed(101)
    model = NeuralCellularAutomaton(NCAConfig(state_channels=8, hidden_channels=16, fire_rate=1.0, alive_channel=4, max_steps=20))
    seed = make_seed_state(batch_size=1, channels=8, height=9, width=9, alive_channel=4)
    target = make_target(batch_size=1, channels=8, height=9, width=9, spec=TargetSpec(radius=2))
    config = TrainingConfig(
        variant="regeneration", iterations=2, learning_rate=1e-3,
        steps_min=2, steps_max=2, batch_size=2, pool_size=4,
        damage_probability=0.5, damage_min_active_cells=4,
        loss_mode=MODE, record_every=1, seed=17,
    )
    return model, seed, target, config


def test_train_records_stab18_telemetry() -> None:
    model, seed, target, config = _tiny_fixture()
    summary = train(model=model, seed_state=seed, target=target, config=config)
    item = summary.history[-1]
    assert summary.loss_mode == MODE
    for key in (
        "causal_latent_prune_loss",
        "causal_probe_mature_samples",
        "causal_probe_classified_samples",
        "causal_probe_nonbeneficial_samples",
        "causal_probe_nonbeneficial_fraction",
        "causal_probe_dropped_cells_mean",
        "causal_probe_actual_drop_fraction_mean",
        "causal_delta_mean",
        "causal_delta_min",
        "causal_delta_max",
        "causal_intact_future_loss_mean",
        "causal_counterfactual_future_loss_mean",
        "causal_dropout_fraction",
        "causal_probe_steps",
    ):
        assert key in item
    assert item["causal_dropout_fraction"] == pytest.approx(0.25)
    assert item["causal_probe_steps"] == 16
    assert item["life_channel"] == 4


def test_resumable_records_stab18_telemetry() -> None:
    model, seed, target, config = _tiny_fixture()
    session = ResumableTrainingSession(model, seed, target, config)
    session.advance(2)
    item = session.summary().history[-1]
    assert "causal_latent_prune_loss" in item
    assert "causal_probe_nonbeneficial_fraction" in item
    assert "causal_delta_mean" in item
    assert item["causal_dropout_fraction"] == pytest.approx(0.25)
    assert item["life_channel"] == 4


def test_stab16_and_stab17_modes_remain_compatible() -> None:
    model = NeuralCellularAutomaton(NCAConfig(state_channels=8, hidden_channels=16, alive_channel=4))
    TrainingConfig(loss_mode="global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800").validate(model)
    TrainingConfig(loss_mode="global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800_visanchor_r1").validate(model)


def test_stab18_frozen_config() -> None:
    config = load_config(ROOT / "experiments/dg1a/configs/p0_stab18_life4_band113_800_causal_latent_dropout25_prune_t16.yaml")
    assert config["model"]["alive_channel"] == 4
    assert config["model"]["alive_threshold"] == pytest.approx(0.1)
    assert config["reporting"]["visible_channels"] == 4
    assert config["training"]["loss_mode"] == MODE
    assert config["training"]["iterations"] == 200
    assert config["training"]["steps_min"] == 64
    assert config["training"]["steps_max"] == 96
    assert config["training"]["batch_size"] == 8
    assert config["training"]["pool_size"] == 64
    assert config["training"]["damage_probability"] == pytest.approx(0.5)
    assert config["training"]["damage_height_fraction"] == pytest.approx(0.5)
    assert config["training"]["damage_width_fraction"] == pytest.approx(0.5)
    assert config["training"]["hidden_state_l2_weight"] == pytest.approx(0.00001)
    assert CAUSAL_LATENT_DROPOUT_FRACTION == pytest.approx(0.25)
    assert LIFE_VIABILITY_FLOOR == 113
    assert FORMATION_OCCUPANCY_CEILING == 800
    assert HOME_T16_PROBE_STEPS == 16


def test_stab18_config_fails_closed_without_life4() -> None:
    model = NeuralCellularAutomaton(NCAConfig(state_channels=8, hidden_channels=16, alive_channel=3))
    with pytest.raises(ValueError, match="STAB-18 requires model alive_channel 4"):
        TrainingConfig(loss_mode=MODE).validate(model)


def test_resumable_pool_never_stores_stab18_virtual_trajectory(monkeypatch) -> None:
    import yggdrasil.resume as resume_module
    model, seed, target, config = _tiny_fixture()
    session = ResumableTrainingSession(model, seed, target, config)

    original = resume_module._rng_neutral_homeostasis_trajectory

    def extreme_trajectory(*, model, result, generator):
        states = original(model=model, result=result, generator=generator)
        return (states[0],) + tuple(x * 0.0 + 999.0 for x in states[1:])

    monkeypatch.setattr(resume_module, "_rng_neutral_homeostasis_trajectory", extreme_trajectory)
    monkeypatch.setattr(
        resume_module,
        "decoupled_mature_sample_mask",
        lambda result, target, **kwargs: torch.ones(result.shape[0], dtype=torch.bool, device=result.device),
    )
    session.advance(1)
    storage = session.pool.state_dict()["storage"]
    assert float(storage.abs().max().item()) < 999.0


def test_runner_evidence_records_stab18_mode_and_telemetry(tmp_path: Path) -> None:
    config = {
        "experiment_id": "DG1A-P0", "variant": "growth_only", "seed": 0,
        "device": "cpu", "precision": "float32",
        "model": {"state_channels": 8, "hidden_channels": 16, "fire_rate": 1.0, "alive_channel": 4, "alive_threshold": 0.1, "max_steps": 20},
        "phenotype": {"height": 7, "width": 7, "seed_location": "center"},
        "target": {"kind": "disk", "radius": 1, "rgba": [0.15, 0.75, 0.30, 1.0]},
        "training": {
            "iterations": 1, "learning_rate": 0.001, "steps_min": 1, "steps_max": 1,
            "batch_size": 1, "pool_size": 1, "damage_probability": 0.0,
            "damage_height_fraction": 0.5, "damage_width_fraction": 0.5,
            "damage_min_active_cells": 1, "gradient_clip_norm": 1.0,
            "hidden_state_l2_weight": 0.00001, "loss_mode": MODE,
        },
        "resource_limits": {"max_height": 7, "max_width": 7, "max_state_channels": 8, "max_hidden_channels": 16, "max_development_steps": 20},
        "evaluation": {"growth_steps": 1, "persistence_steps": 1},
        "recovery": {"eval_steps": 1, "lesion": {"kind": "center", "height_fraction": 0.5, "width_fraction": 0.5}},
        "reporting": {"visible_channels": 4, "record_every_iterations": 1},
    }
    config_path = tmp_path / "tiny_stab18.yaml"
    evidence_path = tmp_path / "tiny_stab18.json"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    subprocess.run(
        [sys.executable, str(ROOT / "experiments/dg1a/run_p0.py"), "--config", str(config_path), "--evidence", str(evidence_path)],
        cwd=ROOT, env=env, check=True, capture_output=True, text=True,
    )
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["effective_training_loss_mode"] == MODE
    item = evidence["training"]["history"][-1]
    assert "causal_latent_prune_loss" in item
    assert "causal_probe_nonbeneficial_fraction" in item
    assert "causal_delta_mean" in item
    assert item["causal_dropout_fraction"] == pytest.approx(0.25)
    assert item["life_channel"] == 4
