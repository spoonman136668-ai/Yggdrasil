"""WSP80 evaluator-private deterministic SELFTEST worlds and real paid sessions.

Learner and policy MUST NOT import this file. No arbitrary-state training API.
The evaluator's private transition function is not a free learning oracle.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from random import Random
import json

SEEDS=tuple(range(5601,5617))
STATES=tuple(product((0,1), repeat=6))
ACTIONS=tuple(range(6))
STAGE_A=144
CHARGES=384


def _rng(seed,purpose):
    value=sha256(f'WSP80|SELFTEST|{seed}|{purpose}'.encode('ascii')).digest()
    return Random(int.from_bytes(value,'big'))


@dataclass(frozen=True)
class Experience:
    before:tuple[int,...]
    action:int
    after:tuple[int,...]
    action_cost:int=1


@dataclass(frozen=True)
class World:
    seed:int
    family:str
    _roles:tuple[int,...]
    _channels:tuple[int,...]

    def _step_oracle(self,s,a):
        if type(s) is not tuple or s not in STATES or type(a) is not int or a not in ACTIONS:
            raise ValueError('evaluator-only state/action invalid')
        r=self._roles
        role=self._channels[a]
        t=list(s)
        t[r[role]]^=1
        if role>=1:
            if self.family=='degree2_control':
                effect=s[r[(role+1)%6]] & s[r[(role+3)%6]]
            elif self.family=='degree3_control':
                effect=s[r[(role+1)%6]] & s[r[(role+3)%6]] & s[r[(role+4)%6]]
            elif self.family=='quartic_positive':
                effect=(s[r[(role+1)%6]] & s[r[(role+2)%6]] &
                        s[r[(role+3)%6]] & s[r[(role+4)%6]])
            elif self.family=='quartic_complemented':
                effect=(s[r[(role+1)%6]] & s[r[(role+2)%6]] &
                        s[r[(role+3)%6]] & (1^s[r[(role+4)%6]]))
            else:
                raise ValueError('unknown family')
            t[r[role-1]]^=effect
        if role>=2:
            # A second sparse public interaction, still within the frozen <=3-term size.
            t[r[role-2]] ^= s[r[(role+2)%6]] ^ (
                s[r[(role+1)%6]] & s[r[(role+5)%6]])
        return tuple(t)

    def training_session(self):
        return Session(self)

    def receipt(self):
        hidden={'seed':self.seed,'family':self.family,
                'roles':self._roles,'channels':self._channels}
        return {'schema':'wsp80.source-private.v1','seed':self.seed,
                'family':self.family,
                'hidden_source_sha256':sha256(json.dumps(hidden,sort_keys=True,
                    separators=(',',':')).encode('ascii')).hexdigest(),
                'stageA_charges':STAGE_A,'max_charges':CHARGES,
                'reset_allowed':False}


class Session:
    def __init__(self,world):
        self._world=world
        self.current=(0,)*6
        self.ledger=[]

    def step(self,a):
        if type(a) is not int or a not in ACTIONS:
            raise ValueError('invalid paid action')
        if len(self.ledger)>=CHARGES:
            raise ValueError('paid action budget exceeded')
        s=self.current
        y=self._world._step_oracle(s,a)
        self.current=y
        row=Experience(s,a,y)
        self.ledger.append(row)
        return row


def build_world(seed,cohort='SELFTEST'):
    if type(seed) is not int or seed not in SEEDS or cohort!='SELFTEST':
        raise PermissionError('unregistered/protected source blocked')
    family=('degree2_control' if seed<=5604 else
            'degree3_control' if seed<=5608 else
            'quartic_positive' if seed<=5612 else 'quartic_complemented')
    r=_rng(seed,'shuffled-sensor-and-action-roles')
    roles=list(ACTIONS)
    channels=list(ACTIONS)
    r.shuffle(roles)
    r.shuffle(channels)
    world=World(seed,family,tuple(roles),tuple(channels))
    assert len(set(world._roles))==6 and len(set(world._channels))==6
    return world
