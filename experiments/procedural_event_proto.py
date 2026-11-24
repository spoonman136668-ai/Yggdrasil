"""Isolated, exploratory batch-1 performance screen; no training/quality claim.

Frozen design (before any primary measurement): FP32, seed 1729, rank 16,
64-element seed, eight fixed coordinate features, tau=0.1 RMS residual,
shift probability 0.2, noise std 0.01, 32 warmup samples per arm,
single CPU intra/inter-op thread, 300 timed steps at CPU 1024/2048;
optional CUDA 2048/500. Dense and procedural FFNs use hidden width dim.
Each arm gets the exact same stream; no fitting or result-based tuning.
Primary gate at dim >=2048: dense/event mean latency >=2 and static
parameter+buffer bytes ratio >=5. Report always-deep and dense-gated
controls to isolate low rank versus gating. This is not a formal external
research contribution or a quality-matched test.
"""
import argparse
import hashlib
import json
import math
import platform
import time

import torch
from torch import nn

SEED = 1729
TAU = 0.1
RANK = 16
WARMUP = 32


class DenseBlock(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.fc1 = nn.Linear(dim, dim)
        self.fc2 = nn.Linear(dim, dim)

    def forward(self, x):
        return self.fc2(torch.nn.functional.silu(self.fc1(x)))


def basis(dim):
    # Fixed coordinate features, not learned dense weights.
    p = torch.linspace(-1.0, 1.0, dim)
    return torch.stack((torch.ones_like(p), p, p.square(),
                        p.pow(3), torch.sin(math.pi*p), torch.cos(math.pi*p),
                        torch.sin(2*math.pi*p), torch.cos(2*math.pi*p)), dim=1)


class ProceduralLinear(nn.Module):
    def __init__(self, in_dim, out_dim, rank=RANK, seed_dim=64):
        super().__init__()
        self.rank = rank
        self.seed = nn.Parameter(torch.randn(seed_dim) / math.sqrt(seed_dim))
        self.hyper = nn.Linear(seed_dim, 16*rank)
        self.bias = nn.Parameter(torch.zeros(out_dim))
        self.register_buffer("input_basis", basis(in_dim))
        self.register_buffer("output_basis", basis(out_dim))

    def factors(self):
        a, b = self.hyper(self.seed).reshape(2, 8, self.rank).unbind(0)
        u = (self.output_basis @ a) / math.sqrt(self.rank)
        v = (self.input_basis @ b) / math.sqrt(self.input_basis.shape[0])
        return u, v

    def forward(self, x):
        u, v = self.factors()
        return (x @ v) @ u.T + self.bias


class ProceduralBlock(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.fc1 = ProceduralLinear(dim, dim)
        self.fc2 = ProceduralLinear(dim, dim)

    def forward(self, x):
        return self.fc2(torch.nn.functional.silu(self.fc1(x)))


class EventDrivenProceduralBlock(nn.Module):
    def __init__(self, dim, tau=TAU, deep=None):
        super().__init__()
        self.dim = dim
        self.tau = tau
        self.pred_scale = nn.Parameter(torch.ones(dim))
        self.pred_bias = nn.Parameter(torch.zeros(dim))
        self.deep = ProceduralBlock(dim) if deep is None else deep
        self.reset()

    def reset(self):
        self.previous_x = None
        self.previous_y = None
        self.skips = 0
        self.deep_calls = 0

    def forward(self, x):
        if x.shape != (1, self.dim):
            raise ValueError("event gate supports exactly batch 1")
        # First sample must run deep. Later use the causal one-step
        # predictor and RMS-normalized residual; equality runs deep.
        skip = False
        if self.previous_x is not None:
            pred = self.pred_scale * self.previous_x + self.pred_bias
            surprise = torch.linalg.vector_norm(x - pred) / math.sqrt(self.dim)
            skip = bool(surprise < self.tau)
        if skip:
            self.skips += 1
            y = self.previous_y
        else:
            self.deep_calls += 1
            y = self.deep(x)
        self.previous_x = x.detach()
        self.previous_y = y.detach()
        return y


def stream(dim, steps, shift_prob=0.2):
    g = torch.Generator(device="cpu").manual_seed(SEED)
    state = torch.randn((1, dim), generator=g)
    samples = []
    for _ in range(steps):
        if torch.rand((), generator=g).item() < shift_prob:
            state = torch.randn((1, dim), generator=g)
        samples.append(state + 0.01*torch.randn((1, dim), generator=g))
    return torch.cat(samples).contiguous()


def static_bytes(model):
    return sum(t.numel()*t.element_size()
               for t in list(model.parameters()) + list(model.buffers()))


def parameter_bytes(model):
    return sum(t.numel()*t.element_size() for t in model.parameters())


def sync(device):
    if device.type == "cuda":
        torch.cuda.synchronize(device)


@torch.inference_mode()
def self_test():
    for dim in (1024, 2048):
        dense = DenseBlock(dim)
        event = EventDrivenProceduralBlock(dim)
        x = torch.zeros(1, dim)
        assert dense(x).shape == event(x).shape == (1, dim)
        assert event.deep_calls == 1 and event.skips == 0
        assert torch.equal(event(x), event.previous_y)
        assert event.skips == 1 and event.deep_calls == 1
        assert torch.isfinite(event(torch.ones_like(x))).all()
        assert event.deep_calls == 2 and event.skips == 1
        assert static_bytes(event) < static_bytes(dense)
        assert parameter_bytes(event) < parameter_bytes(dense)
    e = EventDrivenProceduralBlock(16, tau=0.0)
    e(torch.zeros(1, 16))
    e(torch.zeros(1, 16))
    assert e.deep_calls == 2 and e.skips == 0  # equality
    layer = ProceduralLinear(7, 11, rank=3)
    x = torch.randn(1, 7)
    u, v = layer.factors()
    # Dense materialization only in this small test oracle, never forward.
    assert torch.allclose(layer(x), x @ (u @ v.T).T + layer.bias,
                          atol=1e-5, rtol=1e-5)
    print("SELF_TEST_PASS: shapes, finite, both paths, equality, footprint, factor oracle")


@torch.inference_mode()
def measure(model, warm, samples, device):
    model.eval()
    for x in warm:
        model(x.unsqueeze(0))
    sync(device)
    if isinstance(model, EventDrivenProceduralBlock):
        model.reset()
    times = []
    for x in samples:
        start = time.perf_counter_ns()
        y = model(x.unsqueeze(0))
        sync(device)
        times.append((time.perf_counter_ns()-start)/1e6)
    assert torch.isfinite(y).all()
    mean = sum(times)/len(times)
    ordered = sorted(times)
    gated = isinstance(model, EventDrivenProceduralBlock)
    if gated:
        assert model.deep_calls + model.skips == len(samples)
    return dict(parameter_bytes=parameter_bytes(model),
                static_bytes=static_bytes(model),
                state_bytes=2*samples.shape[1]*samples.element_size() if gated else 0,
                ms_per_step=mean, steps_per_second=1000/mean,
                p50_ms=ordered[len(ordered)//2],
                p95_ms=ordered[math.ceil(0.95*len(ordered))-1],
                skip_rate=model.skips/len(samples) if gated else 0.0,
                deep_calls=model.deep_calls if gated else len(samples))


def benchmark(dim, steps, device):
    torch.manual_seed(SEED)
    cpu_stream = stream(dim, steps + WARMUP)
    digest = hashlib.sha256(cpu_stream.numpy().tobytes()).hexdigest()
    data = cpu_stream.to(device)
    warm, samples = data[:WARMUP], data[WARMUP:]
    results = {}
    factories = (
        ("dense", lambda: DenseBlock(dim)),
        ("procedural", lambda: ProceduralBlock(dim)),
        ("event", lambda: EventDrivenProceduralBlock(dim)),
        ("dense_gated", lambda: EventDrivenProceduralBlock(dim, deep=DenseBlock(dim))),
    )
    for name, factory in factories:
        torch.manual_seed(SEED)
        model = factory().to(device)
        results[name] = measure(model, warm, samples, device)
        del model
    dense, event = results["dense"], results["event"]
    speedup = dense["ms_per_step"]/event["ms_per_step"]
    compression = dense["static_bytes"]/event["static_bytes"]
    return dict(dim=dim, steps=steps, device=str(device),
                hardware=torch.cuda.get_device_name(device) if device.type == "cuda" else platform.processor(),
                os=platform.platform(), torch_version=torch.__version__,
                threads=torch.get_num_threads(), seed=SEED, tau=TAU, rank=RANK,
                shift_prob=0.2, warmup=WARMUP, stream_sha256=digest,
                arms=results, speedup=speedup, static_compression=compression,
                stage1_gate=("PASS" if speedup >= 2 and compression >= 5 else "FAIL")
                if dim >= 2048 else "NOT_PRIMARY",
                quality_matched=False)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    p.add_argument("--dim", type=int, default=1024)
    p.add_argument("--steps", type=int, default=300)
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.dim < 1 or args.steps < 1:
        p.error("positive dim and steps required")
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.manual_seed(SEED)
    if args.self_test:
        self_test()
        return
    if args.device == "cuda" and not torch.cuda.is_available():
        p.error("CUDA unavailable")
    print(json.dumps(benchmark(args.dim, args.steps, torch.device(args.device)),
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
