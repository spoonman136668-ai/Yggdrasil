#!/usr/bin/env python3
"""Stage 7: Causal Uncertainty Skipping on DenseFFN-4L (Decoupling Gate from Compression).

Stage 6b (6d1302a) proved that causal between-epoch uncertainty skipping beat
both always-on Monarch (-0.0201 BPB) and random 50% skipping (-0.0423 BPB) at
54.4% skip, while Monarch's 5.17x compression left a +0.4134 BPB gap vs Dense.

Stage 7 decouples the two mechanisms by applying the EXACT same causal
between-epoch uncertainty gate (50% skip target, zero val leakage, FP64 scoring
over all 19,567 transitions) directly to DenseFFN-4L:
  1. dense_always:  Standard 4-layer DenseBlock FFN (0% skip baseline).
  2. dense_causal:  4-layer DenseBlock FFN + causal uncertainty gate (50% skip).
  3. dense_random:  4-layer DenseBlock FFN + stateless pseudorandom 50% skip control.

Pre-registered Stage 7 Falsification Criteria:
  - PASS: dense_causal beats dense_random on held-out FP64 BPB AND stays within
          <= +0.05 BPB of dense_always AND achieves mean skip rate in [40%, 65%].
  - MIXED: dense_causal beats dense_random and skips [40%, 65%], but trails
           dense_always by > +0.05 BPB.
  - FAIL: dense_causal fails to beat dense_random or collapses skip rate.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from experiments.procedural_event_proto import DenseBlock
from experiments.procedural_event_stage3_lm import _make_batches, load_repo_byte_corpus
from experiments.procedural_event_stage6_multilayer import MultiLayerByteLM
from experiments.procedural_event_stage6b_qualification import (
    complete_batches,
    evaluate,
    matched_bigram,
)


class CausalGatedDenseFFN(nn.Module):
    """Standard DenseBlock FFN wrapped with Stage 6b's causal uncertainty or random skip gate."""

    def __init__(
        self,
        dim: int,
        hidden_dim: int,
        target_skip_rate: float = 0.50,
        enable_skip: bool = True,
        random_seed: Optional[int] = None,
    ) -> None:
        super().__init__()
        self.dim = dim
        self.target_skip_rate = float(target_skip_rate)
        self.enable_skip = bool(enable_skip)
        self.random_seed = random_seed

        self.gate_proj = nn.Linear(dim, 1)
        self.register_buffer("tau_eval", torch.tensor(float("-inf"), dtype=torch.float32))
        self.dense = DenseBlock(dim=dim, hidden_dim=hidden_dim)

    def gate_scores(self, h: torch.Tensor) -> torch.Tensor:
        return self.gate_proj(h.detach()).squeeze(-1)

    def forward(self, h: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        scores = self.gate_scores(h)
        if not self.enable_skip:
            deep = torch.ones_like(scores, dtype=torch.bool)
        elif self.random_seed is not None:
            row = torch.arange(h.shape[0], device=h.device, dtype=torch.int64)[:, None]
            pos = torch.arange(h.shape[1], device=h.device, dtype=torch.int64)[None, :]
            key = (row * 0x1E3779B1 + pos + self.random_seed * 0x05EBCA6B) & 0xFFFFFFFF
            key = ((key ^ (key >> 16)) * 0x45D9F3B) & 0xFFFFFFFF
            key = ((key ^ (key >> 16)) * 0x45D9F3B) & 0xFFFFFFFF
            key = key ^ (key >> 16)
            deep = key >= int(self.target_skip_rate * (1 << 32))
        else:
            deep = scores >= self.tau_eval

        out = torch.zeros_like(h)
        if bool(deep.any().item()):
            out[deep] = self.dense(h[deep])
        return out, scores, deep


def build_dense_gated_model(
    arm: str,
    *,
    dim: int = 128,
    n_layers: int = 4,
    ffn_mult: int = 4,
    seed: int = 42,
    dropout: float = 0.1,
    target_skip_rate: float = 0.50,
) -> MultiLayerByteLM:
    if arm not in {"dense_always", "dense_causal", "dense_random"}:
        raise ValueError(f"Unknown arm: {arm}")
    torch.manual_seed(seed)
    model = MultiLayerByteLM(
        n_layers=n_layers, dim=dim, ffn_mult=ffn_mult, ffn_type="dense", dropout=dropout
    )
    for i, layer in enumerate(model.layers):
        orig_dense = layer.ffn
        gated = CausalGatedDenseFFN(
            dim=dim,
            hidden_dim=dim * ffn_mult,
            target_skip_rate=target_skip_rate,
            enable_skip=(arm != "dense_always"),
            random_seed=(seed + i) if arm == "dense_random" else None,
        )
        # Preserve exact identical initial DenseBlock weights across all 3 arms!
        gated.dense.load_state_dict(orig_dense.state_dict())
        layer.ffn = gated
    return model


@torch.inference_mode()
def calibrate_dense_causal(
    model: MultiLayerByteLM,
    train_batches: List[Tuple[torch.Tensor, torch.Tensor]],
    max_batches: int = 16,
) -> None:
    was_training = model.training
    model.eval()
    try:
        for layer_idx, layer in enumerate(model.layers):
            ffn = layer.ffn
            if not isinstance(ffn, CausalGatedDenseFFN) or not ffn.enable_skip or ffn.random_seed is not None:
                continue
            scores_list: List[torch.Tensor] = []
            for xb, _ in train_batches[:max_batches]:
                b, t = xb.shape
                pos = torch.arange(t, device=xb.device).unsqueeze(0)
                mask = torch.triu(torch.ones((t, t), dtype=torch.bool, device=xb.device), diagonal=1)
                x = model.emb(xb) + model.pos_emb(pos)
                for prev_idx in range(layer_idx):
                    x, _, _ = model.layers[prev_idx](x, mask, model.out_norm, model.emb.weight, None)
                h_attn = layer.attn_norm(x)
                attn_out, _ = layer.attn(h_attn, h_attn, h_attn, attn_mask=mask, need_weights=False)
                x_pre = x + attn_out
                scores_list.append(ffn.gate_scores(layer.ffn_norm(x_pre)).reshape(-1))
            all_s = torch.cat(scores_list, dim=0)
            q = torch.quantile(all_s, ffn.target_skip_rate)
            ffn.tau_eval.copy_(q)
    finally:
        model.train(was_training)


def run_stage7(
    dim: int = 128,
    n_layers: int = 4,
    ffn_mult: int = 4,
    epochs: int = 20,
    seq_len: int = 64,
    batch_size: int = 32,
    lr: float = 3e-3,
    target_skip_rate: float = 0.50,
    seed: int = 42,
    out_json: str | None = None,
) -> Dict[str, object]:
    train_bytes, val_bytes, train_sha, val_sha, n_files = load_repo_byte_corpus()
    train_tokens = torch.tensor(list(train_bytes), dtype=torch.long)
    val_tokens = torch.tensor(list(val_bytes), dtype=torch.long)

    train_batches = _make_batches(train_tokens, seq_len=seq_len, batch_size=batch_size)
    val_batches = complete_batches(val_tokens, seq_len=seq_len, batch_size=batch_size)
    bigram = matched_bigram(train_tokens, val_batches, alpha=0.1)

    arms = ("dense_always", "dense_causal", "dense_random")
    metrics: Dict[str, Dict[str, object]] = {}
    meta: Dict[str, Dict[str, object]] = {}

    for arm in arms:
        t0 = time.perf_counter()
        model = build_dense_gated_model(
            arm,
            dim=dim,
            n_layers=n_layers,
            ffn_mult=ffn_mult,
            seed=seed,
            dropout=0.1,
            target_skip_rate=target_skip_rate,
        )
        opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-2)
        sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)
        train_bpb_end = 0.0

        for ep in range(epochs):
            model.train()
            total_ce = 0.0
            for xb, yb in train_batches:
                opt.zero_grad(set_to_none=True)
                logits, aux, _ = model(xb, targets=yb)
                ce = F.cross_entropy(logits.reshape(-1, 256), yb.reshape(-1))
                loss = ce + (0.1 * aux if arm == "dense_causal" else 0.0)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                opt.step()
                total_ce += float(ce.item())
            sched.step()
            train_bpb_end = (total_ce / max(len(train_batches), 1)) / math.log(2.0)

            if arm == "dense_causal" and ep in (0, 4, 9, 14, epochs - 1):
                calibrate_dense_causal(model, train_batches)

        ev = evaluate(model, val_batches)
        elapsed = time.perf_counter() - t0
        mean_sk = sum(ev["per_layer_skip"]) / len(ev["per_layer_skip"])
        metrics[arm] = ev
        meta[arm] = {
            "train_bpb_end": round(train_bpb_end, 4),
            "mean_val_skip": round(mean_sk, 4),
            "elapsed_sec": round(elapsed, 2),
        }
        print(
            f"[{arm:12s}] bpb={ev['bpb']:.4f} | mean_skip={mean_sk*100:5.1f}% | "
            f"per_layer={[round(x, 3) for x in ev['per_layer_skip']]} | {elapsed:.1f}s",
            flush=True,
        )

    b_always = float(metrics["dense_always"]["bpb"])
    b_causal = float(metrics["dense_causal"]["bpb"])
    b_random = float(metrics["dense_random"]["bpb"])
    sk_causal = float(meta["dense_causal"]["mean_val_skip"])

    if b_causal < b_random and (0.40 <= sk_causal <= 0.65):
        verdict = "PASS" if (b_causal - b_always) <= 0.05 else "MIXED"
    else:
        verdict = "FAIL"

    report = {
        "schema": "yggdrasil.stage7-dense-causal-skip.v1",
        "corpus": {
            "files": n_files,
            "train_sha256_16": train_sha,
            "val_sha256_16": val_sha,
            "bigram_bpb": bigram["bpb"],
            "score_sha256": bigram["score_sha256"],
        },
        "metrics": metrics,
        "meta": meta,
        "deltas": {
            "causal_minus_always_bpb": round(b_causal - b_always, 4),
            "causal_minus_random_bpb": round(b_causal - b_random, 4),
        },
        "verdict": verdict,
    }
    if out_json:
        Path(out_json).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(
        f"\nStage 7 Verdict: {verdict} | causal-always={b_causal - b_always:+.4f} BPB | "
        f"causal-random={b_causal - b_random:+.4f} BPB | skip={sk_causal*100:.1f}%"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 7 Causal Uncertainty Skipping on DenseFFN-4L")
    parser.add_argument("--dim", type=int, default=128)
    parser.add_argument("--layers", type=int, default=4)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--out-json",
        type=str,
        default="experiments/procedural_event_stage7_dense_skip_results.json",
    )
    args = parser.parse_args()
    run_stage7(dim=args.dim, n_layers=args.layers, epochs=args.epochs, seed=args.seed, out_json=args.out_json)


if __name__ == "__main__":
    main()
