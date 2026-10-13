"""Y031: pre-registered jump-drift and net utility of bounded observed memory."""
import importlib.util
import hashlib
import json
from collections import OrderedDict
from pathlib import Path

PRIOR=Path(__file__).resolve().parent.parent/"20261012-y030-new-family"/"execute.py"
spec=importlib.util.spec_from_file_location("y030_frozen",PRIOR)
assert spec and spec.loader
prior=importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)

SHIFTS=(0,1,2,9,10,11,4,5)
WEIGHTS=(1,3,10)


def world(seed,episode):
    active,neighbors=prior.geometry(seed,episode)
    displacement=SHIFTS[episode]
    transformed={k:{(v+displacement)%16 for v in neighbors[k]} for k in active}
    return active,transformed


def signature(seed):
    data=[]
    for episode in range(8):
        active,neighbors=world(seed,episode)
        data.append([active,[[k,sorted(neighbors[k])] for k in active]])
    return hashlib.sha256(json.dumps(data,separators=(",",":")).encode()).hexdigest()


def evaluate(seed,read_cache):
    cache=OrderedDict()
    previous_active=set()
    previous_assignment={}
    evaluator_history={}
    episodes=[]
    for episode in range(8):
        active,neighbors=world(seed,episode)
        assert prior.hall_cardinality(active,neighbors)==7
        attempted={k:cache[k] for k in active if k in cache} if read_cache else {}
        legal={k:v for k,v in attempted.items() if v in neighbors[k]}
        assigned,calls=prior.match(active,neighbors,attempted)
        assert len(assigned)==7
        returning=[k for k in assigned if k in evaluator_history]
        churn=sum(assigned[k]!=evaluator_history[k] for k in returning)
        for key in assigned:
            evaluator_history[key]=assigned[key]
        for key in active:
            cache.pop(key,None)
        writes=0
        for key in sorted(previous_active.difference(active)):
            cache.pop(key,None)
            cache[key]=previous_assignment[key]
            writes+=1
            while len(cache)>9:
                cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+7<=16
        assert not set(active).intersection(cache)
        previous_active=set(active)
        previous_assignment=assigned
        episodes.append({"episode":episode,"matched":len(assigned),
            "churn":churn,"search_calls":calls,"cache_writes":writes,
            "cache_occupancy":len(cache),"attempted_cache_reads":len(attempted),
            "legal_cache_preferences":len(legal)})
    out={"seed":seed,"cohort":"development" if seed<52 else "heldout",
         "arm":"retained" if read_cache else "sham",
         "churn":sum(r["churn"] for r in episodes),
         "search_calls":sum(r["search_calls"] for r in episodes),
         "writes":sum(r["cache_writes"] for r in episodes),
         "read_attempts":sum(r["attempted_cache_reads"] for r in episodes),
         "legal_prefs":sum(r["legal_cache_preferences"] for r in episodes),
         "episodes":episodes}
    out["costs"]={str(w):w*out["churn"]+out["search_calls"]+out["writes"]+out["read_attempts"] for w in WEIGHTS}
    return out


def run():
    rows=[evaluate(seed,read) for seed in range(48,56) for read in (False,True)]
    sigs={str(s):signature(s) for s in range(48,56)}
    unique=len(set(sigs.values()))==8
    for i in range(0,len(rows),2):
        a,b=rows[i:i+2]
        assert a["writes"]==b["writes"]
        assert [x["cache_occupancy"] for x in a["episodes"]]==[
            x["cache_occupancy"] for x in b["episodes"]]
    pairs=[(rows[2*(seed-48)],rows[2*(seed-48)+1]) for seed in range(52,56)]
    churn_savings=[a["churn"]-b["churn"] for a,b in pairs]
    cost_savings={str(w):[a["costs"][str(w)]-b["costs"][str(w)]
                          for a,b in pairs] for w in WEIGHTS}
    totals={w:sum(v) for w,v in cost_savings.items()}
    if not unique:
        label="INVALID_NONUNIQUE_GEOMETRY"
    elif all(all(v>0 for v in savings) for savings in cost_savings.values()):
        label="CONSISTENT_NET_GAIN"
    elif all(v<0 for v in totals.values()):
        label="NET_HARM"
    else:
        label="TRADEOFF_OR_MIXED"
    return {"schema":"yggdrasil.y031-jump-drift-utility.v1",
        "predecessor_head":"72b64a2b9a5344ad3064978c9a4a823c26cac4c4",
        "classification":label,"geometry_signatures":sigs,
        "unique_geometry_signatures":unique,"frozen_displacements":SHIFTS,
        "heldout_churn_savings":churn_savings,
        "heldout_cost_savings_by_weight":cost_savings,
        "heldout_total_cost_savings":totals,
        "heldout_legal_cache_preferences":sum(b["legal_prefs"] for a,b in pairs),
        "rows":rows,"model_calls":0,
        "claim_limit":"Synthetic bounded memory cost, not actual monetary or general cognitive utility"}


if __name__=="__main__":
    result=run()
    assert result==run()
    print(json.dumps(result,sort_keys=True,indent=2))
