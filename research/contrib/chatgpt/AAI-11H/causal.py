"""AAI-11H: tokenless causal structural run-length posterior, novel substrate.

This file NEVER reads privileged law/intermediates or the benchmark oracle.
Both arms consume precisely the SAME latest sixteen public observations.
"""
from __future__ import annotations
import json
import math
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"AAI-11P"))
sys.path.insert(0,str(HERE.parent/"AAI-11A"))
import world, controls
import learner as original

ARMS=("fixed16_posterior_ablation","runlength_posterior_candidate")
HORIZONS=(4,8,16)
ODDS=9.0
LOG_ODDS=math.log(ODDS)
LOG_RIGHT=math.log(.9)
LOG_NULL_REF=math.log(2.)


def hypothesis_posterior(errors):
    if not errors or any(type(v) is not int or v<0 or v>16 for v in errors):
        raise ValueError("invalid public hypothesis errors")
    minimum=min(errors)
    factors=[ODDS**(minimum-v) for v in errors]
    total=sum(factors)
    return tuple(v/total for v in factors)


def per_horizon(rows,horizon):
    """Original public structural grammar, observed mediator supervision only."""
    if horizon not in HORIZONS or len(rows)>16:
        raise ValueError("unfrozen causal horizon or public history")
    recent=rows[-horizon:]
    n=len(recent)
    errors=[[0]*width for width in original.SIZES]
    for x,obs in recent:
        k=original.x_key(x)
        for out,truths in enumerate((original.TRUTH01[k],
                                     original.TRUTH01[k],
                                     original.TRUTH2[k][obs[0]][obs[1]])):
            dst=errors[out]
            actual=obs[out]
            for i,value in enumerate(truths):
                dst[i]+=int(value!=actual)
    weights=[]
    log_bayes_factor=0.
    for counts in errors:
        weights.append(hypothesis_posterior(counts))
        minimum=min(counts)
        log_bayes_factor+=(n*(LOG_RIGHT+LOG_NULL_REF)
                           -minimum*LOG_ODDS
                           +math.log(sum(ODDS**(minimum-v) for v in counts))
                           -math.log(len(counts)))
    return tuple(weights),log_bayes_factor


class RunLengthCausalPosterior(original.GraphWindow):
    """Structural causal inference with online change-point run-length mixtures."""

    def __init__(self,arm):
        if arm not in ARMS:
            raise ValueError("unregistered AAI11H causal-model arm")
        self.arm=arm
        super().__init__("graph_recent16")

    def _invalidate(self):
        super()._invalidate()
        self._horizon_cache=None

    def _active_horizons(self):
        if self._horizon_cache is None:
            horizons=HORIZONS if self.arm=="runlength_posterior_candidate" else (16,)
            data=[per_horizon(self.rows,r) for r in horizons]
            logs=[item[1] for item in data]
            offset=max(logs)
            weights=[math.exp(v-offset) for v in logs]
            total=sum(weights)
            self._horizon_cache=tuple((w/total,item[0],r)
                                      for w,item,r in zip(weights,data,horizons))
        return self._horizon_cache

    @staticmethod
    def _forecast(weights,k):
        p0=sum(w*v for w,v in zip(weights[0],original.TRUTH01[k]))
        p1=sum(w*v for w,v in zip(weights[1],original.TRUTH01[k]))
        p2=0.
        for upstream0 in (0,1):
            for upstream1 in (0,1):
                joint=(p0 if upstream0 else 1-p0)*(p1 if upstream1 else 1-p1)
                p2+=joint*sum(w*v for w,v in zip(
                    weights[2],original.TRUTH2[k][upstream0][upstream1]))
        return p0,p1,p2

    def predict(self,x):
        k=original.x_key(x)
        if k not in self._pred_cache:
            prob=[0.,0.,0.]
            for run_prob,operator_weights,_ in self._active_horizons():
                causal=self._forecast(operator_weights,k)
                for j in range(3):
                    prob[j]+=run_prob*causal[j]
            result=tuple(round(max(0.,min(1.,v)),12) for v in prob)
            if any(not math.isfinite(v) for v in result):
                raise AssertionError("non-finite learned causal prediction")
            self._pred_cache[k]=result
        return self._pred_cache[k]

    def choose(self,row):
        world.visible(row)
        return controls.plan(self,row)

    def state(self):
        return {"type":"aai11h.structural-runlength-posterior.v1",
                "arm":self.arm,
                "rows":[[list(x),list(m)] for x,m in self.rows]}


def checkpoint(actor):
    if not isinstance(actor,RunLengthCausalPosterior):
        raise TypeError("wrong learned causal checkpoint type")
    return controls.canonical(actor.state())


def restore(arm,source):
    if arm not in ARMS or type(source) is not str:
        raise ValueError("unregistered or wrong-form public causal checkpoint")
    data=json.loads(source)
    if (controls.canonical(data)!=source or type(data) is not dict or
        set(data)!={"type","arm","rows"} or
        data["type"]!="aai11h.structural-runlength-posterior.v1" or
        data["arm"]!=arm or type(data["rows"]) is not list or
        len(data["rows"])>16):
        raise ValueError("invalid or noncanonical AAI11H causal checkpoint")
    actor=RunLengthCausalPosterior(arm)
    for item in data["rows"]:
        if type(item) is not list or len(item)!=2:
            raise ValueError("invalid causal public observation row")
        x=world.bits(item[0],6)
        m=world.bits(item[1],3)
        actor._append((x,m))
    if checkpoint(actor)!=source:
        raise ValueError("public cold restoration changed state")
    return actor
