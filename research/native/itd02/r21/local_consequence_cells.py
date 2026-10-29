"""R21 local source consequence generalization with unchanged R20 local cells.

No magic action code, route, objective, external action director or source
counterfactual. Only already selected actual public before/action/after.
"""
from __future__ import annotations
import hashlib,json
from research.native.itd02.r10.public_adapter import canonical
from research.native.itd02.r18.mission_cells import OriginalMissionAdapter,projected
from research.native.itd02.r20.state_credit_cells import StateCreditCells
SCHEMA="yggdrasil.itd02.r21.local-original-public-consequence.v1"
MAX_SAMPLES=4096
MAX_CONTEXTS=4096
MAX_CHECKPOINT=4000000

def context(original):
    p=projected(original)
    item={"mission":original["mission"],
          "visible":[p["image"][3][i] for i in (4,5,6)]}
    return hashlib.sha256(canonical(item)).hexdigest()

def blank():
    return [{"n":0,"changed":0,"no_effect":0} for _ in range(7)]

def score(stat):
    n=stat["n"]
    return 4096*(stat["changed"]-stat["no_effect"])//(n+64)

class LocalConsequenceCells:
    def __init__(self,parent=None):
        self.parent=StateCreditCells() if parent is None else parent
        if type(self.parent)is not StateCreditCells:
            raise ValueError("R21_WRONG_PARENT_ARCHITECTURE")
        self.local={}
    @property
    def samples(self):return self.parent.samples
    def _valid(self):
        if (type(self.local)is not dict or len(self.local)>MAX_CONTEXTS
             or self.samples>MAX_SAMPLES):
            raise ValueError("R21_LOCAL_SELECTED_BOUNDS")
        count=0
        for k,rows in self.local.items():
            if (type(k)is not str or len(k)!=64
                or any(ch not in "0123456789abcdef" for ch in k)
                or type(rows)is not list or len(rows)!=7):
                raise ValueError("R21_LOCAL_CONTEXT")
            for v in rows:
                if (type(v)is not dict or set(v)!={"n","changed","no_effect"}
                    or any(type(v[k])is not int for k in v)
                    or not (0<=v["changed"]<=v["n"] and 0<=v["no_effect"]<=v["n"])
                    or v["changed"]+v["no_effect"]>v["n"]):
                    raise ValueError("R21_LOCAL_OUTCOME_COUNTS")
                count+=v["n"]
        if count!=self.samples:raise ValueError("R21_SELECTED_SOURCE_COUNT_DRIFT")
    def start_session(self,adapter,name,live=False):
        self._valid()
        return self.parent.start_session(adapter,name,live=live)
    def choose(self,before):
        self._valid()
        key=context(before)
        proposal=self.parent.choose(before)
        baseline=proposal["action"]
        rows=self.local.get(key,blank())
        highest=score(rows[baseline])
        best=None
        for action,stat in enumerate(rows):
            if stat["changed"]<2:continue
            value=score(stat)
            if value>highest:
                best=action
                highest=value
        if best is not None:
            return {"schema":SCHEMA,"action":best,
                    "status":"SELECT_NATIVE_LOCAL_SELECTED_CAUSAL_EFFECT",
                    "external_fallback":False}
        return {"schema":SCHEMA,"action":baseline,
                "status":proposal["status"],"external_fallback":False}
    def learn_selected(self,adapter,before,after):
        self._valid()
        key=context(before);context(after)
        if (type(adapter)is not OriginalMissionAdapter or
            adapter.pending is not None or adapter.current!=after or
            not adapter.ledger or before["mission"]!=after["mission"]):
            raise ValueError("R21_SELECTED_SOURCE_MISSION_MISMATCH")
        event=adapter.ledger[-1]
        from research.native.itd02.r10.public_adapter import digest
        if (event["before_sha"]!=digest(before)
            or event["after_sha"]!=digest(after)
            or type(event["action"])is not int
            or event["action"] not in range(7)):
            raise ValueError("R21_SELECTED_ORIGINAL_PUBLIC_DIGEST_MISMATCH")
        if (self.samples>=MAX_SAMPLES or
            key not in self.local and len(self.local)>=MAX_CONTEXTS):
            raise ValueError("R21_SELECTED_SOURCE_BUDGET")
        result=self.parent.learn_selected(adapter,before,after)
        rows=self.local.setdefault(key,blank())
        stat=rows[event["action"]]
        stat["n"]+=1
        if before["direction"]==after["direction"]:
            if before["image"]!=after["image"]:stat["changed"]+=1
            else:stat["no_effect"]+=1
        self._valid()
        return result
    def checkpoint(self):
        from research.native.itd02.r21.checkpoint import checkpoint
        return checkpoint(self)
    @classmethod
    def restore(cls,blob):
        from research.native.itd02.r21.checkpoint import restore
        return restore(blob)
