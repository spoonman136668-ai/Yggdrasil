"""Y034: frozen sticky versus overwrite cache recovery with equal slot ceiling."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PARENT=Path(__file__).resolve().parent.parent/"20261013-y033-shock-recovery"/"execute.py"
spec=importlib.util.spec_from_file_location("y033_frozen",PARENT)
assert spec and spec.loader
y33=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y33)
oracle=y33.prior

ARMS=("sham","recent","sticky")


def evaluate(seed,arm):
    cache=OrderedDict()
    old_active=set()
    old_assign={}
    history_for_evaluator={}
    baseline_for_evaluator={}
    trace=[]
    for ep in range(len(y33.PROGRAM)):
        active,adj=y33.geometry(seed,ep)
        optimum=oracle.hall_cardinality(active,adj)
        pref={key:cache[key] for key in active
              if arm!="sham" and key in cache and cache[key] in adj[key]}
        assigned,calls=oracle.match(active,adj,pref)
        returning=[key for key in assigned if key in history_for_evaluator]
        churn=sum(assigned[key]!=history_for_evaluator[key] for key in returning)
        for key in assigned:history_for_evaluator[key]=assigned[key]
        if ep<4:
            for key in assigned:baseline_for_evaluator.setdefault(key,assigned[key])
        overlap=[key for key in assigned if ep>=6 and key in baseline_for_evaluator]
        drift=sum(assigned[key]!=baseline_for_evaluator[key] for key in overlap)

        writes=0
        if arm=="sticky":
            # Cache may reserve memory for an active motif; never exceed nine
            # total cache slots even if those motifs are currently active.
            for key in active:
                if key in cache and cache[key] not in adj[key]:
                    cache.pop(key)
            for key in sorted(old_active.difference(active)):
                if key in old_assign and key not in cache:
                    cache[key]=old_assign[key]
                    writes+=1
                    while len(cache)>9:cache.popitem(last=False)
        else:
            # Sham and recency update precisely the same cache/write policy.
            for key in active:cache.pop(key,None)
            for key in sorted(old_active.difference(active)):
                cache.pop(key,None)
                if key in old_assign:
                    cache[key]=old_assign[key]
                    writes+=1
                    while len(cache)>9:cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+len(active)<=16
        old_active=set(active)
        old_assign=assigned
        phase="baseline" if ep<4 else "shock" if ep<6 else "recovery"
        trace.append({
            "observation":ep,"phase":phase,"matched":len(assigned),
            "hall_cardinality":optimum,"churn":churn,"returning":len(returning),
            "baseline_overlap":len(overlap),"baseline_drift":drift,
            "search_calls":calls,"writes":writes,"cached_entries":len(cache),
            "cached_active_entries":len(set(cache).intersection(active)),
            "legal_preferences":len(pref)
        })
    return {
        "seed":seed,"cohort":"development" if seed<76 else "heldout",
        "arm":arm,"recovery_churn":sum(t["churn"] for t in trace if t["phase"]=="recovery"),
        "recovery_baseline_drift":sum(t["baseline_drift"] for t in trace
                                      if t["phase"]=="recovery"),
        "total_writes":sum(t["writes"] for t in trace),
        "total_search_calls":sum(t["search_calls"] for t in trace),
        "total_legal_preferences":sum(t["legal_preferences"] for t in trace),
        "episodes":trace
    }


def run():
    signatures={str(s):y33.signature(s) for s in range(72,80)}
    unique=len(set(signatures.values()))==8
    rows=[evaluate(seed,arm) for seed in range(72,80) for arm in ARMS]
    groups={seed:rows[3*(seed-72):3*(seed-72)+3] for seed in range(72,80)}
    all_matched=True
    oracle_ok=True
    for group in groups.values():
        # Sham and recency must write equal count with equal occupancy.
        assert [t["writes"] for t in group[0]["episodes"]]==[
            t["writes"] for t in group[1]["episodes"]]
        assert [t["cached_entries"] for t in group[0]["episodes"]]==[
            t["cached_entries"] for t in group[1]["episodes"]]
        for result in group:
            for ep in result["episodes"]:
                if ep["matched"]!=ep["hall_cardinality"]:oracle_ok=False
                if ep["matched"]!=7:all_matched=False
                assert ep["cached_entries"]<=9
    heldout=[groups[s] for s in range(76,80)]
    identity_savings=[g[1]["recovery_baseline_drift"]-
                      g[2]["recovery_baseline_drift"] for g in heldout]
    churn_savings=[g[1]["recovery_churn"]-
                   g[2]["recovery_churn"] for g in heldout]
    if not unique or not oracle_ok:
        label="INVALID"
    elif not all_matched:
        label="GEOMETRY_DEFICIENCY"
    elif (sum(identity_savings)>0 and all(s>=0 for s in identity_savings)
          and sum(churn_savings)>=0):
        label="STICKY_RESTORES_BASELINE"
    elif sum(identity_savings)>0 and sum(churn_savings)<0:
        label="STICKY_TRADEOFF"
    elif sum(identity_savings)<0:
        label="STICKY_HARM"
    else:
        label="NO_BENEFIT"
    return {
        "schema":"yggdrasil.y034-sticky-memory.v1",
        "predecessor_head":"4051a585bd41ff9d88aceee57f548ff5fce5dcd6",
        "classification":label,
        "unique_signatures":unique,"all_seven_matched":all_matched,
        "hall_oracle_agrees":oracle_ok,
        "geometry_signatures":signatures,
        "heldout_sticky_baseline_savings_vs_recent":identity_savings,
        "heldout_sticky_churn_savings_vs_recent":churn_savings,
        "heldout_recovery_baseline_drift_by_arm":{
            arm:sum(g[i]["recovery_baseline_drift"] for g in heldout)
            for i,arm in enumerate(ARMS)
        },
        "heldout_recovery_churn_by_arm":{
            arm:sum(g[i]["recovery_churn"] for g in heldout)
            for i,arm in enumerate(ARMS)
        },
        "heldout_cache_writes_by_arm":{
            arm:sum(g[i]["total_writes"] for g in heldout)
            for i,arm in enumerate(ARMS)
        },
        "rows":rows,"model_calls":0,
        "scope":"Nine-slot synthetic sticky assignment cache, no semantic restoration claim"
    }


if __name__=="__main__":
    result=run()
    assert result==run()
    print(json.dumps(result,sort_keys=True,indent=2))
