"""Y033: preregistered recurrent-versus-constant geometry memory break-even."""
import importlib.util
import hashlib
import json
from collections import OrderedDict
from pathlib import Path

OLD=Path(__file__).resolve().parent.parent/"20261013-y032-stationarity"/"execute.py"
spec=importlib.util.spec_from_file_location("y032_frozen",OLD)
assert spec and spec.loader
previous=importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
y30=previous.y30

SCHEDULES={"recurrent":(0,1,2,1,0,1,2,1),
           "constant":(0,0,0,0,0,0,0,0)}
WEIGHTS=(1,3,10,30)


def world(seed,episode,condition):
    keys,neighbors=y30.geometry(seed,episode)
    shift=SCHEDULES[condition][episode]
    return keys,{key:{(v+shift)%16 for v in neighbors[key]} for key in keys}


def geometry_signature(seed,condition):
    source=[]
    for ep in range(8):
        active,neighbors=world(seed,ep,condition)
        source.append([active,[[k,sorted(neighbors[k])] for k in active]])
    return hashlib.sha256(json.dumps(source,separators=(",",":")).encode()).hexdigest()


def evaluate(seed,condition,retain):
    cache=OrderedDict()
    prev_active=set()
    prev_assignment={}
    evaluator_history={}
    trace=[]
    for ep in range(8):
        active,neighbors=world(seed,ep,condition)
        assert y30.hall_cardinality(active,neighbors)==7
        preferred={k:cache[k] for k in active if k in cache} if retain else {}
        legal={k:v for k,v in preferred.items() if v in neighbors[k]}
        assigned,calls=y30.match(active,neighbors,preferred)
        assert len(assigned)==7
        returning=[k for k in assigned if k in evaluator_history]
        churn=sum(assigned[k]!=evaluator_history[k] for k in returning)
        evaluator_history.update(assigned)
        for k in active:
            cache.pop(k,None)
        writes=0
        for k in sorted(prev_active.difference(active)):
            cache.pop(k,None)
            cache[k]=prev_assignment[k]
            writes+=1
            while len(cache)>9:
                cache.popitem(last=False)
        assert len(cache)<=9 and not set(cache).intersection(active)
        prev_active=set(active)
        prev_assignment=assigned
        trace.append({"episode":ep,"assigned":len(assigned),
            "churn":churn,"calls":calls,"writes":writes,
            "reads":len(preferred),"legal_preferences":len(legal),
            "cache_occupancy":len(cache)})
    values={"seed":seed,"condition":condition,"arm":"retained" if retain else "sham",
            "churn":sum(row["churn"] for row in trace),
            "search_calls":sum(row["calls"] for row in trace),
            "cache_writes":sum(row["writes"] for row in trace),
            "cache_reads":sum(row["reads"] for row in trace),
            "legal_prefs":sum(row["legal_preferences"] for row in trace),
            "trace":trace}
    values["cost"]={str(w):w*values["churn"]+values["search_calls"]+
                     values["cache_writes"]+values["cache_reads"] for w in WEIGHTS}
    return values


def condition(name):
    rows=[evaluate(seed,name,ret) for seed in range(64,72) for ret in (False,True)]
    sigs={str(seed):geometry_signature(seed,name) for seed in range(64,72)}
    assert len(set(sigs.values()))==8
    for i in range(0,len(rows),2):
        sham,ret=rows[i:i+2]
        assert sham["cache_writes"]==ret["cache_writes"]
        assert [x["cache_occupancy"] for x in sham["trace"]]==[
            x["cache_occupancy"] for x in ret["trace"]]
    held=[(rows[2*(seed-64)],rows[2*(seed-64)+1]) for seed in range(68,72)]
    perweight={str(w):[a["cost"][str(w)]-b["cost"][str(w)] for a,b in held] for w in WEIGHTS}
    total_churn_saved=sum(a["churn"]-b["churn"] for a,b in held)
    overhead=sum(b["search_calls"]+b["cache_reads"]-
                 a["search_calls"]-a["cache_reads"] for a,b in held)
    return {"condition":name,"sigs":sigs,"unique_sigs":True,
            "net_savings_by_weight":perweight,
            "aggregate_net_savings":{w:sum(v) for w,v in perweight.items()},
            "per_seed_churn_saved":[a["churn"]-b["churn"] for a,b in held],
            "total_churn_saved":total_churn_saved,
            "total_extra_search_and_read_overhead":overhead,
            "break_even_churn_weight":overhead/total_churn_saved if total_churn_saved>0 else None,
            "heldout_legal_preferences":sum(b["legal_prefs"] for a,b in held),
            "rows":rows}


def run():
    recur=condition("recurrent")
    const=condition("constant")
    v3=recur["aggregate_net_savings"]["3"]
    v30=recur["aggregate_net_savings"]["30"]
    if all(x>0 for x in recur["net_savings_by_weight"]["3"]):
        label="RECURSIVE_RETENTION_NET_GAIN"
    elif v30>0 and v3<=0:
        label="COST_DEPENDENT"
    else:
        label="NO_NET_GAIN"
    return {"schema":"yggdrasil.y033-recurrence-break-even.v1",
        "predecessor_head":"128d005f98e99b14ebdc35a5eac6f7cb197cf073",
        "classification":label,"conditions":[recur,const],
        "model_calls":0,
        "claim_limit":"Cost threshold in finite synthetic matched assignment, not actual finance/biology"}


if __name__=="__main__":
    x=run()
    assert x==run()
    print(json.dumps(x,sort_keys=True,indent=2))
