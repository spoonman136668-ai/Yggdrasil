"""Independent conventional Bayesian active-learning benchmark for DG1-HC06.

Implements the fixed six-hypothesis/action prior from scratch, not a subclass
or import of HC05 learner. Uses Shannon outcome entropy, two-step expectimax.
Posterior is exact uniform over surviving fixed deterministic hypotheses.
This is still a source-aligned symbolic control, not general Bayesian physics.
"""
from __future__ import annotations

import hashlib
import json
from math import log2

SCHEMA="yggdrasil.dg1-hc06.independent-bayesian.v1"
N_ACTIONS=4
MAX_SNAPSHOT=1024
ALL=0b111111
DISCOUNT=0.9

def state_ok(s):
    if type(s) is not int or s < 0 or s > 15:
        raise ValueError("BAYES_PUBLIC_STATE_INVALID")
    return s

def action_ok(a):
    if type(a) is not int or a < 0 or a > 3:
        raise ValueError("BAYES_PUBLIC_ACTION_INVALID")
    return a

def rule_output(s,a,h):
    """Six frozen causal formulas, independently coded."""
    state_ok(s)
    action_ok(a)
    if type(h) is not int or h not in range(6):
        raise ValueError("BAYES_RULE_INVALID")
    l=(s >> ((a+3)%4)) & 1
    r=(s >> ((a+1)%4)) & 1
    own=(s >> a) & 1
    if h in (0,1):
        base=l ^ r
    elif h in (2,3):
        base=l ^ r ^ own
    else:
        base=l & r
    return base ^ (h % 2)

def subset(mask,s,a,effect):
    return sum(1<<h for h in range(6)
               if mask & (1<<h) and rule_output(s,a,h)==effect)

def count_effects(mask,s,a):
    zero=one=0
    for h in range(6):
        if mask & (1<<h):
            if rule_output(s,a,h):
                one+=1
            else:
                zero+=1
    return zero,one

def entropy(mask,s,a):
    z,o=count_effects(mask,s,a)
    n=z+o
    if n==0: return 0.0
    x=0.0
    for c in (z,o):
        if c:
            p=c/n
            x-=p*log2(p)
    return x

def canonical(o):
    return json.dumps(o,sort_keys=True,separators=(",",":"),allow_nan=False).encode("ascii")

class BayesianEntropyPlanner:
    def __init__(self):
        self.survivors=[ALL,ALL,ALL,ALL]
        self.charged=0
        self.unsatisfied=0

    @property
    def logical_bits(self):
        return 24

    def observe(self,before,action,after):
        state_ok(before)
        action_ok(action)
        state_ok(after)
        if after not in (before,before^(1<<action)):
            raise ValueError("BAYES_NONLOCAL_PUBLIC_DELTA")
        e=int(before!=after)
        old=self.survivors[action]
        new=subset(old,before,action,e)
        if old and not new:
            self.unsatisfied+=1
        self.survivors[action]=new
        self.charged+=1

    def predict(self,state,action):
        state_ok(state)
        action_ok(action)
        z,o=count_effects(self.survivors[action],state,action)
        if (z and o) or not (z or o):
            return None
        return state^((1 if o else 0)<<action)

    def choose(self,state):
        state_ok(state)
        scores=[]
        for a in range(4):
            mask=self.survivors[a]
            z,o=count_effects(mask,state,a)
            denom=z+o
            immediate=entropy(mask,state,a)
            future=0.0
            if denom:
                for effect,support in ((0,z),(1,o)):
                    if not support: continue
                    post=subset(mask,state,a,effect)
                    hypothetical_next=state^(effect<<a)
                    # This is hypothetical belief propagation ONLY; no
                    # actual source physics or hidden rule oracle called.
                    best=max(entropy(post if b==a else self.survivors[b],
                                     hypothetical_next,b)
                             for b in range(4))
                    future+=(support/denom)*best
            scores.append(immediate+DISCOUNT*future)
        return max(range(4),key=lambda a:(scores[a],-a))

    def snapshot(self):
        payload={"schema":SCHEMA,"survivors":self.survivors,
                 "charged":self.charged,"unsatisfied":self.unsatisfied}
        digest=hashlib.sha256(canonical(payload)).hexdigest()
        encoded=canonical({"payload":payload,"sha256":digest})
        if len(encoded)>MAX_SNAPSHOT:
            raise ValueError("BAYES_CHECKPOINT_EXCEEDS_BUDGET")
        return encoded

    @classmethod
    def restore(cls,data):
        if type(data) is not bytes or not 0<len(data)<=MAX_SNAPSHOT:
            raise ValueError("BAYES_CHECKPOINT_REJECTED")
        try:
            o=json.loads(data)
            if type(o) is not dict or set(o)!={"payload","sha256"}:
                raise ValueError("BAYES_BAD_ENVELOPE")
            p=o["payload"]
            if (type(p) is not dict or
                set(p)!={"schema","survivors","charged","unsatisfied"} or
                p["schema"]!=SCHEMA):
                raise ValueError("BAYES_BAD_SCHEMA")
            if hashlib.sha256(canonical(p)).hexdigest()!=o["sha256"]:
                raise ValueError("BAYES_HASH_REJECT")
            ss=p["survivors"]
            if type(ss) is not list or len(ss)!=4 or any(
                type(m) is not int or not 0<=m<=ALL for m in ss
            ):
                raise ValueError("BAYES_BAD_MASK")
            n=p["charged"]; u=p["unsatisfied"]
            if (type(n) is not int or type(u) is not int or
                not 0<=u<=n<=100000):
                raise ValueError("BAYES_BAD_COUNTERS")
            model=cls()
            model.survivors=ss[:];model.charged=n;model.unsatisfied=u
            if model.snapshot()!=data:
                raise ValueError("BAYES_NONCANONICAL")
            return model
        except (TypeError,ValueError,UnicodeError,OverflowError,KeyError) as e:
            raise ValueError("BAYES_CHECKPOINT_REJECTED") from e
