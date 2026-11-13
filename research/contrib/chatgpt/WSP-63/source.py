"""WSP63 evaluator-only no-reset physics with one-bit action effects.

Four fresh chain, four XOR/AND, four cubic out-of-basis worlds. Hidden source
physics and oracle task distances never enter either learner. All physical
training action consequences must come from one stateful session per arm.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from random import Random
import json

SEEDS = tuple(range(2901, 2913))
STATES = tuple(product((0, 1), repeat=4))
CHANNELS = tuple(range(4))
INITIAL = (0, 0, 0, 0)
TRAIN_ACTIONS = 48
TASKS_PER_WORLD = 32


def _rng(seed, label):
    key=sha256(f"WSP63|SELFTEST|{seed}|{label}".encode("ascii")).digest()
    return Random(int.from_bytes(key,"big"))


@dataclass(frozen=True)
class Experience:
    before: tuple[int,...]
    action: int
    after: tuple[int,...]
    action_cost: int = 1


@dataclass(frozen=True)
class Task:
    start: tuple[int,...]
    target: tuple[int,...]
    _shortest: int


@dataclass(frozen=True)
class World:
    seed: int
    family: str
    _bit_roles: tuple[int,...]
    _channel_roles: tuple[int,...]

    def _step_oracle(self, state, channel):
        if type(state) is not tuple or state not in STATES or (
                type(channel) is not int or channel not in CHANNELS):
            raise ValueError("invalid physical source action")
        role=self._channel_roles[channel]
        bits=self._bit_roles
        if role==0:
            flip=1
        elif role==1:
            flip=state[bits[0]]
        elif role==2:
            if self.family=="chain":
                flip=state[bits[1]]
            else:
                flip=state[bits[0]] ^ (state[bits[1]] & state[bits[3]])
        elif role==3:
            if self.family=="chain":
                flip=state[bits[2]]
            elif self.family=="xor_and":
                flip=state[bits[1]] ^ (state[bits[0]] & state[bits[2]])
            else:
                # Explicit cubic out-of-family negative control:
                # 3-input AND requires degree-3 ANF, not the 7-term
                # degree-2 basis supplied to the new compressed learner.
                flip=state[bits[0]] & state[bits[1]] & state[bits[2]]
        else:
            raise RuntimeError("invalid hidden role")
        after=list(state)
        after[bits[role]] ^= flip
        return tuple(after)

    def training_session(self):
        return Session(self)

    def _shortest(self, start, target):
        if start==target:
            return 0
        q=deque([(start,0)])
        seen={start}
        while q:
            state,depth=q.popleft()
            if depth>=6:
                continue
            for action in CHANNELS:
                future=self._step_oracle(state,action)
                if future==target:
                    return depth+1
                if future not in seen:
                    seen.add(future)
                    q.append((future,depth+1))
        return None

    def tasks(self):
        candidates=[]
        for start in STATES:
            for target in STATES:
                shortest=self._shortest(start,target)
                if shortest is not None and 2<=shortest<=6:
                    candidates.append(Task(start,target,shortest))
        if len(candidates)<TASKS_PER_WORLD:
            raise RuntimeError("not enough reachable heldout goals")
        r=_rng(self.seed,"heldout-goals")
        r.shuffle(candidates)
        return tuple(candidates[:TASKS_PER_WORLD])

    def evaluate(self, task, actions):
        if actions is None or type(actions) not in (tuple,list) or len(actions)>6:
            return False
        current=task.start
        for channel in actions:
            current=self._step_oracle(current,channel)
        return current==task.target

    def receipt(self):
        secret={"seed":self.seed,"family":self.family,
                "bits":self._bit_roles,"channels":self._channel_roles}
        tasks=[[t.start,t.target,t._shortest] for t in self.tasks()]
        def digest(x):
            return sha256(json.dumps(x,sort_keys=True,
                   separators=(",",":")).encode("ascii")).hexdigest()
        return {
            "schema":"wsp63.selftest-world.v1","seed":self.seed,
            "family":self.family,
            "source_sha256":digest(secret),
            "heldout_sha256":digest(tasks),
            "tasks":TASKS_PER_WORLD,
            "charged_actions_per_arm":TRAIN_ACTIONS,
            "training_resets_allowed":False
        }


class Session:
    def __init__(self, world):
        self._world=world
        self.state=INITIAL
        self.ledger=[]

    def step(self, action):
        if len(self.ledger)>=TRAIN_ACTIONS:
            raise ValueError("exceeded charged action ceiling")
        before=self.state
        after=self._world._step_oracle(before,action)
        self.state=after
        observation=Experience(before,action,after)
        self.ledger.append(observation)
        return observation


def build_world(seed,cohort="SELFTEST"):
    if cohort!="SELFTEST" or type(seed) is not int or seed not in SEEDS:
        raise PermissionError("WSP63 protected/unregistered source blocked")
    family=("chain" if seed<=2904 else
            "xor_and" if seed<=2908 else "cubic_negative")
    r=_rng(seed,"hidden-roles")
    bits,channels=list(CHANNELS),list(CHANNELS)
    r.shuffle(bits)
    r.shuffle(channels)
    w=World(seed,family,tuple(bits),tuple(channels))
    assert len(set(w._bit_roles))==len(set(w._channel_roles))==4
    assert len(w.tasks())==TASKS_PER_WORLD
    return w
