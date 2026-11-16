"""Direct non-gradient GF(2) latent relation weights, source-blind.

State starts without any learned factors. Each independent measured residual
row creates one extra 16-bit numerical factor, up to four under the
inductively supplied rank<=4 physics. Evidence and immutable cold replay
are separate from the coefficient-only storage count.
"""
from __future__ import annotations
from array import array
from hashlib import sha256
import json

SCHEMA="wsp126.direct-rank-growth.v1"


def _canon(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"))


def _digest(value):
    return sha256(_canon(value).encode()).hexdigest()


def _receipt_valid(v):
    return (type(v) is str and len(v)==64 and
            all(c in "0123456789abcdef" for c in v))


def _valid_row(row):
    return (type(row) is list and len(row)==7 and
            type(row[0]) is int and 132000<=row[0]<132128 and
            type(row[1]) is int and row[1]==row[0]-132000 and
            type(row[2]) is int and row[2]>=0 and
            all(type(x) is int and 0<=x<16 for x in row[3:5]) and
            type(row[5]) is int and row[5] in (0,1) and
            _receipt_valid(row[6]))


class _Law:
    def __init__(self):
        self.events=[]
        self.seen=set()
        self.observed=[{} for _ in range(16)]
        self.factors={}  # pivot column -> 16-bit GF(2) basis row
        self.rows=[None]*16
        self.codes=array("i",[-1]*16)

    def _columns(self):
        pivots=sorted(self.factors,reverse=True)
        return tuple((pivots+[c for c in range(16)
                              if c not in pivots])[:4])

    def next_pair(self):
        n=len(self.events)
        if n<128:
            return (n//16,n%16)
        if n<160:
            row=8+(n-128)//4
            col=self._columns()[(n-128)%4]
            return (row,col)
        return None

    def _add_factor(self,mask):
        remainder=mask
        for bit in sorted(self.factors,reverse=True):
            if remainder & (1<<bit):
                remainder ^= self.factors[bit]
        if remainder:
            pivot=remainder.bit_length()-1
            if pivot in self.factors or len(self.factors)>=4:
                raise ValueError("WSP126_REPRESENTATION_RANK_OVER_BUDGET")
            self.factors[pivot]=remainder

    def _reconstruct_row(self,a):
        if len(self.factors)!=4:
            return
        basis=[self.factors[bit] for bit in sorted(self.factors,reverse=True)]
        candidates=[]
        for code in range(16):
            candidate=0
            for bit in range(4):
                if code & (1<<bit):
                    candidate ^= basis[bit]
            if all(((candidate>>col)&1)==effect
                   for col,effect in self.observed[a].items()):
                candidates.append((code,candidate))
        if len(candidates)!=1:
            raise ValueError("WSP126_PIVOT_ROW_NOT_IDENTIFIABLE")
        self.codes[a],self.rows[a]=candidates[0]

    def ingest(self,event):
        if not _valid_row(event):
            raise ValueError("WSP126_INVALID_COLD_SOURCE_EVENT")
        seed,law,subject,a,b,outcome,_=event
        if self.next_pair()!=(a,b):
            raise ValueError("WSP126_UNFROZEN_ACTION_ORDER")
        if (seed,subject) in self.seen or b in self.observed[a]:
            raise ValueError("WSP126_DUPLICATE_CAUSAL_ACTION")
        self.events.append(event[:])
        self.seen.add((seed,subject))
        self.observed[a][b]=outcome
        if a<8 and len(self.observed[a])==16:
            row_mask=sum(effect<<col for col,effect in self.observed[a].items())
            self.rows[a]=row_mask
            self._add_factor(row_mask)
        if a>=8 and len(self.observed[a])==4:
            self._reconstruct_row(a)

    def infer(self,a,b):
        if self.rows[a] is not None:
            return (self.rows[a]>>b)&1
        # No extrapolation from less than a four-dimensional witnessed
        # span: an unseen factor can be hidden by current observations.
        if b in self.observed[a]:
            return self.observed[a][b]
        return None

    def payload(self):
        return {"events":self.events,
                "factors":{str(k):self.factors[k] for k in sorted(self.factors)},
                "rows":self.rows,
                "codes":list(self.codes),
                "factor_slots":len(self.factors)}


class DirectRankGrowth:
    def __init__(self):
        self.state={}

    def _state(self,law_id):
        if type(law_id) is not int or not 0<=law_id<128:
            raise ValueError("WSP126_INVALID_LAW_ID")
        if law_id not in self.state:
            self.state[law_id]=_Law()
        return self.state[law_id]

    def choose(self,view,available):
        if (getattr(view,"cohort",None)!="fit" or
                view.seed!=132000+view.law_id):
            raise PermissionError("WSP126_ACTIONS_ONLY_FIT")
        st=self._state(view.law_id)
        pair=st.next_pair()
        if pair is None:
            return None
        action=view.subject(*pair)
        if action not in available or (view.seed,action) in st.seen:
            raise ValueError("WSP126_ACTION_ALREADY_CONSUMED")
        return action

    def observe(self,view,evidence):
        if (getattr(view,"cohort",None)!="fit" or
                view.seed!=132000+view.law_id or
                getattr(evidence,"seed",None)!=view.seed or
                getattr(evidence,"law_id",None)!=view.law_id or
                type(getattr(evidence,"subject",None)) is not int or
                evidence.subject not in view.legal or
                view.pair(evidence.subject)!=
                    (getattr(evidence,"left",None),
                     getattr(evidence,"right",None)) or
                type(getattr(evidence,"effect",None)) is not int or
                evidence.effect not in (0,1) or
                not _receipt_valid(getattr(evidence,"source_sha256",None))):
            raise ValueError("WSP126_UNVERIFIED_SOURCE_CONSEQUENCE")
        self._state(view.law_id).ingest(
            [evidence.seed,evidence.law_id,evidence.subject,
             evidence.left,evidence.right,evidence.effect,evidence.source_sha256])

    def infer(self,view,subject):
        a,b=view.pair(subject)
        return self._state(view.law_id).infer(a,b)

    @property
    def factor_slots(self):
        return sum(len(st.factors) for st in self.state.values())

    @property
    def row_code_slots(self):
        return len(self.state)*16

    @property
    def rank4_laws(self):
        return sum(len(st.factors)==4 for st in self.state.values())

    def snapshot(self):
        data={"schema":SCHEMA,
              "states":{str(k):v.payload()
                        for k,v in sorted(self.state.items())}}
        return _canon({"payload":data,"sha256":_digest(data)})

    @classmethod
    def restore(cls,contents):
        try:
            outer=json.loads(contents)
            body=outer["payload"]
            if body.get("schema")!=SCHEMA or outer.get("sha256")!=_digest(body):
                raise ValueError("WSP126_COLD_DIGEST_INVALID")
            states=body["states"]
            if type(states) is not dict:
                raise ValueError("WSP126_COLD_STATE_FORMAT")
            recovered=cls()
            for key in sorted(states,key=int):
                if str(int(key))!=key or not 0<=int(key)<128:
                    raise ValueError("WSP126_COLD_BAD_LAW_KEY")
                expected=states[key]
                if type(expected) is not dict or type(expected.get("events")) is not list:
                    raise ValueError("WSP126_COLD_NO_EVENTS")
                st=recovered._state(int(key))
                for event in expected["events"]:
                    if not _valid_row(event) or event[1]!=int(key):
                        raise ValueError("WSP126_COLD_BAD_EVENT")
                    st.ingest(event)
                if st.payload()!=expected:
                    raise ValueError("WSP126_COLD_FABRICATED_LATENT_FACTOR")
            return recovered
        except (KeyError,TypeError,AttributeError,IndexError) as exc:
            raise ValueError("WSP126_COLD_FORMAT") from exc
