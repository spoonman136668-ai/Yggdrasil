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
    far_field_background_alpha_mse,
    foreground_morphology_mse,
    morphology_mse,
)
from yggdrasil.nca import NCAConfig, NeuralCellularAutomaton, make_seed_state
from yggdrasil.resume import ResumableTrainingSession
from yggdrasil.target import TargetSpec, make_target
from yggdrasil.training import TrainingConfig, train, training_morphology_loss

ROOT = Path(__file__).resolve().parents[1]
MODE = "global_plus_foreground_farfield_bg_alpha"


def test_far_field_loss_exempts_foreground_and_one_cell_halo() -> None:
    state = torch.zeros((1, 4, 5, 5), dtype=torch.float32)
    target = torch.zeros_like(state)
    target[:, 3, 2, 2] = 1.0
    state[:, 3, 2, 2] = 9.0
    state[:, 3, 2, 3] = 8.0
    state[:, 3, 0, 0] = 3.0
    value = far_field_background_alpha_mse(state, target, support_radius=1)
    assert value.item() == pytest.approx(9.0 / 16.0)


def test_radius6_target_support_geometry_is_frozen() -> None:
    target = make_target(batch_size=1, channels=16, height=40, width=40, spec=TargetSpec(radius=6))
    foreground = target[:, 3:4] > 0.1
    support = torch.nn.functional.max_pool2d(foreground.float(), kernel_size=3, stride=1, padding=1) > 0
    assert int(foreground.sum().item()) == 113
    assert int(support.sum().item()) == 169
    assert int((support & ~foreground).sum().item()) == 56
    assert int((~support).sum().item()) == 1431


def test_far_field_loss_rejects_missing_foreground() -> None:
    state = torch.zeros((1, 4, 3, 3), dtype=torch.float32)
    target = torch.zeros_like(state)
    with pytest.raises(ValueError, match="no foreground"):
        far_field_background_alpha_mse(state, target)


def test_far_field_loss_rejects_missing_far_field() -> None:
    state = torch.zeros((1, 4, 3, 3), dtype=torch.float32)
    target = torch.zeros_like(state)
    target[:, 3, 1, 1] = 1.0
    with pytest.raises(ValueError, match="no far-field"):
        far_field_background_alpha_mse(state, target, support_radius=1)


def test_halo1_exact_formula_is_finite() -> None:
    state = torch.zeros((1, 4, 5, 5), dtype=torch.float32)
    target = torch.zeros_like(state)
    target[:, :, 2, 2] = 1.0
    state[:, 3, 0, 0] = 0.5
    config = TrainingConfig(loss_mode=MODE, visible_channels=4)
    actual = training_morphology_loss(result=state, target=target, config=config)
    expected = (
        morphology_mse(state, target, visible_channels=4)
        + foreground_morphology_mse(state, target, visible_channels=4)
        + far_field_background_alpha_mse(state, target, support_radius=1)
    )
    assert actual.item() == pytest.approx(expected.item())
    assert torch.isfinite(actual)


def test_halo1_dead_state_sanity_matches_preregistration() -> None:
    target = make_target(batch_size=1, channels=16, height=40, width=40, spec=TargetSpec(radius=6))
    state = torch.zeros_like(target)
    config = TrainingConfig(loss_mode=MODE, visible_channels=4)
    value = training_morphology_loss(result=state, target=target, config=config)
    assert value.item() == pytest.approx(0.44832421875, rel=1e-6)


def test_stab07_config_validates_and_freezes_halo1_envelope() -> None:
    config = load_config(ROOT / "experiments/dg1a/configs/p0_stab07_halo1.yaml")
    assert config["training"]["loss_mode"] == MODE
    assert config["training"]["steps_min"] == 64
    assert config["training"]["steps_max"] == 96
    assert config["training"]["damage_height_fraction"] == pytest.approx(0.5)
    assert config["training"]["damage_width_fraction"] == pytest.approx(0.5)
    assert config["recovery"]["lesion"]["height_fraction"] == pytest.approx(0.6)
    assert config["recovery"]["lesion"]["width_fraction"] == pytest.approx(0.6)


def _tiny_fixture():
    torch.manual_seed(41)
    model = NeuralCellularAutomaton(NCAConfig(state_channels=8, hidden_channels=16, fire_rate=1.0, max_steps=6))
    seed = make_seed_state(batch_size=1, channels=8, height=9, width=9)
    target = make_target(batch_size=1, channels=8, height=9, width=9, spec=TargetSpec(radius=2))
    config = TrainingConfig(variant="regeneration", iterations=2, learning_rate=1e-3, steps_min=2, steps_max=2, batch_size=2, pool_size=4, damage_probability=0.5, damage_min_active_cells=4, loss_mode=MODE, record_every=1, seed=6)
    return model, seed, target, config


def test_train_records_halo1_component_telemetry() -> None:
    model, seed, target, config = _tiny_fixture()
    summary = train(model=model, seed_state=seed, target=target, config=config)
    assert summary.loss_mode == MODE
    assert "foreground_morphology_mse" in summary.history[-1]
    assert "far_field_background_alpha_mse" in summary.history[-1]
    assert summary.history[-1]["far_field_background_alpha_mse"] >= 0.0


def test_resumable_training_records_halo1_component_telemetry() -> None:
    model, seed, target, config = _tiny_fixture()
    session = ResumableTrainingSession(model, seed, target, config)
    session.advance(2)
    summary = session.summary()
    assert summary.loss_mode == MODE
    assert "foreground_morphology_mse" in summary.history[-1]
    assert "far_field_background_alpha_mse" in summary.history[-1]


def test_runner_evidence_records_halo1_mode_and_telemetry(tmp_path: Path) -> None:
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
    config_path = tmp_path / "tiny_stab07.yaml"
    evidence_path = tmp_path / "tiny_stab07.json"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    subprocess.run([sys.executable, str(ROOT / "experiments/dg1a/run_p0.py"), "--config", str(config_path), "--evidence", str(evidence_path)], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["effective_training_loss_mode"] == MODE
    assert evidence["training"]["loss_mode"] == MODE
    assert "far_field_background_alpha_mse" in evidence["training"]["history"][-1]
