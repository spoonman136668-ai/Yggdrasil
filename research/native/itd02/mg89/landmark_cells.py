"""MG89 observed landmark relations; public original selected actions only.

Image patch alignment is a programmed geometry prior, not learned map pose.
"""
from __future__ import annotations
import hashlib
import json
from research.native.itd02.mg88.alignment_cells import PublicAlignmentCells,public_alignment
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter,original_public
from research.native.itd02.r10.public_adapter import canonical,digest

SCHEMA="yggdrasil.itd02.mg89.landmark-links.v1"
LIMIT=4096
MAX_PAIRS=8192
MAX_STEPS=12000
MAX_BYTES=12000000

def patch_ids(view):
    original_public(view)
    img=view["image"]
    patches={}
    for x in range(6):
        for y in range(6):
            four=[img[x][y],img[x+1][y],img[x][y+1],img[x+1][y+1]]
            if any(tile[0]==0 for tile in four):
                continue
            if len({tuple(tile) for tile in four})<2:
                continue
            sig=hashlib.sha256(canonical(four)).hexdigest()
            patches.setdefault(sig,set()).add((x,y))
    return patches

class LandmarkLinkCells:
    def __init__(self,parent=None):
        self.parent=PublicAlignmentCells() if parent is None else parent
        if type(self.parent) is not PublicAlignmentCells:
            raise ValueError("MG89_PARENT_REQUIRED")
        self.landmarks={}
        self.links={}
        self.events=[{"count":0,"novel":0,"matched":0} for _ in range(7)]

    @property
    def samples(self):
        return self.parent.samples

    def _valid(self):
        self.parent._valid()
        if (type(self.landmarks) is not dict or len(self.landmarks)>LIMIT
            or type(self.links) is not dict or type(self.events) is not list
            or len(self.events)!=7 or self.samples>MAX_STEPS):
            raise ValueError("MG89_MEMORY_CAP")
        if sum(x["count"] for x in self.events)!=self.samples:
            raise ValueError("MG89_SAMPLE_CONSERVATION")
        if len(self.landmarks)!=sum(x["novel"] for x in self.events):
            raise ValueError("MG89_LANDMARK_CONSERVATION")
        if sum(sum(a) for a in self.links.values())!=sum(x["matched"] for x in self.events):
            raise ValueError("MG89_LINK_CONSERVATION")
        valid=lambda s:type(s) is str and len(s)==64 and all(c in "0123456789abcdef" for c in s)
        if any(not valid(k) or type(v) is not int or not 0<v<=MAX_STEPS
               for k,v in self.landmarks.items()):
            raise ValueError("MG89_BAD_LANDMARK")
        pairs=0
        for sig,row in self.links.items():
            if not valid(sig) or sig not in self.landmarks or type(row) is not list or len(row)!=7:
                raise ValueError("MG89_BAD_LINK")
            if any(type(v) is not int or not 0<=v<=MAX_STEPS for v in row):
                raise ValueError("MG89_BAD_EDGE_VALUE")
            pairs+=sum(int(x>0) for x in row)
        if pairs>MAX_PAIRS:
            raise ValueError("MG89_EDGE_CAP")

    def start_session(self,adapter,name,live=False):
        if type(adapter) is not OriginalMissionAdapter or live:
            raise ValueError("MG89_SOURCE_SESSION_ONLY")
        self._valid()
        return self.parent.start_session(adapter,name,live=False)

    def choose(self,before):
        original_public(before)
        self._valid()
        current=patch_ids(before)
        row=self.parent.parent.cells.get(digest(before))
        if row is None:
            row=[{"count":0,"next":{},"q":0} for _ in range(7)]
        def score(a):
            n=row[a]["count"]
            e=self.events[a]
            support=sum(1 for sig in current if self.links.get(sig,[0]*7)[a])
            repeat=max(row[a]["next"].values(),default=0)
            return (200//(1+n)+250*e["novel"]//(1+e["count"])
                    +80*support//(1+len(current))-120*repeat//(1+n))
        a=max(range(7),key=lambda action:(score(action),-action))
        return {"schema":SCHEMA,"action":a,
                "status":"MG89_SELECTED_PUBLIC_LANDMARK_LINKS",
                "external_fallback":False}

    def learn_selected(self,adapter,before,after):
        self._valid()
        original_public(before)
        original_public(after)
        if (type(adapter) is not OriginalMissionAdapter or adapter.pending is not None
            or adapter.current!=after or not adapter.ledger
            or before["mission"]!=after["mission"]):
            raise ValueError("MG89_SOURCE_NOT_SELECTED")
        event=adapter.ledger[-1]
        a=event["action"]
        if (type(a) is not int or a not in range(7)
            or event["before_sha"]!=digest(before)
            or event["after_sha"]!=digest(after)):
            raise ValueError("MG89_SOURCE_DIGEST_DRIFT")
        if self.samples>=MAX_STEPS:
            raise ValueError("MG89_SOURCE_STEP_CAP")
        old,new=patch_ids(before),patch_ids(after)
        novel=set(new)-set(self.landmarks)
        if len(self.landmarks)+len(novel)>LIMIT:
            raise ValueError("MG89_LANDMARK_CAP")
        offset=public_alignment(before,after)
        match=[]
        if offset is not None:
            dx,dy=offset
            for sig,positions in old.items():
                other=new.get(sig,set())
                if other and any((x+dx,y+dy) in other for x,y in positions):
                    match.append(sig)
        pairs=sum(sum(int(z>0) for z in row) for row in self.links.values())
        pairs+=sum(int(not self.links.get(sig,[0]*7)[a]) for sig in match)
        if pairs>MAX_PAIRS:
            raise ValueError("MG89_LINK_CAP")
        n=self.samples
        receipt=self.parent.learn_selected(adapter,before,after)
        if self.samples!=n+1:
            raise ValueError("MG89_PARENT_DRIFT")
        for sig in new:
            self.landmarks[sig]=self.landmarks.get(sig,0)+1
        for sig in match:
            self.links.setdefault(sig,[0]*7)[a]+=1
        self.events[a]["count"]+=1
        self.events[a]["novel"]+=len(novel)
        self.events[a]["matched"]+=len(match)
        self._valid()
        return receipt

    def checkpoint(self):
        self._valid()
        state={"schema":SCHEMA,"parent":self.parent.checkpoint().decode(),
               "landmarks":self.landmarks,"links":self.links,"events":self.events}
        blob=canonical({"state":state,"sha256":hashlib.sha256(canonical(state)).hexdigest()})
        if len(blob)>MAX_BYTES:
            raise ValueError("MG89_COLD_CAP")
        return blob

    @classmethod
    def restore(cls,raw):
        try:
            if type(raw) is not bytes or not 0<len(raw)<=MAX_BYTES:
                raise ValueError("MG89_BAD_COLD_BYTES")
            wire=json.loads(raw)
            if type(wire) is not dict or set(wire)!={"state","sha256"}:
                raise ValueError("MG89_BAD_COLD_ENVELOPE")
            s=wire["state"]
            if (type(s) is not dict or set(s)!={"schema","parent","landmarks","links","events"}
                or s["schema"]!=SCHEMA or type(s["parent"]) is not str
                or hashlib.sha256(canonical(s)).hexdigest()!=wire["sha256"]):
                raise ValueError("MG89_BAD_COLD_DIGEST")
            obj=cls(PublicAlignmentCells.restore(s["parent"].encode()))
            obj.landmarks=s["landmarks"]
            obj.links=s["links"]
            obj.events=s["events"]
            obj._valid()
            if obj.checkpoint()!=raw:
                raise ValueError("MG89_NONCANONICAL")
            return obj
        except (ValueError,TypeError,KeyError,AttributeError,UnicodeError) as exc:
            raise ValueError("MG89_COLD_REJECT") from exc
