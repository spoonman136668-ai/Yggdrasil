"""Y036: preregistered intermediate-degree quorum filter experiment."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PREVIOUS=Path(__file__).resolve().parent.parent/"20261013-y035-interaction"/"execute.py"
_spec=importlib.util.spec_from_file_location("y035_frozen",PREVIOUS)
assert _spec and _spec.loader
y35=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(y35)
y34=y35.y34
y25=y35.y25

DEVELOPMENT=tuple(range(200,208))
HELDOUT=tuple(range(208,224))
REGIMES=y35.REGIMES
POLICIES=("matched_sham","full","quorum2","quorum2_conflict5","quorum2_conflict6")


def evaluate(seed,regime,policy):
    cache=OrderedDict()
    prev_active=set()
    prev_assignment={}
    evaluator_only_history={}
    episodes=[]
    for episode in range(8):
        active=y25.active_keys(seed,episode)
        adjacency=y34.neighborhoods(seed,episode,active,regime)
        assert y25.hall_cardinality(active,adjacency)==7
        legal={key:cache[key] for key in active
               if key in cache and cache[key] in adjacency[key]}
        if policy in ("quorum2_conflict5","quorum2_conflict6"):
            max_degree=5 if policy.endswith("5") else 6
            legal={key:cell for key,cell in legal.items()
                   if sum(cell in adjacency[k] for k in active)<=max_degree}
        minimum={"matched_sham":999,"full":1,"quorum2":2,
                 "quorum2_conflict5":2,"quorum2_conflict6":2}[policy]
        preferred=legal if len(legal)>=minimum else {}
        assigned,calls=y25.match(active,adjacency,preferred)
        assert len(assigned)==7 and len(set(assigned.values()))==7
        returning=[key for key in active if key in evaluator_only_history]
        churn=sum(assigned[key]!=evaluator_only_history[key] for key in returning)
        for key in active:
            evaluator_only_history[key]=assigned[key]
        for key in active:cache.pop(key,None)
        writes=0
        for key in sorted(prev_active.difference(active)):
            cache.pop(key,None)
            cache[key]=prev_assignment[key]
            writes+=1
            while len(cache)>9:cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+7<=16 and not set(cache).intersection(active)
        prev_active=set(active)
        prev_assignment=assigned
        episodes.append({"episode":episode,"assigned":len(assigned),"churn":churn,
                         "calls":calls,"writes":writes,"cache_keys":list(cache),
                         "preferences":len(preferred)})
    return {"seed":seed,"churn":sum(e["churn"] for e in episodes),
            "search_calls":sum(e["calls"] for e in episodes),
            "cache_writes":sum(e["writes"] for e in episodes),
            "used_preferences":sum(e["preferences"] for e in episodes),
            "episodes":episodes}


def regime_result(regime):
    rows=[]
    for seed in DEVELOPMENT+HELDOUT:
        policies={p:evaluate(seed,regime,p) for p in POLICIES}
        control=policies["matched_sham"]
        for arm in policies.values():
            assert control["cache_writes"]==arm["cache_writes"]
            for a,b in zip(control["episodes"],arm["episodes"]):
                assert a["writes"]==b["writes"]
                assert a["cache_keys"]==b["cache_keys"]
                assert a["assigned"]==b["assigned"]==7
        rows.append({"seed":seed,"cohort":"development" if seed in DEVELOPMENT else "heldout",
                     "churn":{p:v["churn"] for p,v in policies.items()},
                     "search_calls":{p:v["search_calls"] for p,v in policies.items()},
                     "preferences":{p:v["used_preferences"] for p,v in policies.items()},
                     "matched_cache_writes":control["cache_writes"]})
    sealed=[r for r in rows if r["cohort"]=="heldout"]
    totals={p:sum(r["churn"][p] for r in sealed) for p in POLICIES}
    return {"regime":regime,"heldout_churn":totals,
            "sham_relative_savings":{p:totals["matched_sham"]-totals[p] for p in POLICIES[1:]},
            "heldout_preferences":{p:sum(r["preferences"][p] for r in sealed) for p in POLICIES},
            "seed_rows":rows}


def run():
    rows=[regime_result(r) for r in REGIMES]
    by={r["regime"]:r for r in rows}
    gains={policy:{
        regime:by[regime]["heldout_churn"][policy]<
               by[regime]["heldout_churn"]["quorum2"]
        for regime in ("drift4","late_shock")}
        for policy in ("quorum2_conflict5","quorum2_conflict6")}
    slow=by["drift1"]["sham_relative_savings"]
    if any(all(g.values()) and slow[p]>=.7*slow["full"] for p,g in gains.items()):
        classification="INTERMEDIATE_GATE_GAIN"
    elif any(any(g.values()) for g in gains.values()):
        classification="PARTIAL"
    else:
        classification="NO_GAIN"
    return {"schema":"yggdrasil.y036-intermediate-conflict-quorum.v1",
            "parent_head":"35eace118e16ab8195a6810f2bc6ec569dfd0106",
            "classification":classification,
            "development_seeds":DEVELOPMENT,"heldout_seeds":HELDOUT,
            "regimes":rows,"model_calls":0,
            "claim_limit":"Synthetic bounded cache-degree preference gating only"}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
