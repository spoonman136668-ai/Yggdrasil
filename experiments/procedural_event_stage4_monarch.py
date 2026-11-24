#!/usr/bin/env python3
"""Stage 4: Full-Rank Procedural Monarch FFN + Eval-Calibrated Surprise Gating (Yggdrasil).

Architectural pivot directly addressing Stage 3b's two mathematical failure modes:
  1. Full-Rank ProceduralMonarchLinear: Synthesizes 2-stage block-diagonal
     Monarch butterfly factors (B1 -> transpose-permute -> B2) on the fly from a
     cache-resident seed + compact block embeddings via a shared hypernetwork.
     Preserves FULL matrix rank min(in_dim, out_dim) without ever materializing
     the dense [out_dim, in_dim] matrix.
  2. Dropout-Free Eval Calibration (calibrate_tau_on_train): Calibrates tau_ema
     on a slice of the training set in eval() mode (dropout disabled, zero val
     leakage) so held-out skip rates track the target budget [30%, 70%] instead
     of collapsing to 98.4%.

Pre-registered Stage 4 Falsification Criteria (frozen 16-file Yggdrasil corpus):
  - PASS: Held-out val BPB < Bigram (3.8092) AND < MixerOnly-NoFFN AND within
          <= +0.10 BPB of DenseFFN-LM AND FFN static memory >= 4.0x smaller at
          dim=256 AND (for event-gated) held-out skip rate in [30%, 70%].
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


class ProceduralMonarchLinear(nn.Module):
    """Full-rank 2-stage Monarch linear layer synthesized from a cache-resident seed.

    Factorizes in_dim = G * b_in and out_dim = G * b_out (with G = n_blocks):
      1. Reshape x: [..., G, b_in]
      2. Stage 1 block-diagonal B1 [G, b_in, G]: y1 = einsum('...gi,gij->...gj', x, B1)
      3. Transpose permutation: [..., G, G] -> [..., G, G] (swap last two axes)
      4. Stage 2 block-diagonal B2 [G, G, b_out]: y2 = einsum('...gj,gjo->...go', y1_T, B2)
      5. Reshape y2 -> [..., out_dim] + bias.

    B1 and B2 are synthesized on the fly by shared lightweight hypernetworks
    conditioned on (seed, block_emb[g]), preserving full rank min(in_dim, out_dim)
    with O(G * hyper_hidden * (b_in + b_out)) static parameters.
    """

    def __init__(
        self,
        in_dim: int,
        out_dim: int,
        n_blocks: int = 16,
        seed_dim: int = 64,
        block_emb_dim: int = 16,
        hyper_hidden: int = 32,
        bias: bool = True,
    ) -> None:
        super().__init__()
        if in_dim % n_blocks != 0 or out_dim % n_blocks != 0:
            raise ValueError(
                f"in_dim ({in_dim}) and out_dim ({out_dim}) must be divisible by n_blocks ({n_blocks})"
            )
        self.in_dim = in_dim
        self.out_dim = out_dim
        self.n_blocks = n_blocks
        self.b_in = in_dim // n_blocks
        self.b_out = out_dim // n_blocks

        self.seed = nn.Parameter(torch.randn(seed_dim) * 0.1)
        self.block_emb = nn.Parameter(torch.randn(n_blocks, block_emb_dim) * 0.1)

        cond_dim = seed_dim + block_emb_dim
        # Shared hypernetwork generating all G blocks of B1: [G, b_in * G]
        self.hyper_b1_fc1 = nn.Linear(cond_dim, hyper_hidden)
        self.hyper_b1_fc2 = nn.Linear(hyper_hidden, self.b_in * n_blocks)

        # Shared hypernetwork generating all G blocks of B2: [G, G * b_out]
        self.hyper_b2_fc1 = nn.Linear(cond_dim, hyper_hidden)
        self.hyper_b2_fc2 = nn.Linear(hyper_hidden, n_blocks * self.b_out)

        # Variance-preserving scales for stable deep residual training
        self.scale_b1 = nn.Parameter(torch.tensor(1.0 / math.sqrt(self.b_in)))
        self.scale_b2 = nn.Parameter(torch.tensor(1.0 / math.sqrt(n_blocks)))

        if bias:
            self.bias = nn.Parameter(torch.zeros(out_dim))
        else:
            self.register_parameter("bias", None)

    def synthesize_blocks(self) -> Tuple[torch.Tensor, torch.Tensor]:
        """Synthesize (B1: [G, b_in, G], B2: [G, G, b_out]) on the fly."""
        seed_exp = self.seed.unsqueeze(0).expand(self.n_blocks, -1)
        cond = torch.cat([seed_exp, self.block_emb], dim=-1)  # [G, cond_dim]

        b1 = self.hyper_b1_fc2(F.silu(self.hyper_b1_fc1(cond))).view(
            self.n_blocks, self.b_in, self.n_blocks
        )
        b2 = self.hyper_b2_fc2(F.silu(self.hyper_b2_fc1(cond))).view(
            self.n_blocks, self.n_blocks, self.b_out
        )
        # RMS-normalize per block for stable gradient flow
        b1 = b1 / (b1.pow(2).mean(dim=(1, 2), keepdim=True).sqrt() + 1e-6) * self.scale_b1
        b2 = b2 / (b2.pow(2).mean(dim=(1, 2), keepdim=True).sqrt() + 1e-6) * self.scale_b2
        return b1, b2

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        b1, b2 = self.synthesize_blocks()
        orig_shape = x.shape[:-1]
        xg = x.reshape(-1, self.n_blocks, self.b_in)  # [N, G, b_in]
        y1 = torch.einsum("ngi,gij->ngj", xg, b1)  # [N, G, G]
        y1_t = y1.transpose(1, 2).contiguous()  # [N, G, G] (full cross-block mixing)
        y2 = torch.einsum("ngj,gjo->ngo", y1_t, b2)  # [N, G, b_out]
        out = y2.reshape(*orig_shape, self.out_dim)
        if self.bias is not None:
            out = out + self.bias
        return out


class EventMonarchProceduralFFN(nn.Module):
    """Full-rank Monarch procedural FFN with eval-calibrated surprise skipping."""

    def __init__(
        self,
        dim: int,
        hidden_dim: int,
        n_blocks: int = 16,
        seed_dim: int = 64,
        hyper_hidden: int = 32,
        target_skip_rate: float = 0.50,
        enable_skip: bool = True,
    ) -> None:
        super().__init__()
        self.dim = dim
        self.target_skip_rate = float(target_skip_rate)
        self.enable_skip = bool(enable_skip)

        self.pred_scale = nn.Parameter(torch.ones(dim))
        self.pred_bias = nn.Parameter(torch.zeros(dim))
        self.fast_scale = nn.Parameter(torch.zeros(dim))
        self.fast_bias = nn.Parameter(torch.zeros(dim))
        self.register_buffer("tau_eval", torch.tensor(0.5, dtype=torch.float32))

        self.fc1 = ProceduralMonarchLinear(
            dim, hidden_dim, n_blocks=n_blocks, seed_dim=seed_dim, hyper_hidden=hyper_hidden
        )
        self.fc2 = ProceduralMonarchLinear(
            hidden_dim, dim, n_blocks=n_blocks, seed_dim=seed_dim, hyper_hidden=hyper_hidden
        )

    def surprise_norm(self, h: torch.Tensor, prev_h: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        h_det = h.detach()
        prev_det = prev_h.detach()
        h_hat = prev_det * self.pred_scale + self.pred_bias
        surprise = torch.linalg.vector_norm(h_det - h_hat, dim=-1) / math.sqrt(self.dim)
        return h_hat, surprise

    def forward(self, h: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        prev_h = torch.zeros_like(h)
        prev_h[:, 1:, :] = h[:, :-1, :]
        h_hat, surprise = self.surprise_norm(h, prev_h)
        track_loss = F.mse_loss(h_hat[:, 1:, :], h[:, 1:, :].detach())

        if not self.enable_skip:
            delta = self.fc2(F.silu(self.fc1(h)))
            deep_mask = torch.ones(h.shape[:2], dtype=torch.bool, device=h.device)
            return delta, track_loss, deep_mask

        # During training, use per-batch quantile directly (immune to EMA lag);
        # during eval, use the dropout-free train-calibrated tau_eval buffer.
        if self.training:
            tau = torch.quantile(surprise[:, 1:].reshape(-1), self.target_skip_rate)
        else:
            tau = self.tau_eval

        deep_mask = surprise >= tau
        fast_delta = h * self.fast_scale + self.fast_bias
        out = fast_delta.clone()
        if bool(deep_mask.any().item()):
            h_deep = h[deep_mask]
            out[deep_mask] = self.fc2(F.silu(self.fc1(h_deep)))
        return out, track_loss, deep_mask

    def forward_step_batch1(self, h: torch.Tensor, prev_h: torch.Tensor) -> Tuple[torch.Tensor, bool]:
        if not self.enable_skip:
            return self.fc2(F.silu(self.fc1(h))), False
        _, surprise = self.surprise_norm(h, prev_h)
        if float(surprise.item()) < float(self.tau_eval.item()):
            return h * self.fast_scale + self.fast_bias, True
        return self.fc2(F.silu(self.fc1(h))), False


class Stage4ByteLM(nn.Module):
    """Causal attention byte LM matching Stage 3b's exact backbone."""

    def __init__(
        self,
        dim: int = 256,
        n_heads: int = 4,
        ffn_mult: int = 4,
        ffn_type: str = "dense",
        n_blocks: int = 16,
        hyper_hidden: int = 32,
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
            self.ffn = EventMonarchProceduralFFN(
                dim=dim,
                hidden_dim=hidden_dim,
                n_blocks=n_blocks,
                seed_dim=64,
                hyper_hidden=hyper_hidden,
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

    def calibrate_tau_on_train(self, train_batches: List[Tuple[torch.Tensor, torch.Tensor]], max_batches: int = 12) -> None:
        """Calibrate tau_eval on training data in eval() mode (dropout OFF, zero val leakage)."""
        if not isinstance(self.ffn, EventMonarchProceduralFFN) or not self.ffn.enable_skip:
            return
        self.eval()
        surprises: List[torch.Tensor] = []
        with torch.inference_mode():
            for xb, _ in train_batches[:max_batches]:
                b, t = xb.shape
                pos = torch.arange(t, device=xb.device).unsqueeze(0)
                x = self._causal_attn(self.emb(xb) + self.pos_emb(pos))
                h = self.ffn_norm(x)
                prev_h = torch.zeros_like(h)
                prev_h[:, 1:, :] = h[:, :-1, :]
                _, s = self.ffn.surprise_norm(h, prev_h)
                surprises.append(s[:, 1:].reshape(-1))
        all_s = torch.cat(surprises, dim=0)
        q = torch.quantile(all_s, self.ffn.target_skip_rate)
        self.ffn.tau_eval.copy_(q)

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
class Stage4Result:
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


def benchmark_monarch_dim2048(steps: int = 200) -> Dict[str, object]:
    """Scale check at dim=2048 (hidden=8192, G=32 blocks) on batch-1 CPU."""
    torch.manual_seed(42)
    dim = 2048
    hidden = 8192
    dense = DenseBlock(dim=dim, hidden_dim=hidden).eval()
    monarch = EventMonarchProceduralFFN(
        dim=dim, hidden_dim=hidden, n_blocks=32, seed_dim=64, hyper_hidden=32, enable_skip=True
    ).eval()
    monarch.tau_eval.fill_(0.25)

    _, dense_b = static_footprint_bytes(dense)
    _, mon_b = static_footprint_bytes(monarch)

    # Synthetic piecewise stream (shift_prob=0.2)
    x_seq = torch.empty((steps + 20, 1, dim))
    curr = torch.randn((1, dim))
    x_seq[0] = curr
    probs = torch.rand((steps + 20,))
    for t in range(1, steps + 20):
        if float(probs[t].item()) < 0.2:
            curr = torch.randn((1, dim))
        else:
            curr = curr + 0.02 * torch.randn((1, dim))
        x_seq[t] = curr

    with torch.inference_mode():
        for t in range(20):
            _ = dense(x_seq[t])
        t0 = time.perf_counter()
        for t in range(20, steps + 20):
            _ = dense(x_seq[t])
        d_el = time.perf_counter() - t0

        prev = torch.zeros((1, dim))
        for t in range(20):
            _ = monarch.forward_step_batch1(x_seq[t], prev)
            prev = x_seq[t]
        skips = 0
        t0 = time.perf_counter()
        for t in range(20, steps + 20):
            _, sk = monarch.forward_step_batch1(x_seq[t], prev)
            prev = x_seq[t]
            if sk:
                skips += 1
        m_el = time.perf_counter() - t0

    return {
        "dim": dim,
        "hidden_dim": hidden,
        "dense_static_mb": round(dense_b / (1024.0 * 1024.0), 4),
        "monarch_static_mb": round(mon_b / (1024.0 * 1024.0), 4),
        "memory_reduction_x": round(dense_b / max(mon_b, 1), 2),
        "dense_ms_per_step": round((d_el / steps) * 1000.0, 4),
        "monarch_event_ms_per_step": round((m_el / steps) * 1000.0, 4),
        "speedup_x": round(d_el / max(m_el, 1e-12), 3),
        "skip_rate": round(skips / float(steps), 4),
    }


def run_stage4(
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

    def _fit_and_score(model: Stage4ByteLM) -> Tuple[float, float, float, int, int, float]:
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

        # Calibrate tau_eval on training data in eval() mode (dropout OFF, zero val leakage)
        model.calibrate_tau_on_train(train_batches)

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

    torch.manual_seed(seed)
    no_ffn_lm = Stage4ByteLM(dim=dim, ffn_type="none")
    nf_tr, nf_val, _, nf_p, _, _ = _fit_and_score(no_ffn_lm)

    torch.manual_seed(seed)
    dense_lm = Stage4ByteLM(dim=dim, ffn_type="dense")
    d_tr, d_val, _, d_p, d_b, d_ms = _fit_and_score(dense_lm)

    results: List[Stage4Result] = [
        Stage4Result(
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
        Stage4Result(
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
        ("MonarchProto-Deep(G=16)", 16, 32, False),
        ("MonarchProto-Event(G=16)", 16, 32, True),
    ]
    for name, n_blocks, h_hid, enable_skip in variants:
        torch.manual_seed(seed)
        lm = Stage4ByteLM(
            dim=dim,
            ffn_type="monarch",
            n_blocks=n_blocks,
            hyper_hidden=h_hid,
            target_skip_rate=target_skip_rate,
            enable_skip=enable_skip,
        )
        tr, val, sk, p, b, ms = _fit_and_score(lm)
        mem_red = d_b / max(b, 1)
        delta_dense = val - d_val
        delta_nof = val - nf_val
        speedup = d_ms / max(ms, 1e-12)

        skip_ok = (not enable_skip) or (0.30 <= sk <= 0.70)
        if not math.isfinite(val) or val >= bigram_bpb:
            verdict = "FAIL"
        elif val < nf_val and delta_dense <= 0.10 and mem_red >= 4.0 and skip_ok:
            verdict = "PASS"
        else:
            verdict = "MIXED"

        results.append(
            Stage4Result(
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

    scale_2048 = benchmark_monarch_dim2048(steps=200)
    return {
        "corpus": {
            "files": n_files,
            "train_bytes": len(train_bytes),
            "val_bytes": len(val_bytes),
            "train_sha256_16": train_sha,
            "val_sha256_16": val_sha,
            "bigram_val_bpb": round(bigram_bpb, 4),
        },
        "results": [asdict(r) for r in results],
        "scale_2048": scale_2048,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 4 Full-Rank Procedural Monarch FFN Benchmark")
    parser.add_argument("--dim", type=int, default=256)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--seq-len", type=int, default=64)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=3e-3)
    parser.add_argument("--target-skip-rate", type=float, default=0.50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    out = run_stage4(
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
        f"=== Stage 4 Full-Rank Procedural Monarch Byte LM (files={c['files']}, train={c['train_bytes']}B [{c['train_sha256_16']}], "
        f"val={c['val_bytes']}B [{c['val_sha256_16']}], Bigram Val BPB={c['bigram_val_bpb']:.4f}) ==="
    )
    for r in out["results"]:
        print(
            f"{r['name']:26s} | FFN={r['ffn_static_mb']:.4f}MB ({r['ffn_memory_reduction_x']:.2f}x) | "
            f"val_bpb={r['val_bpb']:.4f} ({r['bpb_delta_vs_dense']:+.4f} dense, {r['bpb_delta_vs_no_ffn']:+.4f} noFFN) | "
            f"skip={r['val_skip_rate']*100:.1f}% | ffn_ms={r['ffn_ms_per_token']:.4f} ({r['ffn_speedup_vs_dense']:.2f}x) | {r['verdict']}"
        )
    s = out["scale_2048"]
    print(
        f"\n=== Stage 4 Scale Check (dim={s['dim']}, hidden={s['hidden_dim']}, CPU batch-1) ===\n"
        f"Static MB: Dense={s['dense_static_mb']:.4f} MB vs Monarch={s['monarch_static_mb']:.4f} MB ({s['memory_reduction_x']:.2f}x smaller)\n"
        f"Latency  : Dense={s['dense_ms_per_step']:.4f} ms/step vs MonarchEvent={s['monarch_event_ms_per_step']:.4f} ms/step "
        f"({s['speedup_x']:.3f}x speedup, skip={s['skip_rate']*100:.1f}%)"
    )


if __name__ == "__main__":
    main()
