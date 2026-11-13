"""WSP66 evaluator-only chronological hidden-mode physics.

The learner never imports this source or sees hidden mode, channel roles,
oracle outcomes, or heldout labels. Training has ONE no-reset 48-action
session; standardized heldout TEST episodes restart separately, exposing the
same public action/consequence prefixes to all models but no train updates.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from random import Random
import json

SEEDS=tuple(range(3201,3217))
CHANNELS=(0,1,2,3)
TRAIN_CHARGES=48
TEST_CASES=64


def _rng(seed,label):
    digest=sha256(f"WSP66|SELFTEST|{seed}|{label}".encode("ascii")).digest()
    return Random(int.from_bytes(digest,"big"))


@dataclass(frozen=True)
class PublicExperience:
    before:tuple[int,...]
    action:int
    after:tuple[int,...]
    action_cost:int=1


@dataclass(frozen=True)
class HeldoutCase:
    history:tuple[PublicExperience,...]
    current:tuple[int,...]
    action:int
    _truth:tuple[int,...]
    _mode:int
    _prefix_actions:tuple[int,...]


@dataclass(frozen=True)
class World:
    seed:int
    bits:int
    _sensor_roles:tuple[int,...]
    _channel_roles:tuple[int,...]

    @property
    def family(self):
        return "mode_gate_3" if self.bits==3 else "mode_xor_4"

    def _step(self,state,action,mode):
        if (type(state) is not tuple or len(state)!=self.bits or
                any(type(v) is not int or v not in (0,1) for v in state) or
                type(action) is not int or action not in CHANNELS or
                mode not in (0,1)):
            raise ValueError("invalid evaluator-only physical state")
        role=self._channel_roles[action]
        out=list(state)
        bits=self._sensor_roles
        if role==0:
            mode ^= 1  # Completely unobservable physical mode transition.
        elif role==1:
            out[bits[0]] ^= 1
        elif role==2:
            out[bits[1]] ^= state[bits[0]]
            if self.bits==4:
                out[bits[2]] ^= 1  # Coupled visible effects, source only.
        elif role==3:
            trigger=mode if self.bits==3 else (mode ^ state[bits[0]])
            out[bits[-1]] ^= trigger
        else:
            raise RuntimeError("hidden channel roles violated")
        return tuple(out),mode

    def session(self):
        return Session(self)

    def test_cases(self):
        rng=_rng(self.seed,"heldout-action-prefixes")
        hidden_channel=self._channel_roles.index(3)
        cases=[]
        already=set()
        while len(cases)<TEST_CASES:
            length=rng.randrange(8,17)
            prefix=tuple(rng.choice(CHANNELS) for _ in range(length))
            if prefix in already:
                continue
            already.add(prefix)
            state=(0,)*self.bits
            mode=0
            observations=[]
            for action in prefix:
                after,mode=self._step(state,action,mode)
                observations.append(PublicExperience(state,action,after))
                state=after
            truth,_=self._step(state,hidden_channel,mode)
            cases.append(HeldoutCase(tuple(observations),state,
                        hidden_channel,truth,mode,prefix))
        assert len(cases)==TEST_CASES
        return tuple(cases)

    def receipt(self):
        private={"seed":self.seed,"bits":self.bits,
                 "roles":self._sensor_roles,"channels":self._channel_roles}
        heldout=[
            [list(case._prefix_actions),list(case.current),case.action,
             list(case._truth),case._mode]
            for case in self.test_cases()
        ]
        def digest(x):
            return sha256(json.dumps(x,sort_keys=True,
                          separators=(",",":")).encode("ascii")).hexdigest()
        return {
            "schema":"wsp65.hidden-mode-world.v1",
            "seed":self.seed,"bits":self.bits,"family":self.family,
            "hidden_source_sha256":digest(private),
            "heldout_test_sha256":digest(heldout),
            "test_cases":len(heldout),"training_charges":TRAIN_CHARGES,
            "training_resets":False,
            "eval_prefixes_are_public_only":True
        }


class Session:
    def __init__(self,world):
        self._world=world
        self.state=(0,)*world.bits
        self._hidden_mode=0
        self.charges=[]

    def step(self,action):
        if len(self.charges)>=TRAIN_CHARGES:
            raise ValueError("training action ceiling")
        before=self.state
        after,h=self._world._step(before,action,self._hidden_mode)
        self.state,self._hidden_mode=after,h
        row=PublicExperience(before,action,after)
        self.charges.append(row)
        return row


def build_world(seed,cohort="SELFTEST"):
    if type(seed) is not int or seed not in SEEDS or cohort!="SELFTEST":
        raise PermissionError("WSP66 protected/unregistered world blocked")
    bits=3 if seed<=3208 else 4
    rng=_rng(seed,"hidden-role-permutation")
    roles=list(range(bits))
    channels=list(CHANNELS)
    rng.shuffle(roles)
    rng.shuffle(channels)
    world=World(seed,bits,tuple(roles),tuple(channels))
    assert len(set(world._channel_roles))==4
    assert len(set(world._sensor_roles))==bits
    assert len(world.test_cases())==TEST_CASES
    return world
