#!/usr/bin/env python3
"""Procedural-Weight + Event-Driven Residual Prototype (Yggdrasil).

Isolated, falsifiable batch-1 inference prototype comparing:
  1. DenseBlock: Standard static-weight FFN baseline (fc1 -> SiLU -> fc2).
  2. EventDrivenProceduralBlock: Diagonal affine local predictor with residual
     surprise gating + ProceduralLinear layers that synthesize low-rank weight
     factors (u, v) on the fly from a cache-resident seed without materializing
     the full [out_dim, in_dim] weight matrix.

Falsification criteria (at dim >= 2048):
  - PASS: Batch-1 latency >= 2.0x faster than DenseBlock AND static memory >= 5.0x smaller.
  - FAIL: Otherwise (record exact numbers and root cause).
"""

from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import asdict, dataclass
from typing import Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F


class DenseBlock(nn.Module):
    """Standard static-weight FFN baseline (fc1 -> SiLU -> fc2)."""

    def __init__(self, dim: int, hidden_dim: Optional[int] = None) -> None:
        super().__init__()
        self.dim = dim
        self.hidden_dim = hidden_dim if hidden_dim is not None else 4 * dim
        self.fc1 = nn.Linear(dim, self.hidden_dim)
        self.fc2 = nn.Linear(self.hidden_dim, dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.fc2(F.silu(self.fc1(x)))


class ProceduralLinear(nn.Module):
    """Synthesizes low-rank factors (u, v) on the fly from a cache-resident seed.

    Computes y = (x @ v) @ u.T + bias where:
      - seed: [seed_dim] cache-resident learned vector (default 64)
      - hyper_net(seed) -> u_core [basis_dim, rank], v_core [basis_dim, rank]
      - u = u_basis @ u_core -> [out_dim, rank]
      - v = v_basis @ v_core -> [in_dim, rank]
    Never materializes the full [out_dim, in_dim] weight matrix.
    """

    def __init__(
        self,
        in_dim: int,
        out_dim: int,
        rank: int = 16,
        seed_dim: int = 64,
        basis_dim: int = 8,
        hyper_hidden: int = 32,
        bias: bool = True,
    ) -> None:
        super().__init__()
        self.in_dim = in_dim
        self.out_dim = out_dim
        self.rank = rank
        self.seed_dim = seed_dim
        self.basis_dim = basis_dim

        # Cache-resident procedural seed.
        self.seed = nn.Parameter(torch.randn(seed_dim) * 0.02)

        # Lightweight hypernetwork emitting compact core factor tensors.
        core_size = basis_dim * rank
        self.hyper_fc1 = nn.Linear(seed_dim, hyper_hidden)
        self.hyper_fc2 = nn.Linear(hyper_hidden, 2 * core_size)

        # Compact learned projection bases for output and input dimensions.
        self.u_basis = nn.Parameter(
            torch.randn(out_dim, basis_dim) / math.sqrt(out_dim * basis_dim)
        )
        self.v_basis = nn.Parameter(
            torch.randn(in_dim, basis_dim) / math.sqrt(in_dim * basis_dim)
        )

        if bias:
            self.bias = nn.Parameter(torch.zeros(out_dim))
        else:
            self.register_parameter("bias", None)

    def synthesize_factors(self) -> Tuple[torch.Tensor, torch.Tensor]:
        """Return low-rank factors (u: [out_dim, rank], v: [in_dim, rank])."""
        h = F.silu(self.hyper_fc1(self.seed))
        cores = self.hyper_fc2(h)
        core_size = self.basis_dim * self.rank
        u_core = cores[:core_size].view(self.basis_dim, self.rank)
        v_core = cores[core_size:].view(self.basis_dim, self.rank)
        u = self.u_basis @ u_core  # [out_dim, rank]
        v = self.v_basis @ v_core  # [in_dim, rank]
        return u, v

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        u, v = self.synthesize_factors()
        # Factorized matmul: never materializes [out_dim, in_dim].
        z = x @ v  # [..., rank]
        y = z @ u.transpose(0, 1)  # [..., out_dim]
        if self.bias is not None:
            y = y + self.bias
        return y


class EventDrivenProceduralBlock(nn.Module):
    """Diagonal affine local predictor + surprise-gated procedural FFN."""

    def __init__(
        self,
        dim: int,
        hidden_dim: Optional[int] = None,
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

        # Diagonal affine local predictor: x_hat = pred_scale * prev_x + pred_bias
        self.pred_scale = nn.Parameter(torch.ones(dim))
        self.pred_bias = nn.Parameter(torch.zeros(dim))

        # Deep procedural path (invoked only when surprise >= tau).
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

        # Streaming state for single-argument forward(x) calls.
        self._prev_x: Optional[torch.Tensor] = None

    def reset_state(self) -> None:
        self._prev_x = None

    def compute_prediction_and_surprise(
        self, x: torch.Tensor, prev_x: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        ref = prev_x if prev_x is not None else self._prev_x
        if ref is None:
            x_hat = self.pred_bias.expand_as(x)
        else:
            x_hat = ref * self.pred_scale + self.pred_bias
        residual = x - x_hat
        # RMS residual norm (scale-invariant across dim).
        surprise = torch.linalg.vector_norm(residual, dim=-1) / math.sqrt(self.dim)
        return x_hat, surprise

    def forward_with_stats(
        self,
        x: torch.Tensor,
        prev_x: Optional[torch.Tensor] = None,
        update_state: bool = True,
    ) -> Tuple[torch.Tensor, bool, float]:
        x_hat, surprise = self.compute_prediction_and_surprise(x, prev_x=prev_x)
        surprise_val = float(surprise.mean().item())
        if update_state:
            self._prev_x = x.detach()

        if surprise_val < self.tau:
            # Fast skip path: bypass deep procedural block completely.
            return x_hat, True, surprise_val

        # Deep procedural path.
        out = self.fc2(F.silu(self.fc1(x)))
        return out, False, surprise_val

    def forward(
        self, x: torch.Tensor, prev_x: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        out, _, _ = self.forward_with_stats(x, prev_x=prev_x, update_state=True)
        return out


def static_footprint_bytes(module: nn.Module) -> Tuple[int, int]:
    """Return (total_elements, total_bytes) across all parameters and buffers."""
    total_elems = 0
    total_bytes = 0
    for tensor in list(module.parameters()) + list(module.buffers()):
        total_elems += tensor.numel()
        total_bytes += tensor.numel() * tensor.element_size()
    return total_elems, total_bytes


def generate_piecewise_stream(
    steps: int,
    dim: int,
    shift_prob: float = 0.2,
    drift_std: float = 0.02,
    seed: int = 42,
    device: torch.device | str = "cpu",
) -> Tuple[torch.Tensor, int]:
    """Generate a synthetic piecewise-predictable batch-1 stream [steps, 1, dim].

    With probability `shift_prob`, the state jumps to a fresh N(0, I) draw
    (high surprise). Otherwise it evolves smoothly with small Gaussian drift
    `drift_std` around the previous state (low surprise).
    """
    gen = torch.Generator(device="cpu")
    gen.manual_seed(seed)

    stream = torch.empty((steps, 1, dim), dtype=torch.float32)
    curr = torch.randn((1, dim), generator=gen)
    stream[0] = curr
    shift_count = 1  # Step 0 has no prior state, so it triggers a shift.

    probs = torch.rand((steps,), generator=gen)
    for t in range(1, steps):
        if float(probs[t].item()) < shift_prob:
            curr = torch.randn((1, dim), generator=gen)
            shift_count += 1
        else:
            curr = curr + torch.randn((1, dim), generator=gen) * drift_std
        stream[t] = curr

    return stream.to(device), shift_count


@dataclass
class BenchmarkResult:
    device: str
    dim: int
    hidden_dim: int
    steps: int
    warmup: int
    shift_prob: float
    tau: float
    rank: int
    seed_dim: int
    basis_dim: int
    dense_params: int
    dense_static_mb: float
    proto_params: int
    proto_static_mb: float
    memory_reduction_x: float
    dense_ms_per_step: float
    dense_steps_per_sec: float
    proto_ms_per_step: float
    proto_steps_per_sec: float
    speedup_ratio: float
    skip_rate: float
    stream_shift_rate: float
    always_deep_ms_per_step: float
    always_deep_speedup_ratio: float
    falsification_verdict: str


def _sync(device: torch.device) -> None:
    if device.type == "cuda":
        torch.cuda.synchronize(device)


def run_benchmark(
    device_str: str = "cpu",
    dim: int = 1024,
    steps: int = 300,
    warmup: int = 20,
    ffn_mult: int = 4,
    rank: int = 16,
    seed_dim: int = 64,
    basis_dim: int = 8,
    shift_prob: float = 0.2,
    tau: float = 0.25,
    seed: int = 42,
) -> BenchmarkResult:
    device = torch.device(device_str)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but torch.cuda.is_available() is False")

    torch.manual_seed(seed)
    hidden_dim = dim * ffn_mult

    dense = DenseBlock(dim=dim, hidden_dim=hidden_dim).to(device).eval()
    proto = (
        EventDrivenProceduralBlock(
            dim=dim,
            hidden_dim=hidden_dim,
            rank=rank,
            seed_dim=seed_dim,
            basis_dim=basis_dim,
            tau=tau,
        )
        .to(device)
        .eval()
    )

    dense_params, dense_bytes = static_footprint_bytes(dense)
    proto_params, proto_bytes = static_footprint_bytes(proto)
    dense_mb = dense_bytes / (1024.0 * 1024.0)
    proto_mb = proto_bytes / (1024.0 * 1024.0)
    mem_ratio = dense_bytes / max(proto_bytes, 1)

    total_steps = warmup + steps
    stream, shift_count = generate_piecewise_stream(
        steps=total_steps,
        dim=dim,
        shift_prob=shift_prob,
        seed=seed,
        device=device,
    )

    with torch.inference_mode():
        # Warmup DenseBlock
        for t in range(warmup):
            _ = dense(stream[t])
        _sync(device)

        t0 = time.perf_counter()
        for t in range(warmup, total_steps):
            _ = dense(stream[t])
        _sync(device)
        dense_elapsed = time.perf_counter() - t0

        # Warmup EventDrivenProceduralBlock
        proto.reset_state()
        for t in range(warmup):
            _ = proto(stream[t])
        _sync(device)

        skips = 0
        t0 = time.perf_counter()
        for t in range(warmup, total_steps):
            _, skipped, _ = proto.forward_with_stats(stream[t])
            if skipped:
                skips += 1
        _sync(device)
        proto_elapsed = time.perf_counter() - t0

        # Diagnostic ablation: always-deep procedural block (tau=0.0, 0% skip)
        orig_tau = proto.tau
        proto.tau = 0.0
        proto.reset_state()
        for t in range(min(warmup, 10)):
            _ = proto(stream[t])
        _sync(device)

        t0 = time.perf_counter()
        for t in range(warmup, total_steps):
            _ = proto(stream[t])
        _sync(device)
        deep_elapsed = time.perf_counter() - t0
        proto.tau = orig_tau

    dense_ms = (dense_elapsed / steps) * 1000.0
    proto_ms = (proto_elapsed / steps) * 1000.0
    deep_ms = (deep_elapsed / steps) * 1000.0

    dense_sps = steps / max(dense_elapsed, 1e-12)
    proto_sps = steps / max(proto_elapsed, 1e-12)
    speedup = dense_elapsed / max(proto_elapsed, 1e-12)
    deep_speedup = dense_elapsed / max(deep_elapsed, 1e-12)
    skip_rate = skips / float(steps)
    shift_rate = shift_count / float(total_steps)

    if dim >= 2048:
        verdict = "PASS" if (speedup >= 2.0 and mem_ratio >= 5.0) else "FAIL"
    else:
        verdict = (
            "PASS_SUBSCALE"
            if (speedup >= 2.0 and mem_ratio >= 5.0)
            else "FAIL_SUBSCALE"
        )

    return BenchmarkResult(
        device=device_str,
        dim=dim,
        hidden_dim=hidden_dim,
        steps=steps,
        warmup=warmup,
        shift_prob=shift_prob,
        tau=tau,
        rank=rank,
        seed_dim=seed_dim,
        basis_dim=basis_dim,
        dense_params=dense_params,
        dense_static_mb=round(dense_mb, 4),
        proto_params=proto_params,
        proto_static_mb=round(proto_mb, 4),
        memory_reduction_x=round(mem_ratio, 2),
        dense_ms_per_step=round(dense_ms, 4),
        dense_steps_per_sec=round(dense_sps, 2),
        proto_ms_per_step=round(proto_ms, 4),
        proto_steps_per_sec=round(proto_sps, 2),
        speedup_ratio=round(speedup, 3),
        skip_rate=round(skip_rate, 4),
        stream_shift_rate=round(shift_rate, 4),
        always_deep_ms_per_step=round(deep_ms, 4),
        always_deep_speedup_ratio=round(deep_speedup, 3),
        falsification_verdict=verdict,
    )


def run_self_test() -> None:
    """Lightweight inline smoke test verifying core prototype invariants."""
    torch.manual_seed(0)
    for dim in (64, 1024):
        dense = DenseBlock(dim=dim).eval()
        proto = EventDrivenProceduralBlock(dim=dim, tau=0.25).eval()

        x0 = torch.randn(1, dim)
        x_small = x0 + 0.01 * torch.randn(1, dim)
        x_large = torch.randn(1, dim) * 2.0

        with torch.inference_mode():
            y_dense = dense(x0)
            y_skip, skipped_low, s_low = proto.forward_with_stats(
                x_small, prev_x=x0, update_state=False
            )
            y_deep, skipped_high, s_high = proto.forward_with_stats(
                x_large, prev_x=x0, update_state=False
            )

        assert y_skip.shape == y_dense.shape, f"Shape mismatch: {y_skip.shape} vs {y_dense.shape}"
        assert y_deep.shape == y_dense.shape, f"Shape mismatch: {y_deep.shape} vs {y_dense.shape}"
        assert skipped_low is True and s_low < proto.tau, f"Expected skip, got skipped={skipped_low}, s={s_low}"
        assert skipped_high is False and s_high >= proto.tau, f"Expected deep path, got skipped={skipped_high}, s={s_high}"

        if dim >= 1024:
            dense_p, dense_b = static_footprint_bytes(dense)
            proto_p, proto_b = static_footprint_bytes(proto)
            assert proto_p < dense_p and proto_b < dense_b, (
                f"Expected smaller static footprint at dim={dim}: proto={proto_p}, dense={dense_p}"
            )
    print("SELF_TEST: PASS")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Procedural-Weight + Event-Driven Residual Prototype Benchmark"
    )
    parser.add_argument("--device", type=str, default="cpu", choices=["cpu", "cuda"])
    parser.add_argument("--dim", type=int, default=1024)
    parser.add_argument("--steps", type=int, default=300)
    parser.add_argument("--warmup", type=int, default=20)
    parser.add_argument("--ffn-mult", type=int, default=4)
    parser.add_argument("--rank", type=int, default=16)
    parser.add_argument("--seed-dim", type=int, default=64)
    parser.add_argument("--basis-dim", type=int, default=8)
    parser.add_argument("--shift-prob", type=float, default=0.2)
    parser.add_argument("--tau", type=float, default=0.25)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return

    res = run_benchmark(
        device_str=args.device,
        dim=args.dim,
        steps=args.steps,
        warmup=args.warmup,
        ffn_mult=args.ffn_mult,
        rank=args.rank,
        seed_dim=args.seed_dim,
        basis_dim=args.basis_dim,
        shift_prob=args.shift_prob,
        tau=args.tau,
        seed=args.seed,
    )

    if args.json:
        print(json.dumps(asdict(res), indent=2))
        return

    print(
        f"=== Procedural-Event Prototype Benchmark ({res.device}, dim={res.dim}, hidden={res.hidden_dim}, steps={res.steps}) ==="
    )
    print(
        f"Static Memory : Dense={res.dense_static_mb:.4f} MB ({res.dense_params:,} params) | "
        f"Proto={res.proto_static_mb:.4f} MB ({res.proto_params:,} params) | "
        f"Reduction={res.memory_reduction_x:.2f}x"
    )
    print(
        f"DenseBlock    : {res.dense_ms_per_step:.4f} ms/step | {res.dense_steps_per_sec:.2f} steps/s"
    )
    print(
        f"Proto (Event) : {res.proto_ms_per_step:.4f} ms/step | {res.proto_steps_per_sec:.2f} steps/s | "
        f"Speedup={res.speedup_ratio:.3f}x | SkipRate={res.skip_rate * 100:.2f}%"
    )
    print(
        f"Proto (Deep)  : {res.always_deep_ms_per_step:.4f} ms/step | "
        f"AlwaysDeepSpeedup={res.always_deep_speedup_ratio:.3f}x (tau=0.0 diagnostic)"
    )
    print(f"Verdict       : {res.falsification_verdict}")


if __name__ == "__main__":
    main()
