#!/usr/bin/env python3
"""F21: pinned owner-JEPA pilot exact linear-capacity source audit (PUBLIC DEV).

No modifications to JEPA source, Yggdrasil main or protected datasets.
Original paired data is source-defined and public; a direct OLS solver uses
the identical public training examples as the trainable JEPA and SGD control.
"""
import argparse
import importlib.util
import json
import math
import random
import subprocess
import sys
from pathlib import Path

PREREG = "71ce1fa8049112d3207a20e878549189d31d937a"
JEPA_COMMIT = "a5ba7c7ee26b6818c8024861bdb2630c4c3b9a6a"
JEPA_TREE = "0dee20efffc5de68cafe054eaee29eb85b96e924"
JEPA_BLOB = "a535d22f6e206b90ddb93b720d5fb93294d4089e"


def verify_source(root):
    root = Path(root).resolve()
    head = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    tree = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD^{tree}"], text=True).strip()
    path = root / "yggdrasil" / "paired_view_jepa.py"
    blob = subprocess.check_output(
        ["git", "-C", str(root), "hash-object", str(path)], text=True).strip()
    if (head, tree, blob) != (JEPA_COMMIT, JEPA_TREE, JEPA_BLOB):
        raise RuntimeError("F21_PINNED_OWNER_SOURCE_DRIFT")
    return path


def load_exact_source(path):
    spec = importlib.util.spec_from_file_location("qtr_f21_owner_jepa", str(path))
    if spec is None or spec.loader is None:
        raise ValueError("F21_NO_OWNER_SOURCE_LOADER")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def folded_matrix(learner):
    # Exact model equation: y_i = sum_j P_ij * sum_k E_jk * x_k.
    return tuple(tuple(
        sum(learner.predictor[i][j] * learner.encoder[j][k] for j in range(2))
        for k in range(3)) for i in range(2))


def apply_linear(weights, observation):
    return tuple(sum(weights[i][j] * observation[j] for j in range(3))
                 for i in range(2))


def fit_direct_ols(train):
    # Fully optimized conventional direct linear control; only public Pair data.
    # Solve (X^T X)W=X^T Y with pivoted Gauss-Jordan elimination (3x5 matrix).
    rows = [[0.] * 5 for _ in range(3)]
    for pair in train:
        x, y = pair.observation, pair.other_view
        for i in range(3):
            for j in range(3):
                rows[i][j] += x[i] * x[j]
            for j in range(2):
                rows[i][3 + j] += x[i] * y[j]
    for col in range(3):
        pivot = max(range(col, 3), key=lambda i: abs(rows[i][col]))
        if abs(rows[pivot][col]) < 1.e-10:
            raise ValueError("F21_SINGULAR_PUBLIC_TRAINING_MATRIX")
        rows[pivot], rows[col] = rows[col], rows[pivot]
        scale = rows[col][col]
        rows[col] = [z / scale for z in rows[col]]
        for i in range(3):
            if i == col:
                continue
            scale = rows[i][col]
            rows[i] = [a - scale * b for a, b in zip(rows[i], rows[col])]
    return tuple(tuple(rows[k][3 + out] for k in range(3))
                 for out in range(2))


def mse(weights, paired):
    return sum(sum((a - b)**2 for a, b in zip(
        apply_linear(weights, p.observation), p.other_view))
        for p in paired) / (len(paired) * 2)


def run(root):
    owner = load_exact_source(verify_source(root))
    train = owner.development_pairs(0, 180)
    holdout = owner.development_pairs(5000, 90)
    before = owner.PairedViewJEPA()
    candidate = owner.PairedViewJEPA()
    candidate.fit(train, epochs=170, lr=.025)
    repeated = owner.PairedViewJEPA()
    repeated.fit(train, epochs=170, lr=.025)
    direct_sgd = owner.DirectLinearControl()
    direct_sgd.fit(train, epochs=170, lr=.025)
    direct_ols = fit_direct_ols(train)

    folded = folded_matrix(candidate)
    rng = random.Random(211)
    public_probes = [tuple(rng.uniform(-3., 3.) for _ in range(3))
                     for _ in range(128)]
    all_public = [p.observation for p in holdout] + public_probes
    diffs = [abs(a - b) for x in all_public for a, b in zip(
        candidate.predict(x), apply_linear(folded, x))]
    max_gap = max(diffs)
    if max_gap > 5e-12:
        raise ValueError("F21_JEPA_DIRECT_LINEAR_PARITY_FAIL")

    for x in all_public:
        if candidate.predict(x) != repeated.predict(x):
            raise ValueError("F21_NONDETERMINISTIC_TRAINING")
    # A linear predictor must have zero interaction contrast between the
    # first two input channels regardless of training and fixed action.
    contrast = max(abs(a + b - c - d)
                   for a, b, c, d in zip(
                       candidate.predict((1., 1., 1.)),
                       candidate.predict((-1., -1., 1.)),
                       candidate.predict((1., -1., 1.)),
                       candidate.predict((-1., 1., 1.))))
    if contrast > 5e-12:
        raise ValueError("F21_NONLINEAR_INTERACTION_UNEXPECTED")
    values = {
        "jepa_untrained_holdout_mse": before.mse(holdout),
        "jepa_trained_holdout_mse": candidate.mse(holdout),
        "direct_sgd_trained_holdout_mse": direct_sgd.mse(holdout),
        "direct_ols_trained_holdout_mse": mse(direct_ols, holdout),
    }
    if not all(math.isfinite(x) for x in values.values()):
        raise ValueError("F21_NONFINITE_PUBLIC_SCORE")
    if not values["jepa_trained_holdout_mse"] < values["jepa_untrained_holdout_mse"]:
        raise ValueError("F21_OWNER_PILOT_NO_LEARNING")
    if values["direct_ols_trained_holdout_mse"] > values["jepa_trained_holdout_mse"] + 1.e-10:
        raise ValueError("F21_STRONG_CONVENTIONAL_CEILING_NOT_MET")
    return {
        "schema": "yggdrasil.qtr.f21.source-exact-jepa-linear-equivalence.v1",
        "prereg_commit": PREREG,
        "owner_commit": JEPA_COMMIT,
        "owner_tree": JEPA_TREE,
        "owner_blob": JEPA_BLOB,
        "train_pairs": len(train), "heldout_pairs": len(holdout),
        "independent_public_probes": len(public_probes),
        "epochs_per_sgd_model": 170,
        "source_owner_model_unchanged": True,
        "jepa_encoder_parameters": 6, "jepa_predictor_parameters": 4,
        "folded_direct_parameters": 6,
        "trained_weights_deterministic": True,
        "max_abs_jepa_vs_folded_direct_linear": max_gap,
        "max_abs_nonlinear_interaction_contrast": contrast,
        "holdout_scores": values,
        "actual_native_causal_transfer_tested": False,
        "source_linear_class_equivalent": True,
        "original_first_use": False, "scientific_pass": False,
        "classification": "DEV_JEPA_LINEAR_FUNCTION_CLASS_CEILING",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner-root", required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.owner_root), indent=2, sort_keys=True))
