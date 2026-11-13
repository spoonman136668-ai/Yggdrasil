"""WSP64 evaluator-only variable-sensor and hidden-mode physical worlds.

Neither the hidden physics nor the role maps, task plans, or hidden mode are
supplied to the learner. All training observations arise from a stateful
no-reset session's charged action consequences. SELFTEST only.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from random import Random
import json

SEEDS=tuple(range(3001,3013))
ACTIONS=tuple(range(4))
TASKS_PER_WORLD=32


def _rng(seed,label):
    h=sha256(f"WSP64|SELFTEST|{seed}|{label}".encode("ascii")).digest()
    return Random(int.from_bytes(h,"big"))


@dataclass(frozen=True)
class Experience:
    before: tuple[int,...]
    action: int
    after: tuple[int,...]
    action_cost: int=1


@dataclass(frozen=True)
class Task:
    start: tuple[int,...]
    target: tuple[int,...]
    _shortest: int


@dataclass(frozen=True)
class World:
    seed: int
    family: str
    bits: int
    _roles: tuple[int,...]
    _channels: tuple[int,...]

    @property
    def states(self):
        return tuple(product((0,1),repeat=self.bits))

    @property
    def budget(self):
        return 64 if self.family=="latent" else 48

    def _step_oracle(self,before,action,mode=0):
        if (type(before) is not tuple or before not in self.states or
                type(action) is not int or action not in ACTIONS or
                mode not in (0,1)):
            raise ValueError("invalid evaluator-only source state/action")
        roles=self._roles
        role=self._channels[action]
        after=list(before)
        if self.family=="small":
            if role==0:
                after[roles[0]] ^= 1
            elif role==1:
                after[roles[1]] ^= before[roles[0]]
            elif role==2:
                after[roles[2]] ^= before[roles[1]]
            else:
                after[roles[0]] ^= before[roles[1]]
                after[roles[2]] ^= before[roles[1]]
        elif self.family=="large":
            if role==0:
                after[roles[0]] ^= 1
            elif role==1:
                after[roles[1]] ^= before[roles[0]]
            elif role==2:
                after[roles[2]] ^= before[roles[0]]
                after[roles[3]] ^= (before[roles[0]] & before[roles[1]])
            else:
                after[roles[4]] ^= before[roles[2]]
        else:
            # Hidden role3 changes mode without changing visible sensors.
            # Different hidden modes can have incompatible visible effects
            # for the same visible state and chosen action.
            if role==0:
                after[roles[0]] ^= mode
            elif role==1:
                after[roles[1]] ^= 1
            elif role==2:
                after[roles[2]] ^= before[roles[1]]
            else:
                mode ^= 1
        return tuple(after),mode

    def training_session(self):
        return Session(self)

    def _reachability(self):
        initial=(0,)*self.bits
        seen={initial}
        frontier=deque([initial])
        while frontier:
            state=frontier.popleft()
            for action in ACTIONS:
                future,_=self._step_oracle(state,action)
                if future not in seen:
                    seen.add(future)
                    frontier.append(future)
        return tuple(sorted(seen))

    def _shortest(self,start,target):
        if start==target: return 0
        seen={start}
        frontier=deque([(start,0)])
        while frontier:
            state,dist=frontier.popleft()
            if dist>=6: continue
            for action in ACTIONS:
                nxt,_=self._step_oracle(state,action)
                if nxt==target: return dist+1
                if nxt not in seen:
                    seen.add(nxt)
                    frontier.append((nxt,dist+1))
        return None

    def tasks(self):
        if self.family=="latent":
            return ()
        reachable=self._reachability()
        candidates=[]
        for start in reachable:
            for target in reachable:
                distance=self._shortest(start,target)
                if distance is not None and 2<=distance<=6:
                    candidates.append(Task(start,target,distance))
        if len(candidates)<TASKS_PER_WORLD:
            raise RuntimeError("not enough reachable multi-step tasks")
        r=_rng(self.seed,"heldout-goals")
        r.shuffle(candidates)
        return tuple(candidates[:TASKS_PER_WORLD])

    def evaluate(self,task,sequence):
        if sequence is None or type(sequence) not in (tuple,list) or len(sequence)>6:
            return False
        state=task.start
        for action in sequence:
            state,_=self._step_oracle(state,action)
        return state==task.target

    def receipt(self):
        secret={"seed":self.seed,"family":self.family,"bits":self.bits,
                "roles":self._roles,"channels":self._channels}
        tasks=[[t.start,t.target,t._shortest] for t in self.tasks()]
        def digest(obj):
            return sha256(json.dumps(obj,sort_keys=True,
                          separators=(",",":")).encode("ascii")).hexdigest()
        return {"schema":"wsp64.variable-latent-world.v1",
                "seed":self.seed,"family":self.family,"bits":self.bits,
                "hidden_sha256":digest(secret),"heldout_sha256":digest(tasks),
                "heldout_tasks":len(tasks),"charged_actions":self.budget,
                "training_resets":False}


class Session:
    """The sole physical training entrypoint; current state cannot be set."""
    def __init__(self,world):
        self._world=world
        self.state=(0,)*world.bits
        self._mode=0
        self.ledger=[]

    def step(self,action):
        if len(self.ledger)>=self._world.budget:
            raise ValueError("charged physical action ceiling")
        before=self.state
        after,new_mode=self._world._step_oracle(before,action,self._mode)
        self.state,self._mode=after,new_mode
        observed=Experience(before,action,after)
        self.ledger.append(observed)
        return observed


def build_world(seed,cohort="SELFTEST"):
    if cohort!="SELFTEST" or type(seed) is not int or seed not in SEEDS:
        raise PermissionError("WSP64 source is SELFTEST only")
    family=("small" if seed<=3004 else
            "large" if seed<=3008 else "latent")
    bits={"small":3,"large":5,"latent":4}[family]
    r=_rng(seed,"shuffled-physical-channel-roles")
    roles=list(range(bits))
    channels=list(ACTIONS)
    r.shuffle(roles)
    r.shuffle(channels)
    w=World(seed,family,bits,tuple(roles),tuple(channels))
    if family!="latent":
        assert len(w.tasks())==32
    assert len(set(w._roles))==bits and len(set(w._channels))==4
    return w
