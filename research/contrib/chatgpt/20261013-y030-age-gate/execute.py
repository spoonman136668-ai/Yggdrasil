"""Y030: frozen observed-age gating ablation under nonstationary environments."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

SRC=Path(__file__).resolve().parent.parent/"20261013-y029-frontier"/"execute.py"
spec=importlib.util.spec_from_file_location("y029_frozen",SRC)
assert spec and spec.loader
y29=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y29)
y25=y29.y25

DEVELOPMENT_SEEDS=tuple(range(56,64))
HELDOUT_SEEDS=tuple(range(64,80))
REGIMES=("drift1","drift3","drift5","alternating")
POLICIES=("matched_sham","full_cache","age2_cache","age4_cache")


def run_policy(seed,regime,policy):
    cache=OrderedDict()
    previous_active=set()
    previous_assignment={}
    evaluator_history={}
    episodes=[]
    for episode in range(8):
        active=y25.active_keys(seed,episode)
        adjacency=y29.neighbors(seed,episode,active,regime)
        assert y25.hall_cardinality(active,adjacency)==7
        limit=(2 if policy=="age2_cache" else
               4 if policy=="age4_cache" else None)
        pref={}
        if policy!="matched_sham":
            pref={key:cell
                  for key,(cell,last_seen) in cache.items()
                  if key in active and (limit is None or episode-last_seen<=limit)}
        legal={k:c for k,c in pref.items() if c in adjacency[k]}
        assigned,calls=y25.match(active,adjacency,pref)
        assert len(assigned)==7 and len(set(assigned.values()))==7
        returning=[key for key in active if key in evaluator_history]
        churn=sum(assigned[key]!=evaluator_history[key] for key in returning)
        for key in active:
            evaluator_history[key]=assigned[key]
        for key in active:
            cache.pop(key,None)
        writes=0
        for key in sorted(previous_active.difference(active)):
            cache.pop(key,None)
            cache[key]=(previous_assignment[key],episode-1)
            writes+=1
            while len(cache)>9:
                cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+7<=16
        assert not set(cache).intersection(active)
        previous_active=set(active)
        previous_assignment=assigned
        episodes.append({
            "episode":episode,"churn":churn,"calls":calls,
            "writes":writes,"cached_keys":list(cache),
            "cached_ages":[(k,t) for k,(_,t) in cache.items()],
            "legal_preferences":len(legal),
            "matched":len(assigned)
        })
    return {"seed":seed,"churn":sum(x["churn"] for x in episodes),
            "search_calls":sum(x["calls"] for x in episodes),
            "cache_writes":sum(x["writes"] for x in episodes),
            "legal_preferences":sum(x["legal_preferences"] for x in episodes),
            "episodes":episodes}


def run_regime(regime):
    all_results=[]
    for seed in DEVELOPMENT_SEEDS+HELDOUT_SEEDS:
        arms={policy:run_policy(seed,regime,policy) for policy in POLICIES}
        control=arms["matched_sham"]
        for policy in POLICIES[1:]:
            other=arms[policy]
            assert control["cache_writes"]==other["cache_writes"]
            for a,b in zip(control["episodes"],other["episodes"]):
                assert a["writes"]==b["writes"]
                assert a["cached_keys"]==b["cached_keys"]
                assert a["cached_ages"]==b["cached_ages"]
                assert a["matched"]==b["matched"]==7
        all_results.append({
            "seed":seed,"cohort":"development" if seed in DEVELOPMENT_SEEDS else "heldout",
            "policy_churn":{policy:arm["churn"] for policy,arm in arms.items()},
            "legal_preference_counts":{policy:arm["legal_preferences"] for policy,arm in arms.items()},
            "paired_cache_writes":control["cache_writes"],
            "policy_search_calls":{policy:arm["search_calls"] for policy,arm in arms.items()},
            "policy_episode_churn":{policy:[e["churn"] for e in arm["episodes"]] for policy,arm in arms.items()}
        })
    heldout=[r for r in all_results if r["cohort"]=="heldout"]
    totals={policy:sum(s["policy_churn"][policy] for s in heldout)
            for policy in POLICIES}
    savings={policy:totals["matched_sham"]-totals[policy] for policy in POLICIES[1:]}
    return {"regime":regime,"total_heldout_churn":totals,
            "sham_relative_savings":savings,
            "legal_preferences":{p:sum(s["legal_preference_counts"][p] for s in heldout)
                                 for p in POLICIES},
            "seed_results":all_results}


def run():
    rows=[run_regime(regime) for regime in REGIMES]
    result={row["regime"]:row for row in rows}
    age2=result["drift1"]["sham_relative_savings"]["age2_cache"]
    full=result["drift1"]["sham_relative_savings"]["full_cache"]
    harm_regime_improvement=[
        result[regime]["total_heldout_churn"]["age2_cache"]<
        result[regime]["total_heldout_churn"]["full_cache"]
        for regime in ("drift5","alternating")]
    if all(harm_regime_improvement) and age2>=0.75*full:
        classification="GATING_BENEFIT"
    elif any(harm_regime_improvement):
        classification="TRADEOFF"
    else:
        classification="NO_GATING_BENEFIT"
    return {"schema":"yggdrasil.y030-age-gated-memory.v1",
            "parent_head":"0fa63655436e4f6da528fcd5a82a23383b5ee66f",
            "classification":classification,
            "development_seeds":DEVELOPMENT_SEEDS,"heldout_seeds":HELDOUT_SEEDS,
            "regimes":rows,"model_calls":0,
            "claim_limit":"Synthetic bounded observed assignment age gating; no learned semantics"}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
