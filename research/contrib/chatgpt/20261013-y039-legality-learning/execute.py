"""Y039: legality-conditioned 2-bit frequency learning with real 4-slot eviction."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PARENT=Path(__file__).resolve().parent.parent/"20261013-y038-eviction-drift"/"execute.py"
spec=importlib.util.spec_from_file_location("y038_frozen",PARENT)
assert spec and spec.loader
y38=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y38)
y35=y38.y35

ARMS=("LRU","LFU_ANY_HIT","LFU_LEGAL_HIT")


def evaluate(seed,arm):
    cache=OrderedDict()
    last_active=set()
    last_assign={}
    last_counts={}
    evaluator_history={}
    trace=[]
    for ep in range(16):
        active,neighbors,hot=y38.geometry(seed,ep,1)
        oracle=y35.hall_cardinality(active,neighbors)
        preferred={}
        counts={}
        for key in active:
            record=cache.get(key)
            if record is None:
                counts[key]=1
            else:
                cell,old_count=record
                legal=cell in neighbors[key]
                if legal:preferred[key]=cell
                if arm=="LFU_LEGAL_HIT" and not legal:
                    counts[key]=1
                else:
                    counts[key]=min(3,old_count+1)
        assigned,calls=y35.match(active,neighbors,preferred)
        returning=[key for key in assigned if key in evaluator_history]
        churn=sum(assigned[key]!=evaluator_history[key] for key in returning)
        hot_churn=sum(assigned[key]!=evaluator_history[key]
                      for key in returning if key in hot)
        for key in assigned:evaluator_history[key]=assigned[key]
        for key in active:cache.pop(key,None)
        writes=evictions=0
        for key in sorted(last_active.difference(active)):
            if key in last_assign:
                cache.pop(key,None)
                cache[key]=(last_assign[key],last_counts[key])
                writes+=1
                while len(cache)>4:
                    if arm=="LRU":
                        cache.popitem(last=False)
                    else:
                        keys=list(cache)
                        victim=min(keys,key=lambda k:(cache[k][1],keys.index(k),k))
                        cache.pop(victim)
                    evictions+=1
        assert len(cache)<=4 and len(cache)+len(active)<=11
        assert all(1<=x[1]<=3 for x in cache.values())
        last_active=set(active)
        last_assign=assigned
        last_counts=counts
        trace.append({
            "episode":ep,"matched":len(assigned),"oracle":oracle,
            "churn":churn,"hot_churn":hot_churn,
            "search_calls":calls,"writes":writes,"evictions":evictions,
            "cached_entries":len(cache),"legal_preferences":len(preferred)
        })
    return {
        "seed":seed,"cohort":"development" if seed<124 else "heldout",
        "arm":arm,"hot_churn":sum(x["hot_churn"] for x in trace),
        "all_churn":sum(x["churn"] for x in trace),
        "evictions":sum(x["evictions"] for x in trace),
        "writes":sum(x["writes"] for x in trace),
        "search_calls":sum(x["search_calls"] for x in trace),
        "legal_preferences":sum(x["legal_preferences"] for x in trace),
        "episodes":trace
    }


def run():
    signatures={str(s):y38.signature(s,1) for s in range(120,128)}
    unique=len(set(signatures.values()))==8
    rows=[evaluate(seed,arm) for seed in range(120,128) for arm in ARMS]
    groups={s:rows[3*(s-120):3*(s-120)+3] for s in range(120,128)}
    hall=True
    full=True
    for g in groups.values():
        for r in g:
            for ep in r["episodes"]:
                if ep["matched"]!=ep["oracle"]:hall=False
                if ep["matched"]!=7:full=False
                if ep["cached_entries"]>4:raise AssertionError("CAPACITY")
    held=[groups[s] for s in range(124,128)]
    exercised=all(r["evictions"]>0 for group in held for r in group)
    hot_savings=[g[1]["hot_churn"]-g[2]["hot_churn"] for g in held]
    total_savings=[g[1]["all_churn"]-g[2]["all_churn"] for g in held]
    if not unique or not hall:
        label="INVALID"
    elif not full:
        label="GEOMETRY_DEFICIENCY"
    elif not exercised:
        label="CAUSAL_TEST_UNEXERCISED"
    elif (sum(hot_savings)>0 and sum(total_savings)>=0
          and sum(v>=0 for v in hot_savings)>=3):
        label="LEGAL_HIT_LEARNING_BENEFIT"
    elif sum(hot_savings)>0 and sum(total_savings)<0:
        label="MIXED"
    else:
        label="NEGATIVE"
    return {
        "schema":"yggdrasil.y039-legal-hit-frequency.v1",
        "predecessor_head":"439a84addf877ecf0d67b0656b1480147d5cc0aa",
        "classification":label,
        "unique_signatures":unique,"geometry_signatures":signatures,
        "hall_agrees":hall,"all_matched":full,
        "all_arms_evicted":exercised,
        "heldout_hot_savings_legal_vs_any":hot_savings,
        "heldout_total_savings_legal_vs_any":total_savings,
        "heldout_churn_by_arm":{arm:{
            "hot":sum(g[i]["hot_churn"] for g in held),
            "total":sum(g[i]["all_churn"] for g in held),
            "evictions":sum(g[i]["evictions"] for g in held)}
            for i,arm in enumerate(ARMS)},
        "rows":rows,"model_calls":0,
        "scope":"Synthetic observed-legality feedback for four-slot frequency learning"
    }


if __name__=="__main__":
    outcome=run()
    assert outcome==run()
    print(json.dumps(outcome,sort_keys=True,indent=2))
