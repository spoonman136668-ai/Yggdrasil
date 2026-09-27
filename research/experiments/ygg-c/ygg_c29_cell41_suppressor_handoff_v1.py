#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c28_critical_addition_compensation_v1 as c28

PREREG="79f72878d862c49ee8a3a51e370646b2a4c2c598"
PARENT_RUN="36322950976"
BELOW=0.134765625
LEVELS=[10,11,12]

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def maturity(row): return bool(row["maturity"]["a25"]["pass"])

def one_pass():
    c27=c28.c27; c26=c27.c26; c25=c26.c25; c24=c25.c24; c23=c24.c23; c22=c23.c22
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
            required={6,14,42,46}
            if not required.issubset(set(base38)): raise AssertionError(f"C29 required present cells missing level={level}")
            def run(lesion): return c22.run_manifest_with_lesion(m8,level,sorted(lesion))
            original=run(l8); base_row=run(base38)
            add41=set(base38)|{41}
            rows={
                "ADD41":run(add41),
                "ADD41_REMOVE42":run(add41-{42}),
                "ADD41_REMOVE46":run(add41-{46}),
                "ADD41_REMOVE42_REMOVE46":run(add41-{42,46}),
                "ADD41_REMOVE6_REMOVE14":run(add41-{6,14}),
                "BASE_REMOVE42_REMOVE46":run(set(base38)-{42,46}),
                "BASE_REMOVE6_REMOVE14":run(set(base38)-{6,14}),
            }
            groups.append({
                "level":level,
                "original_failure":not maturity(original),
                "base_rescue":maturity(base_row),
                "arms":{k:{"maturity_pass":maturity(v)} for k,v in rows.items()},
                "base_cardinality":len(base38),
            })
    finally:
        c3.pressure_lesion=old_pressure; c16.parent.ALPHA=old_parent; c16.parent.g.ALPHA=old_runtime; c16.dose.ALPHAS=old_dose
    anchors=all(
        g["original_failure"] and g["base_rescue"] and
        not g["arms"]["ADD41"]["maturity_pass"] and
        not g["arms"]["ADD41_REMOVE42"]["maturity_pass"] and
        not g["arms"]["ADD41_REMOVE46"]["maturity_pass"]
        for g in groups)
    A=[g["arms"]["ADD41_REMOVE42_REMOVE46"]["maturity_pass"] for g in groups]
    B=[g["arms"]["ADD41_REMOVE6_REMOVE14"]["maturity_pass"] for g in groups]
    if not anchors: cat="ANCHOR_NOT_REPRODUCED"
    elif all(A) and not any(B): cat="COOPERATIVE_42_46_SUPPRESSION"
    elif all(A) and all(B): cat="GENERIC_TWO_REMOVAL_RESCUE"
    elif any(A): cat="PARTIAL_PAIR_SUPPRESSION"
    else: cat="NO_PAIR_SUPPRESSION"
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
        "alpha_exact":BELOW==c28.BELOW==0.134765625,
        "anchors_reproduced":all(
            g["original_failure"] and g["base_rescue"] and
            not g["arms"]["ADD41"]["maturity_pass"] and
            not g["arms"]["ADD41_REMOVE42"]["maturity_pass"] and
            not g["arms"]["ADD41_REMOVE46"]["maturity_pass"]
            for g in a["groups"]),
        "registered_arms_exact":all(
            set(g["arms"])=={
                "ADD41","ADD41_REMOVE42","ADD41_REMOVE46","ADD41_REMOVE42_REMOVE46",
                "ADD41_REMOVE6_REMOVE14","BASE_REMOVE42_REMOVE46","BASE_REMOVE6_REMOVE14"
            } for g in a["groups"]),
        "runtime_alpha_restored":a["runtime_alpha_restored"],
        "dose_allowlist_restored":a["dose_allowlist_restored"],
        "pressure_lesion_restored":a["pressure_lesion_restored"],
    }
    cat=a["classification"]
    allowed={"COOPERATIVE_42_46_SUPPRESSION","GENERIC_TWO_REMOVAL_RESCUE","PARTIAL_PAIR_SUPPRESSION","NO_PAIR_SUPPRESSION","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-C29","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_C29_CELL41_SUPPRESSOR_HANDOFF":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
