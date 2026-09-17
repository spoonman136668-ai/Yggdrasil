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
    balanced_morphology_mse,
    foreground_morphology_mse,
    morphology_mse,
)
from yggdrasil.training import TrainingConfig, training_morphology_loss


ROOT = Path(__file__).resolve().parents[1]


def test_global_plus_foreground_exact_formula() -> None:
    state = torch.zeros((1, 4, 2, 2), dtype=torch.float32)
    target = torch.zeros_like(state)
    target[:, :, 0, 0] = 1.0
    config = TrainingConfig(loss_mode="global_plus_foreground", visible_channels=4)

    value = training_morphology_loss(result=state, target=target, config=config)
    global_value = morphology_mse(state, target, visible_channels=4)
    foreground_value = foreground_morphology_mse(
        state,
        target,
        visible_channels=4,
        alpha_channel=3,
        foreground_threshold=0.1,
    )

    assert value.item() == pytest.approx(
        global_value.item() + foreground_value.item()
    )
    assert value.item() == pytest.approx(1.25)
    assert torch.isfinite(value)


def test_foreground_mask_is_target_alpha_strictly_above_point_one() -> None:
    state = torch.zeros((1, 4, 2, 2), dtype=torch.float32)
    target = torch.zeros_like(state)
    target[:, 3, 0, 0] = 0.1

    with pytest.raises(ValueError, match="no foreground"):
        foreground_morphology_mse(state, target, visible_channels=4)

    target[:, 3, 0, 0] = 0.1001
    value = foreground_morphology_mse(state, target, visible_channels=4)
    assert torch.isfinite(value)


def test_global_plus_foreground_rejects_empty_target_foreground() -> None:
    state = torch.zeros((1, 4, 2, 2), dtype=torch.float32)
    target = torch.zeros_like(state)
    config = TrainingConfig(loss_mode="global_plus_foreground", visible_channels=4)

    with pytest.raises(ValueError, match="no foreground"):
        training_morphology_loss(result=state, target=target, config=config)


def test_historical_global_mse_mode_is_unchanged() -> None:
    state = torch.zeros((1, 4, 2, 2), dtype=torch.float32)
    target = torch.ones_like(state)
    config = TrainingConfig(loss_mode="global_mse", visible_channels=4)

    actual = training_morphology_loss(result=state, target=target, config=config)
    expected = morphology_mse(state, target, visible_channels=4)

    assert actual.item() == pytest.approx(expected.item())


def test_historical_balanced_mode_is_unchanged() -> None:
    state = torch.zeros((1, 4, 2, 2), dtype=torch.float32)
    target = torch.zeros_like(state)
    target[:, :, 0, 0] = 1.0
    config = TrainingConfig(loss_mode="balanced_fg_bg", visible_channels=4)

    actual = training_morphology_loss(result=state, target=target, config=config)
    expected = balanced_morphology_mse(
        state,
        target,
        visible_channels=4,
        alpha_channel=3,
        foreground_threshold=0.1,
        foreground_weight=0.5,
    )

    assert actual.item() == pytest.approx(expected.item())


def test_stab04_config_validates_and_selects_new_mode() -> None:
    config = load_config(ROOT / "experiments/dg1a/configs/p0_stab04_fg1.yaml")

    assert config["training"]["loss_mode"] == "global_plus_foreground"
    assert config["training"]["steps_min"] == 64
    assert config["training"]["steps_max"] == 96
    assert config["training"]["damage_height_fraction"] == pytest.approx(0.5)
    assert config["recovery"]["lesion"]["height_fraction"] == pytest.approx(0.6)


def test_runner_evidence_records_effective_global_plus_foreground_mode(tmp_path: Path) -> None:
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
            "max_steps": 4,
        },
        "phenotype": {"height": 7, "width": 7, "seed_location": "center"},
        "target": {
            "kind": "disk",
            "radius": 1,
            "rgba": [0.15, 0.75, 0.30, 1.0],
        },
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
            "loss_mode": "global_plus_foreground",
        },
        "resource_limits": {
            "max_height": 7,
            "max_width": 7,
            "max_state_channels": 8,
            "max_hidden_channels": 16,
            "max_development_steps": 4,
        },
        "evaluation": {"growth_steps": 1, "persistence_steps": 1},
        "recovery": {
            "eval_steps": 1,
            "lesion": {
                "kind": "center",
                "height_fraction": 0.5,
                "width_fraction": 0.5,
            },
        },
        "reporting": {"visible_channels": 4, "record_every_iterations": 1},
    }
    config_path = tmp_path / "tiny_stab04.yaml"
    evidence_path = tmp_path / "tiny_stab04.json"
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
    assert evidence["effective_training_loss_mode"] == "global_plus_foreground"
    assert evidence["training"]["loss_mode"] == "global_plus_foreground"
