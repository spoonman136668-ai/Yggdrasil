#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c24_cell2_cell6_one_sided_decomposition_v1 as c24

PREREG="93073938d2fb21be6415154492be129c9ddef696"
PARENT_RUN="36304396514"
BELOW=0.134765625
PARTNER=6
LEVELS=list(range(8,17))

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def maturity(row): return bool(row["maturity"]["a25"]["pass"])

def one_pass():
    c23=c24.c23; c22=c23.c22; c20=c22.c20; c19=c20.c19; c16=c19.c17.c16; c3=c16.c3
    old_pressure=c3.pressure_lesion; old_parent=float(c16.parent.ALPHA); old_runtime=float(c16.parent.g.ALPHA); old_dose=tuple(c16.dose.ALPHAS)
    c16.parent.ALPHA=BELOW; c16.parent.g.ALPHA=BELOW; c16.dose.ALPHAS=c19.c17.EXTENDED; c3.pressure_lesion=c16.c5.fine_pressure
    groups=[]
    try:
        base=c3.lu2v.primary_manifests(c3.LU2VF1)
        for level in LEVELS:
            manifests=[c3.pressure_manifest(m,level) for m in base]
            byrep={int(m["replicate"]):m for m in manifests}
            m8=byrep[8]; mp=byrep[PARTNER]
            l8=sorted(m8["lesion"]); lp=sorted(mp["lesion"])
            only8=set(l8)-set(lp); onlyp=set(lp)-set(l8)
            eligible={2,10}.issubset(onlyp) and {6,14}.issubset(only8)
            if not eligible: raise AssertionError(f"C25 required cells not eligible level={level}")
            original=c22.run_manifest_with_lesion(m8,level,l8)
            full=c22.run_manifest_with_lesion(m8,level,lp)
            lesions={
                "add2":sorted(set(l8)|{2}),
                "add10":sorted(set(l8)|{10}),
                "remove6":sorted(set(l8)-{6}),
                "remove14":sorted(set(l8)-{14}),
                "add2_remove6":sorted((set(l8)|{2})-{6}),
                "add10_remove14":sorted((set(l8)|{10})-{14}),
            }
            arms={}
            for name,lesion in lesions.items():
                row=c22.run_manifest_with_lesion(m8,level,lesion)
                arms[name]={
                    "lesion":lesion,"maturity_pass":maturity(row),
                    "cardinality":len(lesion),"delta_vs_original":len(lesion)-len(l8),
                }
            groups.append({
                "level":level,"replicate":8,"partner":PARTNER,
                "original_failure":not maturity(original),"full_partner_rescue":maturity(full),
                "original_cardinality":len(l8),"eligible":eligible,"arms":arms
            })
    finally:
        c3.pressure_lesion=old_pressure; c16.parent.ALPHA=old_parent; c16.parent.g.ALPHA=old_runtime; c16.dose.ALPHAS=old_dose
    anchor_ok=all(g["original_failure"] and g["full_partner_rescue"] for g in groups)
    add2_pass=all(g["arms"]["add2"]["maturity_pass"] for g in groups)
    add10_fail=all(not g["arms"]["add10"]["maturity_pass"] for g in groups)
    rem6_pass=all(g["arms"]["remove6"]["maturity_pass"] for g in groups)
    rem14_fail=all(not g["arms"]["remove14"]["maturity_pass"] for g in groups)
    pair_pass=all(g["arms"]["add2_remove6"]["maturity_pass"] for g in groups)
    if not anchor_ok: cat="ANCHOR_NOT_REPRODUCED"
    elif add2_pass and add10_fail and rem6_pass and rem14_fail: cat="BOTH_FACTORS_INDEPENDENTLY_REPAIR"
    elif add2_pass and add10_fail and not (rem6_pass and rem14_fail): cat="CELL2_ADDITION_REPAIRS"
    elif rem6_pass and rem14_fail and not (add2_pass and add10_fail): cat="CELL6_REMOVAL_REPAIRS"
    elif (not add2_pass) and (not rem6_pass) and pair_pass: cat="PAIR_REQUIRED_FOR_REPAIR"
    else: cat="MIXED_REPAIR_DIRECTION"
    return {
        "groups":groups,"classification":cat,
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
        "alpha_exact":BELOW==c24.BELOW==0.134765625,
        "replicate8_partner6_exact":all(g["replicate"]==8 and g["partner"]==6 for g in a["groups"]),
        "all_required_cells_eligible":all(g["eligible"] for g in a["groups"]),
        "original_full_anchors_reproduced":all(g["original_failure"] and g["full_partner_rescue"] for g in a["groups"]),
        "one_sided_cardinality_exact":all(
            g["arms"]["add2"]["delta_vs_original"]==1 and g["arms"]["add10"]["delta_vs_original"]==1 and
            g["arms"]["remove6"]["delta_vs_original"]==-1 and g["arms"]["remove14"]["delta_vs_original"]==-1
            for g in a["groups"]),
        "paired_cardinality_exact":all(
            g["arms"]["add2_remove6"]["delta_vs_original"]==0 and g["arms"]["add10_remove14"]["delta_vs_original"]==0
            for g in a["groups"]),
        "runtime_alpha_restored":a["runtime_alpha_restored"],
        "dose_allowlist_restored":a["dose_allowlist_restored"],
        "pressure_lesion_restored":a["pressure_lesion_restored"],
    }
    cat=a["classification"]
    allowed={"BOTH_FACTORS_INDEPENDENTLY_REPAIR","CELL2_ADDITION_REPAIRS","CELL6_REMOVAL_REPAIRS","PAIR_REQUIRED_FOR_REPAIR","MIXED_REPAIR_DIRECTION","ANCHOR_NOT_REPRODUCED"}
    out={"schema":1,"experiment":"YGG-C25","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_C25_SYMMETRIC_REPAIR_DIRECTION":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
