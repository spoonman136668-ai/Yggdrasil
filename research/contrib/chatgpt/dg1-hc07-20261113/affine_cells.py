"""HC07: non-token, bounded executable causal-dependency graph cells.

Each action's unknown effect is an affine Boolean causal program over
**any subset** of four observed state variables plus unknown sign. These
are source-agnostic fixed candidate programs, not hidden graph labels.
All version-space elimination uses charged public action consequences.
"""
from __future__ import annotations
import json
import hashlib
from fractions import Fraction

N_ACTIONS=4
N_STATES=16
CANDIDATES=32
FULL=(1<<CANDIDATES)-1
SNAP_LIMIT=1024
SCHEMA="ygg.dg1-hc07.affine-causal-graph-dev.v1"


def state_checked(value):
    if type(value) is not int or not 0 <= value < N_STATES:
        raise ValueError("HC07_BAD_PUBLIC_STATE")
    return value


def action_checked(value):
    if type(value) is not int or not 0 <= value < N_ACTIONS:
        raise ValueError("HC07_BAD_PUBLIC_ACTION")
    return value


def program_effect(state, program_id):
    state_checked(state)
    if type(program_id) is not int or not 0 <= program_id < CANDIDATES:
        raise ValueError("HC07_BAD_PROGRAM")
    parent_mask=program_id>>1
    sign=program_id & 1
    return ((state & parent_mask).bit_count() & 1) ^ sign


def remove_inconsistent(old_mask, state, observed_effect):
    return sum(
        1<<h for h in range(CANDIDATES)
        if old_mask & (1<<h) and program_effect(state,h)==observed_effect
    )


def split_counts(mask, state):
    zeros=ones=0
    for h in range(CANDIDATES):
        if mask & (1<<h):
            if program_effect(state,h):
                ones+=1
            else:
                zeros+=1
    return zeros,ones


def gini(mask,state):
    z,o=split_counts(mask,state)
    n=z+o
    return Fraction(2*z*o,n*n) if n else Fraction(0)


def canonical(data):
    return json.dumps(data,sort_keys=True,separators=(",",":"),
                      allow_nan=False).encode("ascii")


class AffineCausalCells:
    __slots__=("surviving","observations","violations")

    def __init__(self):
        self.surviving=[FULL]*N_ACTIONS
        self.observations=0
        self.violations=0

    @property
    def logical_hypothesis_bits(self):
        return N_ACTIONS*CANDIDATES

    def observe(self,before,action,after):
        state_checked(before)
        action_checked(action)
        state_checked(after)
        if after not in (before,before^(1<<action)):
            raise ValueError("HC07_NONLOCAL_PHYSICAL_OUTCOME")
        e=int(before!=after)
        old=self.surviving[action]
        next_mask=remove_inconsistent(old,before,e)
        if old and not next_mask:
            self.violations+=1
        self.surviving[action]=next_mask
        self.observations+=1

    def predict(self,state,action):
        state_checked(state)
        action_checked(action)
        zeros,ones=split_counts(self.surviving[action],state)
        if (zeros and ones) or (not zeros and not ones):
            return None
        return state^((1 if ones else 0)<<action)

    def choose(self,state):
        state_checked(state)
        scores=[gini(self.surviving[a],state) for a in range(N_ACTIONS)]
        return max(range(N_ACTIONS),key=lambda a:(scores[a],-a))

    def program_support(self):
        return [x.bit_count() for x in self.surviving]

    def snapshot(self):
        p={
            "schema":SCHEMA,"surviving":self.surviving,
            "observations":self.observations,"violations":self.violations
        }
        v=canonical({"payload":p,"sha256":hashlib.sha256(canonical(p)).hexdigest()})
        if len(v)>SNAP_LIMIT:
            raise ValueError("HC07_CHECKPOINT_SIZE")
        return v

    @classmethod
    def restore(cls,data):
        if type(data) is not bytes or not 0 < len(data)<=SNAP_LIMIT:
            raise ValueError("HC07_CHECKPOINT_REJECTED")
        try:
            o=json.loads(data)
            if type(o) is not dict or set(o)!={"payload","sha256"}:
                raise ValueError("HC07_BAD_ENVELOPE")
            p=o["payload"]
            if (type(p) is not dict or
                set(p)!={"schema","surviving","observations","violations"} or
                p["schema"]!=SCHEMA):
                raise ValueError("HC07_BAD_SCHEMA")
            if hashlib.sha256(canonical(p)).hexdigest()!=o["sha256"]:
                raise ValueError("HC07_BAD_HASH")
            surviving=p["surviving"]
            if (type(surviving) is not list or len(surviving)!=N_ACTIONS
                or any(type(x) is not int or not 0<=x<=FULL for x in surviving)):
                raise ValueError("HC07_BAD_HYPOTHESES")
            n=p["observations"]
            violations=p["violations"]
            if (type(n) is not int or type(violations) is not int or
                not 0<=violations<=n<=100000):
                raise ValueError("HC07_BAD_COUNTERS")
            m=cls()
            m.surviving=surviving[:]
            m.observations=n
            m.violations=violations
            if m.snapshot()!=data:
                raise ValueError("HC07_NONCANONICAL")
            return m
        except (ValueError,TypeError,UnicodeError,KeyError,OverflowError) as exc:
            raise ValueError("HC07_CHECKPOINT_REJECTED") from exc
