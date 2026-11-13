"""WSP78 source-blind experience-to-executable-ReLU causal effect programmer.

A physically paid row teaches action-conditioned GF(2) polynomial delta
coefficients. Exact linear constraints yield *numeric learned coefficient
weights* for a fixed degree<=2 ReLU monomial circuit, rather than a table of
observed states. Its cold inference is numeric ReLU forward ONLY: neither
GF2 basis, source rules nor raw paid training ledger is consulted. Query
identifiability is compiled into a second numeric ReLU gate head from PUBLIC
enumerable inputs and paid-experience GF(2) rank, NOT heldout physics labels.

The full fixed-source Boolean grammar is a strong inductive prior; this is
not independent new-feature discovery, general AGI or a proof that numeric
compilation beats an equally expressive symbolic causal hypothesis engine.
"""
from __future__ import annotations
from itertools import combinations,product
from hashlib import sha256
from math import isfinite
import json

STATES=tuple(product((0,1),repeat=6))
ACTIONS=tuple(range(6))
INPUTS=12
OUTPUTS=6
DEGREE=2
MONOMIALS=tuple(
    comb for order in range(DEGREE+1)
    for comb in combinations(range(6),order)
)
assert len(MONOMIALS)==22
MAX_CHARGES=144
MAX_SNAPSHOT_BYTES=600000
SCHEMA="wsp78.learned-neural-parity.v1"


def _canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),
                      ensure_ascii=True,allow_nan=False)


def _state_action(state,action):
    if type(state) is not tuple or state not in STATES or (
        type(action) is not int or action not in ACTIONS):
        raise ValueError("invalid public six-bit physical input")
    return [float(i) for i in state]+[float(action==a) for a in ACTIONS]


def _monomial_mask(state,monomials):
    out=0
    for i,term in enumerate(monomials):
        if all(state[j] for j in term):
            out |= 1<<i
    return out


def _relu(value):
    return value if value>0.0 else 0.0


class CausalWeightProgrammer:
    """All source-side training uses previously PAID action/consequence rows.

    After compile(), numerical hidden_w (monomial ReLU detectors), numerical
    effect_w (LEARNED coefficient weights), and confidence_w/b (trained
    source-blind unlabeled-public-input gate) are sufficient for inference.
    """
    gradient_steps=0

    def __init__(self,degree=DEGREE):
        if type(degree) is not int or degree not in (1,2):
            raise ValueError("unsupported prospectively frozen degree")
        self.degree=degree
        self.monomials=tuple(t for t in MONOMIALS if len(t)<=degree)
        self.count=len(self.monomials)
        self._basis=[{} for _ in ACTIONS]
        self._inconsistent=[False]*len(ACTIONS)
        self.charged_actions=0
        self.current=(0,)*6
        self._compiled=False
        self.hidden_w=[]
        self.hidden_b=[]
        for action in ACTIONS:
            for term in self.monomials:
                row=[0.0]*INPUTS
                for i in term:
                    row[i]=1.0
                row[6+action]=1.0
                self.hidden_w.append(row)
                self.hidden_b.append(float(-len(term)))
        self.effect_w=[[0.0]*len(self.hidden_w) for _ in range(OUTPUTS)]
        self.confidence_w=[]
        self.confidence_b=[]
        self._rank_after_compile=[0]*6

    def charge(self,experience):
        state=experience.before
        action=experience.action
        after=experience.after
        _state_action(state,action)
        _state_action(after,action)
        if (state!=self.current or
            type(experience.action_cost) is not int or experience.action_cost!=1 or
            self.charged_actions>=MAX_CHARGES):
            raise ValueError("nonchronological/unpaid source-side physical action")
        mask=_monomial_mask(state,self.monomials)
        truth=sum(int(state[j]!=after[j])<<j for j in range(6))
        basis=self._basis[action]
        r=truth
        while mask:
            pivot=mask.bit_length()-1
            if pivot in basis:
                mask^=basis[pivot][0]
                r^=basis[pivot][1]
            else:
                basis[pivot]=(mask,r)
                break
        if not mask and r:
            self._inconsistent[action]=True
        self.current=after
        self.charged_actions+=1
        self._compiled=False

    def _identifiable(self,state,action):
        if self._inconsistent[action]:
            return False
        mask=_monomial_mask(state,self.monomials)
        basis=self._basis[action]
        while mask:
            pivot=mask.bit_length()-1
            row=basis.get(pivot)
            if row is None:
                return False
            mask^=row[0]
        return True

    def _coefficients(self,action,bit):
        known=0
        for pivot in sorted(self._basis[action]):
            row,rhs=self._basis[action][pivot]
            # Existing reduced row has lower-index terms; free variables=0.
            value=((rhs>>bit)&1)^((row&known).bit_count()&1)
            if value:
                known|=1<<pivot
        return known

    def compile(self):
        if self.charged_actions not in (96,144):
            raise ValueError("only frozen 96 or 144 paid action compile milestones")
        units=len(self.hidden_w)
        self.effect_w=[[0.0]*units for _ in range(OUTPUTS)]
        for action in ACTIONS:
            for bit in range(OUTPUTS):
                coeff=self._coefficients(action,bit)
                for term in range(self.count):
                    if coeff>>term&1:
                        self.effect_w[bit][action*self.count+term]=1.0
        self.confidence_w=[]
        self.confidence_b=[]
        for state in STATES:
            for action in ACTIONS:
                if self._identifiable(state,action):
                    # Exact-input numeric ReLU indicator: output one iff
                    # all six physical bits and the one-hot action match.
                    row=[float(1 if v else -1) for v in state]
                    row += [float(a==action) for a in ACTIONS]
                    bias=float(sum(1 for v in state if not v)-6)
                    self.confidence_w.append(row)
                    self.confidence_b.append(bias)
        self._rank_after_compile=[len(b) for b in self._basis]
        self._compiled=True
        return {"paid_actions":self.charged_actions,
                "degree":self.degree,
                "constraint_rank":tuple(self._rank_after_compile),
                "inconsistent_actions":tuple(
                    i for i in ACTIONS if self._inconsistent[i]),
                "causal_weight_nonzero":sum(int(bool(z))
                    for row in self.effect_w for z in row),
                "numeric_confidence_detector_units":len(self.confidence_w),
                "learned_numeric_weight_parameters":
                    sum(len(row) for row in self.effect_w)+
                    len(self.confidence_w)*(INPUTS+1)}

    def _numeric_forward(self,state,action):
        x=_state_action(state,action)
        hidden=[_relu(sum(w*v for w,v in zip(row,x))+bias)
                for row,bias in zip(self.hidden_w,self.hidden_b)]
        next_bits=[]
        # Learned effect counts, ReLU sawtooth parity, then ReLU XOR.
        for bit in range(OUTPUTS):
            count=sum(w*h for w,h in zip(self.effect_w[bit],hidden))
            parity=count+sum(
                (2.0 if threshold%2==0 else -2.0)*
                _relu(count-threshold)
                for threshold in range(1,self.count+1))
            nxt=x[bit]+parity-2.0*_relu(x[bit]+parity-1.0)
            if not isfinite(nxt) or abs(nxt-round(nxt))>1e-7:
                raise ArithmeticError("numeric causal circuit violated binary invariant")
            next_bits.append(int(round(nxt)))
        return tuple(next_bits)

    def _numeric_confidence(self,state,action):
        x=_state_action(state,action)
        signal=sum(_relu(sum(w*z for w,z in zip(row,x))+bias)
                   for row,bias in zip(self.confidence_w,self.confidence_b))
        if abs(signal-round(signal))>1e-7 or signal>1.0+1e-7:
            raise ArithmeticError("numeric confidence detector not unique")
        return signal>0.5

    def predict(self,state,action,force=False):
        if not self._compiled or type(force) is not bool:
            raise ValueError("numeric model not compiled / invalid inference request")
        # Always perform physical output numeric forward; uncertainty uses
        # another numeric ReLU head, not a GF2 symbolic test at runtime.
        result=self._numeric_forward(state,action)
        if not force and not self._numeric_confidence(state,action):
            return None
        return result

    def snapshot(self):
        if not self._compiled:
            raise ValueError("cannot save an uncompiled weight program")
        p={"schema":SCHEMA,
           "degree":self.degree,"paid_actions":self.charged_actions,
           "hidden_w":self.hidden_w,"hidden_b":self.hidden_b,
           "effect_w":self.effect_w,
           "confidence_w":self.confidence_w,
           "confidence_b":self.confidence_b}
        self._validate_numeric(p)
        fingerprint=sha256(_canonical(p).encode("ascii")).hexdigest()
        raw=_canonical({"payload":p,"sha256":fingerprint})
        if len(raw)>MAX_SNAPSHOT_BYTES:
            raise OverflowError("source-blind neural weight snapshot too large")
        return raw

    @staticmethod
    def _validate_numeric(p):
        if type(p) is not dict or set(p)!={
            "schema","degree","paid_actions","hidden_w","hidden_b",
            "effect_w","confidence_w","confidence_b"} or p["schema"]!=SCHEMA:
            raise ValueError("invalid neural schema")
        deg=p["degree"]
        if type(deg) is not int or deg not in (1,2):
            raise ValueError("degree invalid")
        count=sum(len(t)<=deg for t in MONOMIALS)
        units=len(ACTIONS)*count
        if (type(p["paid_actions"]) is not int or
            p["paid_actions"] not in (96,144)):
            raise ValueError("physical custody invalid")
        def matrix(arr,rows,cols):
            return (type(arr) is list and len(arr)==rows and
                all(type(x) is list and len(x)==cols and
                    all(type(v) in (int,float) and isfinite(v) for v in x)
                    for x in arr))
        if not matrix(p["hidden_w"],units,INPUTS):
            raise ValueError("hidden matrix invalid")
        if not matrix(p["effect_w"],OUTPUTS,units):
            raise ValueError("causal numerical coefficient matrix invalid")
        if (type(p["hidden_b"]) is not list or len(p["hidden_b"])!=units or
            any(type(v) not in (int,float) or not isfinite(v)
                for v in p["hidden_b"])):
            raise ValueError("hidden bias invalid")
        confident=len(p["confidence_w"])
        if confident>384 or not matrix(p["confidence_w"],confident,INPUTS):
            raise ValueError("numerical confidence matrix invalid")
        if (type(p["confidence_b"]) is not list or
            len(p["confidence_b"])!=confident or
            any(type(v) not in (int,float) or not isfinite(v)
                for v in p["confidence_b"])):
            raise ValueError("confidence bias invalid")

    @classmethod
    def restore(cls,raw):
        if type(raw) is not str or len(raw)>MAX_SNAPSHOT_BYTES:
            raise ValueError("cold weights invalid")
        try:
            doc=json.loads(raw)
            if type(doc) is not dict or set(doc)!={"payload","sha256"}:
                raise ValueError("invalid neural envelope")
            p=doc["payload"]
            cls._validate_numeric(p)
            if sha256(_canonical(p).encode("ascii")).hexdigest()!=doc["sha256"]:
                raise ValueError("numerical weight fingerprint mismatch")
            m=cls(p["degree"])
            m.charged_actions=p["paid_actions"]
            m.hidden_w=p["hidden_w"]
            m.hidden_b=p["hidden_b"]
            m.effect_w=p["effect_w"]
            m.confidence_w=p["confidence_w"]
            m.confidence_b=p["confidence_b"]
            m._compiled=True
            if m.snapshot()!=raw:
                raise ValueError("noncanonical neural matrix snapshot")
            # Restored class intentionally does NOT recreate the training
            # basis or source ledger and is for cold numeric inference.
            return m
        except (ValueError,TypeError,KeyError,UnicodeError,
                json.JSONDecodeError,OverflowError) as exc:
            raise ValueError("tampered/corrupt cold neural weights") from exc
