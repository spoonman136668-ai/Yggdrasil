"""TGAP26: source-blind expected information value for high-bit probes.

Independent YGG-KNOW01 synthetic contributor. The frozen tgap26_protocol.json
precedes this implementation. Nothing here touches native checkpoints or
protected CausalGym source; all private laws live in the fixture/scorer.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import time
from pathlib import Path

from know25_x2_probe_dev import (
    TruthPosterior, ContextBeta, Passive, FLIPS, FLOOR, SPAN,
    canonical, digest, score,
)
from anf_causal_identifiability_dev import hidden_bit, op_table

SCHEMA = "yggdrasil.tgap26.learned-high-probe-result.dev.v1"
PROTO = "yggdrasil.tgap26.unlock-hidden-variable-through-learned-probe-value.frozen-dev.v1"
PROTOCOL_BLOB = "78fd9d3de9e63846f7b823c406b7ae23ab365dba"
MODE = "engineering_fixture_only"
FIT = ((12001, "x0"), (12007, "x1"), (12013, "xor01"))
PAIRS = (
    ("x0", "x0_xor_x2", (12311, 12317, 12323, 12329)),
    ("xor01", "xor01_xor_x2", (12411, 12421, 12433, 12437)),
    ("and01", "and01_xor_x2", (12503, 12511, 12517, 12527)),
)
SEEDS = frozenset([s for s, _ in FIT] + [s for _, _, ss in PAIRS for s in ss])
LAWS = frozenset([op for _, op in FIT] + [op for a, b, _ in PAIRS for op in (a, b)])
FAMILY = tuple(op_table(op) for pair in PAIRS for op in pair[:2])
POLICIES = (
    "trained_active", "trained_no_x2", "trained_forced_x2",
    "no_fit_active", "uniform_full_active", "known_family_active",
    "context_beta_active", "trained_random", "uninformed_p05",
)

def require(ok, reason):
    if not ok:
        raise ValueError("YGG_TGAP26_" + reason)

def protocol():
    path = Path(__file__).with_name("tgap26_protocol.json")
    raw = path.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    require(blob == PROTOCOL_BLOB, "FROZEN_BLOB")
    d = json.loads(raw)
    require(d["schema"] == PROTO and
            [(x["seed"], x["law"]) for x in d["public_source"]["fit_worlds"]] == list(FIT) and
            [(x["low_law"], x["high_law"], tuple(x["seeds"])) for x in d["public_source"]["held_pairs"]] == list(PAIRS),
            "FROZEN_PROTOCOL")
    return d

def coin(seed, step):
    require(type(seed) is int and seed in SEEDS and
            type(step) is int and 0 <= step < 24, "PRIVATE_COIN")
    raw = hashlib.sha256(f"tgap26:private:outcome:v1:{seed}:{step}".encode("ascii")).digest()
    return int.from_bytes(raw[:8], "big") / (1 << 64)

def consequence(seed, law, step, action):
    require(law in LAWS and type(action) is int and 0 <= action <= 3 and
            type(step) is int and 0 <= step < 24, "PRIVATE_LAW_ACTION")
    effective = (step % 4) ^ FLIPS[action]
    return int(coin(seed, step) < FLOOR + SPAN * hidden_bit(law, effective))

def fit():
    protocol()
    models = []
    beta = [[0, 0] for _ in range(8)]
    for seed, law in FIT:
        m = TruthPosterior([.25] * 8)
        for t in range(24):
            y = consequence(seed, law, t, 0)
            m.observe(t, t % 4, 0, y)
            beta[t % 4][0] += y
            beta[t % 4][1] += 1
        raw = m.checkpoint()
        require(TruthPosterior.restore(raw, digest(raw)).checkpoint() == raw,
                "FIT_COLD_REPLAY")
        models.append(m)
    prior = [float(min(.92, max(.08, (.5 + sum(m.coeff_marginals()[j]
                 for m in models)) / 5))) for j in range(8)]
    require(all(abs(p - .25) < 1e-12 for p in prior[4:]), "FIT_X2_BLIND")
    return {"trained_prior": prior, "fit_actions": 72,
            "fit_cold_hashes": [digest(m.checkpoint()) for m in models],
            "fit_cold_bytes": [len(m.checkpoint()) for m in models],
            "beta": beta}

def model_for(name, bundle):
    require(name in POLICIES, "POLICY")
    if name == "uninformed_p05":
        return Passive()
    if name == "context_beta_active":
        m = ContextBeta()
        m.counts = [list(x) for x in bundle["beta"]]
        return m
    if name == "known_family_active":
        return TruthPosterior([.5] * 8, family=FAMILY)
    if name == "uniform_full_active":
        return TruthPosterior([.5] * 8)
    if name == "no_fit_active":
        return TruthPosterior([.25] * 8)
    return TruthPosterior(bundle["trained_prior"])

def entropy(p):
    return -p * math.log(p) - (1-p) * math.log1p(-p) if 0 < p < 1 else 0.0

def information_gain(m, c, a):
    """Expected high-bit entropy reduction, averaged over BOTH possible y."""
    target = c ^ FLIPS[a]
    if isinstance(m, ContextBeta):
        if target < 4:
            return 0.0
        s, n = m.counts[target]
        p = (s+1)/(n+2)
        return entropy(p) - p*entropy((s+2)/(n+3)) - (1-p)*entropy((s+1)/(n+3))
    require(isinstance(m, TruthPosterior), "INFORMATION_MODEL")
    weights = m.weights()
    prior = [sum(w for h,w in zip(m.family, weights) if (h>>j)&1)
             for j in range(4,8)]
    likelihood = [FLOOR + SPAN*((h>>target)&1) for h in m.family]
    py = sum(w*q for w,q in zip(weights, likelihood))
    require(0 < py < 1, "PREDICTIVE_LIKELIHOOD")
    loss = 0.0
    for j in range(4,8):
        joint1 = sum(w*q for h,w,q in zip(m.family,weights,likelihood)
                     if (h>>j)&1)
        joint0 = prior[j-4] - joint1
        after1,after0 = joint1/py, joint0/(1-py)
        loss += entropy(prior[j-4]) - py*entropy(after1) - (1-py)*entropy(after0)
    return loss

def choose(m, c, actions):
    require(actions and all(type(x) is int and x in range(4) for x in actions),
            "PUBLIC_ACTION_SET")
    return min(actions, key=lambda a: (-information_gain(m, c, a), a))

def run_world(name, seed, law, bundle):
    require(name in POLICIES and type(seed) is int and
            any(seed in ss and law in (a,b) for a,b,ss in PAIRS),
            "HELD_SOURCE_IDENTITY")
    m = model_for(name, bundle)
    rng = random.Random(seed * 7381 + 59)
    trace = []
    choices = [0]*4
    for t in range(24):
        c = t % 4
        if t < 12 or name == "uninformed_p05":
            a = t % 3
        elif name == "trained_no_x2":
            a = choose(m, c, (0,1,2))
        elif name == "trained_forced_x2":
            a = 3
        elif name == "trained_random":
            a = rng.randrange(4)
        else:
            a = choose(m, c, (0,1,2,3))
        y = consequence(seed, law, t, a)
        m.observe(t, c, a, y)
        trace.append([t, c, a, y])
        choices[a] += 1
    if isinstance(m, TruthPosterior):
        raw = m.checkpoint()
        require(TruthPosterior.restore(raw, digest(raw)).checkpoint() == raw,
                "HELD_COLD_REPLAY")
        size = len(raw)
    else:
        size = len(canonical({"counts": getattr(m, "counts", []),
                              "trace": trace}))
    high = [float(m.predict(c, 0)) for c in range(4,8)]
    expected = sum(score(p, FLOOR + SPAN*hidden_bit(law,c))
                   for c,p in zip(range(4,8),high))
    require(len(trace)==24 and sum(choices)==24 and len(high)==4 and
            all(0 <= p <= 1 and math.isfinite(p) for p in high),
            "HELD_BUDGET")
    return {"trace":trace, "choices":choices, "high":high,
            "high_sum":expected, "checkpoint_bytes":size}

def proof():
    start = time.monotonic()
    bundle = fit()
    metrics = {}
    pairs = {}
    for name in POLICIES:
        rows, paired = [], []
        for low,high,seeds in PAIRS:
            for seed in seeds:
                left=run_world(name,seed,low,bundle)
                right=run_world(name,seed,high,bundle)
                rows.extend((left,right))
                paired.append({"seed":seed,
                    "indistinguishable":left["trace"]==right["trace"] and left["high"]==right["high"],
                    "paired_brier":(left["high_sum"]+right["high_sum"])/8,
                    "high_forecast_l1":sum(abs(a-b) for a,b in
                                            zip(left["high"],right["high"]))/4})
        require(len(rows)==24 and all(len(row["trace"])==24 for row in rows),
                "HELD_COUNT")
        metrics[name]={
            "high_expected_brier":round(sum(x["high_sum"] for x in rows)/96, 9),
            "action_counts":[sum(x["choices"][j] for x in rows) for j in range(4)],
            "post_warmup_x2_actions":sum(sum(row[2]==3 for row in x["trace"][12:]) for x in rows),
            "avg_checkpoint_bytes":round(sum(x["checkpoint_bytes"] for x in rows)/24,2),
            "held_observations":sum(len(x["trace"]) for x in rows),
            "high_score_queries":96,
        }
        pairs[name]=paired
    cand=metrics["trained_active"]["high_expected_brier"]
    h={
        "H1_no_x2_identifiability_negative":all(p["indistinguishable"] and p["paired_brier"]>=.25-1e-8
                                                 for p in pairs["trained_no_x2"]),
        "H2_learned_x2_probe_count":metrics["trained_active"]["post_warmup_x2_actions"]>=144,
        "H3_active_gain_over_barred":metrics["trained_no_x2"]["high_expected_brier"]-cand>=.02,
        "H4_vs_full_uniform_bayes":metrics["uniform_full_active"]["high_expected_brier"]-cand>=.01,
        "H5_fit_gain_over_nofit":metrics["no_fit_active"]["high_expected_brier"]-cand>=.01,
        "H6_paired_high_divergence":sum(p["high_forecast_l1"]>=.05 for p in pairs["trained_active"])>=8,
    }
    require(h["H1_no_x2_identifiability_negative"],"PAIR_NEGATIVE_CONTROL")
    successes=sum(h.values())
    return {"schema":SCHEMA,"source_mode":MODE,"fit_actions":bundle["fit_actions"],
            "fit_checkpoint_hashes":bundle["fit_cold_hashes"],
            "held_actions_per_policy":576,"high_queries_per_policy":96,
            "metrics":metrics,"hypotheses":h,
            "development_verdict":"DEV_MECHANISM_DISCOVERY_SUPPORTED" if successes==6
                  else "DEV_MIXED_X2_DISCOVERY" if successes else "DEV_NO_GO",
            "engineering_gate":"SOURCE_ONLY_CHECKS_PASSED",
            "science_gate":"SCIENTIFIC_NO_GO_SYNTHETIC",
            "accepted_native_modified":False,"first_use_426":False,"deployment":"NONE",
            "isolated_wall_seconds":round(time.monotonic()-start,4)}

if __name__ == "__main__":
    print("YGG_TGAP26_RECEIPT="+json.dumps(proof(),sort_keys=True))
