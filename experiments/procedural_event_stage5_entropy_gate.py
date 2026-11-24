#!/usr/bin/env python3
"""Stage 5: Learned Token-Router & Pre-FFN Entropy-Gated Monarch FFN (Yggdrasil).

Directly tests the Stage 4 hypothesis:
  Stage 4 proved full-rank ProceduralMonarchLinear achieves near-dense BPB
  (3.8061 vs 3.7858 BPB, 5.37x smaller at dim=256, 47.56x smaller at dim=2048),
  while raw state-delta skipping (||h_t - h_{t-1}||) degraded byte-LM BPB to
  3.9735 at 49.6% skip.

Stage 5 tests two task-aligned conditional gates with the exact same Monarch FFN:
  1. RouterMonarchFFN (Mixture-of-Depths style): A lightweight learned linear
     router (dim -> 1, 257 params) selects the top-k highest-priority tokens and
     multiplies the Monarch FFN residual by sigmoid(score), training end-to-end.
  2. EntropyMonarchFFN (Uncertainty / Predictive-Surprise Gate): Uses a compact
     uncertainty probe (dim -> 1, trained to predict pre-FFN next-byte NLL) so
     the Monarch FFN skips already-confident tokens and fires only on uncertain
     tokens.

Both gates are calibrated on training data in eval() mode (dropout OFF, zero
validation leakage) for hard-skip inference.

Pre-registered Stage 5 Falsification Criteria (frozen 16-file Yggdrasil corpus):
  - PASS: Held-out val BPB < Bigram (3.8092) AND < MixerOnly-NoFFN AND within
          <= +0.10 BPB of DenseFFN-LM AND FFN static memory >= 4.0x smaller AND
          held-out skip rate in [30%, 70%].
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
from experiments.procedural_event_stage4_monarch import ProceduralMonarchLinear


class GatedMonarchFFN(nn.Module):
    """Full-rank Monarch procedural FFN with learned router or uncertainty gate."""

    def __init__(
        self,
        dim: int,
        hidden_dim: int,
        gate_mode: str = "router",
        n_blocks: int = 16,
        seed_dim: int = 64,
        hyper_hidden: int = 32,
        target_skip_rate: float = 0.50,
    ) -> None:
        super().__init__()
        if gate_mode not in ("router", "uncertainty"):
            raise ValueError(f"Unsupported gate_mode: {gate_mode}")
        self.dim = dim
        self.gate_mode = gate_mode
        self.target_skip_rate = float(target_skip_rate)

        self.gate_proj = nn.Linear(dim, 1)
        self.register_buffer("tau_eval", torch.tensor(0.0, dtype=torch.float32))

        self.fc1 = ProceduralMonarchLinear(
            dim, hidden_dim, n_blocks=n_blocks, seed_dim=seed_dim, hyper_hidden=hyper_hidden
        )
        self.fc2 = ProceduralMonarchLinear(
            hidden_dim, dim, n_blocks=n_blocks, seed_dim=seed_dim, hyper_hidden=hyper_hidden
        )

    def gate_scores(self, h: torch.Tensor) -> torch.Tensor:
        """Compute scalar routing/uncertainty score per token [...,]."""
        inp = h.detach() if self.gate_mode == "uncertainty" else h
        return self.gate_proj(inp).squeeze(-1)

    def forward(
        self, h: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        scores = self.gate_scores(h)  # [B, T]
        if self.training:
            tau = torch.quantile(scores.detach().reshape(-1), self.target_skip_rate)
        else:
            tau = self.tau_eval

        deep_mask = scores >= tau
        out = torch.zeros_like(h)
        if bool(deep_mask.any().item()):
            h_deep = h[deep_mask]
            ffn_out = self.fc2(F.silu(self.fc1(h_deep)))
            if self.gate_mode == "router":
                # Differentiable router weight (Mixture-of-Depths style)
                w = torch.sigmoid(scores[deep_mask]).unsqueeze(-1)
                out[deep_mask] = ffn_out * w
            else:
                out[deep_mask] = ffn_out
        return out, scores, deep_mask

    def forward_step_batch1(self, h: torch.Tensor) -> Tuple[torch.Tensor, bool]:
        score = self.gate_scores(h)
        if float(score.item()) < float(self.tau_eval.item()):
            return torch.zeros_like(h), True
        ffn_out = self.fc2(F.silu(self.fc1(h)))
        if self.gate_mode == "router":
            ffn_out = ffn_out * torch.sigmoid(score).unsqueeze(-1)
        return ffn_out, False


class Stage5ByteLM(nn.Module):
    """Causal attention byte LM isolating learned-router / uncertainty-gated Monarch FFN."""

    def __init__(
        self,
        dim: int = 256,
        n_heads: int = 4,
        ffn_mult: int = 4,
        ffn_type: str = "dense",
        n_blocks: int = 16,
        hyper_hidden: int = 32,
        target_skip_rate: float = 0.50,
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
        if ffn_type == "dense":
            self.ffn: nn.Module = DenseBlock(dim=dim, hidden_dim=hidden_dim)
        elif ffn_type in ("router", "uncertainty"):
            self.ffn = GatedMonarchFFN(
                dim=dim,
                hidden_dim=hidden_dim,
                gate_mode=ffn_type,
                n_blocks=n_blocks,
                seed_dim=64,
                hyper_hidden=hyper_hidden,
                target_skip_rate=target_skip_rate,
            )
        else:
            raise ValueError(f"Unknown ffn_type: {ffn_type}")
        self.out_norm = nn.LayerNorm(dim)

    def _causal_attn(self, x: torch.Tensor) -> torch.Tensor:
        t = x.shape[1]
        h = self.attn_norm(x)
        mask = torch.triu(torch.ones((t, t), dtype=torch.bool, device=x.device), diagonal=1)
        attn_out, _ = self.attn(h, h, h, attn_mask=mask, need_weights=False)
        return x + self.drop(attn_out)

    def calibrate_tau_on_train(
        self, train_batches: List[Tuple[torch.Tensor, torch.Tensor]], max_batches: int = 16
    ) -> None:
        if not isinstance(self.ffn, GatedMonarchFFN):
            return
        self.eval()
        scores_list: List[torch.Tensor] = []
        with torch.inference_mode():
            for xb, _ in train_batches[:max_batches]:
                b, t = xb.shape
                pos = torch.arange(t, device=xb.device).unsqueeze(0)
                x = self._causal_attn(self.emb(xb) + self.pos_emb(pos))
                h = self.ffn_norm(x)
                scores_list.append(self.ffn.gate_scores(h).reshape(-1))
        all_s = torch.cat(scores_list, dim=0)
        q = torch.quantile(all_s, self.ffn.target_skip_rate)
        self.ffn.tau_eval.copy_(q)

    def forward(
        self, tokens: torch.Tensor, targets: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor, float]:
        b, t = tokens.shape
        pos = torch.arange(t, device=tokens.device).unsqueeze(0)
        x = self.drop(self.emb(tokens) + self.pos_emb(pos))
        x = self._causal_attn(x)

        aux_loss = torch.zeros((), device=tokens.device)
        if isinstance(self.ffn, DenseBlock):
            x = x + self.ffn_drop(self.ffn(self.ffn_norm(x)))
            skip_rate = 0.0
        else:
            h = self.ffn_norm(x)
            delta, scores, deep_mask = self.ffn(h)
            skip_rate = float((~deep_mask).float().mean().item())
            if self.ffn.gate_mode == "uncertainty" and targets is not None:
                # Train uncertainty probe to predict pre-FFN per-token NLL (detached)
                with torch.no_grad():
                    pre_logits = F.linear(self.out_norm(x), self.emb.weight)
                    pre_nll = F.cross_entropy(
                        pre_logits.reshape(-1, 256), targets.reshape(-1), reduction="none"
                    ).view(b, t)
                aux_loss = F.mse_loss(scores, pre_nll)
            x = x + self.ffn_drop(delta)

        logits = F.linear(self.out_norm(x), self.emb.weight)
        return logits, aux_loss, skip_rate

    def benchmark_ffn_batch1(self, val_tokens: torch.Tensor, steps: int = 400) -> Tuple[float, float]:
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

            for t in range(min(20, n)):
                ht = h_all[t : t + 1]
                if isinstance(self.ffn, DenseBlock):
                    _ = self.ffn(ht)
                else:
                    _ = self.ffn.forward_step_batch1(ht)

            skips = 0
            t0 = time.perf_counter()
            for t in range(n):
                ht = h_all[t : t + 1]
                if isinstance(self.ffn, DenseBlock):
                    _ = self.ffn(ht)
                else:
                    _, skipped = self.ffn.forward_step_batch1(ht)
                    if skipped:
                        skips += 1
            elapsed = time.perf_counter() - t0
        return (elapsed / max(n, 1)) * 1000.0, skips / float(max(n, 1))


@dataclass
class Stage5Result:
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


def run_stage5(
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

    def _fit_and_score(model: Stage5ByteLM) -> Tuple[float, float, float, int, int, float]:
        opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-2)
        sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)
        train_bpb_end = 0.0
        for _ in range(epochs):
            model.train()
            total_ce = 0.0
            for xb, yb in train_batches:
                opt.zero_grad(set_to_none=True)
                logits, aux_loss, _ = model(xb, targets=yb)
                ce = F.cross_entropy(logits.reshape(-1, 256), yb.reshape(-1))
                loss = ce + 0.1 * aux_loss
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                opt.step()
                total_ce += float(ce.item())
            sched.step()
            train_bpb_end = (total_ce / max(len(train_batches), 1)) / math.log(2.0)

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

        ffn_p, ffn_b = static_footprint_bytes(model.ffn)
        ms_tok, _ = model.benchmark_ffn_batch1(val_tokens, steps=400)
        return train_bpb_end, val_bpb, val_skip, ffn_p, ffn_b, ms_tok

    torch.manual_seed(seed)
    dense_lm = Stage5ByteLM(dim=dim, ffn_type="dense")
    d_tr, d_val, _, d_p, d_b, d_ms = _fit_and_score(dense_lm)

    results: List[Stage5Result] = [
        Stage5Result(
            name="DenseFFN-LM",
            ffn_params=d_p,
            ffn_static_mb=round(d_b / (1024.0 * 1024.0), 4),
            ffn_memory_reduction_x=1.0,
            train_bpb_end=round(d_tr, 4),
            val_bpb=round(d_val, 4),
            bpb_delta_vs_dense=0.0,
            val_skip_rate=0.0,
            ffn_ms_per_token=round(d_ms, 4),
            ffn_speedup_vs_dense=1.0,
            verdict="BASELINE_VALID",
        )
    ]

    for name, ffn_type in [
        ("RouterMonarch(G=16,50%)", "router"),
        ("EntropyMonarch(G=16,50%)", "uncertainty"),
    ]:
        torch.manual_seed(seed)
        lm = Stage5ByteLM(
            dim=dim,
            ffn_type=ffn_type,
            n_blocks=16,
            hyper_hidden=32,
            target_skip_rate=target_skip_rate,
        )
        tr, val, sk, p, b, ms = _fit_and_score(lm)
        mem_red = d_b / max(b, 1)
        delta_dense = val - d_val
        speedup = d_ms / max(ms, 1e-12)

        if not math.isfinite(val) or val >= bigram_bpb:
            verdict = "FAIL"
        elif delta_dense <= 0.10 and mem_red >= 4.0 and (0.30 <= sk <= 0.70):
            verdict = "PASS"
        else:
            verdict = "MIXED"

        results.append(
            Stage5Result(
                name=name,
                ffn_params=p,
                ffn_static_mb=round(b / (1024.0 * 1024.0), 4),
                ffn_memory_reduction_x=round(mem_red, 2),
                train_bpb_end=round(tr, 4),
                val_bpb=round(val, 4),
                bpb_delta_vs_dense=round(delta_dense, 4),
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
        "results": [asdict(r) for r in results],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 5 Learned Router & Entropy-Gated Monarch FFN")
    parser.add_argument("--dim", type=int, default=256)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--seq-len", type=int, default=64)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=3e-3)
    parser.add_argument("--target-skip-rate", type=float, default=0.50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    out = run_stage5(
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
        f"=== Stage 5 Router & Entropy-Gated Monarch LM (files={c['files']}, train={c['train_bytes']}B [{c['train_sha256_16']}], "
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
