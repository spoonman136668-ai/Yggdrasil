"""Y039: cache interruption and observed-only state reacquisition."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

BASE=Path(__file__).resolve().parent.parent/"20261013-y038-retention-capacity"/"execute.py"
spec=importlib.util.spec_from_file_location("y038_frozen",BASE)
assert spec and spec.loader
y38=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y38)
y37=y38.y37
y25=y38.y25

DEV=tuple(range(368,376))
HELDOUT=tuple(range(376,392))
REGIMES=y37.REGIMES
ARMS=("uninterrupted_sham","uninterrupted_full",
      "interrupted_sham","interrupted_full")
RESET_EPISODES=(3,6)


def evaluate(seed,regime,arm):
    assert arm in ARMS
    interrupted=arm.startswith("interrupted")
    use_memory=arm.endswith("full")
    cache=OrderedDict()
    previous_active=set()
    previous_allocation={}
    evaluator_only_history={}
    rows=[]
    for episode in range(8):
        if interrupted and episode in RESET_EPISODES:
            cache.clear()
            previous_active=set()
            previous_allocation={}
        active=y37.active_keys(seed,episode)
        graph=y37.graph(seed,episode,regime,active)
        assert y25.hall_cardinality(list(active),graph)==7
        pref={key:cache[key] for key in active
              if use_memory and key in cache and cache[key] in graph[key]}
        matched,calls=y25.match(list(active),graph,pref)
        assert len(matched)==7 and len(set(matched.values()))==7
        returning=[k for k in active if k in evaluator_only_history]
        churn=sum(matched[k]!=evaluator_only_history[k] for k in returning)
        for key in active:evaluator_only_history[key]=matched[key]
        for key in active:cache.pop(key,None)
        writes=0
        for key in sorted(previous_active.difference(active)):
            cache.pop(key,None)
            cache[key]=previous_allocation[key]
            writes+=1
            while len(cache)>9:cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+7<=16
        assert not set(cache).intersection(active)
        previous_active=set(active)
        previous_allocation=matched
        rows.append({"episode":episode,"churn":churn,
                     "calls":calls,"writes":writes,"cache_keys":list(cache),
                     "used_preferences":len(pref),"matched":len(matched)})
    return {"seed":seed,"churn":sum(r["churn"] for r in rows),
            "postreset_churn":sum(r["churn"] for r in rows if r["episode"]>=3),
            "calls":sum(r["calls"] for r in rows),
            "writes":sum(r["writes"] for r in rows),
            "used_preferences":sum(r["used_preferences"] for r in rows),
            "episodes":rows}


def regime_result(regime):
    hashes={seed:y37.environment_fingerprint(seed,regime) for seed in DEV+HELDOUT}
    assert len(set(hashes.values()))==24
    seed_rows=[]
    for seed in DEV+HELDOUT:
        arms={name:evaluate(seed,regime,name) for name in ARMS}
        for a,b in (("uninterrupted_sham","uninterrupted_full"),
                    ("interrupted_sham","interrupted_full")):
            first,second=arms[a],arms[b]
            assert first["writes"]==second["writes"]
            for r,s in zip(first["episodes"],second["episodes"]):
                assert r["writes"]==s["writes"]
                assert r["cache_keys"]==s["cache_keys"]
                assert r["matched"]==s["matched"]==7
        seed_rows.append({
            "seed":seed,"cohort":"development" if seed in DEV else "heldout",
            "fingerprint":hashes[seed],
            "churn":{name:out["churn"] for name,out in arms.items()},
            "postreset_churn":{name:out["postreset_churn"] for name,out in arms.items()},
            "calls":{name:out["calls"] for name,out in arms.items()},
            "preferences":{name:out["used_preferences"] for name,out in arms.items()},
            "episode_churn":{name:[r["churn"] for r in out["episodes"]]
                             for name,out in arms.items()}
        })
    heldout=[r for r in seed_rows if r["cohort"]=="heldout"]
    total={name:sum(r["churn"][name] for r in heldout) for name in ARMS}
    post={name:sum(r["postreset_churn"][name] for r in heldout) for name in ARMS}
    per_episode={name:[sum(row["episode_churn"][name][ep] for row in heldout)
                       for ep in range(8)] for name in ARMS}
    return {"regime":regime,"unique_environment_count":24,
            "heldout_churn":total,"heldout_postreset_churn":post,
            "episode_churn":per_episode,
            "interrupted_memory_savings":total["interrupted_sham"]-total["interrupted_full"],
            "seed_rows":seed_rows}


def run():
    results=[regime_result(reg) for reg in REGIMES]
    recovery=[]
    for r in results:
        saved=r["interrupted_memory_savings"]
        later=any(
            r["episode_churn"]["interrupted_sham"][ep]>
            r["episode_churn"]["interrupted_full"][ep]
            for ep in (4,5,7))
        recovery.append(saved>0 and later)
    if sum(recovery)>=3:
        label="RECOVERY_BENEFIT"
    elif sum(r["interrupted_memory_savings"]>0 for r in results)>=2:
        label="PARTIAL"
    else:
        label="NO_RECOVERY"
    return {"schema":"yggdrasil.y039-bounded-interruption-recovery.v1",
            "parent_head":"e99b3609b36fffd528bfa3e9c74aab7f3f8c168f",
            "classification":label,
            "reset_episode_starts":RESET_EPISODES,
            "development_seeds":DEV,"heldout_seeds":HELDOUT,
            "regimes":results,"model_calls":0,
            "claim_limit":"Synthetic cache recreation after interruption, no cognitive regeneration"}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
