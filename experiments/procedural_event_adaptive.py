"""Exploratory adaptive residual falsification; no official research acceptance.
Parent 9b143393a948439db022e581f914df938bb65752.
Freeze: seeds 1741/1742, D=128, synthetic structured/full teachers, 10000
training and 2000 independent validation rows, 900 Adam updates, batch 128,
lr .003, FP32 one CPU thread. All arms get identical training batches.
Grow 8->16->24 features at updates 300/600 iff training-only event MSE
exceeds 25% of persistence event MSE. SVD of training residual covariance
initializes added input directions; zero output makes growth function-preserving.
Random growth reuses the same schedule, with random directions. Fixed 8 and
24, dense gated/always, persistence and diagonal controls. No tuning/retries.
Full-teacher gate on BOTH seeds: >=20% shift gain vs persistence, <=1.15x
best dense overall error, >=5x static compression vs dense gated, and >=5%
shift improvement vs both fixed24 and matched random growth. No latency
or native learning claim. Compact direct factors replace the hypernetwork;
this tests adaptive residual capacity, not procedural weight synthesis itself.
"""
import argparse
import hashlib
import json
import math
import platform
import time
import torch
from torch import nn

D, N, V, STEPS, BATCH = 128, 10000, 2000, 900, 128
SEEDS = (1741, 1742)
ARMS = ("diagonal", "fixed8", "fixed24", "dense_gated", "dense_always",
        "adaptive", "random_growth")


def dataset(seed, teacher):
    g = torch.Generator().manual_seed(seed)
    k = 8 if teacher == "structured" else D
    q = torch.linalg.qr(torch.randn(D, k, generator=g)).Q
    a = torch.randn(k, k, generator=g)/math.sqrt(k)
    b = torch.randn(k, k, generator=g)/math.sqrt(k)
    scale = .8+.15*torch.rand(D, generator=g)
    bias = .05*torch.randn(D, generator=g)
    def sample(n, offset):
        r = torch.Generator().manual_seed(seed+offset)
        shift = torch.rand(n, generator=r)<.2
        shift[0] = True
        states = torch.randn(n, D, generator=r)
        x = states[shift.long().cumsum(0)-1]+.01*torch.randn(n,D,generator=r)
        prev = torch.cat((torch.zeros_like(x[:1]),x[:-1]))
        gate = (x-prev).square().mean(1).sqrt()>=.1
        z = x@q
        residual = torch.nn.functional.silu(z@a)@b@q.T*math.sqrt(D/k)
        y = scale*x+bias+.7*shift[:,None]*residual+.02*torch.randn(n,D,generator=r)
        return x,gate,y,shift
    return sample(N,10000),sample(V,20000)


class Block(nn.Module):
    def __init__(self, rank):
        super().__init__()
        self.a = nn.Linear(D,rank)
        self.b = nn.Linear(rank,D,bias=False)
    def forward(self,x):
        return self.b(torch.nn.functional.silu(self.a(x)))


class Model(nn.Module):
    def __init__(self, arm):
        super().__init__()
        self.arm = arm
        self.scale = nn.Parameter(torch.ones(D))
        self.bias = nn.Parameter(torch.zeros(D))
        self.blocks = nn.ModuleList()
        rank = 128 if arm.startswith("dense") else 24 if arm=="fixed24" else 8
        if arm!="diagonal":
            self.blocks.append(Block(rank))
    def forward(self,x,gate):
        y = self.scale*x+self.bias
        for block in self.blocks:
            r = block(x)
            y = y + (r if self.arm=="dense_always" else r*gate[:,None])
        return y
    @property
    def rank(self):
        return sum(b.a.out_features for b in self.blocks)
    @torch.no_grad()
    def grow(self,x,gate,y,directed):
        block = Block(8)
        if directed:
            xx = x[gate]
            err = (y-self(x,gate))[gate]
            u,_,_ = torch.linalg.svd(xx.T@err,full_matrices=False)
            block.a.weight.copy_(u[:,:8].T)
            block.a.bias.zero_()
        block.b.weight.zero_()
        self.blocks.append(block)


def size(m):
    return sum(p.numel()*p.element_size() for p in m.parameters())


@torch.no_grad()
def score(pred,data):
    e = (pred-data[2]).square().mean(1)
    return dict(overall=float(e.mean()),shift=float(e[data[3]].mean()),
                predictable=float(e[~data[3]].mean()))


def fit(arm,seed,train,val,schedule=()):
    start = time.perf_counter()
    torch.manual_seed(seed)
    m = Model(arm)
    opt = torch.optim.Adam(m.parameters(),lr=.003)
    rng = torch.Generator().manual_seed(seed+30000)
    probe = tuple(t[:1024] for t in train)
    px,pg,py,_ = probe
    base = float((px[pg]-py[pg]).square().mean())
    growth = []
    first,last = [],[]
    for i in range(STEPS):
        if i in (300,600):
            with torch.no_grad():
                ratio = float((m(px,pg)[pg]-py[pg]).square().mean())/base
                add = (arm=="adaptive" and ratio>.25) or (arm=="random_growth" and i in schedule)
                if add:
                    before = m(px,pg)
                    m.grow(px,pg,py,arm=="adaptive")
                    assert torch.equal(before,m(px,pg))
                    growth.append(i)
            # Reset at identical boundaries for every arm.
            opt = torch.optim.Adam(m.parameters(),lr=.003)
        ix = torch.randint(N,(BATCH,),generator=rng)
        x,g,y = (t[ix] for t in train[:3])
        loss = (m(x,g)-y).square().mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
        if i<100: first.append(float(loss.detach()))
        if i>=STEPS-100: last.append(float(loss.detach()))
    with torch.no_grad():
        metrics = score(m(val[0],val[1]),val)
    return dict(**metrics,rank=m.rank,static_bytes=size(m),growth=growth,
                first100=sum(first)/100,last100=sum(last)/100,
                train_seconds=time.perf_counter()-start)


def self_test():
    torch.manual_seed(1)
    x=torch.randn(32,D)
    g=torch.arange(32)%2==0
    y=torch.randn_like(x)
    m=Model("adaptive")
    before=m(x,g).detach()
    assert torch.equal(before[~g],x[~g])
    m.grow(x,g,y,True)
    assert m.rank==16 and torch.equal(before,m(x,g))
    m(x,g).square().mean().backward()
    assert m.blocks[-1].b.weight.grad.abs().sum()>0
    assert size(Model("dense_gated"))/size(Model("fixed24"))>=5
    print("SELF_TEST_PASS")


def run():
    rows=[]
    for seed in SEEDS:
        for teacher in ("structured","full"):
            train,val=dataset(seed,teacher)
            arms={"persistence":score(val[0],val)}
            for arm in ARMS:
                arms[arm]=fit(arm,seed,train,val,arms.get("adaptive",{}).get("growth",()))
            p=arms["adaptive"]
            gain=1-p["shift"]/arms["persistence"]["shift"]
            ratio=p["overall"]/min(arms["dense_gated"]["overall"],arms["dense_always"]["overall"])
            comp=arms["dense_gated"]["static_bytes"]/p["static_bytes"]
            controls={k:1-p["shift"]/arms[k]["shift"] for k in ("fixed24","random_growth")}
            rows.append(dict(seed=seed,teacher=teacher,arms=arms,shift_gain=gain,
                dense_ratio=ratio,compression=comp,control_gains=controls,
                gate_agreement=float((val[1]==val[3]).float().mean()),
                train_sha256=hashlib.sha256(train[0].numpy().tobytes()+train[2].numpy().tobytes()).hexdigest(),
                val_sha256=hashlib.sha256(val[0].numpy().tobytes()+val[2].numpy().tobytes()).hexdigest(),
                passed=bool(gain>=.2 and ratio<=1.15 and comp>=5 and min(controls.values())>=.05)))
            print(f"finished {seed} {teacher}",file=__import__("sys").stderr,flush=True)
    return dict(rows=rows,passed=all(r["passed"] for r in rows if r["teacher"]=="full"),
                seeds=SEEDS,steps=STEPS,batch=BATCH,train_n=N,val_n=V,
                torch=torch.__version__,platform=platform.platform(),python=platform.python_version(),
                threads=torch.get_num_threads(),cuda=torch.cuda.is_available())


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    if args.self_test: self_test()
    else: print(json.dumps(run(),indent=2,sort_keys=True))
