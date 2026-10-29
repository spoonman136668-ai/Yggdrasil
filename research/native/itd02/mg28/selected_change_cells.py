"""MG28 native local-cell selected-public next-change learning.

Only selected original mission, direction and image; parent MG23 unchanged.
Predicts on-policy source-public change, not causal success or hidden goals.
"""
from __future__ import annotations
import hashlib
import json
from research.native.itd02.r10.public_adapter import canonical,digest
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter,original_public
from research.native.itd02.mg23.selected_target_cells import TargetCreditCells,observed_key

SCHEMA="yggdrasil.itd02.mg28.original-selected-public-next-change.v1"
MAX_CONTEXTS=4096
MAX_SAMPLES=4096
MAX_CHECKPOINT=6500000

def empty():
    return [{"count":0,"changed":0} for _ in range(7)]

class SelectedChangeCells:
    def __init__(self,parent=None,enabled=True):
        self.parent=TargetCreditCells() if parent is None else parent
        if type(self.parent) is not TargetCreditCells or type(enabled) is not bool:
            raise ValueError("MG28_WRONG_NATIVE_PARENT_OR_ABLATION")
        self.cells={}
        self.enabled=enabled

    @property
    def samples(self):
        return self.parent.samples

    def _valid(self):
        if (type(self.cells) is not dict or len(self.cells)>MAX_CONTEXTS
            or self.samples>MAX_SAMPLES or type(self.enabled) is not bool):
            raise ValueError("MG28_NATIVE_LOCAL_BOUNDS")
        total=0
        for k,row in self.cells.items():
            if (type(k) is not str or len(k)!=64 or
                any(c not in "0123456789abcdef" for c in k) or
                type(row) is not list or len(row)!=7):
                raise ValueError("MG28_LOCAL_CONTEXT")
            for stat in row:
                if (type(stat) is not dict or set(stat)!={"count","changed"} or
                    type(stat["count"]) is not int or type(stat["changed"]) is not int or
                    not 0<=stat["changed"]<=stat["count"]):
                    raise ValueError("MG28_LOCAL_EVENT_COUNT")
                total+=stat["count"]
        if total!=self.samples:
            raise ValueError("MG28_PARENT_SOURCE_COUNT_DRIFT")
        self.parent._valid()

    def start_session(self,adapter,name,live=False):
        self._valid()
        if type(adapter) is not OriginalMissionAdapter:
            raise ValueError("MG28_NOT_ORIGINAL_ADAPTER")
        self.parent.start_session(adapter,name,live=live)

    def choose(self,before):
        self._valid()
        key=observed_key(before)
        base=self.parent.choose(before)
        if (type(base) is not dict or type(base.get("action")) is not int
            or base["action"] not in range(7) or base.get("external_fallback") is not False):
            raise ValueError("MG28_MISSING_SOURCE_NATIVE_DECISION")
        if not self.enabled:
            return base
        row=self.cells.get(key,empty())
        stat=row[base["action"]]
        prior=10000*(stat["changed"]+1)//(stat["count"]+2)
        best=None
        high=0
        for action,item in enumerate(row):
            if item["count"]<3:
                continue
            score=10000*(item["changed"]+1)//(item["count"]+2)
            if score>=7500 and score>=prior+1000 and score>high:
                best=action
                high=score
        if best is None or best==base["action"]:
            return base
        return {"schema":SCHEMA,"action":best,
                "status":"MG28_LOCAL_OWN_SELECTED_REAL_NEXT_PUBLIC_CHANGE",
                "external_fallback":False}

    def learn_selected(self,adapter,before,after):
        self._valid()
        original_public(before)
        original_public(after)
        if (type(adapter) is not OriginalMissionAdapter or
            not adapter.ledger or adapter.pending is not None or
            adapter.current!=after or before["mission"]!=after["mission"]):
            raise ValueError("MG28_UNSELECTED_OR_MISMATCHED_PUBLIC_SOURCE")
        latest=adapter.ledger[-1]
        key=observed_key(before)
        if (latest["before_sha"]!=digest(before) or latest["after_sha"]!=digest(after)
            or type(latest["action"]) is not int or latest["action"] not in range(7)
            or latest["mission"]!=before["mission"]):
            raise ValueError("MG28_NOT_ONE_ACTUAL_SELECTED_ORIGINAL_SOURCE")
        if self.samples>=MAX_SAMPLES or (key not in self.cells and len(self.cells)>=MAX_CONTEXTS):
            raise ValueError("MG28_SOURCE_COUNT_OR_CONTEXT_BOUND")
        prior=self.samples
        receipt=self.parent.learn_selected(adapter,before,after)
        if self.samples!=prior+1:
            raise ValueError("MG28_PARENT_FEEDBACK_NOT_CONSERVED")
        row=self.cells.setdefault(key,empty())
        stat=row[latest["action"]]
        stat["count"]+=1
        if digest(before)!=digest(after):
            stat["changed"]+=1
        self._valid()
        return receipt

    def checkpoint(self):
        self._valid()
        source={"schema":SCHEMA,"parent":self.parent.checkpoint().decode("utf-8"),
                "cells":self.cells,"enabled":self.enabled}
        raw=canonical({"state":source,"sha256":hashlib.sha256(canonical(source)).hexdigest()})
        if len(raw)>MAX_CHECKPOINT:
            raise ValueError("MG28_LOCAL_CHECKPOINT_CAP")
        return raw

    @classmethod
    def restore(cls,blob):
        try:
            if type(blob) is not bytes or not 0<len(blob)<=MAX_CHECKPOINT:
                raise ValueError("MG28_RESTORE_SIZE")
            record=json.loads(blob)
            if type(record) is not dict or set(record)!={"state","sha256"}:
                raise ValueError("MG28_RESTORE_WIRE")
            state=record["state"]
            if (type(state) is not dict or
                set(state)!={"schema","parent","cells","enabled"} or
                state["schema"]!=SCHEMA or type(state["parent"]) is not str or
                hashlib.sha256(canonical(state)).hexdigest()!=record["sha256"]):
                raise ValueError("MG28_RESTORE_CHECKSUM")
            parent=TargetCreditCells.restore(state["parent"].encode("utf-8"))
            obj=cls(parent,enabled=state["enabled"])
            obj.cells=state["cells"]
            obj._valid()
            if obj.checkpoint()!=blob:
                raise ValueError("MG28_RESTORE_NOT_CANONICAL")
            return obj
        except (ValueError,TypeError,KeyError,UnicodeError,AttributeError) as e:
            raise ValueError("MG28_UNTRUSTED_NATIVE_SELECTED_MEMORY") from e
