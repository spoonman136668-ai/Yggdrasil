"""Y031: controlled 12-episode delayed-reentry memory-age ablation."""
import importlib.util
import json
import hashlib
from pathlib import Path
from collections import OrderedDict

PARENT=Path(__file__).resolve().parent.parent/"20261012-y030-new-family"/"execute.py"
spec=importlib.util.spec_from_file_location("y030_frozen",PARENT)
assert spec and spec.loader
prior=importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)

EPISODES=(0,1,4,6,9,10,13,15,18,20,23,25)
ARMS=("sham","unrestricted","age2")


def geometry_signature(seed):
    series=[]
    for logical in EPISODES:
        active,near=prior.geometry(seed,logical)
        series.append({"active":active,
                       "neighbors":[sorted(near[k]) for k in active]})
    source=json.dumps(series,sort_keys=True,separators=(",",":"))
    return hashlib.sha256(source.encode()).hexdigest()


def evaluate(seed, arm):
    cache=OrderedDict()
    previous_active=set()
    previous_assignment={}
    history_for_evaluator={}
    records=[]
    for observation,logical in enumerate(EPISODES):
        active,adj=prior.geometry(seed,logical)
        oracle=prior.hall_cardinality(active,adj)
        preferred={}
        if arm != "sham":
            for key in active:
                old=cache.get(key)
                if old is None: continue
                cell,last_seen=old
                if cell not in adj[key]:continue
                if arm=="age2" and observation-last_seen>2:continue
                preferred[key]=cell
        placed,calls=prior.match(active,adj,preferred)
        returning=[k for k in placed if k in history_for_evaluator]
        churn=sum(placed[k]!=history_for_evaluator[k] for k in returning)
        for k in placed:history_for_evaluator[k]=placed[k]
        for k in active:cache.pop(k,None)
        writes=0
        for key in sorted(previous_active.difference(active)):
            cache.pop(key,None)
            if key in previous_assignment:
                cache[key]=(previous_assignment[key],observation-1)
                writes+=1
                while len(cache)>9:cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+len(active)<=16
        assert not set(cache).intersection(active)
        previous_active=set(active)
        previous_assignment=placed
        records.append({
            "observation":observation,"logical_episode":logical,
            "oracle_cardinality":oracle,
            "matched":len(placed),
            "returning":len(returning),"churn":churn,
            "calls":calls,"writes":writes,
            "entries":len(cache),"legal_preferences":len(preferred)
        })
    return {
        "seed":seed,"cohort":"development" if seed<52 else "heldout",
        "arm":arm,"churn":sum(e["churn"] for e in records),
        "search_calls":sum(e["calls"] for e in records),
        "cache_writes":sum(e["writes"] for e in records),
        "legal_preferences":sum(e["legal_preferences"] for e in records),
        "episodes":records
    }


def run():
    signatures={str(seed):geometry_signature(seed) for seed in range(48,56)}
    unique=len(set(signatures.values()))==8
    rows=[evaluate(seed,arm) for seed in range(48,56) for arm in ARMS]
    groups={seed:rows[3*(seed-48):3*(seed-48)+3] for seed in range(48,56)}
    same_writes=True
    hall_ok=True
    full_match=True
    for triple in groups.values():
        occupancy=[[ep["entries"] for ep in r["episodes"]] for r in triple]
        write_seq=[[ep["writes"] for ep in r["episodes"]] for r in triple]
        if not (occupancy[0]==occupancy[1]==occupancy[2]
                and write_seq[0]==write_seq[1]==write_seq[2]):
            same_writes=False
        for row in triple:
            for ep in row["episodes"]:
                if ep["oracle_cardinality"]!=ep["matched"]:hall_ok=False
                if ep["matched"]!=7:full_match=False
    pairs=[groups[s] for s in range(52,56)]
    savings=[r[1]["churn"]-r[2]["churn"] for r in pairs]
    if not unique or not hall_ok or not same_writes:
        label="INVALID"
    elif not full_match:
        label="GEOMETRY_DEFICIENCY"
    elif all(x>=0 for x in savings) and sum(savings)>0:
        label="AGE_GATING_BENEFIT"
    elif sum(savings)<0:
        label="AGE_GATING_HARM"
    else:
        label="MIXED"
    return {
        "schema":"yggdrasil.y031-delayed-reentry-age2.v1",
        "predecessor_head":"72b64a2b9a5344ad3064978c9a4a823c26cac4c4",
        "classification":label,
        "signatures":signatures,"unique_signatures":unique,
        "hall_oracle_agrees":hall_ok,
        "all_seven_matched":full_match,
        "matched_writes_and_entries":same_writes,
        "heldout_age2_savings_vs_unrestricted":savings,
        "heldout_sham_churn":sum(r[0]["churn"] for r in pairs),
        "heldout_unrestricted_churn":sum(r[1]["churn"] for r in pairs),
        "heldout_age2_churn":sum(r[2]["churn"] for r in pairs),
        "rows":rows,"model_calls":0,
        "scope":"Synthetic bounded allocation history; not learned semantic memory"
    }


if __name__=="__main__":
    result=run()
    assert result==run()
    print(json.dumps(result,sort_keys=True,indent=2))
