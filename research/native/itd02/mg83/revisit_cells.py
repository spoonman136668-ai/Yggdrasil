"""MG83 native source-public repeated-consequence guard on frozen MG82.

Retains actually selected next-public SHA-256 outcomes only. Repetition is not
causal understanding. The unchanged parent chooses actions in all other cases.
"""
from __future__ import annotations
import hashlib
import json
from research.native.itd02.mg82.effect_cells import PublicEffectCells
from research.native.itd02.mg23.selected_target_cells import observed_key
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter, original_public
from research.native.itd02.r10.public_adapter import canonical,digest

SCHEMA="yggdrasil.itd02.mg83.revisited-public-successor.v1"
MAX_CONTEXTS=4096
MAX_SAMPLES=4096
MAX_CHECKPOINT=12500000
MIN_REPEAT=2

def blank():
    return [{"count":0,"successors":{}} for _ in range(7)]

def valid_hash(h):
    return type(h) is str and len(h)==64 and all(c in "0123456789abcdef" for c in h)

class RevisitGuard:
    def __init__(self, parent=None):
        self.parent=PublicEffectCells(mode="effect") if parent is None else parent
        if type(self.parent) is not PublicEffectCells or self.parent.mode!="effect":
            raise ValueError("MG83_FROZEN_EFFECT_PARENT_REQUIRED")
        self.cells={}

    @property
    def samples(self):
        return self.parent.samples

    def _valid(self):
        self.parent._valid()
        if type(self.cells) is not dict or len(self.cells)>MAX_CONTEXTS or self.samples>MAX_SAMPLES:
            raise ValueError("MG83_CONTEXT_BOUNDS")
        total=0
        for key,row in self.cells.items():
            if not valid_hash(key) or type(row) is not list or len(row)!=7:
                raise ValueError("MG83_CONTEXT_KEY")
            for entry in row:
                if (type(entry) is not dict or set(entry)!={"count","successors"}
                    or type(entry["count"]) is not int or not 0<=entry["count"]<=MAX_SAMPLES
                    or type(entry["successors"]) is not dict):
                    raise ValueError("MG83_CONTEXT_ROW")
                if (any(not valid_hash(d) or type(v) is not int or v<=0
                        for d,v in entry["successors"].items())
                    or sum(entry["successors"].values())!=entry["count"]):
                    raise ValueError("MG83_SELECTED_SUCCESSOR_CUSTODY")
                total+=entry["count"]
        if total!=self.samples:
            raise ValueError("MG83_SELECTED_SAMPLE_NOT_CONSERVED")

    def start_session(self,adapter,name,live=False):
        self._valid()
        if type(adapter) is not OriginalMissionAdapter:
            raise ValueError("MG83_NOT_ORIGINAL_MISSION_ADAPTER")
        return self.parent.start_session(adapter,name,live=live)

    def choose(self,before):
        self._valid()
        original_public(before)
        base=self.parent.choose(before)
        if (type(base) is not dict or type(base.get("action")) is not int
            or base["action"] not in range(7) or base.get("external_fallback") is not False):
            raise ValueError("MG83_PARENT_NOT_NATIVE_SELECTED")
        row=self.cells.get(observed_key(before))
        if row is None:
            return base
        selected=base["action"]
        evidence=row[selected]
        if (evidence["count"]<MIN_REPEAT
            or max(evidence["successors"].values(),default=0)<MIN_REPEAT):
            return base
        # Conservative untried-effect probe after an action has returned the
        # same successor twice. No counterfactual or semantic goal knowledge.
        alternate=min((a for a in range(7) if a!=selected),
                      key=lambda a:(row[a]["count"],a))
        if row[alternate]["count"]>=evidence["count"]:
            return base
        return {"schema":SCHEMA,"action":alternate,
                "status":"MG83_REVISITED_ORIGINAL_PUBLIC_CONSEQUENCE_ESCAPE",
                "external_fallback":False}

    def learn_selected(self,adapter,before,after):
        self._valid()
        original_public(before)
        original_public(after)
        if (type(adapter) is not OriginalMissionAdapter
            or not adapter.ledger or adapter.pending is not None
            or adapter.current!=after or before["mission"]!=after["mission"]):
            raise ValueError("MG83_NOT_COMPLETED_SELECTED_ORIGINAL_SOURCE")
        last=adapter.ledger[-1]
        if (type(last.get("action")) is not int or last["action"] not in range(7)
            or last["before_sha"]!=digest(before) or last["after_sha"]!=digest(after)
            or last["mission"]!=before["mission"]):
            raise ValueError("MG83_ORIGINAL_PUBLIC_LEDGER_DRIFT")
        key=observed_key(before)
        if self.samples>=MAX_SAMPLES or (key not in self.cells and len(self.cells)>=MAX_CONTEXTS):
            raise ValueError("MG83_SOURCE_CAP")
        n=self.samples
        receipt=self.parent.learn_selected(adapter,before,after)
        if self.samples!=n+1:
            raise ValueError("MG83_PARENT_FEEDBACK_NOT_CONSERVED")
        cell=self.cells.setdefault(key,blank())[last["action"]]
        cell["count"]+=1
        target=last["after_sha"]
        cell["successors"][target]=cell["successors"].get(target,0)+1
        self._valid()
        return receipt

    def checkpoint(self):
        self._valid()
        state={"schema":SCHEMA,"parent":self.parent.checkpoint().decode("utf-8"),
               "cells":self.cells}
        payload=canonical({"state":state,"sha256":hashlib.sha256(canonical(state)).hexdigest()})
        if len(payload)>MAX_CHECKPOINT:
            raise ValueError("MG83_CHECKPOINT_CAP")
        return payload

    @classmethod
    def restore(cls,raw):
        try:
            if type(raw) is not bytes or not 0<len(raw)<=MAX_CHECKPOINT:
                raise ValueError("MG83_CHECKPOINT_SIZE")
            wire=json.loads(raw)
            if type(wire) is not dict or set(wire)!={"state","sha256"}:
                raise ValueError("MG83_CHECKPOINT_ENVELOPE")
            state=wire["state"]
            if (type(state) is not dict or set(state)!={"schema","parent","cells"}
                or state["schema"]!=SCHEMA or type(state["parent"]) is not str
                or hashlib.sha256(canonical(state)).hexdigest()!=wire["sha256"]):
                raise ValueError("MG83_CHECKPOINT_DIGEST")
            result=cls(PublicEffectCells.restore(state["parent"].encode("utf-8")))
            result.cells=state["cells"]
            result._valid()
            if result.checkpoint()!=raw:
                raise ValueError("MG83_NONCANONICAL_CHECKPOINT")
            return result
        except (ValueError,TypeError,KeyError,UnicodeError,AttributeError) as exc:
            raise ValueError("MG83_UNTRUSTED_CHECKPOINT") from exc
