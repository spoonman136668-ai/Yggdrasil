"""R14: bounded source-public temporal transition memory (opt-in development).

This is a readout alongside unchanged R11 local cells and R13 action policy.
Only ACTUAL selected R10 public consequences may update the per-episode ring.
No global pose, map, other actor state, prewritten DoorKey solution or oracle.
"""
from __future__ import annotations

import hashlib
import json

from research.native.itd02.r10.public_adapter import (
    canonical, digest, public_observation
)
from research.native.itd02.r13.explore_choice import propose_native_action

SCHEMA="yggdrasil.itd02.r14.source-public-temporal-loop-memory.v1"
MAX_STEPS=192
MAX_BYTES=120000

class TemporalCells:
    def __init__(self):
        self.visits={}
        self.edges={}
        self.seen={}
        self.steps=0

    def decide(self,local,observation):
        public=public_observation(observation)
        parent=propose_native_action(local,public)
        base=parent["action"]
        if type(base)is not int or base not in range(7):
            raise ValueError("R14_PARENT_NOT_NATIVE")
        before=digest(public)
        counts=self.visits.get(before,[0]*7)
        successor=self.edges.get(before,{})
        scores=[]
        for action in range(7):
            known=successor.get(str(action))
            score=(4*int(action==base) - 3*counts[action]
                   -2*int(known==before and known is not None)
                   -min(2,self.seen.get(known,0)) if known is not None else
                   4*int(action==base)-3*counts[action])
            scores.append(score)
        start=int(before[:2],16)%7
        score=max(scores)
        for advance in range(7):
            action=(start+advance)%7
            if scores[action]==score:
                return {"action":action,"status":"SELECT_NATIVE_PUBLIC_TEMPORAL_ACTION",
                        "parent_action":base,"source_public_sha256":before,
                        "actual_selected_prior_local_count":counts[action],
                        "score":score,"source_only":True}
        raise ValueError("R14_UNREACHABLE_NATIVE_SELECT")

    def learn_selected(self,before,action,after,event):
        b=public_observation(before)
        a=public_observation(after)
        if (type(action)is not int or not 0<=action<=6 or type(event)is not dict
            or self.steps>=MAX_STEPS):
            raise ValueError("R14_INVALID_ACTUAL_SELECTED_EVENT")
        old,new=digest(b),digest(a)
        if (event.get("before_public_sha256")!=old
            or event.get("after_public_sha256")!=new
            or event.get("action")!=action):
            raise ValueError("R14_NOT_ORIGINAL_R10_SELECTED_EVENT")
        row=self.visits.get(old,[0]*7)[:]
        row[action]+=1
        edge=dict(self.edges.get(old,{}))
        edge[str(action)]=new
        if len(self.visits)>=MAX_STEPS and old not in self.visits:
            raise ValueError("R14_PUBLIC_EPISODE_MEMORY_BUDGET")
        self.visits[old]=row
        self.edges[old]=edge
        self.seen[new]=self.seen.get(new,0)+1
        self.steps+=1

    def checkpoint(self):
        state={"schema":SCHEMA,"visits":self.visits,"edges":self.edges,
               "seen":self.seen,"steps":self.steps}
        raw=canonical(state)
        blob=canonical({"state":state,"sha256":hashlib.sha256(raw).hexdigest()})
        if len(blob)>MAX_BYTES:raise ValueError("R14_CHECKPOINT_BYTES")
        return blob

    @classmethod
    def restore(cls,raw):
        if type(raw)is not bytes or not 0<len(raw)<=MAX_BYTES:
            raise ValueError("R14_UNTRUSTED_CHECKPOINT_SIZE")
        try:
            env=json.loads(raw)
            if type(env)is not dict or set(env)!={"state","sha256"}:
                raise ValueError("R14_ENVELOPE")
            state=env["state"]
            if (type(state)is not dict or
                set(state)!={"schema","visits","edges","seen","steps"} or
                state["schema"]!=SCHEMA or
                hashlib.sha256(canonical(state)).hexdigest()!=env["sha256"]):
                raise ValueError("R14_BAD_SHA_OR_SCHEMA")
            n=state["steps"]
            if type(n)is not int or not 0<=n<=MAX_STEPS:
                raise ValueError("R14_BAD_EPISODE_LENGTH")
            visits=state["visits"]
            edges=state["edges"]
            seen=state["seen"]
            if (type(visits)is not dict or type(edges)is not dict or
                type(seen)is not dict or set(edges)!=set(visits) or
                len(visits)>n or len(seen)>n):
                raise ValueError("R14_BAD_COUNTS")
            def sha_key(v):
                return type(v)is str and len(v)==64 and all(c in "0123456789abcdef" for c in v)
            if any(not sha_key(k) or type(row)is not list or len(row)!=7 or
                   any(type(a)is not int or not 0<=a<=MAX_STEPS for a in row)
                   for k,row in visits.items()):
                raise ValueError("R14_BAD_LOCAL_CONTEXT")
            if sum(sum(row) for row in visits.values())!=n:
                raise ValueError("R14_FAKE_PUBLIC_SELECTED_HISTORY")
            if (any(not sha_key(k) or type(v)is not int or not 1<=v<=n
                    for k,v in seen.items()) or sum(seen.values())!=n):
                raise ValueError("R14_BAD_SUCCESSOR_VISITS")
            if any(type(row)is not dict or
                   any(type(a)is not str or a not in tuple(map(str,range(7)))
                       or not sha_key(s) for a,s in row.items())
                   for row in edges.values()):
                raise ValueError("R14_BAD_TRANSITIONS")
            out=cls()
            out.visits=visits
            out.edges=edges
            out.seen=seen
            out.steps=n
            if out.checkpoint()!=raw:raise ValueError("R14_NONCANONICAL")
            return out
        except (TypeError,KeyError,ValueError,OverflowError) as exc:
            raise ValueError("R14_UNTRUSTED_SOURCE_PUBLIC_CHECKPOINT") from exc
