"""R20 local-cell state-exact, source-selected reward gating.

Never use R18's mission-global action preference. R17 native successor
selection is retained whenever no exact original state/action reward exists.
"""
import hashlib
from research.native.itd02.r10.public_adapter import canonical,digest
from research.native.itd02.r18.mission_cells import (
    MissionCells,OriginalMissionAdapter,projected
)

SCHEMA="yggdrasil.itd02.r20.original-exact-public-reward.v1"
MAX_SAMPLES=4096
MAX_CONTEXTS=4096
MAX_CHECKPOINT=3000000

def empty():
    return [{"count":0,"positive":0} for _ in range(7)]

class StateCreditCells:
    def __init__(self,parent=None):
        self.parent=MissionCells() if parent is None else parent
        if type(self.parent)is not MissionCells:
            raise ValueError("R20_WRONG_NATIVE_PARENT")
        self.states={}
    @property
    def samples(self):
        return self.parent.samples
    def _valid(self):
        if (type(self.states)is not dict or len(self.states)>MAX_CONTEXTS
            or self.samples>MAX_SAMPLES):
            raise ValueError("R20_STATE_SOURCE_BOUND")
        count=0
        for k,row in self.states.items():
            if (type(k)is not str or len(k)!=64 or
                any(c not in "0123456789abcdef" for c in k)
                or type(row)is not list or len(row)!=7):
                raise ValueError("R20_INVALID_CONTEXT")
            for v in row:
                if (type(v)is not dict or set(v)!={"count","positive"}
                    or type(v["count"])is not int
                    or type(v["positive"])is not int
                    or v["positive"]<0 or v["count"]<v["positive"]):
                    raise ValueError("R20_INVALID_SELECTED_CREDIT")
                count+=v["count"]
        if count!=self.samples:raise ValueError("R20_PARENT_SOURCE_COUNT_DRIFT")
    def start_session(self,adapter,name,live=False):
        self._valid()
        return self.parent.start_session(adapter,name,live=live)
    def choose(self,before):
        self._valid()
        projected_public=projected(before)
        key=digest(before)
        # Parent R18 has global positive action override; deliberately bypass.
        baseline=self.parent.parent.choose(projected_public)
        high=0;chosen=None
        for a,stat in enumerate(self.states.get(key,empty())):
            if not stat["positive"]:continue
            confidence=4096*stat["positive"]//(stat["count"]+64)
            if confidence>high:
                high=confidence
                chosen=a
        if chosen is not None:
            return {"schema":SCHEMA,"action":chosen,
                    "status":"SELECT_NATIVE_EXACT_PUBLIC_REWARDED_SOURCE",
                    "external_fallback":False}
        return {"schema":SCHEMA,"action":baseline["action"],
                "status":baseline["status"],"external_fallback":False}
    def learn_selected(self,adapter,before,after):
        self._valid()
        projected(before);projected(after)
        if (type(adapter)is not OriginalMissionAdapter or
            adapter.pending is not None or adapter.current!=after or
            not adapter.ledger or before["mission"]!=after["mission"]):
            raise ValueError("R20_UNAUTHENTICATED_SELECTED_SOURCE")
        event=adapter.ledger[-1]
        key=digest(before);successor=digest(after)
        if (event["before_sha"]!=key or event["after_sha"]!=successor
            or type(event["action"])is not int or event["action"] not in range(7)):
            raise ValueError("R20_SOURCE_EVENT_DIGEST_DRIFT")
        if (self.samples>=MAX_SAMPLES or
            key not in self.states and len(self.states)>=MAX_CONTEXTS):
            raise ValueError("R20_SOURCE_CONTEXT_BUDGET")
        result=self.parent.learn_selected(adapter,before,after)
        values=self.states.setdefault(key,empty())
        stat=values[event["action"]]
        stat["count"]+=1
        if event["reward"]>0 and event["terminal"] and key!=successor:
            stat["positive"]+=1
        self._valid()
        return result
