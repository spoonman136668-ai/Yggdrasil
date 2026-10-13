"""Y029: radius-one selective trust of bounded cache under alternating drift."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PRIOR_SOURCE=Path(__file__).resolve().parent.parent/"20261012-y028-alternating-drift"/"execute.py"
_spec=importlib.util.spec_from_file_location("y028_frozen",PRIOR_SOURCE)
assert _spec and _spec.loader
y28=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(y28)
y25=y28.y25


def inner_adjacency(seed, episode, active):
    displacement=y28.DISPLACEMENTS[episode]
    homes={key:(7*key+seed+displacement)%16 for key in active}
    for key in active[1:4]:
        homes[key]=homes[active[0]]
    return {
        key:{(home+d)%16 for d in range(-1,2)}
        for key,home in homes.items()
    }


def evaluate(seed, inner_only):
    cache=OrderedDict()
    prev_active=set()
    prev_assignments={}
    evaluator_history={}
    episodes=[]
    for episode in range(8):
        active=y25.active_keys(seed,episode)
        full=y28.alternating_neighbors(seed,episode,active)
        inner=inner_adjacency(seed,episode,active)
        assert all(inner[k].issubset(full[k]) for k in active)
        assert y25.hall_cardinality(active,full)==7
        eligible=inner if inner_only else full
        preferred={k:cache[k] for k in active if k in cache and cache[k] in eligible[k]}
        assignments,calls=y25.match(active,full,preferred)
        returning=[k for k in active if k in evaluator_history]
        churn=sum(assignments[k]!=evaluator_history[k] for k in returning)
        for k in active:
            evaluator_history[k]=assignments[k]
        for k in active:
            cache.pop(k,None)
        writes=0
        for k in sorted(prev_active.difference(active)):
            cache.pop(k,None)
            cache[k]=prev_assignments[k]
            writes+=1
            while len(cache)>9:
                cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+7<=16
        assert not set(cache).intersection(active)
        prev_active=set(active)
        prev_assignments=assignments
        episodes.append({
            "episode":episode,"churn":churn,"assigned":len(assignments),
            "search_calls":calls,"cache_writes":writes,"cache_entries":len(cache),
            "eligible_preferences":len(preferred)
        })
    return {
        "seed":seed,"cohort":"development" if seed<36 else "heldout",
        "arm":"inner_radius1" if inner_only else "full_radius2",
        "churn":sum(r["churn"] for r in episodes),
        "search_calls":sum(r["search_calls"] for r in episodes),
        "cache_writes":sum(r["cache_writes"] for r in episodes),
        "eligible_preferences":sum(r["eligible_preferences"] for r in episodes),
        "episodes":episodes
    }


def run():
    rows=[evaluate(seed,inner) for seed in range(32,40) for inner in (False,True)]
    for i in range(0,len(rows),2):
        a,b=rows[i:i+2]
        assert a["cache_writes"]==b["cache_writes"]
        assert [r["cache_entries"] for r in a["episodes"]]==[
            r["cache_entries"] for r in b["episodes"]]
        assert all(r["assigned"]==7 for c in (a,b) for r in c["episodes"])
    heldout=[(rows[2*(s-32)],rows[2*(s-32)+1]) for s in range(36,40)]
    savings=[full["churn"]-inner["churn"] for full,inner in heldout]
    if sum(savings)>0 and all(value>=0 for value in savings):
        classification="INNER_TRUST_BENEFIT"
    elif any(value>0 for value in savings) and any(value<0 for value in savings):
        classification="MIXED"
    else:
        classification="NO_GAIN"
    return {
        "schema":"yggdrasil.y029-inner-cache-trust.v1",
        "predecessor_head":"553870f7491390ff8884a824832691a60969f985",
        "classification":classification,
        "heldout_savings":savings,
        "heldout_full_churn":sum(a["churn"] for a,b in heldout),
        "heldout_inner_churn":sum(b["churn"] for a,b in heldout),
        "heldout_full_eligible_prefs":sum(a["eligible_preferences"] for a,b in heldout),
        "heldout_inner_eligible_prefs":sum(b["eligible_preferences"] for a,b in heldout),
        "rows":rows,"model_calls":0,
        "claim_limit":"Synthetic radius-based memory trust, not learned policy"
    }


if __name__=="__main__":
    out=run()
    assert out==run()
    print(json.dumps(out,sort_keys=True,indent=2))
