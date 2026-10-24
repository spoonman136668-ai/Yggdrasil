"""ITD-02 R1 Yggdrasil native three-action cellular policy.

Independent Yggdrasil local-plasticity mechanism. Public observations only;
this is an interface development candidate, NOT accepted native transfer.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
from dataclasses import dataclass

SCHEMA="yggdrasil.itd02.r1.public-grid-three-action-cellular-v1"
ACTIONS=(0,1,2)
N=9


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf-8")


@dataclass(frozen=True)
class PublicGrid:
    x:int
    y:int
    goal_x:int
    goal_y:int
    direction:int
    front_blocked:bool


def features(observation):
    if (type(observation) is not PublicGrid or
        any(type(v) is not int or v<0 or v>64 for v in
            (observation.x,observation.y,observation.goal_x,observation.goal_y)) or
        type(observation.direction) is not int or
        observation.direction not in range(4) or
        type(observation.front_blocked) is not bool):
        raise ValueError("Y_R1_INVALID_PUBLIC_GRID")
    dx=observation.goal_x-observation.x
    dy=observation.goal_y-observation.y
    x=[1.,max(-1.,min(1.,dx/16)),max(-1.,min(1.,dy/16)),
       max(0.,min(1.,(abs(dx)+abs(dy))/32))]
    x += [float(observation.direction==i) for i in range(4)]
    x += [float(observation.front_blocked)]
    return tuple(x)


def distance(x):
    return abs(x.goal_x-x.x)+abs(x.goal_y-x.y)


def limited(x,limit=32.):
    if not math.isfinite(x):
        raise ValueError("Y_R1_NONFINITE_LOCAL_STATE")
    return max(-limit,min(limit,x))


@dataclass
class LocalCell:
    fast:float=0.
    slow:float=0.
    updates:int=0

    def output(self,feature):
        return feature*(.70*self.fast+.30*self.slow)

    def learn(self,feature,error):
        self.fast=limited(self.fast+.16*error*feature)
        self.slow=limited(.95*self.slow+.05*self.fast)
        self.updates+=1


class GridColony:
    """Three independent sets of nine local cells and bounded ring coupling.

    Local plasticity updates ONLY the public selected action. No BFS/teacher
    direction/hidden task state, and no binary action remapping.
    """
    def __init__(self):
        self.cells={str(a):[LocalCell() for _ in range(N)] for a in ACTIONS}
        self.feedback_updates=0

    def score(self,observation,action):
        if type(action) is not int or action not in ACTIONS:
            raise ValueError("Y_R1_PUBLIC_ACTION_INVALID")
        phi=features(observation)
        val=[c.output(x) for c,x in zip(self.cells[str(action)],phi)]
        nonlinear=sum(.025*val[j]*val[(j+1)%N] for j in range(N))
        return sum(val)+nonlinear

    def choose(self,observation):
        scores=[self.score(observation,a) for a in ACTIONS]
        return max(ACTIONS,key=lambda a:(scores[a],-a))

    def observe(self,before,action,after,reward,terminal):
        if (type(action) is not int or action not in ACTIONS or
            type(reward) not in (float,int) or not math.isfinite(reward) or
            abs(reward)>100 or type(terminal) is not bool):
            raise ValueError("Y_R1_INVALID_PUBLIC_FEEDBACK")
        phi=features(before)
        features(after)
        if self.feedback_updates>=2**63-1:
            raise ValueError("Y_R1_FEEDBACK_COUNT_EXHAUSTED")
        expected=float(reward)+.15*(distance(before)-distance(after))
        expected=limited(expected,1.)
        prediction=self.score(before,action)
        error=limited(expected-prediction,1.)
        next_state=copy.deepcopy(self)
        for cell,value in zip(next_state.cells[str(action)],phi):
            cell.learn(value,error)
        next_state.feedback_updates+=1
        self.cells=next_state.cells
        self.feedback_updates=next_state.feedback_updates

    def snapshot(self):
        body={"schema":SCHEMA,"feedback_updates":self.feedback_updates,
            "cells":{key:[{"fast":c.fast,"slow":c.slow,"updates":c.updates}
                          for c in cohort]
                     for key,cohort in self.cells.items()}}
        return body

    def save(self):
        body=self.snapshot()
        payload=canonical(body)
        if len(payload)>16384:
            raise ValueError("Y_R1_EXCESSIVE_STATE")
        return canonical({"payload":body,"sha256":hashlib.sha256(payload).hexdigest()})

    @classmethod
    def restore(cls,blob):
        if type(blob) is not bytes or not 0<len(blob)<=16384:
            raise ValueError("Y_R1_BAD_CHECKPOINT_SIZE")
        try:
            wire=json.loads(blob)
            if set(wire)!={"payload","sha256"}:
                raise ValueError("Y_R1_CHECKPOINT_FORMAT")
            data=wire["payload"]
            if hashlib.sha256(canonical(data)).hexdigest()!=wire["sha256"]:
                raise ValueError("Y_R1_CHECKPOINT_TAMPER")
            if (set(data)!={"schema","feedback_updates","cells"} or
                data["schema"]!=SCHEMA or set(data["cells"])!={"0","1","2"}):
                raise ValueError("Y_R1_CHECKPOINT_SOURCE_IDENTITY")
            n=data["feedback_updates"]
            if type(n) is not int or n<0 or n>=2**63:
                raise ValueError("Y_R1_CHECKPOINT_COUNTER")
            next_state=cls()
            for key,records in data["cells"].items():
                if len(records)!=N:
                    raise ValueError("Y_R1_CELL_COUNT")
                cells=[]
                for x in records:
                    if (set(x)!={"fast","slow","updates"} or
                        type(x["updates"]) is not int or x["updates"]<0 or
                        type(x["fast"]) not in (int,float) or
                        type(x["slow"]) not in (int,float) or
                        not math.isfinite(x["fast"]) or not math.isfinite(x["slow"]) or
                        abs(x["fast"])>32 or abs(x["slow"])>32):
                        raise ValueError("Y_R1_CELL_CORRUPTION")
                    cells.append(LocalCell(float(x["fast"]),float(x["slow"]),x["updates"]))
                next_state.cells[key]=cells
            next_state.feedback_updates=n
            return next_state
        except (KeyError,TypeError,OverflowError) as exc:
            raise ValueError("Y_R1_CHECKPOINT_STRUCTURE") from exc
