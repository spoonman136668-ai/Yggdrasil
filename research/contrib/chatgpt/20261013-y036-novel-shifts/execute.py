"""Y036: frozen independently generated global shifts of motif neighborhoods."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent/"20261013-y035-interaction"/"execute.py"
_spec=importlib.util.spec_from_file_location("y035_frozen",SOURCE)
assert _spec and _spec.loader
y35=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(y35)
y25=y35.y25

DEVELOPMENT=tuple(range(200,208))
HELDOUT=tuple(range(208,224))
REGIMES=("reference_drift1","zigzag","shock_recover","xorshift_global")
POLICIES=("matched_sham","full","quorum2","quorum3")
MASK=0xffffffff
ZIGZAG=(0,3,1,4,2,5,3,6)
SHOCK=(0,1,7,8,9,3,4,5)


def displacement(seed,episode,regime):
    if regime=="reference_drift1":
        return episode
    if regime=="zigzag":
        return ZIGZAG[episode]
    if regime=="shock_recover":
        return SHOCK[episode]
    assert regime=="xorshift_global"
    state=(((seed+1)*0x9e3779b1)^((episode+1)*0x85ebca77))&MASK
    state ^= (state<<13)&MASK
    state &= MASK
    state ^= state>>17
    state &= MASK
    state ^= (state<<5)&MASK
    state &= MASK
    return state%16


def neighbors(seed,episode,active,regime):
    shift=displacement(seed,episode,regime)
    homes={key:(7*key+seed+shift)%16 for key in active}
    for key in active[1:4]:
        homes[key]=homes[active[0]]
    return {key:{(home+delta)%16 for delta in range(-2,3)}
            for key,home in homes.items()}


def evaluate(seed,regime,policy):
    cache=OrderedDict()
    previous_active=set()
    previous_assignment={}
    evaluator_history={}
    episodes=[]
    for ep in range(8):
        active=y25.active_keys(seed,ep)
        adjacency=neighbors(seed,ep,active,regime)
        assert y25.hall_cardinality(active,adjacency)==7
        legal={key:cache[key] for key in active
               if key in cache and cache[key] in adjacency[key]}
        minimum={"matched_sham":999,"full":1,"quorum2":2,"quorum3":3}[policy]
        preferred=legal if len(legal)>=minimum else {}
        matched,calls=y25.match(active,adjacency,preferred)
        assert len(matched)==7 and len(set(matched.values()))==7
        returning=[key for key in active if key in evaluator_history]
        churn=sum(matched[key]!=evaluator_history[key] for key in returning)
        for key in active:evaluator_history[key]=matched[key]
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
        episodes.append({"episode":ep,"displacement":displacement(seed,ep,regime),
                         "churn":churn,"search_calls":calls,"cache_writes":writes,
                         "cached_keys":list(cache),"legal_candidates":len(legal),
                         "applied_preferences":len(preferred),"matched":len(matched)})
    return {"seed":seed,"churn":sum(e["churn"] for e in episodes),
            "search_calls":sum(e["search_calls"] for e in episodes),
            "cache_writes":sum(e["cache_writes"] for e in episodes),
            "applied_preferences":sum(e["applied_preferences"] for e in episodes),
            "episodes":episodes}


def evaluate_regime(regime):
    seeds=[]
    for seed in DEVELOPMENT+HELDOUT:
        outcomes={policy:evaluate(seed,regime,policy) for policy in POLICIES}
        control=outcomes["matched_sham"]
        for other in outcomes.values():
            assert other["cache_writes"]==control["cache_writes"]
            for a,b in zip(control["episodes"],other["episodes"]):
                assert a["cache_writes"]==b["cache_writes"]
                assert a["cached_keys"]==b["cached_keys"]
                assert a["matched"]==b["matched"]==7
        seeds.append({"seed":seed,"cohort":"development" if seed in DEVELOPMENT else "heldout",
                      "churn":{p:r["churn"] for p,r in outcomes.items()},
                      "search_calls":{p:r["search_calls"] for p,r in outcomes.items()},
                      "preferences":{p:r["applied_preferences"] for p,r in outcomes.items()},
                      "paired_writes":control["cache_writes"]})
    held=[x for x in seeds if x["cohort"]=="heldout"]
    totals={p:sum(x["churn"][p] for x in held) for p in POLICIES}
    return {"regime":regime,"heldout_churn":totals,
            "sham_relative_savings":{p:totals["matched_sham"]-totals[p]
                                     for p in POLICIES[1:]},
            "heldout_preference_counts":{p:sum(x["preferences"][p] for x in held)
                                         for p in POLICIES},
            "seeds":seeds}


def run():
    results=[evaluate_regime(r) for r in REGIMES]
    by={r["regime"]:r for r in results}
    novel=REGIMES[1:]
    improvements=[by[r]["heldout_churn"]["quorum2"]<
                  by[r]["heldout_churn"]["full"] for r in novel]
    no_worse=[by[r]["heldout_churn"]["quorum2"]<=
              by[r]["heldout_churn"]["full"] for r in novel]
    slow=by["reference_drift1"]["sham_relative_savings"]
    if all(no_worse) and any(improvements) and slow["quorum2"]>=.7*slow["full"]:
        classification="QUORUM_NOVEL_ROBUST"
    elif any(improvements):
        classification="MIXED"
    else:
        classification="NO_GAIN"
    return {"schema":"yggdrasil.y036-global-shift-quenched-novelty.v1",
            "parent_head":"35eace118e16ab8195a6810f2bc6ec569dfd0106",
            "classification":classification,"development_seeds":DEVELOPMENT,
            "sealed_heldout_seeds":HELDOUT,"regimes":results,"model_calls":0,
            "claim_limit":"Synthetic observed-state cache behavior under novel global shifts"}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
