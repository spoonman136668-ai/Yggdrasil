"""Y036: long passive hiatus, new 12-tick horizon, no extra memory."""
import importlib.util
import hashlib
import json
from collections import OrderedDict
from pathlib import Path

OLD=Path(__file__).resolve().parent.parent/"20261013-y035-hibernation"/"execute.py"
spec=importlib.util.spec_from_file_location("y035_frozen",OLD)
assert spec and spec.loader
previous=importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
y30=previous.y30

OBSERVED={"five":(0,1,2,8,9,10,11),"seven":(0,1,2,10,11)}
RESUME={"five":8,"seven":10}
WEIGHTS=(3,10)


def signature(seed):
    sequence=[]
    for episode in range(12):
        keys,adj=y30.geometry(seed,episode)
        sequence.append([keys,[[k,sorted(adj[k])] for k in keys]])
    return hashlib.sha256(json.dumps(sequence,separators=(",",":")).encode()).hexdigest()


def simulate(seed,gap,retain):
    cache=OrderedDict()
    prior_active=set()
    prior_assignment={}
    evaluator_history={}
    clears=0
    trace=[]
    for ep in OBSERVED[gap]:
        if ep==RESUME[gap] and not retain:
            clears+=len(cache)+len(prior_assignment)
            cache.clear()
            prior_active=set()
            prior_assignment={}
        active,adj=y30.geometry(seed,ep)
        assert y30.hall_cardinality(active,adj)==7
        prefs={k:cache[k] for k in active if k in cache}
        legal={k:cell for k,cell in prefs.items() if cell in adj[k]}
        assigned,calls=y30.match(active,adj,prefs)
        assert len(assigned)==7
        returning=[k for k in assigned if k in evaluator_history]
        churn=sum(assigned[k]!=evaluator_history[k] for k in returning)
        evaluator_history.update(assigned)
        for k in active:cache.pop(k,None)
        writes=0
        for k in sorted(prior_active.difference(active)):
            cache.pop(k,None)
            cache[k]=prior_assignment[k]
            writes+=1
            while len(cache)>9:
                cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+7<=16 and not set(cache).intersection(active)
        prior_active=set(active)
        prior_assignment=assigned
        trace.append({"episode":ep,"matched":7,"post_gap":ep>=RESUME[gap],
            "first_reactivation":ep==RESUME[gap],"churn":churn,
            "search_calls":calls,"writes":writes,"reads":len(prefs),
            "legal_preferences":len(legal),"occupancy":len(cache)})
    result={"seed":seed,"gap":gap,"arm":"retain" if retain else "erase",
        "churn":sum(t["churn"] for t in trace),
        "post_gap_churn":sum(t["churn"] for t in trace if t["post_gap"]),
        "first_reactivation_churn":sum(t["churn"] for t in trace if t["first_reactivation"]),
        "search_calls":sum(t["search_calls"] for t in trace),
        "writes":sum(t["writes"] for t in trace),
        "reads":sum(t["reads"] for t in trace),
        "clear_ops":clears,
        "legal_preferences":sum(t["legal_preferences"] for t in trace),
        "trace":trace}
    result["cost"]={str(w):w*result["churn"]+result["search_calls"]+
                    result["writes"]+result["reads"]+result["clear_ops"] for w in WEIGHTS}
    return result


def condition(gap):
    rows=[simulate(seed,gap,retain) for seed in range(88,96)
          for retain in (False,True)]
    heldout=[(rows[2*(seed-88)],rows[2*(seed-88)+1]) for seed in range(92,96)]
    churn_savings=[a["churn"]-b["churn"] for a,b in heldout]
    net={str(w):[a["cost"][str(w)]-b["cost"][str(w)] for a,b in heldout]
         for w in WEIGHTS}
    return {"gap":gap,"observed":OBSERVED[gap],"resume":RESUME[gap],
        "churn_savings":churn_savings,"total_churn_savings":sum(churn_savings),
        "first_reactivation_churn_savings":[a["first_reactivation_churn"]-b["first_reactivation_churn"] for a,b in heldout],
        "net_savings_by_weight":net,
        "net_aggregate":{w:sum(items) for w,items in net.items()},
        "retained_legal_preferences":sum(b["legal_preferences"] for a,b in heldout),
        "rows":rows}


def run():
    signatures={str(s):signature(s) for s in range(88,96)}
    unique=len(set(signatures.values()))==8
    conditions=[condition(gap) for gap in ("five","seven")]
    x,y=(r["total_churn_savings"] for r in conditions)
    if not unique:label="INVALID_NONUNIQUE_GEOMETRY"
    elif x>0 and y<=0:label="SHORT_ONLY_RETENTION"
    elif x>y>0:label="LONG_HORIZON_DECAY"
    else:label="NO_DECAY_OR_NEGATIVE"
    return {"schema":"yggdrasil.y036-long-hibernation.v1",
        "predecessor_head":"589549f49564bea860865893d697fb4de55f4540",
        "classification":label,"horizon_ticks":12,
        "unique_geometry_signatures":unique,"geometry_signatures":signatures,
        "conditions":conditions,"model_calls":0,
        "claim_limit":"Synthetic longer hiatus under unchanged 7+9 storage, not biological memory"}


if __name__=="__main__":
    result=run()
    assert result==run()
    print(json.dumps(result,sort_keys=True,indent=2))
