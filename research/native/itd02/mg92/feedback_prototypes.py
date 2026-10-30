"""MG92 teacher-conditioned public-source feedback gate, no hidden simulator state.

Uses frozen MG91 native reward prototype training; the only new learned
feedback is from actually selected original public action consequences.
Not self-discovered navigation and not permission to promote FORGE models.
"""
from __future__ import annotations
import hashlib
import json
from research.native.itd02.mg91.native_prototypes import PublicRewardPrototypes, _features, K
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter, original_public
from research.native.itd02.r10.public_adapter import canonical, digest

SCHEMA="yggdrasil.itd02.mg92.native-public-consequence-feedback.v1"
MAX_PAIRS=4096
MAX_BYTES=12000000
MAX_ACTIONS=384

class SourceFeedbackPrototypes:
    def __init__(self, parent=None):
        self.parent = PublicRewardPrototypes() if parent is None else parent
        if type(self.parent) is not PublicRewardPrototypes:
            raise ValueError("MG92_FROZEN_NATIVE_PARENT_ONLY")
        self.unchanged={}
        self.last=-1
        self.streak=0
        self.observed=0
        self.changes=0

    @property
    def data_sha(self):
        return self.parent.data_sha

    @property
    def training_count(self):
        return self.parent.training_count

    def fit(self,episodes):
        self.parent.fit(episodes)
        self._valid()

    def _valid(self):
        self.parent._valid()
        if (type(self.unchanged) is not dict or len(self.unchanged)>MAX_PAIRS
            or type(self.last) is not int or self.last not in range(-1,7)
            or type(self.streak) is not int or not 0<=self.streak<=MAX_ACTIONS
            or type(self.observed) is not int or not 0<=self.observed<=MAX_ACTIONS
            or type(self.changes) is not int or not 0<=self.changes<=self.observed):
            raise ValueError("MG92_SELECTED_SOURCE_FEEDBACK_BOUNDS")
        for name,cnt in self.unchanged.items():
            if (type(name) is not str or len(name)!=66
                or name[64]!=":" or name[65] not in "0123456"
                or any(x not in "0123456789abcdef" for x in name[:64])
                or type(cnt) is not int or not 0<cnt<=MAX_ACTIONS):
                raise ValueError("MG92_SELECTED_ONLY_PAIR_CORRUPTED")
        if self.last==-1 and self.streak:
            raise ValueError("MG92_LAST_SOURCE_ACTION_INCONSISTENT")

    def start_session(self,adapter,name,live=False):
        if type(adapter) is not OriginalMissionAdapter or live:
            raise ValueError("MG92_ORIGINAL_PUBLIC_ONLY")
        self.parent.start_session(adapter,name,live=False)
        self.unchanged={}
        self.last=-1
        self.streak=0
        self.observed=0
        self.changes=0
        self._valid()

    def _votes(self,before):
        original_public(before)
        features=set(_features(before))
        front=before["image"][3][5]
        matches=[]
        for i,p in enumerate(self.parent.examples):
            overlap=len(features.intersection(p["patch"]))
            union=max(1,len(features.union(p["patch"])))
            sim=(200*int(p["mission"]==before["mission"])
                +100*int(p["direction"]==before["direction"])
                +100*int(p["front"]==front)
                +50*int(p["prev"]==self.parent.prev)
                +400*overlap//union)
            matches.append((sim,-i,p["action"],p["value"]))
        votes=[0]*7
        for sim,_,a,value in sorted(matches,reverse=True)[:K]:
            votes[a]+=(1+sim)*value
        return votes

    def choose(self,before):
        self._valid()
        original_public(before)
        ident=digest(before)
        votes=self._votes(before)
        def rank(a):
            stale=min(3,self.unchanged.get(ident+":"+str(a),0))
            repeated=max(0,self.streak-2) if self.last==a else 0
            return votes[a]-200000*stale-150000*repeated
        action=max(range(7),key=lambda a:(rank(a),-a))
        return {"schema":SCHEMA,"action":action,
                "status":"MG92_SELECTED_PUBLIC_EFFECT_FEEDBACK",
                "external_fallback":False}

    def observe_selected(self,adapter,before,after):
        self._valid()
        original_public(before)
        original_public(after)
        if (type(adapter) is not OriginalMissionAdapter or adapter.pending is not None
            or adapter.current!=after or not adapter.ledger
            or before["mission"]!=after["mission"]):
            raise ValueError("MG92_UNSELECTED_ORIGINAL_SOURCE")
        row=adapter.ledger[-1]
        a=row.get("action")
        before_sha=digest(before)
        after_sha=digest(after)
        if (type(a) is not int or a not in range(7)
            or row["before_sha"]!=before_sha or row["after_sha"]!=after_sha
            or self.observed>=MAX_ACTIONS):
            raise ValueError("MG92_REAL_SELECTED_LEDGER_MISMATCH")
        pair=before_sha+":"+str(a)
        if before_sha==after_sha and pair not in self.unchanged and len(self.unchanged)>=MAX_PAIRS:
            raise ValueError("MG92_PUBLIC_MEMORY_PAIR_LIMIT")
        # Frozen MG91 parent validates actual selected public custody; no
        # demonstration labels or reward-to-go values may change in heldout.
        self.parent.observe_selected(adapter,before,after)
        if before_sha==after_sha:
            self.unchanged[pair]=self.unchanged.get(pair,0)+1
        else:
            self.changes+=1
        self.streak=min(MAX_ACTIONS,self.streak+1) if self.last==a else 1
        self.last=a
        self.observed+=1
        self._valid()

    def checkpoint(self):
        self._valid()
        state={"schema":SCHEMA,"parent":self.parent.checkpoint().decode("utf8"),
               "unchanged":self.unchanged,"last":self.last,"streak":self.streak,
               "observed":self.observed,"changes":self.changes}
        blob=canonical({"state":state,"sha256":hashlib.sha256(canonical(state)).hexdigest()})
        if len(blob)>MAX_BYTES:
            raise ValueError("MG92_CHECKPOINT_SIZE_CAP")
        return blob

    @classmethod
    def restore(cls,raw):
        try:
            if type(raw) is not bytes or not 0<len(raw)<=MAX_BYTES:
                raise ValueError("MG92_CHECKPOINT_INVALID_BYTES")
            val=json.loads(raw)
            if type(val) is not dict or set(val)!={"state","sha256"}:
                raise ValueError("MG92_CHECKPOINT_ENVELOPE")
            s=val["state"]
            if (type(s) is not dict or set(s)!={"schema","parent","unchanged",
                    "last","streak","observed","changes"}
                or s["schema"]!=SCHEMA or type(s["parent"]) is not str
                or hashlib.sha256(canonical(s)).hexdigest()!=val["sha256"]):
                raise ValueError("MG92_CHECKPOINT_BAD_DIGEST")
            obj=cls(PublicRewardPrototypes.restore(s["parent"].encode("utf8")))
            for prop in ("unchanged","last","streak","observed","changes"):
                setattr(obj,prop,s[prop])
            obj._valid()
            if obj.checkpoint()!=raw:
                raise ValueError("MG92_CHECKPOINT_NONCANONICAL")
            return obj
        except (ValueError,TypeError,KeyError,AttributeError,UnicodeError) as e:
            raise ValueError("MG92_UNTRUSTED_SOURCE_CHECKPOINT") from e
