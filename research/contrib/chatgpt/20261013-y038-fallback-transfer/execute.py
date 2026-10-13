"""Y038: untouched legal singleton fallback tested on new drift geometries."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PARENT=Path(__file__).resolve().parent.parent/"20261013-y037-fallback"/"execute.py"
_spec=importlib.util.spec_from_file_location("y37_frozen",PARENT)
assert _spec and _spec.loader
y37=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(y37)
y25=y37.y25

DEVELOPMENT=tuple(range(248,256))
HELDOUT=tuple(range(256,272))
REGIMES=("drift1","drift0","drift3","drift5","alternating")
POLICIES=y37.POLICIES
ALTERNATING=(0,1,6,7,12,13,18,19)


def neighbors(seed,episode,active,regime):
    if regime=="alternating":
        offset=ALTERNATING[episode]
    else:
        assert regime in ("drift1","drift0","drift3","drift5")
        offset=int(regime[-1])*episode
    homes={key:(7*key+seed+offset)%16 for key in active}
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
    for episode in range(8):
        active=y25.active_keys(seed,episode)
        adjacency=neighbors(seed,episode,active,regime)
        assert y25.hall_cardinality(active,adjacency)==7
        legal={key:cache[key] for key in active
               if key in cache and cache[key] in adjacency[key]}
        if policy=="matched_sham":
            preferred={}
        elif policy=="full":
            preferred=legal
        elif policy=="quorum2":
            preferred=legal if len(legal)>=2 else {}
        elif len(legal)>=2:
            preferred=legal
        elif len(legal)==1:
            cutoff=6 if policy=="fallback6" else 5
            cell=next(iter(legal.values()))
            degree=sum(cell in adjacency[k] for k in active)
            preferred=legal if degree<=cutoff else {}
        else:
            preferred={}
        assigned,calls=y25.match(active,adjacency,preferred)
        assert len(assigned)==7 and len(set(assigned.values()))==7
        returning=[k for k in active if k in evaluator_history]
        churn=sum(assigned[k]!=evaluator_history[k] for k in returning)
        for k in active:
            evaluator_history[k]=assigned[k]
        for k in active:
            cache.pop(k,None)
        writes=0
        for k in sorted(previous_active.difference(active)):
            cache.pop(k,None)
            cache[k]=previous_assignment[k]
            writes+=1
            while len(cache)>9:
                cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+7<=16
        assert not set(cache).intersection(active)
        previous_active=set(active)
        previous_assignment=assigned
        episodes.append({"episode":episode,"churn":churn,"search_calls":calls,
                         "writes":writes,"cached_keys":list(cache),
                         "applied":len(preferred),"matched":len(assigned)})
    return {"seed":seed,"churn":sum(x["churn"] for x in episodes),
            "search_calls":sum(x["search_calls"] for x in episodes),
            "cache_writes":sum(x["writes"] for x in episodes),
            "preferences":sum(x["applied"] for x in episodes),
            "episodes":episodes}


def regime_result(regime):
    rows=[]
    for seed in DEVELOPMENT+HELDOUT:
        arms={p:evaluate(seed,regime,p) for p in POLICIES}
        control=arms["matched_sham"]
        for r in arms.values():
            assert control["cache_writes"]==r["cache_writes"]
            for a,b in zip(control["episodes"],r["episodes"]):
                assert a["writes"]==b["writes"]
                assert a["cached_keys"]==b["cached_keys"]
                assert a["matched"]==b["matched"]==7
        rows.append({"seed":seed,"cohort":"development" if seed in DEVELOPMENT else "heldout",
                     "churn":{p:x["churn"] for p,x in arms.items()},
                     "search_calls":{p:x["search_calls"] for p,x in arms.items()},
                     "preferences":{p:x["preferences"] for p,x in arms.items()},
                     "paired_cache_writes":control["cache_writes"]})
    heldout=[r for r in rows if r["cohort"]=="heldout"]
    total={p:sum(r["churn"][p] for r in heldout) for p in POLICIES}
    return {"regime":regime,"heldout_churn":total,
            "sham_relative_savings":{p:total["matched_sham"]-total[p] for p in POLICIES[1:]},
            "seed_rows":rows}


def run():
    rows=[regime_result(r) for r in REGIMES]
    by={r["regime"]:r for r in rows}
    novel=("drift0","drift3","drift5","alternating")
    no_worse=all(by[r]["heldout_churn"]["fallback6"]<=by[r]["heldout_churn"]["quorum2"]
                 for r in novel)
    improved=any(by[r]["heldout_churn"]["fallback6"]<by[r]["heldout_churn"]["quorum2"]
                 for r in novel)
    anygain=any(by[r]["heldout_churn"][p]<by[r]["heldout_churn"]["quorum2"]
                for r in novel for p in ("fallback6","fallback5"))
    slow=by["drift1"]["sham_relative_savings"]
    if no_worse and improved and slow["fallback6"]>=.7*slow["full"]:
        classification="FALLBACK_GENERALIZES"
    elif anygain:
        classification="MIXED"
    else:
        classification="NO_TRANSFER"
    return {"schema":"yggdrasil.y038-singleton-unseen-drift.v1",
            "parent_head":"78306244bb4f7b71bca9a0da987673f9f0710e8c",
            "classification":classification,"development_seeds":DEVELOPMENT,
            "sealed_heldout_seeds":HELDOUT,"regimes":rows,
            "model_calls":0,"claim_limit":"Finite synthetic observed-cache drift transfer, no learned semantics"}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
