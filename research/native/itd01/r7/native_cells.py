"""Yggdrasil R7: native local-cell online predictive plasticity (source-free).

Four physical-like local cells per public context A/B. Each cell owns signed
fast correlation, its own slow consolidated trace and a bounded nearest-
neighbor message; there is no BPTT, GRU, shared Wingless weight routine,
scripted causal-role lookup or token-language predictor.

This is a small synthetic PUBLIC sensory outcome learning pilot. It is NOT
an authenticated independent H1/H2 cognitive transfer first use.
"""
from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, asdict

MASK=(1<<64)-1


@dataclass
class LocalCell:
    fast: int=0
    slow: float=0.0
    updates: int=0

    def feel(self, public_sensor: bool, public_label: bool):
        # LOCAL Hebbian predictive error: correlate local sensory activity
        # with a *completed public outcome*, not a hidden cause label.
        signed_sensor=1 if public_sensor else -1
        signed_label=1 if public_label else -1
        self.fast=max(-512,min(512,self.fast+signed_sensor*signed_label))
        # This cell alone consolidates its fast evidence; no global gradient.
        self.slow=0.985*self.slow+0.015*self.fast
        self.updates+=1

    def signal(self, sensory_bit: bool) -> float:
        return (1 if sensory_bit else -1)*(0.75*self.fast+0.25*self.slow)


class Colony:
    """Eight local cells, two externally observable public context colonies."""
    def __init__(self):
        self.cells={"A":[LocalCell() for _ in range(4)],
                    "B":[LocalCell() for _ in range(4)]}
        self.feedback_updates=0
        self.neighbor_messages=0

    def _validate(self,context,sensors):
        if context not in ("A","B") or type(sensors) not in (tuple,list) or len(sensors)!=4 or any(type(b) is not bool for b in sensors):
            raise ValueError("YGG_R7_PUBLIC_CONTEXT_OR_SENSOR_INVALID")

    def predict(self,context:str,sensors:tuple[bool,bool,bool,bool])->bool:
        self._validate(context,sensors)
        cells=self.cells[context]
        local=[cell.signal(sensors[i]) for i,cell in enumerate(cells)]
        # BOUNDED nearest-neighbor cell communication. The event topology is
        # a four-cell ring, not a centrally learned global recurrent model.
        feedback=0.0
        for i,own in enumerate(local):
            neighbors=(local[(i-1)%4]+local[(i+1)%4])/2.0
            feedback+=own+0.03*neighbors
        return feedback>0

    def learn_completed_public_feedback(self,context,sensors,public_outcome:bool,delay_steps:int):
        self._validate(context,sensors)
        if type(delay_steps) is not int or delay_steps<2:
            raise ValueError("YGG_R7_EARLY_PRIVATE_FEEDBACK_BLOCKED")
        if type(public_outcome) is not bool:
            raise ValueError("YGG_R7_PUBLIC_OUTCOME_NOT_BOOL")
        for i,cell in enumerate(self.cells[context]):
            cell.feel(sensors[i],public_outcome)
        self.feedback_updates+=1
        self.neighbor_messages+=8

    def checkpoint(self)->bytes:
        body={"schema":"ygg.native_local_cells.r7.v1",
              "cells":{key:[asdict(cell) for cell in self.cells[key]]
                       for key in ("A","B")},
              "feedback_updates":self.feedback_updates,
              "neighbor_messages":self.neighbor_messages}
        raw=json.dumps(body,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
        token=hashlib.sha256(raw).hexdigest()
        blob=json.dumps({"payload":body,"sha256":token},sort_keys=True,
                        separators=(",",":"),allow_nan=False).encode()
        if len(blob)>32768:
            raise ValueError("YGG_R7_MODEL_MEMORY_CAP_EXCEEDED")
        return blob

    @classmethod
    def restore(cls,raw:bytes)->"Colony":
        if type(raw) is not bytes or not (0<len(raw)<=32768):
            raise ValueError("YGG_R7_CHECKPOINT_SIZE_INVALID")
        block=json.loads(raw)
        if type(block) is not dict or set(block)!={"payload","sha256"}:
            raise ValueError("YGG_R7_STATE_FIELDS_INVALID")
        body=block["payload"]
        raw_body=json.dumps(body,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
        if hashlib.sha256(raw_body).hexdigest()!=block["sha256"]:
            raise ValueError("YGG_R7_STATE_HASH_INVALID")
        if body.get("schema")!="ygg.native_local_cells.r7.v1" or set(body["cells"])!={"A","B"}:
            raise ValueError("YGG_R7_CHECKPOINT_CONTEXT_INVALID")
        o=cls()
        for k in ("A","B"):
            if len(body["cells"][k])!=4:
                raise ValueError("YGG_R7_CELL_COUNT_INVALID")
            o.cells[k]=[]
            for v in body["cells"][k]:
                if set(v)!={"fast","slow","updates"} or not -512<=v["fast"]<=512 or v["updates"]<0:
                    raise ValueError("YGG_R7_CELL_PLASTICITY_INVALID")
                o.cells[k].append(LocalCell(**v))
        o.feedback_updates=body["feedback_updates"]
        o.neighbor_messages=body["neighbor_messages"]
        return o


class PublicDevGenerator:
    """Private DEV fixture only. Hidden rule never goes into a Colony."""
    def __init__(self,seed:int):
        self.state=(seed*0x9e3779b97f4a7c15+0xd1b54a32d192ed03)&MASK

    def next(self):
        self.state^=(self.state<<13)&MASK
        self.state^=self.state>>7
        self.state^=(self.state<<17)&MASK
        self.state&=MASK
        return self.state

    def example(self,context):
        readings=tuple(bool(self.next()&1) for _ in range(4))
        public_outcome=(readings[2] if context=="A" else not readings[1])
        if self.next()%10==0:
            public_outcome=not public_outcome
        return readings,public_outcome


def _examples(g,context,n):
    return [(context,*g.example(context)) for _ in range(n)]


def _score(agent,examples):
    if not examples:
        raise ValueError("EMPTY_EVALUATION")
    return sum(agent.predict(ctx,sensors)==outcome
               for ctx,sensors,outcome in examples)/len(examples)


def _majority_zero(examples):
    return sum(not y for _,_,y in examples)/len(examples)


def study(seed:int)->dict:
    g=PublicDevGenerator(seed+71)
    train_a=_examples(g,"A",320)
    valid_a=_examples(g,"A",160)
    train_b=_examples(g,"B",320)
    retained_a=_examples(g,"A",160)
    held_b=_examples(g,"B",160)
    cells=Colony()
    for context,sensors,outcome in train_a:
        cells.predict(context,sensors)
        cells.learn_completed_public_feedback(context,sensors,outcome,2)
    before=_score(cells,valid_a)
    for context,sensors,outcome in train_b:
        cells.predict(context,sensors)
        cells.learn_completed_public_feedback(context,sensors,outcome,2)
    snapshot=cells.checkpoint()
    restarted=Colony.restore(snapshot)
    retained=_score(restarted,retained_a)
    acquired=_score(restarted,held_b)
    sham=Colony()
    same=all(cells.predict(c,x)==restarted.predict(c,x)
             for c,x,_ in retained_a+held_b)
    return {
        "seed":seed,"a_before_b":before,"a_after_b":retained,
        "b_after_training":acquired,
        "sham_a":_score(sham,retained_a),
        "sham_b":_score(sham,held_b),
        "constant_a":_majority_zero(retained_a),
        "constant_b":_majority_zero(held_b),
        "delayed_public_feedback_updates":restarted.feedback_updates,
        "local_cell_updates":sum(v.updates for cells in restarted.cells.values() for v in cells),
        "neighbor_messages":restarted.neighbor_messages,
        "serialized_state_bytes":len(snapshot),
        "cold_restore_exact":same,
        "checkpoint_sha256":hashlib.sha256(snapshot).hexdigest(),
    }


def gates(scores:list[dict])->bool:
    if len(scores)!=3:
        return False
    if any(not z["cold_restore_exact"] or z["delayed_public_feedback_updates"]!=640
           or z["local_cell_updates"]!=2560 or z["serialized_state_bytes"]>32768
           or z["a_after_b"]<.75 or z["b_after_training"]<.75
           or z["a_before_b"]-z["a_after_b"]>.05+1e-9 for z in scores):
        return False
    for key,negative in (("a_after_b","sham_a"),("b_after_training","sham_b"),
                         ("a_after_b","constant_a"),("b_after_training","constant_b")):
        if sum(z[key]-z[negative] for z in scores)/len(scores)<.15:
            return False
    return True
