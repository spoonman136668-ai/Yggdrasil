"""Y037: active-only recurrence with stable paired collision homes and real evictions."""
import importlib.util
import json
import hashlib
from pathlib import Path
from collections import OrderedDict

PARENT=Path(__file__).resolve().parent.parent/"20261013-y036-real-eviction"/"execute.py"
spec=importlib.util.spec_from_file_location("y036_frozen",PARENT)
assert spec and spec.loader
y36=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y36)
y35=y36.y35

CAPACITY=4


def geometry(seed,episode):
    active,_,hot=y35.geometry(seed,episode)
    s=y35.salt(seed)
    neighbors={
        key:{((7*(key//2)+s+d)%16) for d in range(-2,3)}
        for key in active
    }
    return active,neighbors,hot


def signature(seed):
    rows=[]
    for ep in range(16):
        active,neighbors,_=geometry(seed,ep)
        rows.append((active,[sorted(neighbors[key]) for key in active]))
    return hashlib.sha256(json.dumps(rows,separators=(",",":")).encode()).hexdigest()


def evaluate(seed,policy):
    cache=OrderedDict()
    old_active=set()
    old_assignment={}
    old_count={}
    evaluator_history={}
    trace=[]
    for ep in range(16):
        active,adj,hot=geometry(seed,ep)
        oracle=y35.hall_cardinality(active,adj)
        pref={}
        counts={}
        hit_count=0
        for key in active:
            memory=cache.get(key)
            if memory is not None:
                cell,freq=memory
                hit_count+=1
                counts[key]=min(3,freq+1)
                if cell in adj[key]:pref[key]=cell
            else:
                counts[key]=1
        assigned,calls=y35.match(active,adj,pref)
        returning=[key for key in assigned if key in evaluator_history]
        churn=sum(assigned[key]!=evaluator_history[key] for key in returning)
        hot_churn=sum(assigned[key]!=evaluator_history[key]
                      for key in returning if key in hot)
        for key in assigned:evaluator_history[key]=assigned[key]
        for key in active:cache.pop(key,None)
        writes=evictions=0
        for key in sorted(old_active.difference(active)):
            if key in old_assignment:
                cache.pop(key,None)
                cache[key]=(old_assignment[key],old_count[key])
                writes+=1
                while len(cache)>CAPACITY:
                    if policy=="LRU":
                        cache.popitem(last=False)
                    else:
                        assert policy=="LFU"
                        keys=list(cache)
                        key_to_evict=min(keys,key=lambda k:(cache[k][1],keys.index(k),k))
                        cache.pop(key_to_evict)
                    evictions+=1
        assert len(cache)<=CAPACITY and len(cache)+len(active)<=11
        assert all(1<=m[1]<=3 for m in cache.values())
        old_active=set(active)
        old_assignment=assigned
        old_count=counts
        trace.append({
            "episode":ep,"assigned":len(assigned),"oracle":oracle,
            "returning":len(returning),"churn":churn,
            "hot_churn":hot_churn,"calls":calls,
            "writes":writes,"evictions":evictions,
            "entries":len(cache),"hits":hit_count,
            "legal_preferences":len(pref)
        })
    return {
        "seed":seed,"cohort":"development" if seed<100 else "heldout",
        "policy":policy,
        "hot_churn":sum(ep["hot_churn"] for ep in trace),
        "all_churn":sum(ep["churn"] for ep in trace),
        "search_calls":sum(ep["calls"] for ep in trace),
        "evictions":sum(ep["evictions"] for ep in trace),
        "writes":sum(ep["writes"] for ep in trace),
        "legal_preferences":sum(ep["legal_preferences"] for ep in trace),
        "episodes":trace
    }


def run():
    signatures={str(s):signature(s) for s in range(96,104)}
    unique=len(set(signatures.values()))==8
    rows=[evaluate(seed,policy) for seed in range(96,104)
          for policy in ("LRU","LFU")]
    pairs={seed:(rows[2*(seed-96)],rows[2*(seed-96)+1])
           for seed in range(96,104)}
    hall=True
    complete=True
    for a,b in pairs.values():
        for r in (a,b):
            for ep in r["episodes"]:
                if ep["assigned"]!=ep["oracle"]:hall=False
                if ep["assigned"]!=7:complete=False
                if ep["entries"]>CAPACITY:raise AssertionError("CAPACITY")
    held=[pairs[s] for s in range(100,104)]
    exercised=all(a["evictions"]>0 and b["evictions"]>0 for a,b in held)
    hot_saved=[a["hot_churn"]-b["hot_churn"] for a,b in held]
    all_saved=[a["all_churn"]-b["all_churn"] for a,b in held]
    if not unique or not hall:
        label="INVALID"
    elif not complete:
        label="GEOMETRY_DEFICIENCY"
    elif not exercised:
        label="CAUSAL_TEST_UNEXERCISED"
    elif (sum(hot_saved)>0 and sum(all_saved)>=0
          and sum(x>=0 for x in hot_saved)>=3):
        label="FREQ_STABLE_GEOMETRY_BENEFIT"
    elif sum(hot_saved)>0 and sum(all_saved)<0:
        label="MIXED"
    else:
        label="NEGATIVE"
    return {
        "schema":"yggdrasil.y037-stable-homes-eviction.v1",
        "predecessor_head":"30c3385ac5761ab02d38012c0d1b62ce3e2842bc",
        "classification":label,
        "unique_signatures":unique,
        "geometry_signatures":signatures,
        "hall_agrees":hall,"all_matched":complete,
        "all_heldout_evicted":exercised,
        "hot_savings_LFU_vs_LRU":hot_saved,
        "overall_savings_LFU_vs_LRU":all_saved,
        "heldout_hot_churn_LRU":sum(a["hot_churn"] for a,b in held),
        "heldout_hot_churn_LFU":sum(b["hot_churn"] for a,b in held),
        "heldout_all_churn_LRU":sum(a["all_churn"] for a,b in held),
        "heldout_all_churn_LFU":sum(b["all_churn"] for a,b in held),
        "heldout_evictions_by_seed":[[a["evictions"],b["evictions"]] for a,b in held],
        "rows":rows,"model_calls":0,
        "scope":"Four-slot observed-frequency memory under stable collided synthetic homes"
    }


if __name__=="__main__":
    outcome=run()
    assert outcome==run()
    print(json.dumps(outcome,sort_keys=True,indent=2))
