#!/usr/bin/env python3
"""Stage 6: 4-Layer Transformer Stack — Multi-Layer Procedural Monarch & Entropy Skipping (Yggdrasil).

Tests the Stage 5 hypothesis:
  In Stage 5 (6f2f204), 50% FFN skipping in a 1-layer LM failed BPB parity
  (3.9216 vs 3.7858 BPB) because skipping the ONLY FFN starves >50% of tokens
  of all nonlinear FFN processing.

Stage 6 scales to a 4-layer causal Transformer stack (L=4, dim=128, hidden=512,
G=8 full-rank Monarch blocks, 5.6x smaller FFN weights) on the frozen 16-file
Yggdrasil repo corpus, comparing:
  1. DenseFFN-4L:           4-layer Transformer with static DenseBlock FFNs.
  2. MonarchProto-Deep-4L:  4-layer Transformer with full-rank ProceduralMonarchLinear (0% skip).
  3. EntropyMonarch-4L(50%): 4-layer Transformer with per-layer pre-FFN uncertainty
                             gating targeting 50% FFN skip per layer.

Pre-registered Stage 6 Falsification Criteria:
  - PASS: Held-out val BPB < Bigram (3.8092) AND within <= +0.10 BPB of DenseFFN-4L
          AND total FFN static memory >= 4.0x smaller AND (for EntropyMonarch-4L)
          mean stack skip rate in [35%, 65%].
"""

from __future__ import annotations

import argparse
import json
import math
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


class MultiLayerMonarchFFN(nn.Module):
    """Full-rank Monarch FFN with optional per-layer pre-FFN uncertainty skipping."""

    def __init__(
        self,
        dim: int,
        hidden_dim: int,
        n_blocks: int = 8,
        seed_dim: int = 32,
        block_emb_dim: int = 8,
        hyper_hidden: int = 16,
        target_skip_rate: float = 0.50,
        enable_skip: bool = True,
    ) -> None:
        super().__init__()
        self.dim = dim
        self.target_skip_rate = float(target_skip_rate)
        self.enable_skip = bool(enable_skip)

        self.gate_proj = nn.Linear(dim, 1)
        self.register_buffer("tau_eval", torch.tensor(0.0, dtype=torch.float32))

        self.fc1 = ProceduralMonarchLinear(
            dim,
            hidden_dim,
            n_blocks=n_blocks,
            seed_dim=seed_dim,
            block_emb_dim=block_emb_dim,
            hyper_hidden=hyper_hidden,
        )
        self.fc2 = ProceduralMonarchLinear(
            hidden_dim,
            dim,
            n_blocks=n_blocks,
            seed_dim=seed_dim,
            block_emb_dim=block_emb_dim,
            hyper_hidden=hyper_hidden,
        )

    def gate_scores(self, h: torch.Tensor) -> torch.Tensor:
        return self.gate_proj(h.detach()).squeeze(-1)

    def forward(self, h: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        scores = self.gate_scores(h)
        if not self.enable_skip:
            delta = self.fc2(F.silu(self.fc1(h)))
            deep_mask = torch.ones(h.shape[:2], dtype=torch.bool, device=h.device)
            return delta, scores, deep_mask

        tau = (
            torch.quantile(scores.detach().reshape(-1), self.target_skip_rate)
            if self.training
            else self.tau_eval
        )
        deep_mask = scores >= tau
        out = torch.zeros_like(h)
        if bool(deep_mask.any().item()):
            h_deep = h[deep_mask]
            out[deep_mask] = self.fc2(F.silu(self.fc1(h_deep)))
        return out, scores, deep_mask


class TransformerLayer(nn.Module):
    def __init__(
        self,
        dim: int,
        n_heads: int,
        ffn_mult: int,
        ffn_type: str,
        n_blocks: int,
        hyper_hidden: int,
        target_skip_rate: float,
        enable_skip: bool,
        dropout: float,
    ) -> None:
        super().__init__()
        self.attn_norm = nn.LayerNorm(dim)
        self.attn = nn.MultiheadAttention(dim, n_heads, dropout=dropout, batch_first=True)
        self.drop = nn.Dropout(dropout)
        self.ffn_norm = nn.LayerNorm(dim)
        self.ffn_drop = nn.Dropout(dropout)

        hidden_dim = dim * ffn_mult
        if ffn_type == "dense":
            self.ffn: nn.Module = DenseBlock(dim=dim, hidden_dim=hidden_dim)
        else:
            self.ffn = MultiLayerMonarchFFN(
                dim=dim,
                hidden_dim=hidden_dim,
                n_blocks=n_blocks,
                seed_dim=32,
                block_emb_dim=8,
                hyper_hidden=hyper_hidden,
                target_skip_rate=target_skip_rate,
                enable_skip=enable_skip,
            )

    def forward(
        self,
        x: torch.Tensor,
        causal_mask: torch.Tensor,
        out_norm: nn.LayerNorm,
        emb_weight: torch.Tensor,
        targets: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor, float]:
        h_attn = self.attn_norm(x)
        attn_out, _ = self.attn(h_attn, h_attn, h_attn, attn_mask=causal_mask, need_weights=False)
        x = x + self.drop(attn_out)

        aux_loss = torch.zeros((), device=x.device)
        if isinstance(self.ffn, DenseBlock):
            x = x + self.ffn_drop(self.ffn(self.ffn_norm(x)))
            skip_rate = 0.0
        else:
            h_ffn = self.ffn_norm(x)
            delta, scores, deep_mask = self.ffn(h_ffn)
            skip_rate = float((~deep_mask).float().mean().item())
            if self.ffn.enable_skip and targets is not None:
                with torch.no_grad():
                    pre_logits = F.linear(out_norm(x), emb_weight)
                    pre_nll = F.cross_entropy(
                        pre_logits.reshape(-1, 256), targets.reshape(-1), reduction="none"
                    ).view(x.shape[0], x.shape[1])
                aux_loss = F.mse_loss(scores, pre_nll)
            x = x + self.ffn_drop(delta)
        return x, aux_loss, skip_rate


class MultiLayerByteLM(nn.Module):
    def __init__(
        self,
        n_layers: int = 4,
        dim: int = 128,
        n_heads: int = 4,
        ffn_mult: int = 4,
        ffn_type: str = "dense",
        n_blocks: int = 8,
        hyper_hidden: int = 16,
        target_skip_rate: float = 0.50,
        enable_skip: bool = True,
        dropout: float = 0.1,
        max_seq_len: int = 128,
    ) -> None:
        super().__init__()
        self.dim = dim
        self.emb = nn.Embedding(256, dim)
        self.pos_emb = nn.Embedding(max_seq_len, dim)
        self.drop = nn.Dropout(dropout)
        self.layers = nn.ModuleList(
            [
                TransformerLayer(
                    dim=dim,
                    n_heads=n_heads,
                    ffn_mult=ffn_mult,
                    ffn_type=ffn_type,
                    n_blocks=n_blocks,
                    hyper_hidden=hyper_hidden,
                    target_skip_rate=target_skip_rate,
                    enable_skip=enable_skip,
                    dropout=dropout,
                )
                for _ in range(n_layers)
            ]
        )
        self.out_norm = nn.LayerNorm(dim)

    def calibrate_all_layers_on_train(
        self, train_batches: List[Tuple[torch.Tensor, torch.Tensor]], max_batches: int = 16
    ) -> None:
        """Sequentially calibrate each layer's tau_eval in eval() mode (zero val leakage)."""
        self.eval()
        with torch.inference_mode():
            for layer_idx, layer in enumerate(self.layers):
                if not isinstance(layer.ffn, MultiLayerMonarchFFN) or not layer.ffn.enable_skip:
                    continue
                scores_list: List[torch.Tensor] = []
                for xb, _ in train_batches[:max_batches]:
                    b, t = xb.shape
                    pos = torch.arange(t, device=xb.device).unsqueeze(0)
                    mask = torch.triu(torch.ones((t, t), dtype=torch.bool, device=xb.device), diagonal=1)
                    x = self.emb(xb) + self.pos_emb(pos)
                    for prev_idx in range(layer_idx):
                        x, _, _ = self.layers[prev_idx](x, mask, self.out_norm, self.emb.weight, None)
                    h_attn = layer.attn_norm(x)
                    attn_out, _ = layer.attn(h_attn, h_attn, h_attn, attn_mask=mask, need_weights=False)
                    x_pre = x + attn_out
                    scores_list.append(layer.ffn.gate_scores(layer.ffn_norm(x_pre)).reshape(-1))
                all_s = torch.cat(scores_list, dim=0)
                q = torch.quantile(all_s, layer.ffn.target_skip_rate)
                layer.ffn.tau_eval.copy_(q)

    def forward(
        self, tokens: torch.Tensor, targets: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor, List[float]]:
        b, t = tokens.shape
        pos = torch.arange(t, device=tokens.device).unsqueeze(0)
        mask = torch.triu(torch.ones((t, t), dtype=torch.bool, device=tokens.device), diagonal=1)
        x = self.drop(self.emb(tokens) + self.pos_emb(pos))

        total_aux = torch.zeros((), device=tokens.device)
        skips: List[float] = []
        for layer in self.layers:
            x, aux, sk = layer(x, mask, self.out_norm, self.emb.weight, targets=targets)
            total_aux = total_aux + aux
            skips.append(sk)

        logits = F.linear(self.out_norm(x), self.emb.weight)
        return logits, total_aux / float(len(self.layers)), skips

    def total_ffn_footprint(self) -> Tuple[int, int]:
        total_p = 0
        total_b = 0
        for layer in self.layers:
            p, b = static_footprint_bytes(layer.ffn)
            total_p += p
            total_b += b
        return total_p, total_b


@dataclass
class Stage6Result:
    name: str
    total_ffn_params: int
    total_ffn_static_mb: float
    ffn_memory_reduction_x: float
    train_bpb_end: float
    val_bpb: float
    bpb_delta_vs_dense: float
    mean_val_skip_rate: float
    per_layer_skip_rates: List[float]
    verdict: str


def run_stage6(
    n_layers: int = 4,
    dim: int = 128,
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

    def _fit_and_eval(model: MultiLayerByteLM) -> Tuple[float, float, List[float], int, int]:
        opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-2)
        sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)
        train_bpb_end = 0.0
        for _ in range(epochs):
            model.train()
            total_ce = 0.0
            for xb, yb in train_batches:
                opt.zero_grad(set_to_none=True)
                logits, aux, _ = model(xb, targets=yb)
                ce = F.cross_entropy(logits.reshape(-1, 256), yb.reshape(-1))
                loss = ce + 0.1 * aux
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                opt.step()
                total_ce += float(ce.item())
            sched.step()
            train_bpb_end = (total_ce / max(len(train_batches), 1)) / math.log(2.0)

        model.calibrate_all_layers_on_train(train_batches)

        model.eval()
        val_ce = 0.0
        layer_skips = [0.0 for _ in range(n_layers)]
        with torch.inference_mode():
            for xb, yb in val_batches:
                logits, _, sks = model(xb)
                ce = F.cross_entropy(logits.reshape(-1, 256), yb.reshape(-1))
                val_ce += float(ce.item())
                for idx, sk in enumerate(sks):
                    layer_skips[idx] += sk
        n_vb = max(len(val_batches), 1)
        val_bpb = (val_ce / n_vb) / math.log(2.0)
        layer_skips = [round(s / n_vb, 4) for s in layer_skips]
        ffn_p, ffn_b = model.total_ffn_footprint()
        return train_bpb_end, val_bpb, layer_skips, ffn_p, ffn_b

    torch.manual_seed(seed)
    dense_lm = MultiLayerByteLM(n_layers=n_layers, dim=dim, ffn_type="dense")
    d_tr, d_val, d_sks, d_p, d_b = _fit_and_eval(dense_lm)

    results: List[Stage6Result] = [
        Stage6Result(
            name=f"DenseFFN-{n_layers}L",
            total_ffn_params=d_p,
            total_ffn_static_mb=round(d_b / (1024.0 * 1024.0), 4),
            ffn_memory_reduction_x=1.0,
            train_bpb_end=round(d_tr, 4),
            val_bpb=round(d_val, 4),
            bpb_delta_vs_dense=0.0,
            mean_val_skip_rate=0.0,
            per_layer_skip_rates=d_sks,
            verdict="BASELINE_VALID" if d_val < bigram_bpb else "BASELINE_WEAK",
        )
    ]

    for name, enable_skip in [
        (f"MonarchProto-Deep-{n_layers}L", False),
        (f"EntropyMonarch-{n_layers}L(50%)", True),
    ]:
        torch.manual_seed(seed)
        lm = MultiLayerByteLM(
            n_layers=n_layers,
            dim=dim,
            ffn_type="monarch",
            n_blocks=8,
            hyper_hidden=16,
            target_skip_rate=target_skip_rate,
            enable_skip=enable_skip,
        )
        tr, val, sks, p, b = _fit_and_eval(lm)
        mean_sk = sum(sks) / max(len(sks), 1)
        mem_red = d_b / max(b, 1)
        delta_dense = val - d_val

        skip_ok = (not enable_skip) or (0.35 <= mean_sk <= 0.65)
        if not math.isfinite(val) or val >= bigram_bpb:
            verdict = "FAIL"
        elif delta_dense <= 0.10 and mem_red >= 4.0 and skip_ok:
            verdict = "PASS"
        else:
            verdict = "MIXED"

        results.append(
            Stage6Result(
                name=name,
                total_ffn_params=p,
                total_ffn_static_mb=round(b / (1024.0 * 1024.0), 4),
                ffn_memory_reduction_x=round(mem_red, 2),
                train_bpb_end=round(tr, 4),
                val_bpb=round(val, 4),
                bpb_delta_vs_dense=round(delta_dense, 4),
                mean_val_skip_rate=round(mean_sk, 4),
                per_layer_skip_rates=sks,
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
    parser = argparse.ArgumentParser(description="Stage 6 4-Layer Transformer Monarch & Entropy-Skip Test")
    parser.add_argument("--layers", type=int, default=4)
    parser.add_argument("--dim", type=int, default=128)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--seq-len", type=int, default=64)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=3e-3)
    parser.add_argument("--target-skip-rate", type=float, default=0.50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    out = run_stage6(
        n_layers=args.layers,
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
        f"=== Stage 6 {args.layers}-Layer Transformer Byte LM (dim={args.dim}, files={c['files']}, "
        f"Bigram Val BPB={c['bigram_val_bpb']:.4f}) ==="
    )
    for r in out["results"]:
        print(
            f"{r['name']:24s} | FFN={r['total_ffn_static_mb']:.4f}MB ({r['ffn_memory_reduction_x']:.2f}x) | "
            f"val_bpb={r['val_bpb']:.4f} ({r['bpb_delta_vs_dense']:+.4f} vs dense) | "
            f"mean_skip={r['mean_val_skip_rate']*100:.1f}% {r['per_layer_skip_rates']} | {r['verdict']}"
        )


if __name__ == "__main__":
    main()
