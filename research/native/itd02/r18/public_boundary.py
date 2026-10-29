"""R18 opt-in public-only seven-action task-neutral boundary, NOT a native actor.

Every genuine mission is preserved verbatim. Historical R10/R17 remain unchanged
and still reject missions outside DoorKey; R18 does not claim to make R17
compatible with another original source environment.
"""
from __future__ import annotations
import hashlib
import json
import math
import unicodedata
from research.native.itd02.r10.public_adapter import _image_lists

SCHEMA="yggdrasil.itd02.r18.original-public-task-neutral-boundary.v1"
MAX_STEPS=192
MAX_MISSION=256
MAX_CHECKPOINT=2000000
FIELDS=frozenset(("image","direction","mission"))
LEGACY="use the key to open the door and then get to the goal"

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,
                      allow_nan=False).encode("utf-8")

def digest(x):
    return hashlib.sha256(canonical(x)).hexdigest()

def public_frame(obs):
    if type(obs) is not dict or set(obs)!=FIELDS:
        raise ValueError("R18_PUBLIC_FIELDS_OR_PRIVILEGED_INPUT")
    direction=obs["direction"]
    mission=obs["mission"]
    if type(direction) is not int or direction not in (0,1,2,3):
        raise ValueError("R18_PUBLIC_DIRECTION")
    if (type(mission) is not str or not 1<=len(mission)<=MAX_MISSION or
        any(unicodedata.category(c) in ("Cc","Cs") for c in mission)):
        raise ValueError("R18_PUBLIC_MISSION_UNTRUSTED")
    return {"image":_image_lists(obs["image"]),"direction":direction,"mission":mission}

def public_digest(obs):
    return digest(public_frame(obs))

class PublicBoundary:
    def __init__(self):
        self.start=None
        self.current=None
        self.events=[]
        self.pending=None
        self.finished=False

    def begin(self,source_public):
        if self.current is not None:
            raise ValueError("R18_EPISODE_ALREADY_ACTIVE")
        p=public_frame(source_public)
        self.start=p
        self.current=p

    def commit(self,selected_action):
        if self.current is None or self.pending is not None or self.finished:
            raise ValueError("R18_NO_PUBLIC_ACTION_CAPABILITY")
        if type(selected_action) is not int or not 0<=selected_action<=6:
            raise ValueError("R18_INVALID_SELECTED_SOURCE_ACTION")
        if len(self.events)>=MAX_STEPS:
            raise ValueError("R18_SOURCE_EPISODE_BUDGET")
        self.pending=selected_action
        return selected_action

    def feedback(self,selected_action,source_public_after,reward,terminated=False,truncated=False):
        if self.current is None or self.pending is None or self.finished:
            raise ValueError("R18_FEEDBACK_NOT_AUTHORIZED")
        if type(selected_action) is not int or selected_action!=self.pending:
            raise ValueError("R18_WRONG_SELECTED_SOURCE_ACTION")
        q=public_frame(source_public_after)
        if q["mission"]!=self.current["mission"]:
            raise ValueError("R18_ORIGINAL_PUBLIC_MISSION_CHANGED_WITHIN_EPISODE")
        if (type(reward) not in (int,float) or not math.isfinite(reward) or
            not 0<=reward<=1 or type(terminated) is not bool or
            type(truncated) is not bool):
            raise ValueError("R18_UNTRUSTED_SELECTED_SOURCE_RETURN")
        receipt={
            "index":len(self.events)+1,
            "before":digest(self.current),
            "action":selected_action,
            "after":digest(q),
            "reward":float(reward),
            "terminated":terminated,
            "truncated":truncated,
        }
        self.events.append({"receipt":receipt,"public_after":q})
        self.current=q
        self.pending=None
        self.finished=terminated or truncated
        return dict(receipt)

    def checkpoint(self):
        state={"schema":SCHEMA,"start":self.start,"current":self.current,
               "events":self.events,"pending":self.pending,"finished":self.finished}
        blob=canonical({"state":state,"sha256":digest(state)})
        if len(blob)>MAX_CHECKPOINT:
            raise ValueError("R18_CHECKPOINT_TOO_LARGE")
        return blob

    @classmethod
    def restore(cls,blob):
        if type(blob) is not bytes or not 0<len(blob)<=MAX_CHECKPOINT:
            raise ValueError("R18_UNTRUSTED_CHECKPOINT_BYTES")
        try:
            env=json.loads(blob)
            if type(env) is not dict or set(env)!={"state","sha256"} or digest(env["state"])!=env["sha256"]:
                raise ValueError("R18_CHECKPOINT_HASH_INVALID")
            state=env["state"]
            if type(state) is not dict or set(state)!={"schema","start","current","events","pending","finished"} or state["schema"]!=SCHEMA:
                raise ValueError("R18_CHECKPOINT_SCHEMA_INVALID")
            obj=cls()
            if state["start"] is None:
                if any(state[k] not in (None,[],False) for k in ("current","events","pending","finished")):
                    raise ValueError("R18_EMPTY_CHECKPOINT_DRIFT")
            else:
                obj.begin(state["start"])
                if type(state["events"]) is not list or len(state["events"])>MAX_STEPS:
                    raise ValueError("R18_CHECKPOINT_EVENTS_INVALID")
                for item in state["events"]:
                    if type(item) is not dict or set(item)!={"receipt","public_after"}:
                        raise ValueError("R18_CHECKPOINT_EVENT_FIELDS")
                    r=item["receipt"]
                    if type(r) is not dict or set(r)!={"index","before","action","after","reward","terminated","truncated"}:
                        raise ValueError("R18_CHECKPOINT_RECEIPT_FIELDS")
                    obj.commit(r["action"])
                    if obj.feedback(r["action"],item["public_after"],r["reward"],
                                    r["terminated"],r["truncated"])!=r:
                        raise ValueError("R18_CHECKPOINT_REPLAY_DRIFT")
                if state["pending"] is not None:
                    obj.commit(state["pending"])
                if (obj.current!=state["current"] or obj.finished is not state["finished"] or
                    obj.pending!=state["pending"]):
                    raise ValueError("R18_CHECKPOINT_STATE_DRIFT")
            if obj.checkpoint()!=blob:
                raise ValueError("R18_CHECKPOINT_NONCANONICAL")
            return obj
        except (KeyError,TypeError,OverflowError,RecursionError,UnicodeError) as exc:
            raise ValueError("R18_CHECKPOINT_INVALID") from exc
