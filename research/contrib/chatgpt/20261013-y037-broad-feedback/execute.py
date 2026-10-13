"""Y037: compare local and broader observed-feedback shift detection."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PRIOR=Path(__file__).resolve().parent.parent/"20261013-y036-sparse-switch"/"execute.py"
_spec=importlib.util.spec_from_file_location("y036_frozen",PRIOR)
assert _spec and _spec.loader
y36=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(y36)
y33=y36.y33


def evaluate(seed,condition,arm):
    pivot=y36.shared_switch_cue(seed)
    live={}
    cache=OrderedDict()
    seen=set()
    episodes=[]
    for ep in range(12):
        current=y33.active_keys(seed,ep)
        remembered={
            key:(live[key] if key in live else cache[key])
            for key in current if key in live or key in cache
        }
        prediction={key:remembered.get(key,0) for key in current}
        # Only current seven cue labels become visible as feedback after prediction.
        truth={key:y36.actual_target(seed,key,ep,condition,pivot) for key in current}
        returning=[key for key in current if key in seen and key not in live]
        correct=sum(prediction[key]==truth[key] for key in current)
        dormant_correct=sum(prediction[key]==truth[key] for key in returning)
        overlap=[key for key in current if key in live]
        if arm=="BROAD_OBSERVED":
            observable=list(remembered)
        elif arm=="LOCAL_ONLY":
            observable=overlap
        else:
            assert arm=="UNMODIFIED"
            observable=[]
        deltas=[(truth[key]-remembered[key])%4 for key in observable]
        delta=(deltas[0] if deltas and len(set(deltas))==1 and deltas[0]!=0
               and (arm=="LOCAL_ONLY" or len(deltas)>=2) else 0)
        for key in current:
            cache.pop(key,None)
        writes=0
        for key in sorted(set(live).difference(current)):
            cache.pop(key,None)
            cache[key]=live[key]
            writes+=1
            while len(cache)>9:
                cache.popitem(last=False)
        updated=0
        if delta:
            updated=len(cache)
            for key in tuple(cache):
                cache[key]=(cache[key]+delta)%4
        live=truth
        seen.update(current)
        assert len(live)==7 and len(cache)<=9 and len(live)+len(cache)<=16
        episodes.append({
            "episode":ep,"correct":correct,"dormant_correct":dormant_correct,
            "overlap":len(overlap),"evidence_comparisons":len(observable),
            "detected_delta":delta,"maintenance_updates":updated,
            "cache_writes":writes,"cache_entries":len(cache)
        })
    assert episodes[6]["overlap"]==1
    return {
        "seed":seed,"cohort":"development" if seed<112 else "heldout",
        "condition":condition,"arm":arm,"pivot":pivot,
        "post_correct":sum(r["correct"] for r in episodes[7:]),
        "post_dormant_correct":sum(r["dormant_correct"] for r in episodes[7:]),
        "correction_events":sum(bool(r["detected_delta"]) for r in episodes),
        "maintenance_updates":sum(r["maintenance_updates"] for r in episodes),
        "evidence_comparisons":sum(r["evidence_comparisons"] for r in episodes),
        "cache_writes":sum(r["cache_writes"] for r in episodes),
        "episodes":episodes
    }


def run():
    signatures={str(seed):y33.signature(seed) for seed in range(108,116)}
    assert len(set(signatures.values()))==8
    arms=("UNMODIFIED","LOCAL_ONLY","BROAD_OBSERVED")
    rows=[]
    for condition in ("UNIFORM","SPARSE"):
        for seed in range(108,116):
            trio=[evaluate(seed,condition,arm) for arm in arms]
            assert len({r["cache_writes"] for r in trio})==1
            assert len({
                tuple(x["cache_entries"] for x in r["episodes"]) for r in trio
            })==1
            rows.extend(trio)
    def total(cond,arm,field):
        return sum(r[field] for r in rows if r["seed"]>=112
                   and r["condition"]==cond and r["arm"]==arm)
    uni_base=total("UNIFORM","UNMODIFIED","post_correct")
    uni_local=total("UNIFORM","LOCAL_ONLY","post_correct")
    uni_broad=total("UNIFORM","BROAD_OBSERVED","post_correct")
    spr_base=total("SPARSE","UNMODIFIED","post_correct")
    spr_local=total("SPARSE","LOCAL_ONLY","post_correct")
    spr_broad=total("SPARSE","BROAD_OBSERVED","post_correct")
    uniform_events=total("UNIFORM","BROAD_OBSERVED","correction_events")
    sparse_events=total("SPARSE","BROAD_OBSERVED","correction_events")
    if uni_broad>uni_base and spr_broad>=spr_base and uniform_events>0 and sparse_events==0:
        outcome="BROAD_FEEDBACK_DISCRIMINATION"
    elif spr_broad<spr_base:
        outcome="HARM"
    else:
        outcome="MIXED"
    return {
        "schema":"yggdrasil.y037-broad-observed-cue-gate.v1",
        "predecessor_head":"38bd18325c83f380f15258216ace790cf44cdb52",
        "classification":outcome,
        "unique_signatures":True,"signatures":signatures,
        "uniform_unmodified_post_correct":uni_base,
        "uniform_local_post_correct":uni_local,
        "uniform_broad_post_correct":uni_broad,
        "sparse_unmodified_post_correct":spr_base,
        "sparse_local_post_correct":spr_local,
        "sparse_broad_post_correct":spr_broad,
        "broad_uniform_repair_events":uniform_events,
        "broad_sparse_repair_events":sparse_events,
        "broad_extra_comparisons":total("UNIFORM","BROAD_OBSERVED","evidence_comparisons")+
                                  total("SPARSE","BROAD_OBSERVED","evidence_comparisons"),
        "broad_maintenance_updates":total("UNIFORM","BROAD_OBSERVED","maintenance_updates")+
                                     total("SPARSE","BROAD_OBSERVED","maintenance_updates"),
        "rows":rows,"model_calls":0,
        "claim_limit":"Synthetic feedback condition discriminator with known sparse-vs-uniform environment; not open-ended cognitive repair."
    }


if __name__=="__main__":
    result=run()
    assert result==run()
    print(json.dumps(result,sort_keys=True,indent=2))
