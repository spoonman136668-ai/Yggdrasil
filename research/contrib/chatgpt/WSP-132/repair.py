"""WSP132 R1: bounded source-blind confidence repair by challenger hypotheses.

Use the exact WSP131 learned original causal truth and same paid 32 actions.
A packed native binder remains immutable; append a distinct conservative
hypothesis-weight layer containing 30 non-permutation shear challengers per
six-variable permutation. Return a confident prediction only on unanimous
consistent readouts. No source/labels/scorer imports; no additional actions.
"""
from __future__ import annotations
from hashlib import sha256
from itertools import permutations
import json

PERMS=tuple(permutations(range(6)))
PAIRS=tuple((a,b) for a in range(6) for b in range(6) if a!=b)
assert len(PERMS)==720 and len(PAIRS)==30
SCHEMA="wsp132.bounded-confidence-r1.v1"

def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"))
def digest(v):return sha256(canon(v).encode("utf8")).hexdigest()
def _map(x,p):
    y=x&192
    for old,new in enumerate(p):
        y|=((x>>old)&1)<<new
    return y
def _shear(y,a,b):
    return y^(((y>>b)&1)<<a)

class _RepairState:
    def __init__(self,view,base,baseline):
        self.view=view
        self.base=tuple(base)
        if len(self.base)!=256 or any(type(bit) is not int or bit not in (0,1)
                                       for bit in self.base):
            raise ValueError("WSP132_PRIOR_NOT_FULLY_LEARNED")
        self.baseline=baseline
        self.old_sha=digest(self.base)
        self.events=tuple(tuple(row) for row in baseline.events)
        if len(self.events)!=32 or len({row[3] for row in self.events})!=32:
            raise ValueError("WSP132_REPAIR_INCOMPLETE_32_ACTIONS")
        self.pure=[]
        weight=baseline.weights
        for index in range(len(PERMS)):
            if weight&(1<<index):
                self.pure.append(index)
        self.shears=[]
        evidence=tuple((row[3],row[4]) for row in self.events)
        for pindex,p in enumerate(PERMS):
            mapped=tuple((_map(x,p),outcome) for x,outcome in evidence)
            for a,b in PAIRS:
                if all(self.base[_shear(z,a,b)]==observed for z,observed in mapped):
                    self.shears.append((pindex,a,b))
        self.shears=tuple(self.shears)
        self.pure=tuple(self.pure)
        self.pred_cache={}
    def infer(self,x):
        if x in self.pred_cache:return self.pred_cache[x]
        agree=None
        for pindex in self.pure:
            bit=self.base[_map(x,PERMS[pindex])]
            if agree is not None and bit!=agree:
                self.pred_cache[x]=None
                return None
            agree=bit
        for pindex,a,b in self.shears:
            bit=self.base[_shear(_map(x,PERMS[pindex]),a,b)]
            if agree is not None and bit!=agree:
                self.pred_cache[x]=None
                return None
            agree=bit
        self.pred_cache[x]=agree
        return agree
    def counts(self):
        return {"pure_compatible":len(self.pure),
                "shear_compatible":len(self.shears)}
    def payload(self):
        return {"seed":self.view.seed,"law_id":self.view.law_id,
                "original_truth_sha256":self.old_sha,
                "source_receipt":self.baseline.receipt,
                "pure_supporters":list(self.pure),
                "shear_supporters":[list(x) for x in self.shears]}

class NumericBoundedRepair:
    def __init__(self,original_binder):
        self.original=original_binder
        self.states={}
        self.first_by_law={}
    def fit(self,view):
        if view.cohort!="probe":raise PermissionError("WSP132_REPAIR_TRANSFER_TRAINING_DENIED")
        st=self.original.states.get(view.seed)
        if st is None or len(st.events)!=32:
            raise ValueError("WSP132_ORIGINAL_BINDER_NOT_COMPLETE")
        old=self.original._bank(view.law_id).base
        repaired=_RepairState(view,old,st)
        self.states[view.seed]=repaired
        self.first_by_law.setdefault(view.law_id,repaired)
    def _state(self,view):
        if getattr(view,"cohort",None)=="transfer":
            return self.first_by_law.get(view.law_id)
        st=self.states.get(view.seed)
        if st is not None and st.view is not view and st.view.fingerprint()!=view.fingerprint():
            raise ValueError("WSP132_REPAIR_PUBLIC_VIEW_TAMPERED")
        return st
    def infer(self,view,subject):
        st=self._state(view)
        return None if st is None else st.infer(view.input(subject))
    def counts(self,view):
        st=self._state(view)
        return None if st is None else st.counts()
    def snapshot(self):
        payload={"schema":SCHEMA,
                 "original_snapshot":self.original.snapshot(),
                 "states":{str(seed):st.payload()
                     for seed,st in sorted(self.states.items())},
                 "first_by_law":{str(law):st.view.seed
                     for law,st in sorted(self.first_by_law.items())}}
        return canon({"payload":payload,"sha256":digest(payload)})
    @classmethod
    def restore(cls,native_prior,snapshot,view_resolver,original_binder_class):
        try:
            obj=json.loads(snapshot)
            payload=obj["payload"]
            if payload["schema"]!=SCHEMA or obj["sha256"]!=digest(payload):
                raise ValueError("WSP132_REPAIR_CHECKSUM_INVALID")
            restored=original_binder_class.restore(
                native_prior,payload["original_snapshot"],view_resolver)
            model=cls(restored)
            for seed in sorted(payload["states"],key=int):
                if seed!=str(int(seed)):
                    raise ValueError("WSP132_NONCANONICAL_SOURCE_SEED")
                expected=payload["states"][seed]
                v=view_resolver(int(seed))
                model.fit(v)
                if model.states[int(seed)].payload()!=expected:
                    raise ValueError("WSP132_REPAIR_FORGED_CHALLENGER_WEIGHTS")
            names={str(law):st.view.seed
                   for law,st in sorted(model.first_by_law.items())}
            if names!=payload["first_by_law"]:
                raise ValueError("WSP132_REPAIR_FROZEN_BINDING_HISTORY_FORGED")
            return model
        except (TypeError,KeyError,IndexError,AttributeError) as exc:
            raise ValueError("WSP132_REPAIR_STATE_MALFORMED") from exc
