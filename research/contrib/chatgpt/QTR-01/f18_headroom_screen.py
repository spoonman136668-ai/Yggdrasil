#!/usr/bin/env python3
"""QTR F18: FROZEN, PUBLIC DEV intervention consequence headroom screen.

Real pinned upstream source; different nonlinear and lagged causal law families.
Methods learn from identical PUBLIC action/outcome rows. The evaluator alone
selects published worlds and scores held-out intervention values. Not protected
science, not a trained Yggdrasil model, not cross-family transfer.
"""
import argparse
import json
import subprocess
from pathlib import Path

import numpy as np

UPSTREAM_SHA = "51f1431515e310dec72e3f4b6db378df46f832ea"
UPSTREAM_TREE = "c1bf53ecf03ae326b69c0321f4412d81f3122894"
SEEDS = (1911, 1912, 1913, 1914)
N_TRAIN = 480
N_TEST = 240


def verify_upstream(root):
    root = Path(root)
    commit = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    tree = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD^{tree}"], text=True).strip()
    if (commit, tree) != (UPSTREAM_SHA, UPSTREAM_TREE):
        raise ValueError("F18_SOURCE_IDENTITY_MISMATCH")


def public_rows(world, seed, is_train):
    from causal_worlds import build_substrate, worlds
    root = build_substrate(worlds.get(world), standardize=False)
    length = N_TRAIN if is_train else N_TEST
    gen_seed = seed + (1 if is_train else 10001)
    sample_seed = seed if is_train else seed + 10000
    rng = np.random.default_rng(gen_seed)
    if world == "braking":
        levels = (-2.0, -1.0, 1.0, 2.0) if is_train else (-1.5, -0.5, 0.5, 1.5)
        forced = rng.choice(levels, size=length)
        data = root.sample(length, seed=sample_seed, do={"speed": forced})
        cols = {name: data.data[:, i] for i, name in enumerate(data.variables)}
        x = np.column_stack([cols["speed"], cols["road_grip"]])
        y = cols["braking_distance"]
    elif world == "supply":
        levels = (-2.0, 0.0, 2.0) if is_train else (-1.5, 0.5, 1.5)
        forced = rng.choice(levels, size=length)
        data = root.sample(length, seed=sample_seed, do={"order": forced})
        cols = {name: data.data[:, i] for i, name in enumerate(data.variables)}
        x = np.column_stack([cols["inventory"][:-1], cols["order"][:-1],
                             cols["leadtime"][:-1]])
        y = cols["inventory"][1:]
    else:
        raise ValueError("F18_WORLD_NOT_ADMITTED")
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
        raise ValueError("F18_NONFINITE_DATA")
    return x, y


def polynomial_features(x, nonlinear):
    if x.ndim != 2:
        raise ValueError("F18_BAD_FEATURES")
    columns = [np.ones((len(x), 1)), x]
    if nonlinear:
        columns.append(x * x)
    return np.column_stack(columns)


def ols_predict(x_train, y_train, x_eval, nonlinear):
    design = polynomial_features(x_train, nonlinear)
    weight = np.linalg.lstsq(design, y_train, rcond=None)[0]
    return polynomial_features(x_eval, nonlinear) @ weight


def knn_predict(x_train, y_train, x_eval, k=8):
    avg = x_train.mean(axis=0)
    scale = x_train.std(axis=0)
    scale = np.where(scale < 1e-8, 1., scale)
    t = (x_train - avg) / scale
    e = (x_eval - avg) / scale
    dist = np.sum((e[:, None, :] - t[None, :, :]) ** 2, axis=2)
    nearest = np.argpartition(dist, kth=k - 1, axis=1)[:, :k]
    return y_train[nearest].mean(axis=1)


def exact_event_coverage(x_train, x_eval):
    seen = {tuple(row.tolist()) for row in x_train}
    return sum(tuple(row.tolist()) in seen for row in x_eval)


def mlp_predict(x_train, y_train, x_eval, seed, updates=600):
    # Fully fit a conventional 24-unit nonlinear control, no test data in the optimizer.
    mean_x, sd_x = x_train.mean(axis=0), x_train.std(axis=0)
    sd_x = np.where(sd_x < 1e-8, 1., sd_x)
    mean_y, sd_y = float(y_train.mean()), max(float(y_train.std()), 1e-8)
    x = (x_train - mean_x) / sd_x
    target = (y_train - mean_y) / sd_y
    test = (x_eval - mean_x) / sd_x
    rng = np.random.default_rng(seed)
    w1 = rng.normal(0, 0.25, size=(x.shape[1], 24))
    b1 = np.zeros(24)
    w2 = rng.normal(0, 0.15, size=24)
    b2 = np.zeros(1)
    params = [w1, b1, w2, b2]
    moment = [np.zeros_like(p) for p in params]
    velocity = [np.zeros_like(p) for p in params]
    for step in range(1, updates + 1):
        hidden = np.tanh(x @ w1 + b1)
        predicted = hidden @ w2 + b2[0]
        err = (predicted - target) * (2. / len(x))
        backward = err[:, None] * w2[None, :] * (1. - hidden**2)
        gradients = [x.T @ backward + 1.e-4 * w1,
                     backward.sum(axis=0), hidden.T @ err + 1.e-4 * w2,
                     np.asarray([err.sum()])]
        for i, (param, grad) in enumerate(zip(params, gradients)):
            moment[i] *= .9
            moment[i] += .1 * grad
            velocity[i] *= .999
            velocity[i] += .001 * (grad**2)
            param -= .015 * (moment[i] / (1. - .9**step)) / (
                np.sqrt(velocity[i] / (1. - .999**step)) + 1e-8)
    return ((np.tanh(test @ w1 + b1) @ w2 + b2[0]) * sd_y + mean_y)


def score(world, seed):
    train_x, train_y = public_rows(world, seed, True)
    eval_x, eval_y = public_rows(world, seed, False)
    assert len(eval_y) == (N_TEST if world == "braking" else N_TEST - 1)
    if len(train_x) != len(train_y):
        raise ValueError("F18_BAD_TRAIN_LENGTH")
    rng = np.random.default_rng(seed + 50500)
    shuffled = rng.permutation(train_y)
    methods = {
        "linear_ols": ols_predict(train_x, train_y, eval_x, False),
        "quadratic_ols_strong": ols_predict(train_x, train_y, eval_x, True),
        "knn8": knn_predict(train_x, train_y, eval_x),
        "mlp24_adam600": mlp_predict(train_x, train_y, eval_x, seed + 30300),
        "negative_shuffled_quadratic": ols_predict(train_x, shuffled, eval_x, True),
    }
    variance = float(np.var(eval_y))
    if variance <= 1e-9:
        raise ValueError("F18_NO_VARIANCE_HEADROOM")
    measurements = {
        name: {"mse": float(np.mean((prediction - eval_y)**2)),
               "relative_mse": float(np.mean((prediction - eval_y)**2) / variance)}
        for name, prediction in methods.items()
    }
    if any(not np.isfinite(m["relative_mse"]) for m in measurements.values()):
        raise ValueError("F18_NONFINITE_SCORE")
    return {
        "seed": seed, "train_rows": len(train_y), "eval_rows": len(eval_y),
        "exact_event_retrieval_coverage": exact_event_coverage(train_x, eval_x),
        "eval_y_variance": variance, "methods": measurements,
    }


def run(root):
    verify_upstream(root)
    results = {world: [score(world, seed) for seed in SEEDS]
               for world in ("braking", "supply")}
    summary = {}
    for world, items in results.items():
        methods = items[0]["methods"]
        means = {name: float(np.mean([
            item["methods"][name]["relative_mse"] for item in items]))
                 for name in methods}
        summary[world] = {
            "mean_relative_mse": means,
            "strongest_observed_baseline": min(
                (name for name in methods if not name.startswith("negative")),
                key=lambda name: means[name]),
            "linear_to_quadratic_relative_mse_gap": means["linear_ols"] -
                                                     means["quadratic_ols_strong"],
            "exact_retrieval_covered": sum(
                item["exact_event_retrieval_coverage"] for item in items),
            "evaluation_rows": sum(item["eval_rows"] for item in items),
        }
    return {
        "schema": "yggdrasil.qtr.f18.public-dev-baseline-screen.v1",
        "upstream_commit": UPSTREAM_SHA, "upstream_tree": UPSTREAM_TREE,
        "published_dev_worlds_only": True,
        "seeds": list(SEEDS), "native_model_trained": False,
        "recurrent_neural_baseline_trained": False,
        "scientific_pass": False, "cross_family_transfer_tested": False,
        "complete_matched_capacity_compute_budget": False,
        "classification": "DEV_BASELINE_HEADROOM_DIAGNOSTIC_ONLY",
        "summary": summary, "per_seed": results
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream-root", required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.upstream_root), indent=2, sort_keys=True))
