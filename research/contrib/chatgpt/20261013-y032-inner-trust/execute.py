"""Y032: radius-one cached-preference gate under independent keyed drift."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PREVIOUS = Path(__file__).resolve().parent.parent / "20261013-y031-keyed-drift" / "execute.py"
_spec = importlib.util.spec_from_file_location("y031_frozen", PREVIOUS)
assert _spec and _spec.loader
y31 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(y31)


def inner_neighborhood(neighbors):
    inner = {}
    for key, cells in neighbors.items():
        centers = [
            home for home in range(16)
            if {(home+d)%16 for d in range(-2,3)} == cells
        ]
        assert len(centers) == 1
        center = centers[0]
        inner[key] = {(center+d)%16 for d in range(-1,2)}
        assert inner[key].issubset(cells)
        assert len(inner[key]) == 3
    return inner


def evaluate(seed, restrict_inner):
    cache = OrderedDict()
    previous_active = set()
    previous_assignment = {}
    evaluator_history = {}
    rows = []
    for ep in range(8):
        active, neighbor = y31.geometry(seed, ep)
        inner = inner_neighborhood(neighbor)
        preference_sets = inner if restrict_inner else neighbor
        preference = {
            key: cache[key] for key in active
            if key in cache and cache[key] in preference_sets[key]
        }
        match, calls = y31.y030.match(active, neighbor, preference)
        assert len(match)==7
        returning = [key for key in active if key in evaluator_history]
        churn = sum(match[key] != evaluator_history[key] for key in returning)
        for key in active:
            evaluator_history[key]=match[key]
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
        previous_assignment=match
        rows.append({
            "episode":ep,"matched":len(match),"returning":len(returning),
            "churn":churn,"calls":calls,"cache_writes":writes,
            "cache_entries":len(cache),"legal_preferences":len(preference),
        })
    return {
        "seed":seed,
        "cohort":"development" if seed<60 else "heldout",
        "arm":"inner_preference" if restrict_inner else "full_neighborhood",
        "total_churn":sum(x["churn"] for x in rows),
        "total_calls":sum(x["calls"] for x in rows),
        "total_writes":sum(x["cache_writes"] for x in rows),
        "preference_count":sum(x["legal_preferences"] for x in rows),
        "episodes":rows,
    }


def run():
    signatures={str(seed):y31.population_signature(seed) for seed in range(56,64)}
    unique=len(set(signatures.values()))==8
    deficiency=[]
    for seed in range(56,64):
        for ep in range(8):
            active,neighbors=y31.geometry(seed,ep)
            hall=y31.y030.hall_cardinality(active,neighbors)
            if hall<7:
                deficiency.append({"seed":seed,"episode":ep,"hall":hall})
    if not unique or deficiency:
        return {
            "schema":"yggdrasil.y032-keyed-inner-preference.v1",
            "predecessor_head":"244604db6992e598b1c9057083d279d5a8869de4",
            "classification":"NONUNIQUE_GEOMETRY" if not unique else "GEOMETRY_DEFICIENCY",
            "signatures":signatures,"hall_deficiency":deficiency,
            "rows":[],"model_calls":0,
            "claim_limit":"Synthetic frozen geometry validity; no retry of invalid science."
        }
    rows=[evaluate(seed,inner) for seed in range(56,64)
          for inner in (False,True)]
    for i in range(0,len(rows),2):
        a,b=rows[i:i+2]
        assert a["total_writes"]==b["total_writes"]
        assert [e["cache_entries"] for e in a["episodes"]]==[
            e["cache_entries"] for e in b["episodes"]]
        assert all(e["matched"]==7 for policy in (a,b) for e in policy["episodes"])
    heldout=[(rows[2*(s-56)],rows[2*(s-56)+1]) for s in range(60,64)]
    saved=[a["total_churn"]-b["total_churn"] for a,b in heldout]
    if sum(saved)>0 and all(x>=0 for x in saved):
        outcome="INNER_TRUST_TRANSFER"
    elif any(x>0 for x in saved) and any(x<0 for x in saved):
        outcome="MIXED"
    elif sum(saved)<0:
        outcome="FULL_PREFERENCE_WINS"
    else:
        outcome="NO_GAIN"
    return {
        "schema":"yggdrasil.y032-keyed-inner-preference.v1",
        "predecessor_head":"244604db6992e598b1c9057083d279d5a8869de4",
        "classification":outcome,
        "signatures":signatures,"unique_signatures":unique,
        "heldout_savings":saved,
        "heldout_full_churn":sum(a["total_churn"] for a,b in heldout),
        "heldout_inner_churn":sum(b["total_churn"] for a,b in heldout),
        "heldout_full_calls":sum(a["total_calls"] for a,b in heldout),
        "heldout_inner_calls":sum(b["total_calls"] for a,b in heldout),
        "rows":rows,"model_calls":0,
        "claim_limit":"Bounded synthetic observed-assignment preference test only, no semantic learning."
    }


if __name__=="__main__":
    result=run()
    assert result==run()
    print(json.dumps(result,sort_keys=True,indent=2))
