#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c26_dual_rescue_basin_compatibility_v1 as c26

PREREG="6cd01a07abf1b7cd3dd5d5a3a539861ff2101bba"
PARENT_RUN="36312692184"
BELOW=0.134765625
LEVELS=list(range(8,17))
CELLS=list(range(64))

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def maturity(row): return bool(row["maturity"]["a25"]["pass"])

def one_pass():
    c25=c26.c25; c24=c25.c24; c23=c24.c23; c22=c23.c22
    c20=c22.c20; c19=c20.c19; c16=c19.c17.c16; c3=c16.c3
    old_pressure=c3.pressure_lesion; old_parent=float(c16.parent.ALPHA); old_runtime=float(c16.parent.g.ALPHA); old_dose=tuple(c16.dose.ALPHAS)
    c16.parent.ALPHA=BELOW; c16.parent.g.ALPHA=BELOW; c16.dose.ALPHAS=c19.c17.EXTENDED; c3.pressure_lesion=c16.c5.fine_pressure
    groups=[]
    try:
        base=c3.lu2v.primary_manifests(c3.LU2VF1)
        for level in LEVELS:
            manifests=[c3.pressure_manifest(m,level) for m in base]
            byrep={int(m["replicate"]):m for m in manifests}
            m8=byrep[8]; l8=sorted(m8["lesion"])
            original=c22.run_manifest_with_lesion(m8,level,l8)
            base38=sorted((set(l8)-{38})|{42})
            brow=c22.run_manifest_with_lesion(m8,level,base38)
            arms=[]
            for cell in CELLS:
                s=set(base38)
                was_present=cell in s
                if was_present: s.remove(cell)
                else: s.add(cell)
                lesion=sorted(s)
                row=c22.run_manifest_with_lesion(m8,level,lesion)
                symdiff=sorted(set(base38)^set(lesion))
                arms.append({
                    "cell":cell,"action":"REMOVE" if was_present else "ADD",
                    "maturity_pass":maturity(row),"lesion":lesion,
                    "delta_vs_base":len(lesion)-len(base38),
                    "symmetric_difference":symdiff
                })
            groups.append({
                "level":level,"replicate":8,"original_failure":not maturity(original),
                "base38to42_rescue":maturity(brow),"original_lesion":l8,
                "base38to42_lesion":base38,"arms":arms
            })
    finally:
        c3.pressure_lesion=old_pressure; c16.parent.ALPHA=old_parent; c16.parent.g.ALPHA=old_runtime; c16.dose.ALPHAS=old_dose
    per_cell=[]
    for cell in CELLS:
        rows=[next(a for a in g["arms"] if a["cell"]==cell) for g in groups]
        per_cell.append({
            "cell":cell,
            "fail_levels":[g["level"] for g,a in zip(groups,rows) if not a["maturity_pass"]],
            "rescue_levels":[g["level"] for g,a in zip(groups,rows) if a["maturity_pass"]],
            "actions":[a["action"] for a in rows]
        })
    anchors=all(g["original_failure"] and g["base38to42_rescue"] for g in groups)
    universal_critical=[x["cell"] for x in per_cell if x["fail_levels"]==LEVELS]
    any_fail=any(x["fail_levels"] for x in per_cell)
    if not anchors: cat="ANCHOR_NOT_REPRODUCED"
    elif not any_fail: cat="ONE_TOGGLE_BASIN_ROBUST"
    elif universal_critical: cat="ONE_TOGGLE_UNIVERSAL_CRITICAL"
    else: cat="MIXED_ONE_TOGGLE_BASIN"
    return {
        "groups":groups,"per_cell":per_cell,"universal_critical_cells":universal_critical,
        "classification":cat,
        "runtime_alpha_restored":float(c16.parent.ALPHA)==old_parent and float(c16.parent.g.ALPHA)==old_runtime,
        "dose_allowlist_restored":tuple(c16.dose.ALPHAS)==old_dose,
        "pressure_lesion_restored":c3.pressure_lesion is old_pressure,
    }

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one_pass(); b=one_pass(); ba=canonical(a)
    validity={
        "duplicate_analysis_byte_identical":ba==canonical(b),
        "levels_exact":[g["level"] for g in a["groups"]]==LEVELS,
        "alpha_exact":BELOW==c26.BELOW==0.134765625,
        "replicate8_exact":all(g["replicate"]==8 for g in a["groups"]),
        "original_and_38to42_anchors_reproduced":all(g["original_failure"] and g["base38to42_rescue"] for g in a["groups"]),
        "base38to42_exact":all(38 not in g["base38to42_lesion"] and 42 in g["base38to42_lesion"] and len(g["base38to42_lesion"])==len(g["original_lesion"]) for g in a["groups"]),
        "exact_64_toggle_arms_each_level":all([x["cell"] for x in g["arms"]]==CELLS for g in a["groups"]),
        "one_cell_membership_difference_each_arm":all(all(a0["symmetric_difference"]==[a0["cell"]] and abs(a0["delta_vs_base"])==1 for a0 in g["arms"]) for g in a["groups"]),
        "runtime_alpha_restored":a["runtime_alpha_restored"],
        "dose_allowlist_restored":a["dose_allowlist_restored"],
        "pressure_lesion_restored":a["pressure_lesion_restored"],
    }
    cat=a["classification"]
    allowed={"ONE_TOGGLE_BASIN_ROBUST","ONE_TOGGLE_UNIVERSAL_CRITICAL","MIXED_ONE_TOGGLE_BASIN","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-C27","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_C27_38TO42_ONE_TOGGLE_BASIN":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
