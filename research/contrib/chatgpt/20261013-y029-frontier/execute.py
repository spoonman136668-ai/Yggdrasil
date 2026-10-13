"""Y029: first-use preregistered drift x cache-budget factorial scientific battery."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path


OLD=Path(__file__).resolve().parent.parent/"20261012-y025-matched-memory"/"execute.py"
spec=importlib.util.spec_from_file_location("y025_frozen",OLD)
assert spec and spec.loader
y25=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y25)

CAPACITIES=(3,6,9)
REGIMES=("drift1","drift3","drift5","alternating")
DISPLACEMENTS=(0,1,6,7,12,13,18,19)
DEVELOPMENT_SEEDS=tuple(range(32,40))
HELDOUT_SEEDS=tuple(range(40,56))


def neighbors(seed,episode,active,regime):
    if regime=="alternating":
        position=DISPLACEMENTS[episode]
    else:
        assert regime in ("drift1","drift3","drift5")
        position=int(regime[-1])*episode
    homes={key:(7*key+seed+position)%16 for key in active}
    for key in active[1:4]:
        homes[key]=homes[active[0]]
    return {key:{(home+d)%16 for d in range(-2,3)}
            for key,home in homes.items()}


def evaluate(seed,capacity,regime,use_cache):
    cache=OrderedDict()
    previous_active=set()
    previous_assignment={}
    evaluator_history={}
    episodes=[]
    for episode in range(8):
        active=y25.active_keys(seed,episode)
        adjacency=neighbors(seed,episode,active,regime)
        hall=y25.hall_cardinality(active,adjacency)
        assert hall==7
        legal_read={}
        preference={}
        if use_cache:
            preference={key:cache[key] for key in active if key in cache}
            legal_read={key:cell for key,cell in preference.items() if cell in adjacency[key]}
        assigned,calls=y25.match(active,adjacency,preference)
        assert len(assigned)==hall==7
        assert len(set(assigned.values()))==7
        returning=[key for key in active if key in evaluator_history]
        churn=sum(assigned[key]!=evaluator_history[key] for key in returning)
        for key in active:
            evaluator_history[key]=assigned[key]
        for key in active:
            cache.pop(key,None)
        writes=0
        for key in sorted(previous_active.difference(active)):
            cache.pop(key,None)
            cache[key]=previous_assignment[key]
            writes+=1
            while len(cache)>capacity:
                cache.popitem(last=False)
        assert len(cache)<=capacity and len(cache)+len(active)<=16
        assert not set(active).intersection(cache)
        previous_active=set(active)
        previous_assignment=assigned
        episodes.append({"episode":episode,"matched":len(assigned),
                         "returning":len(returning),"churn":churn,
                         "calls":calls,"cache_writes":writes,
                         "cached_keys":list(cache),
                         "legal_read_preferences":len(legal_read)})
    return {"seed":seed,"churn":sum(x["churn"] for x in episodes),
            "search_calls":sum(x["calls"] for x in episodes),
            "cache_writes":sum(x["cache_writes"] for x in episodes),
            "legal_preferences":sum(x["legal_read_preferences"] for x in episodes),
            "episodes":episodes}


def evaluate_cell(capacity,regime):
    seed_rows=[]
    for seed in DEVELOPMENT_SEEDS+HELDOUT_SEEDS:
        sham=evaluate(seed,capacity,regime,False)
        actual=evaluate(seed,capacity,regime,True)
        assert sham["cache_writes"]==actual["cache_writes"]
        for s,a in zip(sham["episodes"],actual["episodes"]):
            assert s["cache_writes"]==a["cache_writes"]
            assert s["cached_keys"]==a["cached_keys"]
            assert s["matched"]==a["matched"]==7
        seed_rows.append({"seed":seed,"cohort":"development" if seed in DEVELOPMENT_SEEDS else "heldout",
                          "saved_churn":sham["churn"]-actual["churn"],
                          "sham_churn":sham["churn"],"read_churn":actual["churn"],
                          "sham_search_calls":sham["search_calls"],
                          "read_search_calls":actual["search_calls"],
                          "legal_cached_preferences":actual["legal_preferences"],
                          "paired_write_count":actual["cache_writes"],
                          "sham_episode_churn":[e["churn"] for e in sham["episodes"]],
                          "read_episode_churn":[e["churn"] for e in actual["episodes"]]})
    heldout=[x for x in seed_rows if x["cohort"]=="heldout"]
    sum_savings=sum(x["saved_churn"] for x in heldout)
    return {"capacity":capacity,"regime":regime,
            "heldout_total_saved_churn":sum_savings,
            "heldout_sham_churn":sum(x["sham_churn"] for x in heldout),
            "heldout_read_churn":sum(x["read_churn"] for x in heldout),
            "heldout_legal_cached_preferences":sum(x["legal_cached_preferences"] for x in heldout),
            "classification":"BENEFIT" if sum_savings>0 else "HARM" if sum_savings<0 else "NEUTRAL",
            "seed_results":seed_rows}


def run():
    results=[evaluate_cell(capacity,regime)
             for capacity in CAPACITIES for regime in REGIMES]
    assert len(results)==12
    positives=sum(r["heldout_total_saved_churn"]>0 for r in results)
    negatives=sum(r["heldout_total_saved_churn"]<0 for r in results)
    classification=("COVERAGE_LIMITED" if positives<6 else
                    "ROBUST_RETENTION" if positives>=10 and negatives==0
                    else "MIXED_FRONTIER")
    return {
        "schema":"yggdrasil.y029-retention-frontier.v1",
        "parent_head":"553870f7491390ff8884a824832691a60969f985",
        "classification":classification,
        "positive_cells":positives,"negative_cells":negatives,
        "development_seeds":DEVELOPMENT_SEEDS,
        "heldout_seeds":HELDOUT_SEEDS,
        "cells":results,"model_calls":0,
        "claim_limit":"Finite synthetic matching memory frontier, no semantic learning or development"
    }


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
