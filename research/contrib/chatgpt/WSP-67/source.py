"""WSP67 evaluator-only charged physical world; never import into neural learner.

All four action roles and sensor roles are hidden, independently shuffled per
SELFTEST world. All unknown causal effects belong to a prospectively GIVEN
constant/at-most-two-literal conjunction family. Source/test labels are not
used for weight construction, neural training or physical action selection.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from random import Random
import json

SEEDS=tuple(range(4101,4109))
STATES=tuple(product((0,1),repeat=4))
ACTIONS=(0,1,2,3)
TRAIN_ACTIONS=96
PHASE_A=64
COMPOSITES=32


def rng(seed,kind):
    key=sha256(f"WSP67|SELFTEST|{seed}|{kind}".encode("ascii")).digest()
    return Random(int.from_bytes(key,"big"))


@dataclass(frozen=True)
class Experience:
    before:tuple[int,...]
    action:int
    after:tuple[int,...]
    action_cost:int=1


@dataclass(frozen=True)
class Composite:
    start:tuple[int,...]
    actions:tuple[int,int]
    _intermediate:tuple[int,...]
    _finish:tuple[int,...]


@dataclass(frozen=True)
class World:
    seed:int
    _roles:tuple[int,...]
    _channels:tuple[int,...]

    def _step_oracle(self,state,channel):
        if (type(state) is not tuple or state not in STATES or
                type(channel) is not int or channel not in ACTIONS):
            raise ValueError("invalid evaluator-only physical query")
        role=self._channels[channel]
        r=self._roles
        out=list(state)
        if role==0:
            out[r[0]]^=1
        elif role==1:
            if state[r[0]]:out[r[1]]^=1
        elif role==2:
            if state[r[1]]:out[r[2]]^=1
            if state[r[1]] and not state[r[3]]:out[r[0]]^=1
        elif role==3:
            if state[r[2]] and state[r[0]]:out[r[3]]^=1
            if state[r[2]]:out[r[1]]^=1
        else:
            raise RuntimeError("invalid hidden role")
        return tuple(out)

    def training_session(self):
        return Session(self)

    def composite_tests(self):
        source=rng(self.seed,"heldout-two-action-compositions")
        combos=list(product(STATES,ACTIONS,ACTIONS))
        source.shuffle(combos)
        selected=[]
        for state,action_a,action_b in combos[:COMPOSITES]:
            mid=self._step_oracle(state,action_a)
            last=self._step_oracle(mid,action_b)
            selected.append(Composite(state,(action_a,action_b),mid,last))
        return tuple(selected)

    def receipt(self):
        secret={"seed":self.seed,"roles":self._roles,"channels":self._channels}
        tests=[[list(c.start),list(c.actions),list(c._intermediate),
                list(c._finish)] for c in self.composite_tests()]
        def hash_json(v):
            return sha256(json.dumps(v,sort_keys=True,
                          separators=(",",":")).encode("ascii")).hexdigest()
        return {"schema":"wsp67.weight-programming-world.v1",
                "seed":self.seed,"source_sha256":hash_json(secret),
                "heldout_composites_sha256":hash_json(tests),
                "states":len(STATES),"channels":len(ACTIONS),
                "charged_training_actions":TRAIN_ACTIONS,
                "phase_a":PHASE_A,"composites":len(tests),
                "training_resets_allowed":False}


class Session:
    def __init__(self,world):
        self._world=world
        self.state=(0,0,0,0)
        self.ledger=[]

    def step(self,action):
        if len(self.ledger)>=TRAIN_ACTIONS:
            raise ValueError("charged action cap")
        old=self.state
        after=self._world._step_oracle(old,action)
        self.state=after
        row=Experience(old,action,after)
        self.ledger.append(row)
        return row


def build_world(seed,cohort="SELFTEST"):
    if cohort!="SELFTEST" or type(seed) is not int or seed not in SEEDS:
        raise PermissionError("WSP67 protected/unregistered worlds forbidden")
    r=rng(seed,"secret-sensor-and-action-roles")
    roles=list(ACTIONS)
    channels=list(ACTIONS)
    r.shuffle(roles)
    r.shuffle(channels)
    world=World(seed,tuple(roles),tuple(channels))
    assert len(set(world._roles))==len(set(world._channels))==4
    assert len(world.composite_tests())==COMPOSITES
    return world
