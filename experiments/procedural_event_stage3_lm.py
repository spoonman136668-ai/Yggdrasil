#!/usr/bin/env python3
"""Stage 3: Real-Data Byte-Level Streaming LM Falsification Test (Yggdrasil).

Evaluates DenseBlock FFN vs. ProceduralLinear FFN (always-deep and event-gated)
inside an identical causal byte-level language model trained on frozen real
repository source files (.py / .md from Yggdrasil main, excluding experiments/).

Pre-registered Stage 3 Falsification Criteria (held-out 20% real text):
  - PASS: Held-out BPB beats empirical Bigram control, stays within <= +0.15 BPB
          of DenseFFN-LM, reduces FFN static memory by >= 4.0x, and (for event-gated)
          achieves >= 30% real-text skip rate.
  - MIXED_SKIP_OR_CAPACITY: Beats Bigram and reduces FFN memory >= 4.0x, but
          either BPB trails DenseFFN-LM by > +0.15 BPB or skip rate < 30%.
  - FAIL: Fails to beat Bigram control or training diverges.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from experiments.procedural_event_proto import (
    DenseBlock,
    ProceduralLinear,
    static_footprint_bytes,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def load_repo_byte_corpus(root: Path = REPO_ROOT) -> Tuple[bytes, bytes, str, str, int]:
    """Load frozen .py/.md files from repo root (excluding experiments/ and proto tests)."""
    files: List[Path] = []
    for ext in ("*.py", "*.md"):
        for p in root.rglob(ext):
            rel = p.relative_to(root).as_posix()
            if (
                rel.startswith(".git/")
                or rel.startswith(".pytest_cache/")
                or rel.startswith("experiments/")
                or rel.startswith("tests/test_procedural_event")
            ):
                continue
            files.append(p)
    files.sort(key=lambda p: p.relative_to(root).as_posix())

    chunks = [p.read_bytes() for p in files]
    full_data = b"\n".join(chunks)
    split_idx = int(len(full_data) * 0.8)
    train_bytes = full_data[:split_idx]
    val_bytes = full_data[split_idx:]
    train_sha = hashlib.sha256(train_bytes).hexdigest()[:16]
    val_sha = hashlib.sha256(val_bytes).hexdigest()[:16]
    return train_bytes, val_bytes, train_sha, val_sha, len(files)


def empirical_bigram_bpb(train_bytes: bytes, val_bytes: bytes, alpha: float = 0.1) -> float:
    """Exact Laplace-smoothed byte bigram baseline BPB on held-out val_bytes."""
    counts = torch.full((256, 256), alpha, dtype=torch.float64)
    tr = torch.tensor(list(train_bytes), dtype=torch.long)
    for i in range(len(tr) - 1):
        counts[tr[i], tr[i + 1]] += 1.0
    probs = counts / counts.sum(dim=-1, keepdim=True)
    log2_probs = torch.log2(probs)

    va = torch.tensor(list(val_bytes), dtype=torch.long)
    nll_bits = -log2_probs[va[:-1], va[1:]].mean().item()
    return float(nll_bits)


class ProceduralFFN(nn.Module):
    """ProceduralLinear FFN with optional event-driven surprise skipping."""

    def __init__(
        self,
        dim: int,
        hidden_dim: int,
        rank: int = 16,
        seed_dim: int = 64,
        basis_dim: int = 8,
        tau: float = 0.0,
    ) -> None:
        super().__init__()
        self.dim = dim
        self.tau = float(tau)
        self.pred_scale = nn.Parameter(torch.ones(dim))
        self.pred_bias = nn.Parameter(torch.zeros(dim))
        self.fast_scale = nn.Parameter(torch.zeros(dim))
        self.fast_bias = nn.Parameter(torch.zeros(dim))
        self.fc1 = ProceduralLinear(dim, hidden_dim, rank=rank, seed_dim=seed_dim, basis_dim=basis_dim)
        self.fc2 = ProceduralLinear(hidden_dim, dim, rank=rank, seed_dim=seed_dim, basis_dim=basis_dim)

    def _surprise(self, h: torch.Tensor, prev_h: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        h_hat = prev_h * self.pred_scale + self.pred_bias
        surprise = torch.linalg.vector_norm(h - h_hat, dim=-1) / math.sqrt(self.dim)
        return h_hat, surprise

    def forward(self, h: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Sequence forward [B, T, dim] -> (delta, track_loss, deep_mask [B, T])."""
        prev_h = torch.zeros_like(h)
        prev_h[:, 1:, :] = h[:, :-1, :]
        h_hat, surprise = self._surprise(h, prev_h)
        track_loss = F.mse_loss(h_hat[:, 1:, :], h[:, 1:, :].detach())

        if self.tau <= 0.0:
            delta = self.fc2(F.silu(self.fc1(h)))
            deep_mask = torch.ones(h.shape[:2], dtype=torch.bool, device=h.device)
            return delta, track_loss, deep_mask

        fast_delta = h * self.fast_scale + self.fast_bias
        deep_mask = surprise >= self.tau
        out = fast_delta.clone()
        if bool(deep_mask.any().item()):
            h_deep = h[deep_mask]
            out[deep_mask] = self.fc2(F.silu(self.fc1(h_deep)))
        return out, track_loss, deep_mask

    def forward_step_batch1(self, h: torch.Tensor, prev_h: torch.Tensor) -> Tuple[torch.Tensor, bool]:
        """Hard-skip single-token step [1, dim]."""
        if self.tau <= 0.0:
            return self.fc2(F.silu(self.fc1(h))), False
        _, surprise = self._surprise(h, prev_h)
        if float(surprise.item()) < self.tau:
            return h * self.fast_scale + self.fast_bias, True
        return self.fc2(F.silu(self.fc1(h))), False


class CausalByteLM(nn.Module):
    """Minimal causal byte-level LM isolating FFN architecture."""

    def __init__(
        self,
        dim: int = 256,
        ffn_mult: int = 4,
        ffn_type: str = "dense",
        rank: int = 16,
        basis_dim: int = 8,
        tau: float = 0.0,
        kernel_size: int = 5,
    ) -> None:
        super().__init__()
        self.dim = dim
        self.kernel_size = kernel_size
        self.ffn_type = ffn_type
        self.emb = nn.Embedding(256, dim)
        self.mixer_norm = nn.LayerNorm(dim)
        # Causal depthwise + pointwise local context mixer
        self.dw_conv = nn.Conv1d(dim, dim, kernel_size=kernel_size, groups=dim)
        self.pw_proj = nn.Linear(dim, dim)

        self.ffn_norm = nn.LayerNorm(dim)
        hidden_dim = dim * ffn_mult
        if ffn_type == "dense":
            self.ffn: nn.Module = DenseBlock(dim=dim, hidden_dim=hidden_dim)
        else:
            self.ffn = ProceduralFFN(
                dim=dim,
                hidden_dim=hidden_dim,
                rank=rank,
                seed_dim=64,
                basis_dim=basis_dim,
                tau=tau,
            )
        self.out_norm = nn.LayerNorm(dim)

    def _causal_mix(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, T, dim]
        h = self.mixer_norm(x).transpose(1, 2)  # [B, dim, T]
        h = F.pad(h, (self.kernel_size - 1, 0))
        h = self.dw_conv(h).transpose(1, 2)
        return x + self.pw_proj(F.silu(h))

    def forward(self, tokens: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, float]:
        x = self.emb(tokens)
        x = self._causal_mix(x)
        h = self.ffn_norm(x)
        if isinstance(self.ffn, DenseBlock):
            delta = self.ffn(h)
            track_loss = torch.zeros((), device=tokens.device)
            skip_rate = 0.0
        else:
            delta, track_loss, deep_mask = self.ffn(h)
            skip_rate = float((~deep_mask).float().mean().item())
        x = x + delta
        logits = F.linear(self.out_norm(x), self.emb.weight)
        return logits, track_loss, skip_rate

    def benchmark_streaming_batch1(self, val_tokens: torch.Tensor, steps: int = 400) -> Tuple[float, float]:
        """Measure batch-1 streaming FFN + head step latency (ms/token) & skip rate."""
        self.eval()
        n = min(steps, len(val_tokens) - self.kernel_size - 1)
        with torch.inference_mode():
            # Precompute mixed hidden states for clean FFN streaming measurement
            seq = val_tokens[: n + self.kernel_size].unsqueeze(0)
            x_mixed = self._causal_mix(self.emb(seq))  # [1, T, dim]
            h_all = self.ffn_norm(x_mixed).squeeze(0)  # [T, dim]

            # Warmup
            prev_h = torch.zeros((1, self.dim))
            for t in range(min(20, n)):
                ht = h_all[t : t + 1]
                if isinstance(self.ffn, DenseBlock):
                    _ = self.ffn(ht)
                else:
                    _ = self.ffn.forward_step_batch1(ht, prev_h)
                prev_h = ht

            skips = 0
            prev_h = torch.zeros((1, self.dim))
            t0 = time.perf_counter()
            for t in range(n):
                ht = h_all[t : t + 1]
                if isinstance(self.ffn, DenseBlock):
                    _ = self.ffn(ht)
                else:
                    _, skipped = self.ffn.forward_step_batch1(ht, prev_h)
                    if skipped:
                        skips += 1
                prev_h = ht
            elapsed = time.perf_counter() - t0
        return (elapsed / max(n, 1)) * 1000.0, skips / float(max(n, 1))


@dataclass
class Stage3ModelResult:
    name: str
    ffn_params: int
    ffn_static_mb: float
    ffn_memory_reduction_x: float
    train_bpb_end: float
    val_bpb: float
    bpb_delta_vs_dense: float
    val_skip_rate: float
    ffn_ms_per_token: float
    ffn_speedup_vs_dense: float
    verdict: str


def _make_batches(data: torch.Tensor, seq_len: int, batch_size: int) -> List[Tuple[torch.Tensor, torch.Tensor]]:
    total_seqs = (len(data) - 1) // seq_len
    trimmed = data[: total_seqs * seq_len + 1]
    xs = trimmed[:-1].view(total_seqs, seq_len)
    ys = trimmed[1:].view(total_seqs, seq_len)
    batches: List[Tuple[torch.Tensor, torch.Tensor]] = []
    for i in range(0, total_seqs, batch_size):
        batches.append((xs[i : i + batch_size], ys[i : i + batch_size]))
    return batches


def train_and_eval_lm(
    name: str,
    model: CausalByteLM,
    train_tokens: torch.Tensor,
    val_tokens: torch.Tensor,
    epochs: int,
    seq_len: int,
    batch_size: int,
    lr: float,
    dense_ffn_bytes: Optional[int],
    dense_val_bpb: Optional[float],
    dense_ms: Optional[float],
    bigram_bpb: float,
    expect_skip: bool,
) -> Tuple[Stage3ModelResult, int, float, float]:
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    train_batches = _make_batches(train_tokens, seq_len=seq_len, batch_size=batch_size)
    val_batches = _make_batches(val_tokens, seq_len=seq_len, batch_size=batch_size)

    train_bpb_end = 0.0
    for _ in range(epochs):
        model.train()
        total_ce = 0.0
        for xb, yb in train_batches:
            opt.zero_grad(set_to_none=True)
            logits, track_loss, _ = model(xb)
            ce = F.cross_entropy(logits.reshape(-1, 256), yb.reshape(-1))
            loss = ce + 0.05 * track_loss
            loss.backward()
            opt.step()
            total_ce += float(ce.item())
        train_bpb_end = (total_ce / max(len(train_batches), 1)) / math.log(2.0)

    model.eval()
    val_ce = 0.0
    val_skips: List[float] = []
    with torch.inference_mode():
        for xb, yb in val_batches:
            logits, _, sk = model(xb)
            ce = F.cross_entropy(logits.reshape(-1, 256), yb.reshape(-1))
            val_ce += float(ce.item())
            val_skips.append(sk)
    val_bpb = (val_ce / max(len(val_batches), 1)) / math.log(2.0)
    val_skip = sum(val_skips) / max(len(val_skips), 1)

    ffn_params, ffn_bytes = static_footprint_bytes(model.ffn)
    ffn_mb = ffn_bytes / (1024.0 * 1024.0)
    ms_tok, _ = model.benchmark_streaming_batch1(val_tokens, steps=400)

    ref_bytes = dense_ffn_bytes if dense_ffn_bytes is not None else ffn_bytes
    ref_bpb = dense_val_bpb if dense_val_bpb is not None else val_bpb
    ref_ms = dense_ms if dense_ms is not None else ms_tok

    mem_red = ref_bytes / max(ffn_bytes, 1)
    bpb_delta = val_bpb - ref_bpb
    speedup = ref_ms / max(ms_tok, 1e-12)

    if dense_val_bpb is None:
        verdict = "BASELINE"
    elif not math.isfinite(val_bpb) or val_bpb >= bigram_bpb:
        verdict = "FAIL"
    elif bpb_delta <= 0.15 and mem_red >= 4.0 and (not expect_skip or val_skip >= 0.30):
        verdict = "PASS"
    else:
        verdict = "MIXED_SKIP_OR_CAPACITY"

    res = Stage3ModelResult(
        name=name,
        ffn_params=ffn_params,
        ffn_static_mb=round(ffn_mb, 4),
        ffn_memory_reduction_x=round(mem_red, 2),
        train_bpb_end=round(train_bpb_end, 4),
        val_bpb=round(val_bpb, 4),
        bpb_delta_vs_dense=round(bpb_delta, 4),
        val_skip_rate=round(val_skip, 4),
        ffn_ms_per_token=round(ms_tok, 4),
        ffn_speedup_vs_dense=round(speedup, 3),
        verdict=verdict,
    )
    return res, ffn_bytes, val_bpb, ms_tok


def run_stage3_lm(
    dim: int = 256,
    epochs: int = 10,
    seq_len: int = 64,
    batch_size: int = 32,
    lr: float = 3e-3,
    tau: float = 0.85,
    seed: int = 42,
) -> Dict[str, object]:
    train_bytes, val_bytes, train_sha, val_sha, n_files = load_repo_byte_corpus()
    bigram_bpb = empirical_bigram_bpb(train_bytes, val_bytes)

    train_tokens = torch.tensor(list(train_bytes), dtype=torch.long)
    val_tokens = torch.tensor(list(val_bytes), dtype=torch.long)

    # 1. Dense FFN baseline
    torch.manual_seed(seed)
    dense_lm = CausalByteLM(dim=dim, ffn_type="dense")
    dense_res, dense_bytes, dense_bpb, dense_ms = train_and_eval_lm(
        "DenseFFN-LM",
        dense_lm,
        train_tokens,
        val_tokens,
        epochs=epochs,
        seq_len=seq_len,
        batch_size=batch_size,
        lr=lr,
        dense_ffn_bytes=None,
        dense_val_bpb=None,
        dense_ms=None,
        bigram_bpb=bigram_bpb,
        expect_skip=False,
    )

    results = [dense_res]
    variants = [
        ("ProtoFFN-Deep(r=16,b=8)", 16, 8, 0.0, False),
        ("ProtoFFN-Event(r=16,b=8)", 16, 8, tau, True),
        ("ProtoFFN-Event(r=32,b=16)", 32, 16, tau, True),
    ]
    for name, rank, basis_dim, t_val, expect_skip in variants:
        torch.manual_seed(seed)
        lm = CausalByteLM(
            dim=dim, ffn_type="procedural", rank=rank, basis_dim=basis_dim, tau=t_val
        )
        res, _, _, _ = train_and_eval_lm(
            name,
            lm,
            train_tokens,
            val_tokens,
            epochs=epochs,
            seq_len=seq_len,
            batch_size=batch_size,
            lr=lr,
            dense_ffn_bytes=dense_bytes,
            dense_val_bpb=dense_bpb,
            dense_ms=dense_ms,
            bigram_bpb=bigram_bpb,
            expect_skip=expect_skip,
        )
        results.append(res)

    return {
        "corpus": {
            "files": n_files,
            "train_bytes": len(train_bytes),
            "val_bytes": len(val_bytes),
            "train_sha256_16": train_sha,
            "val_sha256_16": val_sha,
            "bigram_val_bpb": round(bigram_bpb, 4),
        },
        "config": {
            "dim": dim,
            "epochs": epochs,
            "seq_len": seq_len,
            "batch_size": batch_size,
            "lr": lr,
            "tau": tau,
            "seed": seed,
        },
        "results": [asdict(r) for r in results],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 3 Real-Data Byte-Level LM Benchmark")
    parser.add_argument("--dim", type=int, default=256)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--seq-len", type=int, default=64)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=3e-3)
    parser.add_argument("--tau", type=float, default=0.85)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    out = run_stage3_lm(
        dim=args.dim,
        epochs=args.epochs,
        seq_len=args.seq_len,
        batch_size=args.batch_size,
        lr=args.lr,
        tau=args.tau,
        seed=args.seed,
    )
    if args.json:
        print(json.dumps(out, indent=2))
        return

    c = out["corpus"]
    print(
        f"=== Stage 3 Real-Data Byte LM (files={c['files']}, train={c['train_bytes']}B [{c['train_sha256_16']}], "
        f"val={c['val_bytes']}B [{c['val_sha256_16']}], Bigram Val BPB={c['bigram_val_bpb']:.4f}) ==="
    )
    for r in out["results"]:
        print(
            f"{r['name']:26s} | FFN={r['ffn_static_mb']:.4f}MB ({r['ffn_memory_reduction_x']:.2f}x) | "
            f"val_bpb={r['val_bpb']:.4f} ({r['bpb_delta_vs_dense']:+.4f} vs dense) | "
            f"skip={r['val_skip_rate']*100:.1f}% | ffn_ms={r['ffn_ms_per_token']:.4f} ({r['ffn_speedup_vs_dense']:.2f}x) | {r['verdict']}"
        )


if __name__ == "__main__":
    main()
