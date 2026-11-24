"""Unit tests for Stage 2 and Stage 2b trainable procedural-event prototypes."""

from __future__ import annotations

import sys
from pathlib import Path

import torch
import torch.nn.functional as F

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.procedural_event_stage2_train import (
    TrainableEventProceduralPredictor,
    run_stage2_experiment,
)
from experiments.procedural_event_stage2b_ablation import run_regime


def test_procedural_hypernet_receives_nonzero_gradients() -> None:
    torch.manual_seed(0)
    model = TrainableEventProceduralPredictor(dim=64, rank=8, seed_dim=32, basis_dim=4, tau=0.25)
    prev_x = torch.randn(4, 64) * 0.5
    x = prev_x + torch.randn(4, 64) * 2.0  # guaranteed above tau with non-zero prev_x
    target = torch.randn(4, 64)

    out, x_hat, deep_mask = model.forward_batch(x, prev_x)
    assert bool(deep_mask.all().item())
    loss = F.mse_loss(out, target) + 0.1 * F.mse_loss(x_hat, x)
    loss.backward()

    for name in ("fc1.seed", "fc1.hyper_fc1.weight", "fc1.u_basis", "fc1.v_basis", "fc2.seed", "pred_scale"):
        param = dict(model.named_parameters())[name]
        assert param.grad is not None, f"Missing gradient on {name}"
        assert float(param.grad.abs().sum().item()) > 0.0, f"Zero gradient on {name}"


def test_stage2_smoke_training_reduces_loss() -> None:
    out = run_stage2_experiment(
        dim=64,
        train_steps=160,
        val_steps=64,
        epochs=5,
        batch_size=32,
        lr=5e-3,
        seed=7,
    )
    results = out["results"]
    assert len(results) == 3
    for r in results:
        assert r["train_loss_end"] < r["train_loss_start"], f"{r['name']} did not decrease training loss"
        assert r["val_mse_overall"] > 0.0


def test_stage2b_structured_rank_regime_smoke() -> None:
    reg = run_regime(
        "Smoke Structured",
        teacher_rank=8,
        dim=64,
        train_steps=160,
        val_steps=64,
        epochs=4,
        batch_size=32,
        lr=5e-3,
        seed=9,
    )
    assert reg["teacher_rank"] == 8
    assert len(reg["results"]) == 3
    for r in reg["results"]:
        assert r["train_loss_end"] < r["train_loss_start"]
