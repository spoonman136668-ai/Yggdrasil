"""Y035: frozen joint cache quorum and current-graph conflict exclusion."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PREVIOUS = Path(__file__).resolve().parent.parent / "20261013-y034-quorum-transfer" / "execute.py"
_spec = importlib.util.spec_from_file_location("y034_frozen",PREVIOUS)
assert _spec and _spec.loader
y34=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(y34)
y25=y34.y25

DEVELOPMENT=tuple(range(176,184))
HELDOUT=tuple(range(184,200))
REGIMES=y34.REGIMES
POLICIES=("matched_sham","full","quorum2","quorum2_conflict4")


def evaluate(seed,regime,policy):
    cache=OrderedDict()
    previous_active=set()
    previous_assignment={}
    evaluator_history={}
    episodes=[]
    for episode in range(8):
        active=y25.active_keys(seed,episode)
        neighbors=y34.neighborhoods(seed,episode,active,regime)
        assert y25.hall_cardinality(active,neighbors)==7
        legal={key:cache[key] for key in active if key in cache and cache[key] in neighbors[key]}
        if policy=="quorum2_conflict4":
            legal={key:cell for key,cell in legal.items()
                   if sum(cell in neighbors[k] for k in active)<=4}
        quorum={"matched_sham":999,"full":1,"quorum2":2,"quorum2_conflict4":2}[policy]
        preferences=legal if len(legal)>=quorum else {}
        assigned,calls=y25.match(active,neighbors,preferences)
        assert len(assigned)==7 and len(set(assigned.values()))==7
        returning=[key for key in active if key in evaluator_history]
        churn=sum(assigned[key]!=evaluator_history[key] for key in returning)
        for key in active:evaluator_history[key]=assigned[key]
        for key in active:cache.pop(key,None)
        writes=0
        for key in sorted(previous_active.difference(active)):
            cache.pop(key,None)
            cache[key]=previous_assignment[key]
            writes+=1
            while len(cache)>9:cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+7<=16 and not set(cache).intersection(active)
        previous_active=set(active)
        previous_assignment=assigned
        episodes.append({"episode":episode,"churn":churn,"calls":calls,
                         "writes":writes,"cache_keys":list(cache),
                         "preferences":len(preferences),"matched":len(assigned)})
    return {"seed":seed,"churn":sum(x["churn"] for x in episodes),
            "search_calls":sum(x["calls"] for x in episodes),
            "cache_writes":sum(x["writes"] for x in episodes),
            "used_preferences":sum(x["preferences"] for x in episodes),
            "episodes":episodes}


def regime_result(regime):
    rows=[]
    for seed in DEVELOPMENT+HELDOUT:
        results={p:evaluate(seed,regime,p) for p in POLICIES}
        control=results["matched_sham"]
        for a in results.values():
            assert control["cache_writes"]==a["cache_writes"]
            for l,r in zip(control["episodes"],a["episodes"]):
                assert l["cache_keys"]==r["cache_keys"]
                assert l["writes"]==r["writes"]
                assert l["matched"]==r["matched"]==7
        rows.append({"seed":seed,"cohort":"development" if seed in DEVELOPMENT else "heldout",
                     "churn":{p:r["churn"] for p,r in results.items()},
                     "search_calls":{p:r["search_calls"] for p,r in results.items()},
                     "preferences":{p:r["used_preferences"] for p,r in results.items()},
                     "matched_cache_writes":control["cache_writes"]})
    heldout=[x for x in rows if x["cohort"]=="heldout"]
    churn={p:sum(x["churn"][p] for x in heldout) for p in POLICIES}
    return {"regime":regime,"heldout_churn":churn,
            "sham_relative_savings":{p:churn["matched_sham"]-churn[p] for p in POLICIES[1:]},
            "heldout_preferences":{p:sum(x["preferences"][p] for x in heldout) for p in POLICIES},
            "seed_rows":rows}


def run():
    rows=[regime_result(r) for r in REGIMES]
    m={x["regime"]:x for x in rows}
    c="quorum2_conflict4"
    improved={r:m[r]["heldout_churn"][c]<m[r]["heldout_churn"]["quorum2"]
              for r in ("drift4","late_shock")}
    slow=m["drift1"]["sham_relative_savings"]
    if all(improved.values()) and slow[c]>=.7*slow["full"]:
        label="COMPOSITE_GAIN"
    elif any(improved.values()):
        label="PARTIAL"
    else:
        label="NO_GAIN"
    return {"schema":"yggdrasil.y035-quorum-conflict-interaction.v1",
            "parent_head":"bd5fafd596f2227a42376d55ff6be8ee3a8ea6e3",
            "classification":label,"development_seeds":DEVELOPMENT,
            "sealed_heldout_seeds":HELDOUT,"regimes":rows,
            "model_calls":0,"claim_limit":"Synthetic fixed-quorum conflict gating only"}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
