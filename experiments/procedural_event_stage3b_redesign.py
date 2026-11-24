#!/usr/bin/env python3
"""Stage 3b: Redesign & Re-Falsification on Real Byte-Level LM (Yggdrasil).

Addresses the three root causes diagnosed in Stage 3 (705a2b6):
  1. NormalizedProceduralLinear: L2-normalizes synthesized (u, v) factor columns
     with a learned per-rank gain to eliminate 3-factor multiplicative instability.
  2. BudgetedEventProceduralFFN: Replaces uncalibrated fixed tau with a frozen-eval
     EMA quantile threshold targeting a 50% active token budget (preventing 98%
     skip-collapse) and detaches hidden states from the tracker.
  3. Stronger Causal LM Backbone + MixerOnly-NoFFN Control: Adds causal
     self-attention + dropout + cosine schedule so DenseFFN-LM decisively beats
     both Empirical Bigram (3.8092 BPB) and MixerOnly-NoFFN.

Pre-registered Stage 3b Falsification Criteria:
  - Baseline Validity: DenseFFN-LM < Bigram BPB AND DenseFFN-LM < MixerOnly-NoFFN.
  - PASS: Held-out val BPB < Bigram BPB AND < MixerOnly-NoFFN AND within <= +0.15 BPB
          of DenseFFN-LM AND FFN static memory >= 4.0x smaller AND (for event-gated)
          real-text skip rate in [30%, 70%].
"""

from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from experiments.procedural_event_proto import DenseBlock, static_footprint_bytes
from experiments.procedural_event_stage3_lm import (
    _make_batches,
    empirical_bigram_bpb,
    load_repo_byte_corpus,
)


class NormalizedProceduralLinear(nn.Module):
    """Variance-stabilized procedural low-rank linear layer.

    Synthesizes (u: [out_dim, rank], v: [in_dim, rank]) from a cache-resident
    seed via a compact hypernetwork + learned projection bases, then column-
    normalizes (u, v) and scales by a learned per-rank gain `rank_gain`.
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

        self.seed = nn.Parameter(torch.randn(seed_dim) * 0.1)
        core_size = basis_dim * rank
        self.hyper_fc1 = nn.Linear(seed_dim, hyper_hidden)
        self.hyper_fc2 = nn.Linear(hyper_hidden, 2 * core_size)

        self.u_basis = nn.Parameter(torch.randn(out_dim, basis_dim) / math.sqrt(basis_dim))
        self.v_basis = nn.Parameter(torch.randn(in_dim, basis_dim) / math.sqrt(basis_dim))
        # Per-rank gain initialized so output variance matches standard linear init.
        self.rank_gain = nn.Parameter(torch.full((rank,), 1.0 / math.sqrt(rank)))

        if bias:
            self.bias = nn.Parameter(torch.zeros(out_dim))
        else:
            self.register_parameter("bias", None)

    def synthesize_factors(self) -> Tuple[torch.Tensor, torch.Tensor]:
        h = F.silu(self.hyper_fc1(self.seed))
        cores = self.hyper_fc2(h)
        core_size = self.basis_dim * self.rank
        u_core = cores[:core_size].view(self.basis_dim, self.rank)
        v_core = cores[core_size:].view(self.basis_dim, self.rank)

        u_raw = self.u_basis @ u_core  # [out_dim, rank]
        v_raw = self.v_basis @ v_core  # [in_dim, rank]
        # Column-wise unit-norm stabilization prevents 3-factor gradient blowup.
        u = F.normalize(u_raw, dim=0, eps=1e-6) * self.rank_gain.unsqueeze(0)
        v = F.normalize(v_raw, dim=0, eps=1e-6)
        return u, v

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        u, v = self.synthesize_factors()
        z = x @ v  # [..., rank]
        y = z @ u.transpose(0, 1)  # [..., out_dim]
        if self.bias is not None:
            y = y + self.bias
        return y


class BudgetedEventProceduralFFN(nn.Module):
    """Normalized procedural FFN with EMA-calibrated surprise budget (anti-collapse)."""

    def __init__(
        self,
        dim: int,
        hidden_dim: int,
        rank: int = 16,
        seed_dim: int = 64,
        basis_dim: int = 8,
        target_skip_rate: float = 0.50,
        enable_skip: bool = True,
        ema_momentum: float = 0.05,
    ) -> None:
        super().__init__()
        self.dim = dim
        self.target_skip_rate = float(target_skip_rate)
        self.enable_skip = bool(enable_skip)
        self.ema_momentum = float(ema_momentum)

        # Diagonal affine local state predictor (trained on detached h so LM cannot cheat).
        self.pred_scale = nn.Parameter(torch.ones(dim))
        self.pred_bias = nn.Parameter(torch.zeros(dim))
        self.fast_scale = nn.Parameter(torch.zeros(dim))
        self.fast_bias = nn.Parameter(torch.zeros(dim))

        # Calibrated threshold buffer (updated only during training via EMA quantile).
        self.register_buffer("tau_ema", torch.tensor(0.5, dtype=torch.float32))
        self.register_buffer("_tau_initialized", torch.tensor(False, dtype=torch.bool))

        self.fc1 = NormalizedProceduralLinear(
            dim, hidden_dim, rank=rank, seed_dim=seed_dim, basis_dim=basis_dim
        )
        self.fc2 = NormalizedProceduralLinear(
            hidden_dim, dim, rank=rank, seed_dim=seed_dim, basis_dim=basis_dim
        )

    def _surprise(self, h: torch.Tensor, prev_h: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        # Detach inputs for surprise prediction so main LM loss cannot collapse hidden states.
        h_det = h.detach()
        prev_det = prev_h.detach()
        h_hat = prev_det * self.pred_scale + self.pred_bias
        surprise = torch.linalg.vector_norm(h_det - h_hat, dim=-1) / math.sqrt(self.dim)
        return h_hat, surprise

    def forward(self, h: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        prev_h = torch.zeros_like(h)
        prev_h[:, 1:, :] = h[:, :-1, :]
        h_hat, surprise = self._surprise(h, prev_h)
        track_loss = F.mse_loss(h_hat[:, 1:, :], h[:, 1:, :].detach())

        if not self.enable_skip:
            delta = self.fc2(F.silu(self.fc1(h)))
            deep_mask = torch.ones(h.shape[:2], dtype=torch.bool, device=h.device)
            return delta, track_loss, deep_mask

        # Update calibrated EMA quantile threshold during training only.
        if self.training:
            with torch.no_grad():
                q_val = torch.quantile(surprise[:, 1:].reshape(-1), self.target_skip_rate)
                if not bool(self._tau_initialized.item()):
                    self.tau_ema.copy_(q_val)
                    self._tau_initialized.fill_(True)
                else:
                    self.tau_ema.mul_(1.0 - self.ema_momentum).add_(q_val * self.ema_momentum)

        deep_mask = surprise >= self.tau_ema
        fast_delta = h * self.fast_scale + self.fast_bias
        out = fast_delta.clone()
        if bool(deep_mask.any().item()):
            h_deep = h[deep_mask]
            out[deep_mask] = self.fc2(F.silu(self.fc1(h_deep)))
        return out, track_loss, deep_mask

    def forward_step_batch1(self, h: torch.Tensor, prev_h: torch.Tensor) -> Tuple[torch.Tensor, bool]:
        if not self.enable_skip:
            return self.fc2(F.silu(self.fc1(h))), False
        _, surprise = self._surprise(h, prev_h)
        if float(surprise.item()) < float(self.tau_ema.item()):
            return h * self.fast_scale + self.fast_bias, True
        return self.fc2(F.silu(self.fc1(h))), False


class CausalAttentionByteLM(nn.Module):
    """Compact causal Transformer-style byte LM isolating the FFN block."""

    def __init__(
        self,
        dim: int = 256,
        n_heads: int = 4,
        ffn_mult: int = 4,
        ffn_type: str = "dense",
        rank: int = 16,
        basis_dim: int = 8,
        target_skip_rate: float = 0.50,
        enable_skip: bool = True,
        dropout: float = 0.1,
        max_seq_len: int = 128,
    ) -> None:
        super().__init__()
        self.dim = dim
        self.ffn_type = ffn_type
        self.emb = nn.Embedding(256, dim)
        self.pos_emb = nn.Embedding(max_seq_len, dim)
        self.drop = nn.Dropout(dropout)

        self.attn_norm = nn.LayerNorm(dim)
        self.attn = nn.MultiheadAttention(dim, n_heads, dropout=dropout, batch_first=True)
        self.ffn_norm = nn.LayerNorm(dim)
        self.ffn_drop = nn.Dropout(dropout)

        hidden_dim = dim * ffn_mult
        if ffn_type == "none":
            self.ffn: Optional[nn.Module] = None
        elif ffn_type == "dense":
            self.ffn = DenseBlock(dim=dim, hidden_dim=hidden_dim)
        else:
            self.ffn = BudgetedEventProceduralFFN(
                dim=dim,
                hidden_dim=hidden_dim,
                rank=rank,
                seed_dim=64,
                basis_dim=basis_dim,
                target_skip_rate=target_skip_rate,
                enable_skip=enable_skip,
            )
        self.out_norm = nn.LayerNorm(dim)

    def _causal_attn(self, x: torch.Tensor) -> torch.Tensor:
        t = x.shape[1]
        h = self.attn_norm(x)
        mask = torch.triu(torch.ones((t, t), dtype=torch.bool, device=x.device), diagonal=1)
        attn_out, _ = self.attn(h, h, h, attn_mask=mask, need_weights=False)
        return x + self.drop(attn_out)

    def forward(self, tokens: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, float]:
        b, t = tokens.shape
        pos = torch.arange(t, device=tokens.device).unsqueeze(0)
        x = self.drop(self.emb(tokens) + self.pos_emb(pos))
        x = self._causal_attn(x)

        if self.ffn is None:
            track_loss = torch.zeros((), device=tokens.device)
            skip_rate = 1.0
        elif isinstance(self.ffn, DenseBlock):
            x = x + self.ffn_drop(self.ffn(self.ffn_norm(x)))
            track_loss = torch.zeros((), device=tokens.device)
            skip_rate = 0.0
        else:
            delta, track_loss, deep_mask = self.ffn(self.ffn_norm(x))
            x = x + self.ffn_drop(delta)
            skip_rate = float((~deep_mask).float().mean().item())

        logits = F.linear(self.out_norm(x), self.emb.weight)
        return logits, track_loss, skip_rate

    def benchmark_ffn_batch1(self, val_tokens: torch.Tensor, steps: int = 400) -> Tuple[float, float]:
        if self.ffn is None:
            return 0.0, 1.0
        self.eval()
        chunk = min(64, len(val_tokens))
        with torch.inference_mode():
            # Build realistic post-attention hidden states across non-overlapping chunks
            h_chunks: List[torch.Tensor] = []
            for start in range(0, min(len(val_tokens) - chunk, steps + 64), chunk):
                toks = val_tokens[start : start + chunk].unsqueeze(0)
                pos = torch.arange(chunk).unsqueeze(0)
                x = self._causal_attn(self.emb(toks) + self.pos_emb(pos))
                h_chunks.append(self.ffn_norm(x).squeeze(0))
            h_all = torch.cat(h_chunks, dim=0)
            n = min(steps, h_all.shape[0])

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
class Stage3bResult:
    name: str
    ffn_params: int
    ffn_static_mb: float
    ffn_memory_reduction_x: float
    train_bpb_end: float
    val_bpb: float
    bpb_delta_vs_dense: float
    bpb_delta_vs_no_ffn: float
    val_skip_rate: float
    ffn_ms_per_token: float
    ffn_speedup_vs_dense: float
    verdict: str


def run_stage3b(
    dim: int = 256,
    epochs: int = 20,
    seq_len: int = 64,
    batch_size: int = 32,
    lr: float = 3e-3,
    target_skip_rate: float = 0.50,
    seed: int = 42,
) -> Dict[str, object]:
    train_bytes, val_bytes, train_sha, val_sha, n_files = load_repo_byte_corpus()
    bigram_bpb = empirical_bigram_bpb(train_bytes, val_bytes)
    train_tokens = torch.tensor(list(train_bytes), dtype=torch.long)
    val_tokens = torch.tensor(list(val_bytes), dtype=torch.long)

    train_batches = _make_batches(train_tokens, seq_len=seq_len, batch_size=batch_size)
    val_batches = _make_batches(val_tokens, seq_len=seq_len, batch_size=batch_size)

    def _fit_and_score(
        name: str, model: CausalByteLM
    ) -> Tuple[float, float, float, int, int, float]:
        opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-2)
        sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)
        train_bpb_end = 0.0
        for _ in range(epochs):
            model.train()
            total_ce = 0.0
            for xb, yb in train_batches:
                opt.zero_grad(set_to_none=True)
                logits, track_loss, _ = model(xb)
                ce = F.cross_entropy(logits.reshape(-1, 256), yb.reshape(-1))
                loss = ce + 0.1 * track_loss
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                opt.step()
                total_ce += float(ce.item())
            sched.step()
            train_bpb_end = (total_ce / max(len(train_batches), 1)) / math.log(2.0)

        model.eval()
        val_ce = 0.0
        skips: List[float] = []
        with torch.inference_mode():
            for xb, yb in val_batches:
                logits, _, sk = model(xb)
                ce = F.cross_entropy(logits.reshape(-1, 256), yb.reshape(-1))
                val_ce += float(ce.item())
                skips.append(sk)
        val_bpb = (val_ce / max(len(val_batches), 1)) / math.log(2.0)
        val_skip = sum(skips) / max(len(skips), 1)

        if model.ffn is None:
            ffn_p, ffn_b = 0, 0
        else:
            ffn_p, ffn_b = static_footprint_bytes(model.ffn)
        ms_tok, _ = model.benchmark_ffn_batch1(val_tokens, steps=400)
        return train_bpb_end, val_bpb, val_skip, ffn_p, ffn_b, ms_tok

    # 1. MixerOnly-NoFFN ablation control
    torch.manual_seed(seed)
    no_ffn_lm = CausalAttentionByteLM(dim=dim, ffn_type="none")
    nf_tr, nf_val, nf_skip, nf_p, nf_b, nf_ms = _fit_and_score("MixerOnly-NoFFN", no_ffn_lm)

    # 2. DenseFFN-LM baseline
    torch.manual_seed(seed)
    dense_lm = CausalAttentionByteLM(dim=dim, ffn_type="dense")
    d_tr, d_val, d_skip, d_p, d_b, d_ms = _fit_and_score("DenseFFN-LM", dense_lm)

    results: List[Stage3bResult] = [
        Stage3bResult(
            name="MixerOnly-NoFFN",
            ffn_params=nf_p,
            ffn_static_mb=0.0,
            ffn_memory_reduction_x=0.0,
            train_bpb_end=round(nf_tr, 4),
            val_bpb=round(nf_val, 4),
            bpb_delta_vs_dense=round(nf_val - d_val, 4),
            bpb_delta_vs_no_ffn=0.0,
            val_skip_rate=1.0,
            ffn_ms_per_token=0.0,
            ffn_speedup_vs_dense=0.0,
            verdict="CONTROL_NO_FFN",
        ),
        Stage3bResult(
            name="DenseFFN-LM",
            ffn_params=d_p,
            ffn_static_mb=round(d_b / (1024.0 * 1024.0), 4),
            ffn_memory_reduction_x=1.0,
            train_bpb_end=round(d_tr, 4),
            val_bpb=round(d_val, 4),
            bpb_delta_vs_dense=0.0,
            bpb_delta_vs_no_ffn=round(d_val - nf_val, 4),
            val_skip_rate=0.0,
            ffn_ms_per_token=round(d_ms, 4),
            ffn_speedup_vs_dense=1.0,
            verdict="BASELINE_VALID" if (d_val < bigram_bpb and d_val < nf_val) else "BASELINE_WEAK",
        ),
    ]

    variants = [
        ("NormProto-Deep(r=16,b=8)", 16, 8, False),
        ("NormProto-Event(r=16,b=8)", 16, 8, True),
        ("NormProto-Event(r=32,b=16)", 32, 16, True),
    ]
    for name, rank, basis_dim, enable_skip in variants:
        torch.manual_seed(seed)
        lm = CausalAttentionByteLM(
            dim=dim,
            ffn_type="procedural",
            rank=rank,
            basis_dim=basis_dim,
            target_skip_rate=target_skip_rate,
            enable_skip=enable_skip,
        )
        tr, val, sk, p, b, ms = _fit_and_score(name, lm)
        mem_red = d_b / max(b, 1)
        delta_dense = val - d_val
        delta_nof = val - nf_val
        speedup = d_ms / max(ms, 1e-12)

        skip_ok = (not enable_skip) or (0.30 <= sk <= 0.70)
        if not math.isfinite(val) or val >= bigram_bpb:
            verdict = "FAIL"
        elif val < nf_val and delta_dense <= 0.15 and mem_red >= 4.0 and skip_ok:
            verdict = "PASS"
        else:
            verdict = "MIXED_SKIP_OR_CAPACITY"

        results.append(
            Stage3bResult(
                name=name,
                ffn_params=p,
                ffn_static_mb=round(b / (1024.0 * 1024.0), 4),
                ffn_memory_reduction_x=round(mem_red, 2),
                train_bpb_end=round(tr, 4),
                val_bpb=round(val, 4),
                bpb_delta_vs_dense=round(delta_dense, 4),
                bpb_delta_vs_no_ffn=round(delta_nof, 4),
                val_skip_rate=round(sk, 4),
                ffn_ms_per_token=round(ms, 4),
                ffn_speedup_vs_dense=round(speedup, 3),
                verdict=verdict,
            )
        )

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
            "target_skip_rate": target_skip_rate,
            "seed": seed,
        },
        "results": [asdict(r) for r in results],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 3b Redesigned Byte-Level LM Benchmark")
    parser.add_argument("--dim", type=int, default=256)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--seq-len", type=int, default=64)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=3e-3)
    parser.add_argument("--target-skip-rate", type=float, default=0.50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    out = run_stage3b(
        dim=args.dim,
        epochs=args.epochs,
        seq_len=args.seq_len,
        batch_size=args.batch_size,
        lr=args.lr,
        target_skip_rate=args.target_skip_rate,
        seed=args.seed,
    )
    if args.json:
        print(json.dumps(out, indent=2))
        return

    c = out["corpus"]
    print(
        f"=== Stage 3b Redesigned Real-Data Byte LM (files={c['files']}, train={c['train_bytes']}B [{c['train_sha256_16']}], "
        f"val={c['val_bytes']}B [{c['val_sha256_16']}], Bigram Val BPB={c['bigram_val_bpb']:.4f}) ==="
    )
    for r in out["results"]:
        print(
            f"{r['name']:26s} | FFN={r['ffn_static_mb']:.4f}MB ({r['ffn_memory_reduction_x']:.2f}x) | "
            f"val_bpb={r['val_bpb']:.4f} ({r['bpb_delta_vs_dense']:+.4f} dense, {r['bpb_delta_vs_no_ffn']:+.4f} noFFN) | "
            f"skip={r['val_skip_rate']*100:.1f}% | ffn_ms={r['ffn_ms_per_token']:.4f} ({r['ffn_speedup_vs_dense']:.2f}x) | {r['verdict']}"
        )


if __name__ == "__main__":
    main()
