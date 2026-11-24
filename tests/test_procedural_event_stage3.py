"""Unit tests for Stage 3 and Stage 3b real-data byte-level streaming LM benchmarks."""

from __future__ import annotations

import sys
from pathlib import Path

import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.procedural_event_stage3_lm import (
    CausalByteLM,
    empirical_bigram_bpb,
    load_repo_byte_corpus,
)
from experiments.procedural_event_stage3b_redesign import (
    CausalAttentionByteLM,
    NormalizedProceduralLinear,
)


def test_repo_corpus_loads_deterministically() -> None:
    tr1, va1, s1, v1, n1 = load_repo_byte_corpus()
    tr2, va2, s2, v2, n2 = load_repo_byte_corpus()
    assert n1 == n2 and n1 >= 5
    assert s1 == s2 and v1 == v2
    assert len(tr1) > len(va1) > 1000
    bpb = empirical_bigram_bpb(tr1, va1)
    assert 1.0 < bpb < 7.5


def test_causal_byte_lm_dense_and_procedural_shapes() -> None:
    torch.manual_seed(0)
    tokens = torch.randint(0, 256, (2, 16))
    for ffn_type, tau in (("dense", 0.0), ("procedural", 0.0), ("procedural", 0.85)):
        lm = CausalByteLM(dim=64, ffn_type=ffn_type, rank=8, basis_dim=4, tau=tau)
        logits, track_loss, skip_rate = lm(tokens)
        assert logits.shape == (2, 16, 256)
        assert torch.isfinite(logits).all()
        assert torch.isfinite(track_loss)
        assert 0.0 <= skip_rate <= 1.0


def test_stage3b_normalized_procedural_and_ema_budget_gate() -> None:
    torch.manual_seed(0)
    layer = NormalizedProceduralLinear(in_dim=64, out_dim=256, rank=8, seed_dim=32, basis_dim=4)
    u, v = layer.synthesize_factors()
    assert u.shape == (256, 8) and v.shape == (64, 8)
    # Columns of v should have unit L2 norm
    v_norms = torch.linalg.vector_norm(v, dim=0)
    assert torch.allclose(v_norms, torch.ones_like(v_norms), atol=1e-4)

    tokens = torch.randint(0, 256, (4, 24))
    lm = CausalAttentionByteLM(dim=64, n_heads=2, ffn_type="procedural", rank=8, basis_dim=4, target_skip_rate=0.5)
    lm.train()
    logits, track_loss, skip_rate = lm(tokens)
    assert logits.shape == (4, 24, 256)
    assert torch.isfinite(logits).all() and torch.isfinite(track_loss)
    # EMA quantile calibration should hold skip rate near 50% (not 0% or 98%)
    assert 0.25 <= skip_rate <= 0.75
