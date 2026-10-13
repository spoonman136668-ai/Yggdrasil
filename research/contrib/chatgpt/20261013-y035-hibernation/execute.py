"""Y035: observed assignment retention versus state erasure across passive hiatus."""
import importlib.util
import hashlib
import json
from collections import OrderedDict
from pathlib import Path

PRIOR=Path(__file__).resolve().parent.parent/"20261013-y034-capacity"/"execute.py"
spec=importlib.util.spec_from_file_location("y034_frozen",PRIOR)
assert spec and spec.loader
previous=importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
y30=previous.y30

GAPS={"short":(0,1,2,4,5,6,7),"long":(0,1,2,6,7)}
RESUMES={"short":4,"long":6}
WEIGHTS=(3,10)


def geometry_signature(seed):
    signature=[]
    for ep in range(8):
        active,neighbors=y30.geometry(seed,ep)
        signature.append([active,[[k,sorted(neighbors[k])] for k in active]])
    return hashlib.sha256(json.dumps(signature,separators=(",",":")).encode()).hexdigest()


def evaluate(seed,gap,retain):
    assert gap in GAPS
    cache=OrderedDict()
    previous_active=set()
    previous_assignment={}
    evaluator_history={}
    trace=[]
    cleared=0
    for ep in GAPS[gap]:
        if ep==RESUMES[gap] and not retain:
            # This is the sole intervention: erase all policy-side assignment state.
            cleared+=len(cache)+len(previous_assignment)
            cache.clear()
            previous_active=set()
            previous_assignment={}
        active,neighbors=y30.geometry(seed,ep)
        assert y30.hall_cardinality(active,neighbors)==7
        preferred={k:cache[k] for k in active if k in cache}
        legal={k:v for k,v in preferred.items() if v in neighbors[k]}
        assigned,calls=y30.match(active,neighbors,preferred)
        assert len(assigned)==7
        returning=[k for k in assigned if k in evaluator_history]
        churn=sum(assigned[k]!=evaluator_history[k] for k in returning)
        evaluator_history.update(assigned)
        for key in active:
            cache.pop(key,None)
        writes=0
        for key in sorted(previous_active.difference(active)):
            cache.pop(key,None)
            cache[key]=previous_assignment[key]
            writes+=1
            while len(cache)>9:
                cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+7<=16
        assert not set(active).intersection(cache)
        previous_active=set(active)
        previous_assignment=assigned
        trace.append({
            "episode":ep,"post_reactivation":ep>=RESUMES[gap],
            "first_reactivation_episode":ep==RESUMES[gap],
            "matches":len(assigned),"churn":churn,"calls":calls,
            "cache_writes":writes,"cache_read_attempts":len(preferred),
            "legal_preferences":len(legal),"cache_occupancy":len(cache)})
    summary={
        "seed":seed,"cohort":"development" if seed<84 else "heldout",
        "gap":gap,"arm":"retain" if retain else "erase",
        "churn":sum(row["churn"] for row in trace),
        "reactivation_churn":sum(row["churn"] for row in trace if row["post_reactivation"]),
        "first_reactivation_churn":sum(row["churn"] for row in trace if row["first_reactivation_episode"]),
        "search_calls":sum(row["calls"] for row in trace),
        "cache_writes":sum(row["cache_writes"] for row in trace),
        "cache_read_attempts":sum(row["cache_read_attempts"] for row in trace),
        "cache_clear_ops":cleared,
        "legal_preferences":sum(row["legal_preferences"] for row in trace),
        "max_cache_occupancy":max(row["cache_occupancy"] for row in trace),
        "trace":trace
    }
    summary["cost"]={str(w):
        w*summary["churn"]+summary["search_calls"]+summary["cache_writes"]+
        summary["cache_read_attempts"]+summary["cache_clear_ops"]
        for w in WEIGHTS}
    return summary


def compare_gap(gap):
    rows=[evaluate(seed,gap,keep)
          for seed in range(80,88) for keep in (False,True)]
    held=[(rows[2*(seed-80)],rows[2*(seed-80)+1]) for seed in range(84,88)]
    savings=[erase["churn"]-keep["churn"] for erase,keep in held]
    net={str(w):[a["cost"][str(w)]-b["cost"][str(w)] for a,b in held] for w in WEIGHTS}
    return {
        "gap":gap,"observed_episodes":GAPS[gap],"resume_episode":RESUMES[gap],
        "heldout_churn_savings":savings,
        "heldout_net_cost_savings_by_weight":net,
        "heldout_aggregate_net_cost_savings":{w:sum(v) for w,v in net.items()},
        "heldout_first_reactivation_churn_savings":[
            a["first_reactivation_churn"]-b["first_reactivation_churn"] for a,b in held],
        "heldout_legal_preferences":sum(b["legal_preferences"] for a,b in held),
        "rows":rows
    }


def run():
    signatures={str(seed):geometry_signature(seed) for seed in range(80,88)}
    unique=len(set(signatures.values()))==8
    results=[compare_gap(gap) for gap in ("short","long")]
    if not unique:
        label="INVALID_NONUNIQUE_GEOMETRY"
    elif all(all(s>0 for s in r["heldout_churn_savings"]) and
             r["heldout_aggregate_net_cost_savings"]["3"]>0 for r in results):
        label="RETENTION_SURVIVES_INTERRUPTION"
    elif any(sum(r["heldout_churn_savings"])>0 for r in results) and any(
            sum(r["heldout_churn_savings"])<=0 for r in results):
        label="MIXED"
    else:
        label="NO_UNIVERSAL_RETENTION_GAIN"
    return {"schema":"yggdrasil.y035-hibernation-reactivation.v1",
        "predecessor_head":"bde98bd5406fd9b4ff3b37df039f501f71019f7b",
        "classification":label,"unique_geometry_signatures":unique,
        "geometry_signatures":signatures,"conditions":results,"model_calls":0,
        "claim_limit":"Synthetic assignment-state recovery after passive hiatus; not biological hibernation"}


if __name__=="__main__":
    outcome=run()
    assert outcome==run()
    print(json.dumps(outcome,sort_keys=True,indent=2))
