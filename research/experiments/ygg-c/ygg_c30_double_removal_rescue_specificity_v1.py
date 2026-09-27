#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c29_cell41_suppressor_handoff_v1 as c29

PREREG="9a2a7545c91e7a405b32571b696d0567270c1d06"
PARENT_RUN="36327042750"
BELOW=0.134765625
LEVELS=[10,11,12]

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def maturity(row): return bool(row["maturity"]["a25"]["pass"])

def one_pass():
    c28=c29.c28; c27=c28.c27; c26=c27.c26; c25=c26.c25; c24=c25.c24; c23=c24.c23; c22=c23.c22
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
            base_row=run(base38); frow=run(F); add41=run(set(F)|{41})
            absent=[c for c in range(64) if c not in F]
            arms=[]
            for cell in absent:
                lesion=sorted(set(F)|{cell})
                row=run(lesion)
                arms.append({
                    "cell":cell,"maturity_pass":maturity(row),
                    "lesion":lesion,"symmetric_difference":sorted(set(F)^set(lesion)),
                })
            groups.append({
                "level":level,"base_rescue":maturity(base_row),"double_removal_failure":not maturity(frow),
                "add41_rescue":maturity(add41),"failing_state":F,"absent_cells":absent,
                "rescuing_additions":[x["cell"] for x in arms if x["maturity_pass"]],
                "failing_additions":[x["cell"] for x in arms if not x["maturity_pass"]],
                "arms":arms
            })
    finally:
        c3.pressure_lesion=old_pressure; c16.parent.ALPHA=old_parent; c16.parent.g.ALPHA=old_runtime; c16.dose.ALPHAS=old_dose
    anchors=all(g["base_rescue"] and g["double_removal_failure"] and g["add41_rescue"] for g in groups)
    all41=all(41 in g["rescuing_additions"] for g in groups)
    common=set.intersection(*(set(g["rescuing_additions"]) for g in groups))
    novel=sorted(common-{42,46})
    if not anchors: cat="ANCHOR_NOT_REPRODUCED"
    elif not all41: cat="CELL41_NOT_PORTABLE"
    elif novel==[41]: cat="CELL41_UNIQUE_NOVEL_RESCUER"
    elif 41 in novel and 2<=len(novel)<=6: cat="SMALL_RESCUER_SET"
    elif 41 in novel and len(novel)>6: cat="BROAD_ADDITION_RESCUE"
    else: cat="OTHER_VALID_PATTERN"
    return {
        "groups":groups,"common_rescuing_additions":sorted(common),
        "common_novel_rescuers":novel,"classification":cat,
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
        "alpha_exact":BELOW==c29.BELOW==0.134765625,
        "anchors_reproduced":all(g["base_rescue"] and g["double_removal_failure"] and g["add41_rescue"] for g in a["groups"]),
        "exhaustive_absent_additions":all(g["absent_cells"]==[c for c in range(64) if c not in g["failing_state"]] for g in a["groups"]),
        "one_membership_addition_each":all(all(x["symmetric_difference"]==[x["cell"]] for x in g["arms"]) for g in a["groups"]),
        "controls_41_42_46_present":all(all(c in g["absent_cells"] for c in (41,42,46)) for g in a["groups"]),
        "runtime_alpha_restored":a["runtime_alpha_restored"],
        "dose_allowlist_restored":a["dose_allowlist_restored"],
        "pressure_lesion_restored":a["pressure_lesion_restored"],
    }
    cat=a["classification"]
    allowed={"CELL41_UNIQUE_NOVEL_RESCUER","SMALL_RESCUER_SET","BROAD_ADDITION_RESCUE","CELL41_NOT_PORTABLE","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-C30","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_C30_DOUBLE_REMOVAL_RESCUE_SPECIFICITY":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
