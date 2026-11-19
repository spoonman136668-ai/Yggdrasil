"""Opt-in selector for a matched development comparison on the native model."""

from collections import deque
from fractions import Fraction
from math import isfinite

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import EXPERIENCE_SOURCE, _two_stage_plan
from yggdrasil.native_jepa2_multilearner import _views


class SpecialistSelection:
    """Compare native, direct and temporal forecasts on the same past actions."""

    def __init__(self, system, *, window, minimum_count, minimum_gain,
                 enable_reward=False, evidence=None):
        if (type(window) is not int or type(minimum_count) is not int
                or not 1 <= minimum_count <= window
                or not isinstance(minimum_gain, Fraction) or not 0 < minimum_gain <= 1
                or type(enable_reward) is not bool):
            raise ValueError("Invalid specialist selection configuration")
        self.system = system
        self.window = window
        self.minimum_count = minimum_count
        self.minimum_gain = minimum_gain
        self.enable_reward = enable_reward
        self._evidence = {} if evidence is None else evidence

    @staticmethod
    def _coordinate(views):
        _views(views)
        primary, alternate = views
        if primary[0] != alternate[0]:
            raise ValueError("Specialist views must share the public coordinate")
        return primary[0]

    def _forecasts(self, views, actions):
        native = self.system.native.experience_context_forecast(views[0], *actions)
        specialists = self.system.specialist_forecasts(views, *actions)
        if not all(isfinite(p) and 0 <= p <= 1 for p in (native, *specialists)):
            raise ValueError("Forecasts must be probabilities")
        # Use a fixed specialist precision for scoring and planning to limit
        # the effect of platform rounding differences in the saved weights.
        return native, *(Fraction(round(p * 1_000_000), 1_000_000) for p in specialists)

    def selection(self, views, first, *terminal):
        """Return the forecast origin for this public context and action."""
        key = (self._coordinate(views), first, *terminal)
        if terminal and not self.enable_reward:
            return 0
        losses = self._evidence.get(key, ())
        if len(losses) < self.minimum_count:
            return 0
        direct, temporal = (sum(values) for values in zip(*losses, strict=True))
        threshold = len(losses) * self.minimum_gain
        if direct == temporal or max(direct, temporal) < threshold:
            return 0
        return 1 if direct > temporal else 2

    def forecast(self, views, first, *terminal):
        selected = self.selection(views, first, *terminal)
        if selected == 0:
            return self.system.native.experience_context_forecast(views[0], first, *terminal)
        return self._forecasts(views, (first, *terminal))[selected]

    def plan(self, views):
        return _two_stage_plan(
            lambda first: self.forecast(views, first),
            lambda first, state, second: self.forecast(views, first, state, second),
        )

    def observe_experience(self, identifier, views, row, *, source_sha256, packet_sha256):
        """Add matched losses only when the shared witness transaction succeeds."""
        updated = self.system.observe_experience(
            identifier, views, row, source_sha256=source_sha256, packet_sha256=packet_sha256,
        )
        if updated is self.system:
            return self
        coordinate = self._coordinate(views)
        evidence = self._evidence.copy()
        for actions, outcome in (((row["x1"],), row["s2"]),
                                 ((row["x1"], row["s2"], row["x2"]), row["y"])):
            # The old system is intact. Score its forecasts before retaining
            # any state trained on this outcome, and score only taken actions.
            native, direct, temporal = self._forecasts(views, actions)
            native_loss = (native - outcome) ** 2
            key = (coordinate, *actions)
            losses = deque(evidence.get(key, ()), maxlen=self.window)
            losses.append((native_loss - (direct - outcome) ** 2,
                           native_loss - (temporal - outcome) ** 2))
            evidence[key] = tuple(losses)
        return type(self)(updated, window=self.window, minimum_count=self.minimum_count,
                          minimum_gain=self.minimum_gain, enable_reward=self.enable_reward,
                          evidence=evidence)

    @classmethod
    def replay(cls, start, end, *, window, minimum_count, minimum_gain, enable_reward=False):
        """Rebuild selection evidence from the accepted suffix after the trial start."""
        prior = start.native._episode_reader()._ledger
        current = end.native._episode_reader()._ledger
        if current[:len(prior)] != prior:
            raise ValueError("Specialist selection checkpoint has a different witness prefix")
        selection = cls(start, window=window, minimum_count=minimum_count,
                        minimum_gain=minimum_gain, enable_reward=enable_reward)
        for identifier, views, first, state, second, reward in current[len(prior):]:
            row = {"s1": views[0][0], "x1": first, "s2": state, "x2": second, "y": reward}
            selection = selection.observe_experience(
                identifier, views, row, source_sha256=EXPERIENCE_SOURCE,
                packet_sha256=digest(canonical([identifier, views, row])),
            )
        if selection.system.checkpoint() != end.checkpoint():
            raise ValueError("Specialist selection checkpoint failed exact replay")
        return selection
