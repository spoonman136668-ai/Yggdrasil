"""FKP-19 source-safe physically chosen two-step delayed reward source.

Public TRAIN seeds ONLY. Nothing returns a protected law ID, unrealized reward,
counterfactual effect, or outcome before an action is physically selected.
The hidden polarity is inspectable in source; consequently the resulting
benchmark is known-family development only, NOT owner-controlled unseen science.
"""
from __future__ import annotations

from pathlib import Path
import sys

# Reuse the EXACT FKP18 public-only observation schema, not the hidden source.
sys.path.append(str(Path(__file__).resolve().parents[1] / "FKP-18"))
from temporal_trace import PublicStep, PublicTransition

TRAIN = tuple(range(991100, 991116))
TRAIN_EPISODES = 8
SCORED_EPISODES = 16
TOTAL_EPISODES = TRAIN_EPISODES + SCORED_EPISODES


def assert_train(seed):
    if type(seed) is not int or seed not in TRAIN:
        raise PermissionError("FKP19_UNKNOWN_OR_HELD_WORLD_FORBIDDEN")


def context_at(seed, episode):
    assert_train(seed)
    if type(episode) is not int or not 0 <= episode < TOTAL_EPISODES:
        raise ValueError("FKP19_EPISODE_RANGE")
    return (seed + episode) % 2


def exploratory_actions(seed, episode):
    if type(episode) is not int or not 0 <= episode < TRAIN_EPISODES:
        raise ValueError("FKP19_EXPLORATION_ONLY")
    return (episode // 2) % 2, (episode // 4) % 2


def scored_distractor(seed, episode):
    context_at(seed, episode)
    if episode < TRAIN_EPISODES:
        raise ValueError("FKP19_DISTRCTOR_SCORED_ONLY")
    return (episode // 4) % 2


def _polarity(seed):
    # This deterministic source-local parameter must NEVER be passed to a
    # policy or exported by the public session interface.
    return ((seed * 1103515245 + 12345) >> 17) & 1


def _public_state(ctx, phase):
    return (ctx, phase, 8, 8, 8, 8, 8, 8)


class PublicDelayedSession:
    """One action at each phase; delayed feedback only after second action."""

    __slots__ = ("__seed", "__context", "__phase", "__early", "__first")

    def __init__(self, seed, episode):
        assert_train(seed)
        self.__context = context_at(seed, episode)
        self.__seed = seed
        self.__phase = 0
        self.__early = None
        self.__first = None

    @property
    def public_state(self):
        return _public_state(self.__context, self.__phase)

    @property
    def done(self):
        return self.__phase == 2

    def apply(self, action):
        if type(action) is not int or action not in (0, 1):
            raise ValueError("FKP19_SOURCE_INVALID_BINARY_ACTION")
        if self.__phase == 0:
            before = self.public_state
            after = _public_state(self.__context, 1)
            row = PublicStep(before, action, after, 0.0, False, ())
            self.__early = action
            self.__first = PublicTransition(before, action, 0.0, after, False)
            self.__phase = 1
            return row
        if self.__phase == 1:
            before = self.public_state
            # Reward depends on an EARLIER chosen action, not this distractor.
            success = self.__early == (self.__context ^ _polarity(self.__seed))
            reward = 1.0 if success else -1.0
            after = _public_state(self.__context, 2)
            row = PublicStep(before, action, after, reward, True, (self.__first,))
            self.__phase = 2
            return row
        raise ValueError("FKP19_SESSION_TERMINATED")


def public_episode(seed, episode, early_action, distractor):
    """A physically selected public trajectory; never a counterfactual API."""
    session = PublicDelayedSession(seed, episode)
    first = session.apply(early_action)
    second = session.apply(distractor)
    if not session.done:
        raise AssertionError("FKP19_INCOMPLETE_TWO_STEP")
    return (first, second)
