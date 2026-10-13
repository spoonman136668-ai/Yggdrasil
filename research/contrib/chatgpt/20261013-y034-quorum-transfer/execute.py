"""Y034: unseen geometry-regime zero-retuning test of Y033 cache quorum."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PRIOR = Path(__file__).resolve().parent.parent / "20261013-y033-quorum" / "execute.py"
_spec=importlib.util.spec_from_file_location("y033_frozen",PRIOR)
assert _spec and _spec.loader
y33=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(y33)
y25=y33.y25

DEVELOPMENT=tuple(range(152,160))
HELDOUT=tuple(range(160,176))
REGIMES=("drift1","drift2","drift4","late_shock")
POLICIES=y33.POLICIES
LATE_SHOCK=(0,1,2,3,8,13,14,15)


def neighborhoods(seed,episode,active,regime):
    if regime=="late_shock":
        displacement=LATE_SHOCK[episode]
    else:
        assert regime in ("drift1","drift2","drift4")
        displacement=int(regime[-1])*episode
    homes={key:(7*key+seed+displacement)%16 for key in active}
    for key in active[1:4]:
        homes[key]=homes[active[0]]
    return {key:{(home+delta)%16 for delta in range(-2,3)}
            for key,home in homes.items()}


def evaluate(seed,regime,policy):
    cache=OrderedDict()
    previous_active=set()
    previous_assignment={}
    evaluator_history={}
    rows=[]
    for episode in range(8):
        active=y25.active_keys(seed,episode)
        adjacency=neighborhoods(seed,episode,active,regime)
        assert y25.hall_cardinality(active,adjacency)==7
        legal={key:cache[key] for key in active
               if key in cache and cache[key] in adjacency[key]}
        minimum={"matched_sham":999,"full":1,"quorum2":2,"quorum3":3}[policy]
        preferred=legal if len(legal)>=minimum else {}
        matched,calls=y25.match(active,adjacency,preferred)
        assert len(matched)==7 and len(set(matched.values()))==7
        returning=[key for key in active if key in evaluator_history]
        churn=sum(matched[key]!=evaluator_history[key] for key in returning)
        for key in active:
            evaluator_history[key]=matched[key]
        for key in active:cache.pop(key,None)
        writes=0
        for key in sorted(previous_active.difference(active)):
            cache.pop(key,None)
            cache[key]=previous_assignment[key]
            writes+=1
            while len(cache)>9:cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+7<=16
        assert not set(active).intersection(cache)
        previous_active=set(active)
        previous_assignment=matched
        rows.append({"episode":episode,"churn":churn,"search_calls":calls,
                     "writes":writes,"cache_keys":list(cache),
                     "legal_count":len(legal),"applied_count":len(preferred),
                     "matched":len(matched)})
    return {"seed":seed,"churn":sum(x["churn"] for x in rows),
            "search_calls":sum(x["search_calls"] for x in rows),
            "cache_writes":sum(x["writes"] for x in rows),
            "applied_preferences":sum(x["applied_count"] for x in rows),
            "episodes":rows}


def regime_result(regime):
    results=[]
    for seed in DEVELOPMENT+HELDOUT:
        arms={p:evaluate(seed,regime,p) for p in POLICIES}
        control=arms["matched_sham"]
        for arm in arms.values():
            assert control["cache_writes"]==arm["cache_writes"]
            for a,b in zip(control["episodes"],arm["episodes"]):
                assert a["writes"]==b["writes"]
                assert a["cache_keys"]==b["cache_keys"]
                assert a["matched"]==b["matched"]==7
        results.append({"seed":seed,
                        "cohort":"development" if seed in DEVELOPMENT else "heldout",
                        "churn":{p:r["churn"] for p,r in arms.items()},
                        "search_calls":{p:r["search_calls"] for p,r in arms.items()},
                        "preferences":{p:r["applied_preferences"] for p,r in arms.items()},
                        "paired_cache_writes":control["cache_writes"]})
    sealed=[r for r in results if r["cohort"]=="heldout"]
    churn={p:sum(r["churn"][p] for r in sealed) for p in POLICIES}
    return {"regime":regime,"heldout_churn":churn,
            "sham_relative_savings":{p:churn["matched_sham"]-churn[p] for p in POLICIES[1:]},
            "heldout_preferences":{p:sum(r["preferences"][p] for r in sealed) for p in POLICIES},
            "seed_rows":results}


def run():
    rows=[regime_result(r) for r in REGIMES]
    mapping={r["regime"]:r for r in rows}
    novel=("drift2","drift4","late_shock")
    improved=[mapping[r]["heldout_churn"]["quorum2"]<
              mapping[r]["heldout_churn"]["full"] for r in novel]
    no_worse=[mapping[r]["heldout_churn"]["quorum2"]<=
              mapping[r]["heldout_churn"]["full"] for r in novel]
    slow=mapping["drift1"]["sham_relative_savings"]
    if all(no_worse) and any(improved) and slow["quorum2"]>=.7*slow["full"]:
        label="QUORUM_ROBUST"
    elif any(improved):
        label="MIXED"
    else:
        label="NO_TRANSFER"
    return {"schema":"yggdrasil.y034-new-regime-quorum-transfer.v1",
            "parent_head":"779a617a61428360ac3614e7a241ccc4176fd42f",
            "classification":label,"development_seeds":DEVELOPMENT,
            "sealed_heldout_seeds":HELDOUT,"regimes":rows,
            "model_calls":0,
            "claim_limit":"Synthetic fixed-quorum transfer to new geometric schedules"}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
