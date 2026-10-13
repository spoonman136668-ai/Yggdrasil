"""Y036: rank observed legal cache preferences by current graph conflict."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

SRC=Path(__file__).resolve().parent.parent/"20261013-y035-interaction"/"execute.py"
spec=importlib.util.spec_from_file_location("y35_frozen",SRC)
assert spec and spec.loader
y35=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y35)
y34=y35.y34
y25=y35.y25

DEVELOPMENT=tuple(range(200,208))
HELDOUT=tuple(range(208,224))
REGIMES=y34.REGIMES
POLICIES=("matched_sham","full","quorum2","rank_low_conflict2","rank_low_conflict3")


def evaluate(seed,regime,policy):
    cache=OrderedDict()
    last_active=set()
    last_assignment={}
    evaluator_history={}
    episodes=[]
    for episode in range(8):
        active=y25.active_keys(seed,episode)
        neighbors=y34.neighborhoods(seed,episode,active,regime)
        assert y25.hall_cardinality(active,neighbors)==7
        legal={key:cache[key] for key in active
               if key in cache and cache[key] in neighbors[key]}
        if policy=="matched_sham":
            preferred={}
        elif policy=="full":
            preferred=legal
        elif policy=="quorum2":
            preferred=legal if len(legal)>=2 else {}
        else:
            selected=2 if policy=="rank_low_conflict2" else 3
            if len(legal)<selected:
                preferred={}
            else:
                degree=lambda cell:sum(cell in neighbors[key] for key in active)
                ranked=sorted(legal.items(),key=lambda item:(degree(item[1]),item[0]))
                preferred=dict(ranked[:selected])
        assigned,calls=y25.match(active,neighbors,preferred)
        assert len(assigned)==7 and len(set(assigned.values()))==7
        returning=[k for k in active if k in evaluator_history]
        churn=sum(assigned[k]!=evaluator_history[k] for k in returning)
        for k in active:
            evaluator_history[k]=assigned[k]
        for k in active:
            cache.pop(k,None)
        writes=0
        for k in sorted(last_active.difference(active)):
            cache.pop(k,None)
            cache[k]=last_assignment[k]
            writes+=1
            while len(cache)>9:
                cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+7<=16
        assert not set(cache).intersection(active)
        last_active=set(active)
        last_assignment=assigned
        episodes.append({"episode":episode,"matched":len(assigned),
                         "churn":churn,"calls":calls,
                         "cache_writes":writes,"cached_keys":list(cache),
                         "legal_count":len(legal),"preferred_count":len(preferred)})
    return {"seed":seed,"churn":sum(x["churn"] for x in episodes),
            "calls":sum(x["calls"] for x in episodes),
            "writes":sum(x["cache_writes"] for x in episodes),
            "used_preferences":sum(x["preferred_count"] for x in episodes),
            "episodes":episodes}


def regime_result(regime):
    rows=[]
    for seed in DEVELOPMENT+HELDOUT:
        policy_results={p:evaluate(seed,regime,p) for p in POLICIES}
        sham=policy_results["matched_sham"]
        for p,outcome in policy_results.items():
            assert sham["writes"]==outcome["writes"]
            for a,b in zip(sham["episodes"],outcome["episodes"]):
                assert a["cache_writes"]==b["cache_writes"]
                assert a["cached_keys"]==b["cached_keys"]
                assert a["matched"]==b["matched"]==7
        rows.append({"seed":seed,
                     "cohort":"development" if seed in DEVELOPMENT else "heldout",
                     "churn":{p:v["churn"] for p,v in policy_results.items()},
                     "search_calls":{p:v["calls"] for p,v in policy_results.items()},
                     "preferences":{p:v["used_preferences"] for p,v in policy_results.items()},
                     "paired_cache_writes":sham["writes"]})
    heldout=[r for r in rows if r["cohort"]=="heldout"]
    totals={p:sum(r["churn"][p] for r in heldout) for p in POLICIES}
    return {"regime":regime,"heldout_churn":totals,
            "sham_relative_savings":{p:totals["matched_sham"]-totals[p]
                                      for p in POLICIES[1:]},
            "seed_rows":rows}


def run():
    results=[regime_result(r) for r in REGIMES]
    by={r["regime"]:r for r in results}
    slow=by["drift1"]["sham_relative_savings"]
    rank2="rank_low_conflict2"
    no_worse=all(by[r]["heldout_churn"][rank2]<=by[r]["heldout_churn"]["quorum2"]
                 for r in ("drift4","late_shock"))
    at_least_one=any(by[r]["heldout_churn"][rank2]<by[r]["heldout_churn"]["quorum2"]
                     for r in ("drift4","late_shock"))
    some_improvement=any(
        by[r]["heldout_churn"][p]<by[r]["heldout_churn"]["quorum2"]
        for r in ("drift4","late_shock")
        for p in ("rank_low_conflict2","rank_low_conflict3"))
    if no_worse and at_least_one and slow[rank2]>=.7*slow["full"]:
        classification="RANKED_GAIN"
    elif some_improvement:
        classification="PARTIAL"
    else:
        classification="NO_GAIN"
    return {"schema":"yggdrasil.y036-fixed-rank-preference.v1",
            "parent_head":"35eace118e16ab8195a6810f2bc6ec569dfd0106",
            "classification":classification,"development_seeds":DEVELOPMENT,
            "sealed_heldout_seeds":HELDOUT,"regimes":results,"model_calls":0,
            "claim_limit":"Synthetic current graph preference rank, no learned semantics"}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
