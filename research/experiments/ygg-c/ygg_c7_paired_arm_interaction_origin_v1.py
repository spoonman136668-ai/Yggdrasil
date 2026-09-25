#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c6_transition_cell_factorial_v1 as c6

PREREG="50fbead52ad123670736f6621f7074d9856e2595"
PARENT_CLOSURE="d1bc71b54b0954da561f5ff07a70d00b4cd628b2"
ACCEPTED_A25={
    "000":True,"100":False,"010":True,"001":True,
    "110":False,"101":True,"011":True,"111":True,
}

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def stream_noncollapse_arm(base_rows,rows,arm):
    by_rep={r["manifest"]["replicate"]:r for r in base_rows}
    for row in rows:
        rep=row["manifest"]["replicate"]
        base=by_rep[rep]
        for ph in range(5):
            for stream in ("C","S"):
                b=base[arm]["stream_phase"][str(ph)][stream]
                v=row[arm]["stream_phase"][str(ph)][stream]
                if b>=4 and v<0.75*b:
                    return False
    return True

def summarize_arm(rows,base_rows,arm):
    area=sum(r[arm]["events"]["correct_completion_area_phases0_4"] for r in rows)
    base_area=sum(r[arm]["events"]["correct_completion_area_phases0_4"] for r in base_rows)
    ratio=area/base_area if base_area else None
    incorrect=sum(r[arm]["incorrect_done"] for r in rows)
    prefix=arm
    matching=all(
        r["integrity"][prefix+"_duplicate_cell"] and r["integrity"][prefix+"_duplicate_request"]
        for r in rows
    )
    maturity=all(r["maturity"][arm]["pass"] for r in rows)
    streams=stream_noncollapse_arm(base_rows,rows,arm)
    retained=bool(
        ratio is not None and ratio>=0.90
        and incorrect==0 and matching and maturity and streams
    )
    return {
        "correct_completion_area":area,
        "parent_correct_completion_area":base_area,
        "retention_ratio_vs_l8":ratio,
        "correct_done_total":sum(r[arm]["correct_done"] for r in rows),
        "incorrect_done_total":incorrect,
        "expired_total":sum(r[arm]["expired"] for r in rows),
        "final_backlog_total":sum(r[arm]["backlog"] for r in rows),
        "maturity_pass_count":sum(1 for r in rows if r["maturity"][arm]["pass"]),
        "matching_integrity":matching,
        "stream_noncollapse":streams,
        "retained":retained,
    }

def classify_arm(run,arm):
    retained={}
    summaries={}
    for g in run["groups"]:
        regenerated_manifests,rows=c6.run_condition(run["base_manifests"],g["condition"])
        if canonical(regenerated_manifests)!=canonical(g["manifests"]):
            raise AssertionError("C7 regenerated C6 manifests differ from frozen group")
        s=summarize_arm(rows,run["parent"],arm)
        summaries[g["condition"]]=s
        retained[g["condition"]]=bool(s["retained"])
    path=bool(
        retained["000"]
        and not retained["100"]
        and not retained["110"]
        and retained["111"]
    )
    effects={}
    context=[]
    for slot in ("A","B","C"):
        rows=c6.paired_effects(retained,slot)
        vals={r["effect"] for r in rows}
        effects[slot]=rows
        if len(vals)>1:
            context.append(slot)
    if not path:
        classification="PATH_NOT_REPRODUCED"
    elif context:
        classification="INTERACTION_DRIVEN"
    else:
        classification="SINGLE_DIRECTION_OR_ADDITIVE"
    return {
        "arm":arm,
        "retained_by_condition":retained,
        "summaries":summaries,
        "c6_path_reproduced":path,
        "paired_effects":effects,
        "context_dependent_slots":context,
        "classification":classification,
        "interaction_driven":bool(path and context),
    }

def origin(a0,a25):
    if a0["interaction_driven"] and a25["interaction_driven"]:
        exact=(
            a0["retained_by_condition"]==a25["retained_by_condition"]
            and a0["context_dependent_slots"]==a25["context_dependent_slots"]
            and a0["paired_effects"]==a25["paired_effects"]
        )
        return "SUBSTRATE_SHARED_EXACT" if exact else "ARM_MODULATED"
    if a25["interaction_driven"] and not a0["interaction_driven"]:
        return "A25_INTERACTION_ONLY"
    if a0["interaction_driven"] and not a25["interaction_driven"]:
        return "A0_INTERACTION_ONLY"
    return "NEITHER_INTERACTION"

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    first=c6.one_pass()
    second=c6.one_pass()
    c6_checks,parent_hash=c6.validity(first,second)
    a0=classify_arm(first,"a0")
    a25=classify_arm(first,"a25")
    a25_exact=a25["retained_by_condition"]==ACCEPTED_A25
    category=origin(a0,a25)
    allowed={
        "SUBSTRATE_SHARED_EXACT","ARM_MODULATED","A25_INTERACTION_ONLY",
        "A0_INTERACTION_ONLY","NEITHER_INTERACTION",
    }
    checks=dict(c6_checks)
    checks["a25_accepted_c6_map_exact"]=a25_exact
    checks["origin_classification_produced"]=category in allowed
    valid=all(checks.values())
    q={
        "YGG_C7_PAIRED_ARM_INTERACTION_ORIGIN":valid,
        "origin_classification":category,
        "a0_interaction_classification":a0["classification"],
        "a25_interaction_classification":a25["classification"],
        "a25_accepted_c6_map_exact":a25_exact,
    }
    out={
        "schema":1,
        "experiment":"YGG-C7",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "parent_reference_sha256":parent_hash,
        "duplicate_sha256":hashlib.sha256(canonical(first)).hexdigest(),
        "validity":checks,
        "valid":valid,
        "qualification":q,
        "a0":a0,
        "a25":a25,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
