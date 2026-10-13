"""Y043: preregistered moving motif-identity key-frame equivariance ablation."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent/"20261013-y039-moving-frame"/"execute.py"
spec=importlib.util.spec_from_file_location("y39_frozen",SOURCE)
assert spec and spec.loader
y39=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y39)
y25=y39.y25

DEVELOPMENT=tuple(range(984,992))
HELDOUT=tuple(range(1000,1016))
REGIMES=("drift1","drift3","alternating")
POLICIES=("matched_sham","full","quorum2")
FRAMES=("reference","moving_additive_raw","moving_additive_identity_aware",
        "moving_affine_raw","moving_affine_identity_aware")
ALTERNATING=(0,1,6,7,12,13,18,19)


def encode(key,seed,episode,law):
    if law=="additive":
        return (key+3*seed+5*episode)%16
    assert law=="affine"
    return (5*key+3*seed+3*episode)%16


def decode(observed,seed,episode,law):
    if law=="additive":
        return (observed-3*seed-5*episode)%16
    assert law=="affine"
    return (13*(observed-3*seed-3*episode))%16


def neighbors(seed,episode,active,regime):
    offset=(ALTERNATING[episode] if regime=="alternating" else
            (1 if regime=="drift1" else 3)*episode)
    homes={key:(7*key+seed+offset)%16 for key in active}
    for key in active[1:4]:
        homes[key]=homes[active[0]]
    return {key:{(home+d)%16 for d in range(-2,3)} for key,home in homes.items()}


def evaluate(seed,regime,policy,frame):
    law=("additive" if "additive" in frame else
         "affine" if "affine" in frame else None)
    aware="identity_aware" in frame
    cache=OrderedDict()
    previous_active=set()
    previous_assignment={}
    physical_history={}  # evaluator only, never policy input
    traces=[]
    for episode in range(8):
        physical_active=y25.active_keys(seed,episode)
        physical_neighbors=neighbors(seed,episode,physical_active,regime)
        assert y25.hall_cardinality(physical_active,physical_neighbors)==7
        if law is None:
            active=list(physical_active)
            graph=physical_neighbors
        else:
            assert sorted(encode(k,seed,episode,law) for k in range(16))==list(range(16))
            assert all(decode(encode(k,seed,episode,law),seed,episode,law)==k
                       for k in range(16))
            active=[encode(k,seed,episode,law) for k in physical_active]
            graph={encode(k,seed,episode,law):cells
                   for k,cells in physical_neighbors.items()}
        assert y25.hall_cardinality(active,graph)==7
        # An identity-aware policy has the public coordinate codec and keeps its
        # bounded cache in canonical motif coordinates. Raw policy does not.
        if aware:
            working_active=[decode(k,seed,episode,law) for k in active]
            working_graph={decode(k,seed,episode,law):cells
                           for k,cells in graph.items()}
        else:
            working_active=active
            working_graph=graph
        legal={key:cache[key] for key in working_active
               if key in cache and cache[key] in working_graph[key]}
        threshold={"matched_sham":999,"full":1,"quorum2":2}[policy]
        preferences=legal if len(legal)>=threshold else {}
        allocation,calls=y25.match(working_active,working_graph,preferences)
        assert len(allocation)==7 and len(set(allocation.values()))==7
        if law is None or aware:
            physical=dict(allocation)
        else:
            physical={decode(key,seed,episode,law):cell
                      for key,cell in allocation.items()}
        assert set(physical)==set(physical_active)
        returning=[k for k in physical_active if k in physical_history]
        churn=sum(physical[k]!=physical_history[k] for k in returning)
        for k in physical_active:
            physical_history[k]=physical[k]
        # Every mode uses the same departure-triggered capped cache algorithm.
        # Raw alias changes may alter the *observed* departed-key set; record,
        # but never conceal, the resulting write-count/occupancy difference.
        for key in working_active:
            cache.pop(key,None)
        writes=0
        for key in sorted(previous_active.difference(working_active)):
            cache.pop(key,None)
            cache[key]=previous_assignment[key]
            writes+=1
            while len(cache)>9:
                cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+7<=16
        assert not set(cache).intersection(working_active)
        previous_active=set(working_active)
        previous_assignment=dict(allocation)
        traces.append({
            "episode":episode,"physical_assignment":{str(k):physical[k]
                for k in sorted(physical)},
            "physical_churn":churn,"search_calls":calls,
            "cache_writes":writes,"cache_count":len(cache),
            "preferred_count":len(preferences),"matched":len(allocation),
        })
    return {
        "seed":seed,"frame":frame,"regime":regime,"policy":policy,
        "physical_churn":sum(r["physical_churn"] for r in traces),
        "cache_writes":sum(r["cache_writes"] for r in traces),
        "physical_trace":traces,
    }


def run():
    by_regime=[]
    raw_mismatches={f:0 for f in FRAMES if f.endswith("_raw")}
    aware_mismatches={f:0 for f in FRAMES if f.endswith("_identity_aware")}
    raw_write_disparity={f:0 for f in raw_mismatches}
    physical_churn_totals={regime:{policy:{frame:0 for frame in FRAMES}
                                  for policy in POLICIES} for regime in REGIMES}
    for regime in REGIMES:
        rows=[]
        for seed in DEVELOPMENT+HELDOUT:
            for policy in POLICIES:
                modes={frame:evaluate(seed,regime,policy,frame) for frame in FRAMES}
                ref=modes["reference"]
                for frame,outcome in modes.items():
                    for r,o in zip(ref["physical_trace"],outcome["physical_trace"]):
                        assert r["matched"]==o["matched"]==7
                        if frame.endswith("_identity_aware"):
                            assert r["physical_assignment"]==o["physical_assignment"]
                            assert r["cache_writes"]==o["cache_writes"]
                            assert r["cache_count"]==o["cache_count"]
                        if frame!="reference" and seed in HELDOUT:
                            if r["physical_assignment"]!=o["physical_assignment"]:
                                if frame in aware_mismatches:aware_mismatches[frame]+=1
                                else:raw_mismatches[frame]+=1
                            if frame in raw_mismatches and (
                                r["cache_writes"]!=o["cache_writes"] or
                                r["cache_count"]!=o["cache_count"]):
                                raw_write_disparity[frame]+=1
                    if seed in HELDOUT:
                        physical_churn_totals[regime][policy][frame]+=outcome["physical_churn"]
                rows.append({
                    "seed":seed,"cohort":"development" if seed in DEVELOPMENT else "heldout",
                    "policy":policy,"physical_churn":{m:v["physical_churn"] for m,v in modes.items()},
                    "cache_writes":{m:v["cache_writes"] for m,v in modes.items()},
                })
        by_regime.append({"regime":regime,"rows":rows})
    raw_changes=any(
        physical_churn_totals[g][p][frame]!=physical_churn_totals[g][p]["reference"]
        for g in REGIMES for p in POLICIES for frame in raw_mismatches
    )
    if all(x==0 for x in aware_mismatches.values()) and any(x>0 for x in raw_mismatches.values()) and raw_changes:
        classification="KEY_FRAME_CONFOUND"
    elif sum(aware_mismatches.values())<sum(raw_mismatches.values()):
        classification="PARTIAL"
    else:
        classification="NO_CONFIRMED_CONFOUND"
    return {
        "schema":"yggdrasil.y043-key-identity-coordinate-equivariance.v1",
        "parent_head":"b368758c9f772046f2e67eed628dc3d5e4c6ae4d",
        "classification":classification,
        "development_seeds":DEVELOPMENT,"sealed_heldout_seeds":HELDOUT,
        "raw_assignment_mismatch_count":raw_mismatches,
        "aware_assignment_mismatch_count":aware_mismatches,
        "raw_cache_bookkeeping_disparity_events":raw_write_disparity,
        "heldout_physical_churn":physical_churn_totals,
        "by_regime":by_regime,"model_calls":0,
        "claim_limit":"Synthetic moving-key label equivariance with deterministic public codec. Raw alias effects include changed cache bookkeeping, not isolated key-association alone.",
    }


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
