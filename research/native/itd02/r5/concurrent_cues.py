"""Yggdrasil R5: concurrent real-cue episodic bindings with source-owned R4 cells.

Adds no rule-based hidden success labels or map. R4 reward-conditioned cell
weights are trained on real physical original MemoryEnv consequences. Eight
separate opaque task slots hold early sensory cues for later late decisions.
A conventional Python dictionary is the primary strong matched control.
"""
import hashlib
import json
from research.native.itd02.r4.cue_cells import CueCells,canon,TOKENS

SCHEMA="yggdrasil.itd02.r5.concurrent-episodic-cue-binding.v1"
MAX_SLOTS=8
class ConcurrentCueMemory:
    def __init__(self):
        self.cell=CueCells()
        self.slots={}
        self.training_events=0

    def fit(self,cue,selected,reward,terminal):
        if self.slots:raise ValueError("R5_FIT_WHILE_EPISODIC_SLOTS_ACTIVE")
        self.cell.begin(cue)
        self.cell.observe(selected,reward,terminal)
        self.training_events+=1

    def present(self,slot,cue):
        if type(slot)is not int or not 0<=slot<MAX_SLOTS:
            raise ValueError("R5_INVALID_OPAQUE_TASK_SLOT")
        if cue not in TOKENS:raise ValueError("R5_INVALID_EARLY_PUBLIC_CUE")
        if slot in self.slots or len(self.slots)>=MAX_SLOTS:
            raise ValueError("R5_DUPLICATE_OR_OVER_CAPACITY")
        self.slots[slot]=cue

    def choose(self,slot,top,bottom):
        if type(slot)is not int or slot not in self.slots:
            raise ValueError("R5_EPISODIC_CUE_NOT_RETAINED")
        prior=self.cell.cue
        try:
            self.cell.begin(self.slots[slot])
            return self.cell.choose(top,bottom)
        finally:
            self.cell.cue=prior

    def release(self,slot):
        if slot not in self.slots:raise ValueError("R5_UNBOUND_RELEASE")
        del self.slots[slot]

    def snapshot(self):
        if (type(self.training_events)is not int or
            not 0<=self.training_events<=2**52 or
            self.cell.outcomes!=self.training_events or
            len(self.slots)>MAX_SLOTS or
            any(type(k)is not int or not 0<=k<MAX_SLOTS or c not in TOKENS
                for k,c in self.slots.items())):
            raise ValueError("R5_MEMORY_STATE_INVALID")
        data={"schema":SCHEMA,"r4":self.cell.snapshot().decode("utf8"),
              "slots":{str(k):v for k,v in sorted(self.slots.items())},
              "training_events":self.training_events}
        raw=canon(data)
        if len(raw)>16384:raise ValueError("R5_MEMORY_CAPACITY_EXCEEDED")
        return canon({"data":data,"sha256":hashlib.sha256(raw).hexdigest()})

    @classmethod
    def restore(cls,raw):
        if type(raw)is not bytes or not 0<len(raw)<=16384:
            raise ValueError("R5_CHECKPOINT_SIZE_INVALID")
        try:
            env=json.loads(raw)
            if set(env)!={"data","sha256"}:raise ValueError("R5_AUTH_ENVELOPE")
            d=env["data"]
            if (set(d)!={"schema","r4","slots","training_events"} or
                d["schema"]!=SCHEMA or
                hashlib.sha256(canon(d)).hexdigest()!=env["sha256"]):
                raise ValueError("R5_AUTH_CHECKPOINT")
            p=cls()
            p.cell=CueCells.restore(d["r4"].encode("utf8"))
            if type(d["training_events"])is not int or d["training_events"]!=p.cell.outcomes:
                raise ValueError("R5_TRAINING_EVIDENCE_DRIFT")
            if type(d["slots"])is not dict or len(d["slots"])>MAX_SLOTS:
                raise ValueError("R5_SLOTS_INVALID")
            for k,v in d["slots"].items():
                if not k.isascii() or not k.isdigit() or str(int(k))!=k:
                    raise ValueError("R5_NONCANONICAL_SLOT")
                p.present(int(k),v)
            p.training_events=d["training_events"]
            return p
        except (KeyError,TypeError,OverflowError,ValueError) as exc:
            raise ValueError("R5_ORIGINAL_CHECKPOINT_AUTHENTICATION_FAILED") from exc
