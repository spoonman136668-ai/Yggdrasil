"""AAI-11D tokenless causal posterior and uncertainty-aware decision gate.

Same eight public observations, operator grammar and ordinary public updates as
original graph_recent8. All private true-law simulator operations forbidden.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"AAI-11A"))
sys.path.insert(0,str(HERE.parent/"AAI-11P"))
import world,controls
import learner as graph

ARMS=("posterior_planner","risk_calibrated_planner")
RISK_LAMBDA=0.5
LIKELIHOOD_RATIO=9.0


def posterior(errors):
    # Bernoulli .9 correct/.1 error for a deterministic binary rule.
    # Uniform rule prior; subtract minimum count for stable normalization.
    if not errors or any(type(v) is not int or v<0 or v>8 for v in errors):
        raise ValueError("invalid public mismatch signatures")
    minimum=min(errors)
    unscaled=[LIKELIHOOD_RATIO**(minimum-v) for v in errors]
    total=sum(unscaled)
    return tuple(q/total for q in unscaled)


class PosteriorCausalModel(graph.GraphWindow):
    def __init__(self,name):
        if name not in ARMS:raise ValueError("unknown frozen posterior arm")
        super().__init__("graph_recent8")
        self.arm=name

    def _invalidate(self):
        super()._invalidate()
        self._posterior_cache=None

    def _weights(self):
        if self._posterior_cache is None:
            self._posterior_cache=tuple(posterior(a) for a in self.stats["mismatches"])
        return self._posterior_cache

    def predict(self,x):
        k=graph.x_key(x)
        if k not in self._pred_cache:
            w0,w1,w2=self._weights()
            t0=graph.TRUTH01[k]
            p0=sum(w*bit for w,bit in zip(w0,t0))
            p1=sum(w*bit for w,bit in zip(w1,t0))
            downstream=0.0
            for m0 in (0,1):
                for m1 in (0,1):
                    weight=(p0 if m0 else 1-p0)*(p1 if m1 else 1-p1)
                    structural=sum(w*bit for w,bit in zip(
                        w2,graph.TRUTH2[k][m0][m1]))
                    downstream+=weight*structural
            result=(round(p0,12),round(p1,12),round(downstream,12))
            if any(not 0<=v<=1 for v in result):
                raise AssertionError("invalid posterior causal forecast")
            self._pred_cache[k]=result
        return self._pred_cache[k]

    def choose(self,row):
        world.visible(row)
        if self.arm=="posterior_planner":
            return controls.plan(self,row)
        return self._risk_plan(row)

    def _risk_plan(self,row):
        """Frozen sqrt posterior-uncertainty penalty, no extra actions or data."""
        world.visible(row)
        spent=row["actions_taken"]
        if spent>=2:return None
        x=tuple(row["x"])
        goal=tuple(row["goal"])
        best=float(row["reward"])
        selected=None
        for first in world.ACTIONS:
            x1=world.setbit(x,first)
            p1=self.predict(x1)
            value=self._risk_value(p1,goal,spent+1)
            if value>best+1e-10:
                selected,best=first,value
            if spent==0:
                for second in world.ACTIONS:
                    x2=world.setbit(x1,second)
                    p2=self.predict(x2)
                    value2=self._risk_value(p2,goal,2)
                    if value2>best+1e-10:
                        selected,best=first,value2
        return selected

    @staticmethod
    def _risk_value(probs,goal,steps):
        uncertainty=math.sqrt(sum(p*(1-p) for p in probs))
        return controls.expected(probs,goal,steps)-RISK_LAMBDA*uncertainty

    def state(self):
        return {"type":"aai11d.posterior-causal.v1",
                "arm":self.arm,
                "rows":[[list(x),list(m)] for x,m in self.rows]}


def checkpoint(model):
    if not isinstance(model,PosteriorCausalModel):
        raise TypeError("not an AAI11D posterior model")
    return controls.canonical(model.state())


def restore(arm,payload):
    if arm not in ARMS:raise ValueError("unknown posterior arm")
    data=json.loads(payload)
    if (controls.canonical(data)!=payload or
        type(data) is not dict or set(data)!={"type","arm","rows"} or
        data["type"]!="aai11d.posterior-causal.v1" or data["arm"]!=arm or
        type(data["rows"]) is not list or len(data["rows"])>8):
        raise ValueError("invalid or noncanonical posterior checkpoint")
    actor=PosteriorCausalModel(arm)
    for item in data["rows"]:
        if type(item) is not list or len(item)!=2:
            raise ValueError("invalid public observation row")
        x=world.bits(item[0],6)
        m=world.bits(item[1],3)
        actor._append((x,m))
    if checkpoint(actor)!=payload:
        raise ValueError("public cold restore changed")
    return actor
