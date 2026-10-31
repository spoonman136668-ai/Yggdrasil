"""MG94-AG public-context conventional routing control; development only.

Contexts are prefixes of observed binary events, not family labels. Candidate
and independent conventional contextual selector use the same public context
and identical training data. This is not a native distributed architecture.
"""
from consequential_routing import Cells
from frozen_routing_selector import TRAIN, HELDOUT
import json

COST=1
def public_context(events):
    if len(events)<2:
        raise ValueError("PUBLIC_PREFIX_TOO_SHORT")
    return tuple(events[:2])

def net(events, route):
    model=Cells(route)
    correct=sum(model.step(x)==x for x in events)
    return correct-COST*model.messages

def fit(examples):
    gains={}
    for events in examples:
        key=public_context(events)
        gains[key]=gains.get(key,0)+net(events,True)-net(events,False)
    return {key:gain>0 for key,gain in gains.items()}

def evaluate():
    policy=fit(TRAIN.values())
    # Missing contexts default to communication disabled, fixed before eval.
    output={}
    for name,events in HELDOUT.items():
        key=public_context(events)
        choice=policy.get(key,False)
        output[name]={"public_prefix":list(key),"routed":choice,
                      "selected_net":net(events,choice),"off_net":net(events,False),
                      "on_net":net(events,True)}
    return {"schema":"mg94.public_context.conventional.v1",
            "frozen_policy":{str(k):v for k,v in policy.items()},
            "heldout":output,"scientific_gain":"UNVERIFIED"}
if __name__=="__main__":
    print(json.dumps(evaluate(),indent=2,sort_keys=True))
