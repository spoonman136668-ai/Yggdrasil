"""MG90 empirical selected-public relational graph with original-reward backup.

Observation node = mission, direction, visible patch-identity set (or source
public digest if patches absent). Neither keys, actions nor goals are decoded.
All graph edges are from actually selected original Farama action feedback.
"""
from __future__ import annotations
from collections import deque
import hashlib
import json
import math
from research.native.itd02.mg89.landmark_cells import LandmarkLinkCells,patch_ids
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter,original_public
from research.native.itd02.r10.public_adapter import canonical,digest

SCHEMA="yggdrasil.itd02.mg90.relational-frontier-original-reward.v1"
MAX_NODES=4096
MAX_EDGES=8192
MAX_SAMPLES=12000
MAX_BYTES=12000000
TRACE=32

def nodekey(public):
    original_public(public)
    landmarks=sorted(patch_ids(public))
    info={"mission":public["mission"],"direction":public["direction"],
          "landmarks":landmarks}
    if not landmarks:
        info["unseen_frame"]=digest(public)
    return hashlib.sha256(canonical(info)).hexdigest()

def newrow():
    return [{"count":0,"next":{},"q":0} for _ in range(7)]

def sha(s):
    return type(s) is str and len(s)==64 and all(c in "0123456789abcdef" for c in s)

class RelationalFrontierCells:
    def __init__(self,parent=None):
        self.parent=LandmarkLinkCells() if parent is None else parent
        if type(self.parent) is not LandmarkLinkCells:
            raise ValueError("MG90_NATIVE_LANDMARK_PARENT_REQUIRED")
        self.graph={}
        self.trace=[]
        self.frontier_routes=0

    @property
    def samples(self):
        return self.parent.samples

    def _valid(self):
        self.parent._valid()
        if (type(self.graph) is not dict or len(self.graph)>MAX_NODES
            or type(self.trace) is not list or len(self.trace)>TRACE
            or type(self.frontier_routes) is not int or
            not 0<=self.frontier_routes<=MAX_SAMPLES
            or self.samples>MAX_SAMPLES):
            raise ValueError("MG90_GRAPH_BOUNDS")
        samples=edges=0
        for ident,rows in self.graph.items():
            if not sha(ident) or type(rows) is not list or len(rows)!=7:
                raise ValueError("MG90_PUBLIC_RELATION_NODE_INVALID")
            for item in rows:
                if (type(item) is not dict or set(item)!={"count","next","q"}
                    or type(item["count"]) is not int or not 0<=item["count"]<=MAX_SAMPLES
                    or type(item["q"]) is not int or not 0<=item["q"]<=1000
                    or type(item["next"]) is not dict):
                    raise ValueError("MG90_PUBLIC_ACTION_VALUE_INVALID")
                if (any(not sha(k) or type(v) is not int or v<=0
                        for k,v in item["next"].items())
                    or sum(item["next"].values())!=item["count"]):
                    raise ValueError("MG90_REAL_SELECTED_EDGE_CONSERVATION")
                samples+=item["count"]
                edges+=len(item["next"])
        if samples!=self.samples or edges>MAX_EDGES:
            raise ValueError("MG90_NO_SYNTHETIC_EDGE_OR_ACTION")
        if any(type(t) is not list or len(t)!=2 or not sha(t[0])
               or type(t[1]) is not int or t[1] not in range(7)
               for t in self.trace):
            raise ValueError("MG90_EPISODE_TRACE_INVALID")

    def start_session(self,adapter,name,live=False):
        if type(adapter) is not OriginalMissionAdapter or live:
            raise ValueError("MG90_ORIGINAL_PUBLIC_SESSION_ONLY")
        self._valid()
        self.trace=[]
        return self.parent.start_session(adapter,name,live=False)

    def _motion(self,action):
        # Learned source-selected MG88 camera changes, no action semantics.
        event=self.parent.parent.events[action]
        observed=sum(n for k,n in event["shift"].items() if k!="0,0")
        return 100*observed//(1+event["count"])

    def _score(self,ident,action,untried=False):
        item=self.graph.get(ident,newrow())[action]
        repeated=item["next"].get(ident,0)
        bonus=(180 if untried else 0)
        return (bonus+self._motion(action)
                -50*repeated//(1+item["count"])
                +300*item["q"]//1000)

    def _route(self,initial):
        seen={initial}
        queue=deque([(initial,None)])
        while queue:
            node,first=queue.popleft()
            if node!=initial and (node not in self.graph or
                    any(item["count"]==0 for item in self.graph[node])):
                return first
            row=self.graph.get(node)
            if row is None:
                continue
            for a in range(7):
                for dest in sorted(row[a]["next"]):
                    if dest in seen:
                        continue
                    seen.add(dest)
                    queue.append((dest,a if first is None else first))
        return None

    def choose(self,before):
        original_public(before)
        self._valid()
        ident=nodekey(before)
        rows=self.graph.get(ident,newrow())
        untried=[a for a in range(7) if rows[a]["count"]==0]
        if untried:
            chosen=max(untried,key=lambda a:(self._score(ident,a,True),-a))
            status="MG90_RELATIONAL_SOURCE_FRONTIER_PROBE"
        else:
            route=self._route(ident)
            if route is not None:
                chosen=route
                status="MG90_SOURCE_OBSERVED_SHORTEST_FRONTIER_PATH"
            else:
                chosen=max(range(7),key=lambda a:(
                    self._score(ident,a)-200*rows[a]["count"],-a))
                status="MG90_SOURCE_GRAPH_LOCAL_ESCAPE"
        return {"schema":SCHEMA,"action":chosen,"status":status,
                "external_fallback":False}

    def learn_selected(self,adapter,before,after):
        self._valid()
        original_public(before)
        original_public(after)
        if (type(adapter) is not OriginalMissionAdapter or adapter.pending is not None
            or adapter.current!=after or not adapter.ledger
            or before["mission"]!=after["mission"]):
            raise ValueError("MG90_NOT_COMPLETED_SELECTED_ORIGINAL")
        row=adapter.ledger[-1]
        a=row.get("action")
        if (type(a) is not int or a not in range(7)
            or row["before_sha"]!=digest(before)
            or row["after_sha"]!=digest(after)):
            raise ValueError("MG90_SELECTED_PUBLIC_SOURCE_DRIFT")
        reward=row["reward"]
        if type(reward) not in (int,float) or not math.isfinite(float(reward)) or not 0<=reward<=1:
            raise ValueError("MG90_ORIGINAL_REWARD_INVALID")
        ident,dest=nodekey(before),nodekey(after)
        if (self.samples>=MAX_SAMPLES or
            ident not in self.graph and len(self.graph)>=MAX_NODES):
            raise ValueError("MG90_RELATIONAL_MEMORY_CAP")
        item=self.graph.get(ident,newrow())[a]
        edges=sum(len(i["next"]) for rows in self.graph.values() for i in rows)
        if dest not in item["next"] and edges>=MAX_EDGES:
            raise ValueError("MG90_SELECTED_EDGE_LIMIT")
        n=self.samples
        receipt=self.parent.learn_selected(adapter,before,after)
        if self.samples!=n+1:
            raise ValueError("MG90_PARENT_SELECTED_SAMPLE_DRIFT")
        selected=self.graph.setdefault(ident,newrow())[a]
        selected["count"]+=1
        selected["next"][dest]=selected["next"].get(dest,0)+1
        self.trace.append([ident,a])
        self.trace=self.trace[-TRACE:]
        if reward>0:
            value=round(float(reward)*1000)
            for past,a0 in reversed(self.trace):
                old=self.graph[past][a0]
                old["q"]=max(old["q"],min(1000,value))
                value=value*9//10
        self._valid()
        return receipt

    def checkpoint(self):
        self._valid()
        state={"schema":SCHEMA,"parent":self.parent.checkpoint().decode(),
               "graph":self.graph,"trace":self.trace,
               "frontier_routes":self.frontier_routes}
        blob=canonical({"state":state,"sha256":hashlib.sha256(canonical(state)).hexdigest()})
        if len(blob)>MAX_BYTES:
            raise ValueError("MG90_CHECKPOINT_SIZE")
        return blob

    @classmethod
    def restore(cls,raw):
        try:
            if type(raw) is not bytes or not 0<len(raw)<=MAX_BYTES:
                raise ValueError("MG90_COLD_BYTES")
            data=json.loads(raw)
            if type(data) is not dict or set(data)!={"state","sha256"}:
                raise ValueError("MG90_COLD_ENVELOPE")
            s=data["state"]
            if (type(s) is not dict or
                set(s)!={"schema","parent","graph","trace","frontier_routes"}
                or s["schema"]!=SCHEMA or type(s["parent"]) is not str
                or hashlib.sha256(canonical(s)).hexdigest()!=data["sha256"]):
                raise ValueError("MG90_COLD_SOURCE_DIGEST")
            obj=cls(LandmarkLinkCells.restore(s["parent"].encode()))
            obj.graph=s["graph"]
            obj.trace=s["trace"]
            obj.frontier_routes=s["frontier_routes"]
            obj._valid()
            if obj.checkpoint()!=raw:
                raise ValueError("MG90_COLD_NONCANONICAL")
            return obj
        except (ValueError,TypeError,KeyError,AttributeError,UnicodeError) as exc:
            raise ValueError("MG90_COLD_REJECT") from exc
