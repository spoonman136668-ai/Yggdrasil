"""MG85 hand-engineered conventional spatial planner POSITIVE CONTROL ONLY.

Uses public image/direction/mission + selected actions and source feedback.
Preprogrammed tile semantics, egocentric odometry, breadth-first paths and
mission target parsing are strong external inductive priors, NOT native learning.
No access to environment internals or hidden world coordinates.
"""
from __future__ import annotations
from collections import deque
import hashlib
import json
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter, original_public
from research.native.itd02.r10.public_adapter import canonical, digest

SCHEMA="yggdrasil.itd02.mg85.conventional-public-spatial-positive-control.v1"
FORWARD=((1,0),(0,1),(-1,0),(0,-1))
IDX={"red":0,"green":1,"blue":2,"purple":3,"yellow":4,"grey":5}
OBJ={"key":5,"ball":6,"box":7,"goal":8}
TRAVERSABLE=(1,3,8)
LIMIT=4096
MAX_BYTES=1000000

def key(p):
    return str(p[0])+","+str(p[1])

def pos(k):
    a,b=k.split(",")
    return int(a),int(b)

def walkable(tile):
    return tile[0] in TRAVERSABLE or (tile[0]==4 and tile[2]==0)

class PublicMapControl:
    def __init__(self):
        self.samples=0
        self.grid={}
        self.visited={}
        self.xy=(0,0)
        self.heading=0
        self.carrying=None
        self.opened=0
        self.episodes=0

    def _valid(self):
        if (type(self.samples) is not int or not 0<=self.samples<=LIMIT
            or type(self.episodes) is not int or self.episodes<0
            or type(self.heading) is not int or self.heading not in range(4)
            or type(self.grid) is not dict or len(self.grid)>LIMIT
            or type(self.visited) is not dict or len(self.visited)>LIMIT
            or type(self.xy) not in (tuple,list) or len(self.xy)!=2
            or any(type(n) is not int or abs(n)>512 for n in self.xy)
            or self.carrying not in (None,5,6,7)
            or type(self.opened) is not int or self.opened<0):
            raise ValueError("MG85_PUBLIC_CONVENTIONAL_BOUNDS")
        for k,t in self.grid.items():
            if (type(k) is not str or len(k)>12
                or type(t) is not list or len(t)!=3
                or any(type(n) is not int or not 0<=n<=255 for n in t)
                or abs(pos(k)[0])>512 or abs(pos(k)[1])>512):
                raise ValueError("MG85_PUBLIC_MAP_INVALID")
        for k,n in self.visited.items():
            if (type(k) is not str or len(k)>12
                or type(n) is not int or not 0<=n<=LIMIT):
                raise ValueError("MG85_PUBLIC_VISITS_INVALID")

    def start_session(self,adapter,name,live=False):
        self._valid()
        if type(adapter) is not OriginalMissionAdapter:
            raise ValueError("MG85_PUBLIC_ONLY_ADAPTER")
        frame=adapter.current
        original_public(frame)
        self.grid={}
        self.visited={}
        self.xy=(0,0)
        self.heading=frame["direction"]
        self.carrying=None
        self.opened=0
        self.episodes+=1
        self._observe(frame)

    def _observe(self,frame):
        original_public(frame)
        self.heading=frame["direction"]
        forward=FORWARD[self.heading]
        right=FORWARD[(self.heading+1)%4]
        for x,column in enumerate(frame["image"]):
            for y,tile in enumerate(column):
                if tile[0]==0: # original unseen, no inference
                    continue
                at=(self.xy[0]+(6-y)*forward[0]+(x-3)*right[0],
                    self.xy[1]+(6-y)*forward[1]+(x-3)*right[1])
                self.grid[key(at)]=list(tile)
        self.visited.setdefault(key(self.xy),0)
        if len(self.grid)>LIMIT:
            raise ValueError("MG85_MAP_SOURCE_CAP")

    def _neighbors(self,pt):
        for direction,(dx,dy) in enumerate(FORWARD):
            yield direction,(pt[0]+dx,pt[1]+dy)

    def _reachable(self):
        # Complete shortest-path witness on known source-public traversable
        # tiles only. No hidden grid query or inferred target coordinates.
        root=tuple(self.xy)
        parent={root:None}
        q=deque([root])
        while q:
            here=q.popleft()
            for direction,there in self._neighbors(here):
                if there in parent:
                    continue
                tile=self.grid.get(key(there))
                if tile is None or not walkable(tile):
                    continue
                parent[there]=(here,direction)
                q.append(there)
        return parent

    def _first_step(self,parent,target):
        current=tuple(target)
        if current==tuple(self.xy):
            return None
        while parent[current][0]!=tuple(self.xy):
            current=parent[current][0]
        return parent[current][1]

    def _action_for_dir(self,d):
        offset=(d-self.heading)%4
        return 2 if offset==0 else (1 if offset==1 else 0)

    def _direction_to(self,a,b):
        delta=(b[0]-a[0],b[1]-a[1])
        for d,v in enumerate(FORWARD):
            if delta==v:
                return d
        raise ValueError("MG85_NOT_ADJACENT_PUBLIC_PLAN")

    def _intent(self,action,status):
        if type(action) is not int or action not in range(7):
            raise ValueError("MG85_ORIGINAL_ACTION_INVALID")
        return {"schema":SCHEMA,"action":action,"status":status,
                "external_fallback":False}

    def _approach_object(self,parent,types,color=None):
        options=[]
        for k,tile in self.grid.items():
            if tile[0] not in types or color is not None and tile[1]!=color:
                continue
            target=pos(k)
            for _,adj in self._neighbors(target):
                if adj not in parent:
                    continue
                # shortest route first, with a deterministic coordinate tie.
                depth=0
                cur=adj
                while cur!=tuple(self.xy):
                    cur=parent[cur][0]
                    depth+=1
                options.append((depth,target,adj))
        if not options:
            return None
        depth,target,adj=min(options)
        if adj!=tuple(self.xy):
            return self._action_for_dir(self._first_step(parent,adj))
        return self._action_for_dir(self._direction_to(tuple(self.xy),target))

    def _frontier(self,parent):
        options=[]
        for p in parent:
            unknown=[d for d,t in self._neighbors(p) if key(t) not in self.grid]
            if not unknown:
                continue
            steps=0
            cursor=p
            while cursor!=tuple(self.xy):
                cursor=parent[cursor][0]
                steps+=1
            options.append((steps+2*self.visited.get(key(p),0),steps,p,min(unknown)))
        if options:
            _,_,frontier,d=min(options)
            if frontier==tuple(self.xy):
                return self._action_for_dir(d)
            return self._action_for_dir(self._first_step(parent,frontier))
        remaining=[p for p in parent if p!=tuple(self.xy)]
        if remaining:
            pt=min(remaining,key=lambda p:(self.visited.get(key(p),0),p))
            return self._action_for_dir(self._first_step(parent,pt))
        return 1

    def choose(self,before):
        self._valid()
        original_public(before)
        self._observe(before)
        front=before["image"][3][5]
        mission=before["mission"]
        words=mission.split(" ")
        desired=OBJ.get(words[-1]) if words else None
        color=IDX.get(words[-2]) if len(words)>1 else None
        # Conventional goal semantics: explicit comparison-only prior.
        if front[0]==5 and self.carrying is None:
            return self._intent(3,"MG85_PUBLIC_KNOWN_KEY_PICKUP")
        if front[0]==4 and front[2]!=0 and self.carrying==5:
            return self._intent(5,"MG85_PUBLIC_KNOWN_DOOR_TOGGLE")
        if front[0]==desired and (color is None or front[1]==color) and desired in (5,6,7):
            if self.carrying is None:
                return self._intent(3,"MG85_PUBLIC_MISSION_PICKUP")
            # Need free hands to pick the target; seek empty front to drop.
            if front[0]==desired:
                return self._intent(0,"MG85_PUBLIC_FIND_DROP_SPACE")
        target_visible=any(t[0]==desired and
                           (color is None or t[1]==color)
                           for t in self.grid.values())
        if self.carrying==5 and self.opened and target_visible and front[0]==1:
            return self._intent(4,"MG85_PUBLIC_RELEASE_KEY_FOR_TARGET")
        paths=self._reachable()
        # The conventional control has explicit task object/door semantics.
        if self.carrying is None and desired in (5,6,7):
            target_action=self._approach_object(paths,(desired,),color)
            if target_action is not None:
                return self._intent(target_action,"MG85_PUBLIC_TARGET_APPROACH")
        if self.carrying is None:
            key_action=self._approach_object(paths,(5,))
            if key_action is not None:
                return self._intent(key_action,"MG85_PUBLIC_KEY_APPROACH")
        if self.carrying==5:
            door_action=self._approach_object(paths,(4,))
            if door_action is not None:
                return self._intent(door_action,"MG85_PUBLIC_DOOR_APPROACH")
        if desired==8:
            goal_action=self._approach_object(paths,(8,))
            if goal_action is not None:
                return self._intent(goal_action,"MG85_PUBLIC_GOAL_APPROACH")
        return self._intent(self._frontier(paths),"MG85_PUBLIC_FRONTIER_SEARCH")

    def learn_selected(self,adapter,before,after):
        self._valid()
        original_public(before)
        original_public(after)
        if (type(adapter) is not OriginalMissionAdapter or adapter.pending is not None
            or adapter.current!=after or not adapter.ledger
            or before["mission"]!=after["mission"]):
            raise ValueError("MG85_UNSELECTED_SOURCE")
        row=adapter.ledger[-1]
        if (row["before_sha"]!=digest(before) or row["after_sha"]!=digest(after)
            or type(row["action"]) is not int or row["action"] not in range(7)):
            raise ValueError("MG85_REAL_SELECTED_LEDGER_MISMATCH")
        action=row["action"]
        front=before["image"][3][5]
        nextfront=after["image"][3][5]
        if action==2 and walkable(front):
            delta=FORWARD[before["direction"]]
            self.xy=(self.xy[0]+delta[0],self.xy[1]+delta[1])
        if (action==3 and self.carrying is None and front[0] in (5,6,7)
            and nextfront!=front and before["direction"]==after["direction"]):
            self.carrying=front[0]
        if action==4 and self.carrying is not None and nextfront[0]==self.carrying:
            self.carrying=None
        if (action==5 and front[0]==4 and nextfront[0]==4
            and front[2]!=0 and nextfront[2]==0):
            self.opened+=1
        self._observe(after)
        current=key(self.xy)
        self.visited[current]=self.visited.get(current,0)+1
        self.samples+=1
        self._valid()
        return {"selected_source":True,"samples":self.samples}

    def checkpoint(self):
        self._valid()
        state={"schema":SCHEMA,"samples":self.samples,"episodes":self.episodes,
               "grid":self.grid,"visited":self.visited,"xy":list(self.xy),
               "heading":self.heading,"carrying":self.carrying,"opened":self.opened}
        blob=canonical({"state":state,"sha256":hashlib.sha256(canonical(state)).hexdigest()})
        if len(blob)>MAX_BYTES:
            raise ValueError("MG85_MEMORY_SIZE_CAP")
        return blob

    @classmethod
    def restore(cls,raw):
        try:
            if type(raw) is not bytes or not 0<len(raw)<=MAX_BYTES:
                raise ValueError("MG85_INVALID_CHECKPOINT_SIZE")
            obj=json.loads(raw)
            if type(obj) is not dict or set(obj)!={"state","sha256"}:
                raise ValueError("MG85_CHECKPOINT_ENVELOPE")
            s=obj["state"]
            if (type(s) is not dict or set(s)!={"schema","samples","episodes","grid",
                      "visited","xy","heading","carrying","opened"} or s["schema"]!=SCHEMA
                or hashlib.sha256(canonical(s)).hexdigest()!=obj["sha256"]):
                raise ValueError("MG85_CHECKPOINT_DIGEST")
            model=cls()
            model.samples=s["samples"]
            model.episodes=s["episodes"]
            model.grid=s["grid"]
            model.visited=s["visited"]
            model.xy=s["xy"]
            model.heading=s["heading"]
            model.carrying=s["carrying"]
            model.opened=s["opened"]
            model._valid()
            if model.checkpoint()!=raw:
                raise ValueError("MG85_CHECKPOINT_NOT_CANONICAL")
            return model
        except (ValueError,TypeError,KeyError,AttributeError,UnicodeError) as e:
            raise ValueError("MG85_UNTRUSTED_MODEL_BASED_CONTROL_CHECKPOINT") from e
