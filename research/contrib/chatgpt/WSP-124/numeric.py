"""WSP124 non-gradient numerical causal model repair, source-independent.

XOR and rectangular threshold search are a PROVIDED grammar. What is
programmed from consequences are 16 independent domains' actual factor
vectors, unlisted thresholds and delta values, not new primitive types.
"""
from __future__ import annotations
from array import array
from hashlib import sha256
import json

SCHEMA="wsp124.direct-causal-repair.v1"
FIT=frozenset(range(128900,128916))
DOMAINS=16
SLOTS=19


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"))


def digest(x):
    return sha256(canonical(x).encode("utf-8")).hexdigest()


def _receipt(value):
    return type(value) is str and len(value)==64 and all(
        c in "0123456789abcdef" for c in value)


def _valid_row(row):
    return (type(row) is list and len(row)==7
            and type(row[0]) is int and row[0] in FIT
            and type(row[1]) is int and row[1]==row[0]-128900
            and type(row[2]) is int and row[2]>=0
            and all(type(v) is int and 0<=v<8 for v in row[3:6])
            and _receipt(row[6]))


class NumericRepair:
    def __init__(self):
        self.events=[]
        self.seen=set()
        self.weights={d:array("i",[-1]*SLOTS) for d in range(DOMAINS)}
        self.counts=[0]*DOMAINS
        self.bounds={d:{"x":[2,7],"y":[2,7]} for d in range(DOMAINS)}

    def next_pair(self,domain):
        if type(domain) is not int or not 0<=domain<DOMAINS:
            raise ValueError("WSP124_BAD_DOMAIN")
        n=self.counts[domain]
        if n<8:
            return (0,n)
        if n<15:
            return (n-7,0)
        if n==15:
            return (7,7)
        if n<19:
            lo,hi=self.bounds[domain]["x"]
            return ((lo+hi)//2,7)
        if n<22:
            lo,hi=self.bounds[domain]["y"]
            return (7,(lo+hi)//2)
        if n==22:
            w=self.weights[domain]
            if w[16]<2 or w[17]<2:
                raise AssertionError("WSP124_REPAIR_THRESHOLDS_NOT_IDENTIFIED")
            return (w[16]-1,w[17]-1)
        return None

    def choose(self,view,available):
        if (getattr(view,"seed",None) not in FIT
                or getattr(view,"domain",None)!=view.seed-128900):
            raise PermissionError("WSP124_NUMERIC_FIT_WORLD_ONLY")
        pair=self.next_pair(view.domain)
        if pair is None:
            return None
        subject=view.subject(*pair)
        if subject not in available or (view.seed,subject) in self.seen:
            raise ValueError("WSP124_ACTIVE_QUERY_NOT_LEGAL_OR_REPLAY")
        return subject

    def _apply(self,row):
        if not _valid_row(row):
            raise ValueError("WSP124_BAD_EVIDENCE_ROW")
        seed,d,subject,a,b,effect,_=row
        key=(seed,subject)
        if key in self.seen:
            raise ValueError("WSP124_DUPLICATE_OBSERVATION")
        expected=self.next_pair(d)
        if expected!=(a,b):
            raise ValueError("WSP124_INTERVENTION_ORDER_OR_PAIR_MISMATCH")
        n=self.counts[d]
        w=self.weights[d]
        if n<8:
            w[8+b]=effect
            if n==0:
                w[0]=0
        elif n<15:
            w[a]=effect^w[8]
        else:
            if any(w[i]<0 for i in range(16)):
                raise ValueError("WSP124_MISSING_BASE_FACTOR")
            residue=effect^w[a]^w[8+b]
            if n==15:
                if not 1<=residue<8:
                    raise ValueError("WSP124_REPAIR_WITNESS_MISSING")
                w[18]=residue
            elif n<19:
                if residue not in (0,w[18]):
                    raise ValueError("WSP124_X_THRESHOLD_CONTRADICTION")
                bounds=self.bounds[d]["x"]
                if residue:
                    bounds[1]=min(bounds[1],a)
                else:
                    bounds[0]=max(bounds[0],a+1)
                if bounds[0]>bounds[1]:
                    raise ValueError("WSP124_X_THRESHOLD_CONTRADICTION")
                if n==18:
                    if bounds[0]!=bounds[1]:
                        raise AssertionError("WSP124_X_UNIDENTIFIED")
                    w[16]=bounds[0]
            elif n<22:
                if residue not in (0,w[18]):
                    raise ValueError("WSP124_Y_THRESHOLD_CONTRADICTION")
                bounds=self.bounds[d]["y"]
                if residue:
                    bounds[1]=min(bounds[1],b)
                else:
                    bounds[0]=max(bounds[0],b+1)
                if bounds[0]>bounds[1]:
                    raise ValueError("WSP124_Y_THRESHOLD_CONTRADICTION")
                if n==21:
                    if bounds[0]!=bounds[1]:
                        raise AssertionError("WSP124_Y_UNIDENTIFIED")
                    w[17]=bounds[0]
            else:
                if residue:
                    raise ValueError("WSP124_NEGATIVE_CONFIRMATION_FAILED")
        self.seen.add(key)
        self.events.append(row[:])
        self.counts[d]+=1

    def observe(self,view,event):
        if (getattr(view,"seed",None) not in FIT
                or getattr(view,"domain",None)!=view.seed-128900
                or getattr(event,"seed",None)!=view.seed
                or getattr(event,"domain",None)!=view.domain
                or type(getattr(event,"subject",None)) is not int
                or event.subject not in view.legal
                or (getattr(event,"left",None),getattr(event,"right",None))
                    !=view.pair(event.subject)
                or type(getattr(event,"effect",None)) is not int
                or not 0<=event.effect<8
                or not _receipt(getattr(event,"source_sha256",None))):
            raise ValueError("WSP124_UNVERIFIED_INTERVENTION_RECORD")
        self._apply([event.seed,event.domain,event.subject,event.left,
                     event.right,event.effect,event.source_sha256])

    def infer_pair(self,domain,left,right):
        if (type(domain) is not int or not 0<=domain<DOMAINS
                or type(left) is not int or not 0<=left<8
                or type(right) is not int or not 0<=right<8):
            raise ValueError("WSP124_BAD_PUBLIC_PAIR")
        if self.counts[domain]!=23:
            return None
        w=self.weights[domain]
        if any(value<0 for value in w):
            raise AssertionError("WSP124_INCOMPLETE_REPAIR_STATE")
        return w[left]^w[8+right]^(w[18] if left>=w[16] and right>=w[17] else 0)

    def infer(self,view,subject):
        return self.infer_pair(view.domain,*view.pair(subject))

    def snapshot(self):
        body={"schema":SCHEMA,"events":self.events,
              "weights":{str(d):list(w) for d,w in self.weights.items()},
              "counts":self.counts,"bounds":self.bounds}
        return canonical({"payload":body,"sha256":digest(body)})

    @classmethod
    def restore(cls,contents):
        try:
            outer=json.loads(contents)
            body=outer["payload"]
            if body.get("schema")!=SCHEMA or outer.get("sha256")!=digest(body):
                raise ValueError("WSP124_COLD_DIGEST_INVALID")
            rows=body["events"]
            if type(rows) is not list:
                raise ValueError("WSP124_COLD_HISTORY_FORMAT")
            result=cls()
            for row in rows:
                result._apply(row)
            fresh=json.loads(result.snapshot())["payload"]
            if fresh!=body:
                raise ValueError("WSP124_COLD_REPLAY_MISMATCH")
            return result
        except (KeyError,TypeError,AttributeError,IndexError) as exc:
            raise ValueError("WSP124_COLD_FORMAT_INVALID") from exc
