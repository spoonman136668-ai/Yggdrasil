"""FKP-23 synthetic public physical causal-world source (TRAIN family only).

16 support worlds carry residual relations K; 8 *later* update worlds carry S.
A fresh 16-world S cohort tests adaptation; a separate 16-world K return
cohort tests retention. Source-private masks and cohort memberships are NEVER
delivered by a public action observation. This is inspectable toy data, not
owner-controlled independent hidden-law science first-use.
"""
from __future__ import annotations

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]/"FKP-18"))
from temporal_trace import PublicStep, PublicTransition

SUPPORT=tuple(range(995000,995016))
UPDATE=tuple(range(995100,995108))
SHIFT_EVAL=tuple(range(995200,995216))
RETURN_EVAL=tuple(range(995300,995316))
ALL=SUPPORT+UPDATE+SHIFT_EVAL+RETURN_EVAL
BASE_INPUTS=(3,4,5,6,8,9,10,11,12,13,14,15)
RESIDUAL_INPUTS=(0,1,2,7)
SUPPORT_MASKS=(0x451,0x328,0x6ad,0x13b)
UPDATE_MASKS=(0x6ad,0x13b)
EVAL_MASKS=(0x2ed,0x7a9,0x5c3,0x39e)
FAMILIAR=(0,3,12,15)
CHANGED=(0,5,10,15)


def assert_train(seed):
    if type(seed) is not int or seed not in ALL:
        raise PermissionError("FKP23_UNKNOWN_OR_PROTECTED_SOURCE")


def _f(x):
    if type(x) is not int or not 0<=x<16:
        raise ValueError("FKP23_PUBLIC_FOUR_BIT_INPUT")
    bits=tuple((x>>k)&1 for k in range(4))
    return (1,*bits,*(bits[i]*bits[j] for i in range(4)
                      for j in range(i+1,4)))


def _true_consequence(seed,x):
    assert_train(seed)
    f=_f(x)
    if seed in SUPPORT:
        n=seed-SUPPORT[0]
        mask=SUPPORT_MASKS[(n//4)%4]
        signature=FAMILIAR[n%4]
    elif seed in UPDATE:
        n=seed-UPDATE[0]
        mask=UPDATE_MASKS[(n//4)%2]
        signature=CHANGED[n%4]
    elif seed in SHIFT_EVAL:
        n=seed-SHIFT_EVAL[0]
        mask=EVAL_MASKS[(n//4)%4]
        signature=CHANGED[n%4]
    else:
        n=seed-RETURN_EVAL[0]
        mask=EVAL_MASKS[(n//4)%4]
        signature=FAMILIAR[n%4]
    y=sum(f[i]*((mask>>i)&1) for i in range(11))&1
    if x in RESIDUAL_INPUTS:
        y^=(signature>>RESIDUAL_INPUTS.index(x))&1
    return 1.0 if y else -1.0


def _public(ctx,phase):
    return (ctx,phase,8,8,8,8,8,8)


class PhysicalEpisode:
    __slots__=("__seed","__ctx","__phase","__chosen","__past")

    def __init__(self,seed,context):
        assert_train(seed)
        if type(context) is not int or context not in (0,1):
            raise ValueError("FKP23_BINARY_PUBLIC_CONTEXT")
        self.__seed=seed
        self.__ctx=context
        self.__phase=0
        self.__chosen=[]
        self.__past=[]

    @property
    def public_state(self):
        return _public(self.__ctx,self.__phase)

    @property
    def done(self):
        return self.__phase==4

    def apply(self,action):
        if type(action) is not int or action not in (0,1):
            raise ValueError("FKP23_ONLY_SELECTED_BINARY_ACTION")
        if self.done:
            raise ValueError("FKP23_TERMINATED")
        before=self.public_state
        self.__chosen.append(action)
        after=_public(self.__ctx,self.__phase+1)
        reward=0.0
        if self.__phase==3:
            x=(self.__ctx<<3)|(self.__chosen[0])|(
                self.__chosen[1]<<1)|(self.__chosen[2]<<2)
            reward=_true_consequence(self.__seed,x)
        last=self.__phase==3
        observation=PublicStep(before,action,after,reward,last,
                               tuple(self.__past))
        self.__past.append(PublicTransition(before,action,reward,
                                           after,last))
        self.__phase+=1
        return observation


def physical_action_episode(seed,x):
    """Act on the selected source first; return only earned public trajectory."""
    assert_train(seed)
    if type(x) is not int or not 0<=x<16:
        raise ValueError("FKP23_INVALID_CHOSEN_INPUT")
    session=PhysicalEpisode(seed,x>>3)
    actions=(x&1,(x>>1)&1,(x>>2)&1,0)
    observations=tuple(session.apply(a) for a in actions)
    if not session.done or any(row.reward!=0.0 for row in observations[:3]):
        raise AssertionError("FKP23_PREMATURE_OUTCOME")
    return observations
