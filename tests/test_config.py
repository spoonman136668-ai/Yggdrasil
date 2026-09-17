import pytest

from yggdrasil.config import validate_config


def _base_config() -> dict:
    return {
        "experiment_id": "DG1A-P0",
        "variant": "growth_only",
        "seed": 0,
        "device": "cpu",
        "model": {
            "state_channels": 8,
            "hidden_channels": 16,
            "fire_rate": 1.0,
            "alive_channel": 3,
            "alive_threshold": 0.1,
            "max_steps": 8,
        },
        "phenotype": {"height": 15, "width": 15, "seed_location": "center"},
        "training": {
            "steps_min": 2,
            "steps_max": 3,
            "batch_size": 2,
            "iterations": 3,
            "pool_size": 4,
            "damage_min_active_cells": 4,
        },
        "resource_limits": {
            "max_height": 20,
            "max_width": 20,
            "max_state_channels": 8,
            "max_hidden_channels": 16,
            "max_development_steps": 8,
        },
        "target": {"kind": "disk", "radius": 3, "rgba": [0.1, 0.8, 0.2, 1.0]},
        "evaluation": {"growth_steps": 3, "persistence_steps": 3},
        "recovery": {
            "eval_steps": 3,
            "lesion": {"kind": "center", "height_fraction": 0.3, "width_fraction": 0.3},
        },
        "reporting": {"visible_channels": 4, "record_every_iterations": 1},
    }


def test_config_accepts_bounded_case() -> None:
    validate_config(_base_config())


def test_config_rejects_width_over_limit() -> None:
    config = _base_config()
    config["phenotype"]["width"] = 21

    with pytest.raises(ValueError, match="hard limit"):
        validate_config(config)


def test_config_rejects_evaluation_steps_over_model_limit() -> None:
    config = _base_config()
    config["evaluation"]["growth_steps"] = 9

    with pytest.raises(ValueError, match="evaluation growth_steps"):
        validate_config(config)


def test_config_rejects_persistence_steps_over_model_limit() -> None:
    config = _base_config()
    config["evaluation"]["persistence_steps"] = 9

    with pytest.raises(ValueError, match="evaluation persistence_steps"):
        validate_config(config)


def test_config_rejects_nonpositive_damage_maturity_threshold() -> None:
    config = _base_config()
    config["training"]["damage_min_active_cells"] = 0

    with pytest.raises(ValueError, match="damage_min_active_cells"):
        validate_config(config)
