#!/usr/bin/env python3
import copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c23_rescue_basin_reverse_substitution_v1 as c23

PREREG="2d9355dc7ed07f35947fc0b505804523d1242dbc"
PARENT_RUN="36282449458"
BELOW=0.134765625
PARTNER=6
LEVELS=list(range(8,17))

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def maturity(row): return bool(row["maturity"]["a25"]["pass"])

def one_pass():
    c22=c23.c22; c20=c22.c20; c19=c20.c19; c16=c19.c17.c16; c3=c16.c3
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
            if not eligible: raise AssertionError(f"C24 required cells not eligible level={level}")
            original=c22.run_manifest_with_lesion(m8,level,l8)
            full=c22.run_manifest_with_lesion(m8,level,lp)
            lesions={
                "remove2":sorted(set(lp)-{2}),
                "remove10":sorted(set(lp)-{10}),
                "add6":sorted(set(lp)|{6}),
                "add14":sorted(set(lp)|{14}),
                "replace2to6":sorted((set(lp)-{2})|{6}),
                "replace10to14":sorted((set(lp)-{10})|{14}),
            }
            arms={}
            for name,lesion in lesions.items():
                row=c22.run_manifest_with_lesion(m8,level,lesion)
                arms[name]={
                    "lesion":lesion,"maturity_pass":maturity(row),
                    "cardinality":len(lesion),
                    "delta_vs_full":len(lesion)-len(lp),
                }
            groups.append({
                "level":level,"replicate":8,"partner":PARTNER,
                "original_failure":not maturity(original),"full_partner_rescue":maturity(full),
                "full_partner_cardinality":len(lp),"eligible":eligible,
                "arms":arms,
            })
    finally:
        c3.pressure_lesion=old_pressure; c16.parent.ALPHA=old_parent; c16.parent.g.ALPHA=old_runtime; c16.dose.ALPHAS=old_dose
    anchor_ok=all(
        g["original_failure"] and g["full_partner_rescue"] and
        not g["arms"]["replace2to6"]["maturity_pass"] and
        g["arms"]["replace10to14"]["maturity_pass"]
        for g in groups
    )
    rem2_fail=all(not g["arms"]["remove2"]["maturity_pass"] for g in groups)
    rem10_pass=all(g["arms"]["remove10"]["maturity_pass"] for g in groups)
    add6_fail=all(not g["arms"]["add6"]["maturity_pass"] for g in groups)
    add14_pass=all(g["arms"]["add14"]["maturity_pass"] for g in groups)
    if not anchor_ok: cat="ANCHOR_NOT_REPRODUCED"
    elif rem2_fail and rem10_pass and add6_fail and add14_pass: cat="BOTH_FACTORS_INDEPENDENTLY_SUFFICIENT"
    elif rem2_fail and rem10_pass and not (add6_fail and add14_pass): cat="CELL2_REMOVAL_SUFFICIENT"
    elif add6_fail and add14_pass and not (rem2_fail and rem10_pass): cat="CELL6_ADDITION_SUFFICIENT"
    elif all(g["arms"]["remove2"]["maturity_pass"] and g["arms"]["add6"]["maturity_pass"] for g in groups): cat="REPLACEMENT_INTERACTION_REQUIRED"
    else: cat="MIXED_ONE_SIDED_CAUSALITY"
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
        "alpha_exact":BELOW==c23.BELOW==0.134765625,
        "replicate8_partner6_exact":all(g["replicate"]==8 and g["partner"]==6 for g in a["groups"]),
        "all_required_cells_eligible":all(g["eligible"] for g in a["groups"]),
        "original_full_anchors_reproduced":all(g["original_failure"] and g["full_partner_rescue"] for g in a["groups"]),
        "replacement_anchors_reproduced":all(
            not g["arms"]["replace2to6"]["maturity_pass"] and g["arms"]["replace10to14"]["maturity_pass"]
            for g in a["groups"]),
        "one_sided_cardinality_exact":all(
            g["arms"]["remove2"]["delta_vs_full"]==-1 and g["arms"]["remove10"]["delta_vs_full"]==-1 and
            g["arms"]["add6"]["delta_vs_full"]==1 and g["arms"]["add14"]["delta_vs_full"]==1
            for g in a["groups"]),
        "replacement_cardinality_exact":all(
            g["arms"]["replace2to6"]["delta_vs_full"]==0 and g["arms"]["replace10to14"]["delta_vs_full"]==0
            for g in a["groups"]),
        "runtime_alpha_restored":a["runtime_alpha_restored"],
        "dose_allowlist_restored":a["dose_allowlist_restored"],
        "pressure_lesion_restored":a["pressure_lesion_restored"],
    }
    cat=a["classification"]
    allowed={"BOTH_FACTORS_INDEPENDENTLY_SUFFICIENT","CELL2_REMOVAL_SUFFICIENT","CELL6_ADDITION_SUFFICIENT","REPLACEMENT_INTERACTION_REQUIRED","MIXED_ONE_SIDED_CAUSALITY","ANCHOR_NOT_REPRODUCED"}
    out={"schema":1,"experiment":"YGG-C24","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_C24_CELL2_CELL6_ONE_SIDED_DECOMPOSITION":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
