"""Private WSP84 unregistered four-world Boolean-operator source.

No learner, predictor, or control may import this file or inspect the hidden
masks/target. Only physically charged continuous action consequences are
released as public learner observations. The protected WSP80 cohort cannot
be instantiated through this module.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from random import Random
import json

COHORT={10011:"three_temporal_majority",10012:"three_temporal_majority",
        10013:"memoryless_control",10014:"memoryless_control"}
ACTIONS=tuple(range(6))
STATES=tuple(product((0,1),repeat=6))
CONTEXTS=((),)+tuple((i,) for i in ACTIONS)+tuple(
    (i,j) for i in ACTIONS for j in ACTIONS)
PAID=384
assert len(CONTEXTS)==43


@dataclass(frozen=True)
class PublicEvent:
    before: tuple
    action: int
    after: tuple
    action_cost: int=1


def _secret_seed(seed,domain):
    return int.from_bytes(sha256(
        f"WSP84|DEV|{seed}|{domain}-v1".encode("ascii")).digest(),"big")


def _secret_balanced_mask(seed,slot):
    seq=list(ACTIONS)
    Random(_secret_seed(seed,f"mask|{slot}")).shuffle(seq)
    return tuple(sorted(seq[:3]))


class World:
    def __init__(self,seed):
        if type(seed) is not int or seed not in COHORT:
            raise PermissionError("WSP84 only admits frozen unregistered developer seeds")
        self.seed=seed
        self.family=COHORT[seed]
        self._hidden_action_masks=tuple(_secret_balanced_mask(seed,i)
                                         for i in range(3))
        self._hidden_target=_secret_seed(seed,"target")%6

    def _transition(self,before,action,history):
        if (type(before) is not tuple or before not in STATES
                or type(action) is not int or action not in ACTIONS
                or type(history) not in (tuple,list)
                or any(type(h) is not int or h not in ACTIONS for h in history)):
            raise ValueError("evaluator-private query invalid")
        out=list(before)
        out[action]^=1
        if self.family=="three_temporal_majority":
            entries=(action,history[-1] if history else None,
                     history[-2] if len(history)>=2 else None)
            bits=[int(entry is not None and entry in allowed)
                  for entry,allowed in zip(entries,self._hidden_action_masks)]
            if sum(bits)>=2:
                out[self._hidden_target]^=1
        return tuple(out)

    def private_truth(self,history,state,action):
        return self._transition(state,action,history)

    def session(self):
        return PaidSession(self)

    def private_receipt(self):
        payload={"seed":self.seed,"family":self.family,
                 "hidden_action_masks":self._hidden_action_masks,
                 "target":self._hidden_target}
        return sha256(json.dumps(payload,sort_keys=True,
            separators=(",",":")).encode("ascii")).hexdigest()


class PaidSession:
    def __init__(self,world):
        self._world=world
        self.current=(0,)*6
        self.actions=[]
        self.ledger=[]

    def step(self,action):
        if (type(action) is not int or action not in ACTIONS
                or len(self.ledger)>=PAID):
            raise ValueError("invalid or overbudget physical action")
        before=self.current
        after=self._world._transition(before,action,self.actions)
        event=PublicEvent(before,action,after)
        self.ledger.append(event)
        self.actions.append(action)
        self.current=after
        return event


def fixed_action(seed,step):
    if (type(seed) is not int or seed not in COHORT
            or type(step) is not int or not 0<=step<PAID):
        raise PermissionError("unregistered source action outside frozen scope")
    value=sha256(f"WSP84|DEV|{seed}|action|{step}-v1".encode("ascii")).digest()
    return int.from_bytes(value[:8],"big")%6
