"""Compare equal-budget donor and target probes under known source laws."""

from fractions import Fraction as F
from itertools import product
import json
from math import comb
from pathlib import Path


PLAN = Path(__file__).resolve().parent / "shift-dependence-calibrated-dev-01" / "prereg.json"


def count_likelihood(trials, ones, probabilities):
    return tuple(comb(trials, ones) * p**ones * (1 - p)**(trials - ones)
                 for p in probabilities)


def gain(donor, target, agreement, donor_n, target_n):
    expected = F(0)
    total_mass = F(0)
    for k, m in product(range(donor_n + 1), range(target_n + 1)):
        first = count_likelihood(donor_n, k, donor)
        second = count_likelihood(target_n, m, target)
        by_target = [sum(first[d] * second[t] *
                             (agreement if d == t else 1 - agreement) / 2
                         for d in range(2)) for t in range(2)]
        mass = sum(by_target)
        prediction = sum(w * p for w, p in zip(by_target, target, strict=True)) / mass
        total_mass += mass
        expected += mass * (prediction - sum(target) / 2)**2
    if total_mass != 1:
        raise ValueError("Incomplete probability mass")
    return expected


def run():
    families = json.loads(PLAN.read_bytes())["families"]
    results = []
    for name, laws in families.items():
        donor, target = [tuple(F(str(p)) for p in values) for values in laws]
        for agreement in (F(1, 10), F(1, 2), F(9, 10)):
            for budget in (4, 8):
                cells = [gain(donor, target, agreement, n, budget - n) for n in range(budget + 1)]
                if agreement == F(1, 2) and cells[-1] != 0:
                    raise ValueError("Independent donor unexpectedly informative")
                results.append(dict(family=name, agreement=str(agreement), budget=budget,
                                    brier_gain_by_donor_probes=[float(p) for p in cells],
                                    best_donor_probes=[n for n, p in enumerate(cells)
                                                       if p == max(cells)]))
    return dict(kind="known-law matched probe upper bound", source_actions=0, results=results)


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
