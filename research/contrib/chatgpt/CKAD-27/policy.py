"""Frozen CKAD27 two-stage native reward-hypothesis intervention policy.

The policy only reads the existing cumulative native learner's posterior
candidate forecasts. No hidden world variables, intervention consequences,
held-out labels, weights or source phase metadata enter these choices.

No native code or native model contract is modified. This is experimental
policy arbitration using native non-token causal predictions, not a rival
learner or controller.
"""
from fractions import Fraction
from hashlib import sha256

ARMS=("directed","native","random")
QUARTER_EXPLOIT=4


def require(ok,reason):
    if not ok:
        raise ValueError("CKAD27_POLICY_"+reason)


def weighted_disagreement(model,view,first,state,second):
    experience=model._experience
    require(experience is not None,"EXPERIENCE")
    weights=experience._context_weights_for(view,first,state)
    predictions=experience._context_predictions(view,first,state,second)
    require(len(weights)==len(predictions) and
            all(type(x) is Fraction and 0<=x<=1 for x in predictions) and
            sum(weights,Fraction(0))==1,"WEIGHTS")
    mean=sum((w*p for w,p in zip(weights,predictions)),Fraction(0))
    return sum((w*(p-mean)**2 for w,p in zip(weights,predictions)),Fraction(0))


def directed_first(model,view):
    require(type(view) is tuple and len(view)==2,"PUBLIC_VIEW")
    priorities=[]
    for first in (0,1):
        probability=model.experience_context_forecast(view,first)
        variance=Fraction(0)
        for state in (0,1):
            best=max(weighted_disagreement(model,view,first,state,second)
                     for second in (0,1))
            variance += (probability if state else 1-probability)*best
        priorities.append(variance)
    if priorities[0]==priorities[1]:
        return model.experience_context_explore(view)
    return int(priorities[1]>priorities[0])


def directed_second(model,view,first,state):
    v=[weighted_disagreement(model,view,first,state,x) for x in (0,1)]
    if v[0]==v[1]:
        return model.experience_context_explore(view,first,state)
    return int(v[1]>v[0])


def random_bits(namespace,index):
    require(type(namespace) is str and namespace.isascii() and
            type(index) is int and index>=0,"RANDOM_SOURCE")
    raw=sha256(f"ckad27-action-v1/{namespace}/{index}".encode("ascii")).digest()
    return raw[0]&1,raw[1]&1


def choices(model,view,arm,namespace,index):
    require(arm in ARMS and type(index) is int and index>=0,"ARM")
    if index%QUARTER_EXPLOIT==3:
        plan=model.experience_context_plan(view)
        return (lambda _initial: plan["first_action"],
                lambda _initial,first,state: plan["second_actions"][first][state])
    if arm=="directed":
        return (lambda _initial: directed_first(model,view),
                lambda _initial,first,state: directed_second(model,view,first,state))
    if arm=="native":
        return (lambda _initial: model.experience_context_explore(view),
                lambda _initial,first,state: model.experience_context_explore(view,first,state))
    first,second=random_bits(namespace,index)
    return (lambda _initial: first,lambda _initial,_first,_state: second)
