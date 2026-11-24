#!/usr/bin/env python3
"""Stage 2b: Sample-Size & Teacher-Rank Falsification Ablation (Yggdrasil).

Isolates why Stage 2 hit MIXED_CAPACITY_BOTTLENECK (+12% to +16% shift MSE vs.
persistence at train_steps=1200) by running a 2-regime controlled ablation at
5x higher sample budget (train_steps=6000, ~1,200 shift samples, dim=256):

  Regime 1 (Full-Rank Teacher):   Full-rank random 2-layer SiLU MLP teacher.
  Regime 2 (Structured Teacher):  Intrinsic-rank-16 nonlinear MLP teacher
                                  embedded in R^dim (x -> R^16 -> SiLU -> R^dim).

Pre-registered hypotheses:
  - On Full-Rank Teacher with 5x data, DenseResidualPredictor should stop
    overfitting and reveal any true low-rank capacity gap of ProceduralLinear.
  - On Structured Rank-16 Teacher, EventProto(r=16,b=8) should clear the >=20%
    shift-MSE reduction bar AND stay within <=1.15x of Dense overall val MSE
    while preserving >=5x static memory reduction.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict
from typing import Dict, List, Optional

import torch
import torch.nn.functional as F

from experiments.procedural_event_proto import static_footprint_bytes
from experiments.procedural_event_stage2_train import (
    DenseResidualPredictor,
    Stage2ModelResult,
    TrainableEventProceduralPredictor,
    _eval_dense,
    _eval_event_proto,
    _train_dense,
    _train_event_proto,
)


class ConfigurableRankTeacherEnv:
    """Piecewise-predictable nonlinear stream with full-rank or low-rank teacher."""

    def __init__(
        self,
        dim: int,
        teacher_rank: Optional[int] = None,
        seed: int = 100,
    ) -> None:
        gen = torch.Generator(device="cpu").manual_seed(seed)
        self.dim = dim
        self.teacher_rank = teacher_rank
        self.diag_a = 0.92 + 0.06 * torch.rand(dim, generator=gen)
        self.diag_b = 0.05 * torch.randn(dim, generator=gen)

        if teacher_rank is None:
            # Full-rank 2-layer SiLU teacher MLP
            h = 2 * dim
            self.w1 = torch.randn(dim, h, generator=gen) / math.sqrt(dim)
            self.b1 = 0.1 * torch.randn(h, generator=gen)
            self.w2 = torch.randn(h, dim, generator=gen) / math.sqrt(h)
            self.b2 = 0.05 * torch.randn(dim, generator=gen)
        else:
            # Structured intrinsic-rank nonlinear manifold: R^dim -> R^r -> SiLU -> R^(4r) -> SiLU -> R^dim
            r = teacher_rank
            h = 4 * r
            self.p_in = torch.randn(dim, r, generator=gen) / math.sqrt(dim)
            self.w1 = torch.randn(r, h, generator=gen) / math.sqrt(r)
            self.b1 = 0.1 * torch.randn(h, generator=gen)
            self.w2 = torch.randn(h, r, generator=gen) / math.sqrt(h)
            self.p_out = torch.randn(r, dim, generator=gen) / math.sqrt(r)
            self.b2 = 0.05 * torch.randn(dim, generator=gen)

    def teacher_delta(self, x: torch.Tensor) -> torch.Tensor:
        if self.teacher_rank is None:
            return F.silu(x @ self.w1 + self.b1) @ self.w2 + self.b2
        z = x @ self.p_in
        h = F.silu(z @ self.w1 + self.b1)
        return (h @ self.w2) @ self.p_out + self.b2

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
                x_t = torch.randn((self.dim,), generator=gen)
                y_t = x_t + 0.5 * self.teacher_delta(x_t) + noise_std * torch.randn((self.dim,), generator=gen)
                is_shift[t] = True
            else:
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


def run_regime(
    regime_name: str,
    teacher_rank: Optional[int],
    dim: int = 256,
    train_steps: int = 6000,
    val_steps: int = 400,
    epochs: int = 20,
    batch_size: int = 128,
    lr: float = 3e-3,
    shift_prob: float = 0.2,
    tau: float = 0.25,
    seed: int = 42,
) -> Dict[str, object]:
    torch.manual_seed(seed)
    env = ConfigurableRankTeacherEnv(dim=dim, teacher_rank=teacher_rank, seed=seed + 100)
    train_data = env.sample_dataset(train_steps, shift_prob=shift_prob, seed=seed + 1)
    val_data = env.sample_dataset(val_steps, shift_prob=shift_prob, seed=seed + 2)

    y_val = val_data["next_y"]
    x_val = val_data["curr_x"]
    sm = val_data["is_shift"]
    persist_all = float(F.mse_loss(x_val, y_val).item())
    persist_shift = float(F.mse_loss(x_val[sm], y_val[sm]).item())
    persist_pred = float(F.mse_loss(x_val[~sm], y_val[~sm]).item())

    # 1. Dense baseline
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

    for name, rank, basis_dim in [
        ("EventProto(r=16,b=8)", 16, 8),
        ("EventProto(r=32,b=16)", 32, 16),
    ]:
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
        "regime": regime_name,
        "teacher_rank": teacher_rank,
        "train_shift_samples": int(train_data["is_shift"].sum().item()),
        "val_shift_samples": int(val_data["is_shift"].sum().item()),
        "persistence_baseline": {
            "val_mse_overall": round(persist_all, 5),
            "val_mse_shift": round(persist_shift, 5),
            "val_mse_predictable": round(persist_pred, 5),
        },
        "results": [asdict(r) for r in results],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 2b Sample-Size & Teacher-Rank Ablation")
    parser.add_argument("--dim", type=int, default=256)
    parser.add_argument("--train-steps", type=int, default=6000)
    parser.add_argument("--val-steps", type=int, default=400)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--lr", type=float, default=3e-3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    regimes = [
        run_regime(
            "Full-Rank Nonlinear Teacher",
            teacher_rank=None,
            dim=args.dim,
            train_steps=args.train_steps,
            val_steps=args.val_steps,
            epochs=args.epochs,
            batch_size=args.batch_size,
            lr=args.lr,
            seed=args.seed,
        ),
        run_regime(
            "Structured Rank-16 Nonlinear Teacher",
            teacher_rank=16,
            dim=args.dim,
            train_steps=args.train_steps,
            val_steps=args.val_steps,
            epochs=args.epochs,
            batch_size=args.batch_size,
            lr=args.lr,
            seed=args.seed,
        ),
    ]

    if args.json:
        print(json.dumps(regimes, indent=2))
        return

    for reg in regimes:
        pb = reg["persistence_baseline"]
        print(
            f"\n=== {reg['regime']} (dim={args.dim}, train={args.train_steps}, train_shifts={reg['train_shift_samples']}, epochs={args.epochs}) ==="
        )
        print(
            f"Persistence Baseline: overall_mse={pb['val_mse_overall']:.5f} | shift_mse={pb['val_mse_shift']:.5f} | pred_mse={pb['val_mse_predictable']:.5f}"
        )
        for r in reg["results"]:
            print(
                f"{r['name']:24s} | MB={r['static_mb']:.4f} ({r['memory_reduction_vs_dense']:.2f}x) | "
                f"val_all={r['val_mse_overall']:.5f} ({r['val_mse_ratio_vs_dense']:.3f}x dense) | "
                f"val_shift={r['val_mse_shift']:.5f} ({r['shift_mse_reduction_vs_persistence_pct']:+.2f}% vs persist) | "
                f"val_pred={r['val_mse_predictable']:.5f} | ms/step={r['eval_ms_per_step']:.4f} ({r['eval_speedup_vs_dense']:.2f}x) | "
                f"skip={r['skip_rate']*100:.1f}% | {r['verdict']}"
            )


if __name__ == "__main__":
    main()
