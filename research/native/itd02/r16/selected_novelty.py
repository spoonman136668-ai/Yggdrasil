"""R16: opt-in native local-cell own-source-public episodic action novelty.

Keeps original R15/R11 selected credit unchanged. Only an actual publicly
observed source-selected before/action/after can update the local episode ring.
No map, route, prechosen DoorKey answer, or external stage objective.
"""
from __future__ import annotations
import hashlib
import json
from research.native.itd02.r10.public_adapter import canonical,digest,public_observation
from research.native.itd02.r15.continuity_cells import NativeContinuity

SCHEMA="yggdrasil.itd02.r16.public-selected-episodic-novelty.v1"
LIMIT=192
MAX_CHECKPOINT=1000000

class NativeNovelty:
    def __init__(self,inner=None):
        self.inner=NativeContinuity() if inner is None else inner
        if type(self.inner)is not NativeContinuity:raise ValueError("R16_UNTRUSTED_LOCAL_PARENT")
        self.count={}
        self.novel={}
        self.loops={}
        self.next={}
        self.seen={}
        self.steps=0
        self.live=False

    @property
    def samples(self):
        return self.inner.samples

    def start_session(self,adapter,name,live=False):
        if type(live)is not bool:raise ValueError("R16_BAD_SESSION_MODE")
        self.inner.start_session(adapter,name,live=live)
        self.count={};self.novel={};self.loops={};self.next={};self.seen={}
        self.steps=0;self.live=live

    def choose(self,before):
        if not self.live or self.steps>=LIMIT or self.inner.local.session is None:
            raise ValueError("R16_NOT_IN_LIVE_ORIGINAL_SOURCE_SESSION")
        source=public_observation(before)
        key=digest(source)
        row=self.count.get(key,{})
        shift=int(key[:2],16)%7
        for i in range(7):
            a=(shift+i)%7
            if row.get(str(a),0)==0:
                return {"action":a,"status":"SELECT_NATIVE_UNTRIED_PUBLIC_STATE_ACTION",
                    "external_fallback":False}
        scores={}
        for a in range(7):
            aid=str(a)
            dest=self.next.get(key,{}).get(aid)
            scores[a]=(4*self.novel.get(key,{}).get(aid,0)
                -3*row.get(aid,0)-2*self.loops.get(key,{}).get(aid,0)
                -min(2,self.seen.get(dest,0)) if dest is not None
                else -3*row.get(aid,0))
        high=max(scores.values())
        for i in range(7):
            a=(shift+i)%7
            if scores[a]==high:
                return {"action":a,"status":"SELECT_NATIVE_OBSERVED_PUBLIC_NOVELTY",
                    "external_fallback":False}
        raise ValueError("R16_NO_LOCAL_SELECTED_ACTION")

    def learn_selected(self,adapter,before,after):
        b=public_observation(before);a=public_observation(after)
        if self.live and self.steps>=LIMIT:raise ValueError("R16_PUBLIC_EPISODE_CAP")
        # Authoritative R11/R15 credit happens once BEFORE the local episode audit.
        result=self.inner.learn_selected(adapter,b,a)
        if self.live:
            event=adapter.ledger[-1]
            action=event["action"]
            if type(action)is not int or action not in range(7):
                raise ValueError("R16_ILLEGAL_ORIGINAL_SELECTED_ACTION")
            src=digest(b);dst=digest(a);key=str(action)
            self.count.setdefault(src,{})[key]=self.count.get(src,{}).get(key,0)+1
            if self.seen.get(dst,0)==0:
                self.novel.setdefault(src,{})[key]=self.novel.get(src,{}).get(key,0)+1
            if dst==src:
                self.loops.setdefault(src,{})[key]=self.loops.get(src,{}).get(key,0)+1
            self.next.setdefault(src,{})[key]=dst
            self.seen[dst]=self.seen.get(dst,0)+1
            self.steps+=1
        return result

    def _healthy(self):
        if (type(self.live)is not bool or type(self.steps)is not int or
            not 0<=self.steps<=LIMIT or len(self.count)>LIMIT or
            len(self.seen)>LIMIT):
            raise ValueError("R16_BAD_PUBLIC_SELECTED_LIMIT")
        if any(type(x)is not dict for x in (self.count,self.novel,self.loops,self.next,self.seen)):
            raise ValueError("R16_UNTRUSTED_MEMORY")
        def valid_key(k):
            return type(k)is str and len(k)==64 and all(x in "0123456789abcdef" for x in k)
        total=0
        for state,row in self.count.items():
            if not valid_key(state) or type(row)is not dict:raise ValueError("R16_CONTEXT")
            for act,n in row.items():
                if (act not in tuple(map(str,range(7))) or type(n)is not int
                    or n<1 or n>LIMIT):raise ValueError("R16_ACTION_COUNTER")
                if (self.novel.get(state,{}).get(act,0)>n or
                    self.loops.get(state,{}).get(act,0)>n or
                    not valid_key(self.next.get(state,{}).get(act))):
                    raise ValueError("R16_FALSE_EVENT")
                total+=n
        if total!=self.steps or sum(self.seen.values())!=self.steps:
            raise ValueError("R16_SOURCE_ACTION_COUNT_DRIFT")
        if any(not valid_key(k) or type(v)is not int or v<1 or v>LIMIT
               for k,v in self.seen.items()):
            raise ValueError("R16_NOT_REAL_SELECTED_SOURCE_SUCCESSORS")
        if any(set(self.novel.get(k,{}))-set(v) or set(self.loops.get(k,{}))-set(v)
               or set(self.next.get(k,{}))!=set(v) for k,v in self.count.items()):
            raise ValueError("R16_NO_SOURCE_SELECTED_EDGE")
        return True

    def checkpoint(self):
        self._healthy()
        state={"schema":SCHEMA,"inner":self.inner.checkpoint().decode("utf-8"),
          "count":self.count,"novel":self.novel,"loops":self.loops,"next":self.next,
          "seen":self.seen,"steps":self.steps,"live":self.live}
        data=canonical(state)
        outer=canonical({"state":state,"sha256":hashlib.sha256(data).hexdigest()})
        if len(outer)>MAX_CHECKPOINT:raise ValueError("R16_CHECKPOINT_BYTES")
        return outer

    @classmethod
    def restore(cls,blob):
        try:
            if type(blob)is not bytes or not 0<len(blob)<=MAX_CHECKPOINT:
                raise ValueError("R16_UNTRUSTED_CHECKPOINT_BYTES")
            env=json.loads(blob);state=env["state"]
            if (set(env)!={"state","sha256"} or
                set(state)!={"schema","inner","count","novel","loops","next","seen","steps","live"}
                or state["schema"]!=SCHEMA or
                hashlib.sha256(canonical(state)).hexdigest()!=env["sha256"]):
                raise ValueError("R16_CHECKPOINT_SCHEMA_OR_SHA")
            obj=cls(NativeContinuity.restore(state["inner"].encode("utf-8")))
            for field in ("count","novel","loops","next","seen","steps","live"):
                setattr(obj,field,state[field])
            obj._healthy()
            if obj.checkpoint()!=blob:raise ValueError("R16_NONCANONICAL_COLD_RESTORE")
            return obj
        except (ValueError,TypeError,AttributeError,KeyError,UnicodeDecodeError) as e:
            raise ValueError("R16_UNTRUSTED_SOURCE_SELECTED_MEMORY") from e
