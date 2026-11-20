#!/usr/bin/env python3
"""ENERGY-68: exact constructed orthogonal-block counterexample; no training."""
from fractions import Fraction as F
from itertools import product
import json


def compute():
    total = [F(0) for _ in range(5)]
    null_optimal = [F(0) for _ in range(5)]
    null_forced = [F(0) for _ in range(5)]
    orthogonality = [[F(0) for _ in range(5)] for _ in range(5)]
    count = 0
    for bits in product((-1, 1), repeat=9):
        terms = [bits[2 * i] * bits[2 * i + 1] for i in range(4)]
        noise = bits[8]
        actual = F(noise) + sum((F(t, 10) for t in terms), F(0))
        features = [F(1)] + [F(t) for t in terms]
        for i in range(5):
            for j in range(5):
                orthogonality[i][j] += features[i] * features[j]
        for k in range(5):
            estimate = sum((F(t, 10) for t in terms[:k]), F(0))
            total[k] += (actual - estimate) ** 2
            null_optimal[k] += F(noise) ** 2
            null_forced[k] += (F(noise) - estimate) ** 2
        count += 1
    assert count == 512
    assert orthogonality == [[F(count if i == j else 0) for j in range(5)] for i in range(5)]
    total = [x / count for x in total]
    null_optimal = [x / count for x in null_optimal]
    null_forced = [x / count for x in null_forced]
    assert total == [F(104-k, 100) for k in range(5)]
    assert null_optimal == [F(1)] * 5
    assert null_forced == [F(100+k, 100) for k in range(5)]
    first_gain = (total[0] - total[1]) / total[0]
    joint_gain = (total[0] - total[4]) / total[0]
    assert first_gain < F(3, 100) < joint_gain
    return {
        "schema": "energy68.exact-analytic-census.v1",
        "scope": "CONSTRUCTED_MATHEMATICS_NOT_NATIVE_TRAINING",
        "assignments": count,
        "inputs": "eight Rademacher causal bits plus independent Rademacher noise",
        "mechanism": "four disjoint quadratic products, each coefficient 1/10",
        "population_mse_by_k": [str(x) for x in total],
        "no_signal_optimal_mse_by_k": [str(x) for x in null_optimal],
        "no_signal_forced_coefficients_mse_by_k": [str(x) for x in null_forced],
        "first_step_relative_gain": str(first_gain),
        "joint_four_step_relative_gain": str(joint_gain),
        "threshold": "3/100",
        "exact_orthogonality": True,
        "conclusion": "sequential three-percent early stop can miss jointly beneficial four-term block; full-path conventional control ties joint predictor",
        "scientific_pass": False,
        "native_yggdrasil_training": False,
    }


if __name__ == "__main__":
    print(json.dumps(compute(), sort_keys=True, indent=2))
