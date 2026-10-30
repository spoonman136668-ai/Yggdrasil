"""MG92 original-source feedback on frozen successful-teacher public prototypes.

This is hand-engineered anti-collapse on teacher-conditioned learning, not
autonomous discovery. Only actually selected source public consequences enter
feedback; all fitted source prototypes and discounted rewards remain frozen.
"""
from __future__ import annotations
import hashlib
import json
from research.native.itd02.mg91.native_prototypes import (
    PublicRewardPrototypes,_features,K)
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter,original_public
from research.native.itd02.r10.public_adapter import canonical,digest

SCHEMA="yggdrasil.itd02.mg92.source-public-feedback-action-gate.v1"
MAX_PAIRS=4096
MAX_BYTES=12000000

class PublicFeedbackGate:
    def __init__(self,parent=None):
        self.parent=PublicRewardPrototypes() if parent is None else parent
        if type(self.parent) is not PublicRewardPrototypes:
            raise ValueError("MG92_FROZEN_TEACHER_REWARD_PARENT_REQUIRED")
        self.failed={}
        self.last_action=-1
        self.streak=0
        self.feedback_samples=0

    @property
    def data_sha(self):
        return self.parent.data_sha

    @property
    def examples(self):
        return self.parent.examples

    @property
    def training_count(self):
        return self.parent.training_count

    def fit(self,episodes):
        self.parent.fit(episodes)
        self._valid()

    def _valid(self):
        self.parent._valid()
        if (type(self.failed) is not dict or len(self.failed)>MAX_PAIRS
            or type(self.last_action) is not int or self.last_action not in range(-1,7)
            or type(self.streak) is not int or not 0<=self.streak<=384
            or type(self.feedback_samples) is not int or
            not 0<=self.feedback_samples<=384):
            raise ValueError("MG92_SOURCE_FEEDBACK_MEMORY_LIMIT")
        for key,value in self.failed.items():
            parts=key.split(":")
            if (type(key) is not str or len(parts)!=2 or len(parts[0])!=64
                or any(c not in "0123456789abcdef" for c in parts[0])
                or parts[1] not in [str(x) for x in range(7)]
                or type(value) is not int or not 0<value<=384):
                raise ValueError("MG92_UNTRUSTED_SELECTED_FAILURE_PAIR")

    def start_session(self,adapter,name,live=False):
        self.parent.start_session(adapter,name,live)
        self.failed={}
        self.last_action=-1
        self.streak=0
        self.feedback_samples=0
        self._valid()

    def _votes(self,before):
        # Exact original MG91 trained prototype similarity/reward-to-go
        # features, not a teacher call or source-internal object code.
        current=set(_features(before))
        front=before["image"][3][5]
        selected=[]
        for index,p in enumerate(self.parent.examples):
            overlap=len(current.intersection(p["patch"]))
            union=max(1,len(current.union(p["patch"])))
            similarity=(200*int(p["mission"]==before["mission"])
                       +100*int(p["direction"]==before["direction"])
                       +100*int(p["front"]==front)
                       +50*int(p["prev"]==self.parent.prev)
                       +400*overlap//union)
            selected.append((similarity,-index,p["action"],p["value"]))
        scores=[0]*7
        for similarity,_,action,value in sorted(selected,reverse=True)[:K]:
            scores[action]+=(1+similarity)*value
        return scores

    def choose(self,before):
        original_public(before)
        self._valid()
        scores=self._votes(before)
        sha=digest(before)
        for action in range(7):
            count=self.failed.get(sha+":"+str(action),0)
            scores[action]-=200000*min(3,count)
            if action==self.last_action:
                scores[action]-=150000*max(0,self.streak-2)
        action=max(range(7),key=lambda a:(scores[a],-a))
        return {"schema":SCHEMA,"action":action,
                "status":"MG92_TRAINED_PUBLIC_FEEDBACK_ACTION",
                "external_fallback":False}

    def observe_selected(self,adapter,before,after):
        original_public(before)
        original_public(after)
        if (type(adapter) is not OriginalMissionAdapter
            or adapter.current!=after or adapter.pending is not None
            or not adapter.ledger or before["mission"]!=after["mission"]):
            raise ValueError("MG92_UNSELECTED_HELDOUT_SOURCE")
        row=adapter.ledger[-1]
        action=row["action"]
        if (type(action) is not int or action not in range(7)
            or row["before_sha"]!=digest(before)
            or row["after_sha"]!=digest(after)):
            raise ValueError("MG92_SELECTED_PUBLIC_SOURCE_DIGEST")
        if self.feedback_samples>=384:
            raise ValueError("MG92_ORIGINAL_STEP_CAP")
        pair=row["before_sha"]+":"+str(action)
        if row["before_sha"]==row["after_sha"]:
            if pair not in self.failed and len(self.failed)>=MAX_PAIRS:
                raise ValueError("MG92_PUBLIC_PAIR_CAP")
            self.failed[pair]=self.failed.get(pair,0)+1
        self.streak=min(384,self.streak+1) if action==self.last_action else 1
        self.last_action=action
        self.feedback_samples+=1
        # Parent changes only previous-own-action context, never the
        # saved teacher-generated prototypes or selected reward weights.
        self.parent.observe_selected(adapter,before,after)
        self._valid()

    def checkpoint(self):
        self._valid()
        state={"schema":SCHEMA,"parent":self.parent.checkpoint().decode(),
               "failed":self.failed,"last_action":self.last_action,
               "streak":self.streak,"feedback_samples":self.feedback_samples}
        wire=canonical({"state":state,
                        "sha256":hashlib.sha256(canonical(state)).hexdigest()})
        if len(wire)>MAX_BYTES:
            raise ValueError("MG92_CHECKPOINT_CAP")
        return wire

    @classmethod
    def restore(cls,wire):
        try:
            if type(wire) is not bytes or not 0<len(wire)<=MAX_BYTES:
                raise ValueError("MG92_COLD_BYTES")
            data=json.loads(wire)
            if type(data) is not dict or set(data)!={"state","sha256"}:
                raise ValueError("MG92_COLD_ENVELOPE")
            state=data["state"]
            if (type(state) is not dict
                or set(state)!={"schema","parent","failed","last_action",
                                  "streak","feedback_samples"}
                or state["schema"]!=SCHEMA or type(state["parent"]) is not str
                or hashlib.sha256(canonical(state)).hexdigest()!=data["sha256"]):
                raise ValueError("MG92_COLD_SOURCE_DIGEST")
            obj=cls(PublicRewardPrototypes.restore(state["parent"].encode()))
            obj.failed=state["failed"]
            obj.last_action=state["last_action"]
            obj.streak=state["streak"]
            obj.feedback_samples=state["feedback_samples"]
            obj._valid()
            if obj.checkpoint()!=wire:
                raise ValueError("MG92_NONCANONICAL_COLD")
            return obj
        except (ValueError,TypeError,KeyError,UnicodeError,AttributeError) as e:
            raise ValueError("MG92_UNTRUSTED_COLD_SOURCE_FEEDBACK") from e
