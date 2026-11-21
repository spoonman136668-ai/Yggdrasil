"""MH11 bounded new-memory admission, engineering only.

One previously learned frozen bank; one provisional bank; at most one new
bank admitted per lifetime. No source interfaces, no source-generated data,
no external actor, no automatic fit of a meta-rule, no eviction. The caller
supplies sequential completed public packets, not hidden regime labels.
"""
from __future__ import annotations
import hashlib
import json
import math
from research.mh09_delayed_credit import DelayedCredit, MAX_CLOCK, canonical, vec
from research.mh10_frozen_recall import FrozenBank, EvidenceRecall, fit_bayes_fixture

SCHEMA = "yggdrasil.mh11.memory-admission.eng.v1"
REJECT = 3
TRAIN = 32
VERIFY = 4
MARGIN = math.log(19.)

def ll(y, p, variance):
    return -.5*(3*math.log(2*math.pi*variance)+sum((a-b)**2 for a,b in zip(y,p))/variance)

def logdensity(bank,x,y):
    p,v=bank.predict(x)
    return ll(y,p,v)

def fit_new(old,rows):
    packets=tuple(p for k,(_,x,y) in enumerate(rows)
                  for p in (("action",k,x),("feedback",k,y)))
    if old.kind=="bayes":
        prior=json.loads(old.raw)["prior"]
        return fit_bayes_fixture(packets,noise=old.noise,prior=prior)
    old_model=DelayedCredit.restore(old.raw)
    m=DelayedCredit(old_model.rule,mode=old_model.mode,utility=old_model.utility,trace=old_model.trace)
    for op,k,v in packets:
        if op=="action": m.begin(k,v)
        else: m.feedback(k,v)
    return FrozenBank.from_mh09(m.checkpoint(),old.noise)

class MemoryFormation:
    """Conservative admission before retrieval (single-outstanding-packet API).

    Three decisive contradictions start collection of 32 *subsequent* public
    pairs. Any interruption by old-bank support cancels collection. Freeze the
    provisional model, require four further consecutive predictive successes
    against old and broad unknown, then seal. No validation pair trains it.
    A failed validation cancels the attempt; one attempt maximum per instance.
    Once sealed, only the existing MH10 recall component is used.
    Constants are engineering fixtures, not calibrated scientific thresholds.
    """
    def __init__(self,old):
        if type(old) is not FrozenBank:
            raise ValueError("one previous bank required")
        self._old=FrozenBank.restore(old.record())
        self.clock=0
        self.phase="watch"
        self.reject=0
        self.known=0
        self.rows=[]
        self.validation=[]
        self._candidate=None
        self.pending=None

    @property
    def old(self):
        return self._old

    @property
    def candidate(self):
        return self._candidate

    def begin(self,event,x):
        if self.phase=="sealed":
            raise ValueError("sealed; use recall")
        if self.pending is not None or type(event) is not int or event!=self.clock or self.clock>=MAX_CLOCK:
            raise ValueError("one outstanding action / clock")
        x=vec(x,4,1.)
        self.pending=(event,x)
        self.clock+=1
        return self.old.predict(x)[0] if self.known>=2 and self.phase in ("watch","stopped") else None

    def feedback(self,event,y):
        if type(event) is not int or self.pending is None or event!=self.pending[0]:
            raise ValueError("unmatched consequence")
        y=vec(y,3,2.)
        _,x=self.pending
        known=logdensity(self.old,x,y)
        unknown=ll(y,(0.,)*3,4.)
        bad=unknown-known>=MARGIN
        good=known-unknown>=MARGIN
        next_known=min(2,self.known+1) if good else 0
        phase=self.phase
        reject=self.reject
        rows=list(self.rows)
        validation=list(self.validation)
        candidate=self.candidate
        if phase=="watch":
            reject=min(REJECT,reject+1) if bad else 0
            if reject==REJECT:
                phase="collect"
        elif phase=="collect":
            if not bad:
                phase="stopped"
            else:
                rows.append((event,x,y))
                if len(rows)==TRAIN:
                    candidate=fit_new(self.old,rows)
                    phase="validate"
        elif phase=="validate":
            score=logdensity(candidate,x,y)
            passed=score-max(known,unknown)>=MARGIN
            validation.append((event,x,y,passed))
            if not passed:
                phase="stopped"
            elif len(validation)==VERIFY:
                phase="sealed"
        self.phase,self.reject,self.known=phase,reject,next_known
        self.rows,self.validation,self._candidate=rows,validation,candidate
        self.pending=None
        return self.phase

    def start_recall(self):
        if self.phase!="sealed" or self.pending is not None:
            raise ValueError("no admitted second bank")
        m=EvidenceRecall((self.old,self.candidate))
        m.clock=self.clock
        return m

    def checkpoint(self):
        return canonical({"schema":SCHEMA,"old":self.old.record(),"clock":self.clock,
            "phase":self.phase,"reject":self.reject,"known":self.known,"rows":self.rows,
            "validation":self.validation,"candidate":None if self.candidate is None else self.candidate.record(),
            "pending":self.pending})

    @classmethod
    def restore(cls,raw):
        if type(raw) is not bytes or len(raw)>100000:
            raise ValueError("checkpoint size")
        try:
            d=json.loads(raw.decode("ascii"))
            if type(d) is not dict or set(d)!={"schema","old","clock","phase","reject","known","rows","validation","candidate","pending"} or d["schema"]!=SCHEMA:
                raise ValueError("checkpoint schema")
            m=cls(FrozenBank.restore(d["old"]))
            c=d["clock"]
            if type(c) is not int or not 0<=c<=MAX_CLOCK:
                raise ValueError("clock")
            m.clock=c
            m.phase=d["phase"]
            m.reject=d["reject"]; m.known=d["known"]
            if m.phase not in ("watch","collect","validate","sealed","stopped") or type(m.reject) is not int or not 0<=m.reject<=REJECT or type(m.known) is not int or not 0<=m.known<=2:
                raise ValueError("phase/score")
            if d["pending"] is not None:
                k,x=d["pending"]
                if type(k) is not int or k!=c-1 or c==0 or m.phase=="sealed":
                    raise ValueError("pending identity")
                m.pending=(k,vec(x,4,1.))
            last=c-(1 if m.pending else 0)
            occupied=set()
            for field,limit in (("rows",TRAIN),("validation",VERIFY)):
                data=d[field]
                if type(data) is not list or len(data)>limit:
                    raise ValueError("journal bounds")
                prev=None
                for row in data:
                    if type(row) is not list or len(row)!=(3 if field=="rows" else 4):
                        raise ValueError("journal row")
                    k,x,y=row[:3]
                    if type(k) is not int or not 0<=k<last or k in occupied or (prev is not None and k!=prev+1):
                        raise ValueError("journal identity")
                    prev=k; occupied.add(k)
                    x,y=vec(x,4,1.),vec(y,3,2.)
                    if field=="rows":
                        if ll(y,(0.,)*3,4.)-logdensity(m.old,x,y)<MARGIN:
                            raise ValueError("noncontradictory training row")
                        m.rows.append((k,x,y))
                    else:
                        if type(row[3]) is not bool:
                            raise ValueError("validation flag")
                        m.validation.append((k,x,y,row[3]))
            if d["candidate"] is not None:
                m._candidate=FrozenBank.restore(d["candidate"])
                if m.candidate.kind!=m.old.kind or m.candidate.noise!=m.old.noise or len(m.rows)!=TRAIN:
                    raise ValueError("provisional bank shape")
                # Canonical syntax and valid predictive receipts are not sufficient
                # to bind a provisional bank to its purported training witnesses.
                # Refit only the bounded, explicitly supplied 32-row mechanical
                # archive and compare its *exact* immutable bank bytes. This
                # does not authenticate where those witnesses came from.
                if fit_new(m.old,m.rows).raw != m.candidate.raw:
                    raise ValueError("candidate/training receipt mismatch")
            if (len(m.rows)==TRAIN)!=(m.candidate is not None):
                raise ValueError("candidate/training mismatch")
            if m.validation:
                if m.candidate is None or m.validation[0][0]!=m.rows[-1][0]+1:
                    raise ValueError("validation chronology")
                for k,x,y,ok in m.validation:
                    actual=logdensity(m.candidate,x,y)-max(logdensity(m.old,x,y),ll(y,(0.,)*3,4.))>=MARGIN
                    if actual!=ok:
                        raise ValueError("validation receipt mismatch")
            if m.phase=="watch":
                valid=m.reject<REJECT and not m.rows and not m.validation and m.candidate is None
            elif m.phase=="collect":
                valid=m.reject==REJECT and len(m.rows)<TRAIN and m.candidate is None and not m.validation
            elif m.phase=="validate":
                valid=m.reject==REJECT and m.candidate is not None and len(m.validation)<VERIFY and all(v[3] for v in m.validation)
            elif m.phase=="sealed":
                valid=m.reject==REJECT and m.candidate is not None and len(m.validation)==VERIFY and all(v[3] for v in m.validation)
            else:
                valid=m.reject==REJECT and ((m.candidate is None and not m.validation) or (bool(m.validation) and not m.validation[-1][3] and all(v[3] for v in m.validation[:-1])))
            if not valid or m.checkpoint()!=raw:
                raise ValueError("phase or canonical mismatch")
            return m
        except (TypeError, KeyError, IndexError, OverflowError, UnicodeError) as exc:
            raise ValueError("invalid checkpoint") from exc
