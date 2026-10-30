"""MG88 bounded source-public egocentric alignment observations.

A geometric pixel-overlap inductive bias is supplied, but *no* action meanings,
tile-object semantics, routes, true pose, simulator grid, or goal encoding.
All action->alignment effects come from actually selected source transitions.
"""
from __future__ import annotations
import hashlib
import json
from research.native.itd02.mg87.transition_cells import PublicTransitionCells
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter,original_public
from research.native.itd02.r10.public_adapter import canonical,digest

SCHEMA="yggdrasil.itd02.mg88.native-public-view-alignment-cells.v1"
ACTIONS=7
MAX_CHECKPOINT=12000000
MAX_STEPS=12000
SHIFT=(-1,0,1)

def _blank():
    return {"count":0,"turns":0,"unresolved":0,"shift":{}}

def public_alignment(before,after):
    """Observed image overlap only; never a hidden action/pose estimate.

    Offset is before[x,y] vs after[x+dx,y+dy], not a world coordinate.
    Visible public triples (type != 0) must match in >=70% of >=8 pairs.
    Stable tie break favors higher agreement and more matched overlap.
    """
    original_public(before)
    original_public(after)
    if before["direction"]!=after["direction"]:
        return None
    img0,img1=before["image"],after["image"]
    candidates=[]
    for dx in SHIFT:
        for dy in SHIFT:
            compared=0
            matched=0
            for x in range(7):
                for y in range(7):
                    nx,ny=x+dx,y+dy
                    if not (0<=nx<7 and 0<=ny<7):
                        continue
                    a,b=img0[x][y],img1[nx][ny]
                    if a[0]==0 or b[0]==0:
                        continue
                    compared+=1
                    if a==b:
                        matched+=1
            if compared>=8 and 10*matched>=7*compared:
                # Avoid mistaking repetitive walls for confirmed motion:
                # exact ties choose smaller offset in camera coordinates.
                candidates.append((matched*1000//compared,matched,compared,
                                   -(abs(dx)+abs(dy)),-abs(dx),-abs(dy),dx,dy))
    if not candidates:
        return None
    top=max(candidates)
    return (top[-2],top[-1])

class PublicAlignmentCells:
    def __init__(self,parent=None):
        self.parent=PublicTransitionCells("local") if parent is None else parent
        if type(self.parent) is not PublicTransitionCells or self.parent.mode!="local":
            raise ValueError("MG88_FROZEN_NATIVE_PARENT_REQUIRED")
        self.events=[_blank() for _ in range(ACTIONS)]

    @property
    def samples(self):
        return self.parent.samples

    def _valid(self):
        self.parent._valid()
        if type(self.events) is not list or len(self.events)!=ACTIONS:
            raise ValueError("MG88_ACTION_ARRAY_INVALID")
        total=0
        for entry in self.events:
            if (type(entry) is not dict or set(entry)!={"count","turns","unresolved","shift"}
                or any(type(entry[k]) is not int or not 0<=entry[k]<=MAX_STEPS
                       for k in ("count","turns","unresolved"))
                or type(entry["shift"]) is not dict or len(entry["shift"])>9):
                raise ValueError("MG88_ACTION_SOURCE_LEDGER_BOUNDS")
            count=entry["count"]
            if entry["turns"]+entry["unresolved"]>count:
                raise ValueError("MG88_UNOBSERVABLE_COUNT")
            shifts=0
            for name,value in entry["shift"].items():
                if (type(name) is not str or name not in
                    {str(dx)+","+str(dy) for dx in SHIFT for dy in SHIFT}
                    or type(value) is not int or not 0<value<=MAX_STEPS):
                    raise ValueError("MG88_NO_PRIVILEGED_SHIFT")
                shifts+=value
            if shifts+entry["turns"]+entry["unresolved"]!=count:
                raise ValueError("MG88_ORIGINAL_SOURCE_CONSERVATION")
            total+=count
        if total!=self.samples:
            raise ValueError("MG88_WRAPPER_PARENT_SAMPLE_MISMATCH")

    def start_session(self,adapter,name,live=False):
        if type(adapter) is not OriginalMissionAdapter or live:
            raise ValueError("MG88_ORIGINAL_PUBLIC_SESSION_REQUIRED")
        self._valid()
        return self.parent.start_session(adapter,name,live=False)

    def choose(self,before):
        original_public(before)
        self._valid()
        ident=digest(before)
        row=self.parent.cells.get(ident)
        if row is None:
            row=[{"count":0,"next":{},"q":0} for _ in range(ACTIONS)]
        def score(a):
            local=row[a]["count"]
            prior=self.events[a]
            shifts=sum(v for k,v in prior["shift"].items() if k!="0,0")
            recurring=max(row[a]["next"].values(),default=0)
            # Preregistered, fixed source-empirical action scores. No
            # explicit turn/forward/pickup semantics or goal knowledge.
            return (300//(1+local)
                +200*shifts//(1+prior["count"])
                +60*prior["turns"]//(1+prior["count"])
                -150*recurring//(1+local))
        action=max(range(ACTIONS),key=lambda a:(score(a),-a))
        return {"schema":SCHEMA,"action":action,
                "status":"MG88_OBSERVED_VIEW_ALIGNMENT_ACTION",
                "external_fallback":False}

    def learn_selected(self,adapter,before,after):
        self._valid()
        original_public(before)
        original_public(after)
        if (type(adapter) is not OriginalMissionAdapter
            or adapter.current!=after or adapter.pending is not None
            or not adapter.ledger or before["mission"]!=after["mission"]):
            raise ValueError("MG88_NOT_ACTUAL_SELECTED_ORIGINAL_TRANSITION")
        last=adapter.ledger[-1]
        if (type(last.get("action")) is not int
            or not 0<=last["action"]<ACTIONS
            or last["before_sha"]!=digest(before)
            or last["after_sha"]!=digest(after)):
            raise ValueError("MG88_SELECTED_LEDGER_IDENTITY")
        if self.samples>=MAX_STEPS:
            raise ValueError("MG88_SOURCE_ACTION_CAP")
        before_count=self.samples
        offset=public_alignment(before,after)
        receipt=self.parent.learn_selected(adapter,before,after)
        if self.samples!=before_count+1:
            raise ValueError("MG88_NATIVE_PARENT_SAMPLE_DRIFT")
        row=self.events[last["action"]]
        row["count"]+=1
        if before["direction"]!=after["direction"]:
            row["turns"]+=1
        elif offset is None:
            row["unresolved"]+=1
        else:
            k=str(offset[0])+","+str(offset[1])
            row["shift"][k]=row["shift"].get(k,0)+1
        self._valid()
        return receipt

    def checkpoint(self):
        self._valid()
        state={"schema":SCHEMA,"parent":self.parent.checkpoint().decode("utf-8"),
               "events":self.events}
        wire=canonical({"state":state,
                        "sha256":hashlib.sha256(canonical(state)).hexdigest()})
        if len(wire)>MAX_CHECKPOINT:
            raise ValueError("MG88_FROZEN_CHECKPOINT_LIMIT")
        return wire

    @classmethod
    def restore(cls,raw):
        try:
            if type(raw) is not bytes or not 0<len(raw)<=MAX_CHECKPOINT:
                raise ValueError("MG88_UNTRUSTED_BYTES")
            outer=json.loads(raw)
            if type(outer) is not dict or set(outer)!={"state","sha256"}:
                raise ValueError("MG88_CHECKPOINT_FIELDS")
            state=outer["state"]
            if (type(state) is not dict or
                set(state)!={"schema","parent","events"}
                or state["schema"]!=SCHEMA or type(state["parent"]) is not str
                or hashlib.sha256(canonical(state)).hexdigest()!=outer["sha256"]):
                raise ValueError("MG88_COLD_SOURCE_DIGEST_INVALID")
            obj=cls(PublicTransitionCells.restore(state["parent"].encode("utf-8")))
            obj.events=state["events"]
            obj._valid()
            if obj.checkpoint()!=raw:
                raise ValueError("MG88_NONCANONICAL_COLD")
            return obj
        except (ValueError,TypeError,KeyError,AttributeError,UnicodeError) as e:
            raise ValueError("MG88_UNTRUSTED_COLD_STATE") from e
