"""Engineering repair for Stage 6; original experiment remains unchanged.
No primary training run or scientific acceptance is performed by this module.
Calibrate on training data between epochs, not within the current forward pass.
"""
from __future__ import annotations

import hashlib
import math
import torch
from torch import nn
from torch.nn import functional as F
from experiments.procedural_event_proto import DenseBlock
from experiments.procedural_event_stage3_lm import _make_batches
from experiments.procedural_event_stage6_multilayer import (
    MultiLayerByteLM, MultiLayerMonarchFFN,
)


def rank_safe_blocks(dim, hidden, minimum=8):
    """Remove the structural G**2 rank ceiling; actual rank still needs audit."""
    if min(dim, hidden, minimum) < 1:
        raise ValueError("positive dimensions and block count required")
    for g in range(minimum, math.gcd(dim, hidden) + 1):
        if dim % g == hidden % g == 0 and g*g >= min(dim, hidden):
            return g
    raise ValueError("no rank-safe common block divisor")


class CausalMonarchFFN(MultiLayerMonarchFFN):
    def forward(self, h):
        scores = self.gate_scores(h)
        if not self.enable_skip:
            deep = torch.ones_like(scores, dtype=torch.bool)
        elif self.random_seed is not None:
            # Stateless pseudorandom, independent of input and sequence length.
            row = torch.arange(h.shape[0], device=h.device, dtype=torch.int64)[:, None]
            pos = torch.arange(h.shape[1], device=h.device, dtype=torch.int64)[None, :]
            key = (row*0x1e3779b1 + pos + self.random_seed*0x05ebca6b) & 0xffffffff
            key = ((key ^ (key >> 16))*0x45d9f3b) & 0xffffffff
            key = ((key ^ (key >> 16))*0x45d9f3b) & 0xffffffff
            key = key ^ (key >> 16)
            deep = key >= int(self.target_skip_rate * (1 << 32))
        else:
            # Fixed buffer in BOTH train and eval. -inf = all-deep warmup.
            deep = scores >= self.tau_eval
        out = torch.zeros_like(h)
        if bool(deep.any().item()):
            out[deep] = self.fc2(F.silu(self.fc1(h[deep])))
        return out, scores, deep

    def __init__(self, *args, random_seed=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.random_seed = random_seed
        self.tau_eval.fill_(float("-inf"))


class NoFFN(DenseBlock):
    """Zero residual with identical attention/backbone and no FFN weights."""
    def __init__(self):
        nn.Module.__init__(self)

    def forward(self, x):
        return torch.zeros_like(x)


def build_model(arm, *, dim=128, n_layers=4, ffn_mult=4, seed=42,
                dropout=0.1):
    if arm not in {"dense", "none", "always", "causal", "random"}:
        raise ValueError("unknown arm")
    # Isolate backbone initialization from the choice of FFN parameters.
    torch.manual_seed(seed)
    model = MultiLayerByteLM(n_layers=n_layers, dim=dim, ffn_mult=ffn_mult,
                             ffn_type="dense", dropout=dropout)
    if arm == "dense":
        return model
    g = rank_safe_blocks(dim, dim*ffn_mult)
    for i, layer in enumerate(model.layers):
        if arm == "none":
            layer.ffn = NoFFN()
        else:
            torch.manual_seed(seed + 1000 + i)
            layer.ffn = CausalMonarchFFN(
                dim, dim*ffn_mult, n_blocks=g, enable_skip=arm != "always",
                random_seed=seed+i if arm == "random" else None,
            )
    return model


def complete_batches(data, seq_len, batch_size):
    if data.ndim != 1 or len(data) < 2 or min(seq_len, batch_size) < 1:
        raise ValueError("invalid sequence or batch configuration")
    batches = _make_batches(data, seq_len, batch_size) if len(data) > seq_len else []
    n = sum(y.numel() for _, y in batches)
    if n < len(data)-1:
        batches.append((data[n:-1][None, :], data[n+1:][None, :]))
    assert sum(y.numel() for _, y in batches) == len(data)-1
    return batches


def score_identity(batches):
    digest = hashlib.sha256()
    for x, y in batches:
        for t in (x, y):
            t = t.detach().to(device="cpu", dtype=torch.int64).contiguous()
            digest.update(str(tuple(t.shape)).encode("ascii") + b"|")
            digest.update(t.numpy().astype("<i8", copy=False).tobytes())
    return digest.hexdigest()


@torch.inference_mode()
def rank_audit(model):
    results = []
    for i, layer in enumerate(model.layers):
        if not isinstance(layer.ffn, CausalMonarchFFN):
            continue
        for name in ("fc1", "fc2"):
            p = getattr(layer.ffn, name)
            w = p(torch.eye(p.in_dim, device=p.seed.device, dtype=p.seed.dtype))
            if p.bias is not None:
                w = w-p.bias
            results.append((i, name, int(torch.linalg.matrix_rank(w)), min(p.in_dim,p.out_dim)))
    return results


@torch.inference_mode()
def matched_bigram(train, batches, alpha=0.1):
    """Train on consecutive training bytes; score exactly the neural batch pairs."""
    tr = train.detach().to(device="cpu",dtype=torch.int64)
    if tr.ndim != 1 or len(tr) < 2 or alpha <= 0:
        raise ValueError("invalid training data or smoothing")
    counts = torch.bincount(tr[:-1]*256+tr[1:], minlength=65536).reshape(256,256).double()+alpha
    logp = torch.log2(counts/counts.sum(1,keepdim=True))
    total, count = 0., 0
    for x,y in batches:
        total -= float(logp[x.cpu(), y.cpu()].sum())
        count += y.numel()
    if not count:
        raise ValueError("empty evaluation")
    return dict(bpb=total/count, bytes=count, score_sha256=score_identity(batches))


@torch.inference_mode()
def evaluate(model, batches):
    """Evaluate every supplied transition; weight BPB/skip by actual byte count."""
    was_training = model.training
    model.eval()
    total, count, skips = 0., 0, None
    try:
        for x, y in batches:
            logits, _, rates = model(x)
            n = y.numel()
            total += float(F.cross_entropy(logits.reshape(-1, 256).double(), y.reshape(-1), reduction="sum"))
            if skips is None:
                skips = [0.]*len(rates)
            if len(rates) != len(skips):
                raise ValueError("inconsistent layer count")
            skips = [a+b*n for a,b in zip(skips, rates)]
            count += n
        if not count or not skips:
            raise ValueError("empty evaluation")
        return dict(bpb=total/(count*math.log(2)), bytes=count,
                    score_sha256=score_identity(batches), per_layer_skip=[x/count for x in skips])
    finally:
        model.train(was_training)


def prerequisite_check(metrics, bigram, expected_bytes, rank_verified):
    """Validity only, not a scientific verdict. All controls must be present."""
    required = {"dense", "none", "always", "causal", "random"}
    if not rank_verified or set(metrics) != required or not math.isfinite(bigram["bpb"]):
        return False
    if expected_bytes <= 0 or bigram["bytes"] != expected_bytes or any(
        m["bytes"] != expected_bytes or not math.isfinite(m["bpb"])
        or m["score_sha256"] != bigram["score_sha256"]
        for m in metrics.values()
    ):
        return False
    return metrics["dense"]["bpb"] < bigram["bpb"]
