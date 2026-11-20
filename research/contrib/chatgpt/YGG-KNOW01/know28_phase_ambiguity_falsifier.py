"""KNOW28: analytic phase-ambiguity falsifier; no new simulator first-use.

Frozen prereg was committed before this source at
41fbc89a22aa915234454dbf1d41e9a0ad559d8d.
A synthetic structural counterexample is NOT new native Yggdrasil training.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Callable

SCHEMA = "yggdrasil.know28.phase-ambiguity-analytic-result.v1"
PREREG = "41fbc89a22aa915234454dbf1d41e9a0ad559d8d"
PREREG_BLOB = "34bc59c3fdcf05d1613eb386aa5dd456a4941e71"
PROTO = "yggdrasil.know28.unannounced-return-identifiability.v1"
Q_A, Q_B = Fraction(3, 20), Fraction(17, 20)


def protocol() -> dict:
    path = Path(__file__).with_name("know28_phase_ambiguity_protocol.json")
    content = path.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(content)).encode("ascii")
                        + b"\x00" + content).hexdigest()
    if blob != PREREG_BLOB:
        raise ValueError("KNOW28_PREREG_BLOB_CHANGED")
    data = json.loads(content)
    if (data.get("schema") != PROTO
            or data["branches"]["context"] != 4
            or data["branches"]["action"] != 0
            or data["branches"]["probabilities"] != {"A": 0.15, "B": 0.85}
            or data["score"]["phase_blind_lower_bound"] != 0.25
            or data["custody"]["new_held_trials"] != 0):
        raise ValueError("KNOW28_PREREG_DRIFT")
    return data


def causal_bit(law: str, context: int) -> int:
    if law not in ("H0", "H2") or type(context) is not int or not 0 <= context < 8:
        raise ValueError("KNOW28_BAD_CAUSAL_INPUT")
    x0, x1, x2 = context & 1, (context >> 1) & 1, (context >> 2) & 1
    return (x0 ^ (x1 & x2)) if law == "H0" else (1 ^ (x0 & x2))


def expected_brier(p: Fraction, q: Fraction) -> Fraction:
    if not isinstance(p, Fraction) or not isinstance(q, Fraction) or not (
            0 <= p <= 1 and 0 <= q <= 1):
        raise ValueError("KNOW28_PROBABILITY")
    return q * (1 - q) + (p - q) ** 2


def phase_blind_fork_brier(p: Fraction) -> Fraction:
    """The same pre-return forecast p must be scored on BOTH hidden branches."""
    return (expected_brier(p, Q_A) + expected_brier(p, Q_B)) / 2


def exact_certificate(p: Fraction) -> tuple[Fraction, Fraction]:
    """Universal identity: fork risk = 1/4+(p-1/2)^2, hence >=1/4."""
    risk = phase_blind_fork_brier(p)
    expression = Fraction(1, 4) + (p - Fraction(1, 2)) ** 2
    if risk != expression:
        raise ArithmeticError("KNOW28_NOT_IDENTICAL")
    return risk, expression


def two_indistinguishable_forks(public_prefix: tuple, next_public: tuple) -> tuple:
    """The evaluator branches privately AFTER the last public observation.

    No private regime identifier enters either policy input. The caller must
    supply an already witnessed prefix, not a synthetic outcome generator.
    """
    if not isinstance(public_prefix, tuple) or not isinstance(next_public, tuple):
        raise ValueError("KNOW28_PUBLIC_INPUT")
    return ((public_prefix, next_public), (public_prefix, next_public))


def common_pre_return_forecast(public_prefix: tuple, next_public: tuple,
                               phase_blind_policy: Callable) -> tuple:
    """Both forks call the same policy with exactly the same visible inputs."""
    left, right = two_indistinguishable_forks(public_prefix, next_public)
    a = phase_blind_policy(*left)
    b = phase_blind_policy(*right)
    if not isinstance(a, Fraction) or not 0 <= a <= 1 or a != b:
        raise ValueError("KNOW28_POLICY_USED_HIDDEN_BRANCH_OR_NONDETERMINISM")
    return (a, b)


def proof() -> dict:
    protocol()
    if causal_bit("H0", 4) != 0 or causal_bit("H2", 4) != 1:
        raise AssertionError("KNOW28_FROZEN_LAWS")
    for p in [Fraction(0), Q_A, Fraction(1, 4), Fraction(1, 2),
              Fraction(3, 4), Q_B, Fraction(1)]:
        left, right = exact_certificate(p)
        if left != right or left < Fraction(1, 4):
            raise AssertionError("KNOW28_FORK_BOUND")
    forks = common_pre_return_forecast(
        ((0, 0, 0, 0), (1, 1, 2, 1)), (24, 4, 0),
        lambda prefix, view: Fraction(1, 2))
    if forks[0] != forks[1]:
        raise AssertionError("KNOW28_HIDDEN_FORK_LEAK")
    blind_min = phase_blind_fork_brier(Fraction(1, 2))
    oracle = (expected_brier(Q_A, Q_A) + expected_brier(Q_B, Q_B)) / 2
    if (blind_min, oracle, blind_min - oracle) != (
            Fraction(1, 4), Fraction(51, 400), Fraction(49, 400)):
        raise AssertionError("KNOW28_FROZEN_MARGINS")
    return {
        "schema": SCHEMA,
        "prereg_commit": PREREG,
        "prereg_blob": PREREG_BLOB,
        "context": 4,
        "hidden_forks": ["return_A", "continue_B"],
        "phase_blind_min_brier": float(blind_min),
        "privileged_phase_oracle_brier": float(oracle),
        "irreducible_preobservation_gap": float(blind_min - oracle),
        "result": "IDENTIFIABILITY_LIMIT_CONFIRMED",
        "new_held_trials": 0,
        "new_action_witnesses": 0,
        "old_A_archive_readout_is_not_live_pre_return_forecast": True,
        "native_modified": False,
        "scientific_gain_verified": False,
        "deployment": "NONE",
    }


if __name__ == "__main__":
    print(json.dumps(proof(), sort_keys=True))
