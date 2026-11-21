"""KNOW41 V1/H3 pre-primary impossibility certificate; pure source-free algebra.

No seed, Bernoulli coin, learned model, original dataset, or held outcome is opened.
This theorem only evaluates the fully public frozen structural causal equations.
"""
from fractions import Fraction

from know41_active_identifiability_dev import expected_milli, need

import hashlib
from pathlib import Path

CANDIDATE_V1_BLOB = "034e3e9c7b34bc9a6d419c359a8cd6431200de96"
CANDIDATE_V1_FILE = (Path(__file__).resolve().parent /
                     "know41_active_models_dev.py")


def candidate_forced_exploration_no_go():
    """Analytically reject candidate V1 before ANY frozen FIT/HELD first use.

    The candidate source blob is pinned so this proof may never be applied
    to a different policy. Source-free public SCM, no sampled consequence.
    """
    source = CANDIDATE_V1_FILE.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(source)).encode() +
                        b"\0" + source).hexdigest()
    need(blob == CANDIDATE_V1_BLOB and
         b'a = 1 if (t // 8) % 4 == 0 else int(p1 - .05 > p0)' in source,
         "CANDIDATE_POLICY_DRIFT")
    forced = tuple(t for t in range(192, 256) if (t // 8) % 4 == 0)
    need(forced == tuple(range(192, 200)) + tuple(range(224, 232)),
         "FORCED_TIMELINE")
    static = certificate()
    cohorts = {}
    for theta in (0, 1):
        floor = sum((regret_for_context(theta, t % 8, 1)
                     for t in forced), Fraction(0)) / 64
        no_memory = static[str(theta)]["no_memory_regret"]
        maximum_advantage = no_memory - floor
        cohorts[str(theta)] = {
            "forced_actions": len(forced),
            "forced_regret_floor": floor,
            "no_memory_regret": no_memory,
            "maximum_candidate_advantage_over_no_memory": maximum_advantage,
            "h3_margin": NEW_H3,
            "h3_feasible_under_current_policy": maximum_advantage >= NEW_H3,
        }
    need(cohorts["0"]["forced_regret_floor"] == Fraction(7, 320) and
         cohorts["1"]["forced_regret_floor"] == Fraction(7, 320) and
         cohorts["1"]["maximum_candidate_advantage_over_no_memory"] ==
         Fraction(1, 320) and
         cohorts["1"]["maximum_candidate_advantage_over_no_memory"] < NEW_H3,
         "CANDIDATE_NO_GO_PROOF")
    return {
        "candidate_blob": CANDIDATE_V1_BLOB,
        "candidate_status": "ANALYTIC_NO_GO_UNDER_FROZEN_KNOW41_V3_H3",
        "scientific_gain_verified": False,
        "held_first_use_consumed": False,
        "cohorts": cohorts,
    }




OLD_H3 = Fraction(1, 20)  # .05
NEW_H3 = Fraction(1, 100)  # .01, prospectively frozen in v3


def regret_for_context(theta, c, action):
    need(type(theta) is int and theta in (0, 1), "THEOREM_THETA")
    need(type(c) is int and 0 <= c < 8, "THEOREM_CONTEXT")
    need(type(action) is int and action in (0, 1), "THEOREM_ACTION")
    q0 = Fraction(expected_milli("FORK", c, 0, theta), 1000)
    q1 = Fraction(expected_milli("FORK", c, 1, theta), 1000) - Fraction(1, 20)
    return max(q0, q1) - (q0 if action == 0 else q1)


def mean_regret(theta, choice):
    return sum((regret_for_context(theta, c, choice(c))
                for c in range(8)), Fraction(0, 1)) / 8


def certificate():
    out = {}
    for theta in (0, 1):
        q1_hist = {}
        for c in range(8):
            q1 = expected_milli("FORK", c, 1, theta)
            q1_hist[q1] = q1_hist.get(q1, 0) + 1
        passive = mean_regret(theta, lambda c: 0)
        no_memory = mean_regret(theta, lambda c: int(c % 4 == 0))
        oracle = mean_regret(theta, lambda c: int(
            expected_milli("FORK", c, 1, theta) - 50 >
            expected_milli("FORK", c, 0, theta)))
        need(q1_hist == {150: 2, 350: 4, 550: 2} and
             passive == Fraction(3, 80) and
             oracle == Fraction(0), "THEOREM_BASELINE")
        out[str(theta)] = {
            "action1_q_milli_histogram": q1_hist,
            "oracle_regret": oracle,
            "passive_regret": passive,
            "no_memory_regret": no_memory,
            "maximum_improvement_over_passive": passive,
        }
    need(out["0"]["no_memory_regret"] == Fraction(3, 40) and
         out["1"]["no_memory_regret"] == Fraction(1, 40) and
         OLD_H3 > out["0"]["passive_regret"] and
         OLD_H3 > out["1"]["no_memory_regret"] and
         NEW_H3 < out["1"]["no_memory_regret"],
         "THEOREM_IMPOSSIBILITY")
    return out
