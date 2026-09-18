import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import torch
import yaml

from yggdrasil.config import load_config
from yggdrasil.nca import NCAConfig, NeuralCellularAutomaton, make_seed_state
from yggdrasil.resume import ResumableTrainingSession
from yggdrasil.target import TargetSpec, make_target
from yggdrasil.training import (
    FORMATION_OCCUPANCY_CEILING,
    HOME_T16_PROBE_STEPS,
    LIFE_VIABILITY_FLOOR,
    TrainingConfig,
    decoupled_life_occupancy_ceiling_loss,
    frontier_life_floor_loss,
    hidden_life_growth_frontier,
    train,
    training_morphology_loss,
)
from yggdrasil.metrics import background_alpha_mse, foreground_morphology_mse, morphology_mse

ROOT = Path(__file__).resolve().parents[1]
MODE = "global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800"


def _target(channels: int = 8, size: int = 15, radius: int = 2) -> torch.Tensor:
    return make_target(
        batch_size=1,
        channels=channels,
        height=size,
        width=size,
        spec=TargetSpec(radius=radius),
    )


def _life_state(size: int = 15, count: int = 1) -> torch.Tensor:
    state = torch.zeros((1, 8, size, size), dtype=torch.float32)
    state[:, 4].reshape(-1)[:count] = 0.2
    return state


def test_single_center_life_cell_has_exact_eight_cell_frontier() -> None:
    state = torch.zeros((1, 8, 7, 7), dtype=torch.float32)
    state[:, 4, 3, 3] = 1.0
    frontier = hidden_life_growth_frontier(state, life_channel=4)
    assert int(frontier.sum().item()) == 8
    assert not bool(frontier[0, 0, 3, 3])
    expected = {
        (2, 2), (2, 3), (2, 4),
        (3, 2),         (3, 4),
        (4, 2), (4, 3), (4, 4),
    }
    actual = {
        (int(y), int(x))
        for y, x in torch.nonzero(frontier[0, 0], as_tuple=False).tolist()
    }
    assert actual == expected


def test_remote_dead_cell_is_not_frontier() -> None:
    state = torch.zeros((1, 8, 9, 9), dtype=torch.float32)
    state[:, 4, 4, 4] = 1.0
    frontier = hidden_life_growth_frontier(state, life_channel=4)
    assert not bool(frontier[0, 0, 0, 0])
    assert not bool(frontier[0, 0, 4, 4])


@pytest.mark.parametrize("count", [1, 112, 113])
def test_frontier_floor_exact_hard_count_forward_formula(count: int) -> None:
    state = _life_state(size=15, count=count)
    loss, _ = frontier_life_floor_loss(state, life_channel=4)
    expected = (max(113 - count, 0) / 113.0) ** 2
    assert loss.item() == pytest.approx(expected, rel=1e-6, abs=1e-8)


def test_frontier_floor_zero_and_zero_gradient_at_or_above_113() -> None:
    state = _life_state(size=15, count=113)
    state.requires_grad_(True)
    loss, _ = frontier_life_floor_loss(state, life_channel=4)
    assert loss.item() == pytest.approx(0.0)
    loss.backward()
    assert torch.count_nonzero(state.grad) == 0


def test_frontier_floor_gradient_is_negative_only_on_dead_frontier_life_cells() -> None:
    state = torch.zeros((1, 8, 7, 7), dtype=torch.float32)
    state[:, 4, 3, 3] = 1.0
    state.requires_grad_(True)
    loss, frontier_counts = frontier_life_floor_loss(state, life_channel=4)
    assert frontier_counts.tolist() == [8]
    loss.backward()

    life_grad = state.grad[0, 4]
    frontier = hidden_life_growth_frontier(state.detach(), life_channel=4)[0, 0]
    assert torch.all(life_grad[frontier] < 0.0)
    assert life_grad[3, 3].item() == pytest.approx(0.0)
    assert life_grad[0, 0].item() == pytest.approx(0.0)
    assert torch.count_nonzero(state.grad[:, :4]) == 0
    assert torch.count_nonzero(state.grad[:, 5:]) == 0


def test_frontier_floor_is_independent_of_visible_target_geometry() -> None:
    a = torch.zeros((1, 8, 7, 7), dtype=torch.float32)
    b = torch.zeros_like(a)
    a[:, 4, 3, 3] = 1.0
    b[:, 4, 3, 3] = 1.0
    a[:, 3, 1:6, 1:6] = 1.0
    b[:, 3, 0, 0] = 1.0
    a.requires_grad_(True)
    b.requires_grad_(True)

    loss_a, frontier_a = frontier_life_floor_loss(a, life_channel=4)
    loss_b, frontier_b = frontier_life_floor_loss(b, life_channel=4)
    assert loss_a.item() == pytest.approx(loss_b.item())
    assert torch.equal(frontier_a, frontier_b)

    loss_a.backward()
    loss_b.backward()
    assert torch.equal(a.grad[:, 4], b.grad[:, 4])
    assert torch.count_nonzero(a.grad[:, :4]) == 0
    assert torch.count_nonzero(b.grad[:, :4]) == 0


def test_frontier_floor_and_ceil_form_zero_band_inside_113_to_800() -> None:
    target = _target(size=40, radius=6)
    state = torch.zeros_like(target)
    state[:, 4].reshape(-1)[:200] = 0.2
    floor, _ = frontier_life_floor_loss(state, life_channel=4)
    ceil = decoupled_life_occupancy_ceiling_loss(
        state, target, state_alive_channel=4, target_alpha_channel=3
    )
    assert floor.item() == pytest.approx(0.0)
    assert ceil.item() == pytest.approx(0.0)


def test_stab16_full_objective_adds_exact_floor_to_stab15_formula() -> None:
    result = torch.zeros((1, 8, 9, 9), dtype=torch.float32)
    target = make_target(
        batch_size=1, channels=8, height=9, width=9, spec=TargetSpec(radius=2)
    )
    attractor = torch.tensor(0.25)
    occupancy = torch.tensor(0.125)
    floor = torch.tensor(0.375)
    cfg = TrainingConfig(loss_mode=MODE, visible_channels=4)
    actual = training_morphology_loss(
        result=result,
        target=target,
        config=cfg,
        attractor_loss=attractor,
        occupancy_loss=occupancy,
        frontier_floor_loss=floor,
    )
    expected = (
        morphology_mse(result, target, visible_channels=4)
        + foreground_morphology_mse(result, target, visible_channels=4)
        + background_alpha_mse(result, target)
        + attractor
        + occupancy
        + floor
    )
    assert actual.item() == pytest.approx(expected.item())


def test_stab16_config_fails_closed_without_life4() -> None:
    model = NeuralCellularAutomaton(
        NCAConfig(state_channels=8, hidden_channels=16, alive_channel=3)
    )
    with pytest.raises(ValueError, match="STAB-16 requires model alive_channel 4"):
        TrainingConfig(loss_mode=MODE).validate(model)


def test_stab16_frozen_config() -> None:
    config = load_config(ROOT / "experiments/dg1a/configs/p0_stab16_life4_band113_800.yaml")
    assert config["model"]["alive_channel"] == 4
    assert config["model"]["alive_threshold"] == pytest.approx(0.1)
    assert config["reporting"]["visible_channels"] == 4
    assert config["training"]["loss_mode"] == MODE
    assert config["training"]["iterations"] == 200
    assert config["training"]["steps_min"] == 64
    assert config["training"]["steps_max"] == 96
    assert config["training"]["batch_size"] == 8
    assert config["training"]["pool_size"] == 64
    assert config["training"]["hidden_state_l2_weight"] == pytest.approx(0.00001)
    assert config["evaluation"]["growth_steps"] == 96
    assert config["evaluation"]["persistence_steps"] == 96
    assert config["recovery"]["eval_steps"] == 96
    assert LIFE_VIABILITY_FLOOR == 113
    assert FORMATION_OCCUPANCY_CEILING == 800
    assert HOME_T16_PROBE_STEPS == 16


def _tiny_fixture():
    torch.manual_seed(97)
    model = NeuralCellularAutomaton(
        NCAConfig(
            state_channels=8,
            hidden_channels=16,
            fire_rate=1.0,
            alive_channel=4,
            max_steps=20,
        )
    )
    seed = make_seed_state(
        batch_size=1, channels=8, height=9, width=9, alive_channel=4
    )
    target = make_target(
        batch_size=1, channels=8, height=9, width=9, spec=TargetSpec(radius=2)
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
        seed=13,
    )
    return model, seed, target, config


def test_train_records_frontier_floor_telemetry() -> None:
    model, seed, target, config = _tiny_fixture()
    summary = train(model=model, seed_state=seed, target=target, config=config)
    item = summary.history[-1]
    assert summary.loss_mode == MODE
    assert item["life_channel"] == 4
    assert item["visible_alpha_channel"] == 3
    assert item["life_viability_floor"] == 113
    assert "frontier_floor_loss" in item
    assert "frontier_cells_mean" in item
    assert "formation_occupancy_ceiling_loss" in item
    assert "attractor_trajectory_loss" in item


def test_resumable_records_frontier_floor_telemetry() -> None:
    model, seed, target, config = _tiny_fixture()
    session = ResumableTrainingSession(model, seed, target, config)
    session.advance(2)
    item = session.summary().history[-1]
    assert item["life_channel"] == 4
    assert item["life_viability_floor"] == 113
    assert "frontier_floor_loss" in item
    assert "frontier_cells_mean" in item


def test_resumable_pool_never_stores_stab16_virtual_trajectory(monkeypatch) -> None:
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
        "decoupled_mature_sample_mask",
        lambda result, target, **kwargs: torch.ones(
            result.shape[0], dtype=torch.bool, device=result.device
        ),
    )
    session.advance(1)
    storage = session.pool.state_dict()["storage"]
    assert float(storage.abs().max().item()) < 999.0


def test_stab15_mode_remains_compatible() -> None:
    model = NeuralCellularAutomaton(
        NCAConfig(state_channels=8, hidden_channels=16, alive_channel=4)
    )
    TrainingConfig(
        loss_mode="global_plus_foreground_bg_alpha_attractor_t16_life4_ceil800"
    ).validate(model)


def test_runner_evidence_records_stab16_mode_and_telemetry(tmp_path: Path) -> None:
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
    config_path = tmp_path / "tiny_stab16.yaml"
    evidence_path = tmp_path / "tiny_stab16.json"
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
    assert evidence["config"]["model"]["alive_channel"] == 4
    assert evidence["effective_training_loss_mode"] == MODE
    item = evidence["training"]["history"][-1]
    assert item["life_channel"] == 4
    assert item["life_viability_floor"] == 113
    assert "frontier_floor_loss" in item
    assert "frontier_cells_mean" in item
