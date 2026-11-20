#!/usr/bin/env python3
"""ENERGY-69 frozen source-free joint-block causal admission screen.
Only isolated synthetic causal worlds; not a Yggdrasil learner or first-use data.
"""
import argparse
import csv
import hashlib
import itertools
import json
import os
import time
from pathlib import Path
import numpy as np
from sklearn.linear_model import ElasticNet

SEEDS = (210901, 210917, 210929)
FAMILIES = ("null", "two", "four", "four_plus_fifth")
WORLD_IDS = tuple(range(6))
COMB4 = tuple(itertools.combinations(range(9), 4))
COMB5 = tuple(itertools.combinations(range(9), 5))
METHODS = ("block4", "cv_path", "fixed4", "ridge126", "elasticnet", "shuffled")


def feature_matrix(actions, supports):
    bits = np.where(((actions[:, None] >> np.arange(9)) & 1) != 0, 1.0, -1.0)
    return np.column_stack([np.prod(bits[:, ids], axis=1) for ids in supports])


def fit_ridge(x, y, selected, alpha=0.3):
    if not selected:
        return float(y.mean()), np.empty(0, dtype=float)
    z = x[:, selected]
    mx, my = z.mean(axis=0), float(y.mean())
    w = np.linalg.solve((z - mx).T @ (z - mx) + alpha * np.eye(len(selected)), (z-mx).T @ (y - my))
    return my - float(mx @ w), w


def predict(x, selected, model):
    b, w = model
    return np.full(x.shape[0], b) if not selected else b + x[:, selected] @ w


def greedy_path(x, y):
    chosen = []
    available = np.ones(x.shape[1], dtype=bool)
    for _ in range(5):
        residual = y - predict(x, chosen, fit_ridge(x, y, chosen))
        scores = np.abs(x.T @ residual)
        scores[~available] = -1.0
        chosen.append(int(np.argmax(scores)))
        available[chosen[-1]] = False
    return chosen


def world(seed, family, world_id):
    rng = np.random.default_rng(np.random.SeedSequence([seed, FAMILIES.index(family), world_id, 69]))
    actions = rng.permutation(512).astype(np.int64)
    train, valid, cold = actions[:48], actions[48:64], actions[64:112]
    terms = 0 if family == "null" else 2 if family == "two" else 4
    supports = rng.choice(len(COMB4), size=terms, replace=False)
    signs = rng.choice([-1., 1.], size=terms)
    fifth = COMB5[int(rng.integers(len(COMB5)))] if family == "four_plus_fifth" else None
    fifth_sign = float(rng.choice([-1., 1.]))
    def consequences(ids):
        f = feature_matrix(ids, COMB4)
        truth = (f[:, supports] @ (0.55 * signs)) if terms else np.zeros(len(ids))
        if fifth is not None:
            truth += 0.45 * fifth_sign * feature_matrix(ids, [fifth])[:, 0]
        return truth + rng.normal(0., 0.30, len(ids))
    return train, valid, cold, consequences(train), consequences(valid), consequences(cold)


def score_world(seed, family, world_id):
    tr, va, te, ytr, yva, yte = world(seed, family, world_id)
    start = time.perf_counter()
    xtr, xva, xte = [feature_matrix(ids, COMB4) for ids in (tr, va, te)]
    bank_time = time.perf_counter() - start
    start = time.perf_counter()
    path = greedy_path(xtr, ytr)
    fits = [fit_ridge(xtr, ytr, path[:k]) for k in range(6)]
    val = [float(np.mean((yva - predict(xva, path[:k], fits[k])) ** 2)) for k in range(6)]
    common_time = time.perf_counter() - start
    selected = {"block4": 4 if val[4] + 0.01 < val[0] else 0,
                "cv_path": int(np.argmin(val)), "fixed4": 4}
    output = {}
    for method, k in selected.items():
        begin = time.perf_counter()
        model = fit_ridge(np.vstack((xtr, xva)), np.hstack((ytr, yva)), path[:k])
        predictions = predict(xte, path[:k], model)
        output[method] = (float(np.mean((predictions - yte) ** 2)), bank_time + common_time + (time.perf_counter()-begin))
    start = time.perf_counter()
    full = fit_ridge(np.vstack((xtr, xva)), np.hstack((ytr, yva)), list(range(len(COMB4))))
    yhat = predict(xte, list(range(len(COMB4))), full)
    output["ridge126"] = (float(np.mean((yhat-yte)**2)), bank_time + (time.perf_counter()-start))
    start = time.perf_counter()
    alphas = (0.01, 0.05, 0.2)
    choices = []
    for a in alphas:
        m = ElasticNet(alpha=a, l1_ratio=0.8, fit_intercept=True, max_iter=3000, tol=1e-6, selection="cyclic")
        m.fit(xtr, ytr)
        choices.append(float(np.mean((m.predict(xva)-yva)**2)))
    final = ElasticNet(alpha=alphas[int(np.argmin(choices))], l1_ratio=0.8, fit_intercept=True, max_iter=3000, tol=1e-6, selection="cyclic")
    final.fit(np.vstack((xtr,xva)), np.hstack((ytr,yva)))
    output["elasticnet"] = (float(np.mean((final.predict(xte)-yte)**2)), bank_time + (time.perf_counter()-start))
    start = time.perf_counter()
    s_rng = np.random.default_rng(np.random.SeedSequence([seed, FAMILIES.index(family), world_id, 6901]))
    yshuffle = ytr[s_rng.permutation(len(ytr))]
    s_path = greedy_path(xtr, yshuffle)
    s_fit = fit_ridge(xtr, yshuffle, s_path[:4])
    output["shuffled"] = (float(np.mean((predict(xte, s_path[:4], s_fit)-yte)**2)), bank_time + (time.perf_counter()-start))
    assert len(set(map(int, np.concatenate((tr,va,te))))) == 112
    return {"seed":seed,"family":family,"world":world_id,"k_block":selected["block4"],"k_cv":selected["cv_path"],"path_sha256":hashlib.sha256(bytes(path)).hexdigest(), **{k+"_mse":output[k][0] for k in METHODS}, **{k+"_sec":output[k][1] for k in METHODS}}


def run(seeds, families, worlds, out):
    cases=[score_world(seed,fam,w) for seed in seeds for fam in families for w in worlds]
    out.mkdir(parents=True, exist_ok=True)
    keys=list(cases[0].keys())
    with (out/"cases.csv").open("w",newline="",encoding="utf8") as f:
        writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader();writer.writerows(cases)
    summary={"schema":"energy69.screen.v1","seeds":seeds,"families":families,"world_ids":worlds,
             "cases":len(cases),"scope":"EXTERNAL_SYNTHETIC_ONLY","native_yggdrasil_training":False,
             "mse":{m:float(np.mean([c[m+"_mse"] for c in cases])) for m in METHODS},
             "runtime_seconds":{m:float(sum(c[m+"_sec"] for c in cases)) for m in METHODS},
             "by_seed":{str(s):{m:float(np.mean([c[m+"_mse"] for c in cases if c["seed"]==s])) for m in METHODS} for s in seeds},
             "by_family":{f:{m:float(np.mean([c[m+"_mse"] for c in cases if c["family"]==f])) for m in METHODS} for f in families}}
    competing=min(summary["mse"][m] for m in ("cv_path","fixed4","ridge126","elasticnet"))
    summary["gates"]={"strongest_5pct":summary["mse"]["block4"]<=0.95*competing,
        "every_seed_strongest":all(summary["by_seed"][str(s)]["block4"]< min(summary["by_seed"][str(s)][m] for m in ("cv_path","fixed4","ridge126","elasticnet")) for s in seeds),
        "family_non_degradation_10pct":all(summary["by_family"][f]["block4"]<=1.10*min(summary["by_family"][f][m] for m in ("cv_path","fixed4","ridge126","elasticnet")) for f in families),
        "null_guard_10pct":summary["by_family"]["null"]["block4"]<=1.10*summary["by_family"]["null"]["cv_path"],
        "shuffled_negative_20pct":summary["mse"]["block4"]<=0.8*summary["mse"]["shuffled"]}
    summary["screen_decision"]="DEVELOPMENT_GO_ONLY" if all(summary["gates"].values()) else "DEVELOPMENT_NO_GO"
    (out/"result.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps({"cases":summary["cases"],"mse":summary["mse"],"gates":summary["gates"],"screen_decision":summary["screen_decision"]},sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True);p.add_argument("--smoke",action="store_true")
    a=p.parse_args()
    run((210899,) if a.smoke else SEEDS,("null","four") if a.smoke else FAMILIES,(0,) if a.smoke else WORLD_IDS,a.out)
