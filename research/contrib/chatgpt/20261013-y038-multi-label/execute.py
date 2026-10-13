"""Y038: frozen four-bijection label-equivariance validation of canonical matching."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

SRC=Path(__file__).resolve().parent.parent/"20261013-y037-coordinate-matching"/"execute.py"
spec=importlib.util.spec_from_file_location("y037_frozen",SRC)
assert spec and spec.loader
y37=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y37)
y25=y37.y25
y36=y37.y36

DEV=tuple(range(240,248))
HELDOUT=tuple(range(248,264))
MULTIPLIERS=(3,5,7,9)
POLICIES=("matched_sham","full","quorum2")


def offset(seed):
    return (11*seed+3)%16


def cell_permute(cell,seed,multiplier):
    return (multiplier*cell+offset(seed))%16


def inverse_cell(cell,seed,multiplier):
    return (pow(multiplier,-1,16)*(cell-offset(seed)))%16


def match(active,neighbors,preferred,seed,multiplier,mode):
    if mode in ("reference_numeric","scrambled_numeric"):
        return y25.match(active,neighbors,preferred)
    assert mode=="scrambled_canonical"
    owner={}
    calls=0
    for key in active:
        cell=preferred.get(key)
        if cell is not None and cell in neighbors[key] and cell not in owner:
            owner[cell]=key
    def augment(key,seen):
        nonlocal calls
        calls+=1
        options=sorted(neighbors[key],
                       key=lambda cell:(cell!=preferred.get(key),
                                        inverse_cell(cell,seed,multiplier)))
        for cell in options:
            if cell in seen:
                continue
            seen.add(cell)
            old=owner.get(cell)
            if old is None or augment(old,seen):
                owner[cell]=key
                return True
        return False
    for key in active:
        if key not in owner.values():
            augment(key,set())
    assigned={key:cell for cell,key in owner.items()}
    assert len(assigned)==7
    return assigned,calls


def run_arm(seed,multiplier,mode,policy):
    cache=OrderedDict()
    prev_active=set()
    prev_assignment={}
    evaluator_history={}
    trace=[]
    for episode in range(8):
        active=y25.active_keys(seed,episode)
        ring=y36.neighborhoods(seed,episode,active,"ring_reference")
        graph=ring if mode=="reference_numeric" else {
            key:{cell_permute(cell,seed,multiplier) for cell in neighbors}
            for key,neighbors in ring.items()}
        assert y25.hall_cardinality(active,graph)==7
        legal={key:cache[key] for key in active
               if key in cache and cache[key] in graph[key]}
        threshold={"matched_sham":999,"full":1,"quorum2":2}[policy]
        preferred=legal if len(legal)>=threshold else {}
        allocation,calls=match(active,graph,preferred,seed,multiplier,mode)
        assert len(allocation)==7 and len(set(allocation.values()))==7
        returning=[key for key in active if key in evaluator_history]
        churn=sum(allocation[key]!=evaluator_history[key] for key in returning)
        for key in active:
            evaluator_history[key]=allocation[key]
        for key in active:
            cache.pop(key,None)
        writes=0
        for key in sorted(prev_active.difference(active)):
            cache.pop(key,None)
            cache[key]=prev_assignment[key]
            writes+=1
            while len(cache)>9:
                cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+7<=16
        assert not set(cache).intersection(active)
        prev_active=set(active)
        prev_assignment=allocation
        normalized={str(key):cell if mode=="reference_numeric"
                    else inverse_cell(cell,seed,multiplier)
                    for key,cell in sorted(allocation.items())}
        trace.append({"episode":episode,"normalized_assignment":normalized,
                      "churn":churn,"search_calls":calls,"writes":writes,
                      "cache_keys":list(cache),"matched":len(allocation)})
    return {"seed":seed,"mode":mode,"policy":policy,
            "total_churn":sum(x["churn"] for x in trace),
            "total_writes":sum(x["writes"] for x in trace),
            "trace":trace}


def run():
    rows=[]
    maps=[]
    for multiplier in MULTIPLIERS:
        errors={"scrambled_numeric":0,"scrambled_canonical":0}
        sums={policy:{"reference_numeric":0,"scrambled_numeric":0,
                      "scrambled_canonical":0} for policy in POLICIES}
        for seed in DEV+HELDOUT:
            for policy in POLICIES:
                samples={mode:run_arm(seed,multiplier,mode,policy)
                         for mode in ("reference_numeric","scrambled_numeric",
                                      "scrambled_canonical")}
                ref=samples["reference_numeric"]
                for mode,arm in samples.items():
                    assert ref["total_writes"]==arm["total_writes"]
                    for r,e in zip(ref["trace"],arm["trace"]):
                        assert r["writes"]==e["writes"]
                        assert r["matched"]==e["matched"]==7
                        assert len(r["cache_keys"])==len(e["cache_keys"])
                        if (seed in HELDOUT and mode!="reference_numeric"
                            and r["normalized_assignment"]!=e["normalized_assignment"]):
                            errors[mode]+=1
                    if seed in HELDOUT:
                        sums[policy][mode]+=arm["total_churn"]
                rows.append({"seed":seed,"cohort":"development" if seed in DEV else "heldout",
                             "multiplier":multiplier,"policy":policy,
                             "per_mode_churn":{k:v["total_churn"] for k,v in samples.items()}})
        maps.append({"multiplier":multiplier,"heldout_assignment_mismatches":errors,
                     "heldout_churn_by_policy_mode":sums})
    mismatches_canonical=sum(x["heldout_assignment_mismatches"]["scrambled_canonical"] for x in maps)
    mismatches_numeric=sum(x["heldout_assignment_mismatches"]["scrambled_numeric"] for x in maps)
    different_churn=any(
        values["reference_numeric"]!=values["scrambled_numeric"]
        for x in maps for values in x["heldout_churn_by_policy_mode"].values())
    if mismatches_canonical==0 and mismatches_numeric>0 and different_churn:
        classification="MULTI_MAP_TIEBREAK_CONFOUND"
    elif mismatches_canonical<mismatches_numeric:
        classification="PARTIAL"
    else:
        classification="NO_CONFIRMED_CONFOUND"
    return {"schema":"yggdrasil.y038-four-bijection-equivariance.v1",
            "parent_head":"c7a42ff087b9a477eebf7d3b3f04dbe316260ab7",
            "classification":classification,"development_seeds":DEV,
            "sealed_heldout_seeds":HELDOUT,"maps":maps,"rows":rows,"model_calls":0,
            "claim_limit":"Fixed-capacity synthetic canonical cell-label equivariance"}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
