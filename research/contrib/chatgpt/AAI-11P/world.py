"""AAI-11P six-bit structural causal task -- simulator only, no science first-use.

Hidden labels/formulas are confined to this module, never passed to controls.
Only explicit three synthetic fixture names are admitted to source diagnostics.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json

INPUTS = tuple(itertools.product((0,1),repeat=6))
GOALS = tuple(itertools.product((0,1),repeat=3))
ACTIONS = tuple((i,v) for i in range(6) for v in (0,1))
LAWS = ("A","B","C","D","E","F")
TRAIN = ("A","B")
TRANSFER = ("C","D","E","F")
FIXTURES = ("mechanical:alpha","mechanical:beta","mechanical:gamma")
PUBLIC_KEYS = frozenset(("x","mediators","goal","reward","actions_taken"))
COST = .05


def bits(values,n):
    try:
        seq = tuple(values)
    except TypeError as exc:
        raise ValueError("invalid binary vector") from exc
    if len(seq)!=n or any(type(v) is not int or v not in (0,1) for v in seq):
        raise ValueError("invalid binary vector")
    return seq


def intermediates(law,x):
    """Privileged causal-equations evaluator. NEVER imported by a learner."""
    v=bits(x,6)
    a,b,c,d,e,f=v
    if law=="A":
        m0=a^b; m1=c&d; m2=m0^e
    elif law=="B":
        m0=b|c; m1=d^e; m2=m1&f
    elif law=="C":
        m0=a^f; m1=b&e; m2=m0^m1
    elif law=="D":
        m0=a&d; m1=c^f; m2=m0|m1
    elif law=="E":
        m0=a|e; m1=b&f; m2=m0^m1
    elif law=="F":
        m0=b^d; m1=c|e; m2=m0&m1
    else:
        raise ValueError("unknown privileged simulator regime")
    return (m0,m1,m2)


def reward(m,g,steps):
    m=bits(m,3);g=bits(g,3)
    if type(steps) is not int or not 0<=steps<=2:
        raise ValueError("invalid action count")
    return sum(a==b for a,b in zip(m,g)) - COST*steps


def start(law,x,goal):
    x=bits(x,6);goal=bits(goal,3)
    m=intermediates(law,x)
    return {"x":list(x),"mediators":list(m),"goal":list(goal),
            "reward":reward(m,goal,0),"actions_taken":0}


def do(law,row,action):
    if type(row) is not dict or set(row)!=PUBLIC_KEYS:
        raise ValueError("simulator public state schema mismatch")
    x=list(bits(row["x"],6));goal=bits(row["goal"],3)
    steps=row["actions_taken"]
    if tuple(row["mediators"]) != intermediates(law,x):
        raise ValueError("simulator state drift")
    if type(steps) is not int or steps not in (0,1):
        raise ValueError("two intervention steps maximum")
    if action not in ACTIONS:
        raise ValueError("illegal intervention")
    x[action[0]]=action[1]
    m=intermediates(law,x)
    return {"x":x,"mediators":list(m),"goal":list(goal),
            "reward":reward(m,goal,steps+1),"actions_taken":steps+1}


def visible(row):
    if type(row) is not dict or set(row)!=PUBLIC_KEYS:
        raise ValueError("learner received missing or private field")
    x=bits(row["x"],6);m=bits(row["mediators"],3);goal=bits(row["goal"],3)
    n=row["actions_taken"]
    if type(n) is not int or n not in (0,1,2):
        raise ValueError("invalid public action count")
    if type(row["reward"]) not in (int,float):
        raise ValueError("invalid public reward")
    if abs(row["reward"]-reward(m,goal,n))>1e-9:
        raise ValueError("public reward inconsistent with observed mediator")
    return (x,m)


def copy_public(row):
    visible(row)
    return {"x":list(row["x"]),"mediators":list(row["mediators"]),
            "goal":list(row["goal"]),"reward":row["reward"],
            "actions_taken":row["actions_taken"]}


def fixture(key):
    if type(key) is not str or key not in FIXTURES:
        raise PermissionError("AAI11P SCIENTIFIC WORLD FIRST USE DISARMED")
    return key


def index(key,phase,trial,dimension,size):
    fixture(key)
    if type(trial) is not int or not 0<=trial<8192:
        raise ValueError("invalid fixture trial")
    q=f"AAI11P|{key}|{phase}|{trial}|{dimension}".encode("ascii")
    return int.from_bytes(hashlib.sha256(q).digest()[:8],"big")%size


def fixture_trial(key,phase,trial):
    fixture(key)
    return (INPUTS[index(key,phase,trial,"x",len(INPUTS))],
            GOALS[index(key,phase,trial,"goal",len(GOALS))],
            ACTIONS[index(key,phase,trial,"do",len(ACTIONS))])


def pair(law,key,phase,trial):
    x,g,a=fixture_trial(key,phase,trial)
    first=start(law,x,g)
    second=do(law,first,a)
    return (copy_public(first),copy_public(second))


def setbit(x,action):
    x=list(bits(x,6));i,v=action;x[i]=v
    return tuple(x)


def exact_oracle(law,x,goal):
    """Privileged actual-law oracle, only for benchmark admission/report."""
    x=bits(x,6);goal=bits(goal,3)
    best=reward(intermediates(law,x),goal,0)
    for first in ACTIONS:
        x1=setbit(x,first)
        best=max(best,reward(intermediates(law,x1),goal,1))
        for second in ACTIONS:
            x2=setbit(x1,second)
            best=max(best,reward(intermediates(law,x2),goal,2))
    return best


def distinguish(law1,law2,x):
    # One actual same public intervention, observable outcome differs.
    for action in ACTIONS:
        x1=setbit(x,action)
        if intermediates(law1,x1)!=intermediates(law2,x1):
            return True
    return False


def mechanics():
    pairs=tuple(itertools.combinations(LAWS,2))
    unidentifiable={a+b:[list(x) for x in INPUTS if not distinguish(a,b,x)]
                    for a,b in pairs}
    proportions={}
    for law in LAWS:
        helps=0
        for x in INPUTS:
            for goal in GOALS:
                before=start(law,x,goal)
                if any((after:=do(law,before,a))["mediators"]!=before["mediators"]
                       and after["reward"]>before["reward"] for a in ACTIONS):
                    helps+=1
        proportions[law]=helps/(len(INPUTS)*len(GOALS))
    rows=[]
    for law in LAWS:
        for x in INPUTS:
            for goal in GOALS:
                first=start(law,x,goal)
                if set(first)!=PUBLIC_KEYS:
                    raise AssertionError("private fields leaked")
                for action in ACTIONS:
                    after=do(law,first,action)
                    if after["x"]!=list(setbit(x,action)):
                        raise AssertionError("do intervention did not persist")
                    rows.append([law,list(x),list(goal),list(action),
                                 after["mediators"],after["reward"]])
    wire=json.dumps(rows,sort_keys=True,separators=(",",":")).encode()
    checks={
        "64_binary_inputs":len(INPUTS)==64,
        "8_goals":len(GOALS)==8,
        "12_actual_do_actions":len(ACTIONS)==12,
        "six_distinct_laws":len(LAWS)==6,
        "pairwise_single_do_identifiable_every_x":all(not xs for xs in unidentifiable.values()),
        "consequential_interventions_in_every_law":all(v>=.20 for v in proportions.values()),
        "all_exhaustive_first_step_cases":len(rows)==len(LAWS)*len(INPUTS)*len(GOALS)*len(ACTIONS),
        "science_first_use_disarmed":True,
    }
    return {"schema":"yggdrasil.contrib.aai11p.mechanical.v1",
            "checks":checks,
            "unidentifiable_examples_per_pair":{k:len(v) for k,v in unidentifiable.items()},
            "consequential_fraction":proportions,
            "trace_sha256":hashlib.sha256(wire).hexdigest(),
            "cases":len(rows),"science_cohorts_consumed":0}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mechanical",action="store_true")
    p.add_argument("--primary",action="store_true")
    args=p.parse_args()
    if args.primary or not args.mechanical:
        p.error("AAI11P SCIENTIFIC FIRST USE DISARMED")
    result=mechanics()
    print(json.dumps(result,sort_keys=True))
    if not all(result["checks"].values()):
        raise SystemExit("AAI11P_BENCHMARK_MECHANICAL_INADEQUATE_NO_SCIENCE")


if __name__=="__main__":
    main()
