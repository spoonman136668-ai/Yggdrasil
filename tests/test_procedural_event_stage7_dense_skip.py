"""Unit tests for Stage 7 causal uncertainty skipping on DenseFFN-4L."""

from __future__ import annotations

import sys
from pathlib import Path

import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.procedural_event_stage7_dense_causal_skip import (
    build_dense_gated_model,
    calibrate_dense_causal,
)


def test_stage7_dense_gated_prefix_causality_and_calibration() -> None:
    torch.manual_seed(0)
    xb = torch.randint(0, 256, (4, 24))
    yb = torch.randint(0, 256, (4, 24))

    for arm in ("dense_causal", "dense_random"):
        m = build_dense_gated_model(arm, dim=64, n_layers=2, seed=7, dropout=0.0)
        if arm == "dense_causal":
            calibrate_dense_causal(m, [(xb, yb)])
        m.eval()
        with torch.inference_mode():
            full_logits, _, skips = m(xb)
            pref_logits, _, _ = m(xb[:, :12])
        assert torch.allclose(full_logits[:, :12], pref_logits, atol=1e-5)
        mean_skip = sum(skips) / len(skips)
        assert 0.30 <= mean_skip <= 0.70, f"{arm} skip out of range: {mean_skip}"
