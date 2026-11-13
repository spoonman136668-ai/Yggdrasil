"""Evaluator-private WSP83 four-world DEV-only temporal XOR source.

This module MUST NEVER be imported by a learner, action policy, or control.
Hidden offset/marker are evaluator-private; only separately charged,
continuous before/action/after events cross into public model fitting.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json

COHORT = {9901:"temporal_xor_new",9902:"temporal_xor_new",
          9903:"memoryless_control",9904:"memoryless_control"}
STATES = tuple(product((0,1),repeat=6))
ACTIONS = tuple(range(6))
CONTEXTS = ((),(0,1),(1,0),(0,0),(1,1),(2,2),(3,3),(4,4),
            (5,5),(2,4),(4,2),(5,3))
PAID = 384
assert len(CONTEXTS)==12


@dataclass(frozen=True)
class Event:
    before: tuple
    action: int
    after: tuple
    action_cost: int=1


def _private_int(seed, label):
    return int.from_bytes(sha256(
        f"WSP83|DEV|{seed}|{label}-v1".encode("ascii")).digest(),"big")


class World:
    def __init__(self,seed):
        if type(seed) is not int or seed not in COHORT:
            raise PermissionError("WSP83 developer-only four-world admission")
        self.seed=seed
        self.family=COHORT[seed]
        self._offset=1+_private_int(seed,"offset")%5
        self._marker=_private_int(seed,"marker")%6

    def _transition(self,before,action,history):
        if (type(before) is not tuple or before not in STATES
                or type(action) is not int or action not in ACTIONS
                or type(history) not in (list,tuple)
                or any(type(h) is not int or h not in ACTIONS for h in history)):
            raise ValueError("private oracle query invalid")
        out=list(before)
        out[action]^=1
        if self.family=="temporal_xor_new":
            equal=len(history)>=2 and history[-2]==history[-1]
            marker=bool(history) and history[-1]==self._marker
            if equal != marker:
                out[(action+self._offset)%6]^=1
        return tuple(out)

    def private_truth(self,context,state,action):
        return self._transition(state,action,context)

    def session(self):
        return Session(self)

    def private_receipt(self):
        record={"seed":self.seed,"family":self.family,
                "offset":self._offset,"marker":self._marker}
        return sha256(json.dumps(record,sort_keys=True,
            separators=(",",":")).encode("ascii")).hexdigest()


class Session:
    def __init__(self,world):
        self._world=world
        self.current=(0,)*6
        self.ledger=[]
        self.action_history=[]

    def step(self,action):
        if (type(action) is not int or action not in ACTIONS
                or len(self.ledger)>=PAID):
            raise ValueError("bad or unpaid physical source action")
        before=self.current
        after=self._world._transition(before,action,self.action_history)
        event=Event(before,action,after)
        self.ledger.append(event)
        self.action_history.append(action)
        self.current=after
        return event


def fixed_action(seed,step):
    if (type(seed) is not int or seed not in COHORT
            or type(step) is not int or not 0<=step<PAID):
        raise PermissionError("outside frozen developer action schedule")
    value=sha256(f"WSP83|DEV|{seed}|action|{step}".encode("ascii")).digest()
    return int.from_bytes(value[:8],"big")%6
