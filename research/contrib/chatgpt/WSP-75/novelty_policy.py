"""WSP75 source-blind prediction of reachable novelty from paid physics ONLY.

Novelty is grounded in real observations (state/action previously charged,
actually visited states) and counterfactual NEXT public states predicted by
the frozen, paid-experience-trained Stage A neural models. A proposed
counterfactual never constitutes a free source transition or oracle query.
Each call selects EXACTLY one next action, which must then be physically
paid and appended to the continuous source ledger before calling again.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
from pathlib import Path
from random import Random
import sys

_PARENT=Path(__file__).resolve().parents[1]/"WSP-74"
sys.path.insert(0,str(_PARENT))
from repair import policy_action,random_policy,repair,fitted_readout

ACTION_CHANNELS=tuple(range(4))
B_CHARGES=48
MAX_POLICY_SCORE=20.0


def _public_state(state):
    if type(state) is not tuple or len(state)!=4 or any(
            type(x) is not int or x not in (0,1) for x in state):
        raise ValueError("invalid visible physics state")
    return state


def choose_reachable_novelty_action(primary,secondary,state,charged,seed,Bstep):
    """Frozen deterministic 8/4/4/2/2 policy; source-blind, no free steps."""
    _public_state(state)
    if type(seed) is not int or type(Bstep) is not int or not 0<=Bstep<48:
        raise ValueError("illegal B action request")
    if type(charged) not in (tuple,list) or len(charged)!=96+Bstep:
        raise ValueError("missing or duplicated real charged A/B observations")
    paid_pairs=set()
    visited=set()
    Bcounts=Counter()
    for i,(before,action,after) in enumerate(charged):
        _public_state(before)
        _public_state(after)
        if type(action) is not int or action not in ACTION_CHANNELS:
            raise ValueError("unregistered paid action")
        if i and charged[i-1][2]!=before:
            raise ValueError("impossible physical paid-trajectory continuity")
        paid_pairs.add((before,action))
        visited.add(before)
        visited.add(after)
        if i>=96:
            Bcounts[action]+=1
    if charged[-1][2]!=state:
        raise ValueError("requested action outside real current physical state")
    candidates=[]
    for action in ACTION_CHANNELS:
        left=primary.predict(state,action,force=True)
        right=secondary.predict(state,action,force=True)
        _public_state(left)
        _public_state(right)
        score=(8.0*int((state,action) not in paid_pairs)
               +4.0*int(left not in visited)
               +4.0*int(right not in visited)
               +2.0*int(left!=right)
               +2.0/(1+Bcounts[action]))
        tie=sha256(f"WSP75|reachable-novelty|{seed}|{Bstep}|{action}"
                   .encode("ascii")).digest()
        candidates.append((-score,tie,action))
    winner=min(candidates)
    if not 0.0<=-winner[0]<=MAX_POLICY_SCORE:
        raise AssertionError("novelty policy exceeded preregistered range")
    return winner[2]


def uniform_random(seed):
    """Independent from WSP74 disagreement/random policy and physics."""
    return Random(int.from_bytes(sha256(
        f"WSP75|uniform-physical-action|{seed}".encode("ascii")).digest(),"big"))
