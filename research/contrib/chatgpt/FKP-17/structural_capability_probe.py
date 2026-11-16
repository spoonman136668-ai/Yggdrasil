"""FKP-17 constructive causal-representation limitation audit (public only).

This is a mathematical counterexample for a frozen learned representation,
not an experiment on fresh DEV/TRANSFER worlds. It constructs two physically
consistent PUBLIC two-step trajectories with identical action/register/delta
marginals but different state-conditioned effects. It also checks order loss.
A separate competent Bayesian state-conditional control retains the difference.
No evaluator source, protected seed, reward oracle, or native integration.
"""
from __future__ import annotations

from typing import NamedTuple

STATE = (8, 8, 8, 1, 8, 8, 8, 8)
NO_CHANGE = (8,) * 8
TARGET_REG = 3
TARGET_ACTION = 3
HOLD_ACTION = 4


class PublicTransition(NamedTuple):
    before: tuple[int, ...]
    action: int
    reward: float
    after: tuple[int, ...]
    done: bool


class PublicStep(NamedTuple):
    before: tuple[int, ...]
    action: int
    after: tuple[int, ...]
    reward: float
    done: bool
    history: tuple[PublicTransition, ...]


def _reward(before, after):
    old = sum(abs(v - 8) for v in before)
    new = sum(abs(v - 8) for v in after)
    return (old - new) / 8.0


def _make_step(before, action, after, history):
    return PublicStep(before, action, after, _reward(before, after),
                      False, tuple(history[-16:]))


def _transition_history(row):
    return PublicTransition(row.before, row.action, row.reward,
                            row.after, row.done)


def conditional_cycle(first_target):
    """Two actual local actions return to same public state, conserving sums.

    Law A: register-3 1 -> 2 -> 1. Law B: 1 -> 0 -> 1.
    Both emit one delta +1 and one delta -1 on action 3, sum earned
    rewards to zero, and have identical chosen-action multiset and endpoint.
    Yet on future state register3=1, A gives action3 +1/8 reward while B
    gives action3 -1/8; safe action4 yields zero in BOTH.
    """
    if type(first_target) is not int or first_target not in (0, 2):
        raise ValueError("FKP17_CAPABILITY_INVALID_PUBLIC_PAIR")
    middle = tuple(first_target if i == TARGET_REG else STATE[i]
                   for i in range(len(STATE)))
    first = _make_step(STATE, TARGET_ACTION, middle, ())
    second = _make_step(middle, TARGET_ACTION, STATE,
                        (_transition_history(first),))
    return (first, second)


def temporal_cycle(first_action):
    """Same public action multiset and final state, different latest cause."""
    if type(first_action) is not int or first_action not in (2, 5):
        raise ValueError("FKP17_CAPABILITY_INVALID_TEMPORAL_PAIR")
    second_action = 5 if first_action == 2 else 2
    first = _make_step(NO_CHANGE, first_action, NO_CHANGE, ())
    second = _make_step(NO_CHANGE, second_action, NO_CHANGE,
                        (_transition_history(first),))
    return (first, second)


def _replay(arm, rows, query):
    arm.begin_world()
    for index, row in enumerate(rows):
        if index and rows[index - 1].after != row.before:
            raise ValueError("FKP17_CAPABILITY_NONPHYSICAL_TRAJECTORY")
        if row.history != tuple(_transition_history(x)
                                for x in rows[max(0, index - 16):index]):
            raise ValueError("FKP17_CAPABILITY_HISTORY_LEAK_OR_DISORDER")
        arm.observe_public(row)
    if rows[-1].after != query:
        raise ValueError("FKP17_CAPABILITY_DIFFERENT_QUERY_STATE")
    before = arm.state_receipt()
    selected = arm.choose_public(query)
    if arm.state_receipt() != before:
        raise ValueError("FKP17_CAPABILITY_CHOICE_MUTATED_STATE")
    return before, selected


def audit_frozen_public_arms(structured, independent_symbolic):
    """Audit learner *representation*, not scientific/held-source return.

    An exact collision is stronger than a noisy benchmark result: both
    distinct causal histories map to the SAME complete frozen learner state.
    Such a policy cannot select different optimal actions on identical current
    public register states, irrespective of training amount or future tuning.
    """
    if getattr(structured, "variant", None) != "STRUCTURED":
        raise ValueError("FKP17_CAPABILITY_FROZEN_STRUCTURED_ARM_REQUIRED")
    if getattr(structured, "received_foundation_count", None) != 32768:
        raise ValueError("FKP17_CAPABILITY_FULL_PUBLIC_PRIOR_REQUIRED")
    if getattr(independent_symbolic, "foundation_count", None) != 32768:
        raise ValueError("FKP17_CAPABILITY_FULL_SYMBOLIC_PRIOR_REQUIRED")
    prior_digest = structured.foundation_sha256
    if independent_symbolic.foundation_sha256 != prior_digest:
        raise ValueError("FKP17_CAPABILITY_PRIOR_DIGEST_MISMATCH")
    a, b = conditional_cycle(2), conditional_cycle(0)
    if a[0].after == b[0].after:
        raise AssertionError("FKP17_CAPABILITY_NOT_TWO_CAUSAL_LAWS")
    if not (a[0].reward > 0 and b[0].reward < 0):
        raise AssertionError("FKP17_CAPABILITY_MISSING_DIFFERENT_ACTION_CONSEQUENCES")
    struct_a = _replay(structured, a, STATE)
    struct_b = _replay(structured, b, STATE)
    bayes_a = _replay(independent_symbolic, a, STATE)
    bayes_b = _replay(independent_symbolic, b, STATE)
    temporal_ab = _replay(structured, temporal_cycle(2), NO_CHANGE)
    temporal_ba = _replay(structured, temporal_cycle(5), NO_CHANGE)
    conditional_collision = (struct_a == struct_b)
    temporal_collision = (temporal_ab == temporal_ba)
    symbolic_distinguishes = (bayes_a[0] != bayes_b[0])
    if not (conditional_collision and temporal_collision and
            symbolic_distinguishes):
        raise AssertionError("FKP17_CAPABILITY_EXPECTED_PROOF_DRIFT")
    return {
        "schema": "fkp17.structural-representation-collision.v1",
        "classification": "STRUCTURED_REPRESENTATION_NOT_READY_FOR_DELAYED_CONTEXT_LAW",
        "candidate": "STRUCTURED",
        "source_prior_public_sha256": prior_digest,
        "source_prior_records_each": 32768,
        "public_observed_actions_per_counterexample": 2,
        "identical_current_public_state": True,
        "identical_public_action_marginals": True,
        "identical_observed_reward_sum": True,
        "candidate_same_complete_state_after_distinct_conditional_laws":
            conditional_collision,
        "candidate_same_choice_after_distinct_conditional_laws":
            struct_a[1] == struct_b[1],
        "independent_conditional_symbolic_control_distinguishes":
            symbolic_distinguishes,
        "candidate_same_complete_state_after_reordered_events":
            temporal_collision,
        "candidate_same_choice_after_reordered_events":
            temporal_ab[1] == temporal_ba[1],
        "true_next_action3_rewards_for_two_laws":
            [a[0].reward, b[0].reward],
        "safe_action4_reward_both_laws": 0.0,
        "distinct_optimal_action_under_two_laws": [3, 4],
        "proof_scope": "CONSTRUCTIVE_PUBLIC_TOY_COUNTEREXAMPLE_NOT_PROTECTED_DATA",
        "held_dev_opened": False,
        "reserved_transfer_opened": False,
        "scientific_pass": False,
        "native_model_promoted": False,
    }


def require_unfamiliar_law_representational_readiness(proof):
    """Positive known-family scores cannot waive an explicit collision."""
    if proof.get("classification") == (
            "STRUCTURED_REPRESENTATION_NOT_READY_FOR_DELAYED_CONTEXT_LAW"):
        raise ValueError("FKP17_STRUCTURED_DELAYED_CONTEXT_REPRESENTATION_NO_GO")
    raise ValueError("FKP17_UNVERIFIED_OTHER_REPRESENTATION")
