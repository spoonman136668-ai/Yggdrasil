"""R16 independently learned original-source public motion vs camera-turn evidence.

Source action IDs are opaque: an observed direction-stable scene change is learned
from selected public before/after, never from a programmed "forward" action map.
"""
from __future__ import annotations
import hashlib
import json

from research.native.itd02.r10.public_adapter import (
    DoorKeyPublicAdapter, public_observation, canonical, digest
)
from research.native.itd02.r15.continuity_cells import NativeContinuity

SCHEMA="yggdrasil.itd02.r16.public-nonrotational-selected-effects.v1"
MAX_SAMPLES=4096
MAX_EPISODE=192
MAX_CHECKPOINT=600000

def stat():
    return {"n":0,"same_heading_changed":0,"heading_changed":0,
            "held_lost":0,"held_retained_changed":0}

def held(frame):
    return frame["image"][3][6][0] in (5,6,7)

class MotionCells:
    def __init__(self,local=None):
        self.local=NativeContinuity() if local is None else local
        if type(self.local)is not NativeContinuity:
            raise ValueError("R16_NON_NATIVE_SOURCE")
        self.motion=[stat() for _ in range(7)]
        self.episode=[0]*7
        self.samples=self.local.samples
        self.live=False

    def _valid(self):
        if (self.samples!=self.local.samples or not 0<=self.samples<=MAX_SAMPLES
            or len(self.motion)!=7 or len(self.episode)!=7
            or sum(cell["n"] for cell in self.motion)!=self.samples
            or sum(self.episode)>MAX_EPISODE):
            raise ValueError("R16_SELECTED_SOURCE_TOTALS")

    def start_session(self,adapter,name,live=False):
        self._valid()
        if type(live)is not bool:raise ValueError("R16_SESSION_FLAG")
        self.local.start_session(adapter,name,live=live)
        self.episode=[0]*7
        self.live=live

    def choose(self,before):
        self._valid()
        public=public_observation(before)
        if self.local.local.session is None:
            raise ValueError("R16_SOURCE_SESSION_REQUIRED")
        carry=held(public)
        highest=None
        preferred=None
        for action,cell in enumerate(self.motion):
            numerator=(12*cell["same_heading_changed"]
                     -4*cell["heading_changed"]-8*cell["held_lost"]
                     +4*cell["held_retained_changed"]*int(carry))
            score=(numerator*1024)//(cell["n"]+64)-96*self.episode[action]
            if highest is None or score>highest:
                highest=score
                preferred=action
        if highest is not None and highest>0:
            return {"schema":SCHEMA,"action":preferred,
                    "status":"SELECT_NATIVE_LEARNED_SAME_HEADING_PUBLIC_EFFECT",
                    "external_fallback":False}
        least=min(self.episode)
        start=int(digest(public)[:2],16)%7
        for i in range(7):
            action=(start+i)%7
            if self.episode[action]==least:
                return {"schema":SCHEMA,"action":action,
                        "status":"SELECT_NATIVE_ANTI_CYCLE_UNKNOWN_ACTION",
                        "external_fallback":False}
        raise ValueError("R16_ACTION_UNREACHABLE")

    def learn_selected(self,adapter,before,after):
        self._valid()
        public=public_observation(before)
        target=public_observation(after)
        if (type(adapter)is not DoorKeyPublicAdapter or adapter.pending is not None
            or not adapter.ledger or adapter.current!=target
            or adapter.events!=self.local.local.cursor+1
            or self.samples>=MAX_SAMPLES):
            raise ValueError("R16_NO_AUTHENTIC_SELECTED_EVENT")
        event=adapter.ledger[-1]
        action=event["action"]
        if (type(action)is not int or action not in range(7)
            or event["before_public_sha256"]!=digest(public)
            or event["after_public_sha256"]!=digest(target)
            or self.live and sum(self.episode)>=MAX_EPISODE):
            raise ValueError("R16_UNTRUSTED_SOURCE_ACTION")
        # The original R11 local selected-feedback path is the only authority.
        receipt=self.local.learn_selected(adapter,public,target)
        entry=self.motion[action]
        entry["n"]+=1
        direction_changed=public["direction"]!=target["direction"]
        scene_changed=public["image"]!=target["image"]
        entry["heading_changed"]+=int(direction_changed)
        entry["same_heading_changed"]+=int(not direction_changed and scene_changed)
        entry["held_lost"]+=int(held(public) and not held(target))
        entry["held_retained_changed"]+=int(
            not direction_changed and scene_changed and held(public) and
            held(target) and public["image"][3][6]==target["image"][3][6]
        )
        self.samples+=1
        if self.live:self.episode[action]+=1
        self._valid()
        return receipt

    def checkpoint(self):
        self._valid()
        state={"schema":SCHEMA,"parent":self.local.checkpoint().decode("utf-8"),
               "motion":self.motion,"episode":self.episode,
               "samples":self.samples,"live":self.live}
        encoded=canonical(state)
        blob=canonical({"state":state,"sha256":hashlib.sha256(encoded).hexdigest()})
        if len(blob)>MAX_CHECKPOINT:
            raise ValueError("R16_CHECKPOINT_BUDGET")
        return blob

    @classmethod
    def restore(cls,blob):
        try:
            if type(blob)is not bytes or not 0<len(blob)<=MAX_CHECKPOINT:
                raise ValueError("R16_CHECKPOINT_SIZE")
            wire=json.loads(blob)
            if type(wire)is not dict or set(wire)!={"state","sha256"}:
                raise ValueError("R16_CHECKPOINT_ENVELOPE")
            st=wire["state"]
            if (type(st)is not dict or set(st)!={"schema","parent","motion",
                 "episode","samples","live"} or st["schema"]!=SCHEMA
                or hashlib.sha256(canonical(st)).hexdigest()!=wire["sha256"]):
                raise ValueError("R16_CHECKPOINT_SHA")
            parent=NativeContinuity.restore(st["parent"].encode("utf-8"))
            if (type(st["samples"])is not int or not 0<=st["samples"]<=MAX_SAMPLES
                or st["samples"]!=parent.samples or type(st["live"])is not bool
                or type(st["motion"])is not list or len(st["motion"])!=7
                or type(st["episode"])is not list or len(st["episode"])!=7
                or any(type(n)is not int or not 0<=n<=MAX_EPISODE for n in st["episode"])):
                raise ValueError("R16_CHECKPOINT_META")
            for cell in st["motion"]:
                if (type(cell)is not dict or set(cell)!=set(stat())
                    or any(type(n)is not int or not 0<=n<=MAX_SAMPLES for n in cell.values())
                    or any(cell[k]>cell["n"] for k in (
                        "same_heading_changed","heading_changed","held_lost","held_retained_changed"))
                    or cell["held_retained_changed"]>cell["same_heading_changed"]):
                    raise ValueError("R16_CHECKPOINT_STAT")
            restored=cls(parent)
            restored.motion=st["motion"]
            restored.episode=st["episode"]
            restored.samples=st["samples"]
            restored.live=st["live"]
            restored._valid()
            if restored.checkpoint()!=blob:raise ValueError("R16_NONCANONICAL")
            return restored
        except (ValueError,TypeError,AttributeError,KeyError,UnicodeDecodeError) as exc:
            raise ValueError("R16_UNTRUSTED_CHECKPOINT") from exc
