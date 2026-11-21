"""MH09 engineering-only delayed local credit. No source or scientific admission.

The shared rule is fitted only by the explicit bounded, caller-supplied packet
fitter. No source sampling, reserved seeds, native/Amalgam imports, or archive
selection. Fixed and robust trace controls share the same public ledger.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
import math

SCHEMA = "yggdrasil.mh09.delayed-credit.eng.v1"
CAP = 8
MAX_CLOCK = 100_000_000

def clip(x, lo, hi):
    return max(lo, min(hi, x))

def vec(x, n, bound):
    if type(x) not in (tuple, list) or len(x) != n:
        raise ValueError("vector shape")
    if any(type(v) not in (int, float) or not -bound <= v <= bound for v in x):
        raise ValueError("vector value")
    return tuple(float(v) for v in x)

def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")

def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))

@dataclass(frozen=True)
class Rule:
    theta: tuple = (0.,) * 7

    def __post_init__(self):
        object.__setattr__(self, "theta", vec(self.theta, 7, 4))

    def eta(self, x, p, w, importance, age):
        phi = (1., abs(x), abs(p)/(1+abs(p)), abs(w)/4, importance/16, age/CAP)
        return .25 * sigmoid(sum(a*b for a,b in zip(self.theta[:6],phi)))

    @property
    def decay(self):
        return sigmoid(self.theta[6])

class DelayedCredit:
    """Monotonic action IDs, explicitly matched, possibly out-of-order feedback.
    The age is the number of intervening action starts. Pending entries never
    evict silently. Only one previously completed public witness is retained.
    Protection reflects loss increase on that witness under the proposed
    coordinate update; this is an engineering heuristic, not accepted retention.
    """
    def __init__(self, rule=Rule(), *, mode="meta", utility=True, trace=True):
        if type(rule) is not Rule or mode not in ("meta", "fixed", "robust") or type(utility) is not bool or type(trace) is not bool:
            raise ValueError("configuration")
        self._rule = rule
        self.mode, self.utility, self.trace = mode, utility, trace
        self.w = [[0.] * 4 for _ in range(3)]
        self.q = [[0.] * 4 for _ in range(3)]
        self.clock = 0
        self.pending = {}
        self.prior = None

    @property
    def rule(self):
        return self._rule

    def predict(self, x):
        x = vec(x, 4, 1.)
        return tuple(sum(a*b for a,b in zip(row,x)) for row in self.w)

    def begin(self, event, x):
        if type(event) is not int or event != self.clock or self.clock >= MAX_CLOCK:
            raise ValueError("action clock")
        if len(self.pending) >= CAP or (self.pending and event-min(self.pending) > CAP):
            raise ValueError("pending credit capacity/expiry")
        x = vec(x,4,1.)
        p = self.predict(x)
        self.pending[event] = (x,p)
        self.clock += 1
        return p

    def feedback(self, event, y):
        if type(event) is not int or event not in self.pending:
            raise ValueError("unmatched or duplicate consequence")
        y = vec(y,3,2.)
        x,p = self.pending[event]
        age = self.clock-1-event
        if not 0 <= age <= CAP:
            raise ValueError("expired consequence")
        if not self.trace and age:
            attenuation = 0.
        else:
            attenuation = self.rule.decay**age if self.mode != "fixed" else .5**age
        nw = [row[:] for row in self.w]
        nq = [row[:] for row in self.q]
        oldx, oldy = self.prior if self.prior is not None else (None,None)
        for j in range(3):
            err = clip(y[j]-p[j],-2,2)
            prior_p = sum(a*b for a,b in zip(self.w[j],oldx)) if oldx is not None else 0.
            for i in range(4):
                wi, qi = self.w[j][i], self.q[j][i]
                elig = x[i] * (1. if self.mode == "robust" else 1.+.5*math.tanh(p[j]))
                eta = .125 if self.mode == "fixed" else self.rule.eta(x[i],p[j],wi,qi,age)
                after = clip(wi+eta*err*elig*attenuation/(1.+qi if self.utility else 1.),-4,4)
                nw[j][i] = after
                if self.utility and oldx is not None and after != wi:
                    old_error = prior_p-oldy[j]
                    changed_error = old_error+(after-wi)*oldx[i]
                    delta = changed_error**2-old_error**2
                    nq[j][i] = clip(qi+clip(delta,-.25,.25),0,16)
        self.w,self.q = nw,nq
        self.prior = (x,y)
        del self.pending[event]
        return p

    def checkpoint(self):
        return canonical({"schema":SCHEMA,"theta":self.rule.theta,"mode":self.mode,
            "utility":self.utility,"trace":self.trace,"clock":self.clock,
            "w":self.w,"q":self.q,"prior":self.prior,
            "pending":[[k,x,p] for k,(x,p) in sorted(self.pending.items())]})

    @classmethod
    def restore(cls, raw):
        if type(raw) is not bytes or len(raw)>32768:
            raise ValueError("checkpoint size")
        try:
            d=json.loads(raw.decode("ascii"))
            if type(d) is not dict or set(d)!={"schema","theta","mode","utility","trace","clock","w","q","prior","pending"} or d["schema"]!=SCHEMA:
                raise ValueError("checkpoint schema")
            m=cls(Rule(d["theta"]),mode=d["mode"],utility=d["utility"],trace=d["trace"])
            c=d["clock"]
            if type(c) is not int or not 0<=c<=MAX_CLOCK:
                raise ValueError("checkpoint clock")
            m.clock=c
            if any(type(d[k]) is not list or len(d[k])!=3 for k in ("w","q")):
                raise ValueError("checkpoint matrix")
            m.w=[list(vec(row,4,4.)) for row in d["w"]]
            m.q=[list(vec(row,4,16.)) for row in d["q"]]
            if any(v<0 or (not m.utility and v!=0) for row in m.q for v in row):
                raise ValueError("checkpoint utility")
            if d["prior"] is not None:
                if type(d["prior"]) is not list or len(d["prior"])!=2:
                    raise ValueError("checkpoint prior")
                m.prior=(vec(d["prior"][0],4,1.),vec(d["prior"][1],3,2.))
            if type(d["pending"]) is not list or len(d["pending"])>CAP:
                raise ValueError("checkpoint pending")
            for row in d["pending"]:
                if type(row) is not list or len(row)!=3:
                    raise ValueError("checkpoint row")
                k,x,p=row
                if type(k) is not int or k in m.pending or not 0<=k<c or c-1-k>CAP:
                    raise ValueError("checkpoint identity")
                m.pending[k]=(vec(x,4,1.),vec(p,3,16.))
            if m.checkpoint()!=raw:
                raise ValueError("noncanonical checkpoint")
            return m
        except (TypeError,KeyError,IndexError,OverflowError,UnicodeError) as exc:
            raise ValueError("invalid checkpoint") from exc

def fit_engineering_packets(packets, *, mode="meta", utility=True, trace=True):
    """29 evaluations on caller-supplied finite TRAIN-formatted packet fixtures.
    This is NOT a source-owner admission or a scientific split validator.
    No source calls. Return unchanged frozen rule plus fit identity and score.
    Do not call on reserved, held, external, or previously consumed cohorts.
    """
    if mode not in ("meta","robust") or type(packets) not in (list,tuple) or not 2<=len(packets)<=256:
        raise ValueError("engineering fit arguments")
    frozen=[]
    for row in packets:
        if type(row) not in (tuple,list) or len(row)!=3:
            raise ValueError("packet shape")
        op,k,v=row
        if type(k) is not int or op not in ("action","feedback"):
            raise ValueError("packet identity")
        frozen.append((op,k,vec(v,4 if op=="action" else 3,1. if op=="action" else 2.)))
    def score(theta):
        model=DelayedCredit(Rule(theta),mode=mode,utility=utility,trace=trace)
        total=0.; count=0
        for op,k,v in frozen:
            if op=="action":
                model.begin(k,v)
            else:
                p=model.feedback(k,v)
                total+=sum((a-b)**2 for a,b in zip(p,v))
                count+=3
        if not count or model.pending:
            raise ValueError("incomplete fixture")
        return total/count
    best=(0.,)*7
    initial=loss=score(best)
    evaluations=1
    for step in (1.,.5):
        for i in range(7):
            origin=best
            alternatives=[]
            for sign in (-1.,1.):
                trial=list(origin)
                trial[i]=clip(trial[i]+sign*step,-4,4)
                trial=tuple(trial)
                alternatives.append((score(trial),trial))
                evaluations+=1
            for value,trial in alternatives:
                if value<loss:
                    best,loss=trial,value
    return Rule(best), {"evaluations":evaluations,"initial_mse":initial,
        "selected_mse":loss,"packet_sha256":hashlib.sha256(canonical(frozen)).hexdigest(),
        "mode":mode,"utility":utility,"trace":trace,"scientific_gain_verified":False}
