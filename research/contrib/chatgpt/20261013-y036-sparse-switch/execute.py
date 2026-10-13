"""Y036: global vs sparse value switch, same live-overlap evidence, dormant repair."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PREVIOUS=Path(__file__).resolve().parent.parent/"20261013-y034-feedback-repair"/"execute.py"
_spec=importlib.util.spec_from_file_location("y034_frozen",PREVIOUS)
assert _spec and _spec.loader
y34=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(y34)
y33=y34.y33


def shared_switch_cue(seed):
    overlap=set(y33.active_keys(seed,5)).intersection(y33.active_keys(seed,6))
    assert len(overlap)==1
    return next(iter(overlap))


def actual_target(seed,key,ep,condition,shared):
    base=y33.target(seed,key,0,"STABLE")
    if ep<6:
        return base
    if condition=="UNIFORM" or (condition=="SPARSE" and key==shared):
        return (base+2)%4
    assert condition=="SPARSE"
    return base


def evaluate(seed,condition,correct_dormant):
    pivot=shared_switch_cue(seed)
    live={}
    dormant=OrderedDict()
    seen=set()
    rows=[]
    for ep in range(12):
        keys=y33.active_keys(seed,ep)
        predictions={key:live.get(key,dormant.get(key,0)) for key in keys}
        # Truth only becomes available to policies after all seven predictions.
        observed={key:actual_target(seed,key,ep,condition,pivot) for key in keys}
        returning=[key for key in keys if key in seen and key not in live]
        hits=sum(predictions[key]==observed[key] for key in keys)
        dormant_hits=sum(predictions[key]==observed[key] for key in returning)
        overlap=[key for key in keys if key in live]
        diffs=[(observed[key]-live[key])%4 for key in overlap]
        detected=(diffs[0] if diffs and len(set(diffs))==1 and diffs[0]!=0 else 0)
        for key in keys:
            dormant.pop(key,None)
        writes=0
        for key in sorted(set(live).difference(keys)):
            dormant.pop(key,None)
            dormant[key]=live[key]
            writes+=1
            while len(dormant)>9:
                dormant.popitem(last=False)
        updates=0
        if correct_dormant and detected:
            updates=len(dormant)
            for key in tuple(dormant):
                dormant[key]=(dormant[key]+detected)%4
        live=observed
        seen.update(keys)
        assert len(live)==7 and len(dormant)<=9 and len(live)+len(dormant)<=16
        rows.append({
            "episode":ep,"correct":hits,"dormant_correct":dormant_hits,
            "live_overlap":len(overlap),
            "overlap_evidence_delta":detected,
            "applied_correction":detected if correct_dormant else 0,
            "cache_writes":writes,"cache_entries":len(dormant),
            "maintenance_updates":updates
        })
    assert rows[6]["live_overlap"]==1
    assert rows[6]["overlap_evidence_delta"]==2
    return {
        "seed":seed,"cohort":"development" if seed<92 else "heldout",
        "condition":condition,"pivot":pivot,
        "arm":"local_global_correction" if correct_dormant else "unmodified",
        "post_correct":sum(r["correct"] for r in rows[7:]),
        "post_dormant_correct":sum(r["dormant_correct"] for r in rows[7:]),
        "maintenance_updates":sum(r["maintenance_updates"] for r in rows),
        "writes":sum(r["cache_writes"] for r in rows),
        "episodes":rows
    }


def run():
    fingerprints={str(s):y33.signature(s) for s in range(88,96)}
    assert len(set(fingerprints.values()))==8
    rows=[]
    for condition in ("UNIFORM","SPARSE"):
        for seed in range(88,96):
            a=evaluate(seed,condition,False)
            b=evaluate(seed,condition,True)
            assert a["writes"]==b["writes"]
            assert [r["cache_entries"] for r in a["episodes"]]==[
                r["cache_entries"] for r in b["episodes"]]
            assert [r["cache_writes"] for r in a["episodes"]]==[
                r["cache_writes"] for r in b["episodes"]]
            rows.extend((a,b))
    def total(cond,arm,field):
        return sum(r[field] for r in rows if r["seed"]>=92
                   and r["condition"]==cond and r["arm"]==arm)
    uu=total("UNIFORM","unmodified","post_correct")
    ur=total("UNIFORM","local_global_correction","post_correct")
    su=total("SPARSE","unmodified","post_correct")
    sr=total("SPARSE","local_global_correction","post_correct")
    if ur>uu and sr<su:
        classification="LOCAL_EVIDENCE_AMBIGUITY"
    else:
        classification="MIXED"
    return {
        "schema":"yggdrasil.y036-local-vs-global-switch.v1",
        "predecessor_head":"d7031e055c8566f0b90b0681dc8e9e2bdacf0e87",
        "classification":classification,
        "unique_input_signatures":True,"signatures":fingerprints,
        "uniform_unmodified_post_correct":uu,
        "uniform_repaired_post_correct":ur,
        "sparse_unmodified_post_correct":su,
        "sparse_repaired_post_correct":sr,
        "uniform_extra_maintenance":
            total("UNIFORM","local_global_correction","maintenance_updates"),
        "sparse_extra_maintenance":
            total("SPARSE","local_global_correction","maintenance_updates"),
        "rows":rows,"model_calls":0,
        "claim_limit":"Evidence ambiguity only for local live-overlap feedback policy under synthetic paired-world switch."
    }


if __name__=="__main__":
    result=run()
    assert result==run()
    print(json.dumps(result,sort_keys=True,indent=2))
