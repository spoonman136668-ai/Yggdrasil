"""CCE06 public-only costed Bayesian intervention policy, engineering preflight.

Dirichlet-multinomial posterior over public next-observation responses given
(public current observation, action). Expected parameter information gain uses
an exact KL identity (up to numerical digamma approximation). This is a
legitimate active Bayesian baseline *component*, not a certified strong policy
or a causal topology learner. No evaluator, oracle, or calibration-world import.
"""
from __future__ import annotations
import math
from calibration_controls import validated, code

SCHEMA = 'yggdrasil.y2.cce06.active-bayes.v1'
ACTIONS = (0, 1, 2)
COST = {0: 0, 1: 1, 2: 1}


def _digamma(x):
    if type(x) not in (float, int) or not math.isfinite(x) or x <= 0:
        raise ValueError('CCE06_BAD_DIRICHLET_PARAMETER')
    total = 0.0
    while x < 8:
        total -= 1 / x
        x += 1
    inv = 1 / x
    sq = inv * inv
    return total + math.log(x) - .5 * inv - sq / 12 + sq**2 / 120 - sq**3 / 252


def posterior_information_gain(alpha):
    """E_y KL(Dir(alpha+onehot_y)||Dir(alpha)); nats, no oracle.

    KL for outcome y = log(A/alpha_y) + psi(alpha_y+1)-psi(A+1).
    """
    if (type(alpha) not in (list, tuple) or len(alpha) != 4 or
            any(type(z) not in (int, float) or not math.isfinite(z) or z <= 0
                for z in alpha)):
        raise ValueError('CCE06_BAD_DIRICHLET_VECTOR')
    total = sum(alpha)
    value = sum((v / total) * (math.log(total / v) +
                  _digamma(v + 1) - _digamma(total + 1)) for v in alpha)
    return max(0.0, value)


class ActiveBayesianPolicy:
    """Finite-budget Bayesian information gathering from public consequences.

    Fitting only uses supplied TRAIN events. For active evaluation, choose()
    must be followed by a real observed public transition through update();
    it cannot be scored off-policy using unrelated logged random actions.
    """
    def __init__(self, *, alpha=0.5, probe_penalty=0.05):
        if (type(alpha) not in (int, float) or not math.isfinite(alpha)
                or alpha <= 0 or alpha > 10 or
                type(probe_penalty) not in (int, float)
                or not math.isfinite(probe_penalty)
                or probe_penalty < 0 or probe_penalty > 1):
            raise ValueError('CCE06_ACTIVE_BAD_CONFIG')
        self.alpha = float(alpha)
        self.probe_penalty = float(probe_penalty)
        self.counts = {(obs, a): [self.alpha] * 4
                       for obs in range(4) for a in ACTIONS}
        self.fit_events = 0
        self.fitted = False
        self.current = None
        self.budget = 0
        self.spent = 0
        self.pending = None
        self.actions_taken = 0

    def fit(self, train):
        if self.fitted or type(train) not in (list, tuple) or not train:
            raise ValueError('CCE06_ACTIVE_INVALID_FIT')
        for events in train:
            validated(events)
            for e in events:
                self.counts[code(e['observation']), e['action']][code(e['next_observation'])] += 1
                self.fit_events += 1
        self.fitted = True
        return self

    def posterior(self, observed, action):
        if not self.fitted or type(action) is not int or action not in ACTIONS:
            raise ValueError('CCE06_ACTIVE_NOT_FIT_OR_BAD_ACTION')
        counts = self.counts[code(observed), action]
        total = sum(counts)
        return tuple(c / total for c in counts)

    def info_gain(self, observed, action):
        if not self.fitted or type(action) is not int or action not in ACTIONS:
            raise ValueError('CCE06_ACTIVE_NOT_FIT_OR_BAD_ACTION')
        return posterior_information_gain(self.counts[code(observed), action])

    def start(self, observed, *, paid_budget):
        if (not self.fitted or self.pending is not None or
                type(paid_budget) is not int or not 0 <= paid_budget <= 100000):
            raise ValueError('CCE06_ACTIVE_INVALID_START')
        code(observed)
        self.current = observed[:]
        self.budget = paid_budget
        self.spent = 0
        self.actions_taken = 0

    def choose(self):
        if self.current is None or self.pending is not None:
            raise ValueError('CCE06_ACTIVE_PENDING_OR_NOT_STARTED')
        available = [a for a in ACTIONS if self.spent + COST[a] <= self.budget]
        utilities = [(self.info_gain(self.current, a) - self.probe_penalty * COST[a],
                      -COST[a], -a, a) for a in available]
        action = max(utilities)[-1]
        self.pending = (self.current[:], action)
        self.spent += COST[action]
        return action

    def update(self, event):
        # Enforce actual on-policy public witness, including chosen action.
        if (type(event) is not dict or set(event) !=
                {'observation', 'action', 'next_observation'} or
                self.pending is None):
            raise ValueError('CCE06_ACTIVE_BAD_OR_MISSING_WITNESS')
        observed, action = self.pending
        if (event['observation'] != observed or type(event['action']) is not int
                or event['action'] != action):
            raise ValueError('CCE06_ACTIVE_OFF_POLICY_OR_STALE_WITNESS')
        outcome = code(event['next_observation'])
        self.counts[code(observed), action][outcome] += 1
        self.current = event['next_observation'][:]
        self.pending = None
        self.actions_taken += 1

    def snapshot(self):
        if not self.fitted:
            raise ValueError('CCE06_ACTIVE_NOT_FIT')
        return tuple(tuple(self.counts[obs, a]) for obs in range(4) for a in ACTIONS), (
            tuple(self.current) if self.current is not None else None,
            self.budget, self.spent, self.pending, self.actions_taken)
