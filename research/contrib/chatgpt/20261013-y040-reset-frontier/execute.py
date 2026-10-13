"""Y040: first-use cache recovery frontier over resets x budget x geometry."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent/"20261013-y039-interrupt"/"execute.py"
spec=importlib.util.spec_from_file_location("y039_frozen",SOURCE)
assert spec and spec.loader
y39=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y39)
y37=y39.y37
y25=y39.y25

DEV=tuple(range(392,400))
HELDOUT=tuple(range(400,416))
CAPS=(3,6,9)
SCHEDULES={"none":(),"single":(3,),"double":(3,6),"triple":(2,4,6)}
REGIMES=y37.REGIMES


def evaluate(seed,regime,cap,resets,use_memory):
    cache=OrderedDict()
    prev_active=set()
    prev_assignment={}
    evaluator_history={}
    rows=[]
    for episode in range(8):
        if episode in resets:
            cache.clear()
            prev_active=set()
            prev_assignment={}
        active=y37.active_keys(seed,episode)
        neighbor=y37.graph(seed,episode,regime,active)
        assert y25.hall_cardinality(list(active),neighbor)==7
        preferences={k:cache[k] for k in active
                     if use_memory and k in cache and cache[k] in neighbor[k]}
        assigned,calls=y25.match(list(active),neighbor,preferences)
        assert len(assigned)==7 and len(set(assigned.values()))==7
        returning=[k for k in active if k in evaluator_history]
        churn=sum(assigned[k]!=evaluator_history[k] for k in returning)
        for k in active:evaluator_history[k]=assigned[k]
        for k in active:cache.pop(k,None)
        writes=0
        for k in sorted(prev_active.difference(active)):
            cache.pop(k,None)
            cache[k]=prev_assignment[k]
            writes+=1
            while len(cache)>cap:cache.popitem(last=False)
        assert len(cache)<=cap and len(cache)+7<=16
        assert not set(cache).intersection(active)
        prev_active=set(active)
        prev_assignment=assigned
        rows.append({"episode":episode,"churn":churn,"calls":calls,
                     "writes":writes,"cached_keys":list(cache),
                     "preferences":len(preferences),"matched":len(assigned)})
    return {"seed":seed,"churn":sum(r["churn"] for r in rows),
            "calls":sum(r["calls"] for r in rows),
            "writes":sum(r["writes"] for r in rows),
            "prefs":sum(r["preferences"] for r in rows),"episodes":rows}


def cell(cap,reset_name,regime):
    resets=SCHEDULES[reset_name]
    fingerprints={s:y37.environment_fingerprint(s,regime) for s in DEV+HELDOUT}
    assert len(set(fingerprints.values()))==24
    result=[]
    for seed in DEV+HELDOUT:
        a=evaluate(seed,regime,cap,resets,False)
        b=evaluate(seed,regime,cap,resets,True)
        assert a["writes"]==b["writes"]
        for ra,rb in zip(a["episodes"],b["episodes"]):
            assert ra["writes"]==rb["writes"]
            assert ra["cached_keys"]==rb["cached_keys"]
            assert ra["matched"]==rb["matched"]==7
        result.append({"seed":seed,"cohort":"development" if seed in DEV else "heldout",
                       "sha256_environment":fingerprints[seed],
                       "sham_churn":a["churn"],"memory_churn":b["churn"],
                       "matched_writes":a["writes"],
                       "sham_calls":a["calls"],"memory_calls":b["calls"],
                       "memory_preferences":b["prefs"],
                       "episode_savings":[ra["churn"]-rb["churn"]
                                          for ra,rb in zip(a["episodes"],b["episodes"])]})
    heldout=[r for r in result if r["cohort"]=="heldout"]
    saved=sum(x["sham_churn"]-x["memory_churn"] for x in heldout)
    return {"capacity":cap,"reset_schedule":reset_name,"regime":regime,
            "saved_churn":saved,"heldout_sham_churn":sum(x["sham_churn"] for x in heldout),
            "heldout_memory_churn":sum(x["memory_churn"] for x in heldout),
            "heldout_preferences":sum(x["memory_preferences"] for x in heldout),
            "per_episode_savings":[sum(r["episode_savings"][i] for r in heldout)
                                   for i in range(8)],
            "seed_results":result}

def run():
    cells=[cell(cap,schedule,regime)
           for cap in CAPS for schedule in SCHEDULES for regime in REGIMES]
    assert len(cells)==48
    refs={x["regime"]:x for x in cells if x["capacity"]==9 and x["reset_schedule"]=="none"}
    double={x["regime"]:x for x in cells if x["capacity"]==9 and x["reset_schedule"]=="double"}
    positives=sum(double[r]["saved_churn"]>0 for r in REGIMES)
    retained=sum(double[r]["saved_churn"]>0 and
                 double[r]["saved_churn"]>=.25*refs[r]["saved_churn"]
                 for r in REGIMES)
    if positives>=3 and retained>=3:
        label="BOUNDED_RECOVERY"
    elif positives>=2:
        label="PARTIAL"
    else:
        label="NO_RECOVERY"
    return {"schema":"yggdrasil.y040-reset-severity-frontier.v1",
            "parent_head":"286dfaec783ff017fd6921e0575e7bbf7e70c020",
            "classification":label,"capacity9_double_positive_regimes":positives,
            "capacity9_double_retained_quarter_regimes":retained,
            "development_seeds":DEV,"sealed_heldout_seeds":HELDOUT,
            "cells":cells,"model_calls":0,
            "claim_limit":"Bounded synthetic assignment cache recovery only"}

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
