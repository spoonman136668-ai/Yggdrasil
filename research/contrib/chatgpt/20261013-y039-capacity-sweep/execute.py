"""Y039: preregistered 0/3/6/9 dormant memory capacities, stable vs switch."""
import hashlib
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PREVIOUS=Path(__file__).resolve().parent.parent/"20261013-y033-associative-recall"/"execute.py"
spec=importlib.util.spec_from_file_location("y033_frozen",PREVIOUS)
assert spec and spec.loader
y33=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y33)

CAPACITIES=(0,3,6,9)
CONDITIONS=("STABLE","SWITCH")


def evaluate(seed,condition,capacity):
    assert capacity in CAPACITIES
    live={}
    cache=OrderedDict()
    observed_ever=set()
    rows=[]
    for episode in range(12):
        keys=y33.active_keys(seed,episode)
        predictions={}
        from_dormant=set()
        for key in keys:
            if key in live:
                predictions[key]=live[key]
            elif key in cache:
                predictions[key]=cache[key]
                from_dormant.add(key)
            else:
                predictions[key]=0
        # Feedback is visible only AFTER all seven predictions.
        truth={key:y33.target(seed,key,episode,condition) for key in keys}
        returning=[key for key in keys if key in observed_ever and key not in live]
        correct=sum(predictions[key]==truth[key] for key in keys)
        returning_correct=sum(predictions[key]==truth[key] for key in returning)
        stale_returning_error=sum(
            predictions[key]!=truth[key] for key in returning if key in from_dormant
        )
        for key in keys:
            cache.pop(key,None)
        inserts=evictions=0
        for key in sorted(set(live).difference(keys)):
            if capacity==0:
                continue
            cache.pop(key,None)
            cache[key]=live[key]
            inserts+=1
            while len(cache)>capacity:
                cache.popitem(last=False)
                evictions+=1
        live=truth
        observed_ever.update(keys)
        assert len(live)==7 and len(cache)<=capacity
        assert len(live)+len(cache)<=16
        assert not set(live).intersection(cache)
        rows.append({
            "episode":episode,"correct":correct,"returning":len(returning),
            "returning_correct":returning_correct,"stale_returning_error":stale_returning_error,
            "cache_inserts":inserts,"evictions":evictions,
            "cache_entries":len(cache),
        })
    return {
        "seed":seed,"cohort":"development" if seed<116 else "heldout",
        "condition":condition,"capacity":capacity,
        "correct":sum(r["correct"] for r in rows),
        "post_correct":sum(r["correct"] for r in rows[6:]),
        "returning_correct":sum(r["returning_correct"] for r in rows),
        "post_stale_error":sum(r["stale_returning_error"] for r in rows[6:]),
        "inserts":sum(r["cache_inserts"] for r in rows),
        "evictions":sum(r["evictions"] for r in rows),
        "episodes":rows,
    }


def run():
    signatures={str(seed):y33.signature(seed) for seed in range(112,120)}
    assert len(set(signatures.values()))==8
    rows=[evaluate(seed,condition,cap) for condition in CONDITIONS
          for seed in range(112,120) for cap in CAPACITIES]
    def aggregate(condition,field):
        return {
            str(cap):sum(r[field] for r in rows if r["seed"]>=116
                         and r["condition"]==condition and r["capacity"]==cap)
            for cap in CAPACITIES
        }
    stable=aggregate("STABLE","correct")
    switched=aggregate("SWITCH","post_correct")
    stale=aggregate("SWITCH","post_stale_error")
    inserts=aggregate("STABLE","inserts")
    evictions=aggregate("STABLE","evictions")
    vals=[stable[str(cap)] for cap in CAPACITIES]
    label=("CAPACITY_RECALL_GRADIENT"
           if all(vals[i]<=vals[i+1] for i in range(3)) and vals[-1]>vals[0]
           else "NONMONOTONE")
    return {
        "schema":"yggdrasil.y039-dormant-capacity-frontier.v1",
        "predecessor_head":"3ff04209bda00bf55fdc7d43a3ad19c221d05dda",
        "classification":label,"unique_signatures":True,
        "capacity_levels":CAPACITIES,
        "heldout_stable_correct":stable,
        "heldout_switch_post_correct":switched,
        "heldout_switch_post_stale_errors":stale,
        "heldout_stable_inserts":inserts,
        "heldout_stable_evictions":evictions,
        "rows":rows,"model_calls":0,
        "claim_limit":"Synthetic cue memory retention across predeclared 0/3/6/9 resource bounds."
    }


if __name__=="__main__":
    outcome=run()
    assert outcome==run()
    print(json.dumps(outcome,sort_keys=True,indent=2))
