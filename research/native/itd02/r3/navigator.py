"""Yggdrasil R3: persistent local causal motor memory + bounded optimistic planning.

Original R2 fast/slow local-plasticity source is unmodified and retained.
Episode graph contains only outcomes of actions the agent ACTUALLY performed;
it never receives a hidden map, shortest-path expert or environment seed.
This is an engineered source-owned planning hypothesis, not novel cognition.
"""
from __future__ import annotations
from collections import Counter
import hashlib
import heapq
import json
import math
from research.native.itd02.r2.affordance_cells import AffordanceColony, PublicGrid
from research.native.itd02.r1.native_policy import canonical,features

SCHEMA="yggdrasil.itd02.r3.episodic-causal-goal-search.v1"
class Navigator:
    def __init__(self):
        self.core=AffordanceColony()
        self.motor={str(d):{} for d in range(4)}
        self.width=0;self.height=0
        self.blocked=set()
        self.open_edges=set()
        self.visits={}
        self.steps=0

    def reset_episode(self,width,height):
        if type(width)is not int or type(height)is not int or not (4<=width<=32 and 4<=height<=32):
            raise ValueError("Y_R3_PUBLIC_MAP_SHAPE_INVALID")
        self.width=width;self.height=height
        self.blocked=set();self.open_edges=set()
        self.visits={};self.steps=0

    def _valid(self):
        if self.width==0 and self.height==0:return True
        return 4<=self.width<=32 and 4<=self.height<=32 and self.steps>=0

    def _motor(self,dir):
        choices=self.motor[str(dir)]
        if not choices:return None
        key=max(sorted(choices),key=lambda k:choices[k])
        delta=tuple(map(int,key.split(",")))
        if len(delta)!=2 or sum(abs(a) for a in delta)!=1:return None
        return delta

    def choose(self,st):
        features(st)
        if not self._valid() or self.width==0:
            raise ValueError("Y_R3_EPISODE_NOT_INITIALIZED")
        if not (0<=st.x<self.width and 0<=st.y<self.height
          and 0<=st.goal_x<self.width and 0<=st.goal_y<self.height):
            raise ValueError("Y_R3_PUBLIC_COORDS_OUT_OF_BOUNDS")
        if (st.x,st.y)==(st.goal_x,st.goal_y):
            return self.core.choose(st)
        if any(self._motor(d) is None for d in range(4)):
            return self.core.choose(st)
        # A* over public grid coordinates + heading. Edges were either
        # experienced (free/blocked) or UNKNOWN. No hidden map access.
        start=(st.x,st.y,st.direction)
        goal=(st.goal_x,st.goal_y)
        queue=[(0.,0.,0,start,-1)]
        best={start:0.};serial=0
        while queue:
            _,cost,_,pose,first=heapq.heappop(queue)
            if cost>best.get(pose,float("inf"))+1e-9:continue
            x,y,d=pose
            if (x,y)==goal:
                return first if first>=0 else self.core.choose(st)
            for a in (2,0,1):
                if a==0: nxt=(x,y,(d-1)%4);inc=.35
                elif a==1:nxt=(x,y,(d+1)%4);inc=.35
                else:
                    edge=(x,y,d)
                    if edge in self.blocked:continue
                    dx,dy=self._motor(d)
                    nx,ny=x+dx,y+dy
                    if not (0<=nx<self.width and 0<=ny<self.height):continue
                    nxt=(nx,ny,d)
                    inc=1. if edge in self.open_edges else 1.35
                    inc+=.04*min(10,self.visits.get(nxt,0))
                val=cost+inc
                if val+1e-9<best.get(nxt,float("inf")):
                    best[nxt]=val
                    first_a=a if first<0 else first
                    heur=abs(nxt[0]-goal[0])+abs(nxt[1]-goal[1])
                    serial+=1
                    heapq.heappush(queue,(val+heur,val,serial,nxt,first_a))
        return self.core.choose(st)

    def observe(self,before,action,after,reward,terminal,learn_local):
        features(before);features(after)
        if (type(action)is not int or action not in (0,1,2)
          or type(learn_local)is not bool or
          type(reward) not in (int,float) or not math.isfinite(reward)
          or type(terminal)is not bool or not self._valid()
          or self.width==0 or self.steps>=10000):
            raise ValueError("Y_R3_PUBLIC_OUTCOME_INVALID")
        # Source validation is transactionally delegated to unchanged R2.
        import copy
        fresh=copy.deepcopy(self)
        if learn_local:fresh.core.observe(before,action,after,reward,terminal)
        if action==2:
            edge=(before.x,before.y,before.direction)
            dx,dy=after.x-before.x,after.y-before.y
            if abs(dx)+abs(dy)==1:
                fresh.open_edges.add(edge)
                fresh.blocked.discard(edge)
                if learn_local:
                    key=f"{dx},{dy}"
                    old=fresh.motor[str(before.direction)].get(key,0)
                    fresh.motor[str(before.direction)][key]=old+1
            elif dx==0 and dy==0:
                fresh.blocked.add(edge)
                fresh.open_edges.discard(edge)
            else:raise ValueError("Y_R3_NONCARDINAL_PUBLIC_EFFECT")
        elif (before.x,before.y)!=(after.x,after.y):
            raise ValueError("Y_R3_TURN_MOVED_WITHOUT_ACTION")
        nxt=(after.x,after.y,after.direction)
        fresh.visits[nxt]=fresh.visits.get(nxt,0)+1
        fresh.steps+=1
        self.__dict__.update(fresh.__dict__)

    def snapshot(self):
        if not self._valid():raise ValueError("Y_R3_CHECKPOINT_INVALID_STATE")
        data={"schema":SCHEMA,"core":self.core.save().decode("utf-8"),
          "motor":self.motor,"width":self.width,"height":self.height,
          "blocked":[list(x) for x in sorted(self.blocked)],
          "open_edges":[list(x) for x in sorted(self.open_edges)],
          "visits":[[list(k),v] for k,v in sorted(self.visits.items())],
          "steps":self.steps}
        raw=canonical(data)
        if len(raw)>262144:raise ValueError("Y_R3_CHECKPOINT_OVERSIZE")
        return canonical({"data":data,"sha256":hashlib.sha256(raw).hexdigest()})

    @classmethod
    def restore(cls,raw):
        if type(raw)is not bytes or not 0<len(raw)<=262144:
            raise ValueError("Y_R3_BAD_CHECKPOINT_SIZE")
        try:
            wire=json.loads(raw)
            if set(wire)!={"data","sha256"}:raise ValueError("Y_R3_BAD_ENVELOPE")
            data=wire["data"]
            if (data.get("schema")!=SCHEMA or
                hashlib.sha256(canonical(data)).hexdigest()!=wire["sha256"]):
                raise ValueError("Y_R3_CHECKPOINT_AUTH")
            obj=cls()
            obj.core=AffordanceColony.restore(data["core"].encode())
            motor=data["motor"]
            if set(motor)!={"0","1","2","3"}:raise ValueError("Y_R3_MOTOR_STRUCTURE")
            for direction,counts in motor.items():
                if type(counts)is not dict:raise ValueError("Y_R3_INVALID_MOTOR")
                for key,v in counts.items():
                    parts=key.split(",")
                    if (len(parts)!=2 or not all(a.lstrip("-").isdigit() for a in parts)
                        or sum(abs(int(a)) for a in parts)!=1
                        or type(v)is not int or v<0 or v>10**7):
                        raise ValueError("Y_R3_LEARNED_MOTOR_CORRUPTED")
            obj.motor=motor
            obj.width=data["width"];obj.height=data["height"]
            obj.blocked={tuple(x) for x in data["blocked"]}
            obj.open_edges={tuple(x) for x in data["open_edges"]}
            obj.visits={tuple(k):v for k,v in data["visits"]}
            obj.steps=data["steps"]
            if not obj._valid() or obj.steps>10000 or len(obj.blocked)>4096 or len(obj.visits)>4096:
                raise ValueError("Y_R3_RESTORED_WORLD_INVALID")
            return obj
        except (KeyError,TypeError,OverflowError,AttributeError) as e:
            raise ValueError("Y_R3_CHECKPOINT_STRUCTURE") from e
