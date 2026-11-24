"""UJ-01C: bounded, externally scored corpus interface (DEV only)."""
import hashlib
import json
import math


SPLITS = ("train", "validation", "test")
DOMAINS = ("language", "math")


def _signal(value):
    if type(value) is not str:
        raise ValueError("signal must be text")
    raw = value.encode("utf-8")
    if not 1 <= len(raw) <= 256:
        raise ValueError("signal exceeds encoder bounds")
    return raw


def load_corpus(raw, expected_sha256):
    """Verify bytes before parsing; never download or discover data."""
    if type(raw) is not bytes or not 1 <= len(raw) <= 32 * 1024 * 1024:
        raise ValueError("invalid corpus size")
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ValueError("corpus digest mismatch")
    ids, groups, contexts, partitions = set(), {}, {}, {s: [] for s in SPLITS}
    for line in raw.splitlines():
        row = json.loads(line)
        if type(row) is not dict or set(row) != {
                "id", "group", "domain", "split", "context", "options", "answer"}:
            raise ValueError("invalid record fields")
        ident, group, domain, split = (row[k] for k in ("id", "group", "domain", "split"))
        if any(type(v) is not str or not v for v in (ident, group)):
            raise ValueError("invalid identity")
        if ident in ids or domain not in DOMAINS or split not in SPLITS:
            raise ValueError("duplicate identity or invalid partition")
        ids.add(ident)
        ctx = _signal(row["context"])
        opts = row["options"]
        if type(opts) is not list or not 2 <= len(opts) <= 16:
            raise ValueError("invalid options")
        opts = tuple(_signal(o) for o in opts)
        if len(set(opts)) != len(opts):
            raise ValueError("duplicate options")
        answer = row["answer"]
        if type(answer) is not int or not 0 <= answer < len(opts):
            raise ValueError("invalid answer")
        if groups.setdefault(group, split) != split or contexts.setdefault(ctx, split) != split:
            raise ValueError("cross-split group or exact context leakage")
        partitions[split].append((ident, domain, ctx, opts, answer))
    if any(not p for p in partitions.values()):
        raise ValueError("missing partition")
    return {s: tuple(p) for s, p in partitions.items()}


def probabilities(log_scores):
    scores = tuple(float(v) for v in log_scores)
    if not 2 <= len(scores) <= 16 or any(not math.isfinite(v) for v in scores):
        raise ValueError("invalid scores")
    peak = max(scores)
    weights = [math.exp(v - peak) for v in scores]
    total = sum(weights)
    return tuple(v / total for v in weights)


def evaluate(records, scorer):
    """Scorer sees context and alternatives, never answer, ID or domain."""
    totals = {}
    for _, domain, ctx, options, answer in records:
        p = probabilities(scorer(ctx, options))
        if len(p) != len(options):
            raise ValueError("wrong score count")
        maximum = max(p)
        winners = [i for i, v in enumerate(p) if v == maximum]
        correct = (1 / len(winners)) if answer in winners else 0.0
        # Half the multiclass Brier sum, bounded [0,1].
        brier = sum((v - (i == answer))**2 for i, v in enumerate(p)) / 2
        for key in ("all", domain):
            acc = totals.setdefault(key, [0, 0., 0.])
            acc[0] += 1
            acc[1] += correct
            acc[2] += brier
    if not totals:
        raise ValueError("empty evaluation")
    return {k: {"n": n, "accuracy": a/n, "brier": b/n}
            for k, (n, a, b) in totals.items()}


def training_pairs(partitions):
    """Only the train partition contributes positive future observations."""
    return tuple((ctx, options[answer])
                 for _, _, ctx, options, answer in partitions["train"])


def jepa_scores(model, context, options):
    """Score the same observable alternatives for either JEPA mode."""
    import torch
    with torch.no_grad():
        logp, means = model.predict([context] * len(options))
        targets = model.encode(options, target=True)
        squared = (means - targets[:, None]).square().sum(-1)
        scores = torch.logsumexp(logp - squared / (2 * 0.5**2), dim=1)
    return scores.cpu().tolist()
