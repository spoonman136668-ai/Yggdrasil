"""WSP133 R2 bounded repair: source-blind active alternative-hypothesis audits.

First 16 paid actions use the exact old 720-pure variable binding policy,
then open a 22,320-bit packed causal-hypothesis ledger and spend remaining
16 paid actions maximally separating still-compatible pure/sheared readouts.
No old model weight modification, unseen source labels, paid extra calls or
opaque key decoding.
"""
from __future__ import annotations
from hashlib import sha256
from itertools import permutations
from types import SimpleNamespace
import json

PERMS=tuple(permutations(range(6)))
SHEARS=tuple((a,b) for a in range(6) for b in range(6) if a!=b)
TOTAL=720*(1+len(SHEARS))
SCHEMA="wsp133.active-audit-r2.v1"
assert len(PERMS)==720 and len(SHEARS)==30 and TOTAL==22320

def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"))
def digest(v):return sha256(canon(v).encode("utf8")).hexdigest()
def _permuted(x,p):
    y=x&0xc0
    for i,j in enumerate(p):
        y|=((x>>i)&1)<<j
    return y
def _bit_shear(y,to_bit,from_bit):
    return y^(((y>>from_bit)&1)<<to_bit)

class _OriginalPublic:
    cohort="transfer"
    def __init__(self,law):self.law_id=law
    def input(self,x):
        if type(x) is not int or not 0<=x<256:
            raise ValueError("WSP133_BAD_ORIGINAL_TYPED_INPUT")
        return x

class _State:
    def __init__(self,view,old_truth):
        self.view=view
        self.base=tuple(old_truth)
        if len(self.base)!=256 or any(type(v) is not int or v not in (0,1)
                                       for v in self.base):
            raise ValueError("WSP133_ORIGINAL_KNOWLEDGE_NOT_FULLY_TRAINED")
        self.events=[]
        self.seen=set()
        self.candidates=None
        self.mask=0
        self.receipt=digest([view.fingerprint(),"begin"])
    def value(self,index,x):
        if index<720:
            return self.base[_permuted(x,PERMS[index])]
        flat=index-720
        pindex,pairindex=divmod(flat,len(SHEARS))
        a,b=SHEARS[pairindex]
        y=_permuted(x,PERMS[pindex])
        return self.base[_bit_shear(y,a,b)]
    def audit_candidates(self):
        if len(self.events)!=16:
            raise ValueError("WSP133_AUDIT_BEFORE_16_INTERVENTIONS")
        evidence=[(row[3],row[4]) for row in self.events]
        good=[]
        weights=0
        for index in range(TOTAL):
            if all(self.value(index,x)==y for x,y in evidence):
                good.append(index)
                weights|=1<<index
        self.candidates=good
        self.mask=weights
    def choose_from(self):
        if len(self.events)>=32:return None
        if len(self.events)<16:
            raise ValueError("WSP133_PURE_PRELUDE_HAS_SEPARATE_POLICY")
        if len(self.candidates)<2:
            return next(x for x in range(256) if x not in self.seen)
        best=None
        score=-1
        size=len(self.candidates)
        for x in range(256):
            if x in self.seen:continue
            positive=sum(self.value(i,x) for i in self.candidates)
            balance=min(positive,size-positive)
            if balance>score:
                best=x;score=balance
        if best is None:raise AssertionError("WSP133_EXHAUSTED_ACTIONS")
        return best
    def ingest(self,event):
        if (type(event) is not list or len(event)!=6 or
                any(type(v) is not int for v in event[:5]) or
                type(event[5]) is not str or len(event[5])!=64 or
                event[0]!=self.view.seed or event[1]!=self.view.law_id or
                event[4] not in (0,1) or
                event[3] in self.seen or
                event[2]!=self.view.subject(event[3])):
            raise ValueError("WSP133_INVALID_ACTUAL_EVIDENCE")
        if digest([self.receipt,event[:5]])!=event[5]:
            raise ValueError("WSP133_FAILED_SOURCE_RECEIPT_CHAIN")
        n=len(self.events)
        if n>=32:raise ValueError("WSP133_OVERBUDGET")
        if n>=16 and event[3]!=self.choose_from():
            raise ValueError("WSP133_AUDIT_ACTION_ORDER_INVALID")
        self.receipt=event[5]
        self.events.append(list(event))
        self.seen.add(event[3])
        if n==15:
            self.audit_candidates()
        elif n>=16:
            good=[i for i in self.candidates if self.value(i,event[3])==event[4]]
            self.candidates=good
            self.mask=0
            for i in good:self.mask|=1<<i
    def infer(self,x):
        if self.candidates is None or not self.candidates:return None
        first=self.value(self.candidates[0],x)
        for index in self.candidates[1:]:
            if self.value(index,x)!=first:return None
        return first
    def payload(self):
        return {"seed":self.view.seed,"law_id":self.view.law_id,
                "base_sha256":digest(self.base),"events":self.events,
                "candidate_weights_hex":hex(self.mask),
                "support_count":0 if self.candidates is None else len(self.candidates),
                "source_receipt":self.receipt}

class ActiveCausalAudit:
    def __init__(self,warm_prior,old_legacy_binder_class):
        self.warm_prior=warm_prior
        self.old_legacy_binder_class=old_legacy_binder_class
        self.legacy=old_legacy_binder_class(warm_prior)
        self.states={}
        self.first_by_law={}
        self.base_cache={}
    def _base(self,law):
        if law not in self.base_cache:
            v=_OriginalPublic(law)
            self.base_cache[law]=tuple(self.warm_prior.infer(v,x)
                                       for x in range(256))
        return self.base_cache[law]
    def _state(self,view,create=False):
        if getattr(view,"cohort",None)=="transfer":
            return self.first_by_law.get(view.law_id)
        state=self.states.get(view.seed)
        if state is None and create:
            state=_State(view,self._base(view.law_id))
            self.states[view.seed]=state
            self.first_by_law.setdefault(view.law_id,state)
        elif state is not None and state.view is not view and state.view.fingerprint()!=view.fingerprint():
            raise ValueError("WSP133_CHANGED_SOURCE_VIEW")
        return state
    def choose(self,view,available):
        if view.cohort!="probe":
            raise PermissionError("WSP133_TRANSFER_SOURCE_CALL_DENIED")
        st=self._state(view,True)
        if len(st.events)<16:
            return self.legacy.choose(view,available)
        x=st.choose_from()
        if x is None:return None
        subject=view.subject(x)
        if subject not in available:
            raise ValueError("WSP133_UNAVAILABLE_OR_DUPLICATE_ACTION")
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
            raise ValueError("WSP133_UNAUTHORIZED_OR_INVALID_EVIDENCE")
        st=self._state(view,True)
        if len(st.events)<16:
            self.legacy.observe(view,evidence)
        st.ingest([evidence.seed,evidence.law_id,evidence.subject,
                   evidence.input,evidence.effect,evidence.receipt])
    def infer(self,view,subject):
        st=self._state(view)
        return None if st is None else st.infer(view.input(subject))
    def count(self,view):
        st=self._state(view)
        return None if st is None else st.payload()["support_count"]
    def snapshot(self):
        body={"schema":SCHEMA,
              "states":{str(k):v.payload() for k,v in sorted(self.states.items())},
              "first_by_law":{str(law):s.view.seed
                     for law,s in sorted(self.first_by_law.items())}}
        return canon({"payload":body,"sha256":digest(body)})
    @classmethod
    def restore(cls,warm_prior,legacy_class,snapshot,resolver):
        try:
            obj=json.loads(snapshot);body=obj["payload"]
            if body["schema"]!=SCHEMA or obj["sha256"]!=digest(body):
                raise ValueError("WSP133_SNAPSHOT_DIGEST_INVALID")
            model=cls(warm_prior,legacy_class)
            for k in sorted(body["states"],key=int):
                if str(int(k))!=k:raise ValueError("WSP133_REPLAY_KEY_INVALID")
                v=resolver(int(k))
                for event in body["states"][k]["events"]:
                    action=model.choose(v,set(v.legal)-
                        {v.subject(x) for x in model._state(v,True).seen})
                    if action!=event[2]:
                        raise ValueError("WSP133_REPLAY_ACTION_POLICY_CHANGED")
                    row=SimpleNamespace(seed=event[0],law_id=event[1],
                                        subject=event[2],input=event[3],
                                        effect=event[4],receipt=event[5])
                    model.observe(v,row)
                if model.states[int(k)].payload()!=body["states"][k]:
                    raise ValueError("WSP133_FORGED_NUMERICAL_WEIGHTS")
            first={str(law):st.view.seed for law,st in sorted(model.first_by_law.items())}
            if first!=body["first_by_law"]:
                raise ValueError("WSP133_FORGED_CAUSAL_HISTORY")
            return model
        except (TypeError,AttributeError,KeyError,IndexError) as exc:
            raise ValueError("WSP133_MALFORMED_SNAPSHOT") from exc
