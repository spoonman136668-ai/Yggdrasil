"""Y041: preregistered bounded protected cache through repeated interruptions."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent/"20261013-y040-reset-frontier"/"execute.py"
spec=importlib.util.spec_from_file_location("y40_frozen",SOURCE)
assert spec and spec.loader
y40=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y40)
y37=y40.y37
y25=y40.y25

DEVELOPMENT=tuple(range(416,424))
HELDOUT=tuple(range(424,440))
REGIMES=y37.REGIMES
PRESERVATION=(0,3,6,9)
RESET_STARTS=(2,4,6)


def execute(seed,regime,retained_count,read_memory):
    cache=OrderedDict()
    previous_active=set()
    previous_assignment={}
    evaluator_history={}
    episodes=[]
    for episode in range(8):
        if episode in RESET_STARTS:
            if retained_count==0:
                cache.clear()
            else:
                cache=OrderedDict(list(cache.items())[-retained_count:])
            previous_active=set()
            previous_assignment={}
        active=y37.active_keys(seed,episode)
        adj=y37.graph(seed,episode,regime,active)
        assert y25.hall_cardinality(list(active),adj)==7
        pref={k:cache[k] for k in active
              if read_memory and k in cache and cache[k] in adj[k]}
        assignment,calls=y25.match(list(active),adj,pref)
        assert len(assignment)==7 and len(set(assignment.values()))==7
        returning=[k for k in active if k in evaluator_history]
        churn=sum(assignment[k]!=evaluator_history[k] for k in returning)
        for key in active:evaluator_history[key]=assignment[key]
        for key in active:cache.pop(key,None)
        writes=0
        for key in sorted(previous_active.difference(active)):
            cache.pop(key,None)
            cache[key]=previous_assignment[key]
            writes+=1
            while len(cache)>9:cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+7<=16
        assert not set(cache).intersection(active)
        previous_active=set(active)
        previous_assignment=assignment
        episodes.append({"episode":episode,"churn":churn,"writes":writes,
                         "calls":calls,"cache_keys":list(cache),
                         "prefs":len(pref),"matched":len(assignment)})
    return {"churn":sum(x["churn"] for x in episodes),
            "writes":sum(x["writes"] for x in episodes),
            "calls":sum(x["calls"] for x in episodes),
            "prefs":sum(x["prefs"] for x in episodes),"episodes":episodes}


def evaluate_cell(retained_count,regime):
    identities=[y37.environment_fingerprint(seed,regime) for seed in DEVELOPMENT+HELDOUT]
    assert len(set(identities))==24
    rows=[]
    for seed in DEVELOPMENT+HELDOUT:
        sham=execute(seed,regime,retained_count,False)
        remembered=execute(seed,regime,retained_count,True)
        assert sham["writes"]==remembered["writes"]
        for a,b in zip(sham["episodes"],remembered["episodes"]):
            assert a["writes"]==b["writes"]
            assert a["cache_keys"]==b["cache_keys"]
            assert a["matched"]==b["matched"]==7
        rows.append({"seed":seed,"cohort":"development" if seed in DEVELOPMENT else "heldout",
                     "sham_churn":sham["churn"],"memory_churn":remembered["churn"],
                     "preferences":remembered["prefs"],"write_count":sham["writes"],
                     "episode_savings":[a["churn"]-b["churn"] for a,b in
                                        zip(sham["episodes"],remembered["episodes"])]})
    heldout=[x for x in rows if x["cohort"]=="heldout"]
    saving=sum(x["sham_churn"]-x["memory_churn"] for x in heldout)
    return {"retained_across_reset":retained_count,"regime":regime,"saved_churn":saving,
            "heldout_sham_churn":sum(x["sham_churn"] for x in heldout),
            "heldout_memory_churn":sum(x["memory_churn"] for x in heldout),
            "heldout_legal_preferences":sum(x["preferences"] for x in heldout),
            "per_episode_savings":[sum(x["episode_savings"][i] for x in heldout)
                                   for i in range(8)],"seed_results":rows}


def run():
    cells=[evaluate_cell(n,regime) for n in PRESERVATION for regime in REGIMES]
    by={(c["retained_across_reset"],c["regime"]):c["saved_churn"] for c in cells}
    count3=sum(by[(3,r)]>by[(0,r)] for r in REGIMES)
    count6=sum(by[(6,r)]>by[(3,r)] for r in REGIMES)
    if count3>=3 and count6>=2:
        label="PROTECTED_MEMORY_BENEFIT"
    elif any(by[(n,r)]>by[(0,r)] for n in (3,6) for r in REGIMES):
        label="PARTIAL"
    else:
        label="NO_BENEFIT"
    return {"schema":"yggdrasil.y041-protected-memory-interruption.v1",
            "parent_head":"b332db0668f6d93854bf972f2a7b594d52ad31e7",
            "classification":label,"preserve3_improved_regimes":count3,
            "preserve6_over_3_improved_regimes":count6,
            "reset_episode_starts":RESET_STARTS,
            "development_seeds":DEVELOPMENT,"sealed_heldout_seeds":HELDOUT,
            "cells":cells,"model_calls":0,
            "claim_limit":"Finite synthetic protected assignment memory only"}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
