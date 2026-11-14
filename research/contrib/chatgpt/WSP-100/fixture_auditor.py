"""Independent WSP100 fixture finite-version-space auditor.

No import of the simulator, sampled program, transition function or oracle
data. Exhaustive ONLY over the 256-member public DEV fixture catalogue.
This does not certify identifiability of the future broader original grammar.
"""
from __future__ import annotations
from itertools import product
import hashlib
import json

HYPOTHESES=tuple(product(range(4),repeat=4))
assert len(HYPOTHESES)==256


def _primitive(f,a,b):
    functions=(
        lambda a,b:(a+b)%4,
        lambda a,b:a^b,
        lambda a,b:a if b%2==0 else 3-a,
        lambda a,b:(a*b+b)%4,
    )
    return functions[f](a,b)


def _step(x,hidden,action,parameters):
    family,wiring,trigger,phase=parameters
    next_visible=[]
    for i in range(6):
        q=_primitive(family,x[(i+wiring)%6],x[(i+1+wiring)%6])
        q=_primitive((family+1+i%3)%4,q,x[(i+3)%6])
        q=(q+phase*(1+i%2))%4
        if i<4: q=(q+hidden[i%2])%4
        next_visible.append(q)
    next_hidden=list(hidden)
    for j in range(2):
        enabled=(action==(trigger+j)%4)
        parity=(x[(wiring+j)%6]+x[(wiring+j+2)%6]+phase+j)%2
        if enabled and parity:
            next_hidden[j]=(hidden[j]+1+(phase+j)%3)%4
    return tuple(next_visible),tuple(next_hidden)


def consistent(program,episodes):
    for episode in episodes:
        if not episode or len(episode)!=4:
            raise ValueError("malformed episode length")
        x=tuple(episode[0][0])
        hidden=(0,0)
        for source_x,action,target_y,reward in episode:
            if tuple(source_x)!=x or not (type(action) is int and 0<=action<4):
                raise ValueError("malformed action/history")
            y,hidden=_step(x,hidden,action,program)
            if y!=tuple(target_y) or reward!=int((y[0]+y[1])%4==3):
                return False
            x=y
    return True


def version_space(episodes):
    episodes=tuple(episodes)
    return tuple(program for program in HYPOTHESES if consistent(program,episodes))


def rollout(program,initial,actions):
    x=tuple(initial)
    if len(x)!=6 or any(type(v) is not int or not 0<=v<4 for v in x):
        raise ValueError("invalid heldout source state")
    if len(actions)>4:
        raise ValueError("action horizon exceeded")
    hidden=(0,0)
    predictions=[]
    for a in actions:
        if type(a) is not int or not 0<=a<4:
            raise ValueError("invalid heldout action")
        x,hidden=_step(x,hidden,a,program)
        predictions.append(x)
    return tuple(predictions)


def identifiability(survivors,plan):
    if not survivors:
        return {"classification":"INVALID_NO_CONSISTENT_HYPOTHESIS",
                "survivor_count":0,"identifiable":0,"total":0,"fraction":None}
    if not isinstance(plan,dict) or plan.get("schema")!="wsp100.fixture-heldout-plan.v1":
        raise ValueError("unknown plan schema")
    targets=plan["targets"]
    nslots=len(targets)*2*3*6
    # No target truth or sampled oracle program is read.
    first=None
    invariant=[True]*nslots
    for program in survivors:
        signature=[]
        for initial,a,b in targets:
            for seq in (a,b):
                for state in rollout(program,initial,seq):
                    signature.extend(state)
        if len(signature)!=nslots:
            raise ValueError("prediction size drift")
        if first is None:
            first=signature
        else:
            invariant=[stable and (v==w)
                       for stable,v,w in zip(invariant,first,signature)]
    identifiable=sum(invariant)
    return {"classification":"DEV_FIXTURE_AUDIT_ONLY",
            "survivor_count":len(survivors),
            "identifiable":identifiable,"total":nslots,
            "fraction":identifiable/nslots}


def audit_fixture(bundle,plan):
    if not isinstance(bundle,dict) or bundle.get("fixture_id")!=plan.get("fixture_id"):
        raise ValueError("source/plan identity mismatch")
    observed=tuple(bundle["passive"])+tuple(bundle["active"])
    survivors=version_space(observed)
    proof=identifiability(survivors,plan)
    proof["source_sha256"]=bundle["source_sha256"]
    proof["plan_sha256"]=plan["plan_sha256"]
    return proof
