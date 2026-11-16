"""Equal-information direct greedy and independently coded Bayes-optimal planner."""
from __future__ import annotations
from functools import lru_cache
from hashlib import sha256
from math import isfinite
import struct

COUNT = 6
FULL = (1 << COUNT) - 1
FIELDS = ('channel','positive','cost')


def validate(public_prior, public_costs):
    if len(public_prior) != COUNT or len(public_costs) != COUNT:
        raise ValueError('CB7_SIX_PUBLIC_CANDIDATES')
    if any(type(p) not in (int,float) or not isfinite(p) or p <= 0 for p in public_prior):
        raise ValueError('CB7_INVALID_PUBLIC_PRIORS')
    if abs(sum(public_prior) - 1.) > 1e-10:
        raise ValueError('CB7_NOT_NORMALIZED')
    if any(type(c) not in (int,float) or not isfinite(c) or c < 0 for c in public_costs):
        raise ValueError('CB7_INVALID_PUBLIC_COSTS')


class Base:
    def __init__(self, public_prior, public_costs):
        validate(public_prior, public_costs)
        self.prior = tuple(public_prior)
        self.costs = tuple(public_costs)
        self.mask = FULL
        self.tested = 0
        self.certain = None
        self._receipt = sha256()

    def choose_answer(self):
        return max((i for i in range(COUNT) if (self.mask >> i) & 1),
                   key=lambda i: (self.prior[i], -i))

    def observe(self, row):
        if tuple(getattr(row,'_fields',())) != FIELDS:
            raise ValueError('CB7_EXACT_PUBLIC_EVENT_ONLY')
        channel, result, cost = row
        if type(channel) is not int or channel < 0 or channel >= COUNT or not ((self.mask >> channel) & 1) or (self.tested >> channel) & 1:
            raise ValueError('CB7_REPEATED_OR_IMPOSSIBLE_ACTION')
        if type(result) is not bool or type(cost) not in (int,float) or cost != self.costs[channel]:
            raise ValueError('CB7_PUBLIC_RESULT_OR_CHARGE_MISMATCH')
        self.tested |= 1 << channel
        self.mask = (1 << channel) if result else self.mask & ~(1 << channel)
        self._receipt.update(struct.pack('<B?d', channel, result, cost))
        if self.mask.bit_count() == 1:
            self.certain = self.choose_answer()

    def public_receipt(self):
        return self._receipt.hexdigest()


class DirectOneStep(Base):
    """Source-blind direct positive posterior mass; pay only for one-step VOI."""
    def next_probe(self):
        if self.certain is not None:
            return None
        choices = [i for i in range(COUNT) if (self.mask >> i) & 1]
        total = sum(self.prior[i] for i in choices)
        current = max(self.prior[i] for i in choices) / total
        best, advantage = None, 0.
        for i in choices:
            others = [self.prior[j] for j in choices if j != i]
            expected_correct = (self.prior[i] + max(others, default=0.)) / total
            gain = expected_correct - self.costs[i] - current
            if gain > advantage + 1e-12:
                best, advantage = i, gain
        return best


class ExactBayesianDP(Base):
    """Independent full-horizon optimal value function with stop decision."""
    def __init__(self, public_prior, public_costs):
        super().__init__(public_prior, public_costs)
        self._policy = {}
        priors = self.prior
        costs = self.costs

        @lru_cache(maxsize=None)
        def solve(mask):
            candidates = [i for i in range(COUNT) if mask & (1 << i)]
            if len(candidates) == 1:
                return 1., None
            mass = sum(priors[i] for i in candidates)
            best = max(priors[i] for i in candidates) / mass
            decision = None
            for i in candidates:
                p = priors[i] / mass
                value = -costs[i] + p + (1-p)*solve(mask & ~(1 << i))[0]
                if value > best + 1e-12:
                    best, decision = value, i
            self._policy[mask] = (best, decision)
            return best, decision
        self.expected_optimal = solve(FULL)[0]
        self._solve = solve

    def next_probe(self):
        if self.certain is not None:
            return None
        return self._solve(self.mask)[1]


class ConfirmAscending(Base):
    def next_probe(self):
        if self.certain is not None:
            return None
        return next(i for i in range(COUNT) if (self.mask >> i) & 1)


class NoProbe(Base):
    def next_probe(self):
        return None


class RandomOrder(Base):
    def __init__(self, public_prior, public_costs, seed):
        super().__init__(public_prior, public_costs)
        import random
        rng = random.Random(seed)
        self.order = list(range(COUNT))
        rng.shuffle(self.order)

    def next_probe(self):
        if self.certain is not None:
            return None
        return next(i for i in self.order if (self.mask >> i) & 1)
