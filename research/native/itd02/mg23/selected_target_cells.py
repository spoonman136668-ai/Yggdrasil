"""MG23: native local-cell selected public target and delayed original reward credit.

Independent local implementation over the unchanged MG19/R20 native cells. This
is an opt-in source engineering candidate, never an external route oracle.
"""
from __future__ import annotations
import hashlib
import json
from research.native.itd02.r10.public_adapter import canonical,digest
from research.native.itd02.mg19.genuine_mission_cells import MissionCells
from research.native.itd02.mg19.original_mission_cells import (
    OriginalMissionAdapter,original_public
)

SCHEMA="yggdrasil.itd02.mg23.source-public-target-delayed-local-credit.v1"
WINDOW=32
MAX_SAMPLES=4096
MAX_CONTEXT=4096
MAX_CHECKPOINT=5500000
COLORS={"red":0,"green":1,"blue":2,"purple":3,"yellow":4,"grey":5}
OBJECTS={"key":5,"ball":6,"box":7}

def observed_key(public):
    original_public(public)
    pixel=public["image"][3][5]
    return digest({"mission":public["mission"],"direction":public["direction"],
                   "front":[pixel[0],pixel[1],pixel[2]]})

def empty():
    return [{"count":0,"target":0,"delayed":0} for _ in range(7)]

def observed_target(before,after,selected):
    if selected!=3 or before["direction"]!=after["direction"]:
        return False
    name=before["mission"]
    if not name.startswith("pick up the "):
        return False
    terms=name[len("pick up the "):].split(" ")
    if len(terms)!=2 or terms[0] not in COLORS or terms[1] not in OBJECTS:
        return False
    b=before["image"][3][5]
    n=after["image"][3][5]
    return b[0]==OBJECTS[terms[1]] and b[1]==COLORS[terms[0]] and n[0]==1

class TargetCreditCells:
    def __init__(self,parent=None):
        self.parent=MissionCells() if parent is None else parent
        if type(self.parent) is not MissionCells:
            raise ValueError("MG23_WRONG_LOCAL_NATIVE_PARENT")
        self.cells={}
        self.trace=[]

    @property
    def samples(self):
        return self.parent.samples

    def _valid(self):
        if (type(self.cells) is not dict or type(self.trace) is not list
            or len(self.cells)>MAX_CONTEXT or self.samples>MAX_SAMPLES
            or len(self.trace)>WINDOW):
            raise ValueError("MG23_LOCAL_SELECTED_SOURCE_BOUNDS")
        total=0
        for key,row in self.cells.items():
            if (type(key) is not str or len(key)!=64 or
                any(ch not in "0123456789abcdef" for ch in key) or
                type(row) is not list or len(row)!=7):
                raise ValueError("MG23_SOURCE_CONTEXT_CORRUPT")
            for stat in row:
                if (type(stat) is not dict or set(stat)!={"count","target","delayed"} or
                    any(type(stat[k]) is not int or stat[k]<0 for k in stat) or
                    stat["target"]>stat["count"]):
                    raise ValueError("MG23_UNTRUSTED_LOCAL_SELECTED_CREDIT")
                total+=stat["count"]
        if total!=self.samples:
            raise ValueError("MG23_PARENT_AND_LOCAL_SOURCE_COUNT_DIFFER")
        for item in self.trace:
            if (type(item) is not dict or set(item)!={"context","action"} or
                item["context"] not in self.cells or
                type(item["action"]) is not int or item["action"] not in range(7)):
                raise ValueError("MG23_BAD_DELAYED_SOURCE_ELIGIBILITY")
        self.parent._valid()

    def start_session(self,adapter,name,live=False):
        self._valid()
        if type(adapter) is not OriginalMissionAdapter:
            raise ValueError("MG23_ORIGINAL_MISSION_ADAPTER_REQUIRED")
        self.parent.start_session(adapter,name,live=live)
        self.trace=[]

    def choose(self,before):
        self._valid()
        key=observed_key(before)
        base=self.parent.choose(before)
        if (type(base) is not dict or
            type(base.get("action")) is not int or base["action"] not in range(7) or
            base.get("external_fallback") is not False):
            raise ValueError("MG23_PARENT_NATIVE_SOURCE_MISSING")
        current=base["action"]
        best=current
        high=0
        for selected,stat in enumerate(self.cells.get(key,empty())):
            if not stat["count"]:
                continue
            score=8*stat["target"]+stat["delayed"]
            if score>high:
                high=score
                best=selected
        if high>0:
            return {"schema":SCHEMA,"action":best,
                    "status":"MG23_LOCAL_OWN_SELECTED_PUBLIC_TARGET_OR_TERMINAL_CREDIT",
                    "external_fallback":False}
        return base

    def learn_selected(self,adapter,before,after):
        self._valid()
        original_public(before)
        original_public(after)
        if (type(adapter) is not OriginalMissionAdapter or
            not adapter.ledger or adapter.pending is not None or
            adapter.current!=after or before["mission"]!=after["mission"]):
            raise ValueError("MG23_NOT_ONE_ORIGINAL_SELECTED_EFFECT")
        latest=adapter.ledger[-1]
        key=observed_key(before)
        if (latest["before_sha"]!=digest(before) or
            latest["after_sha"]!=digest(after) or
            type(latest["action"]) is not int or latest["action"] not in range(7) or
            latest["mission"]!=before["mission"]):
            raise ValueError("MG23_SOURCE_ACTION_OR_MISSION_NOT_SELECTED")
        if (self.samples>=MAX_SAMPLES or
            key not in self.cells and len(self.cells)>=MAX_CONTEXT):
            raise ValueError("MG23_LOCAL_NATIVE_SOURCE_CAPACITY")
        preceding=self.samples
        receipt=self.parent.learn_selected(adapter,before,after)
        if self.samples!=preceding+1:
            raise ValueError("MG23_INHERITED_ORIGINAL_SAMPLE_COUNT")
        row=self.cells.setdefault(key,empty())
        statistic=row[latest["action"]]
        statistic["count"]+=1
        if observed_target(before,after,latest["action"]):
            statistic["target"]+=1
        self.trace.append({"context":key,"action":latest["action"]})
        if len(self.trace)>WINDOW:
            self.trace=self.trace[-WINDOW:]
        if latest["terminal"] and latest["reward"]>0:
            for age,item in enumerate(reversed(self.trace)):
                cell=self.cells[item["context"]][item["action"]]
                cell["delayed"]+=WINDOW-age
        self._valid()
        return receipt

    def checkpoint(self):
        self._valid()
        state={"schema":SCHEMA,
               "parent":self.parent.checkpoint().decode("utf-8"),
               "cells":self.cells,"trace":self.trace}
        raw=canonical({"state":state,"sha256":hashlib.sha256(canonical(state)).hexdigest()})
        if len(raw)>MAX_CHECKPOINT:
            raise ValueError("MG23_LOCAL_CHECKPOINT_TOO_LARGE")
        return raw

    @classmethod
    def restore(cls,raw):
        try:
            if type(raw) is not bytes or not 0<len(raw)<=MAX_CHECKPOINT:
                raise ValueError("MG23_COLD_SOURCE_SIZE")
            data=json.loads(raw)
            if type(data) is not dict or set(data)!={"state","sha256"}:
                raise ValueError("MG23_COLD_SOURCE_FIELDS")
            state=data["state"]
            if (type(state) is not dict or
                set(state)!={"schema","parent","cells","trace"} or
                state["schema"]!=SCHEMA or type(state["parent"]) is not str or
                hashlib.sha256(canonical(state)).hexdigest()!=data["sha256"]):
                raise ValueError("MG23_COLD_SOURCE_DIGEST")
            native=cls(MissionCells.restore(state["parent"].encode("utf-8")))
            native.cells=state["cells"]
            native.trace=state["trace"]
            native._valid()
            if native.checkpoint()!=raw:
                raise ValueError("MG23_NONCANONICAL_LOCAL_NATIVE_SOURCE")
            return native
        except (ValueError,TypeError,KeyError,UnicodeError,AttributeError) as exc:
            raise ValueError("MG23_CORRUPT_LOCAL_SELECTED_CREDIT") from exc
