"""Y038: preregistered three-dose home drift ablation of four-slot LFU."""
import importlib.util
import json
import hashlib
from collections import OrderedDict
from pathlib import Path

PARENT=Path(__file__).resolve().parent.parent/"20261013-y037-stable-eviction"/"execute.py"
spec=importlib.util.spec_from_file_location("y037_frozen",PARENT)
assert spec and spec.loader
y37=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y37)
y35=y37.y35

DOSES=(0,1,3)
CAPACITY=4


def geometry(seed,ep,dose):
    active,_,hot=y37.geometry(seed,ep)
    salt=y35.salt(seed)
    adj={
        key:{(7*(key//2)+salt+dose*ep+offset)%16
             for offset in range(-2,3)}
        for key in active
    }
    return active,adj,hot


def signature(seed,dose):
    canonical=[]
    for ep in range(16):
        active,adj,_=geometry(seed,ep,dose)
        canonical.append((active,[sorted(adj[key]) for key in active]))
    return hashlib.sha256(json.dumps(canonical,separators=(",",":")).encode()).hexdigest()


def evaluate(seed,dose,policy):
    cache=OrderedDict()
    prev_active=set()
    prev_placements={}
    prev_counts={}
    evaluator_last={}
    trace=[]
    for ep in range(16):
        active,adj,hot=geometry(seed,ep,dose)
        oracle=y35.hall_cardinality(active,adj)
        preferences={}
        counts={}
        for key in active:
            record=cache.get(key)
            if record is None:
                counts[key]=1
            else:
                cell,count=record
                counts[key]=min(3,count+1)
                if cell in adj[key]:preferences[key]=cell
        assigned,calls=y35.match(active,adj,preferences)
        returning=[key for key in assigned if key in evaluator_last]
        churn=sum(assigned[key]!=evaluator_last[key] for key in returning)
        hot_churn=sum(assigned[key]!=evaluator_last[key]
                      for key in returning if key in hot)
        for key in assigned:evaluator_last[key]=assigned[key]
        for key in active:cache.pop(key,None)
        writes=evictions=0
        for key in sorted(prev_active.difference(active)):
            if key in prev_placements:
                cache.pop(key,None)
                cache[key]=(prev_placements[key],prev_counts[key])
                writes+=1
                while len(cache)>CAPACITY:
                    if policy=="LRU":
                        cache.popitem(last=False)
                    else:
                        assert policy=="LFU"
                        keys=list(cache)
                        evict=min(keys,key=lambda k:(cache[k][1],keys.index(k),k))
                        cache.pop(evict)
                    evictions+=1
        assert len(cache)<=CAPACITY and len(cache)+len(active)<=11
        assert all(1<=v[1]<=3 for v in cache.values())
        prev_active=set(active)
        prev_placements=assigned
        prev_counts=counts
        trace.append({"episode":ep,"matched":len(assigned),
                      "oracle":oracle,"churn":churn,"hot_churn":hot_churn,
                      "search_calls":calls,"evictions":evictions,
                      "writes":writes,"cache_entries":len(cache),
                      "legal_preferences":len(preferences)})
    return {
        "seed":seed,"dose":dose,"cohort":"development" if seed<108 else "heldout",
        "policy":policy,"hot_churn":sum(x["hot_churn"] for x in trace),
        "all_churn":sum(x["churn"] for x in trace),
        "evictions":sum(x["evictions"] for x in trace),
        "search_calls":sum(x["search_calls"] for x in trace),
        "writes":sum(x["writes"] for x in trace),
        "legal_preferences":sum(x["legal_preferences"] for x in trace),
        "episodes":trace
    }


def dose(d):
    signatures={str(s):signature(s,d) for s in range(104,112)}
    unique=len(set(signatures.values()))==8
    rows=[evaluate(seed,d,policy) for seed in range(104,112)
          for policy in ("LRU","LFU")]
    pairs={seed:(rows[2*(seed-104)],rows[2*(seed-104)+1])
           for seed in range(104,112)}
    hall=True
    full=True
    for a,b in pairs.values():
        for row in (a,b):
            for ep in row["episodes"]:
                if ep["matched"]!=ep["oracle"]:hall=False
                if ep["matched"]!=7:full=False
                if ep["cache_entries"]>4:raise AssertionError("CAPACITY")
    heldout=[pairs[s] for s in range(108,112)]
    exercised=all(a["evictions"]>0 and b["evictions"]>0 for a,b in heldout)
    hot=[a["hot_churn"]-b["hot_churn"] for a,b in heldout]
    all_savings=[a["all_churn"]-b["all_churn"] for a,b in heldout]
    label=("BENEFIT" if sum(hot)>0 and sum(all_savings)>=0 else
           "TRADEOFF" if sum(hot)>0 else
           "ADVERSE" if sum(hot)<0 else "NO_GAIN")
    return {
        "dose":d,"unique":unique,"hall_ok":hall,"all_matched":full,
        "exercised":exercised,"signatures":signatures,
        "heldout_hot_savings":hot,"heldout_hot_total_savings":sum(hot),
        "heldout_overall_savings":all_savings,
        "heldout_hot_LRU":sum(a["hot_churn"] for a,b in heldout),
        "heldout_hot_LFU":sum(b["hot_churn"] for a,b in heldout),
        "heldout_evictions":[[a["evictions"],b["evictions"]] for a,b in heldout],
        "label":label,"rows":rows
    }


def run():
    results=[dose(value) for value in DOSES]
    if not all(r["unique"] and r["hall_ok"] for r in results):
        label="INVALID"
    elif not all(r["all_matched"] for r in results):
        label="GEOMETRY_DEFICIENCY"
    elif not all(r["exercised"] for r in results):
        label="CAUSAL_TEST_UNEXERCISED"
    else:
        values=[r["heldout_hot_total_savings"] for r in results]
        label="MONOTONE_LFU_DECAY" if values[0]>values[1]>values[2] else "NONMONOTONE"
    return {
        "schema":"yggdrasil.y038-lfu-home-drift-dose.v1",
        "predecessor_head":"0e744c6417e73223f42294fe3b3c4b2133633403",
        "classification":label,
        "doses":results,"model_calls":0,
        "scope":"Three frozen synthetic home-drift doses; no post-result selection"
    }


if __name__=="__main__":
    data=run()
    assert data==run()
    print(json.dumps(data,sort_keys=True,indent=2))
