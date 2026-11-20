"""KNOW30: exact two-step counterexample to greedy diagnostic information selection.

Analytic only; NO new synthetic HELD, original-world first-use or native model.
Frozen prereg first at 0afe86c11675be82774f6d44fd2daa8aa80658f2.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha1
import json
from pathlib import Path

PREREG_COMMIT = "0afe86c11675be82774f6d44fd2daa8aa80658f2"
PREREG_BLOB = "e3d5edd09ad7dab0b38bcfa59e73394bbdbbcc16"
SCHEMA = "yggdrasil.know30.finite-horizon-action-information-analytic-prereg.v1"
WORLDS = tuple(range(6))
TARGET = (1, 1, 0, 0, 0, 0)
ACTIONS = {
    "a": (1, 0, 0, 0, 0, 0),
    "b": (0, 1, 0, 0, 0, 0),
    "c": (1, 1, 1, 0, 0, 0),
}


def verify_frozen_protocol():
    path = (Path(__file__).resolve().parents[3] / "roadmap" /
            "YGG_KNOW30_FINITE_HORIZON_DIAGNOSTIC_PREREG_2026-11-20.json")
    raw = path.read_bytes()
    got = sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    if got != PREREG_BLOB:
        raise ValueError("KNOW30_PREREG_BLOB_DRIFT")
    protocol = json.loads(raw)
    table = protocol["toy_worlds"]
    if (protocol["schema"] != SCHEMA or table["world_ids"] != list(WORLDS)
            or table["target_bits_by_world"] != list(TARGET)
            or [(a["id"], a["observed_bits_by_world"]) for a in table["actions"]]
               != [(k, list(v)) for k, v in ACTIONS.items()]
            or protocol["execution"]["source_first_use"] is not False):
        raise ValueError("KNOW30_PREREG_CONTRACT_DRIFT")
    return protocol


def brier(states):
    """Posterior Bayes Brier risk for the public binary target query."""
    if not states:
        raise ValueError("KNOW30_EMPTY_POSTERIOR")
    n = len(states)
    ones = sum(TARGET[i] for i in states)
    return Fraction(ones * (n - ones), n * n)


def partition(states, action):
    if action not in ACTIONS:
        raise ValueError("KNOW30_UNKNOWN_ACTION")
    return tuple(tuple(i for i in states if ACTIONS[action][i] == bit)
                 for bit in (0, 1))


def evidence_update(states, action, observed_bit):
    """Only the public diagnostic outcome may update a learner's support."""
    if type(observed_bit) is not int or observed_bit not in (0, 1):
        raise ValueError("KNOW30_INVALID_WITNESS")
    next_states = partition(states, action)[observed_bit]
    if not next_states:
        raise ValueError("KNOW30_IMPOSSIBLE_WITNESS")
    return next_states


def optimal_risk(states, actions, observations_left):
    """Exact optimal public-observation-conditioned decision tree risk."""
    if observations_left == 0:
        return brier(states)
    if observations_left < 0 or observations_left > len(actions):
        raise ValueError("KNOW30_ACTION_BUDGET")
    return min(
        after_action(states, action, tuple(a for a in actions if a != action),
                     observations_left - 1)
        for action in actions
    )


def after_action(states, action, remaining, observations_left):
    """Expected risk conditional on choosing one specified next public action."""
    return sum(
        (Fraction(len(part), len(states)) *
         optimal_risk(part, remaining, observations_left))
        for part in partition(states, action) if part
    )


def greedy_action(states, actions):
    return min(actions, key=lambda a: (after_action(states, a, (), 0), a))


def analytic_result():
    verify_frozen_protocol()
    one = {a: after_action(WORLDS, a, (), 0) for a in ACTIONS}
    two = {a: after_action(
        WORLDS, a, tuple(b for b in ACTIONS if b != a), 1)
        for a in ACTIONS}
    greedy = greedy_action(WORLDS, tuple(ACTIONS))
    best = min(ACTIONS, key=lambda a: (two[a], a))
    assert greedy == "c" and best == "a"
    assert one == {"a": Fraction(2, 15), "b": Fraction(2, 15),
                   "c": Fraction(1, 9)}
    assert two == {"a": Fraction(0), "b": Fraction(0),
                   "c": Fraction(1, 12)}
    return {
        "schema": "yggdrasil.know30.analytic-greedy-horizon-counterexample.v1",
        "prereg_commit": PREREG_COMMIT,
        "prereg_blob": PREREG_BLOB,
        "source_mode": "EXACT_RATIONAL_ANALYTIC_NO_HELD_TRIALS",
        "one_step_risks": {k: str(v) for k, v in one.items()},
        "two_step_optimal_conditional_risks": {k: str(v) for k, v in two.items()},
        "greedy_first": greedy,
        "optimal_two_step_first": best,
        "two_step_avoidable_risk": str(two[greedy] - two[best]),
        "engineering_result": "EXACT_ENUMERATION_PASS",
        "scientific_result": "NO_NATIVE_GAIN_OR_CAUSAL_ATTRIBUTION",
        "original_world_first_use": False,
        "accepted_native_modified": False,
        "deployment": "NONE",
    }


if __name__ == "__main__":
    print(json.dumps(analytic_result(), sort_keys=True))
