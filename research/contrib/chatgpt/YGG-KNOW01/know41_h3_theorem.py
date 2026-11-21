"""KNOW41 V1/H3 pre-primary impossibility certificate; pure source-free algebra.

No seed, Bernoulli coin, learned model, original dataset, or held outcome is opened.
This theorem only evaluates the fully public frozen structural causal equations.
"""
from fractions import Fraction

from know41_active_identifiability_dev import expected_milli, need

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
