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
    homeostasis_background_velocity_loss,
    homeostasis_mature_sample_mask,
    morphology_mse,
)
from yggdrasil.nca import NCAConfig, NeuralCellularAutomaton, make_seed_state
from yggdrasil.resume import ResumableTrainingSession
from yggdrasil.target import TargetSpec, make_target
from yggdrasil.training import (
    TrainingConfig,
    _rng_neutral_homeostasis_probe,
    train,
    training_morphology_loss,
)

ROOT = Path(__file__).resolve().parents[1]
MODE = "global_plus_foreground_bg_alpha_homeostasis"


def test_homeostasis_immature_batch_returns_differentiable_zero() -> None:
    target = torch.zeros((1, 4, 5, 5), dtype=torch.float32)
    target[:, 3, 2, 2] = 1.0
    result = torch.zeros_like(target, requires_grad=True)
    probe = torch.zeros_like(target, requires_grad=True)
    loss = homeostasis_background_velocity_loss(result, probe, target)
    assert loss.item() == pytest.approx(0.0)
    loss.backward()
    assert probe.grad is not None


def test_homeostasis_maturity_is_target_foreground_cardinality() -> None:
    target = torch.zeros((2, 4, 5, 5), dtype=torch.float32)
    target[0, 3, 2, 2] = 1.0
    target[1, 3, 2, 2] = 1.0
    target[1, 3, 2, 3] = 1.0
    state = torch.zeros_like(target)
    state[0, 3, 0, 0] = 0.2
    state[1, 3, 0, 0] = 0.2
    mask = homeostasis_mature_sample_mask(state, target)
    assert mask.tolist() == [True, False]


def test_homeostasis_positive_background_velocity_formula() -> None:
    target = torch.zeros((1, 4, 3, 3), dtype=torch.float32)
    target[:, 3, 1, 1] = 1.0
    result = torch.zeros_like(target)
    result[:, 3, 1, 1] = 1.0
    probe = result.clone()
    probe[:, 3, 0, 0] = 0.05
    loss = homeostasis_background_velocity_loss(result, probe, target, alive_threshold=0.1)
    assert loss.item() == pytest.approx(0.5 / 8.0)


def test_homeostasis_contraction_and_no_growth_are_zero() -> None:
    target = torch.zeros((1, 4, 3, 3), dtype=torch.float32)
    target[:, 3, 1, 1] = 1.0
    result = torch.zeros_like(target)
    result[:, 3, 1, 1] = 1.0
    result[:, 3, 0, 0] = 0.2
    probe = result.clone()
    probe[:, 3, 0, 0] = 0.1
    assert homeostasis_background_velocity_loss(result, probe, target).item() == pytest.approx(0.0)


def test_home1_exact_full_formula() -> None:
    state = torch.zeros((1, 4, 5, 5), dtype=torch.float32)
    target = torch.zeros_like(state)
    target[:, :, 2, 2] = 1.0
    homeostasis = torch.tensor(0.125)
    config = TrainingConfig(loss_mode=MODE, visible_channels=4)
    actual = training_morphology_loss(result=state, target=target, config=config, homeostasis_loss=homeostasis)
    expected = (
        morphology_mse(state, target, visible_channels=4)
        + foreground_morphology_mse(state, target, visible_channels=4)
        + background_alpha_mse(state, target)
        + homeostasis
    )
    assert actual.item() == pytest.approx(expected.item())


def test_home1_requires_dynamic_term() -> None:
    state = torch.zeros((1, 4, 5, 5), dtype=torch.float32)
    target = torch.zeros_like(state)
    target[:, 3, 2, 2] = 1.0
    with pytest.raises(ValueError, match="requires homeostasis_loss"):
        training_morphology_loss(result=state, target=target, config=TrainingConfig(loss_mode=MODE))


def test_rng_neutral_probe_restores_generator_state() -> None:
    torch.manual_seed(47)
    model = NeuralCellularAutomaton(NCAConfig(state_channels=8, hidden_channels=16, fire_rate=0.5, max_steps=4))
    result = make_seed_state(batch_size=1, channels=8, height=7, width=7)
    generator = torch.Generator(device="cpu").manual_seed(99)
    before = generator.get_state().clone()
    probe = _rng_neutral_homeostasis_probe(model=model, result=result, generator=generator)
    after = generator.get_state().clone()
    assert torch.equal(before, after)
    assert probe.shape == result.shape


def test_stab09_config_validates_and_freezes_home1_envelope() -> None:
    config = load_config(ROOT / "experiments/dg1a/configs/p0_stab09_home1.yaml")
    assert config["training"]["loss_mode"] == MODE
    assert config["training"]["steps_min"] == 64
    assert config["training"]["steps_max"] == 96
    assert config["training"]["damage_height_fraction"] == pytest.approx(0.5)
    assert config["training"]["damage_width_fraction"] == pytest.approx(0.5)
    assert config["recovery"]["lesion"]["height_fraction"] == pytest.approx(0.6)
    assert config["recovery"]["lesion"]["width_fraction"] == pytest.approx(0.6)


def _tiny_fixture():
    torch.manual_seed(53)
    model = NeuralCellularAutomaton(NCAConfig(state_channels=8, hidden_channels=16, fire_rate=1.0, max_steps=6))
    seed = make_seed_state(batch_size=1, channels=8, height=9, width=9)
    target = make_target(batch_size=1, channels=8, height=9, width=9, spec=TargetSpec(radius=2))
    config = TrainingConfig(
        variant="regeneration", iterations=2, learning_rate=1e-3,
        steps_min=2, steps_max=2, batch_size=2, pool_size=4,
        damage_probability=0.5, damage_min_active_cells=4,
        loss_mode=MODE, record_every=1, seed=8,
    )
    return model, seed, target, config


def test_train_records_home1_component_telemetry() -> None:
    model, seed, target, config = _tiny_fixture()
    summary = train(model=model, seed_state=seed, target=target, config=config)
    item = summary.history[-1]
    assert summary.loss_mode == MODE
    assert "foreground_morphology_mse" in item
    assert "background_alpha_mse" in item
    assert "homeostasis_background_velocity_loss" in item
    assert "homeostasis_mature_samples" in item
    assert item["homeostasis_background_velocity_loss"] >= 0.0
    assert item["homeostasis_mature_samples"] >= 0


def test_resumable_training_records_home1_component_telemetry() -> None:
    model, seed, target, config = _tiny_fixture()
    session = ResumableTrainingSession(model, seed, target, config)
    session.advance(2)
    item = session.summary().history[-1]
    assert "foreground_morphology_mse" in item
    assert "background_alpha_mse" in item
    assert "homeostasis_background_velocity_loss" in item
    assert "homeostasis_mature_samples" in item


def test_resumable_pool_never_stores_virtual_probe(monkeypatch) -> None:
    import yggdrasil.resume as resume_module
    model, seed, target, config = _tiny_fixture()
    session = ResumableTrainingSession(model, seed, target, config)

    def extreme_probe(*, model, result, generator):
        return torch.full_like(result, 999.0)

    monkeypatch.setattr(resume_module, "_rng_neutral_homeostasis_probe", extreme_probe)
    monkeypatch.setattr(resume_module, "homeostasis_mature_sample_mask", lambda result, target, **kwargs: torch.ones(result.shape[0], dtype=torch.bool, device=result.device))
    session.advance(1)
    storage = session.pool.state_dict()["storage"]
    assert float(storage.abs().max().item()) < 999.0


def test_runner_evidence_records_home1_mode_and_telemetry(tmp_path: Path) -> None:
    config = {
        "experiment_id": "DG1A-P0", "variant": "growth_only", "seed": 0, "device": "cpu", "precision": "float32",
        "model": {"state_channels": 8, "hidden_channels": 16, "fire_rate": 1.0, "alive_channel": 3, "alive_threshold": 0.1, "max_steps": 4},
        "phenotype": {"height": 7, "width": 7, "seed_location": "center"},
        "target": {"kind": "disk", "radius": 1, "rgba": [0.15, 0.75, 0.30, 1.0]},
        "training": {"iterations": 1, "learning_rate": 0.001, "steps_min": 1, "steps_max": 1, "batch_size": 1, "pool_size": 1, "damage_probability": 0.0, "damage_height_fraction": 0.5, "damage_width_fraction": 0.5, "damage_min_active_cells": 1, "gradient_clip_norm": 1.0, "hidden_state_l2_weight": 0.00001, "loss_mode": MODE},
        "resource_limits": {"max_height": 7, "max_width": 7, "max_state_channels": 8, "max_hidden_channels": 16, "max_development_steps": 4},
        "evaluation": {"growth_steps": 1, "persistence_steps": 1},
        "recovery": {"eval_steps": 1, "lesion": {"kind": "center", "height_fraction": 0.5, "width_fraction": 0.5}},
        "reporting": {"visible_channels": 4, "record_every_iterations": 1},
    }
    config_path = tmp_path / "tiny_stab09.yaml"
    evidence_path = tmp_path / "tiny_stab09.json"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    subprocess.run([sys.executable, str(ROOT / "experiments/dg1a/run_p0.py"), "--config", str(config_path), "--evidence", str(evidence_path)], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["effective_training_loss_mode"] == MODE
    assert evidence["training"]["loss_mode"] == MODE
    item = evidence["training"]["history"][-1]
    assert "homeostasis_background_velocity_loss" in item
    assert "homeostasis_mature_samples" in item
