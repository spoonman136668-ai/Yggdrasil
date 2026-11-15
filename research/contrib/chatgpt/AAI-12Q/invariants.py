"""AAI-12Q: causal intervention-effect invariants, not next-token learning.

The only new mechanism: infer a four-component structural causal program
from ACTUAL observed do-response constraints as well as pointwise public
mediator observations. Identical-state ablation has exact same public rows
and grammar, without the transition invariance constraint. Neither imports
the hidden causal generator, oracle or labels.
"""
from __future__ import annotations
import json
import math
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"AAI-12P"))
import world,controls

CANDIDATE="interventional_invariant_recent8"
ABLATION="pointwise_equal_public8"
ARMS=(ABLATION,CANDIDATE)
EFFECT_WEIGHT=2
MAX_PUBLIC_EVENTS=8


def public_do_pairs(rows):
    """Identify adjacent real interventions using ONLY visible public fields."""
    pairs=[]
    for before,after in zip(rows,rows[1:]):
        x0,m0=world.visible(before)
        x1,m1=world.visible(after)
        if (after["actions_taken"]!=before["actions_taken"]+1 or
            before["goal"]!=after["goal"] or
            sum(a!=b for a,b in zip(x0,x1))>1):
            continue
        pairs.append(((*x0,*m0),(*x1,*m1),m0,m1))
    return tuple(pairs)


def contrastive_rule_indices(rows,with_effects):
    if type(with_effects) is not bool or len(rows)>MAX_PUBLIC_EVENTS:
        raise ValueError("unregistered causal update or oversized public state")
    samples=[world.visible(row) for row in rows]
    transitions=public_do_pairs(rows) if with_effects else ()
    chosen=[]
    for out,grammar in enumerate(controls.GRAMMARS):
        best=(float("inf"),None)
        for i,rule in enumerate(grammar):
            point_errors=sum(int(controls._rule(rule,(*x,*m))!=m[out])
                             for x,m in samples)
            delta_errors=0
            for old,new,m0,m1 in transitions:
                predicted_delta=controls._rule(rule,old)^controls._rule(rule,new)
                actual_delta=m0[out]^m1[out]
                delta_errors+=int(predicted_delta!=actual_delta)
            score=point_errors+EFFECT_WEIGHT*delta_errors
            if (score,i)<best:
                best=(score,i)
        chosen.append(best[1])
    return tuple(chosen)


class CausalInvariantModel(controls.Control):
    """Four factored learned causal mechanisms, limited to 8 public events."""

    def __init__(self,arm):
        if arm not in ARMS:
            raise ValueError("unregistered causal invariant arm")
        self.arm=arm
        self.events=[]
        super().__init__("causal_structure_recent8")

    def observe(self,row):
        world.visible(row)
        clean=world.copy_public(row)
        super().observe(clean)
        self.events.append(clean)
        if len(self.events)>MAX_PUBLIC_EVENTS:
            self.events=self.events[-MAX_PUBLIC_EVENTS:]
        if len(self.events)!=len(self.rows):
            raise AssertionError("extra causal learner history beyond public comparator")

    def _structure(self,x):
        if self._best_rules is None:
            self._best_rules=contrastive_rule_indices(
                self.events,self.arm==CANDIDATE)
        return super()._structure(x)

    def state(self):
        # No hidden causal law, private supervision, derived MAP rule or cache.
        return {"type":"aai12q.public-effect-invariant.v1",
                "arm":self.arm,
                "rows":[world.copy_public(row) for row in self.events]}


def checkpoint(model):
    if type(model) is not CausalInvariantModel:
        raise TypeError("wrong public causal model checkpoint")
    return controls.canonical(model.state())


def restore(arm,source):
    if arm not in ARMS or type(source) is not str:
        raise ValueError("wrong public causal invariant checkpoint")
    data=json.loads(source)
    if (type(data) is not dict or controls.canonical(data)!=source or
        set(data)!={"type","arm","rows"} or
        data["type"]!="aai12q.public-effect-invariant.v1" or
        data["arm"]!=arm or type(data["rows"]) is not list or
        len(data["rows"])>MAX_PUBLIC_EVENTS):
        raise ValueError("noncanonical or privately modified public checkpoint")
    model=CausalInvariantModel(arm)
    for row in data["rows"]:
        model.observe(row)
    if checkpoint(model)!=source:
        raise ValueError("cold public causal state corrupted on restoration")
    return model
