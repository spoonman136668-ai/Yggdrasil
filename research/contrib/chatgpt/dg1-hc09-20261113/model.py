"""DG1-HC09: bounded native non-token causal program memory, source-only DEV.

Two banks of version-space programs per physical mechanism action. Programs
contain both affine and 3-bit-majority rules; source world/regime is NEVER
imported here. A contradiction can switch to an older retained bank, but
cannot erase that bank when both slots are occupied.
"""
from __future__ import annotations
import hashlib
import json
from fractions import Fraction
from itertools import combinations

ACTIONS=4
RULES=40
FULL=(1<<RULES)-1
TRIPLES=tuple(combinations(range(4),3))
SNAP_LIMIT=4096
SCHEMA="ygg.dg1-hc09.two-bank-nonlinear-memory.v1"


def valid_state(s):
    if type(s) is not int or not 0<=s<16: raise ValueError("HC09_BAD_STATE")
    return s


def valid_action(a):
    if type(a) is not int or not 0<=a<4: raise ValueError("HC09_BAD_ACTION")
    return a


def effect(state,h):
    valid_state(state)
    if type(h) is not int or not 0<=h<RULES:
        raise ValueError("HC09_BAD_RULE")
    if h<32:
        return (((state & (h>>1)).bit_count()) & 1) ^ (h&1)
    triple=TRIPLES[(h-32)//2]
    votes=sum((state>>i)&1 for i in triple)
    return int(votes>=2)^(h&1)


def filter_rules(mask,state,e):
    return sum(1<<h for h in range(RULES)
               if mask&(1<<h) and effect(state,h)==e)


def counts(mask,state):
    z=o=0
    for h in range(RULES):
        if mask&(1<<h):
            if effect(state,h): o+=1
            else: z+=1
    return z,o


def gini(mask,state):
    z,o=counts(mask,state)
    n=z+o
    return Fraction(2*z*o,n*n) if n else Fraction(0)


def encode(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False).encode("ascii")


class DualRegimeCausalCells:
    def __init__(self,*,bank_limit=2,reactivate=True):
        if type(bank_limit) is not int or not 1<=bank_limit<=2: raise ValueError("HC09_BANK_LIMIT")
        if type(reactivate) is not bool: raise ValueError("HC09_REACTIVATION_FLAG")
        self.bank_limit=bank_limit
        self.reactivate=reactivate
        self.banks=[[FULL]*ACTIONS]
        self.active=0
        self.unresolved=False
        self.observations=0
        self.splits=0
        self.reactivations=0
        self.unresolved_events=0

    @property
    def capacity_bits(self):
        return self.bank_limit*RULES*ACTIONS

    def observe(self,before,action,after):
        valid_state(before); valid_action(action); valid_state(after)
        if after not in (before,before^(1<<action)):
            raise ValueError("HC09_NONLOCAL_PHYSICAL_DELTA")
        physical_effect=int(before!=after)
        active_mask=filter_rules(self.banks[self.active][action],
                                 before,physical_effect)
        if active_mask:
            self.banks[self.active][action]=active_mask
            self.unresolved=False
        else:
            match=next((i for i,bank in enumerate(self.banks)
                        if i!=self.active and
                        filter_rules(bank[action],before,physical_effect)),None)
            if match is not None and self.reactivate:
                self.active=match
                self.banks[self.active][action]=filter_rules(
                    self.banks[self.active][action],before,physical_effect)
                self.reactivations+=1
                self.unresolved=False
            elif len(self.banks)<self.bank_limit:
                new=[FULL]*ACTIONS
                new[action]=filter_rules(FULL,before,physical_effect)
                self.banks.append(new)
                self.active=len(self.banks)-1
                self.splits+=1
                self.unresolved=False
            else:
                # Neither overwrites a retained model nor invents a label.
                self.unresolved=True
                self.unresolved_events+=1
        self.observations+=1
        return not self.unresolved

    def predict(self,state,action):
        valid_state(state);valid_action(action)
        if self.unresolved:return None
        z,o=counts(self.banks[self.active][action],state)
        if (z and o) or not (z or o):return None
        return state^((1 if o else 0)<<action)

    def choose(self,state,flips,limit):
        valid_state(state)
        if (type(flips) is not int or type(limit) is not int
            or not 0<=flips<=limit<=8):
            raise ValueError("HC09_BAD_FLIP_BUDGET")
        candidates=self.banks[self.active]
        info=[gini(candidates[a],state) for a in range(4)]
        if max(info):
            return ("causal",max(range(4),key=lambda a:(info[a],-a)))
        if flips<limit:
            v=[sum(gini(candidates[a],state^(1<<bit)) for a in range(4))
               for bit in range(4)]
            return ("flip",max(range(4),key=lambda bit:(v[bit],-bit)))
        return ("causal",0)

    def supports(self):
        return [tuple(mask.bit_count() for mask in b) for b in self.banks]

    def snapshot(self):
        p={"schema":SCHEMA,"bank_limit":self.bank_limit,"reactivate":self.reactivate,
           "banks":self.banks,"active":self.active,"unresolved":self.unresolved,
           "observations":self.observations,"splits":self.splits,
           "reactivations":self.reactivations,"unresolved_events":self.unresolved_events}
        b=encode({"payload":p,"sha256":hashlib.sha256(encode(p)).hexdigest()})
        if len(b)>SNAP_LIMIT:raise ValueError("HC09_SNAPSHOT_TOO_LARGE")
        return b

    @classmethod
    def restore(cls,raw):
        if type(raw) is not bytes or not 0<len(raw)<=SNAP_LIMIT:
            raise ValueError("HC09_BAD_CHECKPOINT")
        try:
            packet=json.loads(raw)
            if type(packet) is not dict or set(packet)!={"payload","sha256"}:
                raise ValueError("HC09_BAD_ENVELOPE")
            p=packet["payload"]
            required={"schema","bank_limit","reactivate","banks","active","unresolved",
                      "observations","splits","reactivations","unresolved_events"}
            if type(p) is not dict or set(p)!=required or p["schema"]!=SCHEMA:
                raise ValueError("HC09_BAD_SCHEMA")
            if hashlib.sha256(encode(p)).hexdigest()!=packet["sha256"]:
                raise ValueError("HC09_BAD_HASH")
            m=cls(bank_limit=p["bank_limit"],reactivate=p["reactivate"])
            bs=p["banks"]
            if (type(bs) is not list or not 1<=len(bs)<=m.bank_limit or
                any(type(b) is not list or len(b)!=4 or
                    any(type(mask) is not int or not 1<=mask<=FULL
                        for mask in b) for b in bs)):
                raise ValueError("HC09_BAD_BANK_MASK")
            if type(p["active"]) is not int or not 0<=p["active"]<len(bs):
                raise ValueError("HC09_BAD_ACTIVE")
            if type(p["unresolved"]) is not bool:raise ValueError("HC09_BAD_UNRESOLVED")
            for key in ("observations","splits","reactivations","unresolved_events"):
                if type(p[key]) is not int or not 0<=p[key]<=100000:
                    raise ValueError("HC09_BAD_COUNTER")
            if p["splits"]!=len(bs)-1 or p["reactivations"]>p["observations"]:
                raise ValueError("HC09_BAD_COUNTER_RELATION")
            m.banks=[b[:] for b in bs]
            m.active=p["active"];m.unresolved=p["unresolved"]
            for key in ("observations","splits","reactivations","unresolved_events"):
                setattr(m,key,p[key])
            if m.snapshot()!=raw:raise ValueError("HC09_NONCANONICAL")
            return m
        except (ValueError,TypeError,UnicodeError,KeyError,OverflowError) as exc:
            raise ValueError("HC09_BAD_CHECKPOINT") from exc
