#!/usr/bin/env python3
"""QTR F19: preregistered PUBLIC DEV nonlinear temporal causal association baselines.

This is a controlled diagnostic with a pinned independent source simulator;
NOT a native Yggdrasil learner, genuinely unseen science, or model promotion.
The scoring/evaluator owns the causal WorldSpec; predictors receive only
numeric public intervention, proxy-observation, and previous-outcome samples.
"""
import argparse
import json
import math
import subprocess
import time
from pathlib import Path

import numpy as np

from f18_headroom_screen import (
    exact_event_coverage, knn_predict, mlp_predict, ols_predict,
)

UPSTREAM_SHA = "51f1431515e310dec72e3f4b6db378df46f832ea"
UPSTREAM_TREE = "c1bf53ecf03ae326b69c0321f4412d81f3122894"
PREREG_SHA = "0883ba9898ae95e814aa81d25424dac86d0d8ee1"
SEEDS = (2011, 2012, 2013, 2014)
FAMILIES = ("lagged_gate", "lagged_saturator")
TRAIN_LENGTH = 258
EVAL_LENGTH = 194
HIDDEN = 16
ADAM_UPDATES = 240
ADAM_LR = .01


def validate_source(root):
    root = Path(root)
    head = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    tree = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD^{tree}"], text=True).strip()
    if (head, tree) != (UPSTREAM_SHA, UPSTREAM_TREE):
        raise ValueError("F19_PINNED_SOURCE_MISMATCH")


def construct_world(family):
    from causal_worlds.schema import (
        WorldSpec, Variable, Role, Mechanism, Term, Transform, validate,
    )
    if family == "lagged_gate":
        terms = (
            Term("outcome", .55, lag=1, transform=Transform.TANH),
            Term("action", .85, lag=1, transform=Transform.RELU),
            Term("action", -.35, lag=2, transform=Transform.ABS),
            Term("latent", .28),
        )
    elif family == "lagged_saturator":
        terms = (
            Term("outcome", -.45, lag=1, transform=Transform.TANH),
            Term("action", .90, lag=2, transform=Transform.TANH),
            Term("action", .40, lag=1, transform=Transform.ABS),
            Term("latent", .28),
        )
    else:
        raise ValueError("F19_UNKNOWN_FAMILY")
    spec = WorldSpec(
        variables=(
            Variable("latent", Role.DISTURBANCE, hidden=True),
            Variable("action", Role.CONTROLLABLE),
            Variable("indicator", Role.OBSERVABLE),
            Variable("outcome", Role.OUTCOME),
        ),
        mechanisms=(
            Mechanism("indicator", (Term("latent", .60),), noise_scale=.18),
            Mechanism("outcome", terms, noise_scale=.12),
        ),
    )
    validate(spec)
    return spec


def measured_rows(family, seed, train):
    from causal_worlds import build_substrate
    length = TRAIN_LENGTH if train else EVAL_LENGTH
    levels = (-2., -1., 0., 1., 2.) if train else (-1.5, -.5, .5, 1.5)
    rng = np.random.default_rng(seed + (1 if train else 10001))
    actions = rng.choice(levels, size=length)
    sample_seed = seed if train else seed + 10000
    substrate = build_substrate(construct_world(family), standardize=False)
    sample = substrate.sample(length, seed=sample_seed, do={"action": actions})
    cols = {name: sample.data[:, j] for j, name in enumerate(sample.variables)}
    if "latent" in cols or set(cols) != {"action", "indicator", "outcome"}:
        raise ValueError("F19_PRIVATE_VARIABLE_IN_PUBLIC_SAMPLES")
    x = np.column_stack([
        cols["action"][1:-1],
        cols["action"][:-2],
        cols["outcome"][1:-1],
        cols["indicator"][2:],
    ])
    y = cols["outcome"][2:]
    if len(x) != length - 2 or not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("F19_BAD_PUBLIC_DATA")
    return x, y


def symbolic_design(x):
    """Known-transform-family strong prior disclosed before results, not a native learner."""
    a1, a2, prior_y, _indicator = x.T
    return np.column_stack([
        np.ones(len(x)), x,
        np.maximum(a1, 0), np.abs(a1), np.tanh(a1),
        np.maximum(a2, 0), np.abs(a2), np.tanh(a2),
        np.tanh(prior_y),
    ])


def symbolic_ols(x_train, y_train, x_test):
    weights = np.linalg.lstsq(symbolic_design(x_train), y_train, rcond=None)[0]
    return symbolic_design(x_test) @ weights


def rnn_forward(x, params):
    wx, wh, bh, wy, by = params
    prev = np.zeros(wh.shape[0], dtype=np.float64)
    hidden = np.empty((len(x), len(prev)), dtype=np.float64)
    output = np.empty(len(x), dtype=np.float64)
    for t, obs in enumerate(x):
        prev = np.tanh(obs @ wx + prev @ wh + bh)
        hidden[t] = prev
        output[t] = prev @ wy + by[0]
    return output, hidden


def rnn_loss_grad(x, target, params):
    """Full BPTT: gradients flow through input, recurrent and readout parameters."""
    output, h = rnn_forward(x, params)
    wx, wh, _bh, wy, _by = params
    gradient = [np.zeros_like(v) for v in params]
    next_hidden_grad = np.zeros(wh.shape[0])
    norm = float(len(x))
    for t in range(len(x) - 1, -1, -1):
        d_out = 2. * (output[t] - target[t]) / norm
        gradient[3] += h[t] * d_out
        gradient[4][0] += d_out
        delta = (wy * d_out + next_hidden_grad) * (1. - h[t]**2)
        gradient[0] += np.outer(x[t], delta)
        previous = h[t - 1] if t > 0 else np.zeros(wh.shape[0])
        gradient[1] += np.outer(previous, delta)
        gradient[2] += delta
        next_hidden_grad = wh @ delta
    gradient[0] += 2e-5 * wx
    gradient[1] += 2e-5 * wh
    loss = float(np.mean((output - target)**2) +
                 1e-5 * (np.sum(wx**2) + np.sum(wh**2)))
    return loss, gradient


def rnn_predict(train_x, train_y, test_x, seed, updates=ADAM_UPDATES):
    mu_x = train_x.mean(axis=0)
    scale_x = np.maximum(train_x.std(axis=0), 1.e-8)
    mu_y = float(train_y.mean())
    scale_y = max(float(train_y.std()), 1.e-8)
    x = (train_x - mu_x) / scale_x
    target = (train_y - mu_y) / scale_y
    query = (test_x - mu_x) / scale_x
    rng = np.random.default_rng(seed)
    params = [
        rng.normal(0., .15, size=(x.shape[1], HIDDEN)),
        rng.normal(0., .08, size=(HIDDEN, HIDDEN)),
        np.zeros(HIDDEN),
        rng.normal(0., .15, size=HIDDEN),
        np.zeros(1),
    ]
    m = [np.zeros_like(p) for p in params]
    v = [np.zeros_like(p) for p in params]
    begin = time.perf_counter()
    for update in range(1, updates + 1):
        loss, gradients = rnn_loss_grad(x, target, params)
        if not math.isfinite(loss):
            raise ValueError("F19_NONFINITE_RNN_LOSS")
        grad_norm = math.sqrt(sum(float((g * g).sum()) for g in gradients))
        if not math.isfinite(grad_norm):
            raise ValueError("F19_NONFINITE_RNN_GRAD")
        scale = min(1., 5. / max(grad_norm, 1.e-12))
        for i, (param, grad) in enumerate(zip(params, gradients)):
            grad *= scale
            m[i] *= .9
            m[i] += .1 * grad
            v[i] *= .999
            v[i] += .001 * (grad * grad)
            param -= ADAM_LR * (m[i] / (1. - .9**update)) / (
                np.sqrt(v[i] / (1. - .999**update)) + 1e-8)
    output, _ = rnn_forward(query, params)
    result = output * scale_y + mu_y
    if not np.isfinite(result).all():
        raise ValueError("F19_NONFINITE_RNN_OUTPUT")
    return result, time.perf_counter() - begin


def intervention_probes(family, seed):
    from causal_worlds import build_substrate
    root = build_substrate(construct_world(family), standardize=False)
    length = 80
    action = np.asarray([1.5 if t % 2 else -1.5 for t in range(length)])
    a = root.sample(length, seed=seed + 22000, do={"action": action})
    b = root.sample(length, seed=seed + 22000,
                    do={"action": np.zeros(length, dtype=np.float64)})
    target = a.variables.index("outcome")
    probe = float(np.mean(np.abs(a.data[2:, target] - b.data[2:, target])))
    if not np.isfinite(probe):
        raise ValueError("F19_BAD_PROBE")
    return probe


def score(family, seed):
    train_x, train_y = measured_rows(family, seed, True)
    eval_x, eval_y = measured_rows(family, seed, False)
    compare_y = np.random.default_rng(seed + 50500).permutation(train_y)
    start = time.perf_counter()
    recurrent, rnn_elapsed = rnn_predict(train_x, train_y, eval_x,
                                         seed + 30300)
    predictions = {
        "linear_ols": ols_predict(train_x, train_y, eval_x, False),
        "quadratic_ols": ols_predict(train_x, train_y, eval_x, True),
        "symbolic_dictionary_ols": symbolic_ols(train_x, train_y, eval_x),
        "knn8": knn_predict(train_x, train_y, eval_x),
        "mlp24_adam600": mlp_predict(train_x, train_y, eval_x, seed + 33300),
        "elman_rnn16_adam240": recurrent,
        "negative_shuffled_symbolic": symbolic_ols(train_x, compare_y, eval_x),
    }
    variance = float(np.var(eval_y))
    if variance <= 1.e-9:
        raise ValueError("F19_NO_TARGET_VARIANCE")
    normalized = {k: float(np.mean((guess - eval_y)**2) / variance)
                  for k, guess in predictions.items()}
    if any(not np.isfinite(v) for v in normalized.values()):
        raise ValueError("F19_NONFINITE_SCORE")
    # Check deterministic source replay; not all generated-world changes are IID.
    repeated_x, repeated_y = measured_rows(family, seed, False)
    if not np.array_equal(eval_x, repeated_x) or not np.array_equal(eval_y, repeated_y):
        raise ValueError("F19_REPLAY_MISMATCH")
    return {
        "seed": seed,
        "train_rows": len(train_y),
        "evaluation_rows": len(eval_y),
        "intervention_gap": intervention_probes(family, seed),
        "exact_tuple_retrieval_coverage": exact_event_coverage(train_x, eval_x),
        "relative_mse": normalized,
        "rnn_training_seconds": round(rnn_elapsed, 6),
        "score_wall_seconds": round(time.perf_counter() - start, 6),
    }


def run(root):
    validate_source(root)
    results = {family: [score(family, seed) for seed in SEEDS] for family in FAMILIES}
    summaries = {}
    for family, rows in results.items():
        mean_scores = {name: float(np.mean([r["relative_mse"][name] for r in rows]))
                       for name in rows[0]["relative_mse"]}
        candidates = {k: v for k, v in mean_scores.items()
                      if k != "negative_shuffled_symbolic"}
        interventions_identifiable = all(r["intervention_gap"] >= .2 for r in rows)
        negative_valid = mean_scores["negative_shuffled_symbolic"] > min(candidates.values())
        summaries[family] = {
            "mean_relative_mse": mean_scores,
            "strongest_observed_control": min(candidates, key=candidates.get),
            "intervention_probe_min_abs_gap": min(r["intervention_gap"] for r in rows),
            "action_consequences_distinguishable": interventions_identifiable,
            "negative_control_loses": negative_valid,
            "exact_raw_tuple_covered": sum(r["exact_tuple_retrieval_coverage"] for r in rows),
            "eval_rows": sum(r["evaluation_rows"] for r in rows),
            "rnn_train_seconds_total": sum(r["rnn_training_seconds"] for r in rows),
        }
    if all(s["action_consequences_distinguishable"] and s["negative_control_loses"]
           for s in summaries.values()):
        classification = "DEV_MEASURED_CONVENTIONAL_CEILING_OR_HEADROOM_ONLY"
    else:
        classification = "DEV_NEGATIVE_INADEQUATE_IDENTIFIABILITY_OR_CONTROL"
    return {
        "schema": "yggdrasil.qtr.f19.dev-nonlinear-temporal.v1",
        "preregistration_commit": PREREG_SHA,
        "upstream_commit": UPSTREAM_SHA, "upstream_tree": UPSTREAM_TREE,
        "public_development_only": True, "science_pass": False,
        "fully_trained_conventional_rnn": True,
        "native_yggdrasil_trained": False,
        "cross_family_transfer_tested": False,
        "recurrent_one_step_teacher_forcing": True,
        "capacity_compute_matched_to_native": False,
        "seeds": list(SEEDS),
        "classification": classification,
        "summary": summaries, "per_seed": results,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream-root", required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.upstream_root), sort_keys=True, indent=2))
