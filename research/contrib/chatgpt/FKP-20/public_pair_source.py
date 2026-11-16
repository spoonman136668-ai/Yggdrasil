"""FKP-20 original public physical delayed two-parent XOR source.

Only 16 deterministic, inspectable TRAIN worlds are accessible. A session
receives actual 0/1 actions at four stages; source feedback is 0 on stages
0..2 and the only terminal +1/-1 appears AFTER the fourth action is applied.
No future/counterfactual reward or private law is returned to a policy.
This is a nonblind synthetic development source, not unfamiliar-law science.
"""
from __future__ import annotations

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "FKP-18"))
from temporal_trace import PublicStep, PublicTransition

TRAIN=tuple(range(992100,992116))
PHYSICAL_ACTIONS=4
EXPLORE=32
SCORE=16
TOTAL=EXPLORE+SCORE
PAIRS=((0,1),(0,2),(1,2))


def assert_train(seed):
    if type(seed) is not int or seed not in TRAIN:
        raise PermissionError("FKP20_UNKNOWN_OR_PROTECTED_SEED")


def context(seed,episode):
    assert_train(seed)
    if type(episode) is not int or not 0<=episode<TOTAL:
        raise ValueError("FKP20_EPISODE_RANGE")
    return ((episode//8)%2) if episode<EXPLORE else ((seed+episode)%2)


def exploration_tape(seed,episode):
    if type(episode) is not int or not 0<=episode<EXPLORE:
        raise ValueError("FKP20_FROZEN_EXPLORATION_ONLY")
    return (context(seed,episode),(episode//4)%2,
            (episode//2)%2,episode%2,episode//16)


def scored_distractor(seed,episode):
    context(seed,episode)
    if episode<EXPLORE:
        raise ValueError("FKP20_SCORED_ONLY")
    return (episode//4)%2


def _private_law(seed):
    # Never provided to an arm; source itself is inspectable and nonblind.
    i=seed-TRAIN[0]
    return PAIRS[i%3],(i//3)%2


def _public_state(ctx,phase):
    return (ctx,phase,8,8,8,8,8,8)


class SelectedPublicEpisode:
    """Four actual public actions, strictly sequential, never oracle scoring."""

    __slots__=("__seed","__ctx","__stage","__actions","__history")

    def __init__(self,seed,episode):
        assert_train(seed)
        self.__ctx=context(seed,episode)
        self.__seed=seed
        self.__stage=0
        self.__actions=[]
        self.__history=[]

    @property
    def public_state(self):
        return _public_state(self.__ctx,self.__stage)

    @property
    def done(self):
        return self.__stage==PHYSICAL_ACTIONS

    def apply(self,action):
        if type(action) is not int or action not in (0,1):
            raise ValueError("FKP20_INVALID_CHOSEN_ACTION")
        if self.__stage>=PHYSICAL_ACTIONS:
            raise ValueError("FKP20_EPISODE_ALREADY_TERMINATED")
        before=self.public_state
        self.__actions.append(action)
        next_stage=self.__stage+1
        after=_public_state(self.__ctx,next_stage)
        reward=0.0
        if next_stage==PHYSICAL_ACTIONS:
            pair,polarity=_private_law(self.__seed)
            parity=self.__actions[pair[0]]^self.__actions[pair[1]]
            reward=1.0 if parity==(self.__ctx^polarity) else -1.0
        row=PublicStep(before,action,after,reward,
                       next_stage==PHYSICAL_ACTIONS,tuple(self.__history))
        self.__history.append(PublicTransition(before,action,reward,
                                               after,row.done))
        self.__stage=next_stage
        return row
