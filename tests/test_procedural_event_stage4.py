"""Unit tests for Stage 4 full-rank ProceduralMonarchLinear and eval-calibrated surprise gate."""

from __future__ import annotations

import sys
from pathlib import Path

import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.procedural_event_stage4_monarch import (
    ProceduralMonarchLinear,
    Stage4ByteLM,
)


def test_procedural_monarch_linear_is_full_rank() -> None:
    torch.manual_seed(0)
    dim = 64
    layer = ProceduralMonarchLinear(in_dim=dim, out_dim=dim, n_blocks=8, seed_dim=32, hyper_hidden=16, bias=False)
    # Probe the implicit linear map on identity basis to verify full matrix rank
    eye = torch.eye(dim)
    with torch.inference_mode():
        w_eff = layer(eye)
    rank = int(torch.linalg.matrix_rank(w_eff).item())
    assert rank == dim, f"Expected full rank {dim}, got {rank}"


def test_stage4_eval_calibration_prevents_skip_collapse() -> None:
    torch.manual_seed(0)
    lm = Stage4ByteLM(dim=64, n_heads=2, ffn_type="monarch", n_blocks=8, hyper_hidden=16, target_skip_rate=0.50)
    dummy_batches = [(torch.randint(0, 256, (8, 32)), torch.randint(0, 256, (8, 32))) for _ in range(4)]
    lm.calibrate_tau_on_train(dummy_batches)

    lm.eval()
    with torch.inference_mode():
        logits, _, skip_rate = lm(dummy_batches[0][0])
    assert logits.shape == (8, 32, 256)
    assert torch.isfinite(logits).all()
    assert 0.30 <= skip_rate <= 0.70, f"Skip rate collapsed: {skip_rate}"
