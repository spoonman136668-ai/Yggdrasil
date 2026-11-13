"""WSP79 experience-to-numeric ReLU causal weight programming.

SOURCE-BLIND: never imports private physics, test truth or source roles.
For every action/output bit, enumerate ALL sparse GF2 polynomials with
<=3 active public degree<=3 monomials consistent with PAID observations.
Cold inference uses only NUMERICAL ReLU matrices, learned effect weights
and an unlabeled PUBLIC-input numeric ReLU confidence detector. Neither
symbolic hypothesis enumeration nor raw paid observations are consulted
during cold inference. Full search overhead is charged to candidate CPU.
"""
from __future__ import annotations
from itertools import combinations,product
from collections import defaultdict
from hashlib import sha256
from math import isfinite
import json

STATES=tuple(product((0,1),repeat=6))
ACTIONS=tuple(range(6))
DEGREE=3
MAX_TERMS=3
INPUTS=12
OUTPUTS=6
MONOMIALS=tuple(c for d in range(DEGREE+1) for c in combinations(range(6),d))
assert len(MONOMIALS)==42
SCHEMA="wsp79.sparse-causal-numeric-weights.v1"
MAX_SNAPSHOT_BYTES=900000


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),
                      ensure_ascii=True,allow_nan=False)


def valid(state,action):
    if type(state) is not tuple or state not in STATES or (
        type(action) is not int or action not in ACTIONS):
        raise ValueError("illegal public state/action")


def relu(v):
    return v if v>0 else 0.0


def poly_state(state):
    return sum((1<<i) for i,term in enumerate(MONOMIALS)
               if all(state[k] for k in term))


PUBLIC_MONOMIALS={s:poly_state(s) for s in STATES}
MONOMIAL_SETS=tuple(
    sum(1<<j for j in c)
    for degree in range(MAX_TERMS+1)
    for c in combinations(range(len(MONOMIALS)),degree)
)
assert len(MONOMIAL_SETS)==12384


def build_sparse_survivors(rows):
    """Get ALL valid <=3-term effect hypotheses on PAID before/after only.

    rows: unique (public before,public after) for one action, after
    physically paying a step. This is OFFLINE training, not cold inference.
    """
    n=len(rows)
    observed=[0]*len(MONOMIALS)
    effects=[0]*OUTPUTS
    for i,(state,after) in enumerate(rows):
        mask=PUBLIC_MONOMIALS[state]
        for j in range(len(MONOMIALS)):
            if mask>>j&1:
                observed[j] |= 1<<i
        for bit in range(OUTPUTS):
            if state[bit]!=after[bit]:
                effects[bit] |= 1<<i
    solutions=defaultdict(list)
    # Enumerate fixed <=3-sparse class ONCE per action, not once per bit.
    solutions[0].append(0)
    for i,x in enumerate(observed):
        solutions[x].append(1<<i)
    for i in range(len(observed)):
        x=observed[i]
        for j in range(i+1,len(observed)):
            solutions[x^observed[j]].append((1<<i)|(1<<j))
    for i in range(len(observed)):
        x=observed[i]
        for j in range(i+1,len(observed)):
            y=x^observed[j]
            for k in range(j+1,len(observed)):
                solutions[y^observed[k]].append((1<<i)|(1<<j)|(1<<k))
    survivors=[tuple(solutions.get(mask,())) for mask in effects]
    return survivors


def numeric_detector(state,action):
    """PUBLIC exact-input ReLU threshold, one iff all bits/action match."""
    row=[float(1 if bit else -1) for bit in state]
    row.extend(float(a==action) for a in ACTIONS)
    bias=float(sum(1 for bit in state if not bit)-6)
    return row,bias


class SparseCausalNumeric:
    gradient_steps=0
    def __init__(self):
        self._paid=[{} for _ in ACTIONS]
        self.current=(0,)*6
        self.charged_actions=0
        self._compiled=False
        self._survivors=None
        self.hidden_w=[]
        self.hidden_b=[]
        for action in ACTIONS:
            for term in MONOMIALS:
                w=[0.0]*INPUTS
                for bit in term:
                    w[bit]=1.0
                w[6+action]=1.0
                self.hidden_w.append(w)
                self.hidden_b.append(float(-len(term)))
        self.effect_w=[[0.0]*len(self.hidden_w) for _ in range(OUTPUTS)]
        self.confidence_w=[]
        self.confidence_b=[]
        self._consistent_bits=0
        self._consistent_actions=0
        self._candidates_count=0

    def charge(self,experience):
        s,a,y=experience.before,experience.action,experience.after
        valid(s,a)
        valid(y,a)
        if (s!=self.current or
            type(experience.action_cost) is not int or experience.action_cost!=1 or
            self.charged_actions>=144):
            raise ValueError("missing, discontinuous or duplicate paid physical action")
        prior=self._paid[a].get(s)
        if prior is not None and prior!=y:
            raise ValueError("non-deterministic physical public transition")
        self._paid[a][s]=y
        self.current=y
        self.charged_actions+=1
        self._compiled=False

    def compile(self):
        if self.charged_actions not in (96,144):
            raise ValueError("compile only after fully charged A or A+B")
        survivors=[]
        self.effect_w=[[0.0]*len(self.hidden_w) for _ in range(OUTPUTS)]
        consistent_bits=consistent_actions=candidates_count=0
        for action in ACTIONS:
            rows=tuple(sorted(self._paid[action].items()))
            sl=build_sparse_survivors(rows)
            survivors.append(sl)
            candidates_count+=sum(len(s) for s in sl)
            consistent_bits+=sum(bool(s) for s in sl)
            consistent_actions+=int(all(sl))
            for bit,options in enumerate(sl):
                if not options:
                    continue
                # Deterministic canonical sparse vector: sorted by number
                # of nonzero monomials, then combinatorial enumeration.
                selected=options[0]
                for term in range(len(MONOMIALS)):
                    if selected>>term&1:
                        self.effect_w[bit][action*len(MONOMIALS)+term]=1.0
        self._survivors=survivors
        self.confidence_w=[]
        self.confidence_b=[]
        for state in STATES:
            termmask=PUBLIC_MONOMIALS[state]
            for action in ACTIONS:
                if not all(survivors[action]):
                    continue
                unique=True
                for options in survivors[action]:
                    first=(options[0]&termmask).bit_count()&1
                    if any(((alt&termmask).bit_count()&1)!=first for alt in options[1:]):
                        unique=False
                        break
                if unique:
                    w,b=numeric_detector(state,action)
                    self.confidence_w.append(w)
                    self.confidence_b.append(b)
        self._consistent_bits=consistent_bits
        self._consistent_actions=consistent_actions
        self._candidates_count=candidates_count
        self._compiled=True
        return {
            "paid_physical_actions":self.charged_actions,
            "fixed_degree3_monomials_per_action":len(MONOMIALS),
            "fixed_sparse_candidate_vectors_per_action_bit":len(MONOMIAL_SETS),
            "consistent_output_bit_systems":consistent_bits,
            "consistent_public_action_channels":consistent_actions,
            "inconsistent_public_actions":tuple(a for a in ACTIONS if not all(survivors[a])),
            "sum_surviving_sparse_hypotheses":candidates_count,
            "numeric_effect_nonzero":sum(int(bool(v)) for r in self.effect_w for v in r),
            "numeric_confident_public_inputs":len(self.confidence_w),
            "numeric_weight_parameter_count":(
                len(self.hidden_w)*(INPUTS+1)+
                len(self.effect_w)*len(self.hidden_w)+
                len(self.confidence_w)*(INPUTS+1))
        }

    def _forward(self,s,a):
        valid(s,a)
        x=[float(v) for v in s]+[float(a==channel) for channel in ACTIONS]
        hidden=[relu(sum(w*z for w,z in zip(row,x))+bias)
                for row,bias in zip(self.hidden_w,self.hidden_b)]
        out=[]
        for bit in range(OUTPUTS):
            integer_count=sum(w*h for w,h in zip(self.effect_w[bit],hidden))
            parity=integer_count+sum(
                (2.0 if j%2==0 else -2.0)*relu(integer_count-j)
                for j in range(1,MAX_TERMS+1))
            value=x[bit]+parity-2.0*relu(x[bit]+parity-1.0)
            if not isfinite(value) or abs(value-round(value))>1e-7:
                raise ArithmeticError("numerical causal effect not a valid bit")
            out.append(int(round(value)))
        return tuple(out)

    def predict(self,s,a,force=False):
        if not self._compiled or type(force) is not bool:
            raise ValueError("cold numerical model uncompiled or invalid flag")
        prediction=self._forward(s,a)
        if force:
            return prediction
        x=[float(v) for v in s]+[float(a==channel) for channel in ACTIONS]
        score=sum(relu(sum(w*z for w,z in zip(row,x))+b)
                  for row,b in zip(self.confidence_w,self.confidence_b))
        if score>1+1e-7 or abs(score-round(score))>1e-7:
            raise ArithmeticError("source-blind numerical confidence not unique")
        return prediction if score>0.5 else None

    @staticmethod
    def validate_payload(p):
        required={"schema","paid_physical_actions","hidden_w","hidden_b",
                  "effect_w","confidence_w","confidence_b"}
        if type(p) is not dict or set(p)!=required or p["schema"]!=SCHEMA:
            raise ValueError("unknown numerical weight snapshot schema")
        if type(p["paid_physical_actions"]) is not int or p["paid_physical_actions"] not in (96,144):
            raise ValueError("invalid physical training provenance")
        def mat(v,n,m):
            return type(v) is list and len(v)==n and all(
                type(r) is list and len(r)==m and
                all(type(x) in (int,float) and isfinite(x) for x in r)
                for r in v)
        n=len(ACTIONS)*len(MONOMIALS)
        if not mat(p["hidden_w"],n,INPUTS) or not mat(p["effect_w"],OUTPUTS,n):
            raise ValueError("invalid learned numerical neural matrix")
        if type(p["hidden_b"]) is not list or len(p["hidden_b"])!=n or any(
            type(x) not in (int,float) or not isfinite(x) for x in p["hidden_b"]):
            raise ValueError("invalid fixed ReLU bias")
        confidence=len(p["confidence_w"]) if type(p["confidence_w"]) is list else -1
        if confidence<0 or confidence>384 or not mat(p["confidence_w"],confidence,INPUTS):
            raise ValueError("invalid learned numerical confidence head")
        if type(p["confidence_b"]) is not list or len(p["confidence_b"])!=confidence or any(
            type(x) not in (int,float) or not isfinite(x) for x in p["confidence_b"]):
            raise ValueError("invalid confidence biases")

    def snapshot(self):
        if not self._compiled:
            raise ValueError("snapshot before compiled real paid data")
        payload={"schema":SCHEMA,"paid_physical_actions":self.charged_actions,
                 "hidden_w":self.hidden_w,"hidden_b":self.hidden_b,
                 "effect_w":self.effect_w,"confidence_w":self.confidence_w,
                 "confidence_b":self.confidence_b}
        self.validate_payload(payload)
        checksum=sha256(canonical(payload).encode("ascii")).hexdigest()
        raw=canonical({"payload":payload,"sha256":checksum})
        if len(raw)>MAX_SNAPSHOT_BYTES:
            raise ValueError("numeric snapshot too large")
        return raw

    @classmethod
    def restore(cls,raw):
        if type(raw) is not str or len(raw)>MAX_SNAPSHOT_BYTES:
            raise ValueError("bad numerical snapshot")
        try:
            obj=json.loads(raw)
            if type(obj) is not dict or set(obj)!={"payload","sha256"}:
                raise ValueError("invalid numerical envelope")
            payload=obj["payload"]
            cls.validate_payload(payload)
            if sha256(canonical(payload).encode("ascii")).hexdigest()!=obj["sha256"]:
                raise ValueError("numeric weights checksum mismatch")
            m=cls()
            m.charged_actions=payload["paid_physical_actions"]
            m.hidden_w=payload["hidden_w"]
            m.hidden_b=payload["hidden_b"]
            m.effect_w=payload["effect_w"]
            m.confidence_w=payload["confidence_w"]
            m.confidence_b=payload["confidence_b"]
            m._compiled=True
            m._survivors=None
            m._paid=None
            if m.snapshot()!=raw:
                raise ValueError("noncanonical numerical snapshot")
            return m
        except (ValueError,KeyError,TypeError,UnicodeError,OverflowError) as exc:
            raise ValueError("invalid/tampered cold numerical weights") from exc
