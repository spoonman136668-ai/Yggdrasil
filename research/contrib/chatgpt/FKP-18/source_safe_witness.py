"""FKP-18 source-safe constructive public witnesses; no held law generator.

These are FROZEN two-step public facts, not new source-private worlds.
See prereg.json. Reward is physically computed from observed register cost.
No counterfactual labels or privileged alternative outcomes are returned.
"""
from __future__ import annotations
from temporal_trace import PublicStep, PublicTransition

STATE = (8, 8, 8, 1, 8, 8, 8, 8)
NO_CHANGE = (8,) * 8


def _reward(before, after):
    return (sum(abs(x - 8) for x in before) -
            sum(abs(x - 8) for x in after)) / 8.0


def _public(before, action, after, prior=()):
    return PublicStep(before, action, after, _reward(before, after),
                      False, tuple(prior))


def conditional_cycle(case):
    if case not in ("A", "B") or type(case) is not str:
        raise ValueError("FKP18_ONLY_FROZEN_CASES")
    mid_target = 2 if case == "A" else 0
    middle = tuple(mid_target if i == 3 else STATE[i] for i in range(8))
    first = _public(STATE, 3, middle)
    prior = PublicTransition(first.before, first.action,
                             first.reward, first.after, first.done)
    second = _public(middle, 3, STATE, (prior,))
    return (first, second)


def temporal_cycle(case):
    if case not in ("AB", "BA") or type(case) is not str:
        raise ValueError("FKP18_ONLY_FROZEN_TEMPORAL_CASES")
    actions = (2, 5) if case == "AB" else (5, 2)
    first = _public(NO_CHANGE, actions[0], NO_CHANGE)
    prior = PublicTransition(first.before, first.action,
                             first.reward, first.after, first.done)
    second = _public(NO_CHANGE, actions[1], NO_CHANGE, (prior,))
    return (first, second)


def safe_fixed_witnesses():
    return {"conditional_A": conditional_cycle("A"),
            "conditional_B": conditional_cycle("B"),
            "temporal_AB": temporal_cycle("AB"),
            "temporal_BA": temporal_cycle("BA")}
