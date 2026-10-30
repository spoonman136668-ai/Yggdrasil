"""MG91 teacher-conditioned associative public action values, NOT autonomous discovery.

Training labels are only source-selected original MG86 teacher actions in
original positive-terminal-reward DEV episodes. Public mission, direction,
visible image and previous own selected action; no object/action semantics,
hidden state, imitation at runtime, synthetic wins or transformer/tokens.
"""
from __future__ import annotations
import hashlib
import json
import math
from research.native.itd02.mg89.landmark_cells import patch_ids
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter,original_public
from research.native.itd02.r10.public_adapter import canonical,digest

SCHEMA="yggdrasil.itd02.mg91.native-public-reward-prototypes.v1"
MAX_FRAMES=4608
MAX_BYTES=12000000
DISCOUNT=970
K=8

def _features(frame):
    original_public(frame)
    # 64-bit visible appearance fingerprint is a bounded lossy engineered
    # 2x2-patch prior, not a learned world coordinate or task object label.
    return sorted(s[:16] for s in patch_ids(frame))

def _validated_episodes(episodes):
    if type(episodes) is not list or not 0<len(episodes)<=12:
        raise ValueError("MG91_NATIVE_NO_SOURCE_TEACHER_EPISODES")
    frames=0
    for episode in episodes:
        if (type(episode) is not dict or set(episode)!={"steps","success","seed"}
            or episode["success"] is not True or type(episode["seed"]) is not int
            or type(episode["steps"]) is not list
            or not 0<len(episode["steps"])<=384):
            raise ValueError("MG91_NATIVE_MUST_TRAIN_ON_ORIGINAL_SUCCESS")
        if episode["steps"][-1]["reward"]<=0 or not episode["steps"][-1]["terminated"]:
            raise ValueError("MG91_NATIVE_FALSE_TERMINAL_TASK_REWARD")
        frames+=len(episode["steps"])
        for step in episode["steps"]:
            if (type(step) is not dict or
                set(step)!={"before","before_sha","after_sha","action","reward","terminated"}
                or type(step["action"]) is not int or step["action"] not in range(7)
                or type(step["reward"]) not in (float,int)
                or not math.isfinite(step["reward"]) or not 0<=step["reward"]<=1
                or digest(step["before"])!=step["before_sha"]
                or type(step["after_sha"]) is not str or len(step["after_sha"])!=64
                or type(step["terminated"]) is not bool):
                raise ValueError("MG91_NATIVE_SOURCE_SELECTED_PROOF_INVALID")
            original_public(step["before"])
    if frames>MAX_FRAMES:
        raise ValueError("MG91_NATIVE_TRAIN_SAMPLE_CAP")

class PublicRewardPrototypes:
    def __init__(self):
        self.examples=[]
        self.data_sha=None
        self.prev=-1
        self.training_count=0

    def fit(self,episodes):
        if self.data_sha is not None:
            raise ValueError("MG91_NATIVE_TRAINING_ALREADY_SEALED")
        _validated_episodes(episodes)
        self.data_sha=hashlib.sha256(canonical(episodes)).hexdigest()
        for e in episodes:
            rtg=0
            previous=-1
            annotated=[]
            for step in reversed(e["steps"]):
                rtg=min(1000,round(1000*step["reward"])+DISCOUNT*rtg//1000)
                annotated.append(rtg)
            for step,value in zip(e["steps"],reversed(annotated)):
                f=step["before"]
                self.examples.append({"mission":f["mission"],"direction":f["direction"],
                   "front":list(f["image"][3][5]),"prev":previous,
                   "patch":_features(f),"action":step["action"],"value":value})
                previous=step["action"]
        self.training_count=len(self.examples)
        self._valid()

    def _valid(self):
        if (type(self.data_sha) is not str or len(self.data_sha)!=64
            or type(self.examples) is not list or not 0<len(self.examples)<=MAX_FRAMES
            or type(self.training_count) is not int or self.training_count!=len(self.examples)
            or type(self.prev) is not int or self.prev not in range(-1,7)):
            raise ValueError("MG91_NATIVE_UNTRAINED_OR_CORRUPT")
        for p in self.examples:
            if (type(p) is not dict or set(p)!={"mission","direction","front",
                      "prev","patch","action","value"}
                or type(p["mission"]) is not str or not p["mission"]
                or type(p["direction"]) is not int or p["direction"] not in range(4)
                or type(p["prev"]) is not int or p["prev"] not in range(-1,7)
                or type(p["action"]) is not int or p["action"] not in range(7)
                or type(p["value"]) is not int or not 0<=p["value"]<=1000
                or type(p["front"]) is not list or len(p["front"])!=3
                or type(p["patch"]) is not list or len(p["patch"])>36
                or any(type(s) is not str or len(s)!=16 for s in p["patch"])):
                raise ValueError("MG91_NATIVE_SOURCE_PROTOTYPE_BOUNDS")

    def start_session(self,adapter,name,live=False):
        if type(adapter) is not OriginalMissionAdapter or live:
            raise ValueError("MG91_NATIVE_PUBLIC_ORIGINAL_ONLY")
        original_public(adapter.current)
        self.prev=-1

    def choose(self,before):
        original_public(before)
        if not self.examples or self.data_sha is None:
            raise ValueError("MG91_NATIVE_UNTRAINED")
        features=set(_features(before))
        front=before["image"][3][5]
        matches=[]
        for i,p in enumerate(self.examples):
            overlap=len(features.intersection(p["patch"]))
            union=max(1,len(features.union(p["patch"])))
            sim=(200*int(p["mission"]==before["mission"])
                +100*int(p["direction"]==before["direction"])
                +100*int(p["front"]==front)
                +50*int(p["prev"]==self.prev)
                +400*overlap//union)
            matches.append((sim,-i,p["action"],p["value"]))
        top=sorted(matches,reverse=True)[:K]
        votes=[0]*7
        for similarity,_,a,value in top:
            votes[a]+=(1+similarity)*value
        action=max(range(7),key=lambda a:(votes[a],-a))
        return {"schema":SCHEMA,"action":action,
                "status":"MG91_TRAINED_PUBLIC_REWARD_PROTOTYPE",
                "external_fallback":False}

    def observe_selected(self,adapter,before,after):
        original_public(before)
        original_public(after)
        if (type(adapter) is not OriginalMissionAdapter
            or adapter.pending is not None or adapter.current!=after
            or not adapter.ledger or before["mission"]!=after["mission"]):
            raise ValueError("MG91_NATIVE_UNSELECTED_HELDOUT")
        row=adapter.ledger[-1]
        if (row["before_sha"]!=digest(before) or row["after_sha"]!=digest(after)
            or type(row["action"]) is not int or row["action"] not in range(7)):
            raise ValueError("MG91_NATIVE_HELDOUT_SELECTED_LEDGER")
        # Frozen learned action values: prior own selected action is allowed
        # public history; no heldout reward or hidden goal updates weights.
        self.prev=row["action"]

    def checkpoint(self):
        self._valid()
        state={"schema":SCHEMA,"examples":self.examples,
               "training_count":self.training_count,"data_sha":self.data_sha,
               "prev":self.prev}
        raw=canonical({"state":state,"sha256":hashlib.sha256(canonical(state)).hexdigest()})
        if len(raw)>MAX_BYTES:
            raise ValueError("MG91_NATIVE_CHECKPOINT_LIMIT")
        return raw

    @classmethod
    def restore(cls,raw):
        try:
            if type(raw) is not bytes or not 0<len(raw)<=MAX_BYTES:
                raise ValueError("MG91_NATIVE_BAD_BYTES")
            v=json.loads(raw)
            if type(v) is not dict or set(v)!={"state","sha256"}:
                raise ValueError("MG91_NATIVE_BAD_ENVELOPE")
            s=v["state"]
            if (type(s) is not dict or
                set(s)!={"schema","examples","training_count","data_sha","prev"}
                or s["schema"]!=SCHEMA or
                hashlib.sha256(canonical(s)).hexdigest()!=v["sha256"]):
                raise ValueError("MG91_NATIVE_COLD_DIGEST")
            p=cls()
            p.examples=s["examples"]
            p.training_count=s["training_count"]
            p.data_sha=s["data_sha"]
            p.prev=s["prev"]
            p._valid()
            if p.checkpoint()!=raw:
                raise ValueError("MG91_NATIVE_NONCANONICAL")
            return p
        except (ValueError,TypeError,KeyError,AttributeError,UnicodeError) as e:
            raise ValueError("MG91_NATIVE_CHECKPOINT_REJECT") from e
