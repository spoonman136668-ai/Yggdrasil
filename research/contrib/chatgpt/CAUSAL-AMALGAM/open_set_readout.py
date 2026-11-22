"""Evidence-based choice between identity, action transforms and a fallback."""

from causal_templates import CausalTemplates


class OpenSetReadout:
    """Keep a history-conditioned fallback in the evidence comparison."""

    def __init__(self, prior, starting_events, adaptive):
        self.prior = prior
        self.templates = CausalTemplates(prior)
        self.adaptive = adaptive
        self.weights = [0.5, 0.25, 0.25]
        self.previous_action = 0
        for view, action, outcome in starting_events:
            self.adaptive.update((view[0], action, self.previous_action), outcome)
            self.previous_action = action
        self.previous_action = 0

    def evidence_predictions(self, view, action):
        return (self.prior(view, action), self.templates.marginal(view, action),
                self.adaptive.forecast((view[0], action, self.previous_action))[1])

    def forecast(self, options):
        if max(self.weights) >= 0.9:
            index = self.weights.index(max(self.weights))
            return options[index], index
        return sum(w * p for w, p in zip(self.weights, options, strict=True)), None

    def observe(self, view, action, outcome, options):
        if type(outcome) is not int or outcome not in (0, 1):
            raise ValueError("Expected an observed binary consequence")
        likelihoods = [min(0.99, max(0.01, p if outcome else 1 - p)) for p in options]
        weighted = [w * likelihood for w, likelihood in zip(self.weights, likelihoods, strict=True)]
        total = sum(weighted)
        self.weights = [p / total for p in weighted]
        self.templates.advance(view, action, outcome)
        self.adaptive.update((view[0], action, self.previous_action), outcome)
        self.previous_action = action
