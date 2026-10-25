"""Independent conventional full nine-feature public logistic selected-effect control.

Matches actual R1 public features and chosen-action input; does NOT reuse
original Ygg LocalCell update, native learning rule, or private source state.
C28 original source FIT events only: no physical environment import/actions.
"""
from __future__ import annotations
import hashlib
import json
import math
from research.native.itd02.r1.native_policy import PublicGrid, canonical

SCHEMA="itd02.c30.public-nine-feature-per-action-logistic.v1"


def independently_encoded_public(s):
    if type(s) is not PublicGrid:
        raise ValueError("NOT_PUBLIC_ORIGINAL_POSE")
    vals=[s.x,s.y,s.goal_x,s.goal_y]
    if any(type(v) is not int or not 0<=v<=64 for v in vals) or (
        type(s.direction) is not int or s.direction not in (0,1,2,3) or
        type(s.front_blocked) is not bool
    ):
        raise ValueError("INVALID_PUBLIC_NINE_FEATURE_SOURCE")
    gx=s.goal_x-s.x
    gy=s.goal_y-s.y
    phi=(1.0, max(-1.,min(1.,gx/16)),max(-1.,min(1.,gy/16)),
         max(0.,min(1.,(abs(gx)+abs(gy))/32)))
    return (*phi,*(float(s.direction==d) for d in range(4)),float(s.front_blocked))


def sigmoid(x):
    return 1.0/(1.0+math.exp(-max(-20.,min(20.,x))))


def bounded(value):
    if not math.isfinite(value):
        raise ValueError("NONFINITE_ONLINE_WEIGHT")
    return max(-32.,min(32.,value))


class IndependentPublicLogistic:
    def __init__(self,momentum):
        if type(momentum) not in (float,int) or momentum not in (0.,.85):
            raise ValueError("NON_PREREGISTERED_MOMENTUM")
        self.momentum=float(momentum)
        self.weight={str(a):[0.]*9 for a in (0,1,2)}
        self.velocity={str(a):[0.]*9 for a in (0,1,2)}
        self.updates=0

    def predict(self,s,action):
        if type(action) is not int or action not in (0,1,2):
            raise ValueError("ILLEGAL_PUBLIC_SELECTED_ACTION")
        phi=independently_encoded_public(s)
        return sigmoid(sum(w*f for w,f in zip(self.weight[str(action)],phi)))

    def observe(self,s,action,target):
        if type(target) is not int or target not in (0,1):
            raise ValueError("ILLEGAL_PUBLIC_SELECTED_CONSEQUENCE")
        phi=independently_encoded_public(s)
        p=self.predict(s,action)
        key=str(action)
        for i in range(9):
            delta=(target-p)*phi[i]
            self.velocity[key][i]=bounded(self.momentum*self.velocity[key][i]+delta)
            self.weight[key][i]=bounded(self.weight[key][i]+.16*self.velocity[key][i])
        self.updates+=1

    def snapshot(self):
        return {"schema":SCHEMA,"momentum":self.momentum,"updates":self.updates,
                "weight":self.weight,"velocity":self.velocity}

    def checkpoint(self):
        data=self.snapshot()
        digest=hashlib.sha256(canonical(data)).hexdigest()
        blob=canonical({"payload":data,"sha256":digest})
        if len(blob)>32768:raise ValueError("LOGISTIC_CHECKPOINT_TOO_LARGE")
        return blob

    @classmethod
    def restore(cls,blob):
        if type(blob) is not bytes or not 0<len(blob)<=32768:
            raise ValueError("INVALID_LOGISTIC_CHECKPOINT")
        try:
            wire=json.loads(blob)
            if type(wire) is not dict or set(wire)!={"payload","sha256"}:
                raise ValueError("LOGISTIC_WIRE_FIELDS")
            data=wire["payload"]
            if type(data) is not dict or set(data)!={"schema","momentum","updates","weight","velocity"}:
                raise ValueError("LOGISTIC_SCHEMA_FIELDS")
            if hashlib.sha256(canonical(data)).hexdigest()!=wire["sha256"]:
                raise ValueError("LOGISTIC_CHECKPOINT_TAMPER")
            if data["schema"]!=SCHEMA or type(data["updates"]) is not int or not 0<=data["updates"]<=1000000:
                raise ValueError("LOGISTIC_COUNTER_OR_IDENTITY")
            model=cls(data["momentum"])
            for name in ("weight","velocity"):
                if type(data[name]) is not dict or set(data[name])!={"0","1","2"}:
                    raise ValueError("LOGISTIC_ACTION_COEFFICIENTS")
                for action,values in data[name].items():
                    if type(values) is not list or len(values)!=9 or any(
                        type(v) not in (int,float) or not math.isfinite(v) or abs(v)>32
                        for v in values):
                        raise ValueError("LOGISTIC_VECTOR_INVALID")
            model.updates=data["updates"]
            model.weight={a:list(v) for a,v in data["weight"].items()}
            model.velocity={a:list(v) for a,v in data["velocity"].items()}
            return model
        except (TypeError,KeyError,OverflowError,AttributeError) as exc:
            raise ValueError("BAD_LOGISTIC_CHECKPOINT") from exc
