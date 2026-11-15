"""AAI-11I: outcome-conditioned causal belief-state planning, no hidden law.

Same exact 8 PUBLIC (x,mediator) observations, rule grammar, and 9:1
posterior as the frozen AAI-11D baseline. The only novel behavior is
anticipating REAL information from the first intervention before deciding
the second. Imagination is never fed to actual learner memory.
"""
from __future__ import annotations
import itertools
import json
import math
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"AAI-11P"))
sys.path.insert(0,str(HERE.parent/"AAI-11A"))
sys.path.insert(0,str(HERE.parent/"AAI-11D"))
import world,controls
import learner as graph
import calibration as fixed_posterior

ARM="causal_feedback_expectimax"
OUTCOMES=tuple(itertools.product((0,1),repeat=3))
TIE_EPS=1e-10


def _dot(weights,truth):
    return sum(w*v for w,v in zip(weights,truth))


def _predict_joint(weights,k):
    """Model predictive P(m0,m1,m2) obeying structural downstream dependency."""
    w0,w1,w2=weights
    truth01=graph.TRUTH01[k]
    p0=_dot(w0,truth01)
    p1=_dot(w1,truth01)
    result={}
    for m0,m1 in itertools.product((0,1),repeat=2):
        upstream=(p0 if m0 else 1-p0)*(p1 if m1 else 1-p1)
        p2=_dot(w2,graph.TRUTH2[k][m0][m1])
        result[(m0,m1,0)]=upstream*(1-p2)
        result[(m0,m1,1)]=upstream*p2
    if abs(sum(result.values())-1.)>1e-10:
        raise AssertionError("causal rule predictive joint failed normalization")
    if any(not 0<=p<=1 or not math.isfinite(p) for p in result.values()):
        raise AssertionError("invalid causal probability")
    return result


def _hypothetical_weights(actor,k,observed):
    """Actual recent8 posterior updated with ONE imagined PUBLIC row, in scratch only.

    Exact original 8-row eviction and mismatch recurrence. No simulator/law
    is queried, no permanently updated checkpoint or future outcome leaked.
    """
    if type(observed) is not tuple or len(observed)!=3:
        raise ValueError("invalid hypothetical public mediator tuple")
    world.bits(observed,3)
    errors=[list(v) for v in actor.stats["mismatches"]]
    if len(actor.rows)==8:
        old_x,old_m=actor.rows[0]
        old_k=graph.x_key(old_x)
        old_truth=(graph.TRUTH01[old_k],
                   graph.TRUTH01[old_k],
                   graph.TRUTH2[old_k][old_m[0]][old_m[1]])
        for o in range(3):
            for idx,t in enumerate(old_truth[o]):
                errors[o][idx]-=int(t!=old_m[o])
    truth=(graph.TRUTH01[k],graph.TRUTH01[k],
           graph.TRUTH2[k][observed[0]][observed[1]])
    for o in range(3):
        for idx,t in enumerate(truth[o]):
            errors[o][idx]+=int(t!=observed[o])
    return tuple(fixed_posterior.posterior(a) for a in errors)


def _forecast(weights,k):
    w0,w1,w2=weights
    bits=graph.TRUTH01[k]
    p0=_dot(w0,bits)
    p1=_dot(w1,bits)
    p2=0.
    for m0,m1 in itertools.product((0,1),repeat=2):
        mass=(p0 if m0 else 1-p0)*(p1 if m1 else 1-p1)
        p2+=mass*_dot(w2,graph.TRUTH2[k][m0][m1])
    return (round(p0,12),round(p1,12),round(p2,12))


class CausalFeedbackPlanner(fixed_posterior.PosteriorCausalModel):
    """Exact two-action Bayesian branching on public consequences."""

    def __init__(self):
        super().__init__("posterior_planner")

    def choose(self,row):
        world.visible(row)
        spent=row["actions_taken"]
        if spent>=2:return None
        if spent==1:
            # Exactly the original shared policy with REAL observed outcome.
            return controls.plan(self,row)
        x=tuple(row["x"])
        goal=tuple(row["goal"])
        old_weights=self._weights()
        best=float(row["reward"])
        chosen=None
        # Same 12 legal original setbit actions in identical order. Repeated
        # no-ops share a predicted successor, hence compute each x1 only once.
        first_cache={}
        for action in world.ACTIONS:
            x1=world.setbit(x,action)
            k1=graph.x_key(x1)
            if k1 not in first_cache:
                expectation=0.
                for m,prob in _predict_joint(old_weights,k1).items():
                    if prob==0:continue
                    updated=_hypothetical_weights(self,k1,m)
                    # Model's anticipated stopping reward after this REAL first
                    # action is known GIVEN this hypothetical public mediator.
                    conditional=world.reward(m,goal,1)
                    # All 12 legal second do-actions. Same x2 successor can
                    # occur via multiple no-op do choices, so deduplicate.
                    second_keys={graph.x_key(world.setbit(x1,second))
                                 for second in world.ACTIONS}
                    for k2 in second_keys:
                        value=controls.expected(_forecast(updated,k2),goal,2)
                        if value>conditional:
                            conditional=value
                    expectation+=prob*conditional
                first_cache[k1]=expectation
            value=first_cache[k1]
            if value>best+TIE_EPS:
                chosen,best=action,value
        return chosen

    def state(self):
        return {"type":"aai11i.outcome-conditioned-causal.v1",
                "arm":ARM,
                "rows":[[list(x),list(m)] for x,m in self.rows]}


def checkpoint(model):
    if type(model) is not CausalFeedbackPlanner:
        raise TypeError("incorrect outcome-conditioned causal model type")
    return controls.canonical(model.state())


def restore(payload):
    if type(payload) is not str:
        raise ValueError("invalid model source payload")
    d=json.loads(payload)
    if (controls.canonical(d)!=payload or type(d) is not dict or
        set(d)!={"type","arm","rows"} or
        d["type"]!="aai11i.outcome-conditioned-causal.v1" or
        d["arm"]!=ARM or type(d["rows"]) is not list or
        len(d["rows"])>8):
        raise ValueError("unfrozen outcome-conditioned public checkpoint")
    model=CausalFeedbackPlanner()
    for item in d["rows"]:
        if type(item) is not list or len(item)!=2:
            raise ValueError("nonpublic structural checkpoint row")
        model._append((world.bits(item[0],6),world.bits(item[1],3)))
    if checkpoint(model)!=payload:
        raise ValueError("cold checkpoint not stable")
    return model
