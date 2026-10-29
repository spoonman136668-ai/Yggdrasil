"""R19 opt-in native mission-preserving actor from original R17 public FIT.

Legacy DoorKey dispatches unchanged R17. Other original public missions use
separate local-cell motion/successor state initialized from READ-ONLY R17
learned FIT motion counts; never replace genuine source mission or call R17's
old mission-bound actor with a fake DoorKey observation.
No native production/Farama changes; source-only developmental actor.
"""
from __future__ import annotations
import hashlib
import json
from research.native.itd02.r10.public_adapter import (
    DoorKeyPublicAdapter, MISSION as DOORKEY)
from research.native.itd02.r17.successor_cells import SuccessorCells, blank
from research.native.itd02.r18.public_boundary import (
    PublicBoundary,public_frame,digest,canonical)

SCHEMA="yggdrasil.itd02.r19.mission-preserved-selected-native-actor.v1"
MAX_BYTES=2400000
MAX_STEPS=192

class MissionActor:
    def __init__(self, original=None):
        self.original=SuccessorCells() if original is None else original
        if type(self.original) is not SuccessorCells:
            raise ValueError("R19_ORIGINAL_NATIVE_TYPE")
        self.boundary=PublicBoundary()
        self.legacy=None
        self.motion=None
        self.attempts={}
        self.visits={}
        self.counts=[0]*7
        self.mode=None

    def begin(self,source_public):
        p=public_frame(source_public)
        if self.mode is not None:
            raise ValueError("R19_EPISODE_ALREADY_OPEN")
        self.boundary.begin(p)
        if p["mission"]==DOORKEY:
            adapter=DoorKeyPublicAdapter()
            adapter.reset_public(p)
            self.original.start_session(adapter,"r19-original-doorkey",live=True)
            self.legacy=adapter
            self.mode="ORIGINAL_DOORKEY_UNCHANGED"
        else:
            # Original FIT effects are read; this opt-in developmental actor
            # has its own separate motion and public successor learning.
            self.motion=[dict(row) for row in self.original.parent.motion]
            self.mode="NATIVE_NEW_MISSION_PUBLIC_SELECTED"

    def choose(self):
        if self.mode is None or self.boundary.pending is not None or self.boundary.finished:
            raise ValueError("R19_NO_ACTION_PHASE")
        p=public_frame(self.boundary.current)
        if self.mode=="ORIGINAL_DOORKEY_UNCHANGED":
            result=self.original.choose(p)
            return {"action":result["action"],"reason":result["status"],
                    "mode":self.mode,"source_public_sha256":digest(p)}
        if self.mode!="NATIVE_NEW_MISSION_PUBLIC_SELECTED":
            raise ValueError("R19_INVALID_ACTOR_MODE")
        key=digest(p)
        row=self.attempts.get(key,{})
        held=p["image"][3][6][0] in (5,6,7)
        best=None;best_score=None
        for a,s in enumerate(self.motion):
            score=(12*s["same_heading_changed"]-4*s["heading_changed"]
                   -8*s["held_lost"]+4*int(held)*s["held_retained_changed"])*1024//(s["n"]+64)
            score-=96*self.counts[a]+3072*row.get(str(a),blank())["count"]
            last=row.get(str(a),blank())["last"]
            if last:score-=1024*self.visits.get(last,0)
            if best_score is None or score>best_score:
                best_score=score;best=a
        if best_score>0:
            reason="SELECT_R19_NATIVE_SOURCE_LEARNED_PUBLIC_SUCCESSOR"
        else:
            minimum=min(row.get(str(a),blank())["count"] for a in range(7))
            start=int(key[:2],16)%7
            best=next((start+i)%7 for i in range(7) if row.get(str((start+i)%7),blank())["count"]==minimum)
            reason="SELECT_R19_NATIVE_UNTRIED_PUBLIC_SUCCESSOR"
        return {"action":best,"reason":reason,"mode":self.mode,
                "source_public_sha256":key}

    def commit(self,action):
        if self.mode is None:
            raise ValueError("R19_ACTION_BEFORE_BEGIN")
        self.boundary.commit(action)
        if self.legacy is not None:
            self.legacy.submit(action)
        return action

    def feedback(self,action,source_public_after,reward,terminated=False,truncated=False):
        if self.mode is None or self.boundary.current is None or self.boundary.pending!=action:
            raise ValueError("R19_UNAUTHENTICATED_SOURCE_RETURN")
        if self.boundary.finished:
            raise ValueError("R19_TERMINAL_ALREADY_USED")
        q=public_frame(source_public_after)
        before=public_frame(self.boundary.current)
        if q["mission"]!=before["mission"]:
            raise ValueError("R19_SOURCE_MISSION_CHANGED")
        if self.legacy is not None:
            # Original exact native selected-feedback contract unchanged.
            # No source mission substitution or hidden policy inputs.
            if truncated:
                raise ValueError("R19_LEGACY_TRUNCATION_UNSUPPORTED")
            self.legacy.complete(q,reward,terminated,truncated)
            native=self.original.learn_selected(self.legacy,before,q)
            receipt=self.boundary.feedback(action,q,reward,terminated,truncated)
            return {"public_receipt":receipt,"legacy_receipt":native}
        if self.mode!="NATIVE_NEW_MISSION_PUBLIC_SELECTED":
            raise ValueError("R19_INVALID_SOURCE_MODE")
        if len(self.boundary.events)>=MAX_STEPS:
            raise ValueError("R19_DEVELOPMENT_EPISODE_BUDGET")
        original=digest(before);successor=digest(q)
        if (original not in self.attempts and len(self.attempts)>=MAX_STEPS or
            successor not in self.visits and len(self.visits)>=MAX_STEPS):
            raise ValueError("R19_LOCAL_PUBLIC_STATE_BOUNDS")
        receipt=self.boundary.feedback(action,q,reward,terminated,truncated)
        row=self.attempts.setdefault(original,{})
        cell=dict(row.get(str(action),blank()))
        cell["count"]+=1;cell["last"]=successor
        row[str(action)]=cell
        self.visits[successor]=self.visits.get(successor,0)+1
        self.counts[action]+=1
        s=self.motion[action]
        s["n"]+=1
        if before["direction"]!=q["direction"]:
            s["heading_changed"]+=1
        if before["direction"]==q["direction"] and before["image"]!=q["image"]:
            s["same_heading_changed"]+=1
            carried_before=before["image"][3][6]
            carried_after=q["image"][3][6]
            if carried_before[0] in (5,6,7) and carried_before==carried_after:
                s["held_retained_changed"]+=1
        if before["image"][3][6][0] in (5,6,7) and q["image"][3][6][0] not in (5,6,7):
            s["held_lost"]+=1
        return {"public_receipt":receipt,"legacy_receipt":None}

    def checkpoint(self):
        state={"schema":SCHEMA,"mode":self.mode,"original":self.original.checkpoint().decode("utf-8"),
          "boundary":self.boundary.checkpoint().decode("utf-8"),
          "legacy":self.legacy.checkpoint().decode("utf-8") if self.legacy is not None else None,
          "motion":self.motion,"attempts":self.attempts,"visits":self.visits,"counts":self.counts}
        raw=canonical({"state":state,"sha256":digest(state)})
        if len(raw)>MAX_BYTES:raise ValueError("R19_NATIVE_CHECKPOINT_BUDGET")
        return raw

    @classmethod
    def restore(cls,raw):
        if type(raw) is not bytes or not 0<len(raw)<=MAX_BYTES:
            raise ValueError("R19_NATIVE_CHECKPOINT_SIZE")
        try:
            env=json.loads(raw);s=env["state"]
            if (set(env)!={"state","sha256"} or digest(s)!=env["sha256"] or
                set(s)!={"schema","mode","original","boundary","legacy","motion","attempts","visits","counts"}
                or s["schema"]!=SCHEMA or s["mode"] not in (
                    None,"ORIGINAL_DOORKEY_UNCHANGED","NATIVE_NEW_MISSION_PUBLIC_SELECTED")):
                raise ValueError("R19_NATIVE_CHECKPOINT_SCHEMA")
            old=SuccessorCells.restore(s["original"].encode("utf-8"))
            a=cls(old)
            a.boundary=PublicBoundary.restore(s["boundary"].encode("utf-8"))
            a.legacy=DoorKeyPublicAdapter.restore(s["legacy"].encode("utf-8")) if s["legacy"] is not None else None
            a.motion=s["motion"];a.attempts=s["attempts"];a.visits=s["visits"];a.counts=s["counts"];a.mode=s["mode"]
            if (len(a.counts)!=7 or type(a.attempts)is not dict or type(a.visits)is not dict or
                len(a.attempts)>MAX_STEPS or len(a.visits)>MAX_STEPS or
                (a.mode=="ORIGINAL_DOORKEY_UNCHANGED")!=(a.legacy is not None) or
                (a.mode=="NATIVE_NEW_MISSION_PUBLIC_SELECTED")!=(a.motion is not None)):
                raise ValueError("R19_NATIVE_CHECKPOINT_FIELDS")
            if a.checkpoint()!=raw:
                raise ValueError("R19_NATIVE_CHECKPOINT_NONCANONICAL")
            return a
        except (KeyError,ValueError,TypeError,AttributeError,OverflowError,UnicodeError) as e:
            raise ValueError("R19_UNTRUSTED_NATIVE_CHECKPOINT") from e
