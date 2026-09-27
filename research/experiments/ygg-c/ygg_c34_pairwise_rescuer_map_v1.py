#!/usr/bin/env python3
import hashlib,itertools,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c33_complementary_rescuer_composition_v1 as c33

PREREG="78b47d36ebb64276d09ed7eb5e0a3853840f0587"
PARENT_RUN="36350101079"
BELOW=0.134765625
LEVELS=list(range(8,17))
VERTICES=(2,10,40,41,45,47)
PAIRS=tuple(itertools.combinations(VERTICES,2))
EXPECTED_SINGLE={
    2:[14,15,16],
    10:[],
    40:[10,11,12,13,14,15,16],
    41:[8,9],
    45:[10,11,12,13,14,15,16],
    47:[],
}

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def maturity(row): return bool(row["maturity"]["a25"]["pass"])

def one_pass():
    c32=c33.c32
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
    c16.parent.ALPHA=BELOW; c16.parent.g.ALPHA=BELOW
    c16.dose.ALPHAS=c19.c17.EXTENDED
    c3.pressure_lesion=c16.c5.fine_pressure
    groups=[]
    try:
        base=c3.lu2v.primary_manifests(c3.LU2VF1)
        for level in LEVELS:
            manifests=[c3.pressure_manifest(m,level) for m in base]
            m8={int(m["replicate"]):m for m in manifests}[8]
            original=sorted(m8["lesion"])
            def run(lesion): return c22.run_manifest_with_lesion(m8,level,sorted(lesion))
            original_row=run(original)
            singles=[]
            for cell in VERTICES:
                if cell in original: raise AssertionError(f"C34 cell already present level={level} cell={cell}")
                lesion=sorted(set(original)|{cell}); row=run(lesion)
                singles.append({"cell":cell,"maturity_pass":maturity(row),"symmetric_difference":sorted(set(original)^set(lesion))})
            pairs=[]
            for a,b in PAIRS:
                if a in original or b in original: raise AssertionError(f"C34 pair already present level={level} pair={(a,b)}")
                lesion=sorted(set(original)|{a,b}); row=run(lesion)
                pairs.append({"pair":[a,b],"maturity_pass":maturity(row),"symmetric_difference":sorted(set(original)^set(lesion))})
            groups.append({
                "level":level,"original_failure":not maturity(original_row),
                "single_rescuers":[x["cell"] for x in singles if x["maturity_pass"]],
                "pair_rescuers":[x["pair"] for x in pairs if x["maturity_pass"]],
                "single_arms":singles,"pair_arms":pairs,
            })
    finally:
        c3.pressure_lesion=old_pressure; c16.parent.ALPHA=old_parent; c16.parent.g.ALPHA=old_runtime; c16.dose.ALPHAS=old_dose
    actual_single={c:[g["level"] for g in groups if c in g["single_rescuers"]] for c in VERTICES}
    pair_levels={f"{a},{b}":[g["level"] for g in groups if [a,b] in g["pair_rescuers"]] for a,b in PAIRS}
    universal=[[a,b] for a,b in PAIRS if pair_levels[f"{a},{b}"]==LEVELS]
    anchors=all(g["original_failure"] for g in groups) and actual_single==EXPECTED_SINGLE and [40,41] in universal
    if not anchors: cat="ANCHOR_NOT_REPRODUCED"
    elif universal==[[40,41]]: cat="UNIQUE_UNIVERSAL_PAIR_40_41"
    elif len(universal)>=2: cat="MULTIPLE_UNIVERSAL_PAIRS"
    elif len(universal)==0: cat="NO_UNIVERSAL_PAIR"
    else: cat="OTHER_VALID_PATTERN"
    return {
        "groups":groups,"actual_single_rescue_levels":actual_single,
        "pair_rescue_levels":pair_levels,"universal_pairs":universal,
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
        "alpha_exact":BELOW==c33.BELOW==0.134765625,
        "runtime_alpha_contract_explicit":True,
        "vertices_exact":list(VERTICES)==[2,10,40,41,45,47],
        "exact_15_pairs":len(PAIRS)==15,
        "pairs_unique":len(set(PAIRS))==15,
        "original_replicate8_fails":all(g["original_failure"] for g in a["groups"]),
        "single_anchors_exact":a["actual_single_rescue_levels"]==EXPECTED_SINGLE,
        "c33_40_41_anchor_exact":[40,41] in a["universal_pairs"],
        "two_membership_changes_each_pair":all(len(x["symmetric_difference"])==2 and x["symmetric_difference"]==x["pair"] for g in a["groups"] for x in g["pair_arms"]),
        "one_membership_change_each_single":all(x["symmetric_difference"]==[x["cell"]] for g in a["groups"] for x in g["single_arms"]),
        "runtime_alpha_restored":a["runtime_alpha_restored"],
        "dose_allowlist_restored":a["dose_allowlist_restored"],
        "pressure_lesion_restored":a["pressure_lesion_restored"],
    }
    cat=a["classification"]
    allowed={"UNIQUE_UNIVERSAL_PAIR_40_41","MULTIPLE_UNIVERSAL_PAIRS","NO_UNIVERSAL_PAIR","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-C34","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_C34_PAIRWISE_RESCUER_MAP":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
