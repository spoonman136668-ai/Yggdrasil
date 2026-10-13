"""Y037: frozen causal ablation of cell-label numerical tie-break confound."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

SRC=Path(__file__).resolve().parent.parent/"20261013-y036-topology"/"execute.py"
_spec=importlib.util.spec_from_file_location("y036_frozen",SRC)
assert _spec and _spec.loader
y36=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(y36)
y25=y36.y25

DEVELOPMENT=tuple(range(216,224))
HELDOUT=tuple(range(224,240))
MODES=("reference_numeric","scrambled_numeric","scrambled_canonical")
POLICIES=("matched_sham","full","quorum2")


def canonical(seed,observed_cell):
    return (13*(observed_cell-3*seed))%16


def mode_neighbors(seed,episode,active,mode):
    if mode=="reference_numeric":
        return y36.neighborhoods(seed,episode,active,"ring_reference")
    return y36.neighborhoods(seed,episode,active,"fixed_scrambled_ring")


def match(active,neighbors,preferred,seed,mode):
    if mode=="scrambled_numeric" or mode=="reference_numeric":
        return y25.match(active,neighbors,preferred)
    assert mode=="scrambled_canonical"
    owners={}
    calls=0
    for key in active:
        cell=preferred.get(key)
        if cell is not None and cell in neighbors[key] and cell not in owners:
            owners[cell]=key
    def augment(key,seen):
        nonlocal calls
        calls+=1
        choices=sorted(neighbors[key],
                       key=lambda cell:(cell!=preferred.get(key),
                                        canonical(seed,cell)))
        for cell in choices:
            if cell in seen:
                continue
            seen.add(cell)
            previous=owners.get(cell)
            if previous is None or augment(previous,seen):
                owners[cell]=key
                return True
        return False
    for key in active:
        if key not in owners.values():
            augment(key,set())
    assigned={key:cell for cell,key in owners.items()}
    assert len(assigned)==7
    return assigned,calls


def evaluate(seed,mode,policy):
    cache=OrderedDict()
    previous_active=set()
    previous_assignment={}
    evaluator_history={}
    episodes=[]
    for episode in range(8):
        active=y25.active_keys(seed,episode)
        neighbors=mode_neighbors(seed,episode,active,mode)
        assert y25.hall_cardinality(active,neighbors)==7
        legal={key:cache[key] for key in active
               if key in cache and cache[key] in neighbors[key]}
        minimum={"matched_sham":999,"full":1,"quorum2":2}[policy]
        preferences=legal if len(legal)>=minimum else {}
        assigned,calls=match(active,neighbors,preferences,seed,mode)
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
        assert len(cache)<=9 and len(cache)+7<=16
        assert not set(active).intersection(cache)
        previous_active=set(active)
        previous_assignment=assigned
        canonical_assignment={str(key):(cell if mode=="reference_numeric"
                               else canonical(seed,cell))
                              for key,cell in sorted(assigned.items())}
        episodes.append({
            "episode":episode,"canonical_allocation":canonical_assignment,
            "churn":churn,"search_calls":calls,"writes":writes,
            "cache_keys":list(cache),"matched":len(assigned),
            "preference_count":len(preferences)})
    return {"seed":seed,"mode":mode,"policy":policy,
            "churn":sum(x["churn"] for x in episodes),
            "search_calls":sum(x["search_calls"] for x in episodes),
            "cache_writes":sum(x["writes"] for x in episodes),
            "episodes":episodes}


def run():
    rows=[]
    total_mismatch={"scrambled_numeric":0,"scrambled_canonical":0}
    for seed in DEVELOPMENT+HELDOUT:
        for policy in POLICIES:
            outcomes={mode:evaluate(seed,mode,policy) for mode in MODES}
            reference=outcomes["reference_numeric"]
            for mode in MODES[1:]:
                other=outcomes[mode]
                assert reference["cache_writes"]==other["cache_writes"]
                for a,b in zip(reference["episodes"],other["episodes"]):
                    assert a["writes"]==b["writes"]
                    assert a["matched"]==b["matched"]==7
                    assert len(a["cache_keys"])==len(b["cache_keys"])
                    if (a["canonical_allocation"]!=b["canonical_allocation"]
                        and seed in HELDOUT):
                        total_mismatch[mode]+=1
            rows.append({"seed":seed,"cohort":"development" if seed in DEVELOPMENT else "heldout",
                         "policy":policy,
                         "total_churn":{mode:r["churn"] for mode,r in outcomes.items()},
                         "episodes":{mode:r["episodes"] for mode,r in outcomes.items()}})
    heldout=[r for r in rows if r["cohort"]=="heldout"]
    totals={policy:{mode:sum(r["total_churn"][mode] for r in heldout
                                     if r["policy"]==policy)
                    for mode in MODES}
            for policy in POLICIES}
    numeric_difference=any(d["scrambled_numeric"]!=d["reference_numeric"]
                           for d in totals.values())
    if total_mismatch["scrambled_canonical"]==0 and total_mismatch["scrambled_numeric"]>0 and numeric_difference:
        label="COORDINATE_SORT_CONFOUND"
    elif total_mismatch["scrambled_canonical"]<total_mismatch["scrambled_numeric"]:
        label="PARTIAL"
    else:
        label="NO_CONFIRMED_CONFOUND"
    return {"schema":"yggdrasil.y037-cell-coordinate-equivariance.v1",
            "parent_head":"1b89e7039cb750a85ba0a2c384d7b0982e38012e",
            "classification":label,"heldout_assignment_mismatches":total_mismatch,
            "heldout_churn_by_policy_mode":totals,
            "development_seeds":DEVELOPMENT,"sealed_heldout_seeds":HELDOUT,
            "rows":rows,"model_calls":0,
            "claim_limit":"Synthetic matcher equivariance under cell renaming only"}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
