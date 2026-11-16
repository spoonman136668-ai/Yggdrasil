"""WSP130 direct source-blind numerical weight construction and repair.

Learns all 93 low-order ANF weights from ordered consequences, then allocates
one previously absent 4/5-way causal conjunction support from nine new effects.
No source labels, true high masks, scorer or symbolic reference are imported.
"""
from __future__ import annotations
from hashlib import sha256
import json

SCHEMA="wsp130.direct-causal-highorder.v1"
LOW=tuple(sorted((x for x in range(256) if x.bit_count()<=3),
                 key=lambda x:(x.bit_count(),x)))
CORE=(255,)+tuple(255^(1<<i) for i in range(8))
HASH_AUDIT=tuple(sorted((x for x in range(256) if x not in set(LOW+CORE)),
    key=lambda x:(sha256(("WSP130|AUDIT|"+str(x)).encode()).digest(),x)))
assert len(LOW)==93 and len(CORE)==9 and len(HASH_AUDIT)==154

def _canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"))

def _digest(x):
    return sha256(_canon(x).encode()).hexdigest()

def _low_table(bits):
    cells=[(bits>>i)&1 if i<len(LOW) else 0 for i in range(256)]
    # Direct packed coefficients index in LOW order, not numerical order.
    data=[0]*256
    for i,mask in enumerate(LOW):
        data[mask]=(bits>>i)&1
    for k in range(8):
        bit=1<<k
        for x in range(256):
            if x&bit:
                data[x]^=data[x^bit]
    return tuple(data)

class _Law:
    def __init__(self,view,policy):
        self.view=view
        self.policy=policy
        self.events=[]
        self.seen=set()
        self.observed={}
        self.coeff_bits=0
        self.base=None
        self.mask=None
        self.status="LEARNING_LOWER"
        self.receipt=_digest([view.fingerprint(),"begin"])

    def _phase3(self):
        remaining=[x for x in range(256) if x not in self.seen]
        if self.policy=="active" and self.status=="SINGLE":
            high=sorted((x for x in remaining if x&self.mask==self.mask),
                        key=lambda x:(-x.bit_count(),x))
            return tuple(high)+tuple(x for x in HASH_AUDIT if x not in self.seen and x not in high)
        return tuple(x for x in HASH_AUDIT if x not in self.seen)

    def choose_x(self):
        n=len(self.events)
        if n>=128: return None
        if n<93: return LOW[n]
        if n<102: return CORE[n-93]
        tail=self._phase3()
        if not tail:
            raise AssertionError("WSP130_SOURCE_BUDGET_UNFILLED")
        return tail[0]

    def _base_value(self,x):
        if self.base is None:
            raise ValueError("WSP130_SOURCE_EFFECT_BEFORE_LOWER_FIT")
        return self.base[x]

    def _expected(self,x):
        value=self._base_value(x)
        if self.status=="SINGLE":
            return value^int(x&self.mask==self.mask)
        if self.status=="NONE":
            return value
        return None

    def _infer_structure(self):
        residual={x:(self.observed[x]^self._base_value(x)) for x in CORE}
        if residual[255]:
            mask=0
            for i in range(8):
                if residual[255^(1<<i)]==0:
                    mask|=1<<i
            if mask.bit_count() in (4,5) and all(
                    residual[x]==int(x&mask==mask) for x in CORE):
                self.status="SINGLE"
                self.mask=mask
            else:
                self.status="UNSUPPORTED"
                self.mask=None
        elif all(residual[255^(1<<i)]==0 for i in range(8)):
            self.status="NONE"
            self.mask=None
        else:
            self.status="UNSUPPORTED"
            self.mask=None

    def ingest(self,raw):
        if (type(raw) is not list or len(raw)!=6 or
                any(type(v) is not int for v in raw[:5]) or
                type(raw[5]) is not str or len(raw[5])!=64 or
                any(ch not in "0123456789abcdef" for ch in raw[5]) or
                raw[0]!=self.view.seed or raw[1]!=self.view.law_id or
                raw[4] not in (0,1)):
            raise ValueError("WSP130_EVIDENCE_INVALID")
        seed,law,subject,x,bit,receipt=raw
        if self.view.subject(x)!=subject or x!=self.choose_x():
            raise ValueError("WSP130_WRONG_ORDER_OR_DUPLICATE_EVIDENCE")
        if _digest([self.receipt,raw[:5]])!=receipt:
            raise ValueError("WSP130_EVIDENCE_RECEIPT_CHAIN_INVALID")
        n=len(self.events)
        self.events.append(raw[:])
        self.seen.add(x)
        self.observed[x]=bit
        self.receipt=receipt
        if n<93:
            coefficient=bit
            for idx,mask in enumerate(LOW[:n]):
                if x&mask==mask:
                    coefficient^=(self.coeff_bits>>idx)&1
            self.coeff_bits|=coefficient<<n
            if len(self.events)==93:
                self.base=_low_table(self.coeff_bits)
                self.status="DIAGNOSTIC"
        elif n<102:
            if len(self.events)==102:
                self._infer_structure()
        elif self.status in ("SINGLE","NONE"):
            if bit!=self._expected(x):
                self.status="UNSUPPORTED"
                self.mask=None

    def infer(self,view,subject):
        x=view.input(subject)
        if self.base is None: return None
        return self._expected(x)

    def payload(self):
        return {"law_id":self.view.law_id,"seed":self.view.seed,"policy":self.policy,
                "events":self.events,"low_coeff_bits_hex":hex(self.coeff_bits),
                "high_mask":self.mask,"status":self.status,"receipt":self.receipt}

class DirectInducer:
    def __init__(self,policy="active"):
        if policy not in ("active","fixed"):
            raise ValueError("WSP130_INVALID_POLICY")
        self.policy=policy
        self.states={}

    def _state(self,view,create=False):
        if (getattr(view,"cohort",None) not in ("probe","transfer") or
                type(getattr(view,"law_id",None)) is not int or
                not 0<=view.law_id<144):
            raise PermissionError("WSP130_INVALID_LAW_VIEW")
        if view.law_id not in self.states and create:
            if view.cohort!="probe":
                raise PermissionError("WSP130_TRANSFER_NOT_TRAINABLE")
            self.states[view.law_id]=_Law(view,self.policy)
        return self.states.get(view.law_id)

    def choose(self,view,available):
        if view.cohort!="probe":
            raise PermissionError("WSP130_TRANSFER_SOURCE_CALL_DENIED")
        st=self._state(view,create=True)
        if st.view is not view:
            raise ValueError("WSP130_CUSTODY_PUBLIC_VIEW_DRIFT")
        x=st.choose_x()
        if x is None: return None
        subject=view.subject(x)
        if subject not in available:
            raise ValueError("WSP130_QUERY_ALREADY_USED")
        return subject

    def observe(self,view,evidence):
        if (view.cohort!="probe" or
                getattr(evidence,"seed",None)!=view.seed or
                getattr(evidence,"law_id",None)!=view.law_id or
                type(getattr(evidence,"subject",None)) is not int or
                evidence.subject not in view.legal or
                view.input(evidence.subject)!=getattr(evidence,"input",None) or
                type(getattr(evidence,"effect",None)) is not int or
                evidence.effect not in (0,1)):
            raise ValueError("WSP130_UNVERIFIED_TYPED_SOURCE_OUTCOME")
        st=self._state(view,create=True)
        if st.view is not view:
            raise ValueError("WSP130_SOURCE_VIEW_MISMATCH")
        st.ingest([evidence.seed,evidence.law_id,evidence.subject,
                   evidence.input,evidence.effect,evidence.receipt])

    def infer(self,view,subject):
        st=self._state(view)
        return None if st is None else st.infer(view,subject)

    def status(self,view):
        st=self._state(view)
        return None if st is None else st.status

    def support(self,view):
        st=self._state(view)
        return None if st is None else st.mask

    def snapshot(self):
        p={"schema":SCHEMA,"policy":self.policy,
           "states":{str(k):self.states[k].payload() for k in sorted(self.states)}}
        return _canon({"payload":p,"sha256":_digest(p)})

    @classmethod
    def restore(cls,snapshot,view_resolver):
        try:
            outer=json.loads(snapshot)
            body=outer["payload"]
            if body["schema"]!=SCHEMA or outer["sha256"]!=_digest(body):
                raise ValueError("WSP130_SNAPSHOT_DIGEST_INVALID")
            model=cls(body["policy"])
            for key in sorted(body["states"],key=int):
                if str(int(key))!=key:
                    raise ValueError("WSP130_SNAPSHOT_LAW_INDEX")
                payload=body["states"][key]
                view=view_resolver(payload["seed"])
                st=model._state(view,create=True)
                for record in payload["events"]:
                    st.ingest(record)
                if st.payload()!=payload:
                    raise ValueError("WSP130_FORGED_LEARNED_NUMERICAL_WEIGHTS")
            return model
        except (TypeError,KeyError,AttributeError,IndexError) as exc:
            raise ValueError("WSP130_SNAPSHOT_MALFORMED") from exc
