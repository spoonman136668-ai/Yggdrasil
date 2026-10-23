"""Symbolic finite-intervention information screen. No generated cohorts or learner."""
from __future__ import annotations

import argparse
from fractions import Fraction
from math import comb
import json

BUDGET = 32
ADVISORY_ERROR = Fraction(1, 20)
WORLDS = {
    "STRONG": (Fraction(1, 4), Fraction(3, 4)),
    "MODERATE": (Fraction(2, 5), Fraction(3, 5)),
    "WEAK": (Fraction(9, 20), Fraction(11, 20)),
    "UNIDENTIFIABLE": (Fraction(1, 2), Fraction(1, 2)),
}
RARE_TRIGGER = Fraction(1, 64)


def validate(n: int, p: Fraction, q: Fraction) -> None:
    if type(n) is not int or n < 0:
        raise ValueError("episode count must be a nonnegative integer")
    if not isinstance(p, Fraction) or not isinstance(q, Fraction):
        raise TypeError("probabilities must be exact Fractions")
    if not (0 <= p <= 1 and 0 <= q <= 1):
        raise ValueError("probabilities outside [0,1]")


def binomial_pmf(n: int, p: Fraction, k: int) -> Fraction:
    validate(n, p, p)
    if type(k) is not int or not 0 <= k <= n:
        raise ValueError("invalid success count")
    return comb(n, k) * p ** k * (1 - p) ** (n - k)


def oracle_bayes_error(n: int, p: Fraction, q: Fraction) -> Fraction:
    """Optimal known-likelihood equal-prior decision risk from n public trials."""
    validate(n, p, q)
    return sum((min(binomial_pmf(n, p, k), binomial_pmf(n, q, k))
                for k in range(n + 1)), Fraction(0)) / 2


def rare_trigger_error(n: int, trigger: Fraction = RARE_TRIGGER) -> Fraction:
    """No observed rare event means identical public transcripts under W0/W1."""
    validate(n, Fraction(0), trigger)
    return (1 - trigger) ** n / 2


def minimum_rare_probes(target: Fraction = ADVISORY_ERROR,
                        trigger: Fraction = RARE_TRIGGER,
                        limit: int = 100_000) -> int:
    if not 0 < target < Fraction(1, 2):
        raise ValueError("target must be strictly between zero and half")
    if not 0 < trigger <= 1:
        raise ValueError("trigger must be positive and <= 1")
    if type(limit) is not int or limit < 0:
        raise ValueError("invalid search bound")
    # Monotone exact arithmetic, no log rounding at the inequality boundary.
    survival = Fraction(1)
    for n in range(limit + 1):
        if survival / 2 <= target:
            return n
        survival *= 1 - trigger
    raise ValueError("no qualifying n within search bound")


def ratio(x: Fraction) -> dict:
    return {"numerator": x.numerator, "denominator": x.denominator,
            "decimal": format(float(x), ".12f")}


def audit() -> dict:
    cases = {}
    for name, (p, q) in WORLDS.items():
        err = oracle_bayes_error(BUDGET, p, q)
        cases[name] = {"p_world0": ratio(p), "p_world1": ratio(q),
                       "bayes_error_at_32_probes": ratio(err),
                       "oracle_advisory_le_5pct": err <= ADVISORY_ERROR}
    rare = rare_trigger_error(BUDGET)
    needed = minimum_rare_probes()
    if not (rare_trigger_error(needed) <= ADVISORY_ERROR
            and rare_trigger_error(needed - 1) > ADVISORY_ERROR):
        raise AssertionError("minimum probe bound is incorrect")
    return {
        "schema": "mass.r10.finite-probe-source-only.v1",
        "probe_budget": BUDGET,
        "finite_identification_cases": cases,
        "rare_latent_world": {
            "hidden_trigger_probability": ratio(RARE_TRIGGER),
            "bayes_error_at_32_probes": ratio(rare),
            "minimum_probes_for_error_le_5pct": needed,
            "error_at_predecessor_n": ratio(rare_trigger_error(needed - 1)),
            "error_at_minimum_n": ratio(rare_trigger_error(needed)),
        },
        "advisory_error_target_only": ratio(ADVISORY_ERROR),
        "population_identifiability_does_not_ensure_32_probe_identification": True,
        "actual_r10_source_certificate": "NOT_ESTABLISHED",
        "scientific_first_use": False,
        "sampled_experiment_rows": 0,
        "privileged_known_likelihood_oracle_only": True,
        "ckb_controller_admission": "NOT_OBSERVED",
        "original_r7_r9_data_reused": False,
        "source_generator_created": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", action="store_true", required=True)
    parser.parse_args()
    print(json.dumps(audit(), sort_keys=True, indent=2))
