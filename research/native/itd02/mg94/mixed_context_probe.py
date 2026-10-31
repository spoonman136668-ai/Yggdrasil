"""MG94-AJ: mixed familiar/unseen public-prefix development evaluation.

Does not alter preregistered MG94-AD heldout cohort. These are supplemental
synthetic probes, not independent transfer or new native architecture.
"""
from public_context_control import fit, public_context, net
from frozen_routing_selector import TRAIN

PROBES = {
    "familiar_01_shift": [0,1,1,0,0,1]*4,
    "familiar_00_shift": [0,0,1,1]*6,
    "unseen_10_shift": [1,0,0,1,1,0]*4,
    "unseen_11_stable": [1]*24,
}

def run():
    policy=fit(TRAIN.values())
    familiar=set(policy)
    result={}
    for name,stream in PROBES.items():
        prefix=public_context(stream)
        selected=policy.get(prefix,False)
        result[name]={"prefix":list(prefix),"familiar":prefix in familiar,
            "selected_route":selected,"selected_net":net(stream,selected),
            "disabled_net":net(stream,False),"always_net":net(stream,True)}
    assert sum(x["familiar"] for x in result.values())==2
    assert sum(not x["familiar"] for x in result.values())==2
    assert all(not value for value in policy.values())
    return result

if __name__=="__main__":
    import json
    print(json.dumps(run(),sort_keys=True,indent=2))
