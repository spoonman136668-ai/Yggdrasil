"""WSP125 direct numerical feature GROWTH after unanticipated consequences.

No import of source. A new 17-int32 feature bank exists only AFTER a
nonzero residual is measured; source supports and delta are never provided.
Generic two-factor conjunction is a known inductive bias, not invented here.
"""
from __future__ import annotations
from array import array
from hashlib import sha256
import json

SCHEMA="wsp125.source-blind-dynamic-mask-memory.v1"


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"))


def digest(x):
    return sha256(canonical(x).encode()).hexdigest()


def _receipt_ok(x):
    return type(x) is str and len(x)==64 and all(
        c in "0123456789abcdef" for c in x)


def _valid_event(x):
    return (type(x) is list and len(x)==7 and
            type(x[0]) is int and 125900<=x[0]<126028 and
            type(x[1]) is int and x[1]==x[0]-125900 and
            type(x[2]) is int and x[2]>=0 and
            all(type(y) is int and 0<=y<8 for y in x[3:6]) and
            _receipt_ok(x[6]))


class _MaskState:
    def __init__(self):
        self.events=[]
        self.seen=set()
        self.witness=None
        self.delta=None
        self.left=None
        self.right=None

    @property
    def slots(self):
        return (0 if self.left is None else
                len(self.left)+len(self.right)+1)

    def _recompute(self):
        positives=[e for e in self.events if (e[5]^(e[3]^e[4]))!=0]
        if not positives:
            self.witness=self.delta=self.left=self.right=None
            return
        first=positives[0]
        self.witness=(first[3],first[4])
        self.delta=first[5]^(first[3]^first[4])
        self.left=array("i",[-1]*8)
        self.right=array("i",[-1]*8)
        wa,wb=self.witness
        for row in self.events:
            _,_,_,a,b,value,_=row
            residual=value^(a^b)
            if residual not in (0,self.delta):
                raise ValueError("WSP125_MULTIPLE_RESIDUAL_EFFECTS")
            if b==wb:
                flag=int(residual==self.delta)
                if self.left[a] not in (-1,flag):
                    raise ValueError("WSP125_LEFT_CAUSAL_CONTRADICTION")
                self.left[a]=flag
            if a==wa:
                flag=int(residual==self.delta)
                if self.right[b] not in (-1,flag):
                    raise ValueError("WSP125_RIGHT_CAUSAL_CONTRADICTION")
                self.right[b]=flag
        for row in self.events:
            _,_,_,a,b,value,_=row
            if self.left[a]>=0 and self.right[b]>=0:
                residual=value^(a^b)
                required=self.delta if self.left[a] and self.right[b] else 0
                if residual!=required:
                    raise ValueError("WSP125_FACTOR_MODEL_CONTRADICTION")

    def ingest(self,row):
        if not _valid_event(row):
            raise ValueError("WSP125_UNTRUSTED_EVENT_FORMAT")
        key=(row[0],row[2])
        if key in self.seen:
            raise ValueError("WSP125_REPEATED_SOURCE_ACTION")
        self.events.append(row[:])
        self.seen.add(key)
        try:
            self._recompute()
        except Exception:
            self.events.pop()
            self.seen.remove(key)
            self._recompute()
            raise

    def payload(self):
        return {"events":self.events,
                "witness":None if self.witness is None else list(self.witness),
                "delta":self.delta,
                "left":None if self.left is None else list(self.left),
                "right":None if self.right is None else list(self.right),
                "slots":self.slots}


class DirectFeatureGrowth:
    def __init__(self):
        self.state={}

    def _state(self,law_id):
        if type(law_id) is not int or not 0<=law_id<128:
            raise ValueError("WSP125_INVALID_PUBLIC_LAW_ID")
        if law_id not in self.state:
            self.state[law_id]=_MaskState()
        return self.state[law_id]

    def choose(self,view,available):
        if (getattr(view,"cohort",None)!="fit" or
                getattr(view,"seed",None)!=125900+view.law_id):
            raise PermissionError("WSP125_FIT_ACTIONS_ONLY")
        st=self._state(view.law_id)
        if len(st.events)>=32:
            return None
        choices=[]
        if st.witness is not None:
            a0,b0=st.witness
            for a in range(8):
                if st.left[a]<0:
                    choices.append((a,b0))
            for b in range(8):
                if st.right[b]<0:
                    choices.append((a0,b))
        # Fixed deterministic Latin scan before witness and for surplus
        # fully paid source calls after identification.
        for shift in range(8):
            for a in range(8):
                choices.append((a,(a+shift)%8))
        for a,b in choices:
            s=view.subject(a,b)
            if s in available and (view.seed,s) not in st.seen:
                return s
        raise ValueError("WSP125_EXHAUSTED_LEGAL_ACTIONS")

    def observe(self,view,event):
        if (getattr(view,"cohort",None)!="fit" or
                view.seed!=125900+view.law_id or
                getattr(event,"seed",None)!=view.seed or
                getattr(event,"law_id",None)!=view.law_id or
                type(getattr(event,"subject",None)) is not int or
                event.subject not in view.legal or
                view.pair(event.subject)!=
                   (getattr(event,"left",None),getattr(event,"right",None)) or
                type(getattr(event,"effect",None)) is not int or
                not 0<=event.effect<8 or
                not _receipt_ok(getattr(event,"receipt_sha256",None))):
            raise ValueError("WSP125_UNVERIFIED_SOURCE_RECORD")
        self._state(view.law_id).ingest([
            event.seed,event.law_id,event.subject,event.left,event.right,
            event.effect,event.receipt_sha256])

    def infer_pair(self,law_id,left,right):
        if (type(left) is not int or type(right) is not int or
                not 0<=left<8 or not 0<=right<8):
            raise ValueError("WSP125_BAD_CAUSAL_INPUT")
        st=self._state(law_id)
        if st.delta is None:
            return None
        a,b=st.left[left],st.right[right]
        if a==0 or b==0:
            return left^right
        if a==1 and b==1:
            return (left^right)^st.delta
        return None

    def infer(self,view,subject):
        return self.infer_pair(view.law_id,*view.pair(subject))

    @property
    def feature_slots(self):
        return sum(st.slots for st in self.state.values())

    @property
    def learned_laws(self):
        return sum(st.witness is not None for st in self.state.values())

    def snapshot(self):
        body={"schema":SCHEMA,
              "states":{str(k):v.payload()
                        for k,v in sorted(self.state.items())}}
        return canonical({"payload":body,"sha256":digest(body)})

    @classmethod
    def restore(cls,blob):
        try:
            outer=json.loads(blob)
            body=outer["payload"]
            if body.get("schema")!=SCHEMA or outer.get("sha256")!=digest(body):
                raise ValueError("WSP125_COLD_DIGEST_INVALID")
            states=body["states"]
            if type(states) is not dict:
                raise ValueError("WSP125_COLD_FORMAT")
            obj=cls()
            for key in sorted(states,key=int):
                law=int(key)
                if str(law)!=key or not 0<=law<128:
                    raise ValueError("WSP125_COLD_KEY")
                payload=states[key]
                if type(payload) is not dict or type(payload.get("events")) is not list:
                    raise ValueError("WSP125_COLD_EVENTS")
                state=obj._state(law)
                for row in payload["events"]:
                    if not _valid_event(row) or row[1]!=law:
                        raise ValueError("WSP125_COLD_EVENT_REPLAY")
                    state.ingest(row)
                if state.payload()!=payload:
                    raise ValueError("WSP125_COLD_FORGED_RELATION_WEIGHTS")
            return obj
        except (TypeError,ValueError,KeyError,AttributeError) as exc:
            if isinstance(exc,ValueError):
                raise
            raise ValueError("WSP125_COLD_FORMAT") from exc
