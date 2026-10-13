"""Y038: fail-closed nonaliased memory capacity frontier (cap 3/6/9)."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

BASE=Path(__file__).resolve().parent.parent/"20261013-y037-diversity"/"execute.py"
spec=importlib.util.spec_from_file_location("y037_frozen",BASE)
assert spec and spec.loader
y37=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y37)
y25=y37.y25

DEV=tuple(range(344,352))
HELDOUT=tuple(range(352,368))
REGIMES=y37.REGIMES
CAPS=(3,6,9)
POLICIES=("matched_sham","full","quorum2")


def evaluate(seed,regime,cap,policy):
    cache=OrderedDict()
    previous_active=set()
    previous_allocation={}
    evaluator_history={}
    episodes=[]
    for episode in range(8):
        active=y37.active_keys(seed,episode)
        graph=y37.graph(seed,episode,regime,active)
        assert y25.hall_cardinality(list(active),graph)==7
        legal={k:cache[k] for k in active if k in cache and cache[k] in graph[k]}
        minpref={"matched_sham":999,"full":1,"quorum2":2}[policy]
        preferred=legal if len(legal)>=minpref else {}
        assigned,calls=y25.match(list(active),graph,preferred)
        assert len(assigned)==7 and len(set(assigned.values()))==7
        returning=[k for k in active if k in evaluator_history]
        churn=sum(assigned[k]!=evaluator_history[k] for k in returning)
        for k in active:evaluator_history[k]=assigned[k]
        for k in active:cache.pop(k,None)
        writes=0
        for k in sorted(previous_active.difference(active)):
            cache.pop(k,None)
            cache[k]=previous_allocation[k]
            writes+=1
            while len(cache)>cap:cache.popitem(last=False)
        assert len(cache)<=cap and len(cache)+7<=16
        assert not set(active).intersection(cache)
        previous_active=set(active)
        previous_allocation=assigned
        episodes.append({"episode":episode,"assigned":len(assigned),
                         "churn":churn,"calls":calls,"writes":writes,
                         "cache_keys":list(cache),
                         "applied_preferences":len(preferred)})
    return {"seed":seed,"churn":sum(x["churn"] for x in episodes),
            "calls":sum(x["calls"] for x in episodes),
            "writes":sum(x["writes"] for x in episodes),
            "preferences":sum(x["applied_preferences"] for x in episodes),
            "episodes":episodes}


def cell(regime,cap):
    fingerprints={seed:y37.environment_fingerprint(seed,regime)
                  for seed in DEV+HELDOUT}
    assert len(set(fingerprints.values()))==24
    rows=[]
    for seed in DEV+HELDOUT:
        arms={p:evaluate(seed,regime,cap,p) for p in POLICIES}
        sham=arms["matched_sham"]
        for result in arms.values():
            assert result["writes"]==sham["writes"]
            for first,other in zip(sham["episodes"],result["episodes"]):
                assert first["writes"]==other["writes"]
                assert first["cache_keys"]==other["cache_keys"]
                assert first["assigned"]==other["assigned"]==7
        rows.append({"seed":seed,"cohort":"development" if seed in DEV else "heldout",
                     "fingerprint":fingerprints[seed],
                     "churn":{p:arms[p]["churn"] for p in POLICIES},
                     "search_calls":{p:arms[p]["calls"] for p in POLICIES},
                     "used_preferences":{p:arms[p]["preferences"] for p in POLICIES},
                     "cache_writes":sham["writes"]})
    heldout=[r for r in rows if r["cohort"]=="heldout"]
    total={p:sum(r["churn"][p] for r in heldout) for p in POLICIES}
    return {"regime":regime,"capacity":cap,"unique_environment_count":24,
            "heldout_churn":total,
            "savings":{p:total["matched_sham"]-total[p] for p in POLICIES[1:]},
            "rows":rows}


def run():
    cells=[cell(regime,cap) for cap in CAPS for regime in REGIMES]
    assert len(cells)==12
    by={(c["capacity"],c["regime"]):c for c in cells}
    slow=[by[(cap,"drift1")]["savings"]["full"] for cap in CAPS]
    beneficial=sum(c["savings"]["full"]>0 for c in cells)
    all_at_cap9=all(by[(9,regime)]["savings"]["full"]>0 for regime in REGIMES)
    if slow[0]<slow[1]<slow[2] and all_at_cap9:
        label="MONOTONIC_RETENTION"
    elif beneficial>=6:
        label="MIXED"
    else:
        label="NEGATIVE"
    return {"schema":"yggdrasil.y038-nonaliased-capacity-frontier.v1",
            "parent_head":"14398ce9fcf1104d04557ffa8cfc232161133072",
            "classification":label,"slow_drift_saved_by_cap":slow,
            "beneficial_cells":beneficial,
            "development_seeds":DEV,"heldout_seeds":HELDOUT,
            "cells":cells,"model_calls":0,
            "claim_limit":"Nonaliased synthetic episode memory capacity only"}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
