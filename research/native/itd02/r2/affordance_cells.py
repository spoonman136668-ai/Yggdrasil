"""ITD-02 R2 independent Yggdrasil local inhibitory affordance learner.

Only learned from real public chosen-action non-movement, not a hard-coded
blocked-front rule or a 3D map/planner. Original R1 cells remain untouched.
"""
import copy
import hashlib
import json
import math
from research.native.itd02.r1.native_policy import GridColony, PublicGrid, canonical,features
SCHEMA="yggdrasil.itd02.r2.local-forward-inhibition.v1"
class AffordanceColony:
    def __init__(self):
        self.core=GridColony()
        self.blocked_fast=0.0
        self.blocked_slow=0.0
        self.blocked_samples=0
    def _valid(self):
        return (math.isfinite(self.blocked_fast) and math.isfinite(self.blocked_slow)
          and 0<=self.blocked_fast<=8 and 0<=self.blocked_slow<=8
          and type(self.blocked_samples) is int and 0<=self.blocked_samples<2**63)
    def scores(self,s):
        if not self._valid():raise ValueError("Y_R2_LOCAL_STATE_CORRUPTED")
        features(s)
        v=[self.core.score(s,a) for a in (0,1,2)]
        if s.front_blocked and self.blocked_samples>0:
            v[2]-=.75*self.blocked_fast+.25*self.blocked_slow
        return v
    def choose(self,s):
        scores=self.scores(s)
        return max((0,1,2),key=lambda a:(scores[a],-a))
    def observe(self,before,action,after,reward,terminal):
        if not self._valid():raise ValueError("Y_R2_LOCAL_STATE_CORRUPTED")
        if self.blocked_samples>=2**63-2:raise ValueError("Y_R2_SATURATED_LOCAL_STATE")
        # Atomic: original R1 input and selected-action update in local copy.
        nxt=copy.deepcopy(self)
        nxt.core.observe(before,action,after,reward,terminal)
        if action==2 and before.front_blocked:
            if before.x==after.x and before.y==after.y:
                nxt.blocked_fast=min(8.,.90*nxt.blocked_fast+1.25)
            else:
                nxt.blocked_fast=.90*nxt.blocked_fast
            nxt.blocked_slow=.95*nxt.blocked_slow+.05*nxt.blocked_fast
            nxt.blocked_samples+=1
        if not nxt._valid():raise ValueError("Y_R2_INVALID_NEW_LOCAL_STATE")
        self.core=nxt.core
        self.blocked_fast=nxt.blocked_fast
        self.blocked_slow=nxt.blocked_slow
        self.blocked_samples=nxt.blocked_samples
    def save(self):
        if not self._valid():raise ValueError("Y_R2_INVALID_LOCAL_STATE")
        p={"schema":SCHEMA,"r1":self.core.save().decode("utf-8"),
           "fast":self.blocked_fast,"slow":self.blocked_slow,
           "samples":self.blocked_samples}
        digest=hashlib.sha256(canonical(p)).hexdigest()
        return canonical({"payload":p,"sha256":digest})
    @classmethod
    def restore(cls,blob):
        if type(blob) is not bytes or not 0<len(blob)<=32768:
            raise ValueError("Y_R2_CHECKPOINT_SIZE")
        try:
            w=json.loads(blob)
            if set(w)!={"payload","sha256"}:raise ValueError("Y_R2_CHECKPOINT_ENVELOPE")
            p=w["payload"]
            if (set(p)!={"schema","r1","fast","slow","samples"}
               or p["schema"]!=SCHEMA
               or hashlib.sha256(canonical(p)).hexdigest()!=w["sha256"]):
                raise ValueError("Y_R2_CHECKPOINT_AUTHENTICATION")
            c=cls()
            c.core=GridColony.restore(p["r1"].encode("utf-8"))
            c.blocked_fast=p["fast"]
            c.blocked_slow=p["slow"]
            c.blocked_samples=p["samples"]
            if not c._valid():raise ValueError("Y_R2_CORRUPT_AFFORDANCE")
            return c
        except (KeyError,TypeError,OverflowError) as e:
            raise ValueError("Y_R2_CHECKPOINT_STRUCTURE") from e
