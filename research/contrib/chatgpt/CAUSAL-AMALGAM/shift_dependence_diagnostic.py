"""Exact diagnostic for transferring evidence about regime changes."""

from fractions import Fraction
import json
from math import comb


def evaluate(probes, agreement):
    # The crossed-shift fixture's two Bernoulli transition laws.
    donor = (Fraction(5, 32), Fraction(27, 32))
    target = (Fraction(25, 32), Fraction(7, 32))
    unconditional = sum(target) / 2
    score = dict.fromkeys(("independent", "assume_coupled", "known_dependence"), Fraction(0))
    for ones in range(probes + 1):
        evidence = tuple(comb(probes, ones) * q**ones * (1 - q)**(probes - ones)
                         for q in donor)
        posterior = evidence[1] / sum(evidence)
        predictors = {
            "independent": unconditional,
            "assume_coupled": target[0] * (1 - posterior) + target[1] * posterior,
        }
        shift = (1 - agreement) * (1 - posterior) + agreement * posterior
        predictors["known_dependence"] = target[0] * (1 - shift) + target[1] * shift
        for d, likelihood in enumerate(evidence):
            for t, probability in enumerate(target):
                weight = likelihood / 2 * (agreement if d == t else 1 - agreement)
                for name, prediction in predictors.items():
                    score[name] += weight * (probability * (1 - probability)
                                             + (probability - prediction)**2)
    return {name: float(value) for name, value in score.items()}


def run():
    rows = []
    for agreement in (Fraction(1, 10), Fraction(1, 2), Fraction(9, 10)):
        for probes in (0, 2, 4, 8):
            values = evaluate(probes, agreement)
            rows.append(dict(agreement=str(agreement), donor_probes=probes, brier=values))
            if agreement == Fraction(1, 2):
                assert values["known_dependence"] == values["independent"]
    return dict(kind="exact source-law diagnostic", rows=rows, source_actions=0,
                witnesses_admitted=0)


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
