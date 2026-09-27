#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c27_38to42_one_toggle_basin_v1 as c27

PREREG="53a981832ac9c2143e24922c365f92707b8bbf7b"
PARENT_RUN="36316836609"
BELOW=0.134765625
LEVELS=list(range(8,17))
CRITICAL=(4,5,41)

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def maturity(row): return bool(row["maturity"]["a25"]["pass"])

def one_pass():
    c26=c27.c26; c25=c26.c25; c24=c25.c24; c23=c24.c23; c22=c23.c22
    c20=c22.c20; c19=c20.c19; c16=c19.c17.c16; c3=c16.c3
    old_pressure=c3.pressure_lesion; old_parent=float(c16.parent.ALPHA); old_runtime=float(c16.parent.g.ALPHA); old_dose=tuple(c16.dose.ALPHAS)
    c16.parent.ALPHA=BELOW; c16.parent.g.ALPHA=BELOW; c16.dose.ALPHAS=c19.c17.EXTENDED; c3.pressure_lesion=c16.c5.fine_pressure
    groups=[]
    try:
        base=c3.lu2v.primary_manifests(c3.LU2VF1)
        for level in LEVELS:
            manifests=[c3.pressure_manifest(m,level) for m in base]
            m8={int(m["replicate"]):m for m in manifests}[8]
            l8=sorted(m8["lesion"])
            original=c22.run_manifest_with_lesion(m8,level,l8)
            base38=sorted((set(l8)-{38})|{42})
            brow=c22.run_manifest_with_lesion(m8,level,base38)
            crit=[]
            for cell in CRITICAL:
                if cell in base38: raise AssertionError(f"C28 critical unexpectedly present level={level} cell={cell}")
                addles=sorted(set(base38)|{cell})
                addrow=c22.run_manifest_with_lesion(m8,level,addles)
                comps=[]
                for rem in base38:
                    lesion=sorted((set(base38)|{cell})-{rem})
                    row=c22.run_manifest_with_lesion(m8,level,lesion)
                    comps.append({
                        "removed":rem,"maturity_pass":maturity(row),"lesion":lesion,
                        "cardinality":len(lesion),"symdiff":sorted(set(base38)^set(lesion))
                    })
                crit.append({
                    "critical_cell":cell,"addition_failure":not maturity(addrow),
                    "rescuing_removals":[x["removed"] for x in comps if x["maturity_pass"]],
                    "failing_removals":[x["removed"] for x in comps if not x["maturity_pass"]],
                    "compensations":comps
                })
            groups.append({
                "level":level,"replicate":8,
                "original_failure":not maturity(original),
                "base38to42_rescue":maturity(brow),
                "original_lesion":l8,"base38to42_lesion":base38,
                "critical":crit
            })
    finally:
        c3.pressure_lesion=old_pressure; c16.parent.ALPHA=old_parent; c16.parent.g.ALPHA=old_runtime; c16.dose.ALPHAS=old_dose
    anchors=all(g["original_failure"] and g["base38to42_rescue"] and all(c["addition_failure"] for c in g["critical"]) for g in groups)
    any_rescue=any(c["rescuing_removals"] for g in groups for c in g["critical"])
    all_compensable=all(c["rescuing_removals"] for g in groups for c in g["critical"])
    if not anchors: cat="ANCHOR_NOT_REPRODUCED"
    elif all_compensable: cat="ALL_CRITICAL_ADDITIONS_COMPENSABLE"
    elif any_rescue: cat="PARTIAL_CRITICAL_COMPENSABILITY"
    else: cat="NO_SINGLE_REMOVAL_COMPENSATION"
    return {
        "groups":groups,"classification":cat,
        "runtime_alpha_restored":float(c16.parent.ALPHA)==old_parent and float(c16.parent.g.ALPHA)==old_runtime,
        "dose_allowlist_restored":tuple(c16.dose.ALPHAS)==old_dose,
        "pressure_lesion_restored":c3.pressure_lesion is old_pressure,
    }

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one_pass(); b=one_pass(); ba=canonical(a)
    allcomps=[x for g in a["groups"] for c in g["critical"] for x in c["compensations"]]
    validity={
        "duplicate_analysis_byte_identical":ba==canonical(b),
        "levels_exact":[g["level"] for g in a["groups"]]==LEVELS,
        "alpha_exact":BELOW==c27.BELOW==0.134765625,
        "replicate8_exact":all(g["replicate"]==8 for g in a["groups"]),
        "critical_set_exact":all([c["critical_cell"] for c in g["critical"]]==list(CRITICAL) for g in a["groups"]),
        "anchors_reproduced":all(g["original_failure"] and g["base38to42_rescue"] and all(c["addition_failure"] for c in g["critical"]) for g in a["groups"]),
        "exhaustive_base_present_removals":all(all([x["removed"] for x in c["compensations"]]==g["base38to42_lesion"] for c in g["critical"]) for g in a["groups"]),
        "cardinality_preserved":True,
        "compensation_shape_exact":all(len(x["symdiff"])==2 and x["removed"] in x["symdiff"] for x in allcomps),
        "runtime_alpha_restored":a["runtime_alpha_restored"],
        "dose_allowlist_restored":a["dose_allowlist_restored"],
        "pressure_lesion_restored":a["pressure_lesion_restored"],
    }
    # Explicit cardinality and critical-cell membership checks outside compact comprehension.
    validity["cardinality_preserved"]=all(
        all(all(x["cardinality"]==len(g["base38to42_lesion"]) and c["critical_cell"] in x["lesion"] and x["removed"] not in x["lesion"]
                for x in c["compensations"]) for c in g["critical"])
        for g in a["groups"]
    )
    cat=a["classification"]
    allowed={"ALL_CRITICAL_ADDITIONS_COMPENSABLE","PARTIAL_CRITICAL_COMPENSABILITY","NO_SINGLE_REMOVAL_COMPENSATION","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-C28","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_C28_CRITICAL_ADDITION_COMPENSATION":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
