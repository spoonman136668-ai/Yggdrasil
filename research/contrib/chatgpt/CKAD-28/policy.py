"""CKAD28: decision-relevant intervention scoring on native retained hypotheses.

Candidate exploration is read-only and uses only actual public history.
This policy does not change the native learner, its hypothesis space,
its detector or its historical weights. No source-family/phase/labels leak.
"""
from fractions import Fraction
from hashlib import sha256

ARMS = ("decision", "native", "random")
QUARTER_EXPLOIT = 4


def require(ok, reason):
    if not ok:
        raise ValueError("CKAD28_POLICY_" + reason)


def posterior(model, view, first, state):
    require(type(view) is tuple and len(view) == 2 and
            all(type(x) is int and x in (0, 1) for x in view),
            "PUBLIC_VIEW")
    require(type(first) is int and first in (0, 1) and
            type(state) is int and state in (0, 1), "PUBLIC_ACTION")
    ex = model._experience
    require(ex is not None, "EXPERIENCE")
    w = ex._context_weights_for(view, first, state)
    p0 = ex._context_predictions(view, first, state, 0)
    p1 = ex._context_predictions(view, first, state, 1)
    require(len(w) > 0 and len(w) == len(p0) == len(p1) and
            all(type(v) is Fraction and 0 <= v <= 1
                for v in (*w, *p0, *p1)) and
            sum(w, Fraction(0)) == 1, "POSTERIOR")
    return w, p0, p1


def value_perfect_information(model, view, first, state):
    """Value of knowing each model's optimal second action, not raw variance."""
    w, p0, p1 = posterior(model, view, first, state)
    mean0 = sum((a * b for a, b in zip(w, p0)), Fraction(0))
    mean1 = sum((a * b for a, b in zip(w, p1)), Fraction(0))
    oracle = sum((weight * max(a, b)
                  for weight, a, b in zip(w, p0, p1)), Fraction(0))
    value = oracle - max(mean0, mean1)
    require(value >= 0, "NEGATIVE_INFORMATION_VALUE")
    return value


def decision_first(model, view):
    require(type(view) is tuple and len(view) == 2, "PUBLIC_VIEW")
    choices = []
    for first in (0, 1):
        p = model.experience_context_forecast(view, first)
        require(type(p) is Fraction and 0 <= p <= 1, "TRANSITION")
        score = ((1 - p) * value_perfect_information(model, view, first, 0)
                 + p * value_perfect_information(model, view, first, 1))
        choices.append(score)
    if choices[0] == choices[1]:
        return model.experience_context_explore(view)
    return int(choices[1] > choices[0])


def decision_second(model, view, first, state):
    """Penalize immediate reward regret; reward irrelevant variance is discarded."""
    w, p0, p1 = posterior(model, view, first, state)
    means = [sum((weight * p for weight, p in zip(w, probs)), Fraction(0))
             for probs in (p0, p1)]
    best = int(means[1] > means[0])  # deterministic tie
    informed = []
    for action, probs in enumerate((p0, p1)):
        variance = sum((weight * (prediction - means[action]) ** 2
                        for weight, prediction, x, y
                        in zip(w, probs, p0, p1)
                        if int(y > x) != best), Fraction(0))
        regret = means[best] - means[action]
        informed.append(variance - regret)
    if max(informed) <= 0 or informed[0] == informed[1]:
        return best
    return int(informed[1] > informed[0])


def random_bits(namespace, index):
    require(type(namespace) is str and namespace.isascii() and
            type(index) is int and index >= 0, "RANDOM_SOURCE")
    raw = sha256(f"ckad28-action-v1/{namespace}/{index}".encode("ascii")).digest()
    return raw[0] & 1, raw[1] & 1


def choices(model, view, arm, namespace, index):
    require(arm in ARMS and type(index) is int and index >= 0, "ARM")
    if index % QUARTER_EXPLOIT == 3:
        plan = model.experience_context_plan(view)
        return (lambda _initial: plan["first_action"],
                lambda _initial, first, state: plan["second_actions"][first][state])
    if arm == "decision":
        return (lambda _initial: decision_first(model, view),
                lambda _initial, first, state:
                    decision_second(model, view, first, state))
    if arm == "native":
        return (lambda _initial: model.experience_context_explore(view),
                lambda _initial, first, state:
                    model.experience_context_explore(view, first, state))
    first, second = random_bits(namespace, index)
    return (lambda _initial: first, lambda _initial, _first, _state: second)
