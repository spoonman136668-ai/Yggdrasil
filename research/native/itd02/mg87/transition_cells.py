"""MG87 source-selected native local action-consequence cells, DEV only.

No action-name semantics, maze code, map, position, tile meanings, goals,
handwritten policy trace, privileged simulator state, or hidden rewards.
All learning is from actually executed public obs/action/next/reward.
The conventional TD and selected-count ablations share the exact input.
"""
from __future__ import annotations
import hashlib
import json
from research.native.itd02.mg19.original_mission_cells import (
    OriginalMissionAdapter, original_public)
from research.native.itd02.r10.public_adapter import canonical, digest

SCHEMA="yggdrasil.itd02.mg87.local-public-transition-cells.v1"
MODES=("local","td","count")
MAX_STATES=5000
MAX_SAMPLES=12000
MAX_BYTES=12000000
MAX_SUCCESSORS=128
ACTIONS=7
DISCOUNT=900
DIVISOR=1000

def _empty():
    return [{"count":0,"next":{},"q":0} for _ in range(ACTIONS)]

def _hash(s):
    return type(s) is str and len(s)==64 and all(c in "0123456789abcdef" for c in s)

class PublicTransitionCells:
    def __init__(self, mode="local"):
        if type(mode) is not str or mode not in MODES:
            raise ValueError("MG87_MODE_NOT_PREREGISTERED")
        self.mode=mode
        self.cells={}
        self.samples=0

    def _valid(self):
        if (type(self.mode) is not str or self.mode not in MODES
            or type(self.samples) is not int
            or not 0<=self.samples<=MAX_SAMPLES
            or type(self.cells) is not dict or len(self.cells)>MAX_STATES):
            raise ValueError("MG87_NATIVE_CELL_BOUNDS")
        total=0
        for ident,row in self.cells.items():
            if not _hash(ident) or type(row) is not list or len(row)!=ACTIONS:
                raise ValueError("MG87_CELL_IDENTITY")
            for action in row:
                if (type(action) is not dict or set(action)!={"count","next","q"}
                    or type(action["count"]) is not int
                    or not 0<=action["count"]<=MAX_SAMPLES
                    or type(action["q"]) is not int
                    or not 0<=action["q"]<=1000
                    or type(action["next"]) is not dict
                    or len(action["next"])>MAX_SUCCESSORS):
                    raise ValueError("MG87_NATIVE_LOCAL_ACTION_BOUNDS")
                if any(not _hash(k) or type(v) is not int or v<=0
                       for k,v in action["next"].items()):
                    raise ValueError("MG87_SELECTED_SUCCESSOR_BAD")
                if sum(action["next"].values())!=action["count"]:
                    raise ValueError("MG87_SELECTED_TRANSITION_CONSERVATION")
                total+=action["count"]
        if total!=self.samples:
            raise ValueError("MG87_CUMULATIVE_SELECTED_SAMPLES_BAD")

    def start_session(self,adapter,name,live=False):
        if type(adapter) is not OriginalMissionAdapter:
            raise ValueError("MG87_ORIGINAL_PUBLIC_ADAPTER_REQUIRED")
        if type(live) is not bool or live:
            raise ValueError("MG87_NO_LIVE_OR_UNVERIFIED_CONTEXT")
        original_public(adapter.current)
        if self.samples>MAX_SAMPLES or len(self.cells)>MAX_STATES:
            raise ValueError("MG87_NATIVE_CELL_CAP")

    def choose(self,before):
        original_public(before)
        ident=digest(before)
        rows=self.cells.get(ident,_empty())
        if self.mode=="count":
            action=min(range(ACTIONS),key=lambda a:(rows[a]["count"],a))
        elif self.mode=="td":
            # Fixed conventional tabular TD, same observed source inputs.
            action=max(range(ACTIONS),key=lambda a:(
                rows[a]["q"]+300//(rows[a]["count"]+1),-a))
        else:
            # Each cell is a local, online learned source-conditioned effect
            # memory; optimistic exploration uses distinct *observed* next
            # states, not absolute map coordinates or semantic goals.
            action=max(range(ACTIONS),key=lambda a:(
                300//(1+rows[a]["count"])
                +100*(1+len(rows[a]["next"]))//(2+rows[a]["count"])
                +250*rows[a]["q"]//1000,-a))
        return {"schema":SCHEMA,"action":action,
                "status":{"local":"MG87_LOCAL_SOURCE_SUCCESSOR",
                          "td":"MG87_TABULAR_PUBLIC_TD",
                          "count":"MG87_PUBLIC_COUNT_ABLATION"}[self.mode],
                "external_fallback":False}

    def learn_selected(self,adapter,before,after):
        original_public(before)
        original_public(after)
        if (type(adapter) is not OriginalMissionAdapter
            or adapter.pending is not None or adapter.current!=after
            or not adapter.ledger or before["mission"]!=after["mission"]):
            raise ValueError("MG87_UNSELECTED_PUBLIC_FEEDBACK")
        event=adapter.ledger[-1]
        if (type(event.get("action")) is not int
            or not 0<=event["action"]<ACTIONS
            or event["before_sha"]!=digest(before)
            or event["after_sha"]!=digest(after)):
            raise ValueError("MG87_ORIGINAL_SELECTED_LEDGER_MISMATCH")
        if (self.samples>=MAX_SAMPLES or
            len(self.cells)>=MAX_STATES and digest(before) not in self.cells):
            raise ValueError("MG87_RESEARCH_CAP")
        ident=event["before_sha"]
        nextident=event["after_sha"]
        row=self.cells.setdefault(ident,_empty())[event["action"]]
        if (nextident not in row["next"]
            and len(row["next"])>=MAX_SUCCESSORS):
            raise ValueError("MG87_SUCCESSOR_CAP")
        row["count"]+=1
        row["next"][nextident]=row["next"].get(nextident,0)+1
        self.samples+=1
        # Learn bounded nonnegative source-return TD from the returned
        # original reward. It is zero until the world actually pays reward.
        reward=event["reward"]
        if type(reward) not in (int,float) or not 0<=reward<=1:
            raise ValueError("MG87_UNTRUSTED_ORIGINAL_REWARD_RANGE")
        nextmax=max((r["q"] for r in self.cells.get(nextident,[])),default=0)
        target=min(1000,max(0,round(1000*reward)+DISCOUNT*nextmax//DIVISOR))
        row["q"]=min(1000,max(0,(3*row["q"]+target)//4))
        return {"selected_source":True,"samples":self.samples,
                "action":event["action"],"public_effect_memory":True}

    def checkpoint(self):
        self._valid()
        state={"schema":SCHEMA,"mode":self.mode,"samples":self.samples,
               "cells":self.cells}
        blob=canonical({"state":state,
                        "sha256":hashlib.sha256(canonical(state)).hexdigest()})
        if len(blob)>MAX_BYTES:
            raise ValueError("MG87_CHECKPOINT_CAP")
        return blob

    @classmethod
    def restore(cls,raw):
        try:
            if type(raw) is not bytes or not 0<len(raw)<=MAX_BYTES:
                raise ValueError("MG87_UNTRUSTED_BYTES")
            payload=json.loads(raw)
            if type(payload) is not dict or set(payload)!={"state","sha256"}:
                raise ValueError("MG87_CHECKPOINT_FORMAT")
            state=payload["state"]
            if (type(state) is not dict
                or set(state)!={"schema","mode","samples","cells"}
                or state["schema"]!=SCHEMA
                or type(state["mode"]) is not str
                or state["mode"] not in MODES
                or hashlib.sha256(canonical(state)).hexdigest()!=payload["sha256"]):
                raise ValueError("MG87_INVALID_DIGEST_OR_SCHEMA")
            obj=cls(state["mode"])
            obj.samples=state["samples"]
            obj.cells=state["cells"]
            obj._valid()
            if obj.checkpoint()!=raw:
                raise ValueError("MG87_NONCANONICAL_CHECKPOINT")
            return obj
        except (ValueError,TypeError,KeyError,UnicodeError,AttributeError) as exc:
            raise ValueError("MG87_UNTRUSTED_LOCAL_NATIVE_CHECKPOINT") from exc
