"""Y032 frozen conflict-degree 3/4 gating against retention-induced churn."""
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

DEV=tuple(range(104,112))
HELDOUT=tuple(range(112,128))
POLICIES=("matched_sham","full","conflict3","conflict4")
REGIMES=("drift1","drift3","drift5","alternating")


def evaluate(seed,regime,policy):
    cache=OrderedDict()
    previous_active=set()
    previous_assignment={}
    evaluation_history={}
    rows=[]
    for episode in range(8):
        active=y25.active_keys(seed,episode)
        neighbors=y29.neighbors(seed,episode,active,regime)
        assert y25.hall_cardinality(active,neighbors)==7
        preferences={}
        for key in active:
            if policy=="matched_sham" or key not in cache:
                continue
            cell=cache[key]
            if cell not in neighbors[key]:
                continue
            if policy=="conflict3":
                limit=3
            elif policy=="conflict4":
                limit=4
            else:
                limit=7
            degree=sum(cell in neighbors[other] for other in active)
            if degree<=limit:
                preferences[key]=cell
        assignment,calls=y25.match(active,neighbors,preferences)
        assert len(assignment)==7 and len(set(assignment.values()))==7
        returning=[key for key in active if key in evaluation_history]
        churn=sum(assignment[key]!=evaluation_history[key] for key in returning)
        for key in active:evaluation_history[key]=assignment[key]
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
        previous_assignment=assignment
        rows.append({"episode":episode,"churn":churn,"calls":calls,
                     "cache_writes":writes,"cache_keys":list(cache),
                     "preferences":len(preferences),"matched":len(assignment)})
    return {"seed":seed,"churn":sum(r["churn"] for r in rows),
            "calls":sum(r["calls"] for r in rows),
            "writes":sum(r["cache_writes"] for r in rows),
            "preferences":sum(r["preferences"] for r in rows),
            "episodes":rows}


def regime_results(regime):
    seed_rows=[]
    for seed in DEV+HELDOUT:
        arms={p:evaluate(seed,regime,p) for p in POLICIES}
        control=arms["matched_sham"]
        for other in arms.values():
            assert control["writes"]==other["writes"]
            for a,b in zip(control["episodes"],other["episodes"]):
                assert a["cache_writes"]==b["cache_writes"]
                assert a["cache_keys"]==b["cache_keys"]
                assert a["matched"]==b["matched"]==7
        seed_rows.append({
            "seed":seed,"cohort":"development" if seed in DEV else "heldout",
            "churn":{p:x["churn"] for p,x in arms.items()},
            "matching_calls":{p:x["calls"] for p,x in arms.items()},
            "legal_preferences":{p:x["preferences"] for p,x in arms.items()},
            "paired_cache_writes":control["writes"]})
    heldout=[r for r in seed_rows if r["cohort"]=="heldout"]
    totals={p:sum(s["churn"][p] for s in heldout) for p in POLICIES}
    return {
        "regime":regime,"heldout_churn":totals,
        "sham_relative_saving":{p:totals["matched_sham"]-totals[p] for p in POLICIES[1:]},
        "heldout_legal_preferences":{p:sum(s["legal_preferences"][p] for s in heldout)
                                     for p in POLICIES},
        "seed_rows":seed_rows
    }


def run():
    rows=[regime_results(regime) for regime in REGIMES]
    by={r["regime"]:r for r in rows}
    improved_degree3={regime:by[regime]["heldout_churn"]["conflict3"]<
                           by[regime]["heldout_churn"]["full"]
                     for regime in ("drift5","alternating")}
    improved_any={regime:any(
        by[regime]["heldout_churn"][policy]<by[regime]["heldout_churn"]["full"]
        for policy in ("conflict3","conflict4"))
        for regime in ("drift5","alternating")}
    slow=by["drift1"]["sham_relative_saving"]
    if all(improved_degree3.values()) and slow["conflict3"]>=.7*slow["full"]:
        classification="CONFLICT_FRONTIER_GAIN"
    elif any(improved_any.values()):
        classification="TRADEOFF"
    else:
        classification="NO_GAIN"
    return {
        "schema":"yggdrasil.y032-current-conflict-degree-frontier.v1",
        "parent_head":"f9d6f4f042256822968be07f45de3dda56670271",
        "classification":classification,"development_seeds":DEV,"heldout_seeds":HELDOUT,
        "regimes":rows,"model_calls":0,
        "claim_limit":"Synthetic fixed-capacity conflict-degree thresholds, not semantic learning"
    }



if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
