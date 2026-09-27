#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c31_rescuer_pressure_portability_v1 as c31

PREREG="4bc17130fe94eb37120415a0480b610314414487"
PARENT_RUN="36334963456"
BELOW=0.134765625
LEVELS=list(range(8,17))
ADDITIONS=(40,45,41,47,2,10)

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def maturity(row): return bool(row["maturity"]["a25"]["pass"])

def one_pass():
    c30=c31.c30; c29=c30.c29; c28=c29.c28; c27=c28.c27; c26=c27.c26; c25=c26.c25
    c24=c25.c24; c23=c24.c23; c22=c23.c22; c20=c22.c20; c19=c20.c19; c16=c19.c17.c16; c3=c16.c3
    old_pressure=c3.pressure_lesion; old_parent=float(c16.parent.ALPHA); old_runtime=float(c16.parent.g.ALPHA); old_dose=tuple(c16.dose.ALPHAS)
    c16.parent.ALPHA=BELOW; c16.parent.g.ALPHA=BELOW; c16.dose.ALPHAS=c19.c17.EXTENDED; c3.pressure_lesion=c16.c5.fine_pressure
    groups=[]
    try:
        base=c3.lu2v.primary_manifests(c3.LU2VF1)
        for level in LEVELS:
            manifests=[c3.pressure_manifest(m,level) for m in base]
            m8={int(m["replicate"]):m for m in manifests}[8]
            l8=sorted(m8["lesion"])
            def run(lesion): return c22.run_manifest_with_lesion(m8,level,sorted(lesion))
            original=run(l8)
            arms=[]
            for cell in ADDITIONS:
                if cell in l8: raise AssertionError(f"C32 addition already present level={level} cell={cell}")
                lesion=sorted(set(l8)|{cell})
                row=run(lesion)
                arms.append({
                    "cell":cell,"maturity_pass":maturity(row),"lesion":lesion,
                    "symmetric_difference":sorted(set(l8)^set(lesion))
                })
            groups.append({
                "level":level,"original_failure":not maturity(original),
                "original_lesion":l8,"arms":arms,
                "rescuing_additions":[x["cell"] for x in arms if x["maturity_pass"]]
            })
    finally:
        c3.pressure_lesion=old_pressure; c16.parent.ALPHA=old_parent; c16.parent.g.ALPHA=old_runtime; c16.dose.ALPHAS=old_dose
    add2=[g["level"] for g in groups if 2 in g["rescuing_additions"]]
    add10=[g["level"] for g in groups if 10 in g["rescuing_additions"]]
    r40=[g["level"] for g in groups if 40 in g["rescuing_additions"]]
    r45=[g["level"] for g in groups if 45 in g["rescuing_additions"]]
    anchors=all(g["original_failure"] for g in groups) and add2==[14,15,16] and add10==[]
    if not anchors: cat="ANCHOR_NOT_REPRODUCED"
    elif r40==LEVELS and r45==LEVELS: cat="CROSS_BASIN_PORTABLE_40_45"
    elif r40 or r45: cat="PARTIAL_CROSS_BASIN_PORTABILITY"
    else: cat="F_STATE_SPECIFIC_40_45"
    return {
        "groups":groups,
        "rescue_levels":{str(c):[g["level"] for g in groups if c in g["rescuing_additions"]] for c in ADDITIONS},
        "anchors":anchors,"classification":cat,
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
        "alpha_exact":BELOW==c31.BELOW==0.134765625,
        "replicate8_original_fails":all(g["original_failure"] for g in a["groups"]),
        "six_additions_exact":all([x["cell"] for x in g["arms"]]==list(ADDITIONS) for g in a["groups"]),
        "one_membership_addition_each":all(all(x["symmetric_difference"]==[x["cell"]] for x in g["arms"]) for g in a["groups"]),
        "c25_add2_add10_anchors_exact":a["anchors"],
        "runtime_alpha_restored":a["runtime_alpha_restored"],
        "dose_allowlist_restored":a["dose_allowlist_restored"],
        "pressure_lesion_restored":a["pressure_lesion_restored"],
    }
    cat=a["classification"]
    allowed={"CROSS_BASIN_PORTABLE_40_45","PARTIAL_CROSS_BASIN_PORTABILITY","F_STATE_SPECIFIC_40_45","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-C32","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_C32_CROSS_BASIN_RESCUER_TRANSFER":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
