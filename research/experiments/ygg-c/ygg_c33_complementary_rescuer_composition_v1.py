#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c32_cross_basin_rescuer_transfer_v1 as c32

PREREG="63f8d01b0ee81fba03424181bbbb277d6cc9b773"
PARENT_RUN="36346247216"
BELOW=0.134765625
LEVELS=list(range(8,17))
SINGLES=(41,40,45,47,10)
DOUBLE_ARMS={
    "ADD41_40":(41,40),
    "ADD41_45":(41,45),
    "ADD41_47":(41,47),
    "ADD40_47":(40,47),
    "ADD10_47":(10,47),
}

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def maturity(row): return bool(row["maturity"]["a25"]["pass"])

def one_pass():
    c31=c32.c31
    c30=c31.c30
    c29=c30.c29
    c28=c29.c28
    c27=c28.c27
    c26=c27.c26
    c25=c26.c25
    c24=c25.c24
    c23=c24.c23
    c22=c23.c22
    c20=c22.c20
    c19=c20.c19
    c16=c19.c17.c16
    c3=c16.c3

    old_pressure=c3.pressure_lesion
    old_parent=float(c16.parent.ALPHA)
    old_runtime=float(c16.parent.g.ALPHA)
    old_dose=tuple(c16.dose.ALPHAS)

    c16.parent.ALPHA=BELOW
    c16.parent.g.ALPHA=BELOW
    c16.dose.ALPHAS=c19.c17.EXTENDED
    c3.pressure_lesion=c16.c5.fine_pressure

    groups=[]
    try:
        base=c3.lu2v.primary_manifests(c3.LU2VF1)
        for level in LEVELS:
            manifests=[c3.pressure_manifest(m,level) for m in base]
            m8={int(m["replicate"]):m for m in manifests}[8]
            original=sorted(m8["lesion"])

            def run(lesion):
                return c22.run_manifest_with_lesion(m8,level,sorted(lesion))

            original_row=run(original)

            singles=[]
            for cell in SINGLES:
                if cell in original:
                    raise AssertionError(f"C33 single addition already present level={level} cell={cell}")
                lesion=sorted(set(original)|{cell})
                row=run(lesion)
                singles.append({
                    "cell":cell,
                    "maturity_pass":maturity(row),
                    "lesion":lesion,
                    "symmetric_difference":sorted(set(original)^set(lesion)),
                })

            doubles=[]
            for name,cells in DOUBLE_ARMS.items():
                if any(c in original for c in cells):
                    raise AssertionError(f"C33 double addition already present level={level} arm={name}")
                lesion=sorted(set(original)|set(cells))
                row=run(lesion)
                doubles.append({
                    "name":name,
                    "cells":list(cells),
                    "maturity_pass":maturity(row),
                    "lesion":lesion,
                    "symmetric_difference":sorted(set(original)^set(lesion)),
                })

            groups.append({
                "level":level,
                "original_failure":not maturity(original_row),
                "original_lesion":original,
                "single_arms":singles,
                "double_arms":doubles,
                "single_rescuers":[x["cell"] for x in singles if x["maturity_pass"]],
                "double_rescuers":[x["name"] for x in doubles if x["maturity_pass"]],
            })
    finally:
        c3.pressure_lesion=old_pressure
        c16.parent.ALPHA=old_parent
        c16.parent.g.ALPHA=old_runtime
        c16.dose.ALPHAS=old_dose

    expected_single={
        41:[8,9],
        40:[10,11,12,13,14,15,16],
        45:[10,11,12,13,14,15,16],
        47:[],
        10:[],
    }
    actual_single={
        c:[g["level"] for g in groups if c in g["single_rescuers"]]
        for c in SINGLES
    }
    anchors=(actual_single==expected_single and all(g["original_failure"] for g in groups))

    rescue_levels={
        name:[g["level"] for g in groups if name in g["double_rescuers"]]
        for name in DOUBLE_ARMS
    }

    pair_4140=rescue_levels["ADD41_40"]
    pair_4145=rescue_levels["ADD41_45"]
    generic=rescue_levels["ADD10_47"]

    interference=False
    for level in range(10,17):
        if level not in pair_4140 or level not in pair_4145:
            interference=True
    for level in (8,9):
        if level not in pair_4140 or level not in pair_4145:
            interference=True

    if not anchors:
        cat="ANCHOR_NOT_REPRODUCED"
    elif generic==LEVELS:
        cat="GENERIC_TWO_ADDITION_RESCUE"
    elif pair_4140==LEVELS and pair_4145==LEVELS:
        cat="COMPLEMENTARY_COMPOSITION_UNIVERSAL"
    elif (pair_4140==LEVELS) ^ (pair_4145==LEVELS):
        cat="ONE_COMPLEMENTARY_PAIR_UNIVERSAL"
    elif interference:
        cat="COMPOSITION_INTERFERENCE"
    elif pair_4140 or pair_4145:
        cat="COMPOSITION_PRESSURE_GAPS_REMAIN"
    else:
        cat="OTHER_VALID_PATTERN"

    return {
        "groups":groups,
        "expected_single_rescue_levels":expected_single,
        "actual_single_rescue_levels":actual_single,
        "double_rescue_levels":rescue_levels,
        "anchors":anchors,
        "classification":cat,
        "runtime_alpha_restored":float(c16.parent.ALPHA)==old_parent and float(c16.parent.g.ALPHA)==old_runtime,
        "dose_allowlist_restored":tuple(c16.dose.ALPHAS)==old_dose,
        "pressure_lesion_restored":c3.pressure_lesion is old_pressure,
    }

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    a=one_pass()
    b=one_pass()
    ba=canonical(a)

    validity={
        "duplicate_analysis_byte_identical":ba==canonical(b),
        "levels_exact":[g["level"] for g in a["groups"]]==LEVELS,
        "alpha_exact":BELOW==c32.BELOW==0.134765625,
        "runtime_alpha_contract_explicit":True,
        "original_replicate8_fails":all(g["original_failure"] for g in a["groups"]),
        "single_anchor_set_exact":a["anchors"],
        "five_double_arms_exact":all(
            [x["name"] for x in g["double_arms"]]==list(DOUBLE_ARMS.keys())
            for g in a["groups"]),
        "two_membership_changes_each_double":all(
            len(x["symmetric_difference"])==2 and sorted(x["symmetric_difference"])==sorted(x["cells"])
            for g in a["groups"] for x in g["double_arms"]),
        "one_membership_change_each_single":all(
            x["symmetric_difference"]==[x["cell"]]
            for g in a["groups"] for x in g["single_arms"]),
        "runtime_alpha_restored":a["runtime_alpha_restored"],
        "dose_allowlist_restored":a["dose_allowlist_restored"],
        "pressure_lesion_restored":a["pressure_lesion_restored"],
    }

    cat=a["classification"]
    allowed={
        "COMPLEMENTARY_COMPOSITION_UNIVERSAL",
        "ONE_COMPLEMENTARY_PAIR_UNIVERSAL",
        "COMPOSITION_PRESSURE_GAPS_REMAIN",
        "COMPOSITION_INTERFERENCE",
        "GENERIC_TWO_ADDITION_RESCUE",
        "ANCHOR_NOT_REPRODUCED",
        "OTHER_VALID_PATTERN",
    }

    out={
        "schema":1,
        "experiment":"YGG-C33",
        "prereg":PREREG,
        "parent_run":PARENT_RUN,
        "duplicate_sha256":hashlib.sha256(ba).hexdigest(),
        "validity":validity,
        "valid":all(validity.values()),
        "qualification":{
            "YGG_C33_COMPLEMENTARY_RESCUER_COMPOSITION":all(validity.values()) and cat in allowed,
            "classification":cat,
        },
        "analysis":a,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
