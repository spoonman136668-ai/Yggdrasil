"""Unit tests for Stage 5 learned router and uncertainty-gated Monarch FFN."""

from __future__ import annotations

import sys
from pathlib import Path

import torch
import torch.nn.functional as F

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.procedural_event_stage5_entropy_gate import Stage5ByteLM


def test_stage5_router_and_uncertainty_gates_train_and_calibrate() -> None:
    torch.manual_seed(0)
    xb = torch.randint(0, 256, (4, 24))
    yb = torch.randint(0, 256, (4, 24))

    for mode in ("router", "uncertainty"):
        lm = Stage5ByteLM(dim=64, n_heads=2, ffn_type=mode, n_blocks=8, hyper_hidden=16, target_skip_rate=0.50)
        lm.train()
        logits, aux_loss, _ = lm(xb, targets=yb)
        loss = F.cross_entropy(logits.reshape(-1, 256), yb.reshape(-1)) + 0.1 * aux_loss
        loss.backward()
        assert lm.ffn.gate_proj.weight.grad is not None
        assert float(lm.ffn.gate_proj.weight.grad.abs().sum().item()) > 0.0

        lm.calibrate_tau_on_train([(xb, yb)])
        lm.eval()
        with torch.inference_mode():
            _, _, skip_rate = lm(xb)
        assert 0.30 <= skip_rate <= 0.70, f"{mode} skip_rate out of range: {skip_rate}"
