"""FKP-21 16 inspectable synthetic public action/consequence worlds.

Eight low-degree rule worlds, plus eight adversarial extensions indistinguishable
on the 12 pre-frozen observations but differing at one new input each.
Source is ORIGINAL, inspectable and TRAIN ONLY; never a blind scientific source.
No model imports this file or receives world ID, mask, or source-private flip.
"""
from __future__ import annotations
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]/"FKP-18"))
from temporal_trace import PublicStep, PublicTransition

TRAIN=tuple(range(993100,993116))
TRAIN_PATTERNS=(3,4,5,6,8,9,10,11,12,13,14,15)
FIRST_PROBES=(0,1,2,7)
MASKS=(0x451,0x328,0x6ad,0x13b,0x2ed,0x7a9,0x5c3,0x39e)
NUM_FEATURES=11


def _check_seed(seed):
    if type(seed) is not int or seed not in TRAIN:
        raise PermissionError("FKP21_UNKNOWN_OR_PROTECTED_WORLD")


def _features(x):
    if type(x) is not int or not 0<=x<16:
        raise ValueError("FKP21_INVALID_SOURCE_INPUT")
    bits=tuple((x>>i)&1 for i in range(4))
    return (1,*bits,
            *(bits[i]*bits[j] for i in range(4) for j in range(i+1,4)))


def _private_reward(seed,x):
    _check_seed(seed)
    index=seed-TRAIN[0]
    bits=_features(x)
    mask=MASKS[index%8]
    output=sum(((mask>>k)&1)*v for k,v in enumerate(bits))%2
    # A new *higher-order* intervention-outcome relationship flips exactly
    # one previously unseen input, leaving ALL 12 training effects unchanged.
    if index>=8 and x==FIRST_PROBES[(index-8)%4]:
        output^=1
    return 1.0 if output else -1.0


def _state(ctx,phase):
    return (ctx,phase,8,8,8,8,8,8)


class PublicRuleSession:
    """First actions chosen before knowing their physically earned consequence."""
    __slots__=("__seed","__ctx","__phase","__actions","__history")

    def __init__(self,seed,context):
        _check_seed(seed)
        if type(context) is not int or context not in (0,1):
            raise ValueError("FKP21_BAD_PUBLIC_CONTEXT")
        self.__seed=seed
        self.__ctx=context
        self.__phase=0
        self.__actions=[]
        self.__history=[]

    @property
    def public_state(self):
        return _state(self.__ctx,self.__phase)

    @property
    def done(self):
        return self.__phase==4

    def apply(self,action):
        if type(action) is not int or action not in (0,1):
            raise ValueError("FKP21_ONLY_PHYSICAL_BINARY_ACTION")
        if self.done:
            raise ValueError("FKP21_PHYSICAL_EPISODE_ALREADY_DONE")
        before=self.public_state
        self.__actions.append(action)
        after=_state(self.__ctx,self.__phase+1)
        reward=0.0
        if self.__phase==3:
            x=(self.__ctx<<3)|self.__actions[0]|(self.__actions[1]<<1)|(self.__actions[2]<<2)
            reward=_private_reward(self.__seed,x)
        done=self.__phase==3
        row=PublicStep(before,action,after,reward,done,tuple(self.__history))
        self.__history.append(PublicTransition(before,action,reward,after,done))
        self.__phase+=1
        return row


def physical_probe(seed,x):
    """Frozen source protocol selects public action tuple; no oracle value API."""
    _check_seed(seed)
    if type(x) is not int or not 0<=x<16:
        raise ValueError("FKP21_INVALID_PUBLIC_PROBE_INPUT")
    session=PublicRuleSession(seed,x>>3)
    actions=(x&1,(x>>1)&1,(x>>2)&1,0)
    rows=[]
    for action in actions:
        rows.append(session.apply(action))
    if not session.done:
        raise AssertionError("FKP21_PHYSICAL_SESSION_INCOMPLETE")
    return tuple(rows)
