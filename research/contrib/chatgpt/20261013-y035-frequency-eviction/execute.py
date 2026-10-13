"""Y035: online observed-reentry two-bit frequency versus recency eviction."""
import hashlib
import json
from collections import OrderedDict

TEMPLATES=((6,10,14),(5,9,13),(7,10,13),(6,11,14),
           (7,11,15),(5,10,14),(6,9,15),(7,12,15))


def salt(seed):
    return int.from_bytes(hashlib.sha256(("Y035/"+str(seed)).encode()).digest()[:2],"big")%16


def geometry(seed,episode):
    s=salt(seed)
    hot=[(s+d)%16 for d in (0,5,10)]
    cold=[(s+d)%16 for d in range(16) if d not in (0,5,10)]
    assert len(cold)==13
    offset=(7*episode+seed)%13
    rotated=cold[offset:]+cold[:offset]
    active=(hot+rotated[:4]) if episode%2==0 else rotated[:7]
    assert len(active)==len(set(active))==7
    center=(7*s+3*episode+11*(seed-80))%16
    offsets=TEMPLATES[(seed-80+episode)%8]
    home={key:center for key in active[:4]}
    for i,key in enumerate(active[4:]):
        home[key]=(center+offsets[i])%16
    near={key:{(h+d)%16 for d in range(-2,3)} for key,h in home.items()}
    return active,near,set(hot)


def hall_cardinality(active,neighbors):
    deficiency=0
    for subset in range(1,1<<7):
        union=set()
        for i,key in enumerate(active):
            if subset&(1<<i):union.update(neighbors[key])
        deficiency=max(deficiency,subset.bit_count()-len(union))
    return 7-deficiency


def match(active,neighbors,pref):
    owners={}
    calls=0
    for key in active:
        cell=pref.get(key)
        if cell is not None and cell in neighbors[key] and cell not in owners:
            owners[cell]=key

    def augment(key,seen):
        nonlocal calls
        calls+=1
        for cell in sorted(neighbors[key],key=lambda c:(c!=pref.get(key),c)):
            if cell in seen:continue
            seen.add(cell)
            old=owners.get(cell)
            if old is None or augment(old,seen):
                owners[cell]=key
                return True
        return False

    for key in active:
        if key not in owners.values():augment(key,set())
    assigned={key:cell for cell,key in owners.items()}
    assert len(assigned)==hall_cardinality(active,neighbors)
    return assigned,calls


def signature(seed):
    events=[]
    for ep in range(16):
        active,near,_=geometry(seed,ep)
        events.append((active,[sorted(near[k]) for k in active]))
    return hashlib.sha256(json.dumps(events,separators=(",",":")).encode()).hexdigest()


def evaluate(seed,policy):
    cache=OrderedDict()
    prev_active=set()
    prev_assigned={}
    prev_counts={}
    evaluator_last={}
    trace=[]
    for ep in range(16):
        active,neighbors,hot=geometry(seed,ep)
        oracle=hall_cardinality(active,neighbors)
        pref={}
        counts={}
        hits=0
        for key in active:
            stored=cache.get(key)
            if stored is not None:
                cell,count=stored
                hits+=1
                counts[key]=min(3,count+1)
                if cell in neighbors[key]:
                    pref[key]=cell
            else:
                counts[key]=1
        assigned,calls=match(active,neighbors,pref)
        returning=[key for key in assigned if key in evaluator_last]
        churn=sum(assigned[key]!=evaluator_last[key] for key in returning)
        hot_churn=sum(assigned[key]!=evaluator_last[key]
                      for key in returning if key in hot)
        for key in assigned:evaluator_last[key]=assigned[key]
        for key in active:cache.pop(key,None)
        writes=evictions=0
        for key in sorted(prev_active.difference(active)):
            if key in prev_assigned:
                cache.pop(key,None)
                cache[key]=(prev_assigned[key],prev_counts[key])
                writes+=1
                while len(cache)>9:
                    if policy=="LRU":
                        cache.popitem(last=False)
                    else:
                        assert policy=="LFU"
                        keys=list(cache)
                        target=min(keys,key=lambda k:(cache[k][1],keys.index(k),k))
                        cache.pop(target)
                    evictions+=1
        assert len(cache)<=9 and len(cache)+len(active)<=16
        assert all(1<=v[1]<=3 for v in cache.values())
        assert all(1<=v<=3 for v in counts.values())
        prev_active=set(active)
        prev_assigned=assigned
        prev_counts=counts
        trace.append({
            "episode":ep,"matched":len(assigned),"oracle":oracle,
            "returning":len(returning),"churn":churn,"hot_churn":hot_churn,
            "calls":calls,"cache_writes":writes,"evictions":evictions,
            "cache_entries":len(cache),"cache_hits":hits,
            "legal_preferences":len(pref)
        })
    return {
        "seed":seed,"cohort":"development" if seed<84 else "heldout",
        "policy":policy,"hot_churn":sum(e["hot_churn"] for e in trace),
        "overall_churn":sum(e["churn"] for e in trace),
        "cache_hits":sum(e["cache_hits"] for e in trace),
        "legal_preferences":sum(e["legal_preferences"] for e in trace),
        "search_calls":sum(e["calls"] for e in trace),
        "evictions":sum(e["evictions"] for e in trace),
        "cache_writes":sum(e["cache_writes"] for e in trace),
        "episodes":trace
    }


def run():
    signatures={str(s):signature(s) for s in range(80,88)}
    unique=len(set(signatures.values()))==8
    rows=[evaluate(seed,policy) for seed in range(80,88)
          for policy in ("LRU","LFU")]
    by_seed={s:(rows[2*(s-80)],rows[2*(s-80)+1]) for s in range(80,88)}
    oracle_ok=True
    full=True
    for a,b in by_seed.values():
        for row in (a,b):
            for ep in row["episodes"]:
                if ep["matched"]!=ep["oracle"]:oracle_ok=False
                if ep["matched"]!=7:full=False
                if ep["cache_entries"]>9:raise AssertionError("CAPACITY")
    heldout=[by_seed[s] for s in range(84,88)]
    hot_savings=[a["hot_churn"]-b["hot_churn"] for a,b in heldout]
    all_savings=[a["overall_churn"]-b["overall_churn"] for a,b in heldout]
    if not unique or not oracle_ok:
        label="INVALID"
    elif not full:
        label="GEOMETRY_DEFICIENCY"
    elif (sum(hot_savings)>0 and sum(all_savings)>=0
          and sum(x>=0 for x in hot_savings)>=3):
        label="FREQ_EVICTION_BENEFIT"
    elif sum(hot_savings)>0 and sum(all_savings)<0:
        label="MIXED"
    else:
        label="NEGATIVE"
    return {
        "schema":"yggdrasil.y035-observed-frequency-memory.v1",
        "predecessor_head":"70e14ff87ac10ec5f64b0159ee1e7ba805627b55",
        "classification":label,
        "geometry_signatures":signatures,"unique_signatures":unique,
        "hall_agrees":oracle_ok,"all_seven_matched":full,
        "heldout_hot_churn_savings_LFU_vs_LRU":hot_savings,
        "heldout_overall_churn_savings_LFU_vs_LRU":all_savings,
        "heldout_hot_churn_LRU":sum(a["hot_churn"] for a,b in heldout),
        "heldout_hot_churn_LFU":sum(b["hot_churn"] for a,b in heldout),
        "heldout_total_churn_LRU":sum(a["overall_churn"] for a,b in heldout),
        "heldout_total_churn_LFU":sum(b["overall_churn"] for a,b in heldout),
        "rows":rows,"model_calls":0,
        "scope":"Synthetic bounded 2-bit observed frequency tracking, not semantic learning"
    }


if __name__=="__main__":
    outcome=run()
    assert outcome==run()
    print(json.dumps(outcome,sort_keys=True,indent=2))
