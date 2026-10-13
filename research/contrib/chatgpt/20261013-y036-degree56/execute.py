"""Y036: frozen degree-five/six limited quorum under present graph."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

SRC=Path(__file__).resolve().parent.parent/"20261013-y035-interaction"/"execute.py"
spec=importlib.util.spec_from_file_location("y035_frozen",SRC)
assert spec and spec.loader
y35=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y35)
y34=y35.y34
y25=y35.y25

DEV=tuple(range(200,208))
HELDOUT=tuple(range(208,224))
REGIMES=("drift1","drift2","drift4","late_shock")
POLICIES=("matched_sham","full","quorum2","quorum2_degree5","quorum2_degree6")


def evaluate(seed,regime,policy):
    cache=OrderedDict()
    previous_active=set()
    previous_assignment={}
    evaluator_history={}
    episodes=[]
    for episode in range(8):
        active=y25.active_keys(seed,episode)
        graph=y34.neighborhoods(seed,episode,active,regime)
        assert y25.hall_cardinality(active,graph)==7
        legal={key:cache[key] for key in active
               if key in cache and cache[key] in graph[key]}
        hist={degree:0 for degree in range(1,8)}
        degrees={}
        for key,cell in legal.items():
            degree=sum(cell in graph[other] for other in active)
            assert 1<=degree<=7
            hist[degree]+=1
            degrees[key]=degree
        if policy=="matched_sham":
            pref={}
        elif policy=="full":
            pref=legal
        elif policy=="quorum2":
            pref=legal if len(legal)>=2 else {}
        else:
            threshold=5 if policy=="quorum2_degree5" else 6
            assert policy in ("quorum2_degree5","quorum2_degree6")
            eligible={k:c for k,c in legal.items() if degrees[k]<=threshold}
            pref=eligible if len(eligible)>=2 else {}
        matched,calls=y25.match(active,graph,pref)
        assert len(matched)==7 and len(set(matched.values()))==7
        returning=[key for key in active if key in evaluator_history]
        churn=sum(matched[k]!=evaluator_history[k] for k in returning)
        for key in active:evaluator_history[key]=matched[key]
        for key in active:cache.pop(key,None)
        writes=0
        for key in sorted(previous_active.difference(active)):
            cache.pop(key,None)
            cache[key]=previous_assignment[key]
            writes+=1
            while len(cache)>9:cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+7<=16
        assert not set(cache).intersection(active)
        previous_active=set(active)
        previous_assignment=matched
        episodes.append({"episode":episode,"churn":churn,"search_calls":calls,
                         "writes":writes,"cache_keys":list(cache),
                         "legal_count":len(legal),"applied":len(pref),
                         "legal_candidate_degree_histogram":hist,
                         "matched":len(matched)})
    totals={degree:sum(r["legal_candidate_degree_histogram"][degree]
                       for r in episodes) for degree in range(1,8)}
    return {"seed":seed,"churn":sum(r["churn"] for r in episodes),
            "search_calls":sum(r["search_calls"] for r in episodes),
            "writes":sum(r["writes"] for r in episodes),
            "preferred":sum(r["applied"] for r in episodes),
            "degrees":totals,"episodes":episodes}


def regime_result(regime):
    rows=[]
    for seed in DEV+HELDOUT:
        arms={p:evaluate(seed,regime,p) for p in POLICIES}
        sham=arms["matched_sham"]
        for arm in arms.values():
            assert sham["writes"]==arm["writes"]
            for a,b in zip(sham["episodes"],arm["episodes"]):
                assert a["writes"]==b["writes"]
                assert a["cache_keys"]==b["cache_keys"]
                assert a["matched"]==b["matched"]==7
        rows.append({"seed":seed,"cohort":"development" if seed in DEV else "heldout",
                     "churn":{p:r["churn"] for p,r in arms.items()},
                     "calls":{p:r["search_calls"] for p,r in arms.items()},
                     "preferences":{p:r["preferred"] for p,r in arms.items()},
                     "degree_histogram":{p:r["degrees"] for p,r in arms.items()},
                     "write_matched":sham["writes"]})
    heldout=[r for r in rows if r["cohort"]=="heldout"]
    totals={p:sum(r["churn"][p] for r in heldout) for p in POLICIES}
    aggregate_degrees={p:{degree:sum(r["degree_histogram"][p][degree]
                                     for r in heldout) for degree in range(1,8)}
                       for p in POLICIES}
    return {"regime":regime,"heldout_churn":totals,
            "sham_relative_savings":{p:totals["matched_sham"]-totals[p]
                                     for p in POLICIES[1:]},
            "heldout_degree_histogram":aggregate_degrees,
            "heldout_preferences":{p:sum(r["preferences"][p] for r in heldout)
                                   for p in POLICIES},
            "seed_rows":rows}


def run():
    rows=[regime_result(regime) for regime in REGIMES]
    r={x["regime"]:x for x in rows}
    slow=r["drift1"]["sham_relative_savings"]
    better={regime:{p:r[regime]["heldout_churn"][p]<
                      r[regime]["heldout_churn"]["quorum2"]
                    for p in ("quorum2_degree5","quorum2_degree6")}
            for regime in ("drift4","late_shock")}
    if all(better[regime]["quorum2_degree5"] for regime in better) and \
            slow["quorum2_degree5"]>=.7*slow["full"]:
        label="DEGREED_QUORUM_GAIN"
    elif any(any(values.values()) for values in better.values()):
        label="TRADEOFF"
    else:
        label="NO_GAIN"
    return {"schema":"yggdrasil.y036-quorum-degree-5-6.v1",
            "parent_head":"35eace118e16ab8195a6810f2bc6ec569dfd0106",
            "classification":label,"development_seeds":DEV,"heldout_seeds":HELDOUT,
            "regimes":rows,"model_calls":0,
            "claim_limit":"Synthetic present-graph cache preference selection only"}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
