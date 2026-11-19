"""Compare native readouts using only earlier public consequences."""

from fractions import Fraction

from yggdrasil.native_episode_experience import REFRESH_RATE, _view
from yggdrasil.public_causal_cells import PublicCausalCells


class EvidenceReadout:
    """Keep evidence per prediction cell or pool it for a matched control.

    The original and continued forecasts are immutable snapshots. Transition
    evidence never changes a reward cell and vice versa. Unobserved and
    jointly unsupported cells use the original forecast. An evaluator can
    recreate this shadow state from exactly the same public prefix.
    """

    def __init__(self, original, continued, *, local):
        if type(local) is not bool:
            raise ValueError("A boolean evidence scope is required")
        self._forecasts = (original, continued)
        self._local = local
        self._evidence = {}

    def _address(self, view, first, terminal):
        if len(terminal) not in (0, 2):
            raise ValueError("Reward prediction requires both public terminal coordinates")
        terminal = tuple(PublicCausalCells._bit(bit, "TERMINAL_COORDINATE") for bit in terminal)
        public = (_view(view), PublicCausalCells._bit(first, "X1")) + terminal
        if not self._local:
            return len(terminal), public
        return (len(terminal), public[0][0], *public[1:]), public

    def _predict(self, view, first, terminal):
        address, public = self._address(view, first, terminal)
        probabilities = tuple(Fraction(predict(*public)) for predict in self._forecasts)
        if any(not 0 <= p <= 1 for p in probabilities):
            raise ValueError("A forecast is outside the probability interval")
        return address, probabilities

    def forecast(self, view, first, *terminal):
        address, probabilities = self._predict(view, first, terminal)
        if address not in self._evidence:
            return probabilities[0]
        weights = self._evidence[address]
        return sum(w * p for w, p in zip(weights, probabilities, strict=True))

    def _updated(self, view, first, terminal, outcome):
        address, probabilities = self._predict(view, first, terminal)
        weights = self._evidence.get(address, (Fraction(1, 2), Fraction(1, 2)))
        prior = tuple((1 - REFRESH_RATE) * w + REFRESH_RATE / 2 for w in weights)
        likelihoods = (p if outcome else 1 - p for p in probabilities)
        posterior = tuple(w * q for w, q in zip(prior, likelihoods, strict=True))
        total = sum(posterior)
        if not total:
            return address, None
        return address, tuple(w / total for w in posterior)

    def observe(self, view, first, state, second, reward):
        """Update after the full public episode, with no held-label access."""
        state = PublicCausalCells._bit(state, "S2")
        second = PublicCausalCells._bit(second, "X2")
        reward = PublicCausalCells._bit(reward, "Y")
        transition = self._updated(view, first, (), state)
        terminal = self._updated(view, first, (state, second), reward)
        for address, weights in (transition, terminal):
            if weights is None:
                self._evidence.pop(address, None)
            else:
                self._evidence[address] = weights
