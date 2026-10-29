"""MG19 native local-cell selected source learner on exact genuine MiniGrid mission."""
from __future__ import annotations
import hashlib
import json
from research.native.itd02.r10.public_adapter import canonical,digest
from research.native.itd02.r20.state_credit_cells import StateCreditCells
from research.native.itd02.mg19.original_mission_cells import (
    SCHEMA,MAX_CONTEXTS,MAX_SAMPLES,MAX_CHECKPOINT,LEGACY,
    OriginalMissionAdapter,original_public,legacy_public,blank
)

class MissionCells:
    def __init__(self,parent=None):
        self.parent=StateCreditCells() if parent is None else parent
        if type(self.parent) is not StateCreditCells:
            raise ValueError("MG19_WRONG_NATIVE_R20_PARENT")
        self.contexts={}
        self.missions={}

    @property
    def samples(self):
        return self.parent.samples

    def _valid(self):
        if (type(self.contexts) is not dict or type(self.missions) is not dict
            or len(self.contexts)>MAX_CONTEXTS or self.samples>MAX_SAMPLES):
            raise ValueError("MG19_NATIVE_LOCAL_SOURCE_BOUNDS")
        count=0
        for key,row in self.contexts.items():
            if (type(key) is not str or len(key)!=64 or
                any(c not in "0123456789abcdef" for c in key) or
                type(row) is not list or len(row)!=7):
                raise ValueError("MG19_SOURCE_HASH_OR_LOCAL_CELL")
            for value in row:
                if (type(value) is not dict or set(value)!={"count","positive"}
                    or type(value["count"]) is not int or
                    type(value["positive"]) is not int or
                    value["count"]<0 or not 0<=value["positive"]<=value["count"]):
                    raise ValueError("MG19_UNTRUSTED_LOCAL_REWARD_CELL")
                count+=value["count"]
        from research.native.itd02.mg19.original_mission_cells import admitted
        for name,count_one in self.missions.items():
            if not admitted(name) or type(count_one) is not int or count_one<=0:
                raise ValueError("MG19_UNTRUSTED_MISSION_CUSTODY")
        if count!=self.samples or sum(self.missions.values())!=self.samples:
            raise ValueError("MG19_PARENT_LOCAL_COUNT_DRIFT")
        self.parent._valid()

    def start_session(self,adapter,name,live=False):
        self._valid()
        if type(adapter) is not OriginalMissionAdapter:
            raise ValueError("MG19_UNTRUSTED_MISSION_ADAPTER")
        self.parent.start_session(adapter.inner,name,live=live)

    def choose(self,before):
        self._valid()
        original_public(before)
        projected=legacy_public(before)
        if before["mission"] in LEGACY:
            return self.parent.choose(projected)
        # R20's original global-mission reward policy is bypassed on new missions.
        proposal=self.parent.parent.parent.choose(projected)
        state=digest(before)
        best=None
        high=0
        for action,row in enumerate(self.contexts.get(state,blank())):
            if row["positive"]==0:
                continue
            score=4096*row["positive"]//(row["count"]+64)
            if score>high:
                best=action
                high=score
        if best is not None:
            return {"schema":SCHEMA,"action":best,
                    "status":"MG19_NATIVE_EXACT_ORIGINAL_MISSION_STATE_REWARD",
                    "external_fallback":False}
        return {"schema":SCHEMA,"action":proposal["action"],
                "status":proposal["status"],"external_fallback":False}

    def learn_selected(self,adapter,before,after):
        self._valid()
        original_public(before)
        original_public(after)
        if (type(adapter) is not OriginalMissionAdapter or
            adapter.pending is not None or adapter.current!=after or
            not adapter.ledger or before["mission"]!=after["mission"] or
            adapter.events!=adapter.inner.events):
            raise ValueError("MG19_ORIGINAL_MISSION_SELECTED_CUSTODY")
        latest=adapter.ledger[-1]
        key=digest(before)
        successor=digest(after)
        if (latest["before_sha"]!=key or latest["after_sha"]!=successor
            or latest["mission"]!=before["mission"] or
            type(latest["action"]) is not int or
            latest["action"] not in range(7) or
            latest["action"]!=adapter.inner.ledger[-1]["action"]):
            raise ValueError("MG19_WRONG_GENUINE_ORIGINAL_SOURCE_ACTION")
        if (self.samples>=MAX_SAMPLES or
            key not in self.contexts and len(self.contexts)>=MAX_CONTEXTS):
            raise ValueError("MG19_SOURCE_LOCAL_CAPACITY")
        receipt=self.parent.learn_selected(
            adapter.inner,legacy_public(before),legacy_public(after))
        values=self.contexts.setdefault(key,blank())
        stat=values[latest["action"]]
        stat["count"]+=1
        if latest["reward"]>0 and latest["terminal"] and key!=successor:
            stat["positive"]+=1
        self.missions[before["mission"]]=self.missions.get(before["mission"],0)+1
        self._valid()
        return receipt

    def checkpoint(self):
        self._valid()
        state={"schema":SCHEMA,
               "parent":self.parent.checkpoint().decode("utf-8"),
               "contexts":self.contexts,"missions":self.missions}
        raw=canonical({"state":state,"sha256":hashlib.sha256(canonical(state)).hexdigest()})
        if len(raw)>MAX_CHECKPOINT:
            raise ValueError("MG19_LOCAL_CHECKPOINT_SIZE")
        return raw

    @classmethod
    def restore(cls,blob):
        try:
            if type(blob) is not bytes or not 0<len(blob)<=MAX_CHECKPOINT:
                raise ValueError("MG19_RESTORE_SIZE")
            wire=json.loads(blob)
            if type(wire) is not dict or set(wire)!={"state","sha256"}:
                raise ValueError("MG19_CHECKPOINT_FIELDS")
            state=wire["state"]
            if (type(state) is not dict or
                set(state)!={"schema","parent","contexts","missions"} or
                state["schema"]!=SCHEMA or
                hashlib.sha256(canonical(state)).hexdigest()!=wire["sha256"] or
                type(state["parent"]) is not str):
                raise ValueError("MG19_RESTORE_CHECKSUM")
            parent=StateCreditCells.restore(state["parent"].encode("utf-8"))
            result=cls(parent)
            result.contexts=state["contexts"]
            result.missions=state["missions"]
            result._valid()
            if result.checkpoint()!=blob:
                raise ValueError("MG19_RESTORE_NONCANONICAL")
            return result
        except (KeyError,TypeError,UnicodeError,AttributeError,ValueError) as exc:
            raise ValueError("MG19_UNTRUSTED_NATIVE_CHECKPOINT") from exc
