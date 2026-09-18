import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import torch
import yaml

from yggdrasil.config import load_config
from yggdrasil.metrics import (
    background_alpha_mse,
    foreground_morphology_mse,
    morphology_mse,
)
from yggdrasil.nca import NCAConfig, NeuralCellularAutomaton, make_seed_state
from yggdrasil.resume import ResumableTrainingSession
from yggdrasil.target import TargetSpec, make_target
from yggdrasil.training import (
    HOME_T16_PROBE_STEPS,
    TrainingConfig,
    _rng_neutral_homeostasis_trajectory,
    attractor_trajectory_loss,
    train,
    training_morphology_loss,
)

ROOT = Path(__file__).resolve().parents[1]
MODE = "global_plus_foreground_bg_alpha_attractor_t16"


def _center_target(size: int = 3) -> torch.Tensor:
    target = torch.zeros((1, 4, size, size), dtype=torch.float32)
    target[:, :, size // 2, size // 2] = 1.0
    return target


def _static_loss(state: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    return (
        morphology_mse(state, target, visible_channels=4)
        + foreground_morphology_mse(state, target, visible_channels=4)
        + background_alpha_mse(state, target)
    )


def test_attract16_trajectory_is_exact_arithmetic_mean_of_16_future_target_losses() -> None:
    target = _center_target(3)
    states = []
    expected_terms = []
    for index in range(16):
        state = target.clone()
        state[:, 3, 0, 0] = 0.01 * (index + 1)
        states.append(state)
        expected_terms.append(_static_loss(state, target))
    actual = attractor_trajectory_loss(tuple(states), target, visible_channels=4)
    expected = torch.stack(expected_terms).mean()
    assert actual.item() == pytest.approx(expected.item())


def test_attract16_rejects_wrong_horizon() -> None:
    target = _center_target(3)
    with pytest.raises(ValueError, match="exactly 16 future states"):
        attractor_trajectory_loss((target.clone(),), target)


def test_attract16_exact_full_training_formula() -> None:
    state = torch.zeros((1, 4, 5, 5), dtype=torch.float32)
    target = torch.zeros_like(state)
    target[:, :, 2, 2] = 1.0
    attractor = torch.tensor(0.25)
    config = TrainingConfig(loss_mode=MODE, visible_channels=4)
    actual = training_morphology_loss(
        result=state,
        target=target,
        config=config,
        attractor_loss=attractor,
    )
    expected = _static_loss(state, target) + attractor
    assert actual.item() == pytest.approx(expected.item())


def test_attract16_requires_auxiliary_term() -> None:
    target = _center_target(5)
    state = torch.zeros_like(target)
    with pytest.raises(ValueError, match="ATTRACT-16 requires attractor_loss"):
        training_morphology_loss(
            result=state,
            target=target,
            config=TrainingConfig(loss_mode=MODE),
        )


def test_attract16_reuses_exact_16_step_rng_neutral_virtual_trajectory() -> None:
    class CountingModel:
        def __init__(self) -> None:
            self.calls = 0

        def step(self, state, *, generator):
            self.calls += 1
            noise = torch.rand(
                state.shape,
                generator=generator,
                dtype=state.dtype,
                device=state.device,
            )
            return state + noise * 0.001

    model = CountingModel()
    result = torch.zeros((1, 4, 3, 3), dtype=torch.float32)
    generator = torch.Generator(device="cpu").manual_seed(119)
    before = generator.get_state().clone()
    trajectory = _rng_neutral_homeostasis_trajectory(
        model=model,
        result=result,
        generator=generator,
    )
    after = generator.get_state().clone()

    assert HOME_T16_PROBE_STEPS == 16
    assert model.calls == 16
    assert len(trajectory) == 17
    assert torch.equal(before, after)


def test_stab11_config_validates_and_freezes_attract16_envelope() -> None:
    config = load_config(ROOT / "experiments/dg1a/configs/p0_stab11_attract_t16.yaml")
    assert config["training"]["loss_mode"] == MODE
    assert HOME_T16_PROBE_STEPS == 16
    assert config["training"]["iterations"] == 200
    assert config["training"]["steps_min"] == 64
    assert config["training"]["steps_max"] == 96
    assert config["training"]["batch_size"] == 8
    assert config["training"]["pool_size"] == 64
    assert config["training"]["damage_probability"] == pytest.approx(0.5)
    assert config["training"]["damage_height_fraction"] == pytest.approx(0.5)
    assert config["training"]["damage_width_fraction"] == pytest.approx(0.5)
    assert config["evaluation"]["growth_steps"] == 96
    assert config["evaluation"]["persistence_steps"] == 96
    assert config["recovery"]["eval_steps"] == 96
    assert config["recovery"]["lesion"]["height_fraction"] == pytest.approx(0.6)
    assert config["recovery"]["lesion"]["width_fraction"] == pytest.approx(0.6)


def _tiny_fixture():
    torch.manual_seed(67)
    model = NeuralCellularAutomaton(
        NCAConfig(state_channels=8, hidden_channels=16, fire_rate=1.0, max_steps=20)
    )
    seed = make_seed_state(batch_size=1, channels=8, height=9, width=9)
    target = make_target(
        batch_size=1,
        channels=8,
        height=9,
        width=9,
        spec=TargetSpec(radius=2),
    )
    config = TrainingConfig(
        variant="regeneration",
        iterations=2,
        learning_rate=1e-3,
        steps_min=2,
        steps_max=2,
        batch_size=2,
        pool_size=4,
        damage_probability=0.5,
        damage_min_active_cells=4,
        loss_mode=MODE,
        record_every=1,
        seed=10,
    )
    return model, seed, target, config


def test_train_records_attract16_component_telemetry() -> None:
    model, seed, target, config = _tiny_fixture()
    summary = train(model=model, seed_state=seed, target=target, config=config)
    item = summary.history[-1]
    assert summary.loss_mode == MODE
    assert "foreground_morphology_mse" in item
    assert "background_alpha_mse" in item
    assert "attractor_trajectory_loss" in item
    assert "attractor_mature_samples" in item
    assert item["attractor_probe_steps"] == 16
    assert item["attractor_trajectory_loss"] >= 0.0
    assert item["attractor_mature_samples"] >= 0


def test_attract16_immature_batch_returns_differentiable_zero_without_virtual_run(monkeypatch) -> None:
    import yggdrasil.training as training_module

    model, seed, target, config = _tiny_fixture()
    monkeypatch.setattr(
        training_module,
        "homeostasis_mature_sample_mask",
        lambda result, target, **kwargs: torch.zeros(
            result.shape[0], dtype=torch.bool, device=result.device
        ),
    )

    def fail_if_called(*args, **kwargs):
        raise AssertionError("virtual trajectory must not run for an immature batch")

    monkeypatch.setattr(
        training_module,
        "_rng_neutral_homeostasis_trajectory",
        fail_if_called,
    )
    summary = train(model=model, seed_state=seed, target=target, config=config)
    item = summary.history[-1]
    assert item["attractor_mature_samples"] == 0
    assert item["attractor_trajectory_loss"] == pytest.approx(0.0)


def test_resumable_training_records_attract16_component_telemetry() -> None:
    model, seed, target, config = _tiny_fixture()
    session = ResumableTrainingSession(model, seed, target, config)
    session.advance(2)
    item = session.summary().history[-1]
    assert "foreground_morphology_mse" in item
    assert "background_alpha_mse" in item
    assert "attractor_trajectory_loss" in item
    assert "attractor_mature_samples" in item
    assert item["attractor_probe_steps"] == 16


def test_resumable_pool_never_stores_attract16_virtual_trajectory(monkeypatch) -> None:
    import yggdrasil.resume as resume_module

    model, seed, target, config = _tiny_fixture()
    session = ResumableTrainingSession(model, seed, target, config)

    def extreme_trajectory(*, model, result, generator):
        future = tuple(result * 0.0 + 999.0 for _ in range(16))
        return (result,) + future

    monkeypatch.setattr(
        resume_module,
        "_rng_neutral_homeostasis_trajectory",
        extreme_trajectory,
    )
    monkeypatch.setattr(
        resume_module,
        "homeostasis_mature_sample_mask",
        lambda result, target, **kwargs: torch.ones(
            result.shape[0], dtype=torch.bool, device=result.device
        ),
    )
    session.advance(1)
    storage = session.pool.state_dict()["storage"]
    assert float(storage.abs().max().item()) < 999.0


def test_home1_and_home_t16_objective_paths_remain_compatible() -> None:
    target = _center_target(5)
    state = torch.zeros_like(target)
    home = torch.tensor(0.125)

    home1 = training_morphology_loss(
        result=state,
        target=target,
        config=TrainingConfig(
            loss_mode="global_plus_foreground_bg_alpha_homeostasis"
        ),
        homeostasis_loss=home,
    )
    home_t16 = training_morphology_loss(
        result=state,
        target=target,
        config=TrainingConfig(
            loss_mode="global_plus_foreground_bg_alpha_homeostasis_t16"
        ),
        homeostasis_loss=home,
    )
    expected = _static_loss(state, target) + home
    assert home1.item() == pytest.approx(expected.item())
    assert home_t16.item() == pytest.approx(expected.item())


def test_runner_evidence_records_attract16_mode_and_telemetry(tmp_path: Path) -> None:
    config = {
        "experiment_id": "DG1A-P0",
        "variant": "growth_only",
        "seed": 0,
        "device": "cpu",
        "precision": "float32",
        "model": {
            "state_channels": 8,
            "hidden_channels": 16,
            "fire_rate": 1.0,
            "alive_channel": 3,
            "alive_threshold": 0.1,
            "max_steps": 20,
        },
        "phenotype": {"height": 7, "width": 7, "seed_location": "center"},
        "target": {"kind": "disk", "radius": 1, "rgba": [0.15, 0.75, 0.30, 1.0]},
        "training": {
            "iterations": 1,
            "learning_rate": 0.001,
            "steps_min": 1,
            "steps_max": 1,
            "batch_size": 1,
            "pool_size": 1,
            "damage_probability": 0.0,
            "damage_height_fraction": 0.5,
            "damage_width_fraction": 0.5,
            "damage_min_active_cells": 1,
            "gradient_clip_norm": 1.0,
            "hidden_state_l2_weight": 0.00001,
            "loss_mode": MODE,
        },
        "resource_limits": {
            "max_height": 7,
            "max_width": 7,
            "max_state_channels": 8,
            "max_hidden_channels": 16,
            "max_development_steps": 20,
        },
        "evaluation": {"growth_steps": 1, "persistence_steps": 1},
        "recovery": {
            "eval_steps": 1,
            "lesion": {"kind": "center", "height_fraction": 0.5, "width_fraction": 0.5},
        },
        "reporting": {"visible_channels": 4, "record_every_iterations": 1},
    }
    config_path = tmp_path / "tiny_stab11.yaml"
    evidence_path = tmp_path / "tiny_stab11.json"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "experiments/dg1a/run_p0.py"),
            "--config",
            str(config_path),
            "--evidence",
            str(evidence_path),
        ],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["effective_training_loss_mode"] == MODE
    assert evidence["training"]["loss_mode"] == MODE
    item = evidence["training"]["history"][-1]
    assert "attractor_trajectory_loss" in item
    assert "attractor_mature_samples" in item
    assert item["attractor_probe_steps"] == 16
