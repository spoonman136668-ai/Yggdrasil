"""Independent conventional symbolic two-regime causal change-point baseline.

A separately coded exact version-space over the same 40 Boolean rules/action,
two regimes, with Shannon entropy for action/perturb selection. Not a neural
Bayesian state-space model or an independent scientific intelligence baseline.
"""
from __future__ import annotations
import hashlib,json,math
from itertools import combinations

TRIPLES=tuple(combinations(range(4),3))
FULL=(1<<40)-1
SCHEMA="ygg.dg1-hc09.conventional-two-context.v1"


def assert_public(state,action=None):
    if type(state) is not int or not 0<=state<16:raise ValueError("HC09_CONTROL_BAD_STATE")
    if action is not None and (type(action) is not int or not 0<=action<4):
        raise ValueError("HC09_CONTROL_BAD_ACTION")


def eval_rule(state,h):
    assert_public(state)
    if type(h) is not int or not 0<=h<40:raise ValueError("HC09_CONTROL_BAD_RULE")
    if h<32:
        parity=0
        for i in range(4):
            if (h//2)&(1<<i):
                parity^=(state>>i)&1
        return parity^(h&1)
    q=TRIPLES[(h-32)//2]
    return (1 if sum((state>>i)&1 for i in q)>=2 else 0)^(h&1)


def survive(mask,state,value):
    out=0
    for h in range(40):
        if (mask>>h)&1 and eval_rule(state,h)==value:
            out|=1<<h
    return out


def posterior_counts(mask,state):
    n0=n1=0
    for h in range(40):
        if (mask>>h)&1:
            if eval_rule(state,h):n1+=1
            else:n0+=1
    return n0,n1


def shannon(mask,state):
    z,o=posterior_counts(mask,state)
    n=z+o
    if not n:return 0.0
    res=0.0
    for c in (z,o):
        if c:
            p=c/n
            res-=p*math.log2(p)
    return res


def encode(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode("ascii")


class ConventionalContextModel:
    def __init__(self):
        self.contexts=[[FULL]*4]
        self.selected=0
        self.mismatch=False
        self.n=0
        self.switches=0
        self.created=0
        self.unexplained=0

    @property
    def capacity_bits(self):return 320

    def observe(self,before,action,after):
        assert_public(before,action)
        assert_public(after)
        if after not in (before,before^(1<<action)):
            raise ValueError("HC09_CONTROL_NONLOCAL")
        observed=int(after!=before)
        candidate=survive(self.contexts[self.selected][action],before,observed)
        if candidate:
            self.contexts[self.selected][action]=candidate
            self.mismatch=False
        else:
            match=next((i for i,v in enumerate(self.contexts)
                        if i!=self.selected and survive(v[action],before,observed)),None)
            if match is not None:
                self.selected=match
                self.contexts[match][action]=survive(self.contexts[match][action],before,observed)
                self.switches+=1
                self.mismatch=False
            elif len(self.contexts)<2:
                other=[FULL]*4
                other[action]=survive(FULL,before,observed)
                self.contexts.append(other)
                self.selected=1
                self.created+=1
                self.mismatch=False
            else:
                self.unexplained+=1
                self.mismatch=True
        self.n+=1
        return not self.mismatch

    def predict(self,state,action):
        assert_public(state,action)
        if self.mismatch:return None
        a,b=posterior_counts(self.contexts[self.selected][action],state)
        if (a and b) or not (a or b):return None
        return state^((1 if b else 0)<<action)

    def choose(self,state,flips,limit):
        assert_public(state)
        if (type(flips) is not int or type(limit) is not int or
            not 0<=flips<=limit<=8):
            raise ValueError("HC09_CONTROL_BAD_BUDGET")
        masks=self.contexts[self.selected]
        info=[shannon(mask,state) for mask in masks]
        if max(info)>0:
            return "causal",max(range(4),key=lambda a:(info[a],-a))
        if flips<limit:
            next_info=[sum(shannon(m,state^(1<<i)) for m in masks)
                       for i in range(4)]
            return "flip",max(range(4),key=lambda i:(next_info[i],-i))
        return "causal",0

    def supports(self):
        return [tuple(mask.bit_count() for mask in c) for c in self.contexts]

    def snapshot(self):
        payload={"schema":SCHEMA,"contexts":self.contexts,"selected":self.selected,
                 "mismatch":self.mismatch,"n":self.n,"switches":self.switches,
                 "created":self.created,"unexplained":self.unexplained}
        raw=encode({"payload":payload,"sha256":hashlib.sha256(encode(payload)).hexdigest()})
        if len(raw)>4096:raise ValueError("HC09_CONTROL_SNAPSHOT_TOO_BIG")
        return raw

    @classmethod
    def restore(cls,data):
        if type(data) is not bytes or not 0<len(data)<=4096:
            raise ValueError("HC09_CONTROL_SNAPSHOT_REJECTED")
        try:
            value=json.loads(data)
            if type(value) is not dict or set(value)!={"payload","sha256"}:
                raise ValueError("HC09_CONTROL_ENVELOPE")
            p=value["payload"]
            required={"schema","contexts","selected","mismatch","n","switches","created","unexplained"}
            if type(p) is not dict or set(p)!=required or p["schema"]!=SCHEMA:
                raise ValueError("HC09_CONTROL_SCHEMA")
            if hashlib.sha256(encode(p)).hexdigest()!=value["sha256"]:
                raise ValueError("HC09_CONTROL_HASH")
            banks=p["contexts"]
            if (type(banks) is not list or not 1<=len(banks)<=2 or
                any(type(bank) is not list or len(bank)!=4 or
                    any(type(mask) is not int or not 1<=mask<=FULL for mask in bank)
                    for bank in banks)):
                raise ValueError("HC09_CONTROL_BANKS")
            if type(p["selected"]) is not int or not 0<=p["selected"]<len(banks):
                raise ValueError("HC09_CONTROL_SELECTED")
            if type(p["mismatch"]) is not bool:raise ValueError("HC09_CONTROL_MISMATCH")
            for name in ("n","switches","created","unexplained"):
                if type(p[name]) is not int or not 0<=p[name]<=100000:
                    raise ValueError("HC09_CONTROL_COUNTER")
            if p["created"]!=len(banks)-1:raise ValueError("HC09_CONTROL_RELATION")
            m=cls()
            m.contexts=[bank[:] for bank in banks]
            m.selected=p["selected"];m.mismatch=p["mismatch"]
            for name in ("n","switches","created","unexplained"):
                setattr(m,name,p[name])
            if m.snapshot()!=data:raise ValueError("HC09_CONTROL_NOT_CANONICAL")
            return m
        except (TypeError,ValueError,UnicodeError,OverflowError,KeyError) as e:
            raise ValueError("HC09_CONTROL_SNAPSHOT_REJECTED") from e
