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
    TrainingConfig,
    balanced_hard_support_allocation_terms,
    train,
    training_morphology_loss,
)

ROOT = Path(__file__).resolve().parents[1]
MODE = "global_plus_foreground_bg_alpha_attractor_t16_ceil800_alloc_balanced_hard"
STAB12_MODE = "global_plus_foreground_bg_alpha_attractor_t16_ceil800"
STAB13_MODE = "global_plus_foreground_bg_alpha_attractor_t16_ceil800_traceceil800"


def _support_fixture():
    target = torch.zeros((1, 4, 2, 2), dtype=torch.float32)
    target[:, 3, 0, 0] = 1.0
    return target


def test_balanced_alloc_zero_on_perfect_hard_support() -> None:
    target = _support_fixture()
    state = target.clone().requires_grad_(True)
    loss, fp, fn, tp = balanced_hard_support_allocation_terms(state, target)
    assert loss.item() == pytest.approx(0.0)
    assert fp.item() == pytest.approx(0.0)
    assert fn.item() == pytest.approx(0.0)
    assert tp.item() == pytest.approx(1.0)
    loss.backward()
    assert torch.count_nonzero(state.grad) == 0


def test_balanced_alloc_all_dead_is_exactly_half() -> None:
    target = _support_fixture()
    state = torch.zeros_like(target, requires_grad=True)
    loss, fp, fn, tp = balanced_hard_support_allocation_terms(state, target)
    assert loss.item() == pytest.approx(0.5)
    assert fp.item() == pytest.approx(0.0)
    assert fn.item() == pytest.approx(1.0)
    assert tp.item() == pytest.approx(0.0)


def test_balanced_alloc_all_alive_is_exactly_half() -> None:
    target = _support_fixture()
    state = torch.zeros_like(target)
    state[:, 3] = 1.0
    state.requires_grad_(True)
    loss, fp, fn, tp = balanced_hard_support_allocation_terms(state, target)
    assert loss.item() == pytest.approx(0.5)
    assert fp.item() == pytest.approx(1.0)
    assert fn.item() == pytest.approx(0.0)
    assert tp.item() == pytest.approx(1.0)


def test_balanced_alloc_exact_class_normalized_formula() -> None:
    target = torch.zeros((1, 4, 2, 3), dtype=torch.float32)
    target[:, 3, 0, :2] = 1.0
    state = torch.zeros_like(target)
    # TP at [0,0], FN at [0,1], FP at one of four background cells.
    state[:, 3, 0, 0] = 0.2
    state[:, 3, 1, 0] = 0.2
    loss, fp, fn, tp = balanced_hard_support_allocation_terms(state, target)
    assert fp.item() == pytest.approx(1 / 4)
    assert fn.item() == pytest.approx(1 / 2)
    assert tp.item() == pytest.approx(1.0)
    assert loss.item() == pytest.approx(0.5 * (1 / 4) + 0.5 * (1 / 2))


def test_balanced_alloc_gradient_only_on_hard_fp_and_fn_alpha() -> None:
    target = torch.zeros((1, 4, 2, 2), dtype=torch.float32)
    target[:, 3, 0, 0] = 1.0
    target[:, 3, 0, 1] = 1.0
    state = torch.zeros_like(target)
    state[:, 3, 0, 0] = 0.2  # correct TP
    state[:, 3, 0, 1] = 0.0  # FN
    state[:, 3, 1, 0] = 0.2  # FP
    state[:, 3, 1, 1] = 0.0  # correct TN
    state.requires_grad_(True)

    loss, _, _, _ = balanced_hard_support_allocation_terms(state, target)
    loss.backward()
    grad = state.grad[:, 3]

    assert grad[0, 0, 0].item() == pytest.approx(0.0)
    assert grad[0, 0, 1].item() < 0.0
    assert grad[0, 1, 0].item() > 0.0
    assert grad[0, 1, 1].item() == pytest.approx(0.0)
    assert torch.count_nonzero(state.grad[:, :3]) == 0


def test_stab14_full_objective_adds_allocation_to_stab12() -> None:
    state = torch.zeros((1, 4, 5, 5), dtype=torch.float32)
    target = torch.zeros_like(state)
    target[:, :, 2, 2] = 1.0
    attractor = torch.tensor(0.25)
    occupancy = torch.tensor(0.125)
    allocation = torch.tensor(0.0625)
    config = TrainingConfig(loss_mode=MODE, visible_channels=4)
    actual = training_morphology_loss(
        result=state,
        target=target,
        config=config,
        attractor_loss=attractor,
        occupancy_loss=occupancy,
        allocation_loss=allocation,
    )
    static = (
        morphology_mse(state, target, visible_channels=4)
        + foreground_morphology_mse(state, target, visible_channels=4)
        + background_alpha_mse(state, target)
    )
    assert actual.item() == pytest.approx((static + attractor + occupancy + allocation).item())


def test_stab14_requires_all_three_auxiliary_terms() -> None:
    state = torch.zeros((1, 4, 5, 5), dtype=torch.float32)
    target = torch.zeros_like(state)
    target[:, :, 2, 2] = 1.0
    config = TrainingConfig(loss_mode=MODE)
    with pytest.raises(ValueError, match="attractor_loss"):
        training_morphology_loss(result=state,target=target,config=config,occupancy_loss=torch.tensor(0.0),allocation_loss=torch.tensor(0.0))
    with pytest.raises(ValueError, match="occupancy_loss"):
        training_morphology_loss(result=state,target=target,config=config,attractor_loss=torch.tensor(0.0),allocation_loss=torch.tensor(0.0))
    with pytest.raises(ValueError, match="allocation_loss"):
        training_morphology_loss(result=state,target=target,config=config,attractor_loss=torch.tensor(0.0),occupancy_loss=torch.tensor(0.0))


def test_stab12_and_stab13_objectives_remain_compatible() -> None:
    state = torch.zeros((1, 4, 5, 5), dtype=torch.float32)
    target = torch.zeros_like(state)
    target[:, :, 2, 2] = 1.0
    a = torch.tensor(0.25)
    o = torch.tensor(0.125)
    t = torch.tensor(0.0625)
    base = training_morphology_loss(result=state,target=target,config=TrainingConfig(loss_mode=STAB12_MODE),attractor_loss=a,occupancy_loss=o)
    traced = training_morphology_loss(result=state,target=target,config=TrainingConfig(loss_mode=STAB13_MODE),attractor_loss=a,occupancy_loss=o,trace_occupancy_loss=t)
    assert traced.item() == pytest.approx(base.item() + t.item())


def test_stab14_config_is_frozen_from_stab12_envelope() -> None:
    config = load_config(ROOT / "experiments/dg1a/configs/p0_stab14_alloc_balanced_hard.yaml")
    assert config["training"]["loss_mode"] == MODE
    assert FORMATION_OCCUPANCY_CEILING == 800
    assert HOME_T16_PROBE_STEPS == 16
    assert config["training"]["iterations"] == 200
    assert config["training"]["steps_min"] == 64
    assert config["training"]["steps_max"] == 96
    assert config["training"]["batch_size"] == 8
    assert config["training"]["pool_size"] == 64
    assert config["training"]["damage_probability"] == pytest.approx(0.5)
    assert config["evaluation"]["growth_steps"] == 96
    assert config["evaluation"]["persistence_steps"] == 96
    assert config["recovery"]["eval_steps"] == 96


def _tiny_fixture():
    torch.manual_seed(83)
    model = NeuralCellularAutomaton(NCAConfig(state_channels=8, hidden_channels=16, fire_rate=1.0, max_steps=20))
    seed = make_seed_state(batch_size=1, channels=8, height=9, width=9)
    target = make_target(batch_size=1, channels=8, height=9, width=9, spec=TargetSpec(radius=2))
    config = TrainingConfig(
        variant="regeneration", iterations=2, learning_rate=1e-3,
        steps_min=2, steps_max=2, batch_size=2, pool_size=4,
        damage_probability=0.5, damage_min_active_cells=4,
        loss_mode=MODE, record_every=1, seed=13,
    )
    return model, seed, target, config


def test_train_records_stab14_support_telemetry() -> None:
    model, seed, target, config = _tiny_fixture()
    summary = train(model=model, seed_state=seed, target=target, config=config)
    item = summary.history[-1]
    assert summary.loss_mode == MODE
    assert item["attractor_probe_steps"] == 16
    assert item["formation_occupancy_ceiling"] == 800
    assert "support_allocation_loss" in item
    assert "support_false_positive_rate" in item
    assert "support_false_negative_rate" in item
    assert "support_true_positive_cells_mean" in item
    assert 0.0 <= item["support_false_positive_rate"] <= 1.0
    assert 0.0 <= item["support_false_negative_rate"] <= 1.0


def test_resumable_training_records_stab14_support_telemetry() -> None:
    model, seed, target, config = _tiny_fixture()
    session = ResumableTrainingSession(model, seed, target, config)
    session.advance(2)
    item = session.summary().history[-1]
    assert "support_allocation_loss" in item
    assert "support_false_positive_rate" in item
    assert "support_false_negative_rate" in item
    assert "support_true_positive_cells_mean" in item


def test_resumable_pool_still_excludes_virtual_trajectory(monkeypatch) -> None:
    import yggdrasil.resume as resume_module
    model, seed, target, config = _tiny_fixture()
    session = ResumableTrainingSession(model, seed, target, config)

    def extreme_trajectory(*, model, result, generator):
        return (result,) + tuple(result * 0.0 + 999.0 for _ in range(16))

    monkeypatch.setattr(resume_module, "_rng_neutral_homeostasis_trajectory", extreme_trajectory)
    monkeypatch.setattr(
        resume_module,
        "homeostasis_mature_sample_mask",
        lambda result, target, **kwargs: torch.ones(result.shape[0], dtype=torch.bool, device=result.device),
    )
    session.advance(1)
    assert float(session.pool.state_dict()["storage"].abs().max().item()) < 999.0


def test_runner_evidence_records_stab14_mode_and_support_telemetry(tmp_path: Path) -> None:
    config = {
        "experiment_id":"DG1A-P0","variant":"growth_only","seed":0,"device":"cpu","precision":"float32",
        "model":{"state_channels":8,"hidden_channels":16,"fire_rate":1.0,"alive_channel":3,"alive_threshold":0.1,"max_steps":20},
        "phenotype":{"height":7,"width":7,"seed_location":"center"},
        "target":{"kind":"disk","radius":1,"rgba":[0.15,0.75,0.30,1.0]},
        "training":{"iterations":1,"learning_rate":0.001,"steps_min":1,"steps_max":1,"batch_size":1,"pool_size":1,"damage_probability":0.0,"damage_height_fraction":0.5,"damage_width_fraction":0.5,"damage_min_active_cells":1,"gradient_clip_norm":1.0,"hidden_state_l2_weight":0.00001,"loss_mode":MODE},
        "resource_limits":{"max_height":7,"max_width":7,"max_state_channels":8,"max_hidden_channels":16,"max_development_steps":20},
        "evaluation":{"growth_steps":1,"persistence_steps":1},
        "recovery":{"eval_steps":1,"lesion":{"kind":"center","height_fraction":0.5,"width_fraction":0.5}},
        "reporting":{"visible_channels":4,"record_every_iterations":1},
    }
    config_path = tmp_path / "tiny_stab14.yaml"
    evidence_path = tmp_path / "tiny_stab14.json"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    subprocess.run(
        [sys.executable,str(ROOT/"experiments/dg1a/run_p0.py"),"--config",str(config_path),"--evidence",str(evidence_path)],
        cwd=ROOT, env=env, check=True, capture_output=True, text=True
    )
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["effective_training_loss_mode"] == MODE
    item = evidence["training"]["history"][-1]
    assert "support_allocation_loss" in item
    assert "support_false_positive_rate" in item
    assert "support_false_negative_rate" in item
    assert "support_true_positive_cells_mean" in item
