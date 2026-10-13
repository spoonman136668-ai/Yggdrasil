"""Y034: preregistered capacity-limited cache science at 0,4,9 slots."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

OLD=Path(__file__).resolve().parent.parent/"20261013-y033-recurrence"/"execute.py"
spec=importlib.util.spec_from_file_location("y033_frozen",OLD)
assert spec and spec.loader
previous=importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
y30=previous.y30
SCHEDULES=previous.SCHEDULES
CAPACITIES=(0,4,9)
WEIGHTS=(1,3,10)


def world(seed,episode,condition):
    keys,neighbors=y30.geometry(seed,episode)
    shift=SCHEDULES[condition][episode]
    return keys,{key:{(cell+shift)%16 for cell in neighbors[key]} for key in keys}


def evaluate(seed,condition,capacity,retain):
    cache=OrderedDict()
    prev_active=set()
    prev_assignment={}
    evaluation_history={}
    trace=[]
    for ep in range(8):
        active,neighbor=world(seed,ep,condition)
        assert y30.hall_cardinality(active,neighbor)==7
        preferred={k:cache[k] for k in active if k in cache} if retain else {}
        legal={k:v for k,v in preferred.items() if v in neighbor[k]}
        assigned,calls=y30.match(active,neighbor,preferred)
        assert len(assigned)==7
        returning=[k for k in assigned if k in evaluation_history]
        churn=sum(assigned[k]!=evaluation_history[k] for k in returning)
        evaluation_history.update(assigned)
        for key in active:
            cache.pop(key,None)
        writes=0
        if capacity>0:
            for key in sorted(prev_active.difference(active)):
                cache.pop(key,None)
                cache[key]=prev_assignment[key]
                writes+=1
                while len(cache)>capacity:
                    cache.popitem(last=False)
        assert len(cache)<=capacity and len(cache)+7<=16
        assert not set(cache).intersection(active)
        prev_active=set(active)
        prev_assignment=assigned
        trace.append({"episode":ep,"matched":len(assigned),"churn":churn,
                      "search_calls":calls,"writes":writes,
                      "read_attempts":len(preferred),"legal_preferences":len(legal),
                      "cache_occupancy":len(cache)})
    row={"seed":seed,"condition":condition,"capacity":capacity,
         "arm":"retained" if retain else "sham",
         "churn":sum(x["churn"] for x in trace),
         "search_calls":sum(x["search_calls"] for x in trace),
         "cache_writes":sum(x["writes"] for x in trace),
         "cache_reads":sum(x["read_attempts"] for x in trace),
         "legal_prefs":sum(x["legal_preferences"] for x in trace),
         "max_observed_occupancy":max(x["cache_occupancy"] for x in trace),
         "trace":trace}
    row["cost"]={str(w):w*row["churn"]+row["search_calls"]+row["cache_writes"]+row["cache_reads"]
                 for w in WEIGHTS}
    return row


def dose(condition,capacity):
    rows=[evaluate(seed,condition,capacity,read)
          for seed in range(72,80) for read in (False,True)]
    for i in range(0,len(rows),2):
        sham,retained=rows[i:i+2]
        assert sham["cache_writes"]==retained["cache_writes"]
        assert [x["cache_occupancy"] for x in sham["trace"]]==[
            x["cache_occupancy"] for x in retained["trace"]]
        assert all(x["matched"]==7 for r in (sham,retained) for x in r["trace"])
    heldout=[(rows[2*(seed-72)],rows[2*(seed-72)+1]) for seed in range(76,80)]
    savings={str(w):[sham["cost"][str(w)]-retained["cost"][str(w)]
                      for sham,retained in heldout] for w in WEIGHTS}
    return {"condition":condition,"capacity":capacity,
        "heldout_churn_savings":[a["churn"]-b["churn"] for a,b in heldout],
        "heldout_cost_savings_by_weight":savings,
        "heldout_total_cost_savings":{key:sum(x) for key,x in savings.items()},
        "heldout_legal_preferences":sum(b["legal_prefs"] for a,b in heldout),
        "heldout_max_occupancy":max(b["max_observed_occupancy"] for a,b in heldout),
        "rows":rows}


def run():
    signatures={str(seed):previous.geometry_signature(seed,"constant")
                for seed in range(72,80)}
    assert len(set(signatures.values()))==8
    results=[dose(condition,capacity)
             for condition in ("constant","recurrent") for capacity in CAPACITIES]
    constant={r["capacity"]:r for r in results if r["condition"]=="constant"}
    low=constant[4]["heldout_total_cost_savings"]["3"]
    high=constant[9]["heldout_total_cost_savings"]["3"]
    if low>0 and low>high:
        classification="INTERMEDIATE_OPTIMUM"
    elif high>0 and high>low:
        classification="FULL_CAP_OPTIMUM"
    else:
        classification="NO_CAPACITY_GAIN"
    return {"schema":"yggdrasil.y034-cache-capacity-dose.v1",
        "predecessor_head":"92fdc63bd3bc95ec284dfb47a6c1c6d446d9dfb4",
        "classification":classification,"frozen_capacities":CAPACITIES,
        "unique_geometry_signatures":True,"geometry_signatures":signatures,
        "conditions":results,"model_calls":0,
        "claim_limit":"Synthetic memory-capacity tradeoff, not biological developmental memory"}


if __name__=="__main__":
    result=run()
    assert result==run()
    print(json.dumps(result,sort_keys=True,indent=2))
