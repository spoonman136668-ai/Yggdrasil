#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c30_double_removal_rescue_specificity_v1 as c30

PREREG="6231bfbf0392f74a85b5cfe94f65e7ad13d8c2dd"
PARENT_RUN="36331207096"
BELOW=0.134765625
LEVELS=list(range(8,17))
NOVEL=(38,40,41,45,47)
CONTROLS=(42,46)
ADDITIONS=NOVEL+CONTROLS

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def maturity(row): return bool(row["maturity"]["a25"]["pass"])

def one_pass():
    c29=c30.c29; c28=c29.c28; c27=c28.c27; c26=c27.c26; c25=c26.c25; c24=c25.c24; c23=c24.c23; c22=c23.c22
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
            base38=sorted((set(l8)-{38})|{42})
            F=sorted(set(base38)-{42,46})
            def run(lesion): return c22.run_manifest_with_lesion(m8,level,sorted(lesion))
            base_row=run(base38); frow=run(F)
            arms=[]
            for cell in ADDITIONS:
                if cell in F: raise AssertionError(f"C31 addition already present level={level} cell={cell}")
                lesion=sorted(set(F)|{cell})
                row=run(lesion)
                arms.append({"cell":cell,"maturity_pass":maturity(row),"lesion":lesion,
                             "symmetric_difference":sorted(set(F)^set(lesion))})
            groups.append({
                "level":level,"base_rescue":maturity(base_row),"f_state_rescue":maturity(frow),
                "failing_state":F,"arms":arms,
                "rescuing_additions":[x["cell"] for x in arms if x["maturity_pass"]]
            })
    finally:
        c3.pressure_lesion=old_pressure; c16.parent.ALPHA=old_parent; c16.parent.g.ALPHA=old_runtime; c16.dose.ALPHAS=old_dose
    inherited=all(
        g["base_rescue"] and (not g["f_state_rescue"]) and all(c in g["rescuing_additions"] for c in ADDITIONS)
        for g in groups if g["level"] in (10,11,12))
    fail_levels=[g["level"] for g in groups if not g["f_state_rescue"]]
    rescue_levels={str(c):[g["level"] for g in groups if c in g["rescuing_additions"]] for c in ADDITIONS}
    novel_full=all(all(c in g["rescuing_additions"] for c in NOVEL) for g in groups if not g["f_state_rescue"])
    if not inherited: cat="ANCHOR_NOT_REPRODUCED"
    elif fail_levels==[10,11,12]: cat="NO_EXTRA_FAILURE_LEVELS"
    elif novel_full: cat="NOVEL_RESCUERS_FULLY_PORTABLE"
    else: cat="NOVEL_RESCUERS_PRESSURE_SPECIFIC"
    return {
        "groups":groups,"f_failure_levels":fail_levels,"rescue_levels":rescue_levels,
        "inherited_anchor":inherited,"novel_full_on_all_f_failures":novel_full,
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
        "alpha_exact":BELOW==c30.BELOW==0.134765625,
        "novel_set_exact":list(NOVEL)==[38,40,41,45,47],
        "control_set_exact":list(CONTROLS)==[42,46],
        "seven_additions_each_level":all([x["cell"] for x in g["arms"]]==list(ADDITIONS) for g in a["groups"]),
        "one_membership_addition_each":all(all(x["symmetric_difference"]==[x["cell"]] for x in g["arms"]) for g in a["groups"]),
        "inherited_c30_anchors_exact":a["inherited_anchor"],
        "runtime_alpha_restored":a["runtime_alpha_restored"],
        "dose_allowlist_restored":a["dose_allowlist_restored"],
        "pressure_lesion_restored":a["pressure_lesion_restored"],
    }
    cat=a["classification"]
    allowed={"NOVEL_RESCUERS_FULLY_PORTABLE","NOVEL_RESCUERS_PRESSURE_SPECIFIC","NO_EXTRA_FAILURE_LEVELS","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-C31","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_C31_RESCUER_PRESSURE_PORTABILITY":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
