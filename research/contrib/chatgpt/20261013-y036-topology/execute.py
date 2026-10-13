"""Y036: frozen transfer of quorum threshold to fresh bipartite neighborhood topologies."""
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
TOPOLOGIES=("ring_reference","fixed_scrambled_ring","episodic_scrambled_ring","five_neighbor_anchored")
POLICIES=("matched_sham","full","quorum2","quorum3")


def neighborhoods(seed,episode,active,topology):
    if topology=="five_neighbor_anchored":
        return {key:{(2*j+seed+episode+d)%16 for d in range(5)}
                for j,key in enumerate(active)}
    base=y34.neighborhoods(seed,episode,active,"drift1")
    if topology=="ring_reference":
        return base
    if topology=="fixed_scrambled_ring":
        return {key:{(5*cell+3*seed)%16 for cell in cells}
                for key,cells in base.items()}
    assert topology=="episodic_scrambled_ring"
    return {key:{(5*cell+3*seed+3*episode)%16 for cell in cells}
            for key,cells in base.items()}


def evaluate(seed,topology,policy):
    cache=OrderedDict()
    previous_active=set()
    previous_assignment={}
    evaluator_history={}
    episodes=[]
    for episode in range(8):
        active=y25.active_keys(seed,episode)
        neighbor=neighborhoods(seed,episode,active,topology)
        cardinality=y25.hall_cardinality(active,neighbor)
        assert cardinality==7
        legal={key:cache[key] for key in active
               if key in cache and cache[key] in neighbor[key]}
        minimum={"matched_sham":999,"full":1,"quorum2":2,"quorum3":3}[policy]
        pref=legal if len(legal)>=minimum else {}
        assigned,calls=y25.match(active,neighbor,pref)
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
        assert len(cache)<=9 and len(cache)+len(active)<=16
        assert not set(active).intersection(cache)
        previous_active=set(active)
        previous_assignment=assigned
        episodes.append({"episode":episode,"churn":churn,
                         "search_calls":calls,"cache_writes":writes,
                         "cached_keys":list(cache),"used_preferences":len(pref),
                         "legal_count":len(legal),"matched":len(assigned)})
    return {"seed":seed,"churn":sum(r["churn"] for r in episodes),
            "search_calls":sum(r["search_calls"] for r in episodes),
            "cache_writes":sum(r["cache_writes"] for r in episodes),
            "used_preferences":sum(r["used_preferences"] for r in episodes),
            "episodes":episodes}


def topology_result(topology):
    rows=[]
    for seed in DEVELOPMENT+HELDOUT:
        arms={policy:evaluate(seed,topology,policy) for policy in POLICIES}
        sham=arms["matched_sham"]
        for p in POLICIES:
            arm=arms[p]
            assert sham["cache_writes"]==arm["cache_writes"]
            for a,b in zip(sham["episodes"],arm["episodes"]):
                assert a["cache_writes"]==b["cache_writes"]
                assert a["cached_keys"]==b["cached_keys"]
                assert a["matched"]==b["matched"]==7
        rows.append({"seed":seed,
                     "cohort":"development" if seed in DEVELOPMENT else "heldout",
                     "churn":{p:r["churn"] for p,r in arms.items()},
                     "search_calls":{p:r["search_calls"] for p,r in arms.items()},
                     "used_preferences":{p:r["used_preferences"] for p,r in arms.items()},
                     "matched_cache_writes":sham["cache_writes"]})
    heldout=[r for r in rows if r["cohort"]=="heldout"]
    churn={p:sum(r["churn"][p] for r in heldout) for p in POLICIES}
    return {"topology":topology,"heldout_churn":churn,
            "sham_relative_savings":{p:churn["matched_sham"]-churn[p] for p in POLICIES[1:]},
            "heldout_preferences":{p:sum(r["used_preferences"][p] for r in heldout)
                                   for p in POLICIES},
            "seed_rows":rows}


def run():
    rows=[topology_result(t) for t in TOPOLOGIES]
    data={r["topology"]:r for r in rows}
    novel=TOPOLOGIES[1:]
    improved=[data[t]["heldout_churn"]["quorum2"]<
              data[t]["heldout_churn"]["full"] for t in novel]
    no_worse=[data[t]["heldout_churn"]["quorum2"]<=
              data[t]["heldout_churn"]["full"] for t in novel]
    slow=data["ring_reference"]["sham_relative_savings"]
    if all(no_worse) and sum(improved)>=2 and slow["quorum2"]>=.7*slow["full"]:
        classification="TOPOLOGY_TRANSFER"
    elif any(improved):
        classification="MIXED"
    else:
        classification="NEGATIVE"
    return {"schema":"yggdrasil.y036-unseen-topology-quorum.v1",
            "parent_head":"35eace118e16ab8195a6810f2bc6ec569dfd0106",
            "classification":classification,
            "development_seeds":DEVELOPMENT,"sealed_heldout_seeds":HELDOUT,
            "topologies":rows,"model_calls":0,
            "claim_limit":"Synthetic allocation cache threshold under distinct present graphs"}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
