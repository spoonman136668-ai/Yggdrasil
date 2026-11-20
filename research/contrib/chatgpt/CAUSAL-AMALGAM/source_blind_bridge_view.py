"""Pure data-only observation boundary for future NS-Gym Bridge science.

Never import or instantiate the source, use a source actor, sample a world,
or update a native/JEPA checkpoint here.  Official Bridge and NSBridgeWrapper
may return source transition probabilities and ground-truth change metadata
in raw Gym "info" even when change notifications are disabled.  A future
source-owner-authorized runner MUST ensure only the freshly constructed
PublicView result reaches the learner or any matched conventional control.

This validator does not enforce process isolation.  If an agent is also
handed the raw Gym result, env, or a reference to its wrapper, it can
bypass the boundary.  That execution boundary requires owner qualification.
"""
from dataclasses import dataclass

_KEYS = frozenset({"state", "env_change", "delta_change", "relative_time"})
_MAP_STATE_COUNT = 40  # Pinned official 5x8 NS-Gym Bridge map.


@dataclass(frozen=True, slots=True)
class PublicView:
    state: int
    step: int
    reward: int | None
    terminated: bool
    truncated: bool


def _public_state(observation, step):
    if type(observation) is not dict or frozenset(observation) != _KEYS:
        raise ValueError("SOURCE_BLIND_OBSERVATION_SCHEMA")
    state = observation["state"]
    if type(state) is not int or not 0 <= state < _MAP_STATE_COUNT:
        raise ValueError("SOURCE_BLIND_PUBLIC_STATE")
    time = observation["relative_time"]
    if type(time) is not int or time != step:
        raise ValueError("SOURCE_BLIND_PUBLIC_STEP")
    return state


def from_reset(raw):
    """Copy only the public state from an official (obs, info) reset result."""
    if type(raw) not in (tuple, list) or len(raw) != 2:
        raise ValueError("SOURCE_BLIND_RESET_SHAPE")
    observation, _private_info = raw
    state = _public_state(observation, 0)
    # Deliberately do not read, inspect, serialize or forward _private_info.
    return PublicView(state=state, step=0, reward=None,
                      terminated=False, truncated=False)


def from_step(raw, *, step):
    """Copy only public consequence fields from a five-part Gym step result.

    The caller supplies the independently tracked count of actual source
    actions.  We reject a mismatched reported relative time; the source's
    actual outcome/reward is never modified.  No entire raw dict or info object
    is retained by the returned immutable PublicView.
    """
    if type(step) is not int or not 1 <= step <= 1000000:
        raise ValueError("SOURCE_BLIND_PUBLIC_STEP")
    if type(raw) not in (tuple, list) or len(raw) != 5:
        raise ValueError("SOURCE_BLIND_STEP_SHAPE")
    observation, reward, terminated, truncated, _private_info = raw
    state = _public_state(observation, step)
    if type(reward) is not int or reward not in (-1, 0, 1):
        raise ValueError("SOURCE_BLIND_SCALAR_REWARD")
    if type(terminated) is not bool or type(truncated) is not bool:
        raise ValueError("SOURCE_BLIND_TERMINAL_FLAGS")
    return PublicView(state=state, step=step, reward=reward,
                      terminated=terminated, truncated=truncated)
