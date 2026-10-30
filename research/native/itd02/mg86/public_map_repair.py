"""MG86 repaired conventional public-map task calibration; NOT native learning.

All map, orientation, key/door and mission semantics are human-programmed
priors. Only original public observations + selected source actions/feedback
are used. No simulator internal pose, carrying or world map is read.
"""
from __future__ import annotations
import hashlib
import json
from research.native.itd02.mg85.public_map_control import (
    PublicMapControl, FORWARD, IDX, OBJ, key, pos, walkable)
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter,original_public
from research.native.itd02.r10.public_adapter import canonical,digest

SCHEMA="yggdrasil.itd02.mg86.conventional-public-map-cycle-repair.v1"
MAX_BYTES=2000000
MAX_PROBES=4096

class RepairedMapControl(PublicMapControl):
    def __init__(self):
        super().__init__()
        self.deposited_key=False
        self.key_color=None
        self.edge_probes={}
        self.last_source_action=None
        self.movement_failures=0

    def _valid(self):
        super()._valid()
        if (type(self.deposited_key) is not bool
            or self.key_color is not None and (type(self.key_color) is not int
                or self.key_color not in range(6))
            or type(self.edge_probes) is not dict or len(self.edge_probes)>MAX_PROBES
            or self.last_source_action is not None and (type(self.last_source_action) is not int
                or self.last_source_action not in range(7))
            or type(self.movement_failures) is not int or self.movement_failures<0):
            raise ValueError("MG86_CONVENTIONAL_CONTROL_INTEGRITY")
        for name,number in self.edge_probes.items():
            if (type(name) is not str or len(name)>30
                or type(number) is not int or not 0<=number<=256):
                raise ValueError("MG86_PUBLIC_EDGE_PROBE_CORRUPT")

    def start_session(self,adapter,name,live=False):
        # Keep learned source-free conventional geometry separated by episode.
        # Each newly reset original environment has an unrelated coordinate
        # origin, so all spatial and carrying priors are reset with the parent.
        super().start_session(adapter,name,live=live)
        self.deposited_key=False
        self.key_color=None
        self.edge_probes={}
        self.last_source_action=None
        self.movement_failures=0
        self._valid()

    def _is_target(self,front,mission):
        words=mission.split(" ")
        kind=OBJ.get(words[-1]) if words else None
        color=IDX.get(words[-2]) if len(words)>1 else None
        return kind in (5,6,7) and front[0]==kind and (
            color is None or front[1]==color)

    def _locked_doors_known(self):
        return any(tile[0]==4 and tile[2]==2
                   for tile in self.grid.values())

    def _empty_front(self,before):
        return before["image"][3][5][0]==1

    def _navigate(self,parent):
        # A preprogrammed bounded active frontier strategy. An unknown
        # neighbor is interesting only from a *known reachable* floor.
        options=[]
        for p in parent:
            for d,there in self._neighbors(p):
                if key(there) in self.grid:
                    continue
                depth=0
                c=p
                while c!=tuple(self.xy):
                    c=parent[c][0]
                    depth+=1
                probe=key(p)+":"+str(d)
                visits=self.edge_probes.get(probe,0)
                # Stable deterministic choice and explicit re-probe penalty.
                options.append((depth+4*visits+self.visited.get(key(p),0),
                                depth,visits,p,d))
        if options:
            _,depth,visits,p,d=min(options)
            if p==tuple(self.xy):
                action=self._action_for_dir(d)
                self.edge_probes[key(p)+":"+str(d)]=min(256,visits+1)
                return action
            return self._action_for_dir(self._first_step(parent,p))
        # Fallback to old known-floor paths, but break same-cell turning
        # cycles with explicit source-selected original action variation.
        other=[p for p in parent if p!=tuple(self.xy)]
        if other:
            chosen=min(other,key=lambda p:(self.visited.get(key(p),0),p))
            return self._action_for_dir(self._first_step(parent,chosen))
        return 1 if self.last_source_action!=1 else 0

    def choose(self,before):
        self._valid()
        original_public(before)
        self._observe(before)
        front=before["image"][3][5]
        mission=before["mission"]
        words=mission.split(" ")
        desired=OBJ.get(words[-1]) if words else None
        target_color=IDX.get(words[-2]) if len(words)>1 else None

        if self._is_target(front,mission) and self.carrying is None:
            return self._intent(3,"MG86_CONVENTIONAL_TARGET_PICKUP")

        # Doors are opened only as original public state allows. Holding a
        # matching key is determined by *selected* pickup source feedback.
        if front[0]==4 and front[2] in (1,2):
            if front[2]==1 or self.carrying==5 and self.key_color==front[1]:
                return self._intent(5,"MG86_CONVENTIONAL_DOOR_TOGGLE")

        # Repeated pickup/drop of the same just-released key is prohibited
        # unless a still-locked original-public door requires it.
        if front[0]==5 and self.carrying is None:
            if not self.deposited_key or self._locked_doors_known():
                return self._intent(3,"MG86_CONVENTIONAL_KEY_PICKUP")

        # Release only in a source-public empty front tile, after an
        # actually opened door and when a mission target has been seen.
        # Never drop into a target cell or immediately repick gratuitously.
        goal_known=any(tile[0]==desired and
                       (target_color is None or tile[1]==target_color)
                       for tile in self.grid.values())
        if self.carrying==5 and self.opened>0 and goal_known:
            if self._empty_front(before):
                return self._intent(4,"MG86_CONVENTIONAL_KEY_RELEASE")
            # Orient toward a known empty neighbor without inventing
            # simulator carrying-state or secret trajectory information.
            for d,there in self._neighbors(tuple(self.xy)):
                tile=self.grid.get(key(there))
                if tile is not None and tile[0]==1:
                    return self._intent(self._action_for_dir(d),
                                        "MG86_CONVENTIONAL_KEY_RELEASE_ORIENT")

        paths=self._reachable()
        if self.carrying is None and desired in (5,6,7):
            target_action=self._approach_object(paths,(desired,),target_color)
            if target_action is not None:
                return self._intent(target_action,"MG86_CONVENTIONAL_TARGET_APPROACH")
        if self.carrying is None:
            # Do not reacquire deposited key unless an observed locked door
            # remains in the public map. This is not a learned policy.
            if not self.deposited_key or self._locked_doors_known():
                key_action=self._approach_object(paths,(5,))
                if key_action is not None:
                    return self._intent(key_action,"MG86_CONVENTIONAL_KEY_APPROACH")
        if self.carrying==5:
            door_action=self._approach_object(paths,(4,))
            if door_action is not None:
                return self._intent(door_action,"MG86_CONVENTIONAL_LOCKED_DOOR_APPROACH")
        return self._intent(self._navigate(paths),"MG86_CONVENTIONAL_PUBLIC_FRONTIER")

    def learn_selected(self,adapter,before,after):
        self._valid()
        original_public(before)
        original_public(after)
        if (type(adapter) is not OriginalMissionAdapter
            or not adapter.ledger or adapter.pending is not None
            or adapter.current!=after or before["mission"]!=after["mission"]):
            raise ValueError("MG86_NO_COMPLETED_ORIGINAL_SOURCE")
        row=adapter.ledger[-1]
        if (row["before_sha"]!=digest(before) or row["after_sha"]!=digest(after)
            or type(row["action"]) is not int or row["action"] not in range(7)):
            raise ValueError("MG86_SELECTED_SOURCE_DIGEST_MISMATCH")
        previous=tuple(self.xy)
        front=before["image"][3][5]
        action=row["action"]
        if action==3 and front[0]==5 and self.carrying is None:
            if after["image"][3][5]!=front:
                self.key_color=front[1]
                self.deposited_key=False
        if action==4 and self.carrying==5:
            nextfront=after["image"][3][5]
            if nextfront[0]==5:
                self.deposited_key=True
                self.key_color=None
        if action==2 and not walkable(front):
            self.movement_failures+=1
        receipt=super().learn_selected(adapter,before,after)
        if action==2 and not walkable(front) and tuple(self.xy)!=previous:
            raise ValueError("MG86_BLOCKED_FORWARD_PHANTOM_POSITION")
        self.last_source_action=action
        self._valid()
        return receipt

    def checkpoint(self):
        self._valid()
        state={"schema":SCHEMA,
               "parent":super().checkpoint().decode("utf-8"),
               "deposited_key":self.deposited_key,
               "key_color":self.key_color,
               "edge_probes":self.edge_probes,
               "last_source_action":self.last_source_action,
               "movement_failures":self.movement_failures}
        raw=canonical({"state":state,
                       "sha256":hashlib.sha256(canonical(state)).hexdigest()})
        if len(raw)>MAX_BYTES:
            raise ValueError("MG86_MEMORY_CAP")
        return raw

    @classmethod
    def restore(cls,raw):
        try:
            if type(raw) is not bytes or not 0<len(raw)<=MAX_BYTES:
                raise ValueError("MG86_COLD_BYTES")
            data=json.loads(raw)
            if type(data) is not dict or set(data)!={"state","sha256"}:
                raise ValueError("MG86_COLD_ENVELOPE")
            state=data["state"]
            if (type(state) is not dict or set(state)!={"schema","parent",
                    "deposited_key","key_color","edge_probes",
                    "last_source_action","movement_failures"}
                or state["schema"]!=SCHEMA
                or type(state["parent"]) is not str
                or hashlib.sha256(canonical(state)).hexdigest()!=data["sha256"]):
                raise ValueError("MG86_COLD_DIGEST")
            old=PublicMapControl.restore(state["parent"].encode("utf-8"))
            obj=cls()
            for field in ("samples","grid","visited","xy","heading",
                          "carrying","opened","episodes"):
                setattr(obj,field,getattr(old,field))
            for field in ("deposited_key","key_color","edge_probes",
                          "last_source_action","movement_failures"):
                setattr(obj,field,state[field])
            obj._valid()
            if obj.checkpoint()!=raw:
                raise ValueError("MG86_COLD_CANONICAL")
            return obj
        except (ValueError,TypeError,KeyError,AttributeError,UnicodeError) as e:
            raise ValueError("MG86_UNTRUSTED_CONVENTIONAL_CONTROL") from e
