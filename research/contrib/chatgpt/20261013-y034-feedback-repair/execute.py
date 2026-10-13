"""Y034: observed-feedback dormant cache repair under global target drift."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PREVIOUS=Path(__file__).resolve().parent.parent/"20261013-y033-associative-recall"/"execute.py"
_spec=importlib.util.spec_from_file_location("y033_frozen",PREVIOUS)
assert _spec and _spec.loader
y33=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(y33)


def evaluate(seed,condition,repair):
    live={}
    dormant=OrderedDict()
    seen=set()
    rows=[]
    for episode in range(12):
        active=y33.active_keys(seed,episode)
        predicted={}
        sources={}
        for key in active:
            if key in live:
                predicted[key]=live[key]
                sources[key]="live"
            elif key in dormant:
                predicted[key]=dormant[key]
                sources[key]="dormant"
            else:
                predicted[key]=0
                sources[key]="default"
        # Feedback becomes available only after all predictions.
        labels={key:y33.target(seed,key,episode,condition) for key in active}
        returning=[key for key in active if key in seen and key not in live]
        correct=sum(predicted[key]==labels[key] for key in active)
        dormant_correct=sum(predicted[key]==labels[key] for key in returning)
        overlap=[key for key in active if key in live]
        deltas=[(labels[key]-live[key])%4 for key in overlap]
        detected=(deltas[0] if deltas and len(set(deltas))==1 and deltas[0]!=0 else 0)
        for key in active:
            dormant.pop(key,None)
        cache_writes=0
        for key in sorted(set(live).difference(active)):
            dormant.pop(key,None)
            dormant[key]=live[key]
            cache_writes+=1
            while len(dormant)>9:
                dormant.popitem(last=False)
        correction_updates=0
        if repair and detected:
            correction_updates=len(dormant)
            for key in tuple(dormant):
                dormant[key]=(dormant[key]+detected)%4
        live=labels
        seen.update(active)
        assert len(live)==7 and len(dormant)<=9
        assert len(live)+len(dormant)<=16
        assert not set(live).intersection(dormant)
        rows.append({
            "episode":episode,"correct":correct,
            "returning_dormant":len(returning),
            "returning_dormant_correct":dormant_correct,
            "overlap_live":len(overlap),
            "evidence_delta":detected,
            "applied_correction":detected if repair else 0,
            "correction_maintenance_updates":correction_updates,
            "cache_writes":cache_writes,"cache_entries":len(dormant),
        })
    return {
        "seed":seed,"cohort":"development" if seed<76 else "heldout",
        "condition":condition,
        "arm":"feedback_repair" if repair else "unmodified_cache",
        "total_correct":sum(r["correct"] for r in rows),
        "post_switch_correct":sum(r["correct"] for r in rows[7:]),
        "post_switch_dormant_correct":sum(r["returning_dormant_correct"] for r in rows[7:]),
        "maintenance_updates":sum(r["correction_maintenance_updates"] for r in rows),
        "repair_events":sum(bool(r["applied_correction"]) for r in rows),
        "total_cache_writes":sum(r["cache_writes"] for r in rows),
        "episodes":rows,
    }


def run():
    signatures={str(seed):y33.signature(seed) for seed in range(72,80)}
    assert len(set(signatures.values()))==8
    rows=[]
    for condition in ("STABLE","SWITCH"):
        for seed in range(72,80):
            a=evaluate(seed,condition,False)
            b=evaluate(seed,condition,True)
            assert a["total_cache_writes"]==b["total_cache_writes"]
            assert [r["cache_entries"] for r in a["episodes"]]==[
                r["cache_entries"] for r in b["episodes"]]
            assert [r["cache_writes"] for r in a["episodes"]]==[
                r["cache_writes"] for r in b["episodes"]]
            rows.extend((a,b))
    def total(condition,arm,metric):
        return sum(r[metric] for r in rows if r["seed"]>=76
                   and r["condition"]==condition and r["arm"]==arm)
    stable_baseline=total("STABLE","unmodified_cache","total_correct")
    stable_repaired=total("STABLE","feedback_repair","total_correct")
    switch_baseline=total("SWITCH","unmodified_cache","post_switch_correct")
    switch_repaired=total("SWITCH","feedback_repair","post_switch_correct")
    maintenance=total("SWITCH","feedback_repair","maintenance_updates")
    events=total("SWITCH","feedback_repair","repair_events")
    if switch_repaired>switch_baseline and stable_repaired>=stable_baseline and events>0:
        classification="OBSERVED_REPAIR_BENEFIT"
    elif switch_repaired<switch_baseline:
        classification="HARM"
    else:
        classification="NEUTRAL_MIXED"
    return {
        "schema":"yggdrasil.y034-feedback-triggered-dormant-repair.v1",
        "predecessor_head":"719cf42fd7df385483bb17a6a3c0002bdcc99942",
        "classification":classification,
        "unique_fingerprints":True,"fingerprints":signatures,
        "heldout_stable_baseline_correct":stable_baseline,
        "heldout_stable_repaired_correct":stable_repaired,
        "heldout_switch_post_baseline_correct":switch_baseline,
        "heldout_switch_post_repaired_correct":switch_repaired,
        "heldout_switch_post_dormant_baseline_correct":
            total("SWITCH","unmodified_cache","post_switch_dormant_correct"),
        "heldout_switch_post_dormant_repaired_correct":
            total("SWITCH","feedback_repair","post_switch_dormant_correct"),
        "heldout_switch_repair_events":events,
        "heldout_switch_extra_maintenance_updates":maintenance,
        "rows":rows,"model_calls":0,
        "claim_limit":"Predeclared shared-delta repair on synthetic symbolic memory after observed feedback; not general cognition."
    }


if __name__=="__main__":
    result=run()
    assert result==run()
    print(json.dumps(result,sort_keys=True,indent=2))
