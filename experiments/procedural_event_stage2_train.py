#!/usr/bin/env python3
"""Stage 2: Real Training-Loss & Expressivity Falsification Test (Yggdrasil).

Tests whether ProceduralLinear + EventDrivenProceduralBlock can match DenseBlock
validation loss on a non-trivial piecewise-predictable nonlinear dynamical stream
under matched training budgets, while retaining static memory and batch-1 latency
advantages.

Regimes in the synthetic teacher stream:
  - Predictable steps (1 - shift_prob = 0.8): x_{t+1} = diag_a * x_t + diag_b + eps
  - Shift steps (shift_prob = 0.2): sudden input jump followed by a full-rank
    nonlinear 2-layer SiLU teacher MLP transition y_t = teacher_mlp(x_t) + eps.

Pre-registered Stage 2 Falsification Criteria:
  - PASS: Overall val MSE <= 1.15x DenseBlock val MSE AND shift-step val MSE
          reduces persistence-baseline MSE by >= 20% AND static memory >= 5.0x smaller.
  - MIXED_CAPACITY_BOTTLENECK: Beats persistence and keeps >= 5x memory reduction,
          but overall or shift-step MSE trails DenseBlock beyond the 1.15x threshold.
  - FAIL: Fails to beat persistence baseline or training diverges.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import asdict, dataclass
from typing import Dict, List, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from experiments.procedural_event_proto import (
    DenseBlock,
    ProceduralLinear,
    static_footprint_bytes,
)


class DenseResidualPredictor(nn.Module):
    """Static-weight DenseBlock residual next-step predictor baseline."""

    def __init__(self, dim: int, hidden_dim: int | None = None) -> None:
        super().__init__()
        self.dim = dim
        self.block = DenseBlock(dim=dim, hidden_dim=hidden_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.block(x)


class TrainableEventProceduralPredictor(nn.Module):
    """Trainable Event-Driven Procedural Residual Predictor.

    - Local surprise detector: x_hat_t = pred_scale * prev_x + pred_bias
      surprise_t = ||x_t - x_hat_t||_2 / sqrt(dim)
    - Fast skip head (when surprise_t < tau): y_hat = fast_scale * x_t + fast_bias
    - Deep procedural head (when surprise_t >= tau): y_hat = x_t + fc2(SiLU(fc1(x_t)))
    """

    def __init__(
        self,
        dim: int,
        hidden_dim: int | None = None,
        rank: int = 16,
        seed_dim: int = 64,
        basis_dim: int = 8,
        hyper_hidden: int = 32,
        tau: float = 0.25,
    ) -> None:
        super().__init__()
        self.dim = dim
        self.hidden_dim = hidden_dim if hidden_dim is not None else 4 * dim
        self.tau = float(tau)

        # Diagonal affine surprise detector & fast-path predictor
        self.pred_scale = nn.Parameter(torch.ones(dim))
        self.pred_bias = nn.Parameter(torch.zeros(dim))
        self.fast_scale = nn.Parameter(torch.ones(dim))
        self.fast_bias = nn.Parameter(torch.zeros(dim))

        # Deep procedural path
        self.fc1 = ProceduralLinear(
            dim,
            self.hidden_dim,
            rank=rank,
            seed_dim=seed_dim,
            basis_dim=basis_dim,
            hyper_hidden=hyper_hidden,
        )
        self.fc2 = ProceduralLinear(
            self.hidden_dim,
            dim,
            rank=rank,
            seed_dim=seed_dim,
            basis_dim=basis_dim,
            hyper_hidden=hyper_hidden,
        )

    def surprise_norm(self, x: torch.Tensor, prev_x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        x_hat = prev_x * self.pred_scale + self.pred_bias
        residual = x - x_hat
        surprise = torch.linalg.vector_norm(residual, dim=-1) / math.sqrt(self.dim)
        return x_hat, surprise

    def forward_batch(
        self, x: torch.Tensor, prev_x: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Vectorized training/eval pass over [N, dim] tensors."""
        x_hat, surprise = self.surprise_norm(x, prev_x)
        fast_out = x * self.fast_scale + self.fast_bias
        deep_mask = surprise >= self.tau

        out = fast_out.clone()
        if bool(deep_mask.any().item()):
            x_deep = x[deep_mask]
            deep_out = x_deep + self.fc2(F.silu(self.fc1(x_deep)))
            out[deep_mask] = deep_out
        return out, x_hat, deep_mask

    def forward_step_batch1(
        self, x: torch.Tensor, prev_x: torch.Tensor
    ) -> Tuple[torch.Tensor, bool]:
        """Hard-skip batch-1 inference step ([1, dim])."""
        _, surprise = self.surprise_norm(x, prev_x)
        if float(surprise.item()) < self.tau:
            return x * self.fast_scale + self.fast_bias, True
        return x + self.fc2(F.silu(self.fc1(x))), False


class NonlinearTeacherEnv:
    """Piecewise-predictable nonlinear dynamical stream with a full-rank teacher MLP."""

    def __init__(self, dim: int, seed: int = 100) -> None:
        gen = torch.Generator(device="cpu").manual_seed(seed)
        self.dim = dim
        # Stable diagonal affine dynamics for predictable steps
        self.diag_a = 0.92 + 0.06 * torch.rand(dim, generator=gen)
        self.diag_b = 0.05 * torch.randn(dim, generator=gen)

        # Full-rank nonlinear teacher MLP for regime-shift steps
        teacher_hidden = 2 * dim
        self.w1 = torch.randn(dim, teacher_hidden, generator=gen) / math.sqrt(dim)
        self.b1 = 0.1 * torch.randn(teacher_hidden, generator=gen)
        self.w2 = torch.randn(teacher_hidden, dim, generator=gen) / math.sqrt(teacher_hidden)
        self.b2 = 0.05 * torch.randn(dim, generator=gen)

    def teacher_delta(self, x: torch.Tensor) -> torch.Tensor:
        return F.silu(x @ self.w1 + self.b1) @ self.w2 + self.b2

    def sample_dataset(
        self,
        num_steps: int,
        shift_prob: float = 0.2,
        noise_std: float = 0.02,
        seed: int = 42,
    ) -> Dict[str, torch.Tensor]:
        gen = torch.Generator(device="cpu").manual_seed(seed)
        prev_x = torch.empty((num_steps, self.dim), dtype=torch.float32)
        curr_x = torch.empty((num_steps, self.dim), dtype=torch.float32)
        next_y = torch.empty((num_steps, self.dim), dtype=torch.float32)
        is_shift = torch.zeros((num_steps,), dtype=torch.bool)

        probs = torch.rand((num_steps,), generator=gen)
        state = torch.randn((self.dim,), generator=gen) * 0.5

        for t in range(num_steps):
            prev_x[t] = state
            if t == 0 or float(probs[t].item()) < shift_prob:
                # Regime shift: sudden jump in input state, followed by nonlinear teacher dynamics
                x_t = torch.randn((self.dim,), generator=gen)
                y_t = x_t + 0.5 * self.teacher_delta(x_t) + noise_std * torch.randn((self.dim,), generator=gen)
                is_shift[t] = True
            else:
                # Predictable continuation: local diagonal affine evolution
                x_t = state * self.diag_a + self.diag_b + noise_std * torch.randn((self.dim,), generator=gen)
                y_t = x_t * self.diag_a + self.diag_b + noise_std * torch.randn((self.dim,), generator=gen)
                is_shift[t] = False

            curr_x[t] = x_t
            next_y[t] = y_t
            state = y_t

        return {
            "prev_x": prev_x,
            "curr_x": curr_x,
            "next_y": next_y,
            "is_shift": is_shift,
        }


@dataclass
class Stage2ModelResult:
    name: str
    params: int
    static_mb: float
    memory_reduction_vs_dense: float
    train_loss_start: float
    train_loss_end: float
    val_mse_overall: float
    val_mse_shift: float
    val_mse_predictable: float
    val_mse_ratio_vs_dense: float
    shift_mse_reduction_vs_persistence_pct: float
    eval_ms_per_step: float
    eval_speedup_vs_dense: float
    skip_rate: float
    verdict: str


def _train_dense(
    model: DenseResidualPredictor,
    train_data: Dict[str, torch.Tensor],
    epochs: int,
    batch_size: int,
    lr: float,
) -> Tuple[float, float]:
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    n = train_data["curr_x"].shape[0]
    first_loss = 0.0
    last_loss = 0.0
    model.train()
    for ep in range(epochs):
        perm = torch.randperm(n)
        ep_loss = 0.0
        batches = 0
        for i in range(0, n, batch_size):
            idx = perm[i : i + batch_size]
            x = train_data["curr_x"][idx]
            y = train_data["next_y"][idx]
            opt.zero_grad(set_to_none=True)
            pred = model(x)
            loss = F.mse_loss(pred, y)
            loss.backward()
            opt.step()
            ep_loss += float(loss.item())
            batches += 1
        avg = ep_loss / max(batches, 1)
        if ep == 0:
            first_loss = avg
        last_loss = avg
    return first_loss, last_loss


def _train_event_proto(
    model: TrainableEventProceduralPredictor,
    train_data: Dict[str, torch.Tensor],
    epochs: int,
    batch_size: int,
    lr: float,
) -> Tuple[float, float]:
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    n = train_data["curr_x"].shape[0]
    first_loss = 0.0
    last_loss = 0.0
    model.train()
    for ep in range(epochs):
        perm = torch.randperm(n)
        ep_loss = 0.0
        batches = 0
        for i in range(0, n, batch_size):
            idx = perm[i : i + batch_size]
            prev_x = train_data["prev_x"][idx]
            x = train_data["curr_x"][idx]
            y = train_data["next_y"][idx]

            opt.zero_grad(set_to_none=True)
            pred, x_hat, deep_mask = model.forward_batch(x, prev_x)
            pred_loss = F.mse_loss(pred, y)

            # Train local surprise predictor on non-shift (low-surprise) transitions
            # using a Huber loss so large regime jumps don't corrupt the affine tracker.
            local_track_loss = F.huber_loss(x_hat, x, delta=0.5)
            loss = pred_loss + 0.1 * local_track_loss
            loss.backward()
            opt.step()
            ep_loss += float(pred_loss.item())
            batches += 1
        avg = ep_loss / max(batches, 1)
        if ep == 0:
            first_loss = avg
        last_loss = avg
    return first_loss, last_loss


def _eval_dense(
    model: DenseResidualPredictor, val_data: Dict[str, torch.Tensor]
) -> Tuple[float, float, float, float]:
    model.eval()
    x_all = val_data["curr_x"]
    y_all = val_data["next_y"]
    shift_mask = val_data["is_shift"]
    n = x_all.shape[0]

    preds = torch.empty_like(y_all)
    with torch.inference_mode():
        # Warmup
        for t in range(min(20, n)):
            _ = model(x_all[t : t + 1])
        t0 = time.perf_counter()
        for t in range(n):
            preds[t : t + 1] = model(x_all[t : t + 1])
        elapsed = time.perf_counter() - t0

    mse_all = float(F.mse_loss(preds, y_all).item())
    mse_shift = float(F.mse_loss(preds[shift_mask], y_all[shift_mask]).item())
    mse_pred = float(F.mse_loss(preds[~shift_mask], y_all[~shift_mask]).item())
    ms_step = (elapsed / n) * 1000.0
    return mse_all, mse_shift, mse_pred, ms_step


def _eval_event_proto(
    model: TrainableEventProceduralPredictor, val_data: Dict[str, torch.Tensor]
) -> Tuple[float, float, float, float, float]:
    model.eval()
    prev_all = val_data["prev_x"]
    x_all = val_data["curr_x"]
    y_all = val_data["next_y"]
    shift_mask = val_data["is_shift"]
    n = x_all.shape[0]

    preds = torch.empty_like(y_all)
    skips = 0
    with torch.inference_mode():
        for t in range(min(20, n)):
            _ = model.forward_step_batch1(x_all[t : t + 1], prev_all[t : t + 1])
        t0 = time.perf_counter()
        for t in range(n):
            out, skipped = model.forward_step_batch1(x_all[t : t + 1], prev_all[t : t + 1])
            preds[t : t + 1] = out
            if skipped:
                skips += 1
        elapsed = time.perf_counter() - t0

    mse_all = float(F.mse_loss(preds, y_all).item())
    mse_shift = float(F.mse_loss(preds[shift_mask], y_all[shift_mask]).item())
    mse_pred = float(F.mse_loss(preds[~shift_mask], y_all[~shift_mask]).item())
    ms_step = (elapsed / n) * 1000.0
    skip_rate = skips / float(n)
    return mse_all, mse_shift, mse_pred, ms_step, skip_rate


def run_stage2_experiment(
    dim: int = 256,
    train_steps: int = 1200,
    val_steps: int = 300,
    epochs: int = 25,
    batch_size: int = 64,
    lr: float = 3e-3,
    shift_prob: float = 0.2,
    tau: float = 0.25,
    seed: int = 42,
) -> Dict[str, object]:
    torch.manual_seed(seed)
    env = NonlinearTeacherEnv(dim=dim, seed=seed + 100)
    train_data = env.sample_dataset(train_steps, shift_prob=shift_prob, seed=seed + 1)
    val_data = env.sample_dataset(val_steps, shift_prob=shift_prob, seed=seed + 2)

    # Persistence baseline: y_hat = x_t
    y_val = val_data["next_y"]
    x_val = val_data["curr_x"]
    sm = val_data["is_shift"]
    persist_all = float(F.mse_loss(x_val, y_val).item())
    persist_shift = float(F.mse_loss(x_val[sm], y_val[sm]).item())
    persist_pred = float(F.mse_loss(x_val[~sm], y_val[~sm]).item())

    # 1. DenseBlock baseline
    torch.manual_seed(seed)
    dense = DenseResidualPredictor(dim=dim)
    dense_params, dense_bytes = static_footprint_bytes(dense)
    dense_mb = dense_bytes / (1024.0 * 1024.0)
    d_start, d_end = _train_dense(dense, train_data, epochs=epochs, batch_size=batch_size, lr=lr)
    d_all, d_shift, d_pred, d_ms = _eval_dense(dense, val_data)

    results: List[Stage2ModelResult] = [
        Stage2ModelResult(
            name="DenseResidualPredictor",
            params=dense_params,
            static_mb=round(dense_mb, 4),
            memory_reduction_vs_dense=1.0,
            train_loss_start=round(d_start, 5),
            train_loss_end=round(d_end, 5),
            val_mse_overall=round(d_all, 5),
            val_mse_shift=round(d_shift, 5),
            val_mse_predictable=round(d_pred, 5),
            val_mse_ratio_vs_dense=1.0,
            shift_mse_reduction_vs_persistence_pct=round((1.0 - d_shift / persist_shift) * 100.0, 2),
            eval_ms_per_step=round(d_ms, 4),
            eval_speedup_vs_dense=1.0,
            skip_rate=0.0,
            verdict="BASELINE",
        )
    ]

    # 2. Procedural configs: Stage-1 compact (rank=16, basis=8) and higher-capacity (rank=32, basis=16)
    configs = [
        ("EventProto(r=16,b=8)", 16, 8),
        ("EventProto(r=32,b=16)", 32, 16),
    ]
    for name, rank, basis_dim in configs:
        torch.manual_seed(seed)
        proto = TrainableEventProceduralPredictor(
            dim=dim, rank=rank, seed_dim=64, basis_dim=basis_dim, tau=tau
        )
        p_params, p_bytes = static_footprint_bytes(proto)
        p_mb = p_bytes / (1024.0 * 1024.0)
        mem_red = dense_bytes / max(p_bytes, 1)

        p_start, p_end = _train_event_proto(proto, train_data, epochs=epochs, batch_size=batch_size, lr=lr)
        p_all, p_shift, p_pred, p_ms, p_skip = _eval_event_proto(proto, val_data)

        mse_ratio = p_all / max(d_all, 1e-12)
        shift_red_pct = (1.0 - p_shift / max(persist_shift, 1e-12)) * 100.0
        speedup = d_ms / max(p_ms, 1e-12)

        if not math.isfinite(p_all) or p_all >= persist_all:
            verdict = "FAIL"
        elif mse_ratio <= 1.15 and shift_red_pct >= 20.0 and mem_red >= 5.0:
            verdict = "PASS"
        else:
            verdict = "MIXED_CAPACITY_BOTTLENECK"

        results.append(
            Stage2ModelResult(
                name=name,
                params=p_params,
                static_mb=round(p_mb, 4),
                memory_reduction_vs_dense=round(mem_red, 2),
                train_loss_start=round(p_start, 5),
                train_loss_end=round(p_end, 5),
                val_mse_overall=round(p_all, 5),
                val_mse_shift=round(p_shift, 5),
                val_mse_predictable=round(p_pred, 5),
                val_mse_ratio_vs_dense=round(mse_ratio, 3),
                shift_mse_reduction_vs_persistence_pct=round(shift_red_pct, 2),
                eval_ms_per_step=round(p_ms, 4),
                eval_speedup_vs_dense=round(speedup, 3),
                skip_rate=round(p_skip, 4),
                verdict=verdict,
            )
        )

    return {
        "config": {
            "dim": dim,
            "train_steps": train_steps,
            "val_steps": val_steps,
            "epochs": epochs,
            "batch_size": batch_size,
            "lr": lr,
            "shift_prob": shift_prob,
            "tau": tau,
            "seed": seed,
        },
        "persistence_baseline": {
            "val_mse_overall": round(persist_all, 5),
            "val_mse_shift": round(persist_shift, 5),
            "val_mse_predictable": round(persist_pred, 5),
        },
        "results": [asdict(r) for r in results],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 2 Training-Loss Falsification Benchmark")
    parser.add_argument("--dim", type=int, default=256)
    parser.add_argument("--train-steps", type=int, default=1200)
    parser.add_argument("--val-steps", type=int, default=300)
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=3e-3)
    parser.add_argument("--shift-prob", type=float, default=0.2)
    parser.add_argument("--tau", type=float, default=0.25)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    out = run_stage2_experiment(
        dim=args.dim,
        train_steps=args.train_steps,
        val_steps=args.val_steps,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        shift_prob=args.shift_prob,
        tau=args.tau,
        seed=args.seed,
    )
    if args.json:
        print(json.dumps(out, indent=2))
        return

    pb = out["persistence_baseline"]
    print(
        f"=== Stage 2 Real Training-Loss Benchmark (dim={args.dim}, train={args.train_steps}, val={args.val_steps}, epochs={args.epochs}) ==="
    )
    print(
        f"Persistence Baseline: overall_mse={pb['val_mse_overall']:.5f} | shift_mse={pb['val_mse_shift']:.5f} | pred_mse={pb['val_mse_predictable']:.5f}"
    )
    for r in out["results"]:
        print(
            f"{r['name']:24s} | MB={r['static_mb']:.4f} ({r['memory_reduction_vs_dense']:.2f}x) | "
            f"val_all={r['val_mse_overall']:.5f} ({r['val_mse_ratio_vs_dense']:.3f}x dense) | "
            f"val_shift={r['val_mse_shift']:.5f} ({r['shift_mse_reduction_vs_persistence_pct']:+.2f}% vs persist) | "
            f"val_pred={r['val_mse_predictable']:.5f} | ms/step={r['eval_ms_per_step']:.4f} ({r['eval_speedup_vs_dense']:.2f}x) | "
            f"skip={r['skip_rate']*100:.1f}% | {r['verdict']}"
        )


if __name__ == "__main__":
    main()
