"""WSP131 source-blind direct numeric semantic role-binding weights.

Old causal weights are immutable WSP130 learned state. The new learned parameters
are 720 packed binary identity-permutation hypotheses, updated only by observed
external consequence bits. No source/evaluator/true mapping imported.
"""
from __future__ import annotations
from functools import lru_cache
from hashlib import sha256
from itertools import permutations
import json
from types import SimpleNamespace

PERMS=tuple(permutations(range(6)))
FULL=(1<<720)-1
STAGES=(0,4,8,16,32)
SCHEMA="wsp131.semantic-binding-packed-permutation.v1"

def canon(x):return json.dumps(x,sort_keys=True,separators=(",",":"))
def digest(x):return sha256(canon(x).encode("utf8")).hexdigest()

def _permute(x,mapping):
    y=x&192
    for i in range(6):
        y|=((x>>i)&1)<<mapping[i]
    return y

class _PredView:
    cohort="transfer"
    def __init__(self,law_id):
        self.law_id=law_id
    def input(self,subject):
        if type(subject) is not int or not 0<=subject<256:
            raise ValueError("WSP131_BAD_ORIGINAL_PREDICTION_INPUT")
        return subject

class _HypothesisBank:
    def __init__(self,prior,law):
        public_view=_PredView(law)
        self.base=tuple(prior.infer(public_view,i) for i in range(256))
        if any(type(v) is not int or v not in (0,1) for v in self.base):
            raise ValueError("WSP131_WARM_PRIOR_NOT_FULLY_LEARNED")
        self.sha=digest(self.base)
        one=[0]*256
        for i,mapping in enumerate(PERMS):
            power=1<<i
            for x in range(256):
                if self.base[_permute(x,mapping)]:
                    one[x]|=power
        self.one=tuple(one)

class _World:
    def __init__(self,view,bank):
        self.view=view
        self.bank=bank
        self.weights=FULL
        self.seen=set()
        self.events=[]
        self.receipt=digest([view.fingerprint(),"begin"])
    def choose_x(self):
        if len(self.events)>=32:
            return None
        if self.weights.bit_count()<2:
            return next(x for x in range(256) if x not in self.seen)
        num=self.weights.bit_count()
        winner=None;best=-1
        for x in range(256):
            if x in self.seen:continue
            ones=(self.weights & self.bank.one[x]).bit_count()
            split=min(ones,num-ones)
            if split>best:
                winner=x;best=split
        return winner
    def ingest(self,event):
        if (type(event) is not list or len(event)!=6 or
                any(type(v) is not int for v in event[:5]) or
                type(event[5]) is not str or len(event[5])!=64 or
                any(c not in "0123456789abcdef" for c in event[5]) or
                event[0]!=self.view.seed or event[1]!=self.view.law_id or
                event[4] not in (0,1)):
            raise ValueError("WSP131_INVALID_EVIDENCE")
        seed,law,subject,x,bit,receipt=event
        if self.view.subject(x)!=subject or x!=self.choose_x():
            raise ValueError("WSP131_INVALID_ACTION_ORDER_OR_REPLAY")
        if receipt!=digest([self.receipt,event[:5]]):
            raise ValueError("WSP131_INVALID_ACTION_RECEIPT_CHAIN")
        self.receipt=receipt
        self.seen.add(x)
        self.events.append(event[:])
        one=self.bank.one[x]
        self.weights &= one if bit else (FULL^one)
    def infer(self,x):
        if not self.weights:return None
        one=self.weights & self.bank.one[x]
        if one==self.weights:return 1
        if one==0:return 0
        return None
    def resolved(self):
        return bool(self.weights) and all(
            (self.weights & one) in (0,self.weights) for one in self.bank.one)
    def payload(self):
        return {"seed":self.view.seed,"law_id":self.view.law_id,
                "events":self.events,"candidate_weight_hex":hex(self.weights),
                "prior_truth_sha256":self.bank.sha,
                "receipt":self.receipt}

class NativeBinder:
    def __init__(self,prior):
        self.prior=prior
        self.banks={}
        self.states={}
        self.first_binding_by_law={}
    def _bank(self,law):
        if law not in self.banks:
            self.banks[law]=_HypothesisBank(self.prior,law)
        return self.banks[law]
    def _state(self,view,create=False):
        if (getattr(view,"cohort",None) not in ("probe","transfer") or
                type(getattr(view,"law_id",None)) is not int or
                not 0<=view.law_id<128):
            raise PermissionError("WSP131_INVALID_TYPED_VIEW")
        if view.cohort=="transfer":
            return self.first_binding_by_law.get(view.law_id)
        st=self.states.get(view.seed)
        if st is None and create:
            st=_World(view,self._bank(view.law_id))
            self.states[view.seed]=st
            # Chronology, not a hidden-source mode or seed-classification:
            # first learned binding for this law is immutable across later worlds.
            self.first_binding_by_law.setdefault(view.law_id,st)
        elif st is not None and st.view is not view:
            raise ValueError("WSP131_CHANGED_PUBLIC_VIEW")
        return st
    def choose(self,view,available):
        if view.cohort!="probe":
            raise PermissionError("WSP131_NO_TRANSFER_SOURCE_ACTIONS")
        st=self._state(view,True)
        x=st.choose_x()
        if x is None:return None
        subject=view.subject(x)
        if subject not in available:
            raise ValueError("WSP131_ACTION_NOT_AVAILABLE")
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
            raise ValueError("WSP131_UNVERIFIED_SOURCE_CONSEQUENCE")
        st=self._state(view,True)
        st.ingest([evidence.seed,evidence.law_id,evidence.subject,
                   evidence.input,evidence.effect,evidence.receipt])
    def infer(self,view,subject):
        st=self._state(view)
        return None if st is None else st.infer(view.input(subject))
    def resolved(self,view):
        st=self._state(view)
        return bool(st is not None and st.resolved())
    def remaining(self,view):
        st=self._state(view)
        return None if st is None else st.weights.bit_count()
    def snapshot(self):
        body={"schema":SCHEMA,"states":{str(seed):st.payload()
              for seed,st in sorted(self.states.items())},
              "first_binding_by_law":{str(law):st.view.seed
              for law,st in sorted(self.first_binding_by_law.items())}}
        return canon({"payload":body,"sha256":digest(body)})
    @classmethod
    def restore(cls,prior,snapshot,resolver):
        try:
            obj=json.loads(snapshot)
            body=obj["payload"]
            if obj["sha256"]!=digest(body) or body["schema"]!=SCHEMA:
                raise ValueError("WSP131_SNAPSHOT_DIGEST_INVALID")
            m=cls(prior)
            for seed in sorted(body["states"],key=int):
                if str(int(seed))!=seed:
                    raise ValueError("WSP131_NONCANONICAL_SEED")
                expected=body["states"][seed]
                view=resolver(int(seed))
                st=m._state(view,True)
                for event in expected["events"]:
                    st.ingest(event)
                if st.payload()!=expected:
                    raise ValueError("WSP131_FORGED_PERMUTATION_WEIGHTS")
            first={str(law):st.view.seed for law,st in sorted(
                m.first_binding_by_law.items())}
            if first!=body["first_binding_by_law"]:
                raise ValueError("WSP131_FORGED_REBINDING_CUSTODY")
            return m
        except (TypeError,AttributeError,KeyError,IndexError) as exc:
            raise ValueError("WSP131_SNAPSHOT_MALFORMED") from exc
