"""Y033: bounded dormant cue memory with observed-only feedback and a target switch."""
import hashlib
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PRIOR = Path(__file__).resolve().parent.parent / "20261013-y032-inner-trust" / "execute.py"
_spec=importlib.util.spec_from_file_location("y032_frozen",PRIOR)
assert _spec and _spec.loader
y32=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(y32)


def active_keys(seed,episode):
    keys,_=y32.y31.y030.geometry(seed,episode)
    assert len(keys)==len(set(keys))==7
    return keys


def target(seed,key,episode,condition):
    assert condition in ("STABLE","SWITCH")
    digest=hashlib.sha256(("Y033/"+str(seed)+"/"+str(key)).encode("utf-8")).digest()
    initial=digest[0]%4
    if condition=="SWITCH" and episode>=6:
        return (initial+2)%4
    return initial


def signature(seed):
    activity=[active_keys(seed,ep) for ep in range(12)]
    labels=[target(seed,key,0,"STABLE") for key in range(16)]
    canonical=json.dumps({"active":activity,"labels":labels},sort_keys=True,separators=(",",":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def evaluate(seed,condition,read_dormant):
    active_values={}
    cache=OrderedDict()
    seen_by_evaluator=set()
    episodes=[]
    for ep in range(12):
        keys=active_keys(seed,ep)
        predictions={}
        provenance={}
        for key in keys:
            if key in active_values:
                predictions[key]=active_values[key]
                provenance[key]="live"
            elif key in cache and read_dormant:
                predictions[key]=cache[key]
                provenance[key]="dormant"
            else:
                predictions[key]=0
                provenance[key]="default"
        # Important: the policy receives feedback only after all predictions.
        truth={key:target(seed,key,ep,condition) for key in keys}
        dormant_returning=[key for key in keys if key in seen_by_evaluator and key not in active_values]
        correct=sum(predictions[key]==truth[key] for key in keys)
        dormant_correct=sum(predictions[key]==truth[key] for key in dormant_returning)
        dormant_read_correct=sum(
            predictions[key]==truth[key] for key in dormant_returning
            if provenance[key]=="dormant"
        )
        dormant_read_count=sum(provenance[key]=="dormant" for key in dormant_returning)
        for key in keys:
            cache.pop(key,None)
        writes=0
        for key in sorted(set(active_values).difference(keys)):
            cache.pop(key,None)
            cache[key]=active_values[key]
            writes+=1
            while len(cache)>9:
                cache.popitem(last=False)
        active_values=truth
        seen_by_evaluator.update(keys)
        assert len(active_values)==7
        assert len(cache)<=9 and len(cache)+len(active_values)<=16
        assert not set(cache).intersection(active_values)
        episodes.append({
            "episode":ep,"predictions":7,"correct":correct,
            "returning_dormant":len(dormant_returning),
            "dormant_correct":dormant_correct,
            "dormant_read_count":dormant_read_count,
            "dormant_read_correct":dormant_read_correct,
            "cache_writes":writes,"cache_entries":len(cache),
            "prev_live_matches":sum(provenance[k]=="live" for k in keys),
        })
    return {
        "seed":seed,"cohort":"development" if seed<68 else "heldout",
        "condition":condition,
        "arm":"dormant_memory_read" if read_dormant else "write_matched_sham",
        "correct":sum(x["correct"] for x in episodes),
        "post_switch_correct":sum(x["correct"] for x in episodes[6:]),
        "dormant_correct":sum(x["dormant_correct"] for x in episodes),
        "post_switch_dormant_correct":sum(x["dormant_correct"] for x in episodes[6:]),
        "dormant_reads":sum(x["dormant_read_count"] for x in episodes),
        "dormant_read_correct":sum(x["dormant_read_correct"] for x in episodes),
        "total_cache_writes":sum(x["cache_writes"] for x in episodes),
        "episodes":episodes,
    }


def run():
    signatures={str(seed):signature(seed) for seed in range(64,72)}
    assert len(set(signatures.values()))==8, "frozen distinct motif sources"
    rows=[]
    for condition in ("STABLE","SWITCH"):
        for seed in range(64,72):
            pair=[evaluate(seed,condition,False),evaluate(seed,condition,True)]
            a,b=pair
            assert a["total_cache_writes"]==b["total_cache_writes"]
            assert [x["cache_entries"] for x in a["episodes"]]==[
                x["cache_entries"] for x in b["episodes"]]
            assert [x["cache_writes"] for x in a["episodes"]]==[
                x["cache_writes"] for x in b["episodes"]]
            rows.extend(pair)
    heldout=[r for r in rows if r["seed"]>=68]
    def total(condition,arm,field):
        return sum(r[field] for r in heldout if r["condition"]==condition and r["arm"]==arm)
    stable_sham=total("STABLE","write_matched_sham","correct")
    stable_cache=total("STABLE","dormant_memory_read","correct")
    switched_sham=total("SWITCH","write_matched_sham","correct")
    switched_cache=total("SWITCH","dormant_memory_read","correct")
    stable_post=total("STABLE","dormant_memory_read","post_switch_dormant_correct")
    switched_post=total("SWITCH","dormant_memory_read","post_switch_dormant_correct")
    stable_gain=stable_cache-stable_sham
    plasticity_loss=stable_post-switched_post
    positive=stable_gain>0 and total("STABLE","dormant_memory_read","dormant_read_correct")>0
    tradeoff=positive and plasticity_loss>0
    label=("STABILITY_PLASTICITY_TRADEOFF" if tradeoff else
           "STABLE_DORMANT_RECALL" if positive else "OTHERWISE_MIXED")
    return {
        "schema":"yggdrasil.y033-dormant-associative-recall.v1",
        "predecessor_head":"f119338d8cd9376a103742dc894e211d71066954",
        "classification":label,
        "unique_fingerprints":True,"fingerprints":signatures,
        "heldout_stable_sham_correct":stable_sham,
        "heldout_stable_cache_correct":stable_cache,
        "heldout_switched_sham_correct":switched_sham,
        "heldout_switched_cache_correct":switched_cache,
        "heldout_stable_memory_gain":stable_gain,
        "heldout_stable_post_switch_dormant_correct":stable_post,
        "heldout_switched_post_switch_dormant_correct":switched_post,
        "heldout_dormant_plasticity_loss":plasticity_loss,
        "rows":rows,"model_calls":0,
        "claim_limit":"Finite observed-only synthetic cue associations with global target change, not semantic cognition."
    }


if __name__=="__main__":
    result=run()
    assert result==run()
    print(json.dumps(result,sort_keys=True,indent=2))
