"""Y040: synthetic hibernation/revival with stale memory under hidden change."""
import hashlib
import json
from collections import OrderedDict

CAPACITIES=(0,3,6,9)
CONDITIONS=("STABLE","HIDDEN_SHIFT")


def permutation(seed):
    return tuple(sorted(
        range(16),
        key=lambda motif: hashlib.sha256(
            ("Y040order/"+str(seed)+"/"+str(motif)).encode()).digest()
    ))


def active(seed,episode):
    ordered=permutation(seed)
    if episode in (0,1,10,11):
        return list(ordered[:7])
    assert 2<=episode<=9
    return list(ordered[7:14])


def target(seed,key,episode,condition):
    raw=hashlib.sha256(("Y040value/"+str(seed)+"/"+str(key)).encode()).digest()
    initial=raw[0]%4
    if condition=="HIDDEN_SHIFT" and episode>=6 and key in permutation(seed)[:7]:
        return (initial+2)%4
    return initial


def fingerprint(seed):
    source={
        "perm":permutation(seed),
        "initial":[target(seed,key,0,"STABLE") for key in range(16)]
    }
    return hashlib.sha256(json.dumps(source,sort_keys=True).encode()).hexdigest()


def evaluate(seed,condition,capacity):
    live={}
    cache=OrderedDict()
    rows=[]
    for episode in range(12):
        keys=active(seed,episode)
        origin={}
        guesses={}
        for key in keys:
            if key in live:
                guesses[key]=live[key];origin[key]="live"
            elif key in cache:
                guesses[key]=cache[key];origin[key]="dormant"
            else:
                guesses[key]=0;origin[key]="default"
        # Feedback strictly after predictions: policy sees no dormant target shift.
        truth={key:target(seed,key,episode,condition) for key in keys}
        correct=sum(guesses[k]==truth[k] for k in keys)
        stale_dormant=sum(guesses[k]!=truth[k] for k in keys if origin[k]=="dormant")
        dormant_hits=sum(origin[k]=="dormant" for k in keys)
        for key in keys:
            cache.pop(key,None)
        writes=evictions=0
        for key in sorted(set(live).difference(keys)):
            if capacity==0:continue
            cache.pop(key,None)
            cache[key]=live[key]
            writes+=1
            while len(cache)>capacity:
                cache.popitem(last=False);evictions+=1
        live=truth
        assert len(live)==7 and len(cache)<=capacity
        assert len(live)+len(cache)<=16
        assert not set(live).intersection(cache)
        rows.append({
            "episode":episode,"correct":correct,"dormant_hits":dormant_hits,
            "stale_dormant_errors":stale_dormant,
            "cache_writes":writes,"evictions":evictions,
            "cached_entries":len(cache),
        })
    return {
        "seed":seed,"condition":condition,"capacity":capacity,
        "cohort":"development" if seed<124 else "heldout",
        "reactivation_e10_correct":rows[10]["correct"],
        "reactivation_e10_dormant_hits":rows[10]["dormant_hits"],
        "reactivation_e10_stale_errors":rows[10]["stale_dormant_errors"],
        "relearn_e11_correct":rows[11]["correct"],
        "total_correct":sum(x["correct"] for x in rows),
        "total_cache_writes":sum(x["cache_writes"] for x in rows),
        "evictions":sum(x["evictions"] for x in rows),
        "episodes":rows,
    }


def run():
    fingerprints={str(seed):fingerprint(seed) for seed in range(120,128)}
    assert len(set(fingerprints.values()))==8
    for seed in range(120,128):
        core=set(active(seed,0))
        distractor=set(active(seed,2))
        assert len(core)==len(distractor)==7
        assert core.isdisjoint(distractor)
        assert active(seed,10)==active(seed,0)
    rows=[evaluate(seed,condition,cap) for condition in CONDITIONS
          for seed in range(120,128) for cap in CAPACITIES]
    def aggregate(condition,metric):
        return {
            str(cap):sum(r[metric] for r in rows if r["seed"]>=124
                         and r["condition"]==condition and r["capacity"]==cap)
            for cap in CAPACITIES
        }
    stable=aggregate("STABLE","reactivation_e10_correct")
    shifted=aggregate("HIDDEN_SHIFT","reactivation_e10_correct")
    stale=aggregate("HIDDEN_SHIFT","reactivation_e10_stale_errors")
    recovered=aggregate("HIDDEN_SHIFT","relearn_e11_correct")
    hits=aggregate("STABLE","reactivation_e10_dormant_hits")
    if stable["9"]>stable["0"] and shifted["9"]<shifted["0"] and recovered["9"]==28:
        label="HIBERNATION_RECALL_AND_STALE_COST"
    elif stable["9"]>stable["0"]:
        label="PARTIAL"
    else:
        label="NEGATIVE"
    return {
        "schema":"yggdrasil.y040-hibernation-reactivation.v1",
        "predecessor_head":"63a0c708d63ba52556a2096cbf95cda247f42980",
        "classification":label,
        "unique_fingerprints":True,
        "heldout_stable_e10_correct":stable,
        "heldout_shifted_e10_correct":shifted,
        "heldout_shifted_e10_stale_dormant_errors":stale,
        "heldout_stable_e10_dormant_hits":hits,
        "heldout_shifted_e11_relearn_correct":recovered,
        "rows":rows,"model_calls":0,
        "claim_limit":"Synthetic cue hibernation and reactivation under known finite labels and caches.",
    }


if __name__=="__main__":
    data=run()
    assert data==run()
    print(json.dumps(data,sort_keys=True,indent=2))
