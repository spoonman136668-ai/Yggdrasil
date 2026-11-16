"""FKP-22 original inspectable public physical intervention source.

16 SUPPORT worlds teach correlated residual structures. 16 in-family TRAIN
evaluation worlds use different lower-order base masks. Eight shift TRAIN
worlds have a new cross-pattern residual correlation.
Protected original DEV/TRANSFER is never accepted. Only chosen actions are
executed, and ±1 outcome arrives AFTER physically selected fourth action.
"""
from __future__ import annotations

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]/"FKP-18"))
from temporal_trace import PublicStep, PublicTransition

SUPPORT=tuple(range(994000,994016))
KNOWN=tuple(range(994100,994116))
SHIFT=tuple(range(994200,994208))
ALL=SUPPORT+KNOWN+SHIFT
TRAIN=(3,4,5,6,8,9,10,11,12,13,14,15)
PROBES=(0,1,2,7)
SUPPORT_MASKS=(0x451,0x328,0x6ad,0x13b)
EVAL_MASKS=(0x2ed,0x7a9,0x5c3,0x39e)
KNOWN_SIGNATURES=(0,3,12,15)
SHIFT_SIGNATURES=(0,5,10,15)


def _validate_seed(seed):
    if type(seed) is not int or seed not in ALL:
        raise PermissionError("FKP22_PROTECTED_OR_UNKNOWN_WORLD")


def _bits(x):
    if type(x) is not int or not 0<=x<16:
        raise ValueError("FKP22_PUBLIC_INPUT_UINT4")
    b=tuple((x>>i)&1 for i in range(4))
    return (1,*b,*(b[i]&b[j] for i in range(4) for j in range(i+1,4)))


def _private_bit(seed,x):
    _validate_seed(seed)
    f=_bits(x)
    if seed in SUPPORT:
        index=seed-SUPPORT[0]
        base=SUPPORT_MASKS[(index//4)%4]
        residual=KNOWN_SIGNATURES[index%4]
    elif seed in KNOWN:
        index=seed-KNOWN[0]
        base=EVAL_MASKS[(index//4)%4]
        residual=KNOWN_SIGNATURES[index%4]
    else:
        index=seed-SHIFT[0]
        base=EVAL_MASKS[(index//4)%2]
        residual=SHIFT_SIGNATURES[index%4]
    bit=sum(v*((base>>k)&1) for k,v in enumerate(f))&1
    if x in PROBES:
        bit^=(residual>>PROBES.index(x))&1
    return bit


def _state(context,phase):
    return (context,phase,8,8,8,8,8,8)


class PublicChosenSession:
    __slots__=("__seed","__context","__phase","__actions","__history")

    def __init__(self,seed,context):
        _validate_seed(seed)
        if type(context) is not int or context not in (0,1):
            raise ValueError("FKP22_INVALID_PUBLIC_CONTEXT")
        self.__seed=seed
        self.__context=context
        self.__phase=0
        self.__actions=[]
        self.__history=[]

    @property
    def public_state(self):
        return _state(self.__context,self.__phase)

    @property
    def done(self):
        return self.__phase==4

    def apply(self,action):
        if type(action) is not int or action not in (0,1):
            raise ValueError("FKP22_PUBLIC_BINARY_ACTION_ONLY")
        if self.done:
            raise ValueError("FKP22_ACTION_AFTER_TERMINAL")
        before=self.public_state
        self.__actions.append(action)
        after=_state(self.__context,self.__phase+1)
        reward=0.0
        if self.__phase==3:
            x=(self.__context<<3)|self.__actions[0]|(
                self.__actions[1]<<1)|(self.__actions[2]<<2)
            reward=1.0 if _private_bit(self.__seed,x) else -1.0
        terminal=self.__phase==3
        public=PublicStep(before,action,after,reward,terminal,
                          tuple(self.__history))
        self.__history.append(PublicTransition(before,action,reward,after,
                                               terminal))
        self.__phase+=1
        return public


def physically_apply(seed,input_pattern):
    """This is an actual chosen-action episode, NOT a label-oracle lookup."""
    _validate_seed(seed)
    if type(input_pattern) is not int or not 0<=input_pattern<16:
        raise ValueError("FKP22_PUBLIC_INPUT_REQUIRED")
    session=PublicChosenSession(seed,input_pattern>>3)
    actions=(input_pattern&1,(input_pattern>>1)&1,
             (input_pattern>>2)&1,0)
    observed=tuple(session.apply(a) for a in actions)
    if not session.done or any(row.reward!=0.0 for row in observed[:3]):
        raise AssertionError("FKP22_PHYSICAL_CAUSAL_CONTRACT")
    return observed
