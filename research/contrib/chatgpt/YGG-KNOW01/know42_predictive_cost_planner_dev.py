"""KNOW42 development control: cost-sensitive finite-horizon predictive action choice.

Conventional Bayes planning, NOT a novel learner or native integration.
Extends the KNOW30 diagnostic principle from terminal Brier risk to net utility.
Inputs: public future contexts represented by a model's *forecast hypotheses*,
posterior weights, and public action costs. No hidden-world label, sampler,
protected seeds, time-phase exploration rule, or actual future outcome input.
Assumes a stationary latent hypothesis for the bounded planning horizon.
"""
from fractions import Fraction
from functools import lru_cache

MAX_HORIZON = 5
MAX_HYPOTHESES = 8


def _need(ok, reason):
    if not ok:
        raise ValueError("KNOW42_" + reason)


def plan(weights, forecasts, costs=(0, 50), policy="optimal"):
    """Exact expected cumulative net utility, action and conditional values.

    weights: tuple of strictly positive Fraction posterior probabilities summing to 1.
    forecasts: tuple of 1..5 public-context steps, each containing one pair of
       integer milli-probability forecasts (a0, a1) per hypothesis, in weight order.
    costs: pair of integer milli-utility costs (nonnegative at most 1000).
    policy: optimal bounded-horizon, or greedy present-utility on SAME belief.
    Ties choose a0. Each hypothetical observation branch is weighted by its
    predictive probability; these are expectations, NOT generated observations.
    The caller owns witness validation and posterior/memory state; the function
    cannot authenticate whether its input model was legitimately trained.
    """
    _need(type(weights) is tuple and
          1 <= len(weights) <= MAX_HYPOTHESES and
          all(type(w) is Fraction and 0 <= w <= 1 for w in weights) and
          sum(weights) == 1, "WEIGHTS")
    _need(type(forecasts) is tuple and
          1 <= len(forecasts) <= MAX_HORIZON, "HORIZON")
    _need(type(costs) is tuple and len(costs) == 2 and
          all(type(x) is int and 0 <= x <= 1000 for x in costs), "COSTS")
    _need(policy in ("optimal", "greedy"), "POLICY")
    for step in forecasts:
        _need(type(step) is tuple and len(step) == len(weights), "FORECAST_SHAPE")
        for pair in step:
            _need(type(pair) is tuple and len(pair) == 2 and
                  all(type(x) is int and 0 <= x <= 1000 for x in pair),
                  "FORECAST_VALUES")
    q = tuple(tuple(tuple(Fraction(x, 1000) for x in pair)
                    for pair in step) for step in forecasts)
    cost = tuple(Fraction(x, 1000) for x in costs)

    @lru_cache(maxsize=None)
    def solve(t, w):
        if t == len(q):
            return Fraction(0), None, ()
        immediate, values = [], []
        for a in (0, 1):
            likelihood = tuple(row[a] for row in q[t])
            p = sum((wi * qi for wi, qi in zip(w, likelihood)), Fraction(0))
            reward = p - cost[a]
            immediate.append(reward)
            total = reward
            if t + 1 < len(q):
                for y in (0, 1):
                    chance = p if y else 1 - p
                    if not chance:
                        continue
                    new_w = tuple(wi * (qi if y else 1 - qi) / chance
                                  for wi, qi in zip(w, likelihood))
                    total += chance * solve(t + 1, new_w)[0]
            values.append(total)
        score = values if policy == "optimal" else immediate
        a = int(score[1] > score[0])
        return values[a], a, tuple(values)

    value, action, conditional = solve(0, weights)
    return {"action": action, "expected_net_utility": value,
            "conditional_values": conditional,
            "horizon": len(q), "states_evaluated": solve.cache_info().currsize}


def analytical_example():
    """Illustrative public forecasts, not drawn from KNOW41 or a held source."""
    weights = (Fraction(1, 2), Fraction(1, 2))
    step = ((400, 100), (400, 700))
    output = []
    for h in range(1, MAX_HORIZON + 1):
        optimal = plan(weights, (step,) * h)
        greedy = plan(weights, (step,) * h, policy="greedy")
        output.append({"horizon": h, "optimal_action": optimal["action"],
                       "greedy_action": greedy["action"],
                       "optimal_value": str(optimal["expected_net_utility"]),
                       "greedy_value": str(greedy["expected_net_utility"]),
                       "gain": str(optimal["expected_net_utility"] -
                                   greedy["expected_net_utility"])})
    return output
