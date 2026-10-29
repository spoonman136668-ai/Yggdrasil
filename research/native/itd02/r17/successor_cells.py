"""R17 source-public successor persistence atop unchanged original R16 cells.

Local episode counts only from authenticated R10 selected source transitions.
No built-in key, door, goal, map, or source-action semantic lookup.
"""
from __future__ import annotations
import hashlib
import json
from research.native.itd02.r10.public_adapter import (
    DoorKeyPublicAdapter, public_observation, canonical, digest
)
from research.native.itd02.r16.motion_cells import MotionCells, MAX_SAMPLES

SCHEMA="yggdrasil.itd02.r17.public-selected-successor-persistence.v1"
MAX_EPISODE=192
MAX_CONTEXTS=192
MAX_CHECKPOINT=650000

def blank():
    return {"count":0,"last":""}

class SuccessorCells:
    def __init__(self,parent=None):
        self.parent=MotionCells() if parent is None else parent
        if type(self.parent) is not MotionCells:
            raise ValueError("R17_NATIVE_PARENT_TYPE")
        self.attempts={}
        self.visits={}

    @property
    def samples(self):
        return self.parent.samples

    def _valid(self):
        if (len(self.attempts)>MAX_CONTEXTS or len(self.visits)>MAX_EPISODE or
            sum(self.parent.episode)!=sum(self.visits.values()) or
            sum(sum(c["count"] for c in row.values()) for row in self.attempts.values())
              !=sum(self.visits.values())):
            raise ValueError("R17_SELECTED_SOURCE_EPISODE_TOTALS")

    def start_session(self,adapter,name,live=False):
        self._valid()
        self.parent.start_session(adapter,name,live=live)
        self.attempts={}
        self.visits={}

    def choose(self,before):
        self._valid()
        p=public_observation(before)
        if self.parent.local.local.session is None:
            raise ValueError("R17_UNINITIALIZED_SOURCE")
        key=digest(p)
        row=self.attempts.get(key,{})
        held=p["image"][3][6][0] in (5,6,7)
        high=None
        best=None
        for action,cell in enumerate(self.parent.motion):
            num=(12*cell["same_heading_changed"]
                 -4*cell["heading_changed"]-8*cell["held_lost"]
                 +4*int(held)*cell["held_retained_changed"])
            local=row.get(str(action),blank())
            score=(num*1024)//(cell["n"]+64)-96*self.parent.episode[action]
            score-=3072*local["count"]
            if local["last"]:
                score-=1024*self.visits.get(local["last"],0)
            if high is None or score>high:
                high=score
                best=action
        if high is not None and high>0:
            return {"schema":SCHEMA,"action":best,
                    "status":"SELECT_NATIVE_PERSISTENT_PUBLIC_SUCCESSOR",
                    "external_fallback":False}
        minimum=min(row.get(str(a),blank())["count"] for a in range(7))
        start=int(key[:2],16)%7
        for i in range(7):
            action=(start+i)%7
            if row.get(str(action),blank())["count"]==minimum:
                return {"schema":SCHEMA,"action":action,
                        "status":"SELECT_NATIVE_UNTRIED_PUBLIC_SUCCESSOR",
                        "external_fallback":False}
        raise ValueError("R17_NO_SELECTED_ACTION")

    def learn_selected(self,adapter,before,after):
        self._valid()
        p=public_observation(before);q=public_observation(after)
        if (type(adapter)is not DoorKeyPublicAdapter or adapter.pending is not None
            or not adapter.ledger or adapter.current!=q or
            adapter.events!=self.parent.local.local.cursor+1):
            raise ValueError("R17_UNAUTHENTICATED_SELECTED_SOURCE")
        event=adapter.ledger[-1]
        action=event["action"]
        if (type(action)is not int or action not in range(7) or
            event["before_public_sha256"]!=digest(p) or
            event["after_public_sha256"]!=digest(q)):
            raise ValueError("R17_INVALID_SELECTED_SOURCE_EVENT")
        original=digest(p);successor=digest(q)
        if (self.parent.live and
            (sum(self.parent.episode)>=MAX_EPISODE or
             (original not in self.attempts and len(self.attempts)>=MAX_CONTEXTS) or
             (successor not in self.visits and len(self.visits)>=MAX_EPISODE))):
            raise ValueError("R17_LOCAL_SOURCE_BOUNDS")
        receipt=self.parent.learn_selected(adapter,p,q)
        if self.parent.live:
            row=self.attempts.setdefault(original,{})
            cell=dict(row.get(str(action),blank()))
            cell["count"]+=1;cell["last"]=successor
            row[str(action)]=cell
            self.visits[successor]=self.visits.get(successor,0)+1
        self._valid()
        return receipt

    def checkpoint(self):
        self._valid()
        state={"schema":SCHEMA,"parent":self.parent.checkpoint().decode("utf-8"),
               "attempts":self.attempts,"visits":self.visits}
        encoded=canonical(state)
        result=canonical({"state":state,"sha256":hashlib.sha256(encoded).hexdigest()})
        if len(result)>MAX_CHECKPOINT:
            raise ValueError("R17_SNAPSHOT_SIZE")
        return result

    @classmethod
    def restore(cls,blob):
        try:
            if type(blob)is not bytes or not 0<len(blob)<=MAX_CHECKPOINT:
                raise ValueError("R17_RESTORE_SIZE")
            wire=json.loads(blob)
            if type(wire)is not dict or set(wire)!={"state","sha256"}:
                raise ValueError("R17_RESTORE_ENVELOPE")
            s=wire["state"]
            if (type(s)is not dict or set(s)!={"schema","parent","attempts","visits"}
                or s["schema"]!=SCHEMA or
                hashlib.sha256(canonical(s)).hexdigest()!=wire["sha256"]):
                raise ValueError("R17_RESTORE_DIGEST")
            parent=MotionCells.restore(s["parent"].encode("utf-8"))
            if (type(s["attempts"])is not dict or type(s["visits"])is not dict or
                len(s["attempts"])>MAX_CONTEXTS or len(s["visits"])>MAX_EPISODE):
                raise ValueError("R17_RESTORE_BOUNDS")
            for key,row in s["attempts"].items():
                if type(key)is not str or len(key)!=64 or type(row)is not dict:
                    raise ValueError("R17_BAD_CONTEXT")
                if any(c not in "0123456789abcdef" for c in key):
                    raise ValueError("R17_BAD_CONTEXT_HASH")
                for action,cell in row.items():
                    if (action not in tuple(str(i) for i in range(7)) or
                        type(cell)is not dict or set(cell)!={"count","last"} or
                        type(cell["count"])is not int or not 1<=cell["count"]<=MAX_EPISODE or
                        type(cell["last"])is not str or len(cell["last"])!=64 or
                        any(ch not in "0123456789abcdef" for ch in cell["last"])):
                        raise ValueError("R17_BAD_ACTION")
            for key,n in s["visits"].items():
                if (type(key)is not str or len(key)!=64 or
                    any(ch not in "0123456789abcdef" for ch in key) or
                    type(n)is not int or not 1<=n<=MAX_EPISODE):
                    raise ValueError("R17_BAD_VISITS")
            obj=cls(parent)
            obj.attempts=s["attempts"];obj.visits=s["visits"]
            obj._valid()
            if obj.checkpoint()!=blob:
                raise ValueError("R17_NONCANONICAL")
            return obj
        except (ValueError,TypeError,AttributeError,KeyError,UnicodeDecodeError) as exc:
            raise ValueError("R17_UNTRUSTED_CHECKPOINT") from exc
