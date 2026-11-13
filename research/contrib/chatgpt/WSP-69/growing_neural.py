"""Source-blind, gradient-free physical-experience -> real hidden neuron growth.

Neural inference is exclusively numerical: 8 binary inputs, an original
fixed 32-ReLU feature bank, up to 24 new data-derived ReLU hidden units,
raw sensor/action skip connections and 4 edited readout neurons.
The *input* centers of new neurons are selected from charged public
state/action residuals, never evaluator truth or symbolic physics rules.
This is prototype-based local representation growth, NOT discovery of a
general neuron grammar. Same-width random-center control uses identical
fitting algorithm/feature costs without outcome-directed selection.
"""
from __future__ import annotations
from hashlib import sha256
from itertools import product
from math import isfinite
from random import Random
import json

STATES=tuple(product((0,1),repeat=4))
ACTIONS=(0,1,2,3)
INPUTS=8
BASE_NEURONS=32
NEW_PER_PHASE=12
MAX_NEW=24
PARAM_FEATURES=1+INPUTS
RIDGE=0.5
FIXED_SEED=68182026
MARGIN=0.27
MAX_LEVERAGE=2.0
MAX_CHARGES=96
SNAPSHOT_CAP=1000000


def canonical(o):
    return json.dumps(o,sort_keys=True,separators=(",",":"),
                      ensure_ascii=True,allow_nan=False)


def check(state,action):
    if type(state) is not tuple or state not in STATES or (
            type(action) is not int or action not in ACTIONS):
        raise ValueError("invalid source-blind public state/action")
    return state


def inputs(state,action):
    check(state,action)
    return [float(x) for x in state]+[float(action==a) for a in ACTIONS]


def base_features():
    rng=Random(FIXED_SEED)
    hidden=[[rng.uniform(-0.65,0.65) for _ in range(INPUTS)]
            for _ in range(BASE_NEURONS)]
    bias=[rng.uniform(-0.3,0.3) for _ in range(BASE_NEURONS)]
    return hidden,bias


def prototype_neuron(state,action):
    """ReLU(1 - 0.5 * Hamming(x, observed public state/action))."""
    x=inputs(state,action)
    w=[(0.5 if val==1.0 else -0.5) for val in x]
    bias=1.0-0.5*sum(x)
    return w,bias


def _validate_matrix(matrix,rows,cols):
    if (type(matrix) is not list or len(matrix)!=rows or
            any(type(row) is not list or len(row)!=cols or
                any(type(z) not in (float,int) or not isfinite(z)
                    for z in row)
                for row in matrix)):
        raise ValueError("invalid/nonfinite neural parameter matrix")


class FeatureGrowthNeural:
    gradient_steps=0

    def __init__(self,policy="residual",seed=0):
        if policy not in ("residual","random"):
            raise ValueError("invalid frozen neuron construction policy")
        if type(seed) is not int:
            raise ValueError("invalid source-blind training policy seed")
        self.policy=policy
        self.random=Random(int.from_bytes(sha256(
            f"WSP69|random-centers|{seed}".encode("ascii")
        ).digest(),"big"))
        self.hidden_weights,self.hidden_biases=base_features()
        self.centers=[]
        self.w_readout=[]
        self.inverse_cov=[]
        self.ledger=[]
        self.current=(0,0,0,0)
        self.charged_actions=0
        self.growth_rounds=0
        self._init_readout()

    def _width(self):
        return PARAM_FEATURES+len(self.hidden_weights)

    def _init_readout(self):
        n=self._width()
        self.w_readout=[[0.0]*n for _ in range(4)]
        self.inverse_cov=[[(2.0 if i==j else 0.0) for j in range(n)]
                          for i in range(n)]

    def _features(self,state,action):
        x=inputs(state,action)
        return [1.0]+x+[
            max(0.0,sum(a*b for a,b in zip(row,x))+bias)
            for row,bias in zip(self.hidden_weights,self.hidden_biases)
        ]

    def _raw_and_leverage(self,state,action):
        f=self._features(state,action)
        raw=tuple(sum(w*z for w,z in zip(row,f))
                  for row in self.w_readout)
        cf=[sum(row[j]*f[j] for j in range(len(f)))
            for row in self.inverse_cov]
        leverage=sum(f[i]*cf[i] for i in range(len(f)))
        if leverage < -1e-6 or not isfinite(leverage):
            raise ArithmeticError("unstable posterior covariance")
        return raw,max(0.0,leverage)

    def raw(self,state,action):
        return self._raw_and_leverage(state,action)[0]

    def predict(self,state,action,force=False):
        if type(force) is not bool:
            raise ValueError("invalid confidence request")
        raw,leverage=self._raw_and_leverage(state,action)
        if not force and (leverage>MAX_LEVERAGE or
                          any(abs(y-0.5)<MARGIN for y in raw)):
            return None
        return tuple(int(y>=0.5) for y in raw)

    def _learn_row(self,before,action,after):
        f=self._features(before,action)
        n=len(f)
        cf=[sum(self.inverse_cov[i][j]*f[j] for j in range(n))
            for i in range(n)]
        den=1.0+sum(cf[i]*f[i] for i in range(n))
        if den<=0 or not isfinite(den):
            raise ArithmeticError("nonpositive rank-one update")
        gain=[x/den for x in cf]
        for bit in range(4):
            err=after[bit]-sum(self.w_readout[bit][j]*f[j]
                               for j in range(n))
            for j in range(n):
                self.w_readout[bit][j]+=err*gain[j]
        for i in range(n):
            for j in range(n):
                self.inverse_cov[i][j]-=gain[i]*cf[j]

    def charge(self,experience):
        b,a,y=experience.before,experience.action,experience.after
        check(b,a)
        check(y,a)
        if (b!=self.current or type(experience.action_cost) is not int or
                experience.action_cost!=1 or
                self.charged_actions>=MAX_CHARGES):
            raise ValueError("nonchronological/unpaid physical action")
        self._learn_row(b,a,y)
        self.ledger.append((b,a,y))
        self.current=y
        self.charged_actions+=1

    def _choose(self):
        unique=sorted({(b,a) for b,a,y in self.ledger
                       if (b,a) not in self.centers})
        if len(unique)<NEW_PER_PHASE:
            # Fixed budget; require actual distinct experiences rather than
            # inventing synthetic training states from an evaluator.
            return tuple(unique)
        if self.policy=="random":
            return tuple(sorted(self.random.sample(unique,NEW_PER_PHASE)))
        scores=[]
        for b,a in unique:
            residuals=[]
            for x,act,y in self.ledger:
                if x==b and act==a:
                    predicted=self.raw(x,act)
                    residuals.append(sum((predicted[i]-y[i])**2
                                         for i in range(4)))
            scores.append((-(sum(residuals)/len(residuals)),b,a))
        scores.sort()
        return tuple((b,a) for neg,b,a in scores[:NEW_PER_PHASE])

    def grow(self):
        if self.charged_actions not in (48,96):
            raise ValueError("frozen source-visible growth milestones only")
        if self.growth_rounds>=2:
            raise ValueError("growth already completed")
        selected=self._choose()
        if not selected:
            raise ValueError("no public contexts available to construct neurons")
        for state,action in selected:
            w,b=prototype_neuron(state,action)
            self.hidden_weights.append(w)
            self.hidden_biases.append(b)
            self.centers.append((state,action))
        self.growth_rounds+=1
        # Expanding a hidden matrix changes the neural feature basis. Directly
        # reprogram the output/covariance numerical matrices from the user's
        # OWN charged memory, never oracle/source examples.
        self._init_readout()
        for b,a,y in self.ledger:
            self._learn_row(b,a,y)
        return len(selected)

    def snapshot(self):
        payload={
            "schema":"wsp69.neural-feature-growth.v1",
            "hidden_weights":self.hidden_weights,
            "hidden_biases":self.hidden_biases,
            "output_weights":self.w_readout,
            "inverse_covariance":self.inverse_cov,
            "charged_actions":self.charged_actions,
            "growth_rounds":self.growth_rounds
        }
        self._validate()
        fingerprint=sha256(canonical(payload).encode("ascii")).hexdigest()
        raw=canonical({"payload":payload,"sha256":fingerprint})
        if len(raw)>SNAPSHOT_CAP:
            raise OverflowError("neural matrix snapshot exceeds cap")
        return raw

    def _validate(self):
        n_hidden=len(self.hidden_weights)
        if not BASE_NEURONS<=n_hidden<=BASE_NEURONS+MAX_NEW:
            raise ValueError("hidden width out of admissible bounds")
        _validate_matrix(self.hidden_weights,n_hidden,INPUTS)
        if (type(self.hidden_biases) is not list or
                len(self.hidden_biases)!=n_hidden or
                any(type(x) not in (float,int) or not isfinite(x)
                    for x in self.hidden_biases)):
            raise ValueError("bad hidden biases")
        n=PARAM_FEATURES+n_hidden
        _validate_matrix(self.w_readout,4,n)
        _validate_matrix(self.inverse_cov,n,n)
        if (type(self.charged_actions) is not int or
                not 0<=self.charged_actions<=MAX_CHARGES or
                type(self.growth_rounds) is not int or
                not 0<=self.growth_rounds<=2):
            raise ValueError("invalid neural growth/charge receipts")

    @classmethod
    def restore(cls,raw):
        if type(raw) is not str or len(raw)>SNAPSHOT_CAP:
            raise ValueError("invalid weight snapshot")
        try:
            container=json.loads(raw)
            if type(container) is not dict or set(container)!={"payload","sha256"}:
                raise ValueError("bad neural snapshot envelope")
            p=container["payload"]
            if type(p) is not dict or set(p)!={
                "schema","hidden_weights","hidden_biases","output_weights",
                "inverse_covariance","charged_actions","growth_rounds"
            } or p["schema"]!="wsp69.neural-feature-growth.v1":
                raise ValueError("invalid weight snapshot schema")
            if sha256(canonical(p).encode("ascii")).hexdigest()!=container["sha256"]:
                raise ValueError("neural weight hash invalid")
            m=cls()
            m.hidden_weights=p["hidden_weights"]
            m.hidden_biases=p["hidden_biases"]
            m.w_readout=p["output_weights"]
            m.inverse_cov=p["inverse_covariance"]
            m.charged_actions=p["charged_actions"]
            m.growth_rounds=p["growth_rounds"]
            m._validate()
            if m.snapshot()!=raw:
                raise ValueError("noncanonical numeric neural snapshot")
            # Returned cold instance is for inference only; physical charge
            # continuation requires an independently validated live session.
            return m
        except (TypeError,ValueError,KeyError,UnicodeError,
                json.JSONDecodeError,OverflowError) as exc:
            raise ValueError("tampered/invalid neural weights") from exc

    def changed_readout(self,other):
        return int(self.w_readout!=other.w_readout)

    def readout_parameter_count(self):
        return sum(len(row) for row in self.w_readout)

    def snapshot_bytes(self):
        return len(self.snapshot().encode("ascii"))
