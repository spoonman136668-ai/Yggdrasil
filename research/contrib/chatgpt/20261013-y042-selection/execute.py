"""Y042: frozen bounded oldest/newest/spread selection after cache interruptions."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent/"20261013-y041-protected-memory"/"execute.py"
spec=importlib.util.spec_from_file_location("y41_frozen",SOURCE)
assert spec and spec.loader
y41=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y41)
y37=y41.y37
y25=y41.y25

DEVELOPMENT=tuple(range(440,448))
HELDOUT=tuple(range(448,464))
REGIMES=y37.REGIMES
POLICIES=("preserve0","newest3","oldest3","spread3")
RESET_STARTS=(2,4,6)


def retained(cache,policy):
    items=list(cache.items())
    if policy=="preserve0":
        return OrderedDict()
    if len(items)<=3:
        return OrderedDict(items)
    if policy=="newest3":
        return OrderedDict(items[-3:])
    if policy=="oldest3":
        return OrderedDict(items[:3])
    assert policy=="spread3"
    return OrderedDict([items[0],items[len(items)//2],items[-1]])


def execute(seed,regime,policy,read_memory):
    cache=OrderedDict()
    prev_active=set()
    prev_allocation={}
    evaluator_history={}
    episodes=[]
    for ep in range(8):
        if ep in RESET_STARTS:
            cache=retained(cache,policy)
            prev_active=set()
            prev_allocation={}
        active=y37.active_keys(seed,ep)
        adj=y37.graph(seed,ep,regime,active)
        assert y25.hall_cardinality(list(active),adj)==7
        pref={k:cache[k] for k in active
              if read_memory and k in cache and cache[k] in adj[k]}
        assigned,calls=y25.match(list(active),adj,pref)
        assert len(assigned)==7 and len(set(assigned.values()))==7
        ret=[k for k in active if k in evaluator_history]
        churn=sum(assigned[k]!=evaluator_history[k] for k in ret)
        for k in active:evaluator_history[k]=assigned[k]
        for k in active:cache.pop(k,None)
        writes=0
        for k in sorted(prev_active.difference(active)):
            cache.pop(k,None)
            cache[k]=prev_allocation[k]
            writes+=1
            while len(cache)>9:cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+7<=16
        assert not set(cache).intersection(active)
        prev_active=set(active)
        prev_allocation=assigned
        episodes.append({"episode":ep,"churn":churn,"calls":calls,
                         "writes":writes,"cache_keys":list(cache),
                         "preferences":len(pref),"matched":len(assigned)})
    return {"seed":seed,"churn":sum(e["churn"] for e in episodes),
            "calls":sum(e["calls"] for e in episodes),
            "writes":sum(e["writes"] for e in episodes),
            "preferences":sum(e["preferences"] for e in episodes),
            "episodes":episodes}


def evaluate_cell(policy,regime):
    fp=[y37.environment_fingerprint(seed,regime) for seed in DEVELOPMENT+HELDOUT]
    assert len(set(fp))==24
    rows=[]
    for seed in DEVELOPMENT+HELDOUT:
        sham=execute(seed,regime,policy,False)
        full=execute(seed,regime,policy,True)
        assert sham["writes"]==full["writes"]
        for a,b in zip(sham["episodes"],full["episodes"]):
            assert a["writes"]==b["writes"]
            assert a["cache_keys"]==b["cache_keys"]
            assert a["matched"]==b["matched"]==7
        rows.append({"seed":seed,"cohort":"development" if seed in DEVELOPMENT else "heldout",
                     "sham_churn":sham["churn"],"retained_churn":full["churn"],
                     "preferences":full["preferences"],"writes":sham["writes"],
                     "per_episode_saved":[a["churn"]-b["churn"] for a,b in
                                          zip(sham["episodes"],full["episodes"])]})
    sealed=[r for r in rows if r["cohort"]=="heldout"]
    savings=sum(x["sham_churn"]-x["retained_churn"] for x in sealed)
    return {"policy":policy,"regime":regime,"saved_churn":savings,
            "heldout_sham_churn":sum(x["sham_churn"] for x in sealed),
            "heldout_retained_churn":sum(x["retained_churn"] for x in sealed),
            "heldout_preferences":sum(x["preferences"] for x in sealed),
            "rows":rows}


def run():
    cells=[evaluate_cell(p,r) for p in POLICIES for r in REGIMES]
    assert len(cells)==16
    d={(r["policy"],r["regime"]):r["saved_churn"] for r in cells}
    newest_oldest=[d[("newest3",r)]-d[("oldest3",r)] for r in REGIMES]
    spread_newest=[d[("spread3",r)]-d[("newest3",r)] for r in REGIMES]
    if sum(x>0 for x in newest_oldest)>=3 and sum(newest_oldest)>=8:
        label="RECENCY_PRIORITY"
    elif sum(x>0 for x in spread_newest)>=3 and sum(spread_newest)>=8:
        label="POSITIONAL_DIVERSITY"
    else:
        label="MIXED"
    return {"schema":"yggdrasil.y042-memory-selection.v1",
            "parent_head":"53622a4c8a4e553ffde1f798881540397c7c622b",
            "classification":label,
            "recency_minus_oldest_by_regime":newest_oldest,
            "spread_minus_recency_by_regime":spread_newest,
            "development_seeds":DEVELOPMENT,"sealed_heldout_seeds":HELDOUT,
            "cells":cells,"model_calls":0,
            "claim_limit":"Finite observed-memory subset selection; no learned semantic memory"}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
