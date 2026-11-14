"""AAI-10P finite compositional causal-intervention BENCHMARK ONLY.

First-use, model training, transfer-cohort execution and Yggdrasil native
integration are not implemented. See prereg.json frozen before this code.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json

BITS = (0, 1)
INPUTS = tuple(itertools.product(BITS, repeat=3))
GOALS = tuple(itertools.product(BITS, repeat=2))
ACTIONS = tuple(itertools.product(range(3), BITS))
LAWS = ("A", "B", "C", "D")
PAIRS = (("A", "B"), ("C", "D"))
COST = 0.05


def require_bits(values, count):
    values = tuple(values)
    if len(values) != count or any(type(x) is not int or x not in BITS for x in values):
        raise ValueError("public binary vector invalid")
    return values


def mediators(law, x):
    """Mechanistic ground truth for simulator only; never passed to learner."""
    x0, x1, x2 = require_bits(x, 3)
    if law == "A":
        return (x0 ^ x1, x1 ^ x2)
    if law == "B":
        return (x0 & x2, x0 ^ x1)
    if law == "C":
        return (x0 | x1, x1 ^ x2)
    if law == "D":
        return (x0 ^ x2, x1 & x2)
    raise ValueError("unknown simulator law")


def reward(m, goal, actions_taken):
    g = require_bits(goal, 2)
    return sum(a == b for a, b in zip(m, g)) - COST * actions_taken


def public_initial(law, x, goal):
    """All learner-visible state, with no hidden law ID."""
    x = require_bits(x, 3)
    goal = require_bits(goal, 2)
    m = mediators(law, x)
    return {"x": list(x), "mediators": list(m), "goal": list(goal),
            "reward": reward(m, goal, 0), "actions_taken": 0}


def public_step(law, state, action):
    """An actual do(input_i := bit) applied to persistent state."""
    if not isinstance(state, dict) or set(state) != {
        "x", "mediators", "goal", "reward", "actions_taken"
    }:
        raise ValueError("public state shape invalid")
    x = list(require_bits(state["x"], 3))
    goal = require_bits(state["goal"], 2)
    if tuple(state["mediators"]) != mediators(law, x):
        raise ValueError("simulator state drift")
    n = state["actions_taken"]
    if type(n) is not int or n not in (0, 1):
        raise ValueError("two-action intervention horizon exceeded")
    if action not in ACTIONS:
        raise ValueError("invalid do-action")
    index, value = action
    x[index] = value
    m = mediators(law, x)
    return {"x": x, "mediators": list(m), "goal": list(goal),
            "reward": reward(m, goal, n + 1), "actions_taken": n + 1}


def public_trace(law, x, goal, actions):
    if len(actions) > 2:
        raise ValueError("horizon exceeded")
    out = [public_initial(law, x, goal)]
    for action in actions:
        out.append(public_step(law, out[-1], action))
    return out


def one_action_score(law, x, goal, action):
    return public_trace(law, x, goal, (action,))[-1]["reward"]


def oracle_action(law, x, goal):
    """Privileged MECHANICAL benchmark reference, not a matched learner."""
    return max(range(len(ACTIONS)),
               key=lambda i: (one_action_score(law, x, goal, ACTIONS[i]), -i))


def intervention_distinguishes(law1, law2, x):
    """Existence of a public do-action that yields different visible outputs."""
    for action in ACTIONS:
        p = public_trace(law1, x, (0, 0), (action,))[-1]["mediators"]
        q = public_trace(law2, x, (0, 0), (action,))[-1]["mediators"]
        if p != q:
            return True
    return False


def stale_policy_regret(true_law, stale_law):
    """Actual reward gain of true-law oracle over wrong-law optimal action."""
    gains = []
    for x in INPUTS:
        for g in GOALS:
            correct = oracle_action(true_law, x, g)
            wrong = oracle_action(stale_law, x, g)
            gains.append(one_action_score(true_law, x, g, ACTIONS[correct]) -
                         one_action_score(true_law, x, g, ACTIONS[wrong]))
    return sum(gains) / len(gains)


def mechanical():
    """Exhaustive structural and held-out benchmark admission, NO science seeds."""
    checks = {}
    checks["pairwise_do_identifiable"] = all(
        intervention_distinguishes(a, b, x)
        for a, b in PAIRS for x in INPUTS
    )
    visibility = {
        a + b: sum(mediators(a, x) != mediators(b, x) for x in INPUTS) / len(INPUTS)
        for a, b in PAIRS
    }
    checks["distinct_law_outputs"] = all(x >= 0.50 for x in visibility.values())
    regret = {a + "_vs_stale_" + b: stale_policy_regret(a, b)
              for a, b in PAIRS for a, b in ((a, b), (b, a))}
    checks["one_action_oracle_headroom"] = all(v >= 0.50 for v in regret.values())
    effects = {}
    for law in LAWS:
        changed_and_helped = 0
        for x in INPUTS:
            for g in GOALS:
                s = public_initial(law, x, g)
                if any((t := public_step(law, s, action))["mediators"] != s["mediators"]
                       and t["reward"] > s["reward"] for action in ACTIONS):
                    changed_and_helped += 1
        effects[law] = changed_and_helped
    checks["consequential_intervention"] = all(n >= 2 for n in effects.values())
    rows = []
    sequential_count = 0
    for law in LAWS:
        for x in INPUTS:
            for g in GOALS:
                s = public_initial(law, x, g)
                assert "law" not in s and "regime" not in s
                for action in ACTIONS:
                    t = public_step(law, s, action)
                    assert t == public_step(law, s, action)
                    rows.append((law, x, g, action, t))
                    for action2 in ACTIONS:
                        u = public_step(law, t, action2)
                        state = list(x)
                        state[action[0]] = action[1]
                        state[action2[0]] = action2[1]
                        assert u["x"] == state
                        assert u["mediators"] == list(mediators(law, state))
                        assert u["reward"] == reward(u["mediators"], g, 2)
                        sequential_count += 1
    checks["sequential_action_semantics"] = sequential_count == 4608
    checks["same_action_same_reward"] = len(rows) == 768
    checks["no_first_use"] = True  # This implementation contains no learner or science API.
    if not all(checks.values()):
        raise AssertionError("mechanical benchmark admission FAILED: " + repr(checks))
    raw = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    return {"schema": "yggdrasil.contrib.aai10p.mechanical.v1",
            "phase": "MECHANICAL_ONLY_NO_LEARNER_FIRST_USE",
            "pairwise_visibility": visibility, "stale_policy_regret": regret,
            "changed_and_helped_by_law": effects,
            "one_action_cases": len(rows), "two_action_cases": sequential_count,
            "official_mechanical_trace_sha256": hashlib.sha256(raw).hexdigest(),
            "checks": checks, "scientific_cohorts_used": 0,
            "native_model_changed": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mechanical", action="store_true")
    parser.add_argument("--primary", action="store_true")
    args = parser.parse_args()
    if args.primary or not args.mechanical:
        parser.error("AAI-10P SCIENTIFIC FIRST USE IS NOT IMPLEMENTED/AUTHORIZED")
    print(json.dumps(mechanical(), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
