"""Unit tests for Stage 6 multi-layer Transformer Monarch and per-layer calibration."""

from __future__ import annotations

import sys
from pathlib import Path

import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.procedural_event_stage6_multilayer import MultiLayerByteLM


def test_stage6_multilayer_calibration_and_footprint() -> None:
    torch.manual_seed(0)
    dense = MultiLayerByteLM(n_layers=4, dim=128, ffn_type="dense")
    monarch = MultiLayerByteLM(
        n_layers=4, dim=128, ffn_type="monarch", n_blocks=8, hyper_hidden=16, target_skip_rate=0.50, enable_skip=True
    )
    _, d_bytes = dense.total_ffn_footprint()
    _, m_bytes = monarch.total_ffn_footprint()
    assert (d_bytes / m_bytes) >= 4.0

    xb = torch.randint(0, 256, (8, 32))
    yb = torch.randint(0, 256, (8, 32))
    monarch.calibrate_all_layers_on_train([(xb, yb)])

    monarch.eval()
    with torch.inference_mode():
        logits, _, skips = monarch(xb)
    assert logits.shape == (8, 32, 256)
    assert len(skips) == 4
    mean_skip = sum(skips) / 4.0
    assert 0.30 <= mean_skip <= 0.70, f"Mean skip out of range: {mean_skip}"
