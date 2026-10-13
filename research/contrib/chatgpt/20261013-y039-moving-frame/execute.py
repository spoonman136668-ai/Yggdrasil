"""Y039 moving coordinate frame, causal cache representation equivariance."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

SRC=Path(__file__).resolve().parent.parent/"20261013-y038-multi-label"/"execute.py"
spec=importlib.util.spec_from_file_location("y038_frozen",SRC)
assert spec and spec.loader
y38=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y38)
y25=y38.y25
y36=y38.y36

DEV=tuple(range(264,272))
HELDOUT=tuple(range(272,288))
MODES=("reference_numeric","moving_raw_numeric","moving_coordinate_aware")
POLICIES=("matched_sham","full","quorum2")


def encode(cell,seed,episode):
    return (5*cell+3*seed+3*episode)%16


def decode(cell,seed,episode):
    return (13*(cell-3*seed-3*episode))%16


def match(active,neighbors,pref,seed,episode,mode):
    if mode!="moving_coordinate_aware":
        return y25.match(active,neighbors,pref)
    owners={}
    calls=0
    for key in active:
        cell=pref.get(key)
        if cell is not None and cell in neighbors[key] and cell not in owners:
            owners[cell]=key
    def augment(key,seen):
        nonlocal calls
        calls+=1
        options=sorted(neighbors[key],
                       key=lambda cell:(cell!=pref.get(key),
                                        decode(cell,seed,episode)))
        for cell in options:
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
    physical_history={}
    rows=[]
    for episode in range(8):
        active=y25.active_keys(seed,episode)
        ring=y36.neighborhoods(seed,episode,active,"ring_reference")
        graph=ring if mode=="reference_numeric" else {
            key:{encode(cell,seed,episode) for cell in cells}
            for key,cells in ring.items()}
        assert y25.hall_cardinality(active,graph)==7
        if mode=="moving_coordinate_aware":
            legal={key:encode(cache[key],seed,episode)
                   for key in active if key in cache and
                   encode(cache[key],seed,episode) in graph[key]}
        else:
            legal={key:cache[key] for key in active
                   if key in cache and cache[key] in graph[key]}
        minimum={"matched_sham":999,"full":1,"quorum2":2}[policy]
        preferences=legal if len(legal)>=minimum else {}
        assigned,calls=match(active,graph,preferences,seed,episode,mode)
        assert len(assigned)==7 and len(set(assigned.values()))==7
        # Decode into the persistent physical (canonical) cell frame for evaluation.
        physical={key:cell if mode=="reference_numeric" else
                  decode(cell,seed,episode)
                  for key,cell in assigned.items()}
        returning=[key for key in active if key in physical_history]
        churn=sum(physical[key]!=physical_history[key] for key in returning)
        for key in active:
            physical_history[key]=physical[key]
        for key in active:
            cache.pop(key,None)
        writes=0
        for key in sorted(previous_active.difference(active)):
            cache.pop(key,None)
            cache[key]=previous_assignment[key]
            writes+=1
            while len(cache)>9:cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+7<=16
        assert not set(cache).intersection(active)
        previous_active=set(active)
        # In aware mode the memory stores physical cell IDs.
        previous_assignment=(physical if mode=="moving_coordinate_aware"
                             else assigned)
        rows.append({"episode":episode,"physical_assignment":{
                         str(k):physical[k] for k in sorted(physical)},
                     "physical_churn":churn,"cache_writes":writes,
                     "cache_keys":list(cache),"search_calls":calls,
                     "legal_preferences":len(preferences),"matched":len(assigned)})
    return {"seed":seed,"mode":mode,"policy":policy,
            "physical_churn":sum(x["physical_churn"] for x in rows),
            "cache_writes":sum(x["cache_writes"] for x in rows),
            "rows":rows}


def run():
    rows=[]
    mismatches={"moving_raw_numeric":0,"moving_coordinate_aware":0}
    totals={policy:{mode:0 for mode in MODES} for policy in POLICIES}
    for seed in DEV+HELDOUT:
        for policy in POLICIES:
            arms={mode:evaluate(seed,mode,policy) for mode in MODES}
            control=arms["reference_numeric"]
            for mode,arm in arms.items():
                assert control["cache_writes"]==arm["cache_writes"]
                for a,b in zip(control["rows"],arm["rows"]):
                    assert a["cache_writes"]==b["cache_writes"]
                    assert a["matched"]==b["matched"]==7
                    assert len(a["cache_keys"])==len(b["cache_keys"])
                    if (mode!="reference_numeric" and seed in HELDOUT and
                        a["physical_assignment"]!=b["physical_assignment"]):
                        mismatches[mode]+=1
                if seed in HELDOUT:
                    totals[policy][mode]+=arm["physical_churn"]
            rows.append({"seed":seed,
                         "cohort":"development" if seed in DEV else "heldout",
                         "policy":policy,
                         "churn":{mode:arm["physical_churn"] for mode,arm in arms.items()}})
    raw_changes=any(x["moving_raw_numeric"]!=x["reference_numeric"]
                    for x in totals.values())
    if mismatches["moving_coordinate_aware"]==0 and mismatches["moving_raw_numeric"]>0 and raw_changes:
        classification="MOVING_FRAME_CONFOUND"
    elif mismatches["moving_coordinate_aware"]<mismatches["moving_raw_numeric"]:
        classification="PARTIAL"
    else:
        classification="NO_CONFIRMED_CONFOUND"
    return {"schema":"yggdrasil.y039-moving-coordinate-invariance.v1",
            "parent_head":"d0118d27e7204e3ade96d9db194eb44237782e78",
            "classification":classification,
            "heldout_physical_assignment_mismatches":mismatches,
            "heldout_physical_churn_by_mode":totals,
            "development_seeds":DEV,"sealed_heldout_seeds":HELDOUT,
            "rows":rows,"model_calls":0,
            "claim_limit":"Synthetic cache equivalence under per-episode coordinate relabeling"}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
