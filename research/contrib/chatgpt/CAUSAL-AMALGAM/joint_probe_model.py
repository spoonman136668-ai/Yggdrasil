"""Finite Bayesian mixture over both transition margins and dependence."""

from itertools import product
from math import comb

from shift_dependence_trial import likelihood


class JointProbeModel:
    def __init__(self, fit, probes, margins, agreements):
        self.hypotheses = [((a, 1 - a), (1 - b, b), c)
                           for a, b, c in product(margins, margins, agreements)]
        self.weights = [1 / len(self.hypotheses)] * len(self.hypotheses)
        for _, first, second in fit:
            weighted = [w * self._moments(h, first, probes, second, probes)[0]
                        for w, h in zip(self.weights, self.hypotheses, strict=True)]
            total = sum(weighted)
            self.weights = [w / total for w in weighted]

    @staticmethod
    def _moments(hypothesis, first, donor_count, second, target_count):
        a, b, agreement = hypothesis
        donor = [likelihood(first, donor_count, p) for p in a]
        target = [likelihood(second, target_count, p) for p in b]
        p0 = target[0] * (donor[0] * agreement + donor[1] * (1 - agreement)) / 2
        p1 = target[1] * (donor[1] * agreement + donor[0] * (1 - agreement)) / 2
        return p0 + p1, p0 * b[0] + p1 * b[1]

    def distribution(self, first, donor_count, second, target_count):
        mass = numerator = 0.0
        for weight, h in zip(self.weights, self.hypotheses, strict=True):
            marginal, joint = self._moments(h, first, donor_count, second, target_count)
            mass += weight * marginal
            numerator += weight * joint
        return mass, numerator / mass

    def predict(self, donor, target):
        return self.distribution(sum(donor), len(donor), sum(target), len(target))[1]

    def allocation(self, budget):
        gains = []
        for donor in range(budget + 1):
            target = budget - donor
            gain = 0.
            for a, b in product(range(donor + 1), range(target + 1)):
                mass, prediction = self.distribution(a, donor, b, target)
                gain += comb(donor, a) * comb(target, b) * mass * (prediction - .5)**2
            gains.append(gain)
        maximum = max(gains)
        return next(n for n, value in enumerate(gains) if value >= maximum - 1e-12)
