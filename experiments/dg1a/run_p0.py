from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

import torch

from yggdrasil.config import load_config
from yggdrasil.evidence import environment_fingerprint, file_sha256, write_evidence
from yggdrasil.nca import NCAConfig, NeuralCellularAutomaton, make_seed_state
from yggdrasil.target import TargetSpec, make_target, target_identity
from yggdrasil.training import (
    TrainingConfig,
    evaluate_growth_and_recovery,
    evaluate_persistence,
    train,
)


def _git_revision() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run bounded Yggdrasil DG-1A-P0 experiment")
    parser.add_argument("--config", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--checkpoint")
    parser.add_argument("--seed", type=int, help="Override the config seed while preserving config identity")
    args = parser.parse_args()

    config_path = Path(args.config)
    raw = load_config(config_path)
    configured_seed = int(raw["seed"])
    effective_seed = configured_seed if args.seed is None else int(args.seed)
    raw["seed"] = effective_seed

    torch.manual_seed(effective_seed)
    device = torch.device(raw["device"])
    dtype = torch.float32
    if raw.get("precision", "float32") != "float32":
        raise ValueError("P0 runner currently supports float32 only")

    nca_config = NCAConfig(**raw["model"])
    model = NeuralCellularAutomaton(nca_config).to(device=device, dtype=dtype)

    phenotype = raw["phenotype"]
    seed_state = make_seed_state(
        batch_size=1,
        channels=nca_config.state_channels,
        height=int(phenotype["height"]),
        width=int(phenotype["width"]),
        alive_channel=nca_config.alive_channel,
        device=device,
        dtype=dtype,
    )

    target_cfg = raw["target"]
    target_spec = TargetSpec(
        kind=target_cfg["kind"],
        radius=int(target_cfg["radius"]),
        rgba=tuple(float(value) for value in target_cfg["rgba"]),
    )
    target = make_target(
        batch_size=1,
        channels=nca_config.state_channels,
        height=int(phenotype["height"]),
        width=int(phenotype["width"]),
        spec=target_spec,
        device=device,
        dtype=dtype,
    )

    training_cfg = raw["training"]
    lesion_cfg = raw["recovery"]["lesion"]
    training_damage_height = float(
        training_cfg.get("damage_height_fraction", lesion_cfg["height_fraction"])
    )
    training_damage_width = float(
        training_cfg.get("damage_width_fraction", lesion_cfg["width_fraction"])
    )
    train_config = TrainingConfig(
        variant=raw["variant"],
        iterations=int(training_cfg["iterations"]),
        learning_rate=float(training_cfg["learning_rate"]),
        steps_min=int(training_cfg["steps_min"]),
        steps_max=int(training_cfg["steps_max"]),
        batch_size=int(training_cfg["batch_size"]),
        pool_size=int(training_cfg["pool_size"]),
        damage_probability=float(training_cfg["damage_probability"]),
        damage_height_fraction=training_damage_height,
        damage_width_fraction=training_damage_width,
        damage_min_active_cells=int(training_cfg["damage_min_active_cells"]),
        gradient_clip_norm=float(training_cfg["gradient_clip_norm"]),
        hidden_state_l2_weight=float(training_cfg["hidden_state_l2_weight"]),
        loss_mode=str(training_cfg.get("loss_mode", "global_mse")),
        visible_channels=int(raw["reporting"]["visible_channels"]),
        record_every=int(raw["reporting"]["record_every_iterations"]),
        seed=effective_seed,
    )

    training_summary = train(
        model=model,
        seed_state=seed_state,
        target=target,
        config=train_config,
    )
    evaluation = evaluate_growth_and_recovery(
        model=model,
        seed_state=seed_state,
        target=target,
        growth_steps=int(raw["evaluation"]["growth_steps"]),
        recovery_steps=int(raw["recovery"]["eval_steps"]),
        seed=effective_seed + 1,
        lesion_height_fraction=float(lesion_cfg["height_fraction"]),
        lesion_width_fraction=float(lesion_cfg["width_fraction"]),
        visible_channels=int(raw["reporting"]["visible_channels"]),
    )
    evaluation["persistence"] = evaluate_persistence(
        model=model,
        seed_state=seed_state,
        target=target,
        growth_steps=int(raw["evaluation"]["growth_steps"]),
        persistence_steps=int(raw["evaluation"]["persistence_steps"]),
        seed=effective_seed + 2,
        visible_channels=int(raw["reporting"]["visible_channels"]),
    )

    checkpoint_path = None
    if args.checkpoint:
        checkpoint_path = Path(args.checkpoint)
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "model_state_dict": model.state_dict(),
                "nca_config": raw["model"],
                "target": target_cfg,
                "experiment_id": raw["experiment_id"],
                "variant": raw["variant"],
                "seed": effective_seed,
            },
            checkpoint_path,
        )

    record = {
        "schema": "yggdrasil.dg1a.p0.run.v1",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "experiment_id": raw["experiment_id"],
        "variant": raw["variant"],
        "source_revision": _git_revision(),
        "config_path": str(config_path),
        "config_sha256": file_sha256(config_path),
        "configured_seed": configured_seed,
        "seed_override": args.seed,
        "effective_seed": effective_seed,
        "config": raw,
        "effective_training_damage": {
            "height_fraction": training_damage_height,
            "width_fraction": training_damage_width,
        },
        "effective_evaluation_damage": {
            "height_fraction": float(lesion_cfg["height_fraction"]),
            "width_fraction": float(lesion_cfg["width_fraction"]),
        },
        "effective_training_loss_mode": train_config.loss_mode,
        "target_identity": target_identity(
            target_spec,
            height=int(phenotype["height"]),
            width=int(phenotype["width"]),
        ),
        "environment": environment_fingerprint(),
        "training": training_summary.to_dict(),
        "evaluation": evaluation,
        "checkpoint_path": str(checkpoint_path) if checkpoint_path else None,
    }
    write_evidence(args.evidence, record)
    print(json.dumps({"evidence": args.evidence, "final_loss": training_summary.final_recorded_loss}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
