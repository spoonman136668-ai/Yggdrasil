"""Stage 2 diagnostic, frozen before primary execution; exploratory only.
Parent d5e8f1f3eb7cff5add50db26535d4a4da130b72b.
Hypothesis: fixed coordinate basis fails on unstructured transitions even
with more data; a matching structured teacher is a positive control.
Design: dim=128, seeds 1729/1730, train prefixes 1200/10000, independent
2000 validation samples, shift=.2, noise=.02, RMS gate=.1, 600 Adam
updates of batch 128, lr=.003, FP32 single-thread CPU. All learned arms
receive identical batches. No tuning, retries, official acceptance or
training-latency claims. Inference latency is not tested here.
Gate: each full-teacher large-data seed must achieve >=20% shift MSE
reduction vs persistence, <=1.15x best dense overall MSE and >=5x
static compression vs dense-gated. Otherwise retain the negative.
"""
import argparse
import hashlib
import json
import math
import platform
import time
import torch
from torch import nn

D = 128
SEEDS = (1729, 1730)
BUDGETS = (1200, 10000)
STEPS = 600
BATCH = 128
VAL = 2000
TAU = .1


def basis():
    p = torch.linspace(-1., 1., D)
    q = torch.stack((torch.ones_like(p), p, p**2, p**3,
                     torch.sin(math.pi*p), torch.cos(math.pi*p),
                     torch.sin(2*math.pi*p), torch.cos(2*math.pi*p)), 1)
    return torch.linalg.qr(q).Q


def data(seed, kind):
    g = torch.Generator().manual_seed(seed)
    q = basis()
    k = 8 if kind == "structured" else D
    a = torch.randn(k, k, generator=g) / math.sqrt(k)
    b = torch.randn(k, k, generator=g) / math.sqrt(k)
    scale = .8 + .15*torch.rand(D, generator=g)
    bias = .05*torch.randn(D, generator=g)

    def generate(n, offset):
        r = torch.Generator().manual_seed(seed + offset)
        shift = torch.rand(n, generator=r) < .2
        shift[0] = True
        states = torch.randn(n, D, generator=r)
        x = states[shift.long().cumsum(0)-1] + .01*torch.randn(n, D, generator=r)
        prev = torch.cat((torch.zeros_like(x[:1]), x[:-1]))
        observed = (x-prev).square().mean(1).sqrt() >= TAU
        z = x @ q if k == 8 else x
        residual = torch.nn.functional.silu(z @ a) @ b
        if k == 8:
            residual = residual @ q.T * math.sqrt(D/k)
        y = scale*x + bias + .7*shift[:, None]*residual
        y = y + .02*torch.randn(n, D, generator=r)
        return x, observed, y, shift

    return generate(max(BUDGETS), 10000), generate(VAL, 20000)


class Synth(nn.Module):
    def __init__(self, learned=False):
        super().__init__()
        self.seed = nn.Parameter(torch.randn(64)/8)
        self.hyper = nn.Linear(64, 2*8*16)
        if learned:
            self.left = nn.Parameter(torch.randn(D, 8)/math.sqrt(D))
            self.right = nn.Parameter(torch.randn(D, 8)/math.sqrt(D))
        else:
            self.register_buffer("left", basis())
            self.register_buffer("right", basis())
        self.bias = nn.Parameter(torch.zeros(D))

    def forward(self, x):
        a, b = self.hyper(self.seed).reshape(2, 8, 16).unbind()
        u, v = self.left @ a, self.right @ b
        return (x @ v) @ u.T / 4 + self.bias


class Predictor(nn.Module):
    def __init__(self, arm):
        super().__init__()
        self.arm = arm
        self.scale = nn.Parameter(torch.ones(D))
        self.bias = nn.Parameter(torch.zeros(D))
        if arm.startswith("dense"):
            self.deep = nn.Sequential(nn.Linear(D,D), nn.SiLU(), nn.Linear(D,D))
        elif arm.startswith("procedural") or arm == "learned_basis_gated":
            learned = arm == "learned_basis_gated"
            self.deep = nn.Sequential(Synth(learned), nn.SiLU(), Synth(learned))
        else:
            self.deep = None

    def forward(self, x, gate):
        y = x*self.scale + self.bias
        if self.deep is not None:
            residual = self.deep(x)
            y = y + (residual*gate[:,None] if self.arm.endswith("gated") else residual)
        return y


def size(model):
    return sum(t.numel()*t.element_size() for t in
               list(model.parameters())+list(model.buffers()))


@torch.no_grad()
def score(y, val):
    err = (y-val[2]).square().mean(1)
    return {"overall": float(err.mean()), "shift": float(err[val[3]].mean()),
            "predictable": float(err[~val[3]].mean())}


ARMS = ("diagonal", "dense_always", "dense_gated", "procedural_always",
        "procedural_gated", "learned_basis_gated")


def fit(arm, seed, train, val, n):
    torch.manual_seed(seed)
    model = Predictor(arm)
    opt = torch.optim.Adam(model.parameters(), lr=.003)
    r = torch.Generator().manual_seed(seed+30000)
    losses = []
    for _ in range(STEPS):
        ix = torch.randint(n, (BATCH,), generator=r)
        x, gate, y = (t[ix] for t in train[:3])
        loss = (model(x,gate)-y).square().mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
        losses.append(float(loss.detach()))
    with torch.no_grad():
        metrics = score(model(val[0], val[1]), val)
    return dict(**metrics, static_bytes=size(model),
                train_first_100=sum(losses[:100])/100,
                train_last_100=sum(losses[-100:])/100)


def self_test():
    train, val = data(SEEDS[0], "structured")
    assert train[0].shape == (10000,D) and val[0].shape == (VAL,D)
    assert not torch.equal(train[0][:VAL], val[0])
    for arm in ARMS:
        m = Predictor(arm)
        x = val[0][:4]
        gate = torch.zeros(4,dtype=torch.bool)
        y = m(x,gate)
        assert y.shape == x.shape and torch.isfinite(y).all()
        if arm.endswith("gated"):
            assert torch.equal(y,x*m.scale+m.bias)
        m(x,~gate).square().mean().backward()
        if arm.startswith("procedural"):
            assert m.deep[0].seed.grad.abs().sum() > 0
    assert size(Predictor("procedural_gated")) < size(Predictor("dense_gated"))
    print("SELF_TEST_PASS")


def run():
    start = time.perf_counter()
    rows = []
    for seed in SEEDS:
        for kind in ("structured","full"):
            train, val = data(seed,kind)
            for n in BUDGETS:
                arms = {"persistence": score(val[0],val)}
                for arm in ARMS:
                    arms[arm] = fit(arm,seed,train,val,n)
                p = arms["procedural_gated"]
                gain = 1-p["shift"]/arms["persistence"]["shift"]
                ratio = p["overall"]/min(arms["dense_always"]["overall"],arms["dense_gated"]["overall"])
                compression = arms["dense_gated"]["static_bytes"]/p["static_bytes"]
                rows.append(dict(seed=seed,teacher=kind,train_n=n,
                    val_shift_count=int(val[3].sum()),
                    gate_agreement=float((val[1]==val[3]).float().mean()),
                    val_sha256=hashlib.sha256(val[0].numpy().tobytes()+val[2].numpy().tobytes()).hexdigest(),
                    arms=arms,shift_gain=gain,dense_ratio=ratio,
                    compression=compression,gate_pass=bool(gain>=.2 and ratio<=1.15 and compression>=5)))
                print(f"finished {seed} {kind} {n}",flush=True,file=__import__("sys").stderr)
    return dict(dim=D,seeds=SEEDS,budgets=BUDGETS,updates=STEPS,batch=BATCH,
                validation=VAL,torch=torch.__version__,python=platform.python_version(),
                platform=platform.platform(),threads=torch.get_num_threads(),
                cuda=torch.cuda.is_available(),elapsed_seconds=time.perf_counter()-start,
                rows=rows,gate_pass=all(r["gate_pass"] for r in rows
                                        if r["teacher"]=="full" and r["train_n"]==10000))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test",action="store_true")
    args = parser.parse_args()
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.manual_seed(SEEDS[0])
    if args.self_test:
        self_test()
    else:
        print(json.dumps(run(),indent=2,sort_keys=True))
