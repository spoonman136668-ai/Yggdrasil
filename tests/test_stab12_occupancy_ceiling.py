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
    active_cell_count,
    background_alpha_mse,
    foreground_morphology_mse,
    morphology_mse,
)
from yggdrasil.nca import NCAConfig, NeuralCellularAutomaton, make_seed_state
from yggdrasil.resume import ResumableTrainingSession
from yggdrasil.target import TargetSpec, make_target
from yggdrasil.training import (
    FORMATION_OCCUPANCY_CEILING,
    HOME_T16_PROBE_STEPS,
    TrainingConfig,
    attractor_trajectory_loss,
    formation_hard_active_counts,
    formation_occupancy_ceiling_loss,
    train,
    training_morphology_loss,
)

ROOT = Path(__file__).resolve().parents[1]
MODE = "global_plus_foreground_bg_alpha_attractor_t16_ceil800"


def _canonical_state_target(active: int, *, foreground_index: int | None = None):
    state = torch.zeros((1, 4, 40, 40), dtype=torch.float32)
    target = torch.zeros_like(state)
    flat_alpha = state[:, 3].reshape(-1)
    flat_alpha[:active] = 0.2
    if foreground_index is not None:
        target[:, 3].reshape(-1)[foreground_index] = 1.0
    return state, target


def _static_loss(state: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    return (
        morphology_mse(state, target, visible_channels=4)
        + foreground_morphology_mse(state, target, visible_channels=4)
        + background_alpha_mse(state, target)
    )


def test_stab12_ceiling_constant_is_frozen() -> None:
    assert FORMATION_OCCUPANCY_CEILING == 800


def test_formation_hard_active_count_matches_evaluation_semantics() -> None:
    state = torch.zeros((1, 4, 3, 3), dtype=torch.float32)
    state[:, 3, 0, 0] = 0.1
    state[:, 3, 0, 1] = 0.1001
    state[:, 3, 0, 2] = 1.0
    counts = formation_hard_active_counts(state)
    assert counts.tolist() == [2.0]
    assert int(counts.item()) == active_cell_count(state, alive_channel=3, alive_threshold=0.1)


def test_formation_ceiling_loss_is_exact_zero_at_800() -> None:
    state, target = _canonical_state_target(800)
    state.requires_grad_(True)
    loss = formation_occupancy_ceiling_loss(state, target)
    assert loss.item() == pytest.approx(0.0)
    loss.backward()
    assert state.grad is not None
    assert torch.count_nonzero(state.grad) == 0


def test_formation_ceiling_loss_exact_formula_above_800() -> None:
    state, target = _canonical_state_target(801)
    loss = formation_occupancy_ceiling_loss(state, target)
    expected = (1.0 / 800.0) ** 2
    assert loss.item() == pytest.approx(expected, rel=1e-6)


def test_formation_ceiling_gradient_is_restricted_to_active_target_background() -> None:
    state, target = _canonical_state_target(801, foreground_index=0)
    state.requires_grad_(True)
    loss = formation_occupancy_ceiling_loss(state, target)
    loss.backward()
    grad = state.grad[:, 3].reshape(-1)

    assert grad[0].item() == pytest.approx(0.0)
    assert grad[1].item() > 0.0
    assert grad[900].item() == pytest.approx(0.0)
    assert torch.count_nonzero(state.grad[:, :3]) == 0


def test_stab12_full_objective_is_static_plus_attractor_plus_ceiling() -> None:
    state = torch.zeros((1, 4, 5, 5), dtype=torch.float32)
    target = torch.zeros_like(state)
    target[:, :, 2, 2] = 1.0
    attractor = torch.tensor(0.25)
    occupancy = torch.tensor(0.125)
    config = TrainingConfig(loss_mode=MODE, visible_channels=4)
    actual = training_morphology_loss(
        result=state,
        target=target,
        config=config,
        attractor_loss=attractor,
        occupancy_loss=occupancy,
    )
    expected = _static_loss(state, target) + attractor + occupancy
    assert actual.item() == pytest.approx(expected.item())


def test_stab12_requires_both_auxiliary_terms() -> None:
    target = torch.zeros((1, 4, 5, 5), dtype=torch.float32)
    target[:, :, 2, 2] = 1.0
    state = torch.zeros_like(target)
    config = TrainingConfig(loss_mode=MODE)
    with pytest.raises(ValueError, match="attractor_loss"):
        training_morphology_loss(
            result=state,
            target=target,
            config=config,
            occupancy_loss=torch.tensor(0.0),
        )
    with pytest.raises(ValueError, match="occupancy_loss"):
        training_morphology_loss(
            result=state,
            target=target,
            config=config,
            attractor_loss=torch.tensor(0.0),
        )


def test_attract16_semantics_remain_exactly_16_future_states() -> None:
    target = torch.zeros((1, 4, 3, 3), dtype=torch.float32)
    target[:, :, 1, 1] = 1.0
    states = tuple(target.clone() for _ in range(16))
    assert HOME_T16_PROBE_STEPS == 16
    assert attractor_trajectory_loss(states, target).item() == pytest.approx(0.0)
    with pytest.raises(ValueError, match="exactly 16 future states"):
        attractor_trajectory_loss(states[:-1], target)


def test_stab12_config_validates_and_freezes_envelope() -> None:
    config = load_config(ROOT / "experiments/dg1a/configs/p0_stab12_ceil800_attract_t16.yaml")
    assert config["training"]["loss_mode"] == MODE
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
    torch.manual_seed(71)
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
        seed=11,
    )
    return model, seed, target, config


def test_train_records_stab12_component_telemetry() -> None:
    model, seed, target, config = _tiny_fixture()
    summary = train(model=model, seed_state=seed, target=target, config=config)
    item = summary.history[-1]
    assert summary.loss_mode == MODE
    assert "attractor_trajectory_loss" in item
    assert "attractor_mature_samples" in item
    assert item["attractor_probe_steps"] == 16
    assert "formation_occupancy_ceiling_loss" in item
    assert "formation_active_cells_mean" in item
    assert "formation_active_cells_max" in item
    assert item["formation_occupancy_ceiling"] == 800
    assert item["formation_occupancy_ceiling_loss"] == pytest.approx(0.0)


def test_resumable_training_records_stab12_component_telemetry() -> None:
    model, seed, target, config = _tiny_fixture()
    session = ResumableTrainingSession(model, seed, target, config)
    session.advance(2)
    item = session.summary().history[-1]
    assert "attractor_trajectory_loss" in item
    assert "formation_occupancy_ceiling_loss" in item
    assert "formation_active_cells_mean" in item
    assert "formation_active_cells_max" in item
    assert item["formation_occupancy_ceiling"] == 800


def test_resumable_pool_still_excludes_virtual_trajectory(monkeypatch) -> None:
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


def test_runner_evidence_records_stab12_mode_and_telemetry(tmp_path: Path) -> None:
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
    config_path = tmp_path / "tiny_stab12.yaml"
    evidence_path = tmp_path / "tiny_stab12.json"
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
    assert "formation_occupancy_ceiling_loss" in item
    assert "formation_active_cells_mean" in item
    assert "formation_active_cells_max" in item
    assert item["formation_occupancy_ceiling"] == 800
