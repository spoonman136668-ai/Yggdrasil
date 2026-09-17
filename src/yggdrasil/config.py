from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml


def load_config(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError("experiment config must be a mapping")
    validate_config(data)
    return deepcopy(data)


def validate_config(config: dict[str, Any]) -> None:
    required = {
        "experiment_id", "variant", "seed", "device", "model", "phenotype",
        "training", "resource_limits", "target", "evaluation", "recovery", "reporting"
    }
    missing = required - set(config)
    if missing:
        raise ValueError(f"missing config sections: {sorted(missing)}")

    model = config["model"]
    phenotype = config["phenotype"]
    training = config["training"]
    limits = config["resource_limits"]
    recovery = config["recovery"]
    evaluation = config["evaluation"]
    target = config["target"]

    if config["experiment_id"] != "DG1A-P0":
        raise ValueError("experiment_id must be DG1A-P0")
    if config["variant"] not in {"growth_only", "persistence", "regeneration"}:
        raise ValueError("unsupported P0 variant")
    if model["state_channels"] > limits["max_state_channels"]:
        raise ValueError("state_channels exceeds hard limit")
    if model["hidden_channels"] > limits["max_hidden_channels"]:
        raise ValueError("hidden_channels exceeds hard limit")
    if phenotype["height"] > limits["max_height"] or phenotype["width"] > limits["max_width"]:
        raise ValueError("phenotype grid exceeds hard limit")
    if model["max_steps"] > limits["max_development_steps"]:
        raise ValueError("model max_steps exceeds hard limit")
    if training["steps_max"] > model["max_steps"]:
        raise ValueError("training steps exceed model max_steps")
    if recovery["eval_steps"] > model["max_steps"]:
        raise ValueError("recovery eval_steps exceed model max_steps")
    if evaluation["growth_steps"] > model["max_steps"]:
        raise ValueError("evaluation growth_steps exceed model max_steps")
    if evaluation["persistence_steps"] > model["max_steps"]:
        raise ValueError("evaluation persistence_steps exceed model max_steps")
    if training["steps_min"] <= 0 or training["steps_min"] > training["steps_max"]:
        raise ValueError("invalid training step range")
    if training["batch_size"] <= 0 or training["iterations"] <= 0:
        raise ValueError("training batch_size and iterations must be positive")
    if training["pool_size"] < training["batch_size"]:
        raise ValueError("pool_size must be at least batch_size")
    if training["damage_min_active_cells"] <= 0:
        raise ValueError("damage_min_active_cells must be positive")
    if target["kind"] != "disk":
        raise ValueError("P0 currently supports only repository-native disk target")
    if target["radius"] <= 0:
        raise ValueError("target radius must be positive")
