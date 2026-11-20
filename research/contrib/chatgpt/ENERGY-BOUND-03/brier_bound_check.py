#!/usr/bin/env python3
"""Exact rational check of correct-Bayes multiclass Brier decomposition.

Research contributor analytic check; synthetic probability grids only. No
Yggdrasil trainer, checkpoint, observations, or primary evaluation seeds.
"""
from fractions import Fraction
from itertools import product


def simplex_grid(classes: int, denominator: int):
    return [tuple(Fraction(k, denominator) for k in counts)
            for counts in product(range(denominator + 1), repeat=classes)
            if sum(counts) == denominator]


def conditional_expected_brier(p, q):
    """E_{Y~p} sum_i (q_i - 1[Y=i])**2, in exact arithmetic."""
    return sum(p[y] * sum((v - int(i == y)) ** 2
                          for i, v in enumerate(q))
               for y in range(len(p)))


def check():
    count = 0
    strict = 0
    for classes, denominator in ((2, 8), (3, 4), (4, 3)):
        grid = simplex_grid(classes, denominator)
        for p in grid:
            ideal = conditional_expected_brier(p, p)
            for q in grid:
                actual = conditional_expected_brier(p, q)
                square_distance = sum((a - b) ** 2 for a, b in zip(p, q))
                assert actual - ideal == square_distance
                assert actual >= ideal
                assert (actual == ideal) == (p == q)
                count += 1
                strict += int(p != q)
    assert count == 706  # exact audit of 2x8, 3x4 and 4x3 grids
    print(f"ENERGY_BOUND03_RATIONAL_PASS pairs={count} strict_suboptimal={strict}")


if __name__ == "__main__":
    check()
