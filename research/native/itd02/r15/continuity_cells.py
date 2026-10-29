"""R15: opt-in source-public object-continuity learning for native local cells.

No evaluator-provided DoorKey stage, route, hidden pose, or unselected source.
R11 remains authoritative for source-selected consequences and checkpoints.
"""
from __future__ import annotations
import hashlib
import json

from research.native.itd02.r10.public_adapter import (
    DoorKeyPublicAdapter, canonical, digest, public_observation
)
from research.native.itd02.r11.affordance_cells import PublicAffordanceCells
from research.native.itd02.r14.temporal_cells import TemporalCells

SCHEMA="yggdrasil.itd02.r15.public-object-continuity.v1"
MAX_SAMPLES=4096
MAX_CONTEXTS=128
MAX_CHECKPOINT=600000
ACTIONS=tuple(range(7))

def carrying(image):
    return image[3][6][0] in (5,6,7)

def feature(obs):
    frame=public_observation(obs)
    return str(frame["image"][3][5][0])+":"+str(int(carrying(frame["image"])))

def empty_stat():
    return {"count":0,"changed":0,"retained_changed":0,"lost":0,"gained":0}

class NativeContinuity:
    def __init__(self, local=None):
        self.local=PublicAffordanceCells() if local is None else local
        if type(self.local) is not PublicAffordanceCells:
            raise ValueError("R15_UNTRUSTED_NATIVE_CELLS")
        self.temporal=TemporalCells()
        self.memory={}
        self.samples=self.local.samples
        self.live=False

    def start_session(self, adapter, name, live=False):
        if type(live) is not bool:
            raise ValueError("R15_SESSION_MODE")
        self.local.start_session(adapter,name)
        self.temporal=TemporalCells()
        self.live=live

    def _healthy(self):
        if (self.local.samples!=self.samples or not 0<=self.samples<=MAX_SAMPLES
            or len(self.memory)>MAX_CONTEXTS):
            raise ValueError("R15_SELECTED_COUNTS_DRIFT")

    def choose(self, before):
        self._healthy()
        frame=public_observation(before)
        if self.local.session is None:
            raise ValueError("R15_SOURCE_SESSION_MISSING")
        ctx=feature(frame)
        bins=self.memory.get(ctx,{})
        is_held=carrying(frame["image"])
        best=None
        best_score=0
        for action in ACTIONS:
            cell=bins.get(str(action))
            if not cell:continue
            n=cell["count"]
            score=(6*cell["retained_changed"]+2*cell["changed"]-8*cell["lost"]
                   if is_held else 6*cell["gained"]+2*cell["changed"])
            normalized=(score*1024)//n
            if normalized>best_score:
                best_score=normalized;best=action
        if best is not None:
            return {"schema":SCHEMA,"action":best,
                    "status":"SELECT_NATIVE_LEARNED_PUBLIC_OBJECT_CONTINUITY",
                    "external_fallback":False}
        # No external collector and no manually supplied stage objective.
        counts=[bins.get(str(a),{}).get("count",0) for a in ACTIONS]
        least=min(counts)
        start=int(digest(frame)[:2],16)%7
        for shift in ACTIONS:
            action=(start+shift)%7
            if counts[action]==least:
                return {"schema":SCHEMA,"action":action,
                        "status":"SELECT_NATIVE_UNKNOWN_PUBLIC_ACTION",
                        "external_fallback":False}
        raise ValueError("R15_NATIVE_ACTION_UNREACHABLE")

    def learn_selected(self, adapter, before, after):
        self._healthy()
        source_before=public_observation(before)
        source_after=public_observation(after)
        if (type(adapter) is not DoorKeyPublicAdapter or adapter.pending is not None
            or adapter.current is None or not adapter.ledger
            or adapter.events!=self.local.cursor+1):
            raise ValueError("R15_UNRETURNED_SOURCE_EVENT")
        event=adapter.ledger[-1]
        if (event["before_public_sha256"]!=digest(source_before)
            or event["after_public_sha256"]!=digest(source_after)
            or adapter.current!=source_after):
            raise ValueError("R15_SELECTED_SOURCE_PUBLIC_MISMATCH")
        action=event["action"]
        if type(action)is not int or action not in ACTIONS or self.samples>=MAX_SAMPLES:
            raise ValueError("R15_SOURCE_ACTION_OR_BUDGET")
        ctx=feature(source_before)
        if ctx not in self.memory and len(self.memory)>=MAX_CONTEXTS:
            raise ValueError("R15_CONTEXT_LIMIT")
        if self.live and self.temporal.steps>=192:
            raise ValueError("R15_LIVE_EPISODE_LIMIT")
        was=carrying(source_before["image"])
        now=carrying(source_after["image"])
        changed=source_before!=source_after
        same_held=source_before["image"][3][6]==source_after["image"][3][6]
        # Exactly one authoritative original R11 selected-outcome update.
        result=self.local.learn_selected(adapter)
        group=self.memory.setdefault(ctx,{})
        stat=dict(group.get(str(action),empty_stat()))
        stat["count"]+=1
        stat["changed"]+=int(changed)
        stat["retained_changed"]+=int(was and now and same_held and changed)
        stat["lost"]+=int(was and not now)
        stat["gained"]+=int(not was and now)
        group[str(action)]=stat
        self.samples+=1
        if self.live:
            self.temporal.learn_selected(source_before,action,source_after,event)
        self._healthy()
        return result

    def checkpoint(self):
        self._healthy()
        state={"schema":SCHEMA,"local":self.local.checkpoint().decode("utf-8"),
               "temporal":self.temporal.checkpoint().decode("utf-8"),
               "memory":self.memory,"samples":self.samples,"live":self.live}
        encoded=canonical(state)
        wire=canonical({"state":state,"sha256":hashlib.sha256(encoded).hexdigest()})
        if len(wire)>MAX_CHECKPOINT:
            raise ValueError("R15_CHECKPOINT_BUDGET")
        return wire

    @classmethod
    def restore(cls, blob):
        try:
            if type(blob)is not bytes or not 0<len(blob)<=MAX_CHECKPOINT:
                raise ValueError("R15_CHECKPOINT_SIZE")
            outer=json.loads(blob)
            if type(outer)is not dict or set(outer)!={"state","sha256"}:
                raise ValueError("R15_CHECKPOINT_ENVELOPE")
            st=outer["state"]
            if (type(st)is not dict or set(st)!={"schema","local","temporal",
                    "memory","samples","live"} or st["schema"]!=SCHEMA
                or hashlib.sha256(canonical(st)).hexdigest()!=outer["sha256"]):
                raise ValueError("R15_CHECKPOINT_SHA")
            local=PublicAffordanceCells.restore(st["local"].encode())
            temporal=TemporalCells.restore(st["temporal"].encode())
            if (type(st["samples"])is not int or st["samples"]!=local.samples
                or not 0<=st["samples"]<=MAX_SAMPLES or
                type(st["live"])is not bool or type(st["memory"])is not dict
                or len(st["memory"])>MAX_CONTEXTS):
                raise ValueError("R15_CHECKPOINT_META")
            total=0
            for ctx,row in st["memory"].items():
                bits=ctx.split(":")
                if (len(bits)!=2 or not bits[0].isdecimal() or
                    not 0<=int(bits[0])<=10 or bits[1] not in ("0","1")
                    or type(row)is not dict):
                    raise ValueError("R15_CHECKPOINT_CONTEXT")
                for action,cell in row.items():
                    if action not in tuple(map(str,ACTIONS)) or type(cell)is not dict or set(cell)!=set(empty_stat()):
                        raise ValueError("R15_CHECKPOINT_ACTION")
                    if any(type(x)is not int or x<0 or x>MAX_SAMPLES for x in cell.values()):
                        raise ValueError("R15_CHECKPOINT_CELL")
                    if (cell["count"]<=0 or any(cell[q]>cell["count"]
                        for q in ("changed","retained_changed","lost","gained"))):
                        raise ValueError("R15_CHECKPOINT_COUNTERS")
                    total+=cell["count"]
            if total!=st["samples"]:
                raise ValueError("R15_CHECKPOINT_TOTAL")
            obj=cls(local)
            obj.temporal=temporal
            obj.memory=st["memory"]
            obj.samples=st["samples"]
            obj.live=st["live"]
            if obj.checkpoint()!=blob:
                raise ValueError("R15_NONCANONICAL_CHECKPOINT")
            return obj
        except (ValueError,TypeError,KeyError,AttributeError,UnicodeDecodeError) as exc:
            raise ValueError("R15_UNTRUSTED_PUBLIC_CHECKPOINT") from exc
