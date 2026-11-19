"""Route public transition evidence to an opt-in, cell-local alternative."""

from yggdrasil.native_episode_experience import NOVEL_PRIOR, REFRESH_RATE, _view
from yggdrasil.public_causal_cells import PublicCausalCells


class RegimeForecast:
    """Maintain an immutable old readout and one fitted alternative per cell."""

    def __init__(self, anchor, fit, *, assignment):
        if assignment not in ("fixed", "all", "posterior"):
            raise ValueError("Unknown assignment mode")
        self._anchor = anchor
        self._assignment = assignment
        self._cells = {}
        for _, views, row in fit:
            key = self._key(views[0], row["x1"])
            observed = PublicCausalCells._bit(row["s2"], "S2")
            self._cells.setdefault(key, [1.0, 1.0, float(NOVEL_PRIOR)])[observed] += 1

    @staticmethod
    def _key(view, first):
        return _view(view)[0], PublicCausalCells._bit(first, "X1")

    def observe(self, view, first, observed):
        cell = self._key(view, first)
        observed = PublicCausalCells._bit(observed, "S2")
        if cell not in self._cells:
            return
        counts = self._cells[cell]
        zeros, ones, last = counts
        old = float(self._anchor(view, first))
        alternative = ones / (zeros + ones)
        prior = (1 - float(REFRESH_RATE)) * last + float(REFRESH_RATE) * float(NOVEL_PRIOR)
        novel_mass = prior * (alternative if observed else 1 - alternative)
        old_mass = (1 - prior) * (old if observed else 1 - old)
        responsibility = novel_mass / (novel_mass + old_mass)
        counts[2] = responsibility
        if self._assignment == "posterior":
            counts[observed] += responsibility
        elif self._assignment == "all":
            counts[observed] += 1

    def forecast(self, view, first, *terminal):
        old = self._anchor(view, first, *terminal)
        if terminal:
            return old
        counts = self._cells.get(self._key(view, first))
        if counts is None:
            return old
        zeros, ones, weight = counts
        return (1 - weight) * float(old) + weight * ones / (zeros + ones)
