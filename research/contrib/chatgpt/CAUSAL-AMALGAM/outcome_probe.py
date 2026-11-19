"""Pre-outcome binary hypothesis probes with a calibration gate."""

from math import log2


def entropy(probability):
    if probability in (0.0, 1.0):
        return 0.0
    return -probability * log2(probability) - (1-probability) * log2(1-probability)


def reversal_quarters(context, action):
    return 3 if context != action else 2


class OutcomeProbe:
    """Choose public interventions from consequence uncertainty and fit only on receipts."""

    def __init__(self, predictor, *, active):
        self.predictor = predictor
        self.active = active
        self.mass = [0.5, 0.5]
        self.log_loss = [0.0, 0.0]
        self.counts = [[0, 0], [0, 0]]
        self.steps = 0

    def hypotheses(self, context, action):
        probability = self.predictor(context, action)
        # Both actions expose a change, with different known effect strengths.
        reversal = reversal_quarters(context, action) / 4
        return probability, (1-reversal)*probability + reversal*(1-probability)

    def choose(self, context):
        hypotheses = [self.hypotheses(context, action) for action in (0, 1)]
        mixtures = [sum(w*p for w,p in zip(self.mass, pair, strict=True))
                    for pair in hypotheses]
        if self.active:
            information = [entropy(mixture) - sum(w*entropy(p) for w,p in zip(self.mass, pair, strict=True))
                           for mixture,pair in zip(mixtures, hypotheses, strict=True)]
        else:
            information = [0.0, 0.0]
        # A mean difference below numerical roundoff carries no preference.
        # Reserve one in four active interventions for the alternative action.
        # This preserves support for a diagnostic that makes both choices informative.
        action = 0 if self.active and self.steps % 4 == 3 else max(
            (0, 1), key=lambda a: (round(information[a], 12), -self.counts[context][a], -a)
        )
        return action, hypotheses[action], mixtures[action]

    def observe(self, context, action, probabilities, observation):
        if type(observation) is not int or observation not in (0,1):
            raise ValueError("Only an observed binary transition updates belief")
        likelihood = [min(.99, max(.01, p if observation else 1-p)) for p in probabilities]
        weights = [weight * p for weight,p in zip(self.mass,likelihood,strict=True)]
        normalizer = sum(weights)
        self.mass = [p / normalizer for p in weights]
        self.log_loss = [loss-log2(p) for loss,p in zip(self.log_loss,likelihood,strict=True)]
        self.counts[context][action] += 1
        self.steps += 1

    def declaration(self, *, posterior, min_observations, max_bits_per_outcome):
        choice = int(self.mass[1] > self.mass[0])
        if (self.steps >= min_observations and self.mass[choice] >= posterior
                and self.log_loss[choice] / self.steps <= max_bits_per_outcome):
            return choice
        return None
