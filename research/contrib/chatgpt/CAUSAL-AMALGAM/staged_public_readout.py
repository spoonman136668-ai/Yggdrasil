"""Separate pre-outcome readouts from witness admission in a two-action episode."""

from yggdrasil.native_context_basis import canonical, digest, pin, require
from yggdrasil.native_cumulative_learner import EXPERIENCE_SOURCE
from yggdrasil.native_episode_experience import _views
from yggdrasil.public_causal_cells import PublicCausalCells


class StagedPublicReadout:
    """Bind an externally observed episode to one native/specialist snapshot.

    The caller supplies actions and observations. Neither source execution
    nor source-owner admission belongs in this readout.
    """

    def __init__(self, model, identifier, views):
        require(pin(identifier), "STAGED_EPISODE_ID")
        self._views = _views(views)
        require(self._views[0][0] == self._views[1][0], "STAGED_PAIRED_CONTEXT")
        self._model = model
        self._identifier = identifier
        self._first = self._state = self._second = None
        self._closed = False

    def _probabilities(self, *public):
        native = self._model.native.experience_context_forecast(self._views[0], *public)
        return (native, *self._model.specialist_forecasts(self._views, *public))

    def first_action(self, action):
        require(self._first is None and not self._closed, "STAGED_FIRST_ACTION_ORDER")
        action = PublicCausalCells._bit(action, "ACTION")
        result = self._probabilities(action)
        self._first = action
        return result

    def observe_transition(self, state):
        require(self._first is not None and self._state is None and not self._closed,
                "STAGED_TRANSITION_ORDER")
        self._state = PublicCausalCells._bit(state, "S2")

    def second_action(self, action):
        require(self._state is not None and self._second is None and not self._closed,
                "STAGED_SECOND_ACTION_ORDER")
        action = PublicCausalCells._bit(action, "ACTION")
        result = self._probabilities(self._first, self._state, action)
        self._second = action
        return result

    def observe_reward(self, reward):
        require(self._second is not None and not self._closed, "STAGED_REWARD_ORDER")
        reward = PublicCausalCells._bit(reward, "Y")
        row = {"s1": self._views[0][0], "x1": self._first, "s2": self._state,
               "x2": self._second, "y": reward}
        packet = canonical([self._identifier, self._views, row])
        # The core witness append is atomic. Close this staged readout even
        # if it rejects the packet, to avoid a second attempted admission.
        self._closed = True
        return self._model.observe_experience(
            self._identifier, self._views, row, source_sha256=EXPERIENCE_SOURCE,
            packet_sha256=digest(packet),
        )
