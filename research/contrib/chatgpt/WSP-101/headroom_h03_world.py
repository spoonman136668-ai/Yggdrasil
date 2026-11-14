"""H03 separate synthetic DEV causal world, not the H02 or protected WSP101 sources.

This is an evaluator. Models receive only public observation/reward events.
Never import this module in the independent symbolic control implementation.
"""
from __future__ import annotations
import hashlib

DEV_IDS=tuple(range(16))
SOURCE_ACTIONS=(63,107,116,14,95,19,37,119,26,121,76,110,35,111,56,62,90,125,50,71,6,83)
HELDOUT_ACTIONS=(1,2,5,8,10,11,13,20,30,31,42,46,48,51,52,61,73,78,79,106,108,114,118,126)
ALLOWED_MASKS=tuple(m for m in range(1,128) if 2<=m.bit_count()<=4)
assert len(ALLOWED_MASKS)==91
assert len(SOURCE_ACTIONS)==22 and len(HELDOUT_ACTIONS)==24
assert not set(SOURCE_ACTIONS)&set(HELDOUT_ACTIONS)


def _rank(world, field, index=0):
    if type(world) is not int or world not in DEV_IDS:
        raise PermissionError("H03 DEV-only world identities")
    raw=f"WSP101-H03|DEV|{field}|{world}|{index}".encode("ascii")
    return int.from_bytes(hashlib.sha256(raw).digest(),"big")


def _secret(world):
    family=_rank(world,"FAMILY")%6
    mask=ALLOWED_MASKS[_rank(world,"MASK")%len(ALLOWED_MASKS)]
    return family,mask


def _causal_effect(family, mask, action):
    if (type(family) is not int or family not in range(6) or
        type(mask) is not int or mask not in ALLOWED_MASKS or
        type(action) is not int or not 1<=action<=127):
        raise ValueError("H03_INVALID_PROGRAM")
    n=(mask & action).bit_count()
    if family==0:
        return n%2
    if family==1:
        return int(n>=2)
    if family==2:
        return int(n==1)
    if family==3:
        return int(n>=3)
    if family==4:
        return (n%2)^int((action&3)==3)
    return int(n==mask.bit_count())


class _World:
    def __init__(self,world):
        self._world=world
        self._family,self._mask=_secret(world)
        self._episode=0
        self.reset()
    def reset(self):
        self._episode+=1
        self._steps=0
        self._latch=0
        self._previous_action=0
        return 0
    def step(self,action):
        if type(action) is not int or not 0<=action<=127:
            raise ValueError("H03_INVALID_ACTION")
        if self._steps>=2:
            raise ValueError("H03_EPISODE_LIMIT")
        if self._steps==0:
            observation=0
            if action:
                self._latch=_causal_effect(self._family,self._mask,action)
                self._previous_action=action
        else:
            if action!=0:
                raise ValueError("H03_READOUT_REQUIRES_ACTION_ZERO")
            flip=int(self._previous_action!=0 and
                     _rank(self._world,"NOISE",self._previous_action*65536+self._episode)%8==0)
            observation=self._latch^flip
        self._steps+=1
        return {"observation":observation,"reward":observation}


class PublicEndpoint:
    __slots__=("reset","step")
    def __init__(self,w):
        self.reset=w.reset
        self.step=w.step


def observer(world):
    if type(world) is not int or world not in DEV_IDS:
        raise PermissionError("H03 original/protected worlds unavailable")
    return PublicEndpoint(_World(world))


def public_source(world):
    endpoint=observer(world)
    rows=[]
    for action in SOURCE_ACTIONS:
        if endpoint.reset()!=0:
            raise ValueError("H03_PASSIVE_LEAK_ON_RESET")
        a=endpoint.step(action)
        b=endpoint.step(0)
        if a!={"observation":0,"reward":0} or (
            b["observation"] not in (0,1) or b["observation"]!=b["reward"]
        ):
            raise ValueError("H03_BAD_PUBLIC_CONSEQUENCE")
        rows.append((action,b["observation"]))
    return tuple(rows)


def public_passive(world):
    endpoint=observer(world)
    rows=[]
    for _ in SOURCE_ACTIONS:
        endpoint.reset()
        a,b=endpoint.step(0),endpoint.step(0)
        if a!={"observation":0,"reward":0} or b!=a:
            raise ValueError("H03_PASSIVE_INFORMATION_LEAK")
        rows.append((0,b["observation"]))
    return tuple(rows)


def scoring_truth_only(world,action):
    """Evaluator-only hidden true response; never passed into a learner."""
    return _causal_effect(*_secret(world),action)
