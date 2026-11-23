"""Decision-focused Bayesian intervention baseline, strictly public TRAIN.

Unlike parameter-information-gain selection, this policy values an action by
its expected reduction in posterior predictive two-channel Brier risk for the same
state/action cell, weighted by that cell's empirical frequency in TRAIN.
This is a myopic one-step value-of-information baseline, not full planning.
"""
from __future__ import annotations

import math
from calibration_active_bayes import ActiveBayesianPolicy, ACTIONS, COST
from calibration_controls import code, validated


def expected_dirichlet_brier_reduction(alpha):
    """Expected reduction in posterior predictive Brier risk after one sample.

    If theta ~ Dir(alpha), p=E[theta], and y~Categorical(theta), the
    posterior-predictive Brier risk is 1-sum(p**2). Average this quantity
    over the four possible observations after the Dirichlet update.
    """
    if (type(alpha) not in (tuple, list) or len(alpha) != 4 or
            any(type(x) not in (int, float) or not math.isfinite(x) or x <= 0
                for x in alpha)):
        raise ValueError("CCE06_DECISION_BAD_DIRICHLET")
    total = float(sum(alpha))
    # The benchmark loss is the mean of two binary-channel Brier scores,
    # not four-class categorical Brier. Under a Dirichlet posterior the
    # marginal probabilities are Beta-distributed. One observed transition
    # changes each marginal mean by +/-1/(total+1), with Bernoulli variance
    # p*(1-p); average both channels exactly.
    p0 = (alpha[2] + alpha[3]) / total
    p1 = (alpha[1] + alpha[3]) / total
    gain = 0.5 * (p0*(1-p0) + p1*(1-p1)) / ((total + 1) ** 2)
    if not math.isfinite(gain) or gain < -1e-12:
        raise ValueError("CCE06_DECISION_INVALID_RISK_REDUCTION")
    return max(0.0, gain)


class DecisionFocusedBayesianPolicy(ActiveBayesianPolicy):
    """Myopic active Bayesian policy targeting expected terminal Brier risk.

    TRAIN supplies fixed importance weights over public (observation, action)
    contexts. Online updates change each row's Dirichlet posterior, but do not
    change TRAIN weights. This avoids selecting actions using terminal audit
    labels. The fixed weights approximate, rather than certify, audit support.
    """
    def __init__(self, *, alpha=0.5, probe_penalty=0.0001):
        super().__init__(alpha=alpha, probe_penalty=probe_penalty)
        self.train_context_counts = {(obs, action): 0
                                     for obs in range(4) for action in ACTIONS}
        self.train_context_weight = {}
        self.train_events = 0

    def fit(self, train):
        if self.fitted or type(train) not in (tuple, list) or not train:
            raise ValueError("CCE06_DECISION_INVALID_FIT")
        for events in train:
            validated(events)
            for event in events:
                key = (code(event["observation"]), event["action"])
                self.train_context_counts[key] += 1
                self.train_events += 1
        super().fit(train)
        self.train_context_weight = {
            key: count / self.train_events
            for key, count in self.train_context_counts.items()
        }
        return self

    def expected_brier_gain(self, observed, action):
        if not self.fitted or type(action) is not int or action not in ACTIONS:
            raise ValueError("CCE06_DECISION_NOT_FIT_OR_BAD_ACTION")
        key = (code(observed), action)
        weight = self.train_context_weight.get(key, 0.0)
        return weight * expected_dirichlet_brier_reduction(
            self.counts[key]
        )

    def choose(self):
        if self.current is None or self.pending is not None:
            raise ValueError("CCE06_DECISION_PENDING_OR_NOT_STARTED")
        available = [a for a in ACTIONS if self.spent + COST[a] <= self.budget]
        ranked = [
            (self.expected_brier_gain(self.current, a) -
             self.probe_penalty * COST[a], -COST[a], -a, a)
            for a in available
        ]
        action = max(ranked)[-1]
        self.pending = (self.current[:], action)
        self.spent += COST[action]
        return action
