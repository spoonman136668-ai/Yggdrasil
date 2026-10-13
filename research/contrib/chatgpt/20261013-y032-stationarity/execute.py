"""Y032: frozen two-schedule paired utility test on keyed synthetic graph."""
import importlib.util
import hashlib
import json
from collections import OrderedDict
from pathlib import Path

OLD=Path(__file__).resolve().parent.parent/"20261013-y031-jump-drift"/"execute.py"
spec=importlib.util.spec_from_file_location("y031_frozen",OLD)
assert spec and spec.loader
prev=importlib.util.module_from_spec(spec)
spec.loader.exec_module(prev)
y30=prev.prior

SCHEDULES={"smooth":(0,1,2,3,4,5,6,7),
           "jump":(0,1,2,9,10,11,4,5)}
WEIGHTS=(1,3,10)


def world(seed,episode,schedule):
    active,neighbor=y30.geometry(seed,episode)
    displacement=SCHEDULES[schedule][episode]
    adjusted={key:{(v+displacement)%16 for v in neighbor[key]} for key in active}
    return active,adjusted


def signature(seed,schedule):
    data=[]
    for ep in range(8):
        active,neighbor=world(seed,ep,schedule)
        data.append([active,[[k,sorted(neighbor[k])] for k in active]])
    return hashlib.sha256(json.dumps(data,separators=(",",":")).encode()).hexdigest()


def evaluate(seed,schedule,read_cache):
    cache=OrderedDict()
    previous_active=set()
    previous_assignment={}
    history={}
    traces=[]
    for ep in range(8):
        active,neighbor=world(seed,ep,schedule)
        assert y30.hall_cardinality(active,neighbor)==7
        prefs={k:cache[k] for k in active if k in cache} if read_cache else {}
        legal={k:v for k,v in prefs.items() if v in neighbor[k]}
        assignment,calls=y30.match(active,neighbor,prefs)
        assert len(assignment)==7
        returning=[key for key in assignment if key in history]
        churn=sum(assignment[key]!=history[key] for key in returning)
        for key in assignment:
            history[key]=assignment[key]
        for key in active:
            cache.pop(key,None)
        writes=0
        for key in sorted(previous_active.difference(active)):
            cache.pop(key,None)
            cache[key]=previous_assignment[key]
            writes+=1
            while len(cache)>9:
                cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+7<=16 and not set(cache).intersection(active)
        previous_active=set(active)
        previous_assignment=assignment
        traces.append({"episode":ep,"assigned":len(assignment),"churn":churn,
            "calls":calls,"writes":writes,"read_attempts":len(prefs),
            "legal_prefs":len(legal),"occupancy":len(cache)})
    summary={"seed":seed,"schedule":schedule,"arm":"retained" if read_cache else "sham",
        "churn":sum(x["churn"] for x in traces),
        "search_calls":sum(x["calls"] for x in traces),
        "cache_writes":sum(x["writes"] for x in traces),
        "read_attempts":sum(x["read_attempts"] for x in traces),
        "legal_prefs":sum(x["legal_prefs"] for x in traces),
        "trace":traces}
    summary["cost"]={str(w):w*summary["churn"]+summary["search_calls"]+summary["cache_writes"]+summary["read_attempts"] for w in WEIGHTS}
    return summary


def condition(schedule):
    rows=[evaluate(seed,schedule,read) for seed in range(56,64)
          for read in (False,True)]
    signatures={str(seed):signature(seed,schedule) for seed in range(56,64)}
    unique=len(set(signatures.values()))==8
    for j in range(0,len(rows),2):
        a,b=rows[j:j+2]
        assert a["cache_writes"]==b["cache_writes"]
        assert [x["occupancy"] for x in a["trace"]]==[x["occupancy"] for x in b["trace"]]
        assert all(x["assigned"]==7 for r in (a,b) for x in r["trace"])
    heldout=[(rows[2*(seed-56)],rows[2*(seed-56)+1]) for seed in range(60,64)]
    net={str(w):[a["cost"][str(w)]-b["cost"][str(w)] for a,b in heldout] for w in WEIGHTS}
    return {"schedule":schedule,"unique_signatures":unique,
        "geometry_signatures":signatures,"heldout_net_savings":net,
        "heldout_aggregate_net_savings":{w:sum(values) for w,values in net.items()},
        "heldout_churn_savings":[a["churn"]-b["churn"] for a,b in heldout],
        "heldout_legal_preferences":sum(b["legal_prefs"] for a,b in heldout),
        "rows":rows}


def run():
    smooth=condition("smooth")
    jump=condition("jump")
    comparison=[a-b for a,b in zip(smooth["heldout_net_savings"]["3"],
                                    jump["heldout_net_savings"]["3"])]
    if not smooth["unique_signatures"] or not jump["unique_signatures"]:
        label="INVALID_NONUNIQUE_GEOMETRY"
    elif all(d>0 for d in comparison) and smooth["heldout_aggregate_net_savings"]["3"]>0:
        label="ENVIRONMENT_MODERATES_UTILITY"
    elif all(c["heldout_aggregate_net_savings"]["3"]<0 for c in (smooth,jump)):
        label="HARM_BOTH"
    else:
        label="MIXED_OR_UNSUPPORTED"
    return {"schema":"yggdrasil.y032-two-displacement-costs.v1",
       "predecessor_head":"606a2d3cb9d67d0400a558744cab13d4b996227e",
       "classification":label,"smooth_minus_jump_per_seed_weight3":comparison,
       "conditions":[smooth,jump],"model_calls":0,
       "claim_limit":"Frozen synthetic matching-search cost conditions, not real economic value"}


if __name__=="__main__":
    outcome=run()
    assert outcome==run()
    print(json.dumps(outcome,sort_keys=True,indent=2))
