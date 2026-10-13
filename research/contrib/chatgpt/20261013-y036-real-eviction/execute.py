"""Y036: causal LRU vs LFU eviction under an explicitly reduced four-slot cache."""
import importlib.util
import json
from pathlib import Path
from collections import OrderedDict

PARENT=Path(__file__).resolve().parent.parent/"20261013-y035-frequency-eviction"/"execute.py"
spec=importlib.util.spec_from_file_location("y035_frozen",PARENT)
assert spec and spec.loader
y35=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y35)

CACHE_SLOTS=4


def evaluate(seed,policy):
    cache=OrderedDict()
    old_active=set()
    old_assign={}
    old_counts={}
    evaluator_last={}
    rows=[]
    for episode in range(16):
        active,neighbors,hot=y35.geometry(seed,episode)
        oracle=y35.hall_cardinality(active,neighbors)
        preferences={}
        counts={}
        cache_hits=0
        for key in active:
            state=cache.get(key)
            if state is not None:
                cell,count=state
                cache_hits+=1
                counts[key]=min(3,count+1)
                if cell in neighbors[key]:preferences[key]=cell
            else:
                counts[key]=1
        assigned,calls=y35.match(active,neighbors,preferences)
        returning=[key for key in assigned if key in evaluator_last]
        churn=sum(assigned[key]!=evaluator_last[key] for key in returning)
        hot_churn=sum(assigned[key]!=evaluator_last[key]
                      for key in returning if key in hot)
        for key in assigned:evaluator_last[key]=assigned[key]
        for key in active:cache.pop(key,None)

        writes=evictions=0
        for key in sorted(old_active.difference(active)):
            if key in old_assign:
                cache.pop(key,None)
                cache[key]=(old_assign[key],old_counts[key])
                writes+=1
                while len(cache)>CACHE_SLOTS:
                    if policy=="LRU":
                        cache.popitem(last=False)
                    else:
                        assert policy=="LFU"
                        keys=list(cache)
                        evict=min(keys,key=lambda k:(cache[k][1],keys.index(k),k))
                        cache.pop(evict)
                    evictions+=1
        assert len(cache)<=CACHE_SLOTS
        assert len(cache)+len(active)<=11
        assert all(1<=state[1]<=3 for state in cache.values())
        old_active=set(active)
        old_assign=assigned
        old_counts=counts
        rows.append({
            "episode":episode,"matched":len(assigned),
            "oracle":oracle,"churn":churn,"hot_churn":hot_churn,
            "returning":len(returning),"calls":calls,
            "cache_writes":writes,"cache_evictions":evictions,
            "cache_entries":len(cache),"cache_hits":cache_hits,
            "legal_preferences":len(preferences)
        })
    return {
        "seed":seed,"cohort":"development" if seed<92 else "heldout",
        "policy":policy,"hot_churn":sum(t["hot_churn"] for t in rows),
        "all_churn":sum(t["churn"] for t in rows),
        "search_calls":sum(t["calls"] for t in rows),
        "cache_evictions":sum(t["cache_evictions"] for t in rows),
        "cache_writes":sum(t["cache_writes"] for t in rows),
        "cache_hits":sum(t["cache_hits"] for t in rows),
        "legal_preferences":sum(t["legal_preferences"] for t in rows),
        "episodes":rows
    }


def run():
    sig={str(s):y35.signature(s) for s in range(88,96)}
    unique=len(set(sig.values()))==8
    results=[evaluate(seed,policy) for seed in range(88,96)
             for policy in ("LRU","LFU")]
    pairs={s:(results[2*(s-88)],results[2*(s-88)+1]) for s in range(88,96)}
    hall=True
    complete=True
    for a,b in pairs.values():
        for row in (a,b):
            for ep in row["episodes"]:
                if ep["matched"]!=ep["oracle"]:hall=False
                if ep["matched"]!=7:complete=False
                if ep["cache_entries"]>4:raise AssertionError("CAPACITY")
    held=[pairs[s] for s in range(92,96)]
    exercised=all(a["cache_evictions"]>0 and b["cache_evictions"]>0
                  for a,b in held)
    hot_saved=[a["hot_churn"]-b["hot_churn"] for a,b in held]
    overall_saved=[a["all_churn"]-b["all_churn"] for a,b in held]
    if not unique or not hall:
        label="INVALID"
    elif not complete:
        label="GEOMETRY_DEFICIENCY"
    elif not exercised:
        label="CAUSAL_TEST_UNEXERCISED"
    elif (sum(hot_saved)>0 and sum(overall_saved)>=0
          and sum(v>=0 for v in hot_saved)>=3):
        label="FREQ_EVICTION_BENEFIT"
    elif sum(hot_saved)>0 and sum(overall_saved)<0:
        label="MIXED"
    else:
        label="NEGATIVE"
    return {
        "schema":"yggdrasil.y036-cache-pressure.v1",
        "predecessor_head":"6ee81d14358338216bf4a57a2607de6f6fc984e0",
        "classification":label,
        "cache_capacity":4,"all_heldout_arms_evicted":exercised,
        "unique_signatures":unique,"hall_agrees":hall,"all_matched":complete,
        "geometry_signatures":sig,
        "heldout_hot_churn_savings_LFU_vs_LRU":hot_saved,
        "heldout_overall_churn_savings_LFU_vs_LRU":overall_saved,
        "heldout_hot_churn_LRU":sum(a["hot_churn"] for a,b in held),
        "heldout_hot_churn_LFU":sum(b["hot_churn"] for a,b in held),
        "heldout_total_churn_LRU":sum(a["all_churn"] for a,b in held),
        "heldout_total_churn_LFU":sum(b["all_churn"] for a,b in held),
        "heldout_evictions_by_seed":[(a["cache_evictions"],b["cache_evictions"])
                                     for a,b in held],
        "rows":results,
        "model_calls":0,
        "scope":"Synthetic observed-frequency policy under proven four-slot eviction pressure"
    }


if __name__=="__main__":
    result=run()
    assert result==run()
    print(json.dumps(result,sort_keys=True,indent=2))
