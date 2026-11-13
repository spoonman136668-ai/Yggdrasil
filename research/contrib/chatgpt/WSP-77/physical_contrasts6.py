"""WSP77 physically paid empirical action-consequence contrast policy.

Only already *charged* public (before,action,after) facts. No model-imagined
future states, source import, hidden roles, evaluator truth or free source step.
One action is chosen per real continuous B source state and must be paid
before a following call. Four-channel B balancing never learns future physics.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from hashlib import sha256
from random import Random
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from repair6 import repair,fitted_readout

ACTIONS=tuple(range(6))
PHASE_A=96
PHASE_B=48


def _check_state(s):
    if type(s) is not tuple or len(s)!=6 or any(type(v) is not int
            or v not in (0,1) for v in s):
        raise ValueError("invalid observable six-bit state")
    return s


def empirical_paid_facts(rows):
    """Validate trajectory and produce evidence ONLY from real charges."""
    if type(rows) not in (list,tuple) or not 1<=len(rows)<=144:
        raise ValueError("improper real action custody")
    lookup={}
    evidence=defaultdict(dict)
    signatures=defaultdict(set)
    states={_check_state(rows[0][0])}
    for idx,(before,action,after) in enumerate(rows):
        _check_state(before);_check_state(after)
        if type(action) is not int or action not in ACTIONS:
            raise ValueError("wrong public action")
        if idx and rows[idx-1][2]!=before:
            raise ValueError("fabricated disconnected physical action")
        key=(before,action)
        if key in lookup and lookup[key]!=after:
            raise ValueError("unaccounted stochastic/hidden public contradiction")
        lookup[key]=after
        evidence[before][action]=after
        signatures[action].add(tuple(int(x!=y) for x,y in zip(before,after)))
        states.add(after)
    return lookup,evidence,signatures,states


def paid_action_contrasts(rows):
    """Unique distinct-actions-at-SAME-real-state with different outcomes."""
    _,observed,_,_=empirical_paid_facts(rows)
    results=[]
    for state,by_action in observed.items():
        for a in sorted(by_action):
            for b in sorted(by_action):
                if a<b and by_action[a]!=by_action[b]:
                    results.append((state,a,b))
    return tuple(sorted(results))


def choose_observed_contrast(state,charged,seed,Bstep):
    """Fixed 12+8+4+4+2/(1+B action count), hard balanced B action pool."""
    _check_state(state)
    if type(seed) is not int or type(Bstep) is not int or not 0<=Bstep<48:
        raise ValueError("invalid paid B step")
    if type(charged) not in (list,tuple) or len(charged)!=96+Bstep:
        raise ValueError("real A+B physical action budget mismatch")
    lookup,by_state,effects,_=empirical_paid_facts(charged)
    if charged[-1][2]!=state:
        raise ValueError("not the current physically observed state")
    Bcounts=Counter(a for s,a,y in charged[96:])
    least=min(Bcounts[a] for a in ACTIONS)
    eligible=[a for a in ACTIONS if Bcounts[a]<=least+1]
    known=by_state.get(state,{})
    has_distinct= len(set(known.values()))>=2
    ranked=[]
    for action in eligible:
        uncharged=(state,action) not in lookup
        known_other=any(a!=action for a in known)
        score=(12.0*int(uncharged and known_other)
               +8.0*int(uncharged)
               +4.0*int(uncharged and len(effects.get(action,()))>=2)
               +4.0*int(uncharged and has_distinct)
               +2.0/(1+Bcounts[action]))
        tiebreak=sha256(
            f"WSP77|empirical-contrast|{seed}|{Bstep}|{action}"
            .encode("ascii")).digest()
        ranked.append((-score,tiebreak,action))
    return min(ranked)[2]


def uniform_random(seed):
    return Random(int.from_bytes(sha256(
        f"WSP77|uniform-paid-B|{seed}".encode("ascii")).digest(),"big"))


def balanced_cycle(seed):
    rng=Random(int.from_bytes(sha256(
        f"WSP77|balanced-cycle|{seed}".encode("ascii")).digest(),"big"))
    actions=list(ACTIONS)
    rng.shuffle(actions)
    return tuple(actions*8)
