"""Y038: 16-episode finite recurrence stress with unchanged 9-slot memory."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent/"20261013-y036-novel-shifts"/"execute.py"
_spec=importlib.util.spec_from_file_location("y036_frozen",SOURCE)
assert _spec and _spec.loader
y36=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(y36)
y25=y36.y25

DEV=tuple(range(248,256))
HELDOUT=tuple(range(256,272))
REGIMES=y36.REGIMES
POLICIES=y36.POLICIES
EPISODES=16


def neighbors(seed,episode,active,regime):
    if regime=="zigzag":
        shift=y36.ZIGZAG[episode%8]
    elif regime=="shock_recover":
        shift=y36.SHOCK[episode%8]
    else:
        shift=y36.displacement(seed,episode,regime)
    homes={key:(7*key+seed+shift)%16 for key in active}
    for key in active[1:4]:homes[key]=homes[active[0]]
    return {key:{(home+delta)%16 for delta in range(-2,3)}
            for key,home in homes.items()}


def policy_eval(seed,regime,policy):
    cache=OrderedDict()
    previous_active=set()
    previous_assignment={}
    evaluator_history={}
    episodes=[]
    for ep in range(EPISODES):
        active=y25.active_keys(seed,ep)
        adjacency=neighbors(seed,ep,active,regime)
        assert y25.hall_cardinality(active,adjacency)==7
        legal={key:cache[key] for key in active
               if key in cache and cache[key] in adjacency[key]}
        threshold={"matched_sham":999,"full":1,"quorum2":2,"quorum3":3}[policy]
        preferred=legal if len(legal)>=threshold else {}
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
        assert not set(cache).intersection(active)
        previous_active=set(active)
        previous_assignment=matched
        episodes.append({"episode":ep,"matched":len(matched),"churn":churn,
                         "search_calls":calls,"cache_writes":writes,
                         "cache_keys":list(cache),"preferences":len(preferred)})
    return {"seed":seed,"episodes":episodes}


def regime_result(regime):
    seed_rows=[]
    for seed in DEV+HELDOUT:
        outcomes={p:policy_eval(seed,regime,p) for p in POLICIES}
        sham=outcomes["matched_sham"]
        for result in outcomes.values():
            for a,b in zip(sham["episodes"],result["episodes"]):
                assert a["cache_writes"]==b["cache_writes"]
                assert a["cache_keys"]==b["cache_keys"]
                assert a["matched"]==b["matched"]==7
        seed_rows.append({
            "seed":seed,"cohort":"development" if seed in DEV else "heldout",
            "policy_episode_churn":{p:[e["churn"] for e in r["episodes"]]
                                   for p,r in outcomes.items()},
            "policy_episode_calls":{p:[e["search_calls"] for e in r["episodes"]]
                                   for p,r in outcomes.items()},
            "policy_preferences":{p:sum(e["preferences"] for e in r["episodes"])
                                  for p,r in outcomes.items()},
            "cache_writes":sum(e["cache_writes"] for e in sham["episodes"])})
    held=[r for r in seed_rows if r["cohort"]=="heldout"]
    half_churn=[]
    half_calls=[]
    for low,high in ((0,8),(8,16)):
        half_churn.append({p:sum(sum(s["policy_episode_churn"][p][low:high])
                                  for s in held) for p in POLICIES})
        half_calls.append({p:sum(sum(s["policy_episode_calls"][p][low:high])
                                  for s in held) for p in POLICIES})
    return {"regime":regime,"half_churn":half_churn,"half_search_calls":half_calls,
            "heldout_preferences":{p:sum(s["policy_preferences"][p] for s in held)
                                   for p in POLICIES},"seed_rows":seed_rows}


def run():
    rows=[regime_result(r) for r in REGIMES]
    by={r["regime"]:r for r in rows}
    all_cells=[d for r in rows for d in r["half_churn"]]
    no_worse=all(c["quorum2"]<=c["full"] for c in all_cells)
    strict=sum(c["quorum2"]<c["full"] for c in all_cells)
    base=by["reference_drift1"]["half_churn"][0]
    full_saved=base["matched_sham"]-base["full"]
    q2_saved=base["matched_sham"]-base["quorum2"]
    if no_worse and strict>=2 and q2_saved>=.7*full_saved:
        label="LONG_HORIZON_QUORUM"
    elif strict>=2:
        label="PARTIAL"
    else:
        label="NO_LONG_HORIZON_GAIN"
    return {"schema":"yggdrasil.y038-16-episode-returning-memory.v1",
            "parent_head":"481a7ec6ce46100bf7c75d9d1c6fd63f99a2e7fe",
            "classification":label,"development_seeds":DEV,
            "sealed_heldout_seeds":HELDOUT,"regimes":rows,
            "first_half_saved_full":full_saved,
            "first_half_saved_quorum2":q2_saved,"model_calls":0,
            "claim_limit":"Finite synthetic 16-episode assignment memory, unchanged capacity"}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
