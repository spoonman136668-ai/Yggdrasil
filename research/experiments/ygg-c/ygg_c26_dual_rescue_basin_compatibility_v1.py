#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c25_symmetric_repair_direction_v1 as c25

PREREG="2805f771e6c5e27382974c282508fd8d9a4b978f"
PARENT_RUN="36309190350"
BELOW=0.134765625
PARTNER=6
LEVELS=list(range(8,17))

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def maturity(row): return bool(row["maturity"]["a25"]["pass"])

def one_pass():
    c24=c25.c24; c23=c24.c23; c22=c23.c22; c20=c22.c20; c19=c20.c19; c16=c19.c17.c16; c3=c16.c3
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
            required_only8={38,6,14}; required_onlyp={42,2,10}
            eligible=required_only8.issubset(only8) and required_onlyp.issubset(onlyp)
            if not eligible: raise AssertionError(f"C26 required cells not eligible level={level}")
            original=c22.run_manifest_with_lesion(m8,level,l8)
            base38=sorted((set(l8)-{38})|{42})
            base_row=c22.run_manifest_with_lesion(m8,level,base38)
            lesions={
                "base38to42":base38,
                "plus2":sorted(set(base38)|{2}),
                "minus6":sorted(set(base38)-{6}),
                "plus2_minus6":sorted((set(base38)|{2})-{6}),
                "plus10":sorted(set(base38)|{10}),
                "minus14":sorted(set(base38)-{14}),
                "plus10_minus14":sorted((set(base38)|{10})-{14}),
            }
            arms={}
            for name,lesion in lesions.items():
                row=c22.run_manifest_with_lesion(m8,level,lesion)
                arms[name]={
                    "lesion":lesion,"maturity_pass":maturity(row),
                    "cardinality":len(lesion),"delta_vs_base":len(lesion)-len(base38)
                }
            groups.append({
                "level":level,"replicate":8,"partner":PARTNER,
                "original_failure":not maturity(original),
                "base38to42_rescue":maturity(base_row),
                "original_lesion":l8,"partner_lesion":lp,
                "base38to42_lesion":base38,"eligible":eligible,"arms":arms
            })
    finally:
        c3.pressure_lesion=old_pressure; c16.parent.ALPHA=old_parent; c16.parent.g.ALPHA=old_runtime; c16.dose.ALPHAS=old_dose
    anchors=all(g["original_failure"] and g["base38to42_rescue"] and g["arms"]["base38to42"]["maturity_pass"] for g in groups)
    plus2_all=all(g["arms"]["plus2"]["maturity_pass"] for g in groups)
    minus6_all=all(g["arms"]["minus6"]["maturity_pass"] for g in groups)
    combo_all=all(g["arms"]["plus2_minus6"]["maturity_pass"] for g in groups)
    plus10_all=all(g["arms"]["plus10"]["maturity_pass"] for g in groups)
    minus14_all=all(g["arms"]["minus14"]["maturity_pass"] for g in groups)
    ctrlcombo_all=all(g["arms"]["plus10_minus14"]["maturity_pass"] for g in groups)
    if not anchors: cat="ANCHOR_NOT_REPRODUCED"
    elif plus2_all and minus6_all and combo_all and plus10_all and minus14_all and ctrlcombo_all: cat="BASINS_COMPATIBLE"
    elif (not plus2_all) and plus10_all: cat="CELL2_INTERFERES_WITH_LOCAL_REPAIR"
    elif (not minus6_all) and minus14_all: cat="CELL6_REMOVAL_INTERFERES_WITH_LOCAL_REPAIR"
    elif plus2_all and minus6_all and (not combo_all): cat="COMBINED_SIGNATURE_INTERFERES"
    else: cat="MIXED_BASIN_COMPATIBILITY"
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
        "alpha_exact":BELOW==c25.BELOW==0.134765625,
        "replicate8_partner6_exact":all(g["replicate"]==8 and g["partner"]==6 for g in a["groups"]),
        "required_cells_eligible":all(g["eligible"] for g in a["groups"]),
        "original_and_38to42_anchors_reproduced":all(g["original_failure"] and g["base38to42_rescue"] for g in a["groups"]),
        "base38to42_exact":all(
            38 not in g["base38to42_lesion"] and 42 in g["base38to42_lesion"] and
            len(g["base38to42_lesion"])==len(g["original_lesion"])
            for g in a["groups"]),
        "registered_cardinalities_exact":all(
            g["arms"]["plus2"]["delta_vs_base"]==1 and
            g["arms"]["minus6"]["delta_vs_base"]==-1 and
            g["arms"]["plus2_minus6"]["delta_vs_base"]==0 and
            g["arms"]["plus10"]["delta_vs_base"]==1 and
            g["arms"]["minus14"]["delta_vs_base"]==-1 and
            g["arms"]["plus10_minus14"]["delta_vs_base"]==0
            for g in a["groups"]),
        "runtime_alpha_restored":a["runtime_alpha_restored"],
        "dose_allowlist_restored":a["dose_allowlist_restored"],
        "pressure_lesion_restored":a["pressure_lesion_restored"],
    }
    cat=a["classification"]
    allowed={"BASINS_COMPATIBLE","CELL2_INTERFERES_WITH_LOCAL_REPAIR","CELL6_REMOVAL_INTERFERES_WITH_LOCAL_REPAIR","COMBINED_SIGNATURE_INTERFERES","MIXED_BASIN_COMPATIBILITY","ANCHOR_NOT_REPRODUCED"}
    out={"schema":1,"experiment":"YGG-C26","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_C26_DUAL_RESCUE_BASIN_COMPATIBILITY":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
