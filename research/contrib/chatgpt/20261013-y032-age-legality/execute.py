"""Y032: preregistered interaction between cache age and legal margin."""
import importlib.util
import json
import hashlib
from pathlib import Path
from collections import OrderedDict

PARENT=Path(__file__).resolve().parent.parent/"20261013-y031-aged-retention"/"execute.py"
spec=importlib.util.spec_from_file_location("y031_frozen",PARENT)
assert spec and spec.loader
y31=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y31)
y30=y31.prior
ARMS=("sham","unrestricted","age2","hybrid")


def signature(seed):
    canonical=[]
    for logical in y31.EPISODES:
        active,adj=y30.geometry(seed,logical)
        canonical.append((active,[sorted(adj[k]) for k in active]))
    return hashlib.sha256(json.dumps(canonical,separators=(",",":")).encode()).hexdigest()


def inner_neighbors(outer):
    inner={}
    for key,cellset in outer.items():
        possible=[h for h in range(16)
                  if set((h+d)%16 for d in range(-2,3))==cellset]
        assert len(possible)==1
        home=possible[0]
        inner[key]={((home+d)%16) for d in range(-1,2)}
        assert inner[key].issubset(cellset)
    return inner


def evaluate(seed,arm):
    cache=OrderedDict()
    previous_active=set()
    previous_placements={}
    evaluator_history={}
    rows=[]
    for observation,logical in enumerate(y31.EPISODES):
        active,adj=y30.geometry(seed,logical)
        inner=inner_neighbors(adj)
        oracle=y30.hall_cardinality(active,adj)
        pref={}
        for key in active:
            if arm=="sham" or key not in cache:continue
            cell,last=cache[key]
            if cell not in adj[key]:continue
            young=observation-last<=2
            if arm=="age2" and not young:continue
            if arm=="hybrid" and not young and cell not in inner[key]:continue
            pref[key]=cell
        assigned,calls=y30.match(active,adj,pref)
        returning=[k for k in assigned if k in evaluator_history]
        churn=sum(assigned[k]!=evaluator_history[k] for k in returning)
        for k in assigned:evaluator_history[k]=assigned[k]
        for k in active:cache.pop(k,None)
        writes=0
        for key in sorted(previous_active.difference(active)):
            cache.pop(key,None)
            if key in previous_placements:
                cache[key]=(previous_placements[key],observation-1)
                writes+=1
                while len(cache)>9:cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+len(active)<=16
        assert not set(cache).intersection(active)
        previous_active=set(active)
        previous_placements=assigned
        rows.append({"observation":observation,"logical":logical,
                     "matched":len(assigned),"oracle":oracle,
                     "returning":len(returning),"churn":churn,
                     "calls":calls,"writes":writes,"entries":len(cache),
                     "preferences":len(pref)})
    return {
        "seed":seed,"cohort":"development" if seed<60 else "heldout",
        "arm":arm,"total_churn":sum(r["churn"] for r in rows),
        "total_search_calls":sum(r["calls"] for r in rows),
        "total_writes":sum(r["writes"] for r in rows),
        "preferences":sum(r["preferences"] for r in rows),
        "episodes":rows
    }


def run():
    sigs={str(s):signature(s) for s in range(56,64)}
    unique=len(set(sigs.values()))==8
    results=[evaluate(s,arm) for s in range(56,64) for arm in ARMS]
    groups={s:results[4*(s-56):4*(s-56)+4] for s in range(56,64)}
    bookkeeping=True
    oracle_ok=True
    all_matched=True
    for group in groups.values():
        if len({tuple(ep["writes"] for ep in r["episodes"]) for r in group})!=1:
            bookkeeping=False
        if len({tuple(ep["entries"] for ep in r["episodes"]) for r in group})!=1:
            bookkeeping=False
        for r in group:
            for ep in r["episodes"]:
                if ep["matched"]!=ep["oracle"]:oracle_ok=False
                if ep["matched"]!=7:all_matched=False
    heldout=[groups[s] for s in range(60,64)]
    savings=[g[1]["total_churn"]-g[3]["total_churn"] for g in heldout]
    if not unique or not oracle_ok or not bookkeeping:
        label="INVALID"
    elif not all_matched:
        label="GEOMETRY_DEFICIENCY"
    elif all(x>=0 for x in savings) and sum(savings)>0:
        label="HYBRID_BENEFIT"
    elif any(x>0 for x in savings) and any(x<0 for x in savings):
        label="MIXED"
    else:
        label="NO_GAIN"
    return {
        "schema":"yggdrasil.y032-cache-age-legality.v1",
        "predecessor_head":"5d0301092b0f6626001509196d6d063c4f0ca0c0",
        "classification":label,"unique_signatures":unique,
        "hall_agrees":oracle_ok,"all_seven_matched":all_matched,
        "bookkeeping_parity":bookkeeping,"geometry_signatures":sigs,
        "heldout_hybrid_savings_over_unrestricted":savings,
        "heldout_churn_by_arm":{arm:sum(g[i]["total_churn"] for g in heldout)
                               for i,arm in enumerate(ARMS)},
        "heldout_search_calls_by_arm":{arm:sum(g[i]["total_search_calls"] for g in heldout)
                               for i,arm in enumerate(ARMS)},
        "rows":results,"model_calls":0,
        "scope":"Finite synthetic observed-state retention, not semantic cognition"
    }


if __name__=="__main__":
    result=run()
    assert result==run()
    print(json.dumps(result,sort_keys=True,indent=2))
