"""Y037: fixed legal singleton cache fallback, no future state."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

SRC=Path(__file__).resolve().parent.parent/"20261013-y036-rank"/"execute.py"
spec=importlib.util.spec_from_file_location("y36_frozen",SRC)
assert spec and spec.loader
y36=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y36)
y34=y36.y34
y25=y36.y25

DEVELOPMENT=tuple(range(224,232))
HELDOUT=tuple(range(232,248))
REGIMES=y34.REGIMES
POLICIES=("matched_sham","full","quorum2","fallback6","fallback5")


def evaluate(seed,regime,policy):
    cache=OrderedDict()
    previous_active=set()
    previous_allocation={}
    evaluator_history={}
    episodes=[]
    for episode in range(8):
        active=y25.active_keys(seed,episode)
        neighbors=y34.neighborhoods(seed,episode,active,regime)
        assert y25.hall_cardinality(active,neighbors)==7
        legal={key:cache[key] for key in active if key in cache
               and cache[key] in neighbors[key]}
        if policy=="matched_sham":
            preferred={}
        elif policy=="full":
            preferred=legal
        elif policy=="quorum2":
            preferred=legal if len(legal)>=2 else {}
        elif len(legal)>=2:
            preferred=legal
        elif len(legal)==1:
            cutoff=6 if policy=="fallback6" else 5
            cell=next(iter(legal.values()))
            degree=sum(cell in neighbors[key] for key in active)
            preferred=legal if degree<=cutoff else {}
        else:
            preferred={}
        assignments,calls=y25.match(active,neighbors,preferred)
        assert len(assignments)==7 and len(set(assignments.values()))==7
        returning=[k for k in active if k in evaluator_history]
        churn=sum(assignments[k]!=evaluator_history[k] for k in returning)
        for k in active:
            evaluator_history[k]=assignments[k]
        for k in active:
            cache.pop(k,None)
        writes=0
        for k in sorted(previous_active.difference(active)):
            cache.pop(k,None)
            cache[k]=previous_allocation[k]
            writes+=1
            while len(cache)>9:
                cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+7<=16
        assert not set(cache).intersection(active)
        previous_active=set(active)
        previous_allocation=assignments
        episodes.append({"episode":episode,"matched":len(assignments),
                         "churn":churn,"search_calls":calls,
                         "writes":writes,"cache_keys":list(cache),
                         "eligible":len(legal),"applied":len(preferred)})
    return {"seed":seed,"churn":sum(x["churn"] for x in episodes),
            "search_calls":sum(x["search_calls"] for x in episodes),
            "cache_writes":sum(x["writes"] for x in episodes),
            "applied_preferences":sum(x["applied"] for x in episodes),
            "episodes":episodes}


def regime_result(regime):
    rows=[]
    for seed in DEVELOPMENT+HELDOUT:
        arms={p:evaluate(seed,regime,p) for p in POLICIES}
        control=arms["matched_sham"]
        for outcome in arms.values():
            assert control["cache_writes"]==outcome["cache_writes"]
            for a,b in zip(control["episodes"],outcome["episodes"]):
                assert a["writes"]==b["writes"]
                assert a["cache_keys"]==b["cache_keys"]
                assert a["matched"]==b["matched"]==7
        rows.append({"seed":seed,"cohort":"development" if seed in DEVELOPMENT else "heldout",
                     "churn":{p:v["churn"] for p,v in arms.items()},
                     "search_calls":{p:v["search_calls"] for p,v in arms.items()},
                     "preferences":{p:v["applied_preferences"] for p,v in arms.items()},
                     "paired_cache_writes":control["cache_writes"]})
    heldout=[x for x in rows if x["cohort"]=="heldout"]
    total={p:sum(x["churn"][p] for x in heldout) for p in POLICIES}
    return {"regime":regime,"heldout_churn":total,
            "sham_relative_savings":{p:total["matched_sham"]-total[p] for p in POLICIES[1:]},
            "seed_rows":rows}


def run():
    rows=[regime_result(r) for r in REGIMES]
    by={r["regime"]:r for r in rows}
    slow=by["drift1"]["sham_relative_savings"]
    no_worse=all(by[regime]["heldout_churn"]["fallback6"]<=
                 by[regime]["heldout_churn"]["quorum2"]
                 for regime in ("drift4","late_shock"))
    strict=any(by[regime]["heldout_churn"]["fallback6"]<
               by[regime]["heldout_churn"]["quorum2"]
               for regime in ("drift4","late_shock"))
    anygain=any(by[regime]["heldout_churn"][p]<
                by[regime]["heldout_churn"]["quorum2"]
                for regime in ("drift4","late_shock")
                for p in ("fallback6","fallback5"))
    if no_worse and strict and slow["fallback6"]>=.7*slow["full"]:
        label="FALLBACK_GAIN"
    elif anygain:
        label="PARTIAL"
    else:
        label="NO_GAIN"
    return {"schema":"yggdrasil.y037-single-legal-fallback.v1",
            "parent_head":"1c9c8ae47af93b3d9819247ddb8ea2b822cd28ed",
            "classification":label,"development_seeds":DEVELOPMENT,
            "sealed_heldout_seeds":HELDOUT,"regimes":rows,
            "model_calls":0,"claim_limit":"Synthetic legal cached singleton policy, no semantic cognition"}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
