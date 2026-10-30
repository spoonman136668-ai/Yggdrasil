"""MG91 separately implemented conventional sparse linear supervised action value.

Independent of native_prototypes.py, trained on the *same* source-selected
successful original Farama teacher demonstrations and original reward-to-go.
Features represent raw public pixels, mission and own previous action.
Not a model-based/Bayesian scientific acceptance comparator.
"""
from __future__ import annotations
import hashlib
import json
import math
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter,original_public
from research.native.itd02.r10.public_adapter import canonical,digest

SCHEMA="yggdrasil.itd02.mg91.independent-public-linear-control.v1"
MAX_FRAMES=4608
MAX_WEIGHTS=120000
MAX_BYTES=12000000

def _features(frame,previous):
    original_public(frame)
    img=frame["image"]
    ids={ "mission:"+hashlib.sha256(frame["mission"].encode()).hexdigest()[:16],
          "direction:"+str(frame["direction"]),
          "prev:"+str(previous),
          "front:"+",".join(map(str,img[3][5])) }
    for x in range(6):
        for y in range(6):
            cells=[img[x][y],img[x+1][y],img[x][y+1],img[x+1][y+1]]
            if any(t[0]==0 for t in cells):
                continue
            if len({tuple(t) for t in cells})<2:
                continue
            ids.add("appearance:"+hashlib.sha256(canonical(cells)).hexdigest()[:16])
    return sorted(ids)

class IndependentLinearControl:
    def __init__(self):
        self.weights=[{} for _ in range(7)]
        self.prev=-1
        self.data_sha=None
        self.training_count=0

    def fit(self,episodes):
        if self.data_sha is not None or self.training_count:
            raise ValueError("MG91_LINEAR_FROZEN_AFTER_FIT")
        if type(episodes) is not list or not 0<len(episodes)<=12:
            raise ValueError("MG91_LINEAR_ORIGINAL_SUCCESS_DATA_REQUIRED")
        self.data_sha=hashlib.sha256(canonical(episodes)).hexdigest()
        samples=[]
        for ep in episodes:
            if (type(ep) is not dict or set(ep)!={"seed","success","steps"}
                or type(ep["seed"]) is not int or ep["success"] is not True
                or type(ep["steps"]) is not list or not 0<len(ep["steps"])<=384
                or ep["steps"][-1]["reward"]<=0 or not ep["steps"][-1]["terminated"]):
                raise ValueError("MG91_LINEAR_FALSE_POSITIVE_DEMONSTRATION")
            future=0
            returns=[]
            for step in reversed(ep["steps"]):
                if (type(step) is not dict
                    or set(step)!={"before","before_sha","after_sha","action","reward","terminated"}
                    or type(step["action"]) is not int or step["action"] not in range(7)
                    or type(step["reward"]) not in (int,float) or not math.isfinite(step["reward"])
                    or not 0<=step["reward"]<=1
                    or digest(step["before"])!=step["before_sha"]
                    or type(step["after_sha"]) is not str or len(step["after_sha"])!=64):
                    raise ValueError("MG91_LINEAR_ORIGINAL_LEDGER_INVALID")
                original_public(step["before"])
                future=min(1000,round(step["reward"]*1000)+970*future//1000)
                returns.append(future)
            prev=-1
            for step,value in zip(ep["steps"],reversed(returns)):
                samples.append((_features(step["before"],prev),step["action"],value))
                prev=step["action"]
        if not 0<len(samples)<=MAX_FRAMES:
            raise ValueError("MG91_LINEAR_SOURCE_TRAIN_CAP")
        self.training_count=len(samples)
        # Fixed three deterministic full passes. Error is source-real
        # discounted terminal reward for selected actions; other actions
        # are supervised zero for this actual demonstration state.
        for _ in range(3):
            for features,label,value in samples:
                count=len(features)
                for action in range(7):
                    model=self.weights[action]
                    predicted=sum(model.get(f,0) for f in features)//count
                    target=value if action==label else 0
                    err=target-predicted
                    delta=err//64 if err>=0 else -((-err)//64)
                    if delta:
                        for feature in features:
                            model[feature]=max(-1000,min(1000,model.get(feature,0)+delta))
        self._valid()

    def _valid(self):
        if (type(self.weights) is not list or len(self.weights)!=7
            or type(self.data_sha) is not str or len(self.data_sha)!=64
            or type(self.training_count) is not int or not 0<self.training_count<=MAX_FRAMES
            or type(self.prev) is not int or self.prev not in range(-1,7)):
            raise ValueError("MG91_LINEAR_INVALID_OR_UNTRAINED")
        total=0
        for row in self.weights:
            if type(row) is not dict:
                raise ValueError("MG91_LINEAR_WEIGHTS_INVALID")
            total+=len(row)
            for k,v in row.items():
                if (type(k) is not str or not 0<len(k)<=64
                    or type(v) is not int or not -1000<=v<=1000):
                    raise ValueError("MG91_LINEAR_WEIGHT_CORRUPTION")
        if total>MAX_WEIGHTS:
            raise ValueError("MG91_LINEAR_WEIGHTS_CAP")

    def start_session(self,adapter,name,live=False):
        if type(adapter) is not OriginalMissionAdapter or live:
            raise ValueError("MG91_LINEAR_PUBLIC_SOURCE_ONLY")
        original_public(adapter.current)
        self.prev=-1

    def choose(self,before):
        original_public(before)
        if self.data_sha is None:
            raise ValueError("MG91_LINEAR_NOT_TRAINED")
        features=_features(before,self.prev)
        values=[sum(self.weights[a].get(f,0) for f in features)
                for a in range(7)]
        action=max(range(7),key=lambda a:(values[a],-a))
        return {"schema":SCHEMA,"action":action,
                "status":"MG91_TRAINED_INDEPENDENT_LINEAR",
                "external_fallback":False}

    def observe_selected(self,adapter,before,after):
        original_public(before)
        original_public(after)
        if (type(adapter) is not OriginalMissionAdapter
            or adapter.current!=after or adapter.pending is not None
            or not adapter.ledger or before["mission"]!=after["mission"]):
            raise ValueError("MG91_LINEAR_NOT_SELECTED_ORIGINAL")
        row=adapter.ledger[-1]
        if (row["before_sha"]!=digest(before)
            or row["after_sha"]!=digest(after)
            or type(row["action"]) is not int or row["action"] not in range(7)):
            raise ValueError("MG91_LINEAR_SELECTED_DIGEST_MISMATCH")
        self.prev=row["action"]

    def checkpoint(self):
        self._valid()
        state={"schema":SCHEMA,"weights":self.weights,"prev":self.prev,
               "data_sha":self.data_sha,"training_count":self.training_count}
        raw=canonical({"state":state,"sha256":hashlib.sha256(canonical(state)).hexdigest()})
        if len(raw)>MAX_BYTES:
            raise ValueError("MG91_LINEAR_COLD_BYTES_CAP")
        return raw

    @classmethod
    def restore(cls,raw):
        try:
            if type(raw) is not bytes or not 0<len(raw)<=MAX_BYTES:
                raise ValueError("MG91_LINEAR_INVALID_BYTES")
            doc=json.loads(raw)
            if type(doc) is not dict or set(doc)!={"state","sha256"}:
                raise ValueError("MG91_LINEAR_COLD_ENVELOPE")
            s=doc["state"]
            if (type(s) is not dict or
                set(s)!={"schema","weights","prev","data_sha","training_count"}
                or s["schema"]!=SCHEMA or
                hashlib.sha256(canonical(s)).hexdigest()!=doc["sha256"]):
                raise ValueError("MG91_LINEAR_COLD_DIGEST")
            obj=cls()
            obj.weights=s["weights"]
            obj.prev=s["prev"]
            obj.data_sha=s["data_sha"]
            obj.training_count=s["training_count"]
            obj._valid()
            if obj.checkpoint()!=raw:
                raise ValueError("MG91_LINEAR_NONCANONICAL")
            return obj
        except (ValueError,TypeError,KeyError,AttributeError,UnicodeError) as ex:
            raise ValueError("MG91_LINEAR_UNTRUSTED_CHECKPOINT") from ex
