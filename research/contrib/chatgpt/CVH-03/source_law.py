"""CVH-03: exact source-law analysis of PINNED publicly readable CausalGym MDP.

No third-party environment import, object construction, seed, reset, or do.
This is a retrospective analytical check, not scientific source first-use.
"""
from __future__ import annotations
from fractions import Fraction as F
from itertools import product
from typing import Dict, Tuple

SOURCE_REPO = "CausalAILab/Causal-Gymnasium"
SOURCE_SHA = "c94e9a4cd3641588b6b8507e71ccee5c27032bdf"
SOURCE_PATH = "causal_gym/envs/mdp.py"
SOURCE_GIT_BLOB = "6264ec5450754c009e98c3e85f6d5927ece0a9ab"
MAX_STEP = 30
ACTUAL_HORIZON = MAX_STEP + 1  # original step: num_step += 1; truncation if num_step > max_step


def source_law(s: int, action: int, u1: int, u2: int, u3: int) -> tuple[int, int]:
    """Manually transcribed ORIGINAL reward and next-state Boolean equations."""
    if any(type(x) is not int or x not in (0, 1) for x in (s, action, u1, u2, u3)):
        raise ValueError("CVH03_BINARY_INPUT_REQUIRED")
    reward = int(bool(((s != action) != u1) != u3))
    next_state = int(bool((u1 != u2) != (s | action)))
    return reward, next_state


def exogenous_outcomes(prob1=F(9, 10), prob2=F(1, 10), prob3=F(1, 10)):
    probs = (prob1, prob2, prob3)
    if any(type(q) is not F or not 0 <= q <= 1 for q in probs):
        raise ValueError("CVH03_EXOGENOUS_PROB_INVALID")
    for values in product((0, 1), repeat=3):
        weight = F(1)
        for value, prob in zip(values, probs):
            weight *= prob if value else 1 - prob
        yield values, weight


def joint_kernel(s, action, *, probs=(F(9, 10), F(1, 10), F(1, 10))):
    if type(s) is not int or type(action) is not int or s not in (0, 1) or action not in (0, 1):
        raise ValueError("CVH03_INVALID_STATE_ACTION")
    out = {(r, ns): F(0) for r in (0, 1) for ns in (0, 1)}
    for (u1, u2, u3), weight in exogenous_outcomes(*probs):
        r, ns = source_law(s, action, u1, u2, u3)
        out[(r, ns)] += weight
    if sum(out.values()) != 1:
        raise AssertionError("CVH03_NONNORMALIZED_JOINT_KERNEL")
    return out


def reward_expectation(s, action, *, probs=(F(9, 10), F(1, 10), F(1, 10))):
    return sum((p for (r, _), p in joint_kernel(s, action, probs=probs).items() if r == 1), F(0))


def next_state_one_probability(s, action):
    return sum((p for (_, ns), p in joint_kernel(s, action).items() if ns == 1), F(0))


def independent_bellman(horizon=ACTUAL_HORIZON):
    """All actions optimized independently via joint kernel, no policy shortcut."""
    if type(horizon) is not int or not 0 <= horizon <= ACTUAL_HORIZON:
        raise ValueError("CVH03_HORIZON_RANGE")
    value = {0: F(0), 1: F(0)}
    audit = []
    for remaining in range(1, horizon + 1):
        new = {}
        details = {}
        for s in (0, 1):
            Q = {}
            for a in (0, 1):
                Q[a] = sum((p * (r + value[ns]) for (r, ns), p in joint_kernel(s, a).items()), F(0))
            optimal = max(Q, key=Q.get)
            details[s] = {"q_match": Q[s], "q_opposite": Q[1 - s], "optimal_action": optimal}
            new[s] = Q[optimal]
        audit.append((remaining, details, new))
        value = new
    return audit


def analytic_result():
    expected = {}
    for s, a in product((0, 1), repeat=2):
        expected[f"s{s}_a{a}"] = {
            "p_reward_1": reward_expectation(s, a),
            "p_next_state_1": next_state_one_probability(s, a),
            "joint_kernel": joint_kernel(s, a),
        }
    dp = independent_bellman()
    for horizon, details, values in dp:
        for state in (0, 1):
            assert values[state] == horizon * F(41, 50)
            assert details[state]["optimal_action"] == state
            assert details[state]["q_match"] - details[state]["q_opposite"] == F(16, 25)
    return {
        "upstream_repo": SOURCE_REPO,
        "upstream_sha": SOURCE_SHA,
        "upstream_git_blob": SOURCE_GIT_BLOB,
        "classification": "READ_ONLY_FORMAL_SOURCE_LAW_CEILING_NOT_SCIENCE_FIRST_USE",
        "per_state_action": expected,
        "horizon": ACTUAL_HORIZON,
        "optimal_policy": "action == current state",
        "optimal_per_step_mean": F(41, 50),
        "opposite_per_step_mean": F(9, 50),
        "uniform_random_per_step_mean": F(1, 2),
        "optimal_full_episode_mean": F(41, 50) * ACTUAL_HORIZON,
        "opposite_full_episode_mean": F(9, 50) * ACTUAL_HORIZON,
        "uniform_random_full_episode_mean": F(1, 2) * ACTUAL_HORIZON,
        "unique_action_advantage_every_horizon": F(16, 25),
        "all_31_horizons_match_state_optimal": True,
        "actual_source_actions": 0,
        "scientific_pass": False,
    }


def _convert(v):
    if isinstance(v, F):
        return str(v)
    if isinstance(v, dict):
        return {str(k): _convert(x) for k, x in v.items()}
    if isinstance(v, (tuple, list)):
        return [_convert(x) for x in v]
    return v


if __name__ == "__main__":
    import json
    print(json.dumps(_convert(analytic_result()), sort_keys=True, indent=2))
