"""Unit and smoke tests for experiments/procedural_event_proto.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "experiments" / "procedural_event_proto.py"

spec = importlib.util.spec_from_file_location("procedural_event_proto", MODULE_PATH)
assert spec is not None and spec.loader is not None
proto_mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = proto_mod
spec.loader.exec_module(proto_mod)


def test_output_shapes_match_dense_block() -> None:
    torch.manual_seed(7)
    for dim in (64, 1024):
        dense = proto_mod.DenseBlock(dim=dim).eval()
        block = proto_mod.EventDrivenProceduralBlock(dim=dim, tau=0.25).eval()

        x0 = torch.randn(1, dim)
        x_low = x0 + 0.01 * torch.randn(1, dim)
        x_high = torch.randn(1, dim) * 2.0

        with torch.inference_mode():
            y_dense = dense(x0)
            y_skip, skipped_low, _ = block.forward_with_stats(x_low, prev_x=x0, update_state=False)
            y_deep, skipped_high, _ = block.forward_with_stats(x_high, prev_x=x0, update_state=False)

        assert y_skip.shape == y_dense.shape
        assert y_deep.shape == y_dense.shape
        assert torch.isfinite(y_skip).all()
        assert torch.isfinite(y_deep).all()
        assert skipped_low is True
        assert skipped_high is False


def test_skip_and_deep_path_execution_counting() -> None:
    torch.manual_seed(11)
    dim = 128
    block = proto_mod.EventDrivenProceduralBlock(dim=dim, tau=0.25).eval()

    deep_calls = 0
    orig_fc1_forward = block.fc1.forward

    def counted_fc1_forward(x: torch.Tensor) -> torch.Tensor:
        nonlocal deep_calls
        deep_calls += 1
        return orig_fc1_forward(x)

    block.fc1.forward = counted_fc1_forward  # type: ignore[method-assign]

    x0 = torch.randn(1, dim)
    x_predictable = x0 + 0.01 * torch.randn(1, dim)
    x_surprising = x0 + 1.5 * torch.randn(1, dim)

    with torch.inference_mode():
        _, skipped_1, surprise_1 = block.forward_with_stats(x_predictable, prev_x=x0, update_state=False)
        assert skipped_1 is True
        assert surprise_1 < block.tau
        assert deep_calls == 0

        _, skipped_2, surprise_2 = block.forward_with_stats(x_surprising, prev_x=x0, update_state=False)
        assert skipped_2 is False
        assert surprise_2 >= block.tau
        assert deep_calls == 1


def test_static_parameter_footprint_strictly_smaller_at_dim_ge_1024() -> None:
    for dim in (1024, 2048):
        dense = proto_mod.DenseBlock(dim=dim)
        block = proto_mod.EventDrivenProceduralBlock(dim=dim)

        dense_elems, dense_bytes = proto_mod.static_footprint_bytes(dense)
        proto_elems, proto_bytes = proto_mod.static_footprint_bytes(block)

        assert proto_elems < dense_elems
        assert proto_bytes < dense_bytes
        assert (dense_bytes / proto_bytes) >= 5.0


def test_procedural_linear_factors_and_shape() -> None:
    torch.manual_seed(3)
    layer = proto_mod.ProceduralLinear(in_dim=256, out_dim=512, rank=16, seed_dim=64, basis_dim=8)
    u, v = layer.synthesize_factors()
    assert u.shape == (512, 16)
    assert v.shape == (256, 16)
    x = torch.randn(1, 256)
    y = layer(x)
    assert y.shape == (1, 512)
    assert torch.isfinite(y).all()


def test_piecewise_stream_generator_shift_rate() -> None:
    stream, shifts = proto_mod.generate_piecewise_stream(steps=200, dim=32, shift_prob=0.2, seed=42)
    assert stream.shape == (200, 1, 32)
    assert 15 <= shifts <= 70
