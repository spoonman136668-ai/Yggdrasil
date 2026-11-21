"""MH10: frozen two-bank recall and conventional Bayesian regression control.

Engineering only. No external source actor, generator, true regime labels,
bank creation, native integration, or scoring of reserved/consumed cohorts.
Both arms use the same bounded public action/consequence ledger and the same
three-hypothesis evidence gate. Historical state remains immutable.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
import math
from research.mh09_delayed_credit import DelayedCredit, CAP, MAX_CLOCK, canonical, vec

SCHEMA = "yggdrasil.mh10.frozen-recall.eng.v1"
WINDOW = 8

def dot(a,b):
    return sum(x*y for x,y in zip(a,b))

def scalar(x, lo, hi):
    if type(x) not in (int,float) or not lo<=x<=hi:
        raise ValueError("scalar range")
    return float(x)

def _solve(a,b):
    """Deterministic Cholesky solve for fixed four-feature SPD precision."""
    lower=[[0.]*4 for _ in range(4)]
    for i in range(4):
        for j in range(i+1):
            v=a[i][j]-sum(lower[i][k]*lower[j][k] for k in range(j))
            if i==j:
                if not v>0.:
                    raise ValueError("nonpositive precision")
                lower[i][j]=math.sqrt(v)
            else:
                lower[i][j]=v/lower[j][j]
    u=[0.]*4
    for i in range(4):
        u[i]=(b[i]-sum(lower[i][k]*u[k] for k in range(i)))/lower[i][i]
    x=[0.]*4
    for i in range(3,-1,-1):
        x[i]=(u[i]-sum(lower[k][i]*x[k] for k in range(i+1,4)))/lower[i][i]
    return tuple(x)

@dataclass(frozen=True)
class FrozenBank:
    kind: str
    raw: bytes
    noise: float
    weights: tuple
    precision: tuple | None = None

    @classmethod
    def from_mh09(cls, raw, noise=.0625):
        noise=scalar(noise,.0001,16.)
        state=DelayedCredit.restore(raw)
        if state.pending:
            raise ValueError("unresolved bank credit")
        return cls("mh09",raw,noise,tuple(tuple(row) for row in state.w))

    @classmethod
    def from_bayes(cls, raw):
        if type(raw) is not bytes or len(raw)>32768:
            raise ValueError("bayes snapshot size")
        try:
            d=json.loads(raw.decode("ascii"))
            if type(d) is not dict or set(d)!={"schema","noise","prior","precision","cross","count","packet_sha256"} or d["schema"]!="mh10.bayes.v1":
                raise ValueError("bayes snapshot schema")
            noise=scalar(d["noise"],.0001,16.)
            scalar(d["prior"],.0001,16.)
            if type(d["count"]) is not int or not 1<=d["count"]<=128:
                raise ValueError("bayes count")
            if type(d["packet_sha256"]) is not str or len(d["packet_sha256"])!=64 or any(c not in "0123456789abcdef" for c in d["packet_sha256"]):
                raise ValueError("bayes provenance")
            if type(d["precision"]) is not list or len(d["precision"])!=4 or type(d["cross"]) is not list or len(d["cross"])!=3:
                raise ValueError("bayes dimensions")
            a=tuple(vec(row,4,2e6) for row in d["precision"])
            if any(a[i][j]!=a[j][i] for i in range(4) for j in range(4)):
                raise ValueError("nonsymmetric precision")
            weights=tuple(_solve(a,vec(row,4,4e6)) for row in d["cross"])
            if canonical(d)!=raw:
                raise ValueError("noncanonical bayes snapshot")
            return cls("bayes",raw,noise,weights,a)
        except (TypeError,KeyError,IndexError,OverflowError,UnicodeError) as exc:
            raise ValueError("invalid bayes snapshot") from exc

    def predict(self,x):
        x=vec(x,4,1.)
        # Restrict both readouts to the same declared bounded outcome range.
        p=tuple(max(-2.,min(2.,dot(row,x))) for row in self.weights)
        var=self.noise
        if self.precision is not None:
            var+=max(0.,dot(x,_solve(self.precision,x)))
        return p,var

    def record(self):
        return [self.kind,self.raw.decode("ascii"),self.noise]

    @classmethod
    def restore(cls,row):
        if type(row) is not list or len(row)!=3 or type(row[1]) is not str:
            raise ValueError("bank record")
        if row[0]=="mh09":
            return cls.from_mh09(row[1].encode("ascii"),row[2])
        if row[0]=="bayes":
            bank=cls.from_bayes(row[1].encode("ascii"))
            if bank.noise!=scalar(row[2],.0001,16.):
                raise ValueError("noise mismatch")
            return bank
        raise ValueError("bank kind")

def fit_bayes_fixture(packets, *, noise=.0625, prior=1.):
    """Exact Bayesian linear regression posterior for caller-supplied packets.

    Independent output heads, Gaussian known noise, zero-centered Gaussian
    coefficient prior. Uses all completed training pairs and no extra labels.
    No source access; only literal mechanical fixtures in qualification.
    """
    noise=scalar(noise,.0001,16.); prior=scalar(prior,.0001,16.)
    if type(packets) not in (list,tuple) or not 2<=len(packets)<=256:
        raise ValueError("fixture size")
    a=[[float(i==j)/prior for j in range(4)] for i in range(4)]
    cross=[[0.]*4 for _ in range(3)]
    pending={}; clock=0; count=0; receipt=[]
    for row in packets:
        if type(row) not in (tuple,list) or len(row)!=3:
            raise ValueError("fixture packet")
        op,k,v=row
        if type(k) is not int:
            raise ValueError("fixture id")
        if op=="action":
            if k!=clock or len(pending)>=CAP or (pending and k-min(pending)>CAP):
                raise ValueError("fixture action")
            v=vec(v,4,1.)
            pending[k]=v; clock+=1
        elif op=="feedback":
            if k not in pending or clock-1-k>CAP:
                raise ValueError("fixture feedback")
            v=vec(v,3,2.)
            x=pending.pop(k)
            for i in range(4):
                for j in range(4):
                    a[i][j]+=x[i]*x[j]/noise
                for j in range(3):
                    cross[j][i]+=v[j]*x[i]/noise
            count+=1
        else:
            raise ValueError("fixture operation")
        receipt.append((op,k,v))
    if pending or not count:
        raise ValueError("incomplete fixture")
    raw=canonical({"schema":"mh10.bayes.v1","noise":noise,"prior":prior,
        "precision":a,"cross":cross,"count":count,
        "packet_sha256":hashlib.sha256(canonical(receipt)).hexdigest()})
    return FrozenBank.from_bayes(raw)

class EvidenceRecall:
    """Read-only two-bank retrieval under a bounded window of public evidence.

    Gaussian likelihoods, equal priors on banks and a broad unknown hypothesis.
    The window is ordered by original action ID, not by receipt order. This is
    a fixed-hypothesis window filter, NOT exact switching-HMM inference.
    Minimum two witnesses, 0.95 posterior for a known bank; otherwise abstain.
    No unseen-world labels, and no cue-only nomination. Both banks frozen.
    """

    def __init__(self, banks):
        if type(banks) not in (list,tuple) or len(banks)!=2 or any(type(b) is not FrozenBank for b in banks):
            raise ValueError("two frozen banks required")
        # Rebuild from original canonical bytes, not caller-supplied weights.
        self._banks=tuple(FrozenBank.restore(b.record()) for b in banks)
        if self._banks[0].kind!=self._banks[1].kind:
            raise ValueError("unmatched bank family")
        self.clock=0; self.pending={}; self.evidence={}

    @property
    def banks(self):
        return self._banks

    def posterior(self):
        scores=[sum(v[i] for v in self.evidence.values()) for i in range(3)]
        hi=max(scores); exp=[math.exp(v-hi) for v in scores]; total=sum(exp)
        return tuple(v/total for v in exp)

    def choice(self):
        if len(self.evidence)<2:
            return None
        p=self.posterior()
        return 0 if p[0]>=.95 else 1 if p[1]>=.95 else None

    def begin(self,event,x):
        if type(event) is not int or event!=self.clock or self.clock>=MAX_CLOCK:
            raise ValueError("action clock")
        if len(self.pending)>=CAP or (self.pending and event-min(self.pending)>CAP):
            raise ValueError("pending capacity/expiry")
        x=vec(x,4,1.)
        p=tuple(b.predict(x) for b in self.banks)
        selected=self.choice()
        self.pending[event]=p
        self.clock+=1
        return None if selected is None else p[selected][0]

    def feedback(self,event,y):
        if type(event) is not int or event not in self.pending or not 0<=self.clock-1-event<=CAP:
            raise ValueError("unmatched consequence")
        y=vec(y,3,2.)
        def ll(mean,var):
            return -.5*(3*math.log(2*math.pi*var)+sum((a-b)**2 for a,b in zip(y,mean))/var)
        record=tuple(ll(mean,var) for mean,var in self.pending[event])+(ll((0.,)*3,4.),)
        self.evidence[event]=record
        # Last WINDOW completed original action IDs, regardless of delivery order.
        for key in sorted(self.evidence)[:-WINDOW]:
            del self.evidence[key]
        del self.pending[event]
        return self.choice()

    def checkpoint(self):
        return canonical({"schema":SCHEMA,"banks":[b.record() for b in self.banks],
            "clock":self.clock,"pending":[[k,v] for k,v in sorted(self.pending.items())],
            "evidence":[[k,v] for k,v in sorted(self.evidence.items())]})

    @classmethod
    def restore(cls,raw):
        if type(raw) is not bytes or len(raw)>100000:
            raise ValueError("checkpoint size")
        try:
            d=json.loads(raw.decode("ascii"))
            if type(d) is not dict or set(d)!={"schema","banks","clock","pending","evidence"} or d["schema"]!=SCHEMA or type(d["banks"]) is not list:
                raise ValueError("checkpoint schema")
            m=cls([FrozenBank.restore(b) for b in d["banks"]])
            c=d["clock"]
            if type(c) is not int or not 0<=c<=MAX_CLOCK:
                raise ValueError("clock")
            m.clock=c
            for field,limit in (("pending",CAP),("evidence",WINDOW)):
                rows=d[field]
                if type(rows) is not list or len(rows)>limit:
                    raise ValueError("journal bounds")
                target=getattr(m,field)
                for row in rows:
                    if type(row) is not list or len(row)!=2:
                        raise ValueError("journal row")
                    k,v=row
                    if type(k) is not int or not 0<=k<c or k in target:
                        raise ValueError("journal identity")
                    if field=="pending":
                        if c-1-k>CAP or type(v) is not list or len(v)!=2 or any(type(t) is not list or len(t)!=2 for t in v):
                            raise ValueError("pending layout")
                        target[k]=tuple((vec(t[0],3,2.),scalar(t[1],.0001,100000.)) for t in v)
                    else:
                        target[k]=vec(v,3,1e7)
            if set(m.pending)&set(m.evidence) or m.checkpoint()!=raw:
                raise ValueError("checkpoint collision/noncanonical")
            return m
        except (TypeError,KeyError,IndexError,OverflowError,UnicodeError) as exc:
            raise ValueError("invalid checkpoint") from exc
