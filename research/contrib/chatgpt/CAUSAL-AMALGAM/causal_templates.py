"""Action-effect constraints over an already learned native transition readout."""

from itertools import product

TEMPLATES = tuple(product((0, 1), range(4)))


class CausalTemplates:
    """Score reusable action transformations with public witness likelihoods."""

    def __init__(self, prior):
        self.prior = prior
        self.mass = [1 / len(TEMPLATES)] * len(TEMPLATES)

    def probabilities(self, view, action):
        return [self.prior(view, 0 if mask & (1 << view[0]) else action ^ swap)
                for swap, mask in TEMPLATES]

    def marginal(self, view, action):
        return sum(prob * weight for prob, weight in zip(self.probabilities(view, action), self.mass))

    def advance(self, view, action, outcome):
        if type(outcome) is not int or outcome not in (0, 1):
            raise ValueError("Expected a binary observed transition")
        probabilities = [min(0.99, max(0.01, p)) for p in self.probabilities(view, action)]
        weights = [weight * (p if outcome else 1 - p)
                   for p, weight in zip(probabilities, self.mass, strict=True)]
        total = sum(weights)
        self.mass = [weight / total for weight in weights]
