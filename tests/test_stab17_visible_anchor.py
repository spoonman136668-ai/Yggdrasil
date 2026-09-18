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
    FORMATION_OCCUPANCY_CEILING,
    HOME_T16_PROBE_STEPS,
    LIFE_VIABILITY_FLOOR,
    TrainingConfig,
    current_visible_r1_neighborhood,
    mature_visible_anchor_terms,
    train,
    training_morphology_loss,
)

ROOT = Path(__file__).resolve().parents[1]
MODE = "global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800_visanchor_r1"


def _state(size: int = 20, channels: int = 8) -> torch.Tensor:
    return torch.zeros((1, channels, size, size), dtype=torch.float32)


def _mature_state(size: int = 20, channels: int = 8, count: int = 113) -> torch.Tensor:
    state = _state(size, channels)
    state[:, 4].reshape(-1)[:count] = 0.2
    return state


def test_visible_r1_neighborhood_exact_geometry() -> None:
    state = _state(size=7)
    state[:, 3, 3, 3] = 0.2
    mask = current_visible_r1_neighborhood(state)
    assert int(mask.sum().item()) == 9
    expected = {(y, x) for y in (2, 3, 4) for x in (2, 3, 4)}
    actual = {(int(y), int(x)) for y, x in torch.nonzero(mask[0, 0], as_tuple=False).tolist()}
    assert actual == expected


def test_same_cell_visible_alpha_anchors_life() -> None:
    state = _mature_state()
    # Make each mature life cell visible at the same location.
    state[:, 3].reshape(-1)[:113] = 0.2
    loss, mature, fractions, counts = mature_visible_anchor_terms(state)
    assert mature.tolist() == [True]
    assert loss.item() == pytest.approx(0.0)
    assert fractions.tolist() == pytest.approx([0.0])
    assert counts.tolist() == pytest.approx([0.0])


def test_diagonal_visible_alpha_anchors_life() -> None:
    state = _state(size=12)
    # 113 live cells; test one isolated life cell at (5,5) with diagonal visible alpha.
    state[:, 4].reshape(-1)[:113] = 0.2
    state[:, 3, 4, 4] = 0.2
    neighborhood = current_visible_r1_neighborhood(state)
    assert bool(neighborhood[0, 0, 5, 5])


def test_distance_two_visible_alpha_does_not_anchor_life() -> None:
    state = _state(size=12)
    state[:, 4, 5, 5] = 0.2
    state[:, 3, 3, 3] = 0.2
    neighborhood = current_visible_r1_neighborhood(state)
    assert not bool(neighborhood[0, 0, 5, 5])


def test_immature_sample_returns_differentiable_zero() -> None:
    state = _state(size=20)
    state[:, 4].reshape(-1)[:112] = 0.2
    state.requires_grad_(True)
    loss, mature, fractions, counts = mature_visible_anchor_terms(state)
    assert mature.tolist() == [False]
    assert loss.item() == pytest.approx(0.0)
    loss.backward()
    assert torch.count_nonzero(state.grad) == 0


def test_exact_mature_unanchored_fraction_forward_formula() -> None:
    state = _mature_state()
    # Anchor exactly 13 of the 113 life cells using same-cell visible alpha.
    state[:, 3].reshape(-1)[:13] = 0.2
    # The R1 neighborhoods may anchor additional adjacent life cells because life is contiguous.
    visible_neighborhood = current_visible_r1_neighborhood(state)
    hard_alive = state[:, 4:5] > 0.1
    expected_unanchored = int((hard_alive & ~visible_neighborhood).sum().item())
    expected_fraction = expected_unanchored / 113.0
    loss, mature, fractions, counts = mature_visible_anchor_terms(state)
    assert mature.tolist() == [True]
    assert counts.item() == pytest.approx(expected_unanchored)
    assert fractions.item() == pytest.approx(expected_fraction)
    assert loss.item() == pytest.approx(expected_fraction)


def test_anchor_gradient_only_on_hard_alive_unanchored_life() -> None:
    state = _mature_state(size=20)
    # Anchor first local cluster with visible alpha; leave remote mature life unanchored.
    state[:, 3, 0:3, 0:3] = 0.2
    state.requires_grad_(True)
    loss, mature, _, _ = mature_visible_anchor_terms(state)
    assert mature.tolist() == [True]
    loss.backward()
    hard_alive = state.detach()[:, 4:5] > 0.1
    visible_neighborhood = current_visible_r1_neighborhood(state.detach())
    unanchored = hard_alive & ~visible_neighborhood
    anchored = hard_alive & visible_neighborhood
    life_grad = state.grad[:, 4:5]
    assert torch.all(life_grad[unanchored] > 0.0)
    assert torch.all(life_grad[anchored] == 0.0)
    assert torch.all(life_grad[~hard_alive] == 0.0)
    assert torch.count_nonzero(state.grad[:, :4]) == 0
    assert torch.count_nonzero(state.grad[:, 5:]) == 0


def test_target_geometry_cannot_change_anchor_value_or_gradient() -> None:
    a = _mature_state(size=20)
    b = a.clone()
    a[:, 3, 5, 5] = 0.2
    b[:, 3, 5, 5] = 0.2
    # Target tensors are intentionally different but never passed to the anchor helper.
    target_a = torch.zeros_like(a)
    target_b = torch.ones_like(b)
    assert not torch.equal(target_a, target_b)
    a.requires_grad_(True)
    b.requires_grad_(True)
    loss_a, _, _, _ = mature_visible_anchor_terms(a)
    loss_b, _, _, _ = mature_visible_anchor_terms(b)
    assert loss_a.item() == pytest.approx(loss_b.item())
    loss_a.backward(); loss_b.backward()
    assert torch.equal(a.grad, b.grad)


def test_stab17_full_objective_formula() -> None:
    result = torch.zeros((1, 8, 9, 9), dtype=torch.float32)
    target = make_target(batch_size=1, channels=8, height=9, width=9, spec=TargetSpec(radius=2))
    cfg = TrainingConfig(loss_mode=MODE, visible_channels=4)
    attractor = torch.tensor(0.25)
    occupancy = torch.tensor(0.125)
    floor = torch.tensor(0.375)
    anchor = torch.tensor(0.5)
    actual = training_morphology_loss(
        result=result,
        target=target,
        config=cfg,
        attractor_loss=attractor,
        occupancy_loss=occupancy,
        frontier_floor_loss=floor,
        visible_anchor_loss=anchor,
    )
    expected = (
        morphology_mse(result, target, visible_channels=4)
        + foreground_morphology_mse(result, target, visible_channels=4)
        + background_alpha_mse(result, target)
        + attractor + occupancy + floor + anchor
    )
    assert actual.item() == pytest.approx(expected.item())


def test_stab17_requires_anchor_auxiliary() -> None:
    result = torch.zeros((1, 8, 9, 9), dtype=torch.float32)
    target = make_target(batch_size=1, channels=8, height=9, width=9, spec=TargetSpec(radius=2))
    cfg = TrainingConfig(loss_mode=MODE, visible_channels=4)
    with pytest.raises(ValueError, match="visible_anchor_loss"):
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


def test_train_records_visible_anchor_telemetry() -> None:
    model, seed, target, config = _tiny_fixture()
    summary = train(model=model, seed_state=seed, target=target, config=config)
    item = summary.history[-1]
    assert summary.loss_mode == MODE
    assert "mature_visible_anchor_loss" in item
    assert "anchor_mature_samples" in item
    assert "unanchored_life_fraction_mean" in item
    assert "unanchored_life_cells_mean" in item
    assert item["life_channel"] == 4
    assert item["visible_alpha_channel"] == 3


def test_resumable_records_visible_anchor_telemetry() -> None:
    model, seed, target, config = _tiny_fixture()
    session = ResumableTrainingSession(model, seed, target, config)
    session.advance(2)
    item = session.summary().history[-1]
    assert "mature_visible_anchor_loss" in item
    assert "anchor_mature_samples" in item
    assert "unanchored_life_fraction_mean" in item
    assert item["life_channel"] == 4


def test_stab16_mode_remains_compatible() -> None:
    model = NeuralCellularAutomaton(NCAConfig(state_channels=8, hidden_channels=16, alive_channel=4))
    TrainingConfig(loss_mode="global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800").validate(model)


def test_stab17_frozen_config() -> None:
    config = load_config(ROOT / "experiments/dg1a/configs/p0_stab17_life4_band113_800_visanchor_r1.yaml")
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
    assert LIFE_VIABILITY_FLOOR == 113
    assert FORMATION_OCCUPANCY_CEILING == 800
    assert HOME_T16_PROBE_STEPS == 16


def test_stab17_config_fails_closed_without_life4() -> None:
    model = NeuralCellularAutomaton(NCAConfig(state_channels=8, hidden_channels=16, alive_channel=3))
    with pytest.raises(ValueError, match="STAB-17 requires model alive_channel 4"):
        TrainingConfig(loss_mode=MODE).validate(model)


def test_resumable_pool_never_stores_stab17_virtual_trajectory(monkeypatch) -> None:
    import yggdrasil.resume as resume_module
    model, seed, target, config = _tiny_fixture()
    session = ResumableTrainingSession(model, seed, target, config)

    def extreme_trajectory(*, model, result, generator):
        return (result,) + tuple(result * 0.0 + 999.0 for _ in range(16))

    monkeypatch.setattr(resume_module, "_rng_neutral_homeostasis_trajectory", extreme_trajectory)
    monkeypatch.setattr(
        resume_module,
        "decoupled_mature_sample_mask",
        lambda result, target, **kwargs: torch.ones(result.shape[0], dtype=torch.bool, device=result.device),
    )
    session.advance(1)
    storage = session.pool.state_dict()["storage"]
    assert float(storage.abs().max().item()) < 999.0


def test_runner_evidence_records_stab17_mode_and_telemetry(tmp_path: Path) -> None:
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
    config_path = tmp_path / "tiny_stab17.yaml"
    evidence_path = tmp_path / "tiny_stab17.json"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    env = dict(os.environ); env["PYTHONPATH"] = str(ROOT / "src")
    subprocess.run(
        [sys.executable, str(ROOT / "experiments/dg1a/run_p0.py"), "--config", str(config_path), "--evidence", str(evidence_path)],
        cwd=ROOT, env=env, check=True, capture_output=True, text=True,
    )
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["effective_training_loss_mode"] == MODE
    item = evidence["training"]["history"][-1]
    assert "mature_visible_anchor_loss" in item
    assert "unanchored_life_fraction_mean" in item
    assert item["life_channel"] == 4
