import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import torch
import yaml

from yggdrasil.config import load_config
from yggdrasil.damage import center_lesion
from yggdrasil.metrics import active_cell_count, background_alpha_mse, foreground_morphology_mse, morphology_mse
from yggdrasil.nca import NCAConfig, NeuralCellularAutomaton, make_seed_state
from yggdrasil.resume import ResumableTrainingSession
from yggdrasil.target import TargetSpec, make_target
from yggdrasil.training import (
    FORMATION_OCCUPANCY_CEILING,
    HOME_T16_PROBE_STEPS,
    TrainingConfig,
    decoupled_life_occupancy_ceiling_loss,
    decoupled_mature_sample_mask,
    formation_hard_active_counts,
    train,
    training_morphology_loss,
)

ROOT = Path(__file__).resolve().parents[1]
MODE = "global_plus_foreground_bg_alpha_attractor_t16_life4_ceil800"


def _target(channels: int = 8, size: int = 40, radius: int = 6) -> torch.Tensor:
    return make_target(
        batch_size=1,
        channels=channels,
        height=size,
        width=size,
        spec=TargetSpec(radius=radius),
    )


def test_life4_seed_initializes_hidden_life_not_visible_alpha() -> None:
    seed = make_seed_state(batch_size=1, channels=8, height=9, width=9, alive_channel=4)
    cy = cx = 4
    assert seed[0, 4, cy, cx].item() == pytest.approx(1.0)
    assert seed[0, 3, cy, cx].item() == pytest.approx(0.0)
    assert torch.count_nonzero(seed[:, 3]) == 0
    assert torch.count_nonzero(seed[:, 4]) == 1


def test_target_channel4_remains_zero() -> None:
    target = _target(channels=8, size=40)
    assert torch.count_nonzero(target[:, 4]) == 0
    assert int((target[:, 3] > 0.1).sum().item()) == 113


def test_alive_mask_uses_hidden_life_channel4() -> None:
    model = NeuralCellularAutomaton(NCAConfig(state_channels=8, hidden_channels=16, fire_rate=1.0, alive_channel=4))
    state = torch.zeros((1, 8, 5, 5), dtype=torch.float32)
    state[:, 3, 2, 2] = 1.0
    assert not bool(model.alive_mask(state).any())
    state[:, 4, 2, 2] = 1.0
    assert bool(model.alive_mask(state).any())


def test_active_cell_metric_can_diverge_from_visible_alpha() -> None:
    state = torch.zeros((1, 8, 5, 5), dtype=torch.float32)
    state[:, 3, 0, 0] = 1.0
    state[:, 4, 0, 1] = 1.0
    state[:, 4, 0, 2] = 1.0
    assert active_cell_count(state, alive_channel=3, alive_threshold=0.1) == 1
    assert active_cell_count(state, alive_channel=4, alive_threshold=0.1) == 2


def test_decoupled_maturity_counts_life4_against_visible_target_cardinality() -> None:
    target = _target(channels=8, size=40)
    state = torch.zeros_like(target)
    state[:, 4].reshape(-1)[:112] = 0.2
    assert decoupled_mature_sample_mask(state, target, state_alive_channel=4).tolist() == [False]
    state[:, 4].reshape(-1)[112] = 0.2
    assert decoupled_mature_sample_mask(state, target, state_alive_channel=4).tolist() == [True]
    state[:, 3].fill_(1.0)
    assert decoupled_mature_sample_mask(state, target, state_alive_channel=4).tolist() == [True]


def test_life4_ceiling_forward_zero_at_800_and_positive_at_801() -> None:
    target = _target(channels=8, size=40)
    state = torch.zeros_like(target)
    state[:, 4].reshape(-1)[:800] = 0.2
    state.requires_grad_(True)
    loss = decoupled_life_occupancy_ceiling_loss(state, target, state_alive_channel=4)
    assert loss.item() == pytest.approx(0.0)
    loss.backward()
    assert torch.count_nonzero(state.grad) == 0

    state2 = torch.zeros_like(target)
    state2[:, 4].reshape(-1)[:801] = 0.2
    loss2 = decoupled_life_occupancy_ceiling_loss(state2, target, state_alive_channel=4)
    assert loss2.item() == pytest.approx((1.0 / 800.0) ** 2, rel=1e-6)


def test_life4_ceiling_gradient_uses_target_alpha_mask_and_only_life_channel() -> None:
    target = _target(channels=8, size=40)
    foreground = (target[:, 3] > 0.1).reshape(-1)
    fg_index = int(torch.nonzero(foreground, as_tuple=False)[0].item())
    bg_indices = torch.nonzero(~foreground, as_tuple=False).flatten()

    state = torch.zeros_like(target)
    flat_life = state[:, 4].reshape(-1)
    flat_life[fg_index] = 0.2
    flat_life[bg_indices[:800]] = 0.2
    state.requires_grad_(True)

    loss = decoupled_life_occupancy_ceiling_loss(state, target, state_alive_channel=4)
    assert loss.item() == pytest.approx((1.0 / 800.0) ** 2, rel=1e-6)
    loss.backward()

    grad_life = state.grad[:, 4].reshape(-1)
    assert grad_life[fg_index].item() == pytest.approx(0.0)
    assert grad_life[int(bg_indices[0].item())].item() > 0.0
    inactive_bg = int(bg_indices[-1].item())
    assert grad_life[inactive_bg].item() == pytest.approx(0.0)
    assert torch.count_nonzero(state.grad[:, :4]) == 0
    assert torch.count_nonzero(state.grad[:, 5:]) == 0


def test_visible_morphology_loss_ignores_life4_directly() -> None:
    target = _target(channels=8, size=9, radius=2)
    result_a = torch.zeros_like(target)
    result_b = result_a.clone()
    result_b[:, 4].fill_(9.0)
    assert morphology_mse(result_a, target, visible_channels=4).item() == pytest.approx(
        morphology_mse(result_b, target, visible_channels=4).item()
    )
    assert foreground_morphology_mse(result_a, target, visible_channels=4).item() == pytest.approx(
        foreground_morphology_mse(result_b, target, visible_channels=4).item()
    )
    assert background_alpha_mse(result_a, target).item() == pytest.approx(
        background_alpha_mse(result_b, target).item()
    )


def test_life4_full_objective_matches_stab12_visible_formula() -> None:
    result = torch.zeros((1, 8, 9, 9), dtype=torch.float32)
    target = _target(channels=8, size=9, radius=2)
    attractor = torch.tensor(0.25)
    occupancy = torch.tensor(0.125)
    cfg = TrainingConfig(loss_mode=MODE, visible_channels=4)
    actual = training_morphology_loss(
        result=result,
        target=target,
        config=cfg,
        attractor_loss=attractor,
        occupancy_loss=occupancy,
    )
    expected = (
        morphology_mse(result, target, visible_channels=4)
        + foreground_morphology_mse(result, target, visible_channels=4)
        + background_alpha_mse(result, target)
        + attractor
        + occupancy
    )
    assert actual.item() == pytest.approx(expected.item())


def test_stab15_training_config_fails_closed_without_life4() -> None:
    model = NeuralCellularAutomaton(NCAConfig(state_channels=8, hidden_channels=16, alive_channel=3))
    with pytest.raises(ValueError, match="alive_channel 4"):
        TrainingConfig(loss_mode=MODE).validate(model)


def test_center_lesion_geometry_uses_life4_when_requested() -> None:
    state = torch.zeros((1, 8, 9, 9), dtype=torch.float32)
    state[:, 3, :, :] = 1.0
    state[:, 4, 3:6, 3:6] = 1.0
    damaged = center_lesion(
        state,
        height_fraction=1.0,
        width_fraction=1.0,
        alive_channel=4,
        alive_threshold=0.1,
    )
    assert torch.count_nonzero(damaged[:, 4]) == 0
    assert torch.count_nonzero(damaged[:, 3]) > 0


def test_stab15_config_freezes_decoupled_envelope() -> None:
    config = load_config(ROOT / "experiments/dg1a/configs/p0_stab15_life4_ceil800_attract_t16.yaml")
    assert config["model"]["alive_channel"] == 4
    assert config["model"]["alive_threshold"] == pytest.approx(0.1)
    assert config["reporting"]["visible_channels"] == 4
    assert config["training"]["loss_mode"] == MODE
    assert config["training"]["iterations"] == 200
    assert config["training"]["steps_min"] == 64
    assert config["training"]["steps_max"] == 96
    assert config["training"]["batch_size"] == 8
    assert config["training"]["pool_size"] == 64
    assert config["evaluation"]["growth_steps"] == 96
    assert config["evaluation"]["persistence_steps"] == 96
    assert config["recovery"]["eval_steps"] == 96
    assert FORMATION_OCCUPANCY_CEILING == 800
    assert HOME_T16_PROBE_STEPS == 16


def _tiny_fixture():
    torch.manual_seed(79)
    model = NeuralCellularAutomaton(
        NCAConfig(state_channels=8, hidden_channels=16, fire_rate=1.0, alive_channel=4, max_steps=20)
    )
    seed = make_seed_state(batch_size=1, channels=8, height=9, width=9, alive_channel=4)
    target = make_target(batch_size=1, channels=8, height=9, width=9, spec=TargetSpec(radius=2))
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
        seed=12,
    )
    return model, seed, target, config


def test_train_records_decoupled_life_telemetry() -> None:
    model, seed, target, config = _tiny_fixture()
    summary = train(model=model, seed_state=seed, target=target, config=config)
    item = summary.history[-1]
    assert summary.loss_mode == MODE
    assert item["life_channel"] == 4
    assert item["visible_alpha_channel"] == 3
    assert "attractor_trajectory_loss" in item
    assert "formation_occupancy_ceiling_loss" in item
    assert "formation_active_cells_mean" in item
    assert "formation_active_cells_max" in item


def test_resumable_records_decoupled_life_telemetry() -> None:
    model, seed, target, config = _tiny_fixture()
    session = ResumableTrainingSession(model, seed, target, config)
    session.advance(2)
    item = session.summary().history[-1]
    assert item["life_channel"] == 4
    assert item["visible_alpha_channel"] == 3
    assert "formation_occupancy_ceiling_loss" in item


def test_historical_stab12_mode_still_accepts_channel3_model() -> None:
    model = NeuralCellularAutomaton(NCAConfig(state_channels=8, hidden_channels=16, alive_channel=3))
    TrainingConfig(loss_mode="global_plus_foreground_bg_alpha_attractor_t16_ceil800").validate(model)


def test_runner_evidence_records_life4_mode(tmp_path: Path) -> None:
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
            "alive_channel": 4,
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
    config_path = tmp_path / "tiny_stab15.yaml"
    evidence_path = tmp_path / "tiny_stab15.json"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    subprocess.run(
        [sys.executable, str(ROOT / "experiments/dg1a/run_p0.py"), "--config", str(config_path), "--evidence", str(evidence_path)],
        cwd=ROOT, env=env, check=True, capture_output=True, text=True,
    )
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["config"]["model"]["alive_channel"] == 4
    assert evidence["effective_training_loss_mode"] == MODE
    item = evidence["training"]["history"][-1]
    assert item["life_channel"] == 4
    assert item["visible_alpha_channel"] == 3
