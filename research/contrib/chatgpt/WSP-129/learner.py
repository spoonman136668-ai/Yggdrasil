"""WSP129 source-blind direct numerical hypothesis-weight programming.

Packed bit-vector weights represent all 1,350 available causal compositions.
Learning eliminates incompatible weight hypotheses from actual interventions.
The active policy chooses the next consequence probe by version-space balance.
No import of source or symbolic controls is permitted.
"""
from __future__ import annotations
from functools import lru_cache
from hashlib import sha256
from types import SimpleNamespace
import json

SCHEMA="wsp129.operator-weight-hypotheses.v1"
FIXED=((0,0),(1,0),(2,0),(4,0),(8,0),(0,1),(0,2),(0,4),(0,8),
       (1,1),(1,2),(1,4),(1,8),(2,1),(2,2),(2,4),(2,8),
       (4,1),(4,2),(4,4),(4,8),(8,1),(8,2),(8,4))

def _canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"))

def _digest(x):
    return sha256(_canon(x).encode("utf8")).hexdigest()

def _parity(x,m):
    return (x&m).bit_count()%2

def _effect(a,b,L,R,op,c):
    x,y=_parity(a,L),_parity(b,R)
    if op=="XOR": v=x^y
    elif op=="AND": v=x&y
    elif op=="OR": v=x|y
    else: raise AssertionError("WSP129_UNKNOWN_OPERATOR")
    return v^c

@lru_cache(maxsize=1)
def _bank():
    candidates=tuple((op,L,R,c)
                     for op in ("XOR","AND","OR")
                     for L in range(1,16) for R in range(1,16) for c in range(2))
    if len(candidates)!=1350:
        raise AssertionError("WSP129_WRONG_GRAMMAR_CAPACITY")
    positive=[0]*256
    for i,(op,L,R,c) in enumerate(candidates):
        value=1<<i
        for a in range(16):
            for b in range(16):
                if _effect(a,b,L,R,op,c):
                    positive[16*a+b]|=value
    return candidates,tuple(positive),(1<<len(candidates))-1

class _Law:
    def __init__(self,view,policy):
        self.view=view
        self.id=view.law_id
        self.seed=view.seed
        self.policy=policy
        self.weights=_bank()[2]
        self.events=[]
        self.seen=set()
        self.receipt=_digest([view.fingerprint(),"begin"])

    def choose_pair(self):
        if len(self.events)>=24:
            return None
        if self.policy=="fixed":
            return FIXED[len(self.events)]
        _,ones,full=_bank()
        remaining=self.weights
        count=remaining.bit_count()
        if count<2:
            return next((divmod(i,16) for i in range(256)
                         if i not in self.seen),None)
        best_score=-1
        best_i=None
        for i in range(256):
            if i in self.seen:
                continue
            count_one=(remaining & ones[i]).bit_count()
            balance=min(count_one,count-count_one)
            if balance>best_score:
                best_i=i
                best_score=balance
        if best_i is None:
            raise AssertionError("WSP129_MISSING_CHARGED_ACTION")
        return divmod(best_i,16)

    def ingest(self,event):
        if (type(event) is not list or len(event)!=7 or
                any(type(v) is not int for v in event[:6]) or
                type(event[6]) is not str or len(event[6])!=64 or
                not all(c in "0123456789abcdef" for c in event[6]) or
                event[0]!=self.seed or event[1]!=self.id or
                event[5] not in (0,1)):
            raise ValueError("WSP129_INVALID_EVIDENCE")
        seed,law,subject,a,b,val,receipt=event
        if self.view.subject(a,b)!=subject or (a,b)!=self.choose_pair():
            raise ValueError("WSP129_WRONG_ACTION_ORDER")
        previous=self.receipt
        expected=_digest([previous,event[:6]])
        if receipt!=expected:
            raise ValueError("WSP129_SOURCE_RECEIPT_CHAIN_INCONSISTENT")
        self.receipt=receipt
        pos=16*a+b
        _,one,all_candidates=_bank()
        self.weights &= one[pos] if val else (all_candidates^one[pos])
        self.events.append(event[:])
        self.seen.add(pos)

    def infer(self,view,subject):
        a,b=view.pair(subject)
        _,one,_=_bank()
        w=self.weights
        if not w:
            return None
        intersect=w&one[16*a+b]
        if intersect==0: return 0
        if intersect==w: return 1
        return None

    def operator(self):
        if not self.weights:
            return None
        candidates,_,_=_bank()
        ops=set()
        remaining=self.weights
        while remaining:
            low=remaining & -remaining
            index=low.bit_length()-1
            ops.add(candidates[index][0])
            if len(ops)>1: return None
            remaining-=low
        return next(iter(ops))

    def coefficient_weights(self):
        if self.weights.bit_count()==1:
            return _bank()[0][self.weights.bit_length()-1]
        return None

    def payload(self):
        return {"law":self.id,"seed":self.seed,"policy":self.policy,
                "events":self.events,"weight_mask_hex":hex(self.weights),
                "learned_expression":self.coefficient_weights(),
                "source_receipt":self.receipt}

class HypothesisWeightBank:
    def __init__(self,policy="active"):
        if policy not in ("active","fixed"):
            raise ValueError("WSP129_POLICY_INVALID")
        self.policy=policy
        self.states={}

    def _state(self,view,create=False):
        if (getattr(view,"cohort",None) not in ("probe","transfer") or
                type(getattr(view,"law_id",None)) is not int or
                not 0<=view.law_id<128):
            raise PermissionError("WSP129_VIEW_INVALID")
        if view.law_id not in self.states:
            if not create or view.cohort!="probe":
                return None
            self.states[view.law_id]=_Law(view,self.policy)
        return self.states[view.law_id]

    def choose(self,view,available):
        if view.cohort!="probe":
            raise PermissionError("WSP129_NO_TRANSFER_SOURCE_ACTIONS")
        st=self._state(view,create=True)
        if view.seed!=st.seed:
            raise ValueError("WSP129_SOURCE_VIEW_DRIFT")
        pair=st.choose_pair()
        if pair is None: return None
        subject=view.subject(*pair)
        if subject not in available:
            raise ValueError("WSP129_UNAVAILABLE_SELECTED_ACTION")
        return subject

    def observe(self,view,evidence):
        if (view.cohort!="probe" or
                getattr(evidence,"seed",None)!=view.seed or
                getattr(evidence,"law_id",None)!=view.law_id or
                type(getattr(evidence,"subject",None)) is not int or
                evidence.subject not in view.legal or
                view.pair(evidence.subject)!=
                (getattr(evidence,"left",None),getattr(evidence,"right",None)) or
                type(getattr(evidence,"effect",None)) is not int or
                evidence.effect not in (0,1)):
            raise ValueError("WSP129_UNVERIFIED_EVIDENCE")
        st=self._state(view,create=True)
        if st.seed!=view.seed:
            raise ValueError("WSP129_WRONG_SOURCE_VIEW")
        st.ingest([evidence.seed,evidence.law_id,evidence.subject,
                   evidence.left,evidence.right,evidence.effect,
                   evidence.receipt])

    def infer(self,view,subject):
        st=self._state(view)
        return None if st is None else st.infer(view,subject)

    def operator(self,view):
        st=self._state(view)
        return None if st is None else st.operator()

    def exhausted(self,view):
        st=self._state(view)
        return True if st is None else st.weights==0

    def snapshot(self):
        p={"schema":SCHEMA,"policy":self.policy,
           "states":{str(k):self.states[k].payload() for k in sorted(self.states)}}
        return _canon({"payload":p,"sha256":_digest(p)})

    @classmethod
    def restore(cls,snapshot,resolver):
        try:
            record=json.loads(snapshot)
            p=record["payload"]
            if p["schema"]!=SCHEMA or record["sha256"]!=_digest(p):
                raise ValueError("WSP129_SNAPSHOT_DIGEST_INVALID")
            model=cls(p["policy"])
            for name in sorted(p["states"],key=int):
                if str(int(name))!=name:
                    raise ValueError("WSP129_NONCANONICAL_LAW_ID")
                original=p["states"][name]
                view=resolver(original["seed"])
                st=model._state(view,create=True)
                for e in original["events"]:
                    st.ingest(e)
                if st.payload()!=original:
                    raise ValueError("WSP129_FORGED_HYPOTHESIS_WEIGHTS")
            return model
        except (KeyError,TypeError,IndexError,AttributeError) as exc:
            raise ValueError("WSP129_SNAPSHOT_INVALID") from exc
