"""CKAD-SHARED-V2 opt-in tokenless cumulative causal operator-memory.

Training worlds provide compatible general program structures, with local
XOR coefficients and biases marginalized. No source generator is imported.
This module never sees a correct gate or truth-family label.
"""
import json
from yggdrasil.native_hypothesis_portfolio import (
    NativeHypothesisPortfolio,ALL_CANDIDATES,SCHEMA as LOCAL_SCHEMA,
    GATES,grammar,votes,canonical,digest,require,pin,SOURCE_MODE)

SCHEMA="yggdrasil.ckad.shared-operator-v2.v1"
FIT_WORLDS=16
GATE_COUNT=len(GATES)
FULL_GATE_SUPPORT=(1<<GATE_COUNT)-1
GATE_BANK=tuple(
    sum(1<<j for j,(_,gate,_) in enumerate(grammar()) if gate==g)
    for g in GATES)
BANK_TO_GATE={gate:i for i,gate in enumerate(GATES)}

def gate_support(programs):
    """Marginalize local program coefficients/biases without source labels."""
    require(type(programs) is int and programs>=0,"PROGRAMS")
    return sum((1<<i) for i,b in enumerate(GATE_BANK) if programs&b)

def program_scope(gates):
    require(type(gates) is int and 0<=gates<=FULL_GATE_SUPPORT,
            "GATE_SUPPORT")
    out=0
    for i,bank in enumerate(GATE_BANK):
        if gates&(1<<i):
            out |= bank
    return out

def unanimous(programs,m):
    require(type(m) is int and 0<=m<64,"INPUT")
    if not programs:
        return None
    one=programs&votes()[m]
    if not one:
        return 0
    if one==programs:
        return 1
    return None

class NativeSharedOperatorMemory:
    __slots__=("_local","_gate_support","_fit_count","_frozen")
    def __init__(self,local=None,gate_mask=FULL_GATE_SUPPORT,
                 fit_count=0,frozen=False):
        self._local=local if local is not None else NativeHypothesisPortfolio()
        self._gate_support=gate_mask
        self._fit_count=fit_count
        self._frozen=frozen

    @property
    def global_gate_support(self):
        return self._gate_support

    @property
    def fit_worlds(self):
        return self._fit_count

    def observe(self,slot,input_mask,outcome,source_sha):
        """Append one original *fabricated* witnessed consequence to a slot."""
        require(type(slot) is int and 0<=slot<64,"SLOT")
        if self._frozen:
            require(slot>=FIT_WORLDS,"FIT_IMMUTABLE")
        else:
            require(slot==self._fit_count and slot<FIT_WORLDS,
                    "FIT_STAGE_ORDER")
        local=self._local.observe(slot,input_mask,outcome,source_sha)
        return NativeSharedOperatorMemory(local,self._gate_support,
                                          self._fit_count,self._frozen)

    def seal_fit_world(self,slot):
        require(not self._frozen and type(slot) is int
                and slot==self._fit_count and slot<FIT_WORLDS,
                "FIT_WORLD_ORDER")
        s=self._local._state(slot)
        require(s[3]==16 and s[0] and s[1].bit_count()==16,
                "FIT_NOT_QUALIFIED")
        gates=gate_support(s[0])
        require(gates>0,"FIT_INCONSISTENT")
        nxt=self._gate_support&gates
        require(nxt>0,"NO_SHARED_OPERATOR")
        return NativeSharedOperatorMemory(self._local,nxt,
                                           self._fit_count+1,False)

    def freeze(self):
        require(not self._frozen and self._fit_count==FIT_WORLDS,
                "NOT_ALL_FIT")
        return NativeSharedOperatorMemory(self._local,self._gate_support,
                                          self._fit_count,True)

    def candidate_bits(self,slot,use_global=True,gate_override=None):
        require(gate_override is None or (type(gate_override) is int
                and 0<=gate_override<=FULL_GATE_SUPPORT),"OVERRIDE")
        raw=self._local._state(slot)[0]
        if not use_global:
            return raw
        if gate_override is not None:
            return raw&program_scope(gate_override)
        return raw&program_scope(self._gate_support)

    def predict(self,slot,m,use_global=True,gate_override=None):
        return unanimous(self.candidate_bits(slot,use_global,gate_override),m)

    def vector(self,slot,use_global=True,gate_override=None):
        bank=self.candidate_bits(slot,use_global,gate_override)
        return tuple(unanimous(bank,m) for m in range(64))

    def count(self,slot,use_global=True):
        return self.candidate_bits(slot,use_global).bit_count()

    def details(self,slot):
        info=self._local.details(slot)
        return dict(info,global_gates=self._gate_support.bit_count(),
                    global_candidates=self.count(slot,True),
                    global_frozen=self._frozen,fit_worlds=self._fit_count)

    def checkpoint(self):
        raw_local=self._local.checkpoint()
        doc={"schema":SCHEMA,"local_sha256":digest(raw_local),
             "local_ascii":raw_local.decode("ascii"),
             "gate_mask":self._gate_support,
             "fit_count":self._fit_count,"frozen":self._frozen,
             "source_mode":SOURCE_MODE,"accepted_native":False,
             "scientific_pass":False}
        raw=canonical(doc)
        require(len(raw)<=256*1024,"CAPACITY")
        return raw

    @classmethod
    def restore(cls,raw,sha):
        require(type(raw) is bytes and len(raw)<=256*1024
                and pin(sha) and digest(raw)==sha,"COLD_SHA")
        def unique(pairs):
            d={}
            for k,v in pairs:
                require(k not in d,"DUPLICATE_JSON")
                d[k]=v
            return d
        try:
            doc=json.loads(raw.decode("ascii"),object_pairs_hook=unique)
            require(type(doc) is dict and set(doc)=={
                "schema","local_sha256","local_ascii","gate_mask","fit_count",
                "frozen","source_mode","accepted_native","scientific_pass"},
                "COLD_KEYS")
            require(doc["schema"]==SCHEMA and doc["source_mode"]==SOURCE_MODE
                    and doc["accepted_native"] is False
                    and doc["scientific_pass"] is False
                    and type(doc["gate_mask"]) is int
                    and 0<=doc["gate_mask"]<=FULL_GATE_SUPPORT
                    and type(doc["fit_count"]) is int
                    and 0<=doc["fit_count"]<=FIT_WORLDS
                    and type(doc["frozen"]) is bool
                    and (not doc["frozen"] or doc["fit_count"]==FIT_WORLDS),
                    "COLD_FIELDS")
            sub=doc["local_ascii"].encode("ascii")
            local=NativeHypothesisPortfolio.restore(sub,doc["local_sha256"])
            support=FULL_GATE_SUPPORT
            for slot in range(doc["fit_count"]):
                state=local._state(slot)
                require(state[3]==16,"TRAIN_HISTORY")
                support &=gate_support(state[0])
                require(support>0,"COLD_FIT_INCONSISTENT")
            require(support==doc["gate_mask"],"FORGED_SHARED_OPERATOR")
            if doc["frozen"]:
                require(all(k<FIT_WORLDS or doc["frozen"] for k in local._slots),
                        "LOCAL_STAGE")
            instance=cls(local,doc["gate_mask"],
                         doc["fit_count"],doc["frozen"])
            require(instance.checkpoint()==raw,"COLD_BYTES")
            return instance
        except (ValueError,TypeError,KeyError,AttributeError,UnicodeError) as exc:
            raise ValueError("NATIVE_SHARED_OPERATOR_COLD_REJECTED") from exc
