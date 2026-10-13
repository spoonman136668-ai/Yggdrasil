"""Y037: frozen assignment-churn versus search-cost Pareto portfolio."""
import importlib.util
import json
from pathlib import Path

SRC=Path(__file__).resolve().parent.parent/"20261013-y036-novel-shifts"/"execute.py"
spec=importlib.util.spec_from_file_location("y036_frozen",SRC)
assert spec and spec.loader
y36=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y36)

DEVELOPMENT=tuple(range(224,232))
HELDOUT=tuple(range(232,248))
REGIMES=y36.REGIMES
POLICIES=y36.POLICIES


def compare(regime):
    rows=[]
    for seed in DEVELOPMENT+HELDOUT:
        outcomes={p:y36.evaluate(seed,regime,p) for p in POLICIES}
        sham=outcomes["matched_sham"]
        for result in outcomes.values():
            assert result["cache_writes"]==sham["cache_writes"]
            for a,b in zip(sham["episodes"],result["episodes"]):
                assert a["cache_writes"]==b["cache_writes"]
                assert a["cached_keys"]==b["cached_keys"]
                assert a["matched"]==b["matched"]==7
        rows.append({"seed":seed,"cohort":"development" if seed in DEVELOPMENT else "heldout",
                     "churn":{p:x["churn"] for p,x in outcomes.items()},
                     "calls":{p:x["search_calls"] for p,x in outcomes.items()},
                     "preferences":{p:sum(e["applied_preferences"] for e in x["episodes"])
                                    for p,x in outcomes.items()},
                     "paired_writes":sham["cache_writes"]})
    sealed=[r for r in rows if r["cohort"]=="heldout"]
    churn={p:sum(r["churn"][p] for r in sealed) for p in POLICIES}
    calls={p:sum(r["calls"][p] for r in sealed) for p in POLICIES}
    return {"regime":regime,"churn":churn,"matching_search_calls":calls,
            "relative_to_sham_churn_savings":{p:churn["matched_sham"]-churn[p]
                                             for p in POLICIES[1:]},
            "quorum2_minus_full_search_calls":calls["quorum2"]-calls["full"],
            "per_seed":rows}


def run():
    results=[compare(r) for r in REGIMES]
    mapping={x["regime"]:x for x in results}
    any_strict=False
    every=True
    for r in results:
        q2=r["churn"]["quorum2"]
        full=r["churn"]["full"]
        cq2=r["matching_search_calls"]["quorum2"]
        cfull=r["matching_search_calls"]["full"]
        if not (q2<=full and cq2<=cfull):every=False
        if q2<full or cq2<cfull:any_strict=True
    slow=mapping["reference_drift1"]["relative_to_sham_churn_savings"]
    if every and any_strict and slow["quorum2"]>=.7*slow["full"]:
        classification="PARETO_QUORUM2"
    elif any(r["churn"]["quorum2"]<r["churn"]["full"] and
             r["matching_search_calls"]["quorum2"]<r["matching_search_calls"]["full"]
             for r in results):
        classification="TRADEOFF"
    else:
        classification="NOT_PARETO"
    return {"schema":"yggdrasil.y037-search-cost-churn-frontier.v1",
            "parent_head":"0f18249168254a83ca05c987abb01c55d86c0db7",
            "classification":classification,"development_seeds":DEVELOPMENT,
            "sealed_heldout_seeds":HELDOUT,"regimes":results,"model_calls":0,
            "claim_limit":"Finite recursion-call cost proxy only, not wall time or semantic memory"}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
