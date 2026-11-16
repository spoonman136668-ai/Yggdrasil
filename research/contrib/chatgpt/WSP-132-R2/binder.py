"""WSP132-R2 source-blind direct 22,320-hypothesis active confidence repair.

The original WSP130 learned causal function is immutable. The entire repair
budget is still exactly 32 paid interventions, now selected for disagreement
across both 720 familiar permutations and 21,600 single-shear challengers.
No source/evaluator import, no hidden law/mapping labels.
"""
from __future__ import annotations
from hashlib import sha256
from itertools import permutations
from functools import lru_cache
import json

PERMS=tuple(permutations(range(6)))
PAIRS=tuple((i,j) for i in range(6) for j in range(6) if i!=j)
TRANSFORMS=tuple((p,i,j) for p in PERMS for i,j in ((-1,-1),*PAIRS))
COUNT=len(TRANSFORMS)
FULL=(1<<COUNT)-1
SCHEMA="wsp132.r2.active-challenger-binder.v1"
assert COUNT==22320

def canon(x):return json.dumps(x,sort_keys=True,separators=(",",":"))
def digest(x):return sha256(canon(x).encode("utf8")).hexdigest()

def _transform(x,p,i,j):
    y=0
    for a,b in enumerate(p):
        y|=((x>>a)&1)<<b
    if i>=0:
        y^=((y>>j)&1)<<i
    return y

@lru_cache(maxsize=1)
def _inverse_mapping():
    # Inputs and outputs of the semantic mapping differ ONLY in their six
    # low feature bits; two high features are never remapped. A 64x64
    # inverse bit-matrix lets us form each 22,320-bit readout by ORing
    # public warm coefficients instead of evaluating 22k programs per input.
    rows=[[0]*64 for _ in range(64)]
    for n,(p,i,j) in enumerate(TRANSFORMS):
        bit=1<<n
        for x in range(64):
            y=_transform(x,p,i,j)
            rows[x][y]|=bit
    for x in range(64):
        if (sum(v.bit_count() for v in rows[x])!=COUNT or
            sum(rows[x])!=FULL):
            raise AssertionError("WSP132_R2_MAPPING_PARTITION_INVALID")
    return tuple(tuple(row) for row in rows)

class _Original:
    cohort="transfer"
    def __init__(self,law):self.law_id=law
    def input(self,x):
        if type(x) is not int or not 0<=x<256:raise ValueError("WSP132R2_INVALID_ORIGIN_INPUT")
        return x

class _Bank:
    def __init__(self,old,law):
        view=_Original(law)
        self.base=tuple(old.infer(view,x) for x in range(256))
        if any(type(v) is not int or v not in (0,1) for v in self.base):
            raise ValueError("WSP132R2_WARM_CAUSAL_PRIOR_INCOMPLETE")
        self.base_sha=digest(self.base)
        matrix=_inverse_mapping()
        ones=[]
        for x in range(256):
            low=x&63
            high=x&192
            value=0
            for y in range(64):
                if self.base[high|y]:
                    value|=matrix[low][y]
            ones.append(value)
        self.positive=tuple(ones)

class _World:
    def __init__(self,view,bank):
        self.view=view
        self.bank=bank
        self.weights=FULL
        self.events=[]
        self.seen=set()
        self.receipt=digest([view.fingerprint(),"begin"])
    def next_x(self):
        if len(self.events)>=32:return None
        n=self.weights.bit_count()
        if n<2:return next(x for x in range(256) if x not in self.seen)
        best=-1;chosen=None
        for x in range(256):
            if x in self.seen:continue
            on=(self.weights&self.bank.positive[x]).bit_count()
            bal=min(on,n-on)
            if bal>best:best=bal;chosen=x
        return chosen
    def add(self,e):
        if (type(e) is not list or len(e)!=6 or
            any(type(k) is not int for k in e[:5]) or
            type(e[5]) is not str or len(e[5])!=64 or
            any(c not in "0123456789abcdef" for c in e[5]) or
            e[0]!=self.view.seed or e[1]!=self.view.law_id or
            e[4] not in (0,1) or
            self.view.subject(e[3])!=e[2] or e[3]!=self.next_x()):
            raise ValueError("WSP132R2_EVIDENCE_ORDER_OR_TYPE_INVALID")
        if digest([self.receipt,e[:5]])!=e[5]:
            raise ValueError("WSP132R2_EVIDENCE_RECEIPT_INVALID")
        self.receipt=e[5]
        x=e[3];self.seen.add(x);self.events.append(e[:])
        mask=self.bank.positive[x]
        self.weights&=mask if e[4] else (FULL^mask)
    def infer(self,x):
        w=self.weights
        if not w:return None
        one=self.bank.positive[x]&w
        if not one:return 0
        if one==w:return 1
        return None
    def compatible(self):return self.weights.bit_count()
    def payload(self):
        return {"seed":self.view.seed,"law":self.view.law_id,
                "events":self.events,"weights_hex":hex(self.weights),
                "prior_sha256":self.bank.base_sha,"receipt":self.receipt}

class ActiveChallengerRepair:
    def __init__(self,prior):
        self.prior=prior
        self.banks={}
        self.states={}
        self.first_by_law={}
    def _bank(self,law):
        if law not in self.banks:self.banks[law]=_Bank(self.prior,law)
        return self.banks[law]
    def _state(self,view,create=False):
        if (getattr(view,"cohort",None) not in ("probe","transfer") or
            type(getattr(view,"law_id",None)) is not int or
            not 0<=view.law_id<128):
            raise PermissionError("WSP132R2_INVALID_SOURCE_VIEW")
        if view.cohort=="transfer":
            return self.first_by_law.get(view.law_id)
        state=self.states.get(view.seed)
        if state is None and create:
            state=_World(view,self._bank(view.law_id))
            self.states[view.seed]=state
            self.first_by_law.setdefault(view.law_id,state)
        elif (state is not None and state.view is not view and
              state.view.fingerprint()!=view.fingerprint()):
            raise ValueError("WSP132R2_SOURCE_VIEW_TAMPER")
        return state
    def choose(self,view,available):
        if view.cohort!="probe":raise PermissionError("WSP132R2_TRANSFER_ACTION_DENIED")
        state=self._state(view,True)
        x=state.next_x()
        if x is None:return None
        subject=view.subject(x)
        if subject not in available:raise ValueError("WSP132R2_DUPLICATE_SOURCE_ACTION")
        return subject
    def observe(self,view,e):
        if (view.cohort!="probe" or
            getattr(e,"seed",None)!=view.seed or
            getattr(e,"law_id",None)!=view.law_id or
            type(getattr(e,"subject",None)) is not int or
            e.subject not in view.legal or
            view.input(e.subject)!=getattr(e,"input",None) or
            type(getattr(e,"effect",None)) is not int or
            e.effect not in (0,1)):
            raise ValueError("WSP132R2_UNVERIFIED_SOURCE_EFFECT")
        self._state(view,True).add([e.seed,e.law_id,e.subject,e.input,e.effect,e.receipt])
    def infer(self,view,subject):
        st=self._state(view)
        return None if st is None else st.infer(view.input(subject))
    def compatible(self,view):
        st=self._state(view)
        return None if st is None else st.compatible()
    def snapshot(self):
        body={"schema":SCHEMA,"states":{str(seed):st.payload() for seed,st in sorted(self.states.items())},
              "first_by_law":{str(law):st.view.seed for law,st in sorted(self.first_by_law.items())}}
        return canon({"payload":body,"sha256":digest(body)})
    @classmethod
    def restore(cls,prior,snapshot,resolver):
        try:
            obj=json.loads(snapshot)
            payload=obj["payload"]
            if payload["schema"]!=SCHEMA or digest(payload)!=obj["sha256"]:
                raise ValueError("WSP132R2_SNAPSHOT_CHECKSUM_MISMATCH")
            model=cls(prior)
            for key in sorted(payload["states"],key=int):
                if str(int(key))!=key:raise ValueError("WSP132R2_SNAPSHOT_SEED_NONCANONICAL")
                expected=payload["states"][key]
                view=resolver(int(key))
                st=model._state(view,True)
                for e in expected["events"]:st.add(e)
                if st.payload()!=expected:
                    raise ValueError("WSP132R2_FORGED_LEARNED_WEIGHTS")
            first={str(law):st.view.seed for law,st in sorted(model.first_by_law.items())}
            if first!=payload["first_by_law"]:
                raise ValueError("WSP132R2_FORGED_FIRST_BINDING")
            return model
        except (TypeError,KeyError,IndexError,AttributeError) as e:
            raise ValueError("WSP132R2_SNAPSHOT_INVALID") from e
