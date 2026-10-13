"""Y036: frozen cache size x geometry x quorum2 factorial."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent/"20261013-y035-interaction"/"execute.py"
spec=importlib.util.spec_from_file_location("y35_frozen",SOURCE)
assert spec and spec.loader
y35=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y35)
y34=y35.y34
y25=y35.y25

DEVELOPMENT=tuple(range(200,208))
HELDOUT=tuple(range(208,224))
CAPACITIES=(3,6,9)
REGIMES=("drift1","drift2","drift4","late_shock")
POLICIES=("matched_sham","full","quorum2")

def evaluate(seed,capacity,regime,policy):
    cache=OrderedDict()
    prev_active=set()
    prev_assignment={}
    evaluator_history={}
    rows=[]
    for episode in range(8):
        active=y25.active_keys(seed,episode)
        neighbors=y34.neighborhoods(seed,episode,active,regime)
        assert y25.hall_cardinality(active,neighbors)==7
        legal={k:cache[k] for k in active if k in cache and cache[k] in neighbors[k]}
        threshold={"matched_sham":999,"full":1,"quorum2":2}[policy]
        preferred=legal if len(legal)>=threshold else {}
        assigned,calls=y25.match(active,neighbors,preferred)
        assert len(assigned)==7 and len(set(assigned.values()))==7
        returning=[k for k in active if k in evaluator_history]
        churn=sum(assigned[k]!=evaluator_history[k] for k in returning)
        for k in active:evaluator_history[k]=assigned[k]
        for k in active:cache.pop(k,None)
        writes=0
        for k in sorted(prev_active.difference(active)):
            cache.pop(k,None)
            cache[k]=prev_assignment[k]
            writes+=1
            while len(cache)>capacity:cache.popitem(last=False)
        assert len(cache)<=capacity and len(cache)+7<=16
        assert not set(cache).intersection(active)
        prev_active=set(active)
        prev_assignment=assigned
        rows.append({"episode":episode,"matched":len(assigned),"churn":churn,
                     "calls":calls,"cache_writes":writes,"keys":list(cache),
                     "legal_count":len(legal),"applied":len(preferred)})
    return {"seed":seed,"churn":sum(x["churn"] for x in rows),
            "search_calls":sum(x["calls"] for x in rows),
            "writes":sum(x["cache_writes"] for x in rows),
            "applied":sum(x["applied"] for x in rows),"episodes":rows}

def cell(capacity,regime):
    seed_rows=[]
    for seed in DEVELOPMENT+HELDOUT:
        arms={p:evaluate(seed,capacity,regime,p) for p in POLICIES}
        reference=arms["matched_sham"]
        for item in arms.values():
            assert item["writes"]==reference["writes"]
            for a,b in zip(reference["episodes"],item["episodes"]):
                assert a["cache_writes"]==b["cache_writes"]
                assert a["keys"]==b["keys"]
                assert a["matched"]==b["matched"]==7
        seed_rows.append({"seed":seed,"cohort":"development" if seed in DEVELOPMENT else "heldout",
                          "churn":{p:v["churn"] for p,v in arms.items()},
                          "applied_preferences":{p:v["applied"] for p,v in arms.items()},
                          "search_calls":{p:v["search_calls"] for p,v in arms.items()},
                          "paired_cache_writes":reference["writes"]})
    heldout=[x for x in seed_rows if x["cohort"]=="heldout"]
    totals={p:sum(x["churn"][p] for x in heldout) for p in POLICIES}
    return {"capacity":capacity,"regime":regime,"heldout_churn":totals,
            "quorum_minus_full_churn":totals["quorum2"]-totals["full"],
            "sham_relative_savings":{p:totals["matched_sham"]-totals[p] for p in POLICIES[1:]},
            "applied_preferences":{p:sum(x["applied_preferences"][p] for x in heldout)
                                   for p in POLICIES},
            "seed_rows":seed_rows}

def run():
    cells=[cell(cap,r) for cap in CAPACITIES for r in REGIMES]
    assert len(cells)==12
    difference=[x["quorum_minus_full_churn"] for x in cells]
    if all(d<=0 for d in difference) and sum(d<0 for d in difference)>=3:
        label="CAPACITY_ROBUST"
    elif any(d<0 for d in difference) and any(d>0 for d in difference):
        label="MIXED_CAPACITY_EFFECT"
    else:
        label="NO_CAPACITY_ROBUSTNESS"
    return {"schema":"yggdrasil.y036-capacity-quorum-factorial.v1",
            "parent_head":"35eace118e16ab8195a6810f2bc6ec569dfd0106",
            "classification":label,"development_seeds":DEVELOPMENT,
            "sealed_heldout_seeds":HELDOUT,"cells":cells,"model_calls":0,
            "claim_limit":"Synthetic bounded cache quorum/capacity only"}

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
