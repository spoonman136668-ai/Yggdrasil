"""Y035: falsify feedback-repair under key-dependent rather than global drift."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PRIOR=Path(__file__).resolve().parent.parent/"20261013-y034-feedback-repair"/"execute.py"
_spec=importlib.util.spec_from_file_location("y034_frozen",PRIOR)
assert _spec and _spec.loader
y34=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(y34)
y33=y34.y33


def target(seed,key,episode,condition):
    original=y33.target(seed,key,0,"STABLE")
    if episode<6:
        return original
    assert condition in ("UNIFORM","HETEROGENEOUS")
    delta=2 if condition=="UNIFORM" or key%2==1 else 1
    return (original+delta)%4


def evaluate(seed,condition,repair):
    live={}
    dormant=OrderedDict()
    seen=set()
    rows=[]
    for ep in range(12):
        active=y33.active_keys(seed,ep)
        pred={}
        for key in active:
            if key in live:
                pred[key]=live[key]
            elif key in dormant:
                pred[key]=dormant[key]
            else:
                pred[key]=0
        # Hidden labels only emitted by evaluator AFTER all predictions.
        truth={key:target(seed,key,ep,condition) for key in active}
        returning=[key for key in active if key in seen and key not in live]
        correct=sum(pred[key]==truth[key] for key in active)
        dormant_correct=sum(pred[key]==truth[key] for key in returning)
        overlapping=[key for key in active if key in live]
        deltas=[(truth[key]-live[key])%4 for key in overlapping]
        detect=(deltas[0] if len(deltas)>=2 and len(set(deltas))==1 and deltas[0]!=0
                else 0)
        for key in active:
            dormant.pop(key,None)
        writes=0
        for key in sorted(set(live).difference(active)):
            dormant.pop(key,None)
            dormant[key]=live[key]
            writes+=1
            while len(dormant)>9:
                dormant.popitem(last=False)
        repair_ops=0
        if repair and detect:
            repair_ops=len(dormant)
            for key in tuple(dormant):
                dormant[key]=(dormant[key]+detect)%4
        live=truth
        seen.update(active)
        assert len(live)==7 and len(dormant)<=9 and len(live)+len(dormant)<=16
        assert not set(live).intersection(dormant)
        rows.append({
            "episode":ep,"correct":correct,"returning":len(returning),
            "dormant_correct":dormant_correct,
            "overlap_count":len(overlapping),
            "evidence_delta":detect,
            "applied_delta":detect if repair else 0,
            "false_global_correction":bool(repair and detect and condition=="HETEROGENEOUS"),
            "maintenance_updates":repair_ops,
            "cache_writes":writes,"cache_entries":len(dormant),
        })
    return {
        "seed":seed,"cohort":"development" if seed<84 else "heldout",
        "condition":condition,
        "arm":"conservative_feedback_repair" if repair else "unmodified_cache",
        "correct":sum(x["correct"] for x in rows),
        "post_correct":sum(x["correct"] for x in rows[7:]),
        "post_dormant_correct":sum(x["dormant_correct"] for x in rows[7:]),
        "repair_events":sum(bool(x["applied_delta"]) for x in rows),
        "false_global_events":sum(bool(x["false_global_correction"]) for x in rows),
        "maintenance_updates":sum(x["maintenance_updates"] for x in rows),
        "cache_writes":sum(x["cache_writes"] for x in rows),
        "episodes":rows
    }


def run():
    fingerprints={str(seed):y33.signature(seed) for seed in range(80,88)}
    assert len(set(fingerprints.values()))==8
    rows=[]
    for condition in ("UNIFORM","HETEROGENEOUS"):
        for seed in range(80,88):
            a=evaluate(seed,condition,False)
            b=evaluate(seed,condition,True)
            assert a["cache_writes"]==b["cache_writes"]
            assert [x["cache_entries"] for x in a["episodes"]]==[
                x["cache_entries"] for x in b["episodes"]]
            assert [x["cache_writes"] for x in a["episodes"]]==[
                x["cache_writes"] for x in b["episodes"]]
            rows.extend((a,b))
    def aggregate(cond,arm,key):
        return sum(r[key] for r in rows if r["seed"]>=84
                   and r["condition"]==cond and r["arm"]==arm)
    unmodified="unmodified_cache"
    changed="conservative_feedback_repair"
    uniform_orig=aggregate("UNIFORM",unmodified,"post_correct")
    uniform_repaired=aggregate("UNIFORM",changed,"post_correct")
    heterogeneous_orig=aggregate("HETEROGENEOUS",unmodified,"post_correct")
    heterogeneous_repaired=aggregate("HETEROGENEOUS",changed,"post_correct")
    false_global=aggregate("HETEROGENEOUS",changed,"false_global_events")
    if uniform_repaired>uniform_orig and heterogeneous_repaired>=heterogeneous_orig and false_global==0:
        outcome="GATED_REPAIR_SELECTIVITY"
    elif heterogeneous_repaired<heterogeneous_orig:
        outcome="HARM"
    else:
        outcome="MIXED"
    return {
        "schema":"yggdrasil.y035-heterogeneous-cue-repair-falsification.v1",
        "predecessor_head":"08ab3be3bd28516b094084cc5722bf16876af7de",
        "classification":outcome,
        "fingerprints":fingerprints,
        "uniform_post_unmodified_correct":uniform_orig,
        "uniform_post_repaired_correct":uniform_repaired,
        "heterogeneous_post_unmodified_correct":heterogeneous_orig,
        "heterogeneous_post_repaired_correct":heterogeneous_repaired,
        "heterogeneous_false_global_corrections":false_global,
        "uniform_repair_events":aggregate("UNIFORM",changed,"repair_events"),
        "heterogeneous_repair_events":aggregate("HETEROGENEOUS",changed,"repair_events"),
        "heterogeneous_extra_maintenance":aggregate("HETEROGENEOUS",changed,"maintenance_updates"),
        "rows":rows,"model_calls":0,
        "claim_limit":"Observed-only synthetic global-correction gate under hidden heterogeneous switch; not general developmental intelligence."
    }


if __name__=="__main__":
    result=run()
    assert result==run()
    print(json.dumps(result,sort_keys=True,indent=2))
