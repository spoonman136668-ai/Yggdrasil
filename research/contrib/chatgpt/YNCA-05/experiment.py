"""YNCA-05: exact causal identifiability and intervention-value ceiling.

Source-free analytic enumeration only; no native Yggdrasil model, controller,
official science first-use, dataset, trained model, or paid inference.
"""
from __future__ import annotations
from itertools import combinations, product
import hashlib
import json
import math
from pathlib import Path
import sys

ACTIONS = tuple(range(8))
OFF_DIAGONAL = (1, 2, 3, 4, 5, 6)
PAIRS = tuple(combinations(OFF_DIAGONAL, 2))
MEASUREMENT_ERROR = 0.14
SAMPLES_PER_PROBE = 2
TERMINAL_BIT_COST = 0.08
PROBE_BASE_COST = 0.018
PROBE_BIT_COST = 0.012
THRESHOLD = 1e-12
POLICIES = ("no_probe", "bayes_value", "cheap_candidate", "random", "entropy_per_cost") + tuple("fixed" + str(a) for a in OFF_DIAGONAL)


def make_laws():
    # 256 possible 3-input binary Boolean functions; condition on both
    # diagonal outputs. All 64 remaining truth tables are distinct.
    return tuple(tuple(0 if a == 0 else 1 if a == 7 else (bits >> (a - 1)) & 1
                       for a in ACTIONS) for bits in range(1 << 6))


LAWS = make_laws()


def terminal_cost(action):
    return TERMINAL_BIT_COST * action.bit_count()


def probe_cost(action):
    return PROBE_BASE_COST + PROBE_BIT_COST * action.bit_count()


def unit_prior():
    return tuple([1.0 / len(LAWS)] * len(LAWS))


def utility(weights, pair):
    predicted = {a: sum(w * law[a] for w, law in zip(weights, LAWS)) - terminal_cost(a)
                 for a in pair}
    best = max(pair, key=lambda a: (predicted[a], -a))
    return predicted[best]


def truth_oracle_utility(weights, pair):
    return sum(w * max(law[a] - terminal_cost(a) for a in pair)
               for w, law in zip(weights, LAWS))


def likelihood(y, causal_bit):
    p_one = 1 - MEASUREMENT_ERROR if causal_bit else MEASUREMENT_ERROR
    return p_one if y else 1 - p_one


def posterior_branches(weights, action):
    branches = []
    for ys in product((0, 1), repeat=SAMPLES_PER_PROBE):
        unnorm = tuple(w * math.prod(likelihood(y, law[action]) for y in ys)
                       for w, law in zip(weights, LAWS))
        mass = sum(unnorm)
        if mass > 0:
            branches.append((mass, tuple(w / mass for w in unnorm)))
    assert abs(sum(p for p, _ in branches) - 1.0) < 1e-12
    return branches


def expected_after(weights, pair, action):
    return sum(probability * utility(after, pair)
               for probability, after in posterior_branches(weights, action))


def expected_information_gain(weights, action):
    # Shannon information gained from TWO independent noisy samples,
    # computed exactly by summing branch posterior entropies.
    def entropy(w):
        return -sum(p * math.log2(p) for p in w if p > 0)
    before = entropy(weights)
    after = sum(prob * entropy(w) for prob, w in posterior_branches(weights, action))
    return before - after


def means():
    weights = unit_prior()
    per_pair = []
    sums = {policy: 0.0 for policy in POLICIES}
    useful_pairs = 0
    total_oracle = 0.0
    offpair_gain_absmax = 0.0
    false_positive_probe = 0
    for pair in PAIRS:
        baseline = utility(weights, pair)
        oracle = truth_oracle_utility(weights, pair)
        total_oracle += oracle
        value = {a: expected_after(weights, pair, a) - baseline for a in OFF_DIAGONAL}
        net = {a: value[a] - probe_cost(a) for a in OFF_DIAGONAL}
        for action in OFF_DIAGONAL:
            if action not in pair:
                offpair_gain_absmax = max(offpair_gain_absmax, abs(value[action]))
                false_positive_probe += int(value[action] > THRESHOLD)
        ranked = max(OFF_DIAGONAL, key=lambda a: (net[a], -a))
        choice = ranked if net[ranked] > 0 else None
        useful_pairs += int(choice is not None)
        cheap = min(pair, key=lambda a: (probe_cost(a), a))
        entropy_action = max(OFF_DIAGONAL, key=lambda a: (
            expected_information_gain(weights, a) / probe_cost(a), -a))
        # Expected regret plus actual probe cost under each policy.
        def loss(action):
            if action is None:
                return oracle - baseline
            return oracle - (baseline + value[action]) + probe_cost(action)
        losses = {"no_probe": loss(None),
                  "bayes_value": loss(choice),
                  "cheap_candidate": loss(cheap),
                  "random": sum(loss(a) for a in OFF_DIAGONAL) / len(OFF_DIAGONAL),
                  "entropy_per_cost": loss(entropy_action)}
        losses.update({"fixed" + str(a): loss(a) for a in OFF_DIAGONAL})
        for name in POLICIES:
            sums[name] += losses[name]
        per_pair.append({
            "terminal_pair": list(pair),
            "oracle_no_probe_regret": round(loss(None), 10),
            "bayes_value_probe": choice,
            "max_net_gain": round(net[ranked], 10),
            "cheapest_candidate": cheap,
            "entropy_per_cost_action": entropy_action,
        })
    avg = {name: round(sums[name] / len(PAIRS), 10) for name in POLICIES}
    return {
        "terminal_pair_count": len(PAIRS),
        "positive_net_probe_pairs": useful_pairs,
        "nonpositive_net_probe_pairs": len(PAIRS) - useful_pairs,
        "out_of_pair_information_value_max_abs": round(offpair_gain_absmax, 14),
        "out_of_pair_false_positive_information": false_positive_probe,
        "mean_total_regret_and_charged_probe_cost": avg,
        "best_fixed_policy": min(("fixed" + str(a) for a in OFF_DIAGONAL),
                                 key=lambda k: (avg[k], k)),
        "best_non_oracle_baseline": min(
            (k for k in POLICIES if k != "bayes_value"),
            key=lambda k: (avg[k], k)),
        "per_pair": per_pair,
    }


def identifiability():
    # Independent of posterior/probe/noise calculations: exact combinatorial
    # classes of possible truth tables from observed action outcomes.
    sizes = {}
    for k in (0, 1, 2, 3, 4, 5, 6):
        values = []
        for probes in combinations(OFF_DIAGONAL, k):
            signatures = {}
            for law in LAWS:
                signature = (law[0], law[7]) + tuple(law[a] for a in probes)
                signatures[signature] = signatures.get(signature, 0) + 1
            values.append({
                "probe_actions": list(probes),
                "distinct_signatures": len(signatures),
                "smallest_compatible_class": min(signatures.values()),
                "largest_compatible_class": max(signatures.values()),
            })
        sizes[str(k)] = {
            "probe_set_count": len(values),
            "min_distinct_signatures": min(x["distinct_signatures"] for x in values),
            "max_distinct_signatures": max(x["distinct_signatures"] for x in values),
            "min_compatible_class": min(x["smallest_compatible_class"] for x in values),
            "max_compatible_class": max(x["largest_compatible_class"] for x in values),
        }
    assert len(LAWS) == 64
    assert len(set(LAWS)) == 64
    assert sizes["0"]["max_compatible_class"] == 64
    assert sizes["2"]["min_compatible_class"] == 16
    assert sizes["6"]["min_compatible_class"] == 1
    return sizes


def audit():
    sizes = identifiability()
    decisions = means()
    assert decisions["out_of_pair_information_value_max_abs"] <= 1e-12
    assert decisions["out_of_pair_false_positive_information"] == 0
    # The full-law Bayes optimal probe-or-stop decision cannot be worse in
    # expectation than any alternative single-probe strategy under its own
    # correctly specified, fully enumerable 64-function prior.
    optimal = decisions["mean_total_regret_and_charged_probe_cost"]["bayes_value"]
    assert all(optimal <= v + 1e-12 for v in
               decisions["mean_total_regret_and_charged_probe_cost"].values())
    return {
        "all_256_laws_considered": True,
        "conditioning_reduces_to_64_distinct_laws": True,
        "two_distinct_probe_min_residual_is_16": True,
        "six_distinct_probes_identify_truth_table_noiselessly": True,
        "off_pair_value_zero_given_unstructured_prior": True,
        "exact_bayes_value_policy_weakly_dominates_controls": True,
        "identifiability_by_probes": sizes,
        "decision_value": decisions,
    }


def main(argv):
    if argv not in ([], ["--run"], ["--check"]):
        raise SystemExit("Usage: experiment.py [--run|--check]")
    result = audit()
    if argv == ["--check"]:
        print("YNCA05_ANALYTIC_CONSISTENCY_PASS")
        return
    report = {
        "schema": "yggdrasil.ynca05.analytic-ceiling.v1",
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "scope": "Source-free exhaustive analytic bound; no learned native model",
        "truth_table_count_full": 256,
        "truth_table_count_conditioned": len(LAWS),
        "noise_epsilon": MEASUREMENT_ERROR,
        "samples_per_probe": SAMPLES_PER_PROBE,
        "analysis": result,
        "claims": {"native_integrated": False, "scientific_pass": False,
                   "owner_acceptance": False, "deployment": False}
    }
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main(sys.argv[1:])
