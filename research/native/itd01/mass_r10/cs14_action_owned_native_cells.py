"""CS14: new action-owned extension using the genuine unmodified R7 LocalCell.

Explicit observed chosen-action ownership, delayed completed PUBLIC source
reward/next-state, strictly local reward/transition traces and cold persistence.
Original R7 LocalCell source is reused, NOT modified or copied.
"""
from __future__ import annotations
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"r7"))
from native_cells import LocalCell

ORIGINAL_LOCAL_CELL_SOURCE_GIT_BLOB="4c492a494ac5b25d5e9c49b98185be6a2c966b2f"
CHECKPOINT_SCHEMA="ygg.cs14.original_action_owned_localcells.public.v1"
def valid_bit(v):
    if type(v) is not int or v not in (0,1):
        raise ValueError("CS14_ACTION_OWNERSHIP_EXPECTS_EXACT_PUBLIC_BIT")
    return v

class ActionOwnedNativeCells:
    def __init__(self):
        # Each source public (state, chosen action) owns its own two genuine
        # R7 local cells: completed Y reward and source-returned next S.
        self.buckets={(s,a):{
            "reward":LocalCell(),
            "next_state":LocalCell(),
            "count":0}
            for s in (0,1) for a in (0,1)}
        self.completed_feedback_updates=0
    def learn_completed_public_consequence(self,public_state,chosen_action,
                                           public_reward,returned_next_state,delay_steps):
        s=valid_bit(public_state);a=valid_bit(chosen_action)
        y=valid_bit(public_reward);ns=valid_bit(returned_next_state)
        if type(delay_steps) is not int or delay_steps<2:
            raise ValueError("CS14_EARLY_OR_ACTIONLESS_FEEDBACK_DENIED")
        owned=self.buckets[(s,a)]
        owned["reward"].feel(True,bool(y))
        owned["next_state"].feel(True,bool(ns))
        owned["count"]+=1
        self.completed_feedback_updates+=1
    def _signed(self,s,a,channel):
        b=self.buckets[(valid_bit(s),valid_bit(a))]
        n=b["count"]
        if n==0:return 0.0
        cell=b[channel]
        return max(-1.,min(1.,(.75*cell.fast+.25*cell.slow)/n))
    def choose(self,public_state):
        s=valid_bit(public_state)
        return int(self._signed(s,1,"reward")>self._signed(s,0,"reward"))
    def predict_reward(self,s,a):
        return .5*(1.+self._signed(s,a,"reward"))
    def predict_next(self,s,a):
        return .5*(1.+self._signed(s,a,"next_state"))
    def state(self):
        return {
            "schema":CHECKPOINT_SCHEMA,
            "source_native_r7_localcell_blob":ORIGINAL_LOCAL_CELL_SOURCE_GIT_BLOB,
            "buckets":{str(s)+":"+str(a):{
                "reward":asdict(self.buckets[(s,a)]["reward"]),
                "next_state":asdict(self.buckets[(s,a)]["next_state"]),
                "count":self.buckets[(s,a)]["count"]}
                for s in (0,1) for a in (0,1)},
            "completed_feedback_updates":self.completed_feedback_updates,
            "source_action_ownership_explicit":True,
        }
    def checkpoint(self):
        data=self.state()
        payload=json.dumps(data,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
        checksum=hashlib.sha256(payload).hexdigest()
        result=json.dumps({"payload":data,"sha256":checksum},sort_keys=True,
                          separators=(",",":"),allow_nan=False).encode()
        if len(result)>32768:
            raise ValueError("CS14_NATIVE_PERSISTENT_STATE_OVER_CAP")
        return result
    @classmethod
    def restore(cls,raw):
        if type(raw) is not bytes or not (0<len(raw)<=32768):
            raise ValueError("CS14_NATIVE_CHECKPOINT_BYTES_INVALID")
        try:
            obj=json.loads(raw)
            if type(obj) is not dict or set(obj)!={"payload","sha256"}:
                raise ValueError("CS14_NATIVE_CHECKPOINT_FIELDS_INVALID")
            d=obj["payload"]
            payload=json.dumps(d,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
            if hashlib.sha256(payload).hexdigest()!=obj["sha256"]:
                raise ValueError("CS14_NATIVE_CHECKPOINT_HASH_INVALID")
            if (d["schema"]!=CHECKPOINT_SCHEMA or
                d["source_native_r7_localcell_blob"]!=ORIGINAL_LOCAL_CELL_SOURCE_GIT_BLOB or
                d["source_action_ownership_explicit"] is not True or
                set(d["buckets"])==set() or
                set(d["buckets"])!={"0:0","0:1","1:0","1:1"}):
                raise ValueError("CS14_NATIVE_CHECKPOINT_SCHEMA_INVALID")
            model=cls()
            total=0
            for s in (0,1):
                for a in (0,1):
                    x=d["buckets"][str(s)+":"+str(a)]
                    if set(x)!={"reward","next_state","count"} or
                       type(x["count"]) is not int or x["count"]<0:
                        raise ValueError("CS14_NATIVE_BUCKET_INVALID")
                    for field in ("reward","next_state"):
                        vals=x[field]
                        if (set(vals)!={"fast","slow","updates"} or
                            type(vals["updates"]) is not int or vals["updates"]!=x["count"] or
                            type(vals["fast"]) is not int or abs(vals["fast"])>512 or
                            type(vals["slow"]) not in (int,float)):
                            raise ValueError("CS14_NATIVE_CELL_STATE_INVALID")
                        model.buckets[(s,a)][field]=LocalCell(**vals)
                    model.buckets[(s,a)]["count"]=x["count"]
                    total+=x["count"]
            if type(d["completed_feedback_updates"]) is not int or total!=d["completed_feedback_updates"]:
                raise ValueError("CS14_NATIVE_PUBLIC_FEEDBACK_COUNT_MISMATCH")
            model.completed_feedback_updates=total
            if model.checkpoint()!=raw:
                raise ValueError("CS14_NATIVE_NONCANONICAL_RESTORE")
            return model
        except (KeyError,TypeError,IndexError) as e:
            raise ValueError("CS14_NATIVE_CHECKPOINT_INVALID") from e
