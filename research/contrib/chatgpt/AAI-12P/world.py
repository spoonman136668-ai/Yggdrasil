"""AAI-12P structurally heterogeneous source-only causal worlds.

No learner may import this privileged simulator; only the public observations
returned by start/do/pair are delivered. Source-only fixture names are exact,
scientific seed/world first-use is technically disarmed.
"""
from __future__ import annotations
import hashlib
import itertools
import json
import math
from functools import lru_cache

INPUTS=tuple(itertools.product((0,1),repeat=8))
GOALS=tuple(itertools.product((0,1),repeat=4))
ACTIONS=tuple((i,v) for i in range(8) for v in (0,1))
COST=.08
FAMILIES=("chain","context_switch","compensator","inhibitor")
FIT=("mechanical:fit:chain:0","mechanical:fit:chain:1",
     "mechanical:fit:context_switch:0","mechanical:fit:compensator:0")
TRANSFER=("mechanical:transfer:chain:2","mechanical:transfer:chain:3",
          "mechanical:transfer:context_switch:1","mechanical:transfer:context_switch:2",
          "mechanical:transfer:context_switch:3","mechanical:transfer:compensator:1",
          "mechanical:transfer:compensator:2","mechanical:transfer:compensator:3",
          "mechanical:transfer:inhibitor:0","mechanical:transfer:inhibitor:1",
          "mechanical:transfer:inhibitor:2","mechanical:transfer:inhibitor:3")
WORLDS=(*FIT,*TRANSFER)
FIXTURES=("mechanical:alpha","mechanical:beta")
PUBLIC_KEYS=frozenset(("x","mediators","goal","reward","actions_taken"))
OPS=("xor","and","or")


def bits(value,size):
    try: seq=tuple(value)
    except TypeError as e: raise ValueError("invalid public bitvector") from e
    if len(seq)!=size or any(type(z) is not int or z not in (0,1) for z in seq):
        raise ValueError("invalid public bitvector")
    return seq


def fixture(value):
    if type(value) is not str or value not in FIXTURES:
        raise PermissionError("AAI12P SCIENTIFIC FIRST USE DISARMED")
    return value


def law_name(value):
    if type(value) is not str or value not in WORLDS:
        raise PermissionError("AAI12P SCIENTIFIC LAW FIRST USE DISARMED")
    return value


def _number(law,field,span):
    law_name(law)
    digest=hashlib.sha256(f"AAI12P-world-v1|{law}|{field}".encode("ascii")).digest()
    return int.from_bytes(digest[:8],"big")%span


@lru_cache(maxsize=16)
def parameters(law):
    """PRIVILEGED deterministic causal law signature; never given to a learner."""
    law_name(law)
    family=law.split(":")[2]
    i=_number(law,"i",6)
    j=(_number(law,"j",5)+(1 if _number(law,"j",5)>=i else 0))
    k=_number(law,"k",6)
    v=_number(law,"l",5)
    el=v+(1 if v>=k else 0)
    return (family,i,j,k,el,_number(law,"p",6),
            *(_number(law,"op"+str(z),3) for z in range(4)))


def _op(tag,a,b):
    if tag==0:return a^b
    if tag==1:return a&b
    if tag==2:return a|b
    raise ValueError("illegal public Boolean operation")


def intermediates(law,x):
    """Privileged causal-equation evaluator. FORBIDDEN to all learners."""
    x=bits(x,8)
    family,i,j,k,el,p,o0,o1,o2,o3=parameters(law)
    if family=="context_switch":
        m0=(x[i]^x[j]) if not x[6] else (x[i]|x[j])
    else:
        m0=_op(o0,x[i],x[j])
    m1=_op(o1,x[k],x[el])
    if family=="chain":
        m2=_op(o2,m0,x[p])
        m3=_op(o3,m1,m2)
    elif family=="context_switch":
        m2=_op(o2,m0,m1)^x[7]
        m3=_op(o3,m2,x[p])
    elif family=="compensator":
        m2=_op(o2,m0,x[p])
        m3=m0^m1^m2^x[7]
    elif family=="inhibitor":
        m2=m0&(1-m1)
        m3=_op(o3,m2,x[p])^x[6]
    else:
        raise ValueError("unregistered structural DAG family")
    return (m0,m1,m2,m3)


def reward(m,goal,steps):
    m=bits(m,4);goal=bits(goal,4)
    if type(steps) is not int or not 0<=steps<=2:
        raise ValueError("invalid real intervention count")
    return sum(int(a==b) for a,b in zip(m,goal))-COST*steps


def visible(row):
    if type(row) is not dict or set(row)!=PUBLIC_KEYS:
        raise ValueError("learner received hidden, missing or private field")
    x=bits(row["x"],8);m=bits(row["mediators"],4);goal=bits(row["goal"],4)
    steps=row["actions_taken"]
    if type(steps) is not int or steps not in (0,1,2):
        raise ValueError("bad public action count")
    if type(row["reward"]) not in (int,float) or not math.isfinite(row["reward"]):
        raise ValueError("bad public reward")
    if abs(reward(m,goal,steps)-row["reward"])>1e-10:
        raise ValueError("public reward inconsistent with observed outcome")
    return x,m


def copy_public(row):
    visible(row)
    return {"x":list(row["x"]),"mediators":list(row["mediators"]),
            "goal":list(row["goal"]),"reward":row["reward"],
            "actions_taken":row["actions_taken"]}


def start(law,x,goal):
    law_name(law)
    x=bits(x,8);goal=bits(goal,4)
    m=intermediates(law,x)
    return {"x":list(x),"mediators":list(m),"goal":list(goal),
            "reward":reward(m,goal,0),"actions_taken":0}


def setbit(x,action):
    x=list(bits(x,8))
    if action not in ACTIONS:raise ValueError("invalid actual do operation")
    x[action[0]]=action[1]
    return tuple(x)


def do(law,public,action):
    law_name(law)
    x,old_m=visible(public)
    if old_m!=intermediates(law,x):
        raise ValueError("causal simulator public outcome does not match actual world")
    if public["actions_taken"]>=2:
        raise ValueError("already used both real do actions")
    next_x=setbit(x,action)
    m=intermediates(law,next_x)
    steps=public["actions_taken"]+1
    return {"x":list(next_x),"mediators":list(m),
            "goal":list(public["goal"]),
            "reward":reward(m,public["goal"],steps),
            "actions_taken":steps}


def _index(fix,law,phase,index,dimension,size):
    fixture(fix);law_name(law)
    if type(index) is not int or not 0<=index<256:
        raise ValueError("source-only trial index out of range")
    if phase not in ("fit","challenge","retention"):
        raise PermissionError("source-only mechanical phase only")
    wire=f"AAI12P|{fix}|{law}|{phase}|{index}|{dimension}".encode("ascii")
    return int.from_bytes(hashlib.sha256(wire).digest()[:8],"big")%size


def pair(law,fix,phase,index):
    x=INPUTS[_index(fix,law,phase,index,"x",len(INPUTS))]
    goal=GOALS[_index(fix,law,phase,index,"goal",len(GOALS))]
    action=ACTIONS[_index(fix,law,phase,index,"do",len(ACTIONS))]
    initial=start(law,x,goal)
    return copy_public(initial),copy_public(do(law,initial,action))


def contexts(fix,law,n=8):
    fixture(fix);law_name(law)
    if type(n) is not int or not 1<=n<=8:
        raise ValueError("only original eight public evaluation contexts")
    # Exactly frozen public x/goal ranking independent of learner identity.
    candidates=((x,g) for x in INPUTS for g in GOALS)
    def key(item):
        x,goal=item
        wire=f"AAI12P-context|{fix}|{law}|{''.join(map(str,x))}|{''.join(map(str,goal))}".encode("ascii")
        return hashlib.sha256(wire).digest()
    return tuple(sorted(candidates,key=key)[:n])


def exact_oracle(law,x,goal):
    """PRIVILEGED 0/1/2-do reward oracle; only scoring evaluator may call."""
    x=bits(x,8);goal=bits(goal,4)
    best=reward(intermediates(law,x),goal,0)
    reachable={intermediates(law,x)}
    for action in ACTIONS:
        x1=setbit(x,action)
        m1=intermediates(law,x1)
        reachable.add(m1)
        best=max(best,reward(m1,goal,1))
        for second in ACTIONS:
            x2=setbit(x1,second)
            m2=intermediates(law,x2)
            reachable.add(m2)
            best=max(best,reward(m2,goal,2))
    return best,int(goal in reachable)


def mechanical_probe():
    """Factual source-law diagnostics only; no model sees these data."""
    signatures={}
    cases=0
    identity=[]
    changed=[]
    consequential=[]
    xgrid=INPUTS[::4]  # fixed 64 public starts, no seed selection
    for law in TRANSFER:
        truth=[intermediates(law,x) for x in INPUTS]
        signatures[law]=hashlib.sha256(json.dumps(truth).encode()).hexdigest()
        for x in xgrid:
            original=intermediates(law,x)
            for a in ACTIONS:
                changed.append(int(intermediates(law,setbit(x,a))!=original))
                cases+=1
            # Every possible goal evaluated for true positive reward improvement.
            for goal in GOALS:
                before=reward(original,goal,0)
                consequential.append(int(any(
                    reward(intermediates(law,setbit(x,a)),goal,1)>before
                    for a in ACTIONS)))
    for idx,law in enumerate(TRANSFER):
        for other in TRANSFER[idx+1:]:
            matched=0
            total=0
            for x in xgrid:
                if any(intermediates(law,setbit(x,a))!=
                       intermediates(other,setbit(x,a)) for a in ACTIONS):
                    matched+=1
                total+=1
            identity.append(matched/total)
    return {
        "schema":"yggdrasil.contrib.aai12p.diverse-causal-mechanics.v1",
        "source_world_truth_signature_count":len(set(signatures.values())),
        "source_transfer_world_count":len(TRANSFER),
        "families":FAMILIES,
        "all_law_pairwise_distinguishability_min":min(identity),
        "real_first_action_outcome_change_fraction":sum(changed)/len(changed),
        "positive_intervention_opportunity_fraction":sum(consequential)/len(consequential),
        "source_true_do_cases_checked":cases,
        "world_signatures_digest_sha256":hashlib.sha256(
            json.dumps(signatures,sort_keys=True).encode()).hexdigest(),
        "first_use_disarmed":True,
        "science_cohorts_consumed":0
    }
