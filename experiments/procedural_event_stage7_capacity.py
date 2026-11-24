"""Stage 7: isolated always-deep factor-generation ablation; byte LM comparison only."""
import argparse
import hashlib
import json
import math
import platform
import subprocess
import time
from pathlib import Path

import torch
from torch import nn
from torch.nn import functional as F
from experiments.procedural_event_proto import DenseBlock
from experiments.procedural_event_stage4_monarch import ProceduralMonarchLinear
from experiments.procedural_event_stage6b_qualification import (
    build_model, complete_batches, evaluate, matched_bigram,
)

ARMS = ("dense", "generated", "direct", "residual")
SEEDS = (43, 44, 45)
TRAIN_HASH = "ee346df1120165c816b99772f3230a09ada2d7883815c46ac12a0b26bbbfd616"
VAL_HASH = "4ce8d6a707dad6dd3135b784509c5046add37bbb7ba65124656e38e932030dab"
CORPUS = (
    ".github/PULL_REQUEST_TEMPLATE/research-contribution.md", "CONTRIBUTING_RESEARCH.md",
    "docs/research-executor-codex-free.md", "research/contrib/README.md",
    "research/fanout/README.md", "research/fanout/smoke_candidate.py",
    "research/portability/README.md", "scripts/build_code_atlas.py",
    "scripts/free_fanout_sidecar.py", "scripts/portable_checkpoint.py",
    "tests/test_code_atlas.py", "tests/test_free_fanout_sidecar.py",
    "tests/test_native_cells.py", "tests/test_native_cells_wilson.py",
    "tests/test_portable_checkpoint.py", "yggdrasil/public_causal_cells.py",
)


class DirectFactors(nn.Module):
    """Same raw factors, normalization, permutation and bias; no shared generator."""
    def __init__(self, p):
        super().__init__()
        for name in ("in_dim", "out_dim", "n_blocks", "b_in", "b_out"):
            setattr(self, name, getattr(p, name))
        with torch.no_grad():
            c = torch.cat((p.seed.expand(p.n_blocks, -1), p.block_emb), dim=-1)
            self.b1 = nn.Parameter(p.hyper_b1_fc2(F.silu(p.hyper_b1_fc1(c))).reshape(p.n_blocks, p.b_in, p.n_blocks).clone())
            self.b2 = nn.Parameter(p.hyper_b2_fc2(F.silu(p.hyper_b2_fc1(c))).reshape(p.n_blocks, p.n_blocks, p.b_out).clone())
        for name in ("scale_b1", "scale_b2", "bias"):
            setattr(self, name, nn.Parameter(getattr(p, name).detach().clone()))

    def synthesize_blocks(self):
        return tuple(b / (b.pow(2).mean(dim=(1, 2), keepdim=True).sqrt() + 1e-6) * s
                     for b, s in ((self.b1, self.scale_b1), (self.b2, self.scale_b2)))

    forward = ProceduralMonarchLinear.forward


class ResidualFactors(nn.Module):
    """Generated factors plus rank-four global correction, initially exactly zero."""
    def __init__(self, p):
        super().__init__()
        self.base = p
        self.in_dim, self.out_dim = p.in_dim, p.out_dim
        self.down = nn.Linear(self.in_dim, 4, bias=False)
        self.up = nn.Linear(4, self.out_dim, bias=False)
        nn.init.zeros_(self.up.weight)

    def forward(self, x):
        return self.base(x) + self.up(self.down(x))


class AlwaysFFN(DenseBlock):
    def __init__(self, p, arm):
        nn.Module.__init__(self)
        wrap = {"generated": lambda x: x, "direct": DirectFactors, "residual": ResidualFactors}[arm]
        self.fc1, self.fc2 = wrap(p.fc1), wrap(p.fc2)

    def forward(self, x):
        return self.fc2(F.silu(self.fc1(x)))


def model_for(arm, seed, dim=128, layers=4):
    if arm not in ARMS:
        raise ValueError(arm)
    m = build_model("dense" if arm == "dense" else "always", dim=dim, n_layers=layers, seed=seed, dropout=0.1)
    if arm != "dense":
        for layer in m.layers:
            layer.ffn = AlwaysFFN(layer.ffn, arm)
    return m


def corpus(root):
    raw = b"\n".join((root / p).read_bytes() for p in CORPUS)
    tr, va = raw[:78268], raw[78268:]
    if (len(raw), hashlib.sha256(tr).hexdigest(), hashlib.sha256(va).hexdigest()) != (97836, TRAIN_HASH, VAL_HASH):
        raise ValueError("frozen corpus mismatch")
    return tuple(torch.tensor(list(b), dtype=torch.long) for b in (tr, va))


@torch.inference_mode()
def ranks(m, arm):
    if arm == "dense":
        return []
    rows = []
    for layer in m.layers:
        for p in (layer.ffn.fc1, layer.ffn.fc2):
            eye = torch.eye(p.in_dim, dtype=next(p.parameters()).dtype)
            w = p(eye) - p(torch.zeros_like(eye))
            rows.append(int(torch.linalg.matrix_rank(w)))
    return rows


def classify(rows, bigram):
    if bigram.get("bytes") != 19567 or bigram.get("score_sha256") != "21147bac8b56f5b9a3a8a649fa6c3b7cde768b84d19144de74e7d05ed8353d4b" or not math.isfinite(bigram.get("bpb", float("nan"))):
        return "INVALID"
    if set(rows) != {str(s) for s in SEEDS}:
        return "INVALID"
    for group in rows.values():
        if set(group) != set(ARMS):
            return "INVALID"
        for arm, v in group.items():
            if (v["bytes"] != 19567 or v["score_sha256"] != bigram["score_sha256"]
                    or not math.isfinite(v["bpb"]) or any(v["per_layer_skip"])
                    or (arm != "dense" and (v["pre_rank"] != [128]*8 or v["post_rank"] != [128]*8))):
                return "INVALID"
        if group["dense"]["bpb"] >= bigram["bpb"]:
            return "INVALID"
    gains = {arm: [g["generated"]["bpb"]-g[arm]["bpb"] for g in rows.values()] for arm in ("direct", "residual")}
    good = [a for a, gs in gains.items() if min(gs) >= 0.10 and all(g[a]["bpb"] <= g["dense"]["bpb"]+0.15 and g["dense"]["ffn_bytes"] >= 4*g[a]["ffn_bytes"] for g in rows.values())]
    return "SCIENTIFIC_SUPPORTED" if good else ("MIXED" if any(min(gs) >= 0.10 for gs in gains.values()) else "SCIENTIFIC_NEGATIVE")


def run(root, progress=lambda _: None):
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    tr, va = corpus(root)
    tb, vb = complete_batches(tr, 64, 32), complete_batches(va, 64, 32)
    bigram = matched_bigram(tr, vb)
    if bigram["score_sha256"] != "21147bac8b56f5b9a3a8a649fa6c3b7cde768b84d19144de74e7d05ed8353d4b" or len(tb) != 40:
        raise ValueError("scoring or training batch identity mismatch")
    rows = {}
    for seed in SEEDS:
        group = rows[str(seed)] = {}
        for arm in ARMS:
            m = model_for(arm, seed)
            before = ranks(m, arm)
            torch.manual_seed(seed+10000)
            opt = torch.optim.AdamW(m.parameters(), lr=0.003, weight_decay=0.01)
            sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=20)
            t = time.perf_counter()
            train_bpb = []
            for _ in range(20):
                m.train()
                ce_sum, count = 0., 0
                for x, y in tb:
                    opt.zero_grad(set_to_none=True)
                    loss = F.cross_entropy(m(x)[0].reshape(-1,256), y.reshape(-1))
                    ce_sum += float(loss.detach()) * y.numel()
                    count += y.numel()
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(m.parameters(), 1.)
                    opt.step()
                sched.step()
                train_bpb.append(ce_sum/(count*math.log(2)))
            elapsed = time.perf_counter()-t
            v = evaluate(m, vb)
            v.update(pre_rank=before, post_rank=ranks(m, arm), ffn_bytes=m.total_ffn_footprint()[1], train_seconds=elapsed, train_bpb=train_bpb, updates=20*len(tb))
            group[arm] = v
            progress(rows)
            print(seed, arm, v, flush=True)
    return dict(schema="yggdrasil.stage7.capacity.v1", seeds=SEEDS, train_hash=TRAIN_HASH, val_hash=VAL_HASH,
                environment=dict(python=platform.python_version(), platform=platform.platform(), torch=torch.__version__, threads=1),
                metrics=rows, bigram=bigram, classification=classify(rows,bigram))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise SystemExit("refuse to overwrite primary evidence")
    # Read-only Git provenance, no checkout/ref mutation. Refuse dirty tracked source.
    root = Path(__file__).resolve().parents[1]
    git = lambda *a: subprocess.check_output(["git", "-C", str(root), *a], text=True).strip()
    if git("status", "--porcelain", "--untracked-files=no"):
        raise SystemExit("dirty tracked source")
    prereg = "research/contrib/chatgpt/stage7-capacity/prereg.json"
    git("cat-file", "-e", "HEAD:"+prereg)
    identity = dict(commit=git("rev-parse", "HEAD"), tree=git("rev-parse", "HEAD^{tree}"),
                    prereg_blob=git("rev-parse", "HEAD:"+prereg), source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    with args.out.open("x") as f:
        json.dump(dict(status="STARTED", identity=identity, metrics={}), f)
    def save(report):
        tmp = args.out.with_suffix(args.out.suffix+".tmp")
        tmp.write_text(json.dumps(dict(identity=identity, **report), indent=2)+"\n")
        tmp.replace(args.out)
    try:
        result = run(args.corpus_root, lambda rows: save(dict(status="IN_PROGRESS", metrics=rows)))
        save(dict(status="COMPLETED", **result))
    except BaseException as exc:
        previous = json.loads(args.out.read_text())
        previous.pop("identity", None)
        save(dict(previous, status="ABORTED_NO_REPLAY", error=type(exc).__name__))
        raise
