"""Y037: fail-closed nonaliased synthetic environments, fixed quorum policy."""
import hashlib
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

BASE=Path(__file__).resolve().parent.parent/"20261013-y036-degree56"/"execute.py"
spec=importlib.util.spec_from_file_location("y036_frozen",BASE)
assert spec and spec.loader
y36=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y36)
y25=y36.y25

DEV=tuple(range(320,328))
HELDOUT=tuple(range(328,344))
REGIMES=("drift1","drift2","drift4","late_shock")
POLICIES=("matched_sham","full","quorum2","quorum3")
LATE_SHOCK=(0,1,2,3,8,13,14,15)


def hash32(*values):
    content="|".join(str(x) for x in values).encode("utf-8")
    return int.from_bytes(hashlib.sha256(content).digest()[:4],"big")


def active_keys(seed,episode):
    return tuple(sorted(range(16),key=lambda key:
                        (hash32("active",seed,episode,key),key))[:7])


def graph(seed,episode,regime,active):
    if regime=="late_shock":
        shift=LATE_SHOCK[episode]
    else:
        assert regime in ("drift1","drift2","drift4")
        shift=int(regime[-1])*episode
    center=(hash32("home",seed)%16+shift)%16
    homes=[center]*4+[(center+offset)%16 for offset in (5,8,11)]
    adjacency={key:{(home+offset)%16 for offset in range(-2,3)}
               for key,home in zip(active,homes)}
    # Independent constructive perfect matching: four collision keys and
    # three separated homes must have seven distinct legal cells.
    witnesses=[(center+offset)%16 for offset in (-2,-1,0,1,5,8,11)]
    assert len(set(witnesses))==7
    assert all(cell in adjacency[key] for key,cell in zip(active,witnesses))
    assert y25.hall_cardinality(list(active),adjacency)==7
    return adjacency


def environment_fingerprint(seed,regime):
    history=[]
    for episode in range(8):
        active=active_keys(seed,episode)
        adjacency=graph(seed,episode,regime,active)
        history.append({
            "episode":episode,
            "active":active,
            "neighbors":{str(k):sorted(adjacency[k]) for k in active}
        })
    return hashlib.sha256(json.dumps(history,sort_keys=True,
                                     separators=(",",":")).encode()).hexdigest()


def evaluate(seed,regime,policy):
    cache=OrderedDict()
    previous_active=set()
    previous_assignment={}
    evaluator_history={}
    rows=[]
    for episode in range(8):
        active=active_keys(seed,episode)
        adjacency=graph(seed,episode,regime,active)
        legal={key:cache[key] for key in active
               if key in cache and cache[key] in adjacency[key]}
        minimum={"matched_sham":999,"full":1,"quorum2":2,"quorum3":3}[policy]
        preferred=legal if len(legal)>=minimum else {}
        matched,calls=y25.match(list(active),adjacency,preferred)
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
        rows.append({"episode":episode,"churn":churn,"calls":calls,
                     "cache_writes":writes,"cache_keys":list(cache),
                     "legal_preferences":len(legal),"used_preferences":len(preferred),
                     "assigned":len(matched)})
    return {"seed":seed,"churn":sum(r["churn"] for r in rows),
            "search_calls":sum(r["calls"] for r in rows),
            "cache_writes":sum(r["cache_writes"] for r in rows),
            "preferred":sum(r["used_preferences"] for r in rows),
            "episodes":rows}


def regime_result(regime):
    fingerprints={seed:environment_fingerprint(seed,regime)
                  for seed in DEV+HELDOUT}
    # If even one environment history aliases, the ORIGINAL experiment is INVALID.
    assert len(set(fingerprints.values()))==len(DEV)+len(HELDOUT)==24
    rows=[]
    for seed in DEV+HELDOUT:
        arms={p:evaluate(seed,regime,p) for p in POLICIES}
        sham=arms["matched_sham"]
        for policy in POLICIES:
            a=arms[policy]
            assert sham["cache_writes"]==a["cache_writes"]
            for x,y in zip(sham["episodes"],a["episodes"]):
                assert x["cache_writes"]==y["cache_writes"]
                assert x["cache_keys"]==y["cache_keys"]
                assert x["assigned"]==y["assigned"]==7
        rows.append({"seed":seed,"cohort":"development" if seed in DEV else "heldout",
                     "fingerprint":fingerprints[seed],
                     "churn":{p:r["churn"] for p,r in arms.items()},
                     "search_calls":{p:r["search_calls"] for p,r in arms.items()},
                     "preferred":{p:r["preferred"] for p,r in arms.items()},
                     "matched_writes":sham["cache_writes"]})
    sealed=[r for r in rows if r["cohort"]=="heldout"]
    totals={p:sum(r["churn"][p] for r in sealed) for p in POLICIES}
    return {"regime":regime,"unique_environment_count":len(set(fingerprints.values())),
            "fingerprints":fingerprints,
            "heldout_churn":totals,
            "sham_relative_savings":{p:totals["matched_sham"]-totals[p]
                                     for p in POLICIES[1:]},
            "seed_rows":rows}


def run():
    results=[regime_result(regime) for regime in REGIMES]
    by={r["regime"]:r for r in results}
    novel=("drift2","drift4","late_shock")
    no_worse=all(by[regime]["heldout_churn"]["quorum2"]<=
                 by[regime]["heldout_churn"]["full"] for regime in novel)
    improvements=[by[regime]["heldout_churn"]["quorum2"]<
                  by[regime]["heldout_churn"]["full"] for regime in novel]
    slow=by["drift1"]["sham_relative_savings"]
    if no_worse and any(improvements) and slow["quorum2"]>=.7*slow["full"]:
        label="QUORUM_REQUALIFIED"
    elif any(improvements):
        label="MIXED"
    else:
        label="NO_TRANSFER"
    return {"schema":"yggdrasil.y037-diverse-environment-quorum.v1",
            "parent_head":"22e8c99ccca694d46c3cce07d9f11574eef43ee1",
            "classification":label,"development_seeds":DEV,"heldout_seeds":HELDOUT,
            "regimes":results,"model_calls":0,
            "claim_limit":"First-use synthetic nonaliased environment, not semantic cognition"}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
