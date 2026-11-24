#!/usr/bin/env python3
"""Primary training & qualification run for Stage 6b (d227815).

Trains all 5 matched arms from experiments/procedural_event_stage6b_qualification.py
(dense, none, always, causal, random) on the frozen 16-file Yggdrasil repo corpus
with rank-safe G=16 Monarch blocks (rank=128), between-epoch train-only calibration,
FP64 byte-weighted evaluation over all 19,567 validation transitions, post-training
rank audit, and fail-closed prerequisite_check.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import Dict, List

import torch
import torch.nn.functional as F

from experiments.procedural_event_stage3_lm import _make_batches, load_repo_byte_corpus
from experiments.procedural_event_stage6b_qualification import (
    build_model,
    complete_batches,
    evaluate,
    matched_bigram,
    prerequisite_check,
    rank_audit,
)


def run_primary(
    dim: int = 128,
    n_layers: int = 4,
    ffn_mult: int = 4,
    epochs: int = 20,
    seq_len: int = 64,
    batch_size: int = 32,
    lr: float = 3e-3,
    seed: int = 42,
    out_json: str | None = None,
) -> Dict[str, object]:
    train_bytes, val_bytes, train_sha, val_sha, n_files = load_repo_byte_corpus()
    train_tokens = torch.tensor(list(train_bytes), dtype=torch.long)
    val_tokens = torch.tensor(list(val_bytes), dtype=torch.long)

    train_batches = _make_batches(train_tokens, seq_len=seq_len, batch_size=batch_size)
    val_batches = complete_batches(val_tokens, seq_len=seq_len, batch_size=batch_size)
    expected_bytes = len(val_tokens) - 1
    bigram = matched_bigram(train_tokens, val_batches, alpha=0.1)

    arms = ("dense", "none", "always", "causal", "random")
    metrics: Dict[str, Dict[str, object]] = {}
    pre_ranks: Dict[str, List[List[int | str]]] = {}
    post_ranks: Dict[str, List[List[int | str]]] = {}
    train_meta: Dict[str, Dict[str, object]] = {}

    for arm in arms:
        t0 = time.perf_counter()
        model = build_model(arm, dim=dim, n_layers=n_layers, ffn_mult=ffn_mult, seed=seed, dropout=0.1)
        if arm in ("always", "causal", "random"):
            pre_ranks[arm] = [list(r) for r in rank_audit(model)]

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
                loss = ce + (0.1 * aux if arm == "causal" else 0.0)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                opt.step()
                total_ce += float(ce.item())
            sched.step()
            train_bpb_end = (total_ce / max(len(train_batches), 1)) / math.log(2.0)

            # Between-epoch train-only calibration (never inside forward).
            if arm == "causal" and ep in (0, 4, 9, 14, epochs - 1):
                model.calibrate_all_layers_on_train(train_batches)

        ev = evaluate(model, val_batches)
        ffn_p, ffn_b = model.total_ffn_footprint()
        elapsed = time.perf_counter() - t0

        if arm in ("always", "causal", "random"):
            post_ranks[arm] = [list(r) for r in rank_audit(model)]

        metrics[arm] = ev
        train_meta[arm] = {
            "ffn_params": ffn_p,
            "ffn_bytes": ffn_b,
            "train_bpb_end": round(train_bpb_end, 4),
            "elapsed_sec": round(elapsed, 2),
            "mean_val_skip": round(sum(ev["per_layer_skip"]) / len(ev["per_layer_skip"]), 4),
        }
        print(
            f"[{arm:6s}] bpb={ev['bpb']:.4f} | ffn_bytes={ffn_b:>7d} | "
            f"mean_skip={train_meta[arm]['mean_val_skip']*100:5.1f}% | "
            f"per_layer={[round(x, 3) for x in ev['per_layer_skip']]} | {elapsed:.1f}s",
            flush=True,
        )

    pre_rank_ok = all(
        all(r[2] == r[3] for r in rows) for rows in pre_ranks.values()
    )
    post_rank_ok = all(
        all(r[2] == r[3] for r in rows) for rows in post_ranks.values()
    )
    prereq_ok = prerequisite_check(metrics, bigram, expected_bytes, pre_rank_ok and post_rank_ok)

    report = {
        "schema": "yggdrasil.stage6b-primary-results.v1",
        "base_commit": "d227815a74ce27431ec7fba55f28410ed7c85343",
        "corpus": {
            "files": n_files,
            "train_bytes": len(train_bytes),
            "val_bytes": len(val_bytes),
            "expected_val_transitions": expected_bytes,
            "train_sha256_16": train_sha,
            "val_sha256_16": val_sha,
        },
        "config": {
            "dim": dim,
            "n_layers": n_layers,
            "ffn_mult": ffn_mult,
            "epochs": epochs,
            "seq_len": seq_len,
            "batch_size": batch_size,
            "lr": lr,
            "seed": seed,
        },
        "bigram": bigram,
        "metrics": metrics,
        "train_meta": train_meta,
        "rank_audit": {
            "pre_training_full_rank": pre_rank_ok,
            "post_training_full_rank": post_rank_ok,
            "pre": pre_ranks,
            "post": post_ranks,
        },
        "prerequisite_check": prereq_ok,
    }

    if out_json:
        Path(out_json).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(
        f"\nBigram BPB={bigram['bpb']:.4f} (bytes={bigram['bytes']}, sha={bigram['score_sha256'][:16]})"
    )
    print(
        f"Rank Audit: pre_full_rank={pre_rank_ok} | post_full_rank={post_rank_ok} | prerequisite_check={prereq_ok}"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Stage 6b 5-arm primary qualification training")
    parser.add_argument("--dim", type=int, default=128)
    parser.add_argument("--layers", type=int, default=4)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--seq-len", type=int, default=64)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=3e-3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--out-json",
        type=str,
        default="experiments/procedural_event_stage6b_primary_results.json",
    )
    args = parser.parse_args()
    run_primary(
        dim=args.dim,
        n_layers=args.layers,
        epochs=args.epochs,
        seq_len=args.seq_len,
        batch_size=args.batch_size,
        lr=args.lr,
        seed=args.seed,
        out_json=args.out_json,
    )


if __name__ == "__main__":
    main()
