#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c34_pairwise_rescuer_map_v1 as c34

PREREG="f5a114d205d469d86517a6d8133f2791ce5cb901"
PARENT_RUN="36353600852"
BELOW=0.134765625
LEVELS=list(range(8,17))
VERTICES=(2,10,40,41,45,47)
UNIVERSAL=((40,41),(45,47))
EXPECTED_SINGLE=c34.EXPECTED_SINGLE

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def maturity(row): return bool(row["maturity"]["a25"]["pass"])

def one_pass():
    c33=c34.c33; c32=c33.c32; c31=c32.c31; c30=c31.c30; c29=c30.c29
    c28=c29.c28; c27=c28.c27; c26=c27.c26; c25=c26.c25; c24=c25.c24
    c23=c24.c23; c22=c23.c22; c20=c22.c20; c19=c20.c19; c16=c19.c17.c16; c3=c16.c3
    old_pressure=c3.pressure_lesion; old_parent=float(c16.parent.ALPHA); old_runtime=float(c16.parent.g.ALPHA); old_dose=tuple(c16.dose.ALPHAS)
    c16.parent.ALPHA=BELOW; c16.parent.g.ALPHA=BELOW; c16.dose.ALPHAS=c19.c17.EXTENDED; c3.pressure_lesion=c16.c5.fine_pressure
    groups=[]
    try:
        base=c3.lu2v.primary_manifests(c3.LU2VF1)
        for level in LEVELS:
            manifests=[c3.pressure_manifest(m,level) for m in base]; m8={int(m["replicate"]):m for m in manifests}[8]
            original=sorted(m8["lesion"])
            def run(lesion): return c22.run_manifest_with_lesion(m8,level,sorted(lesion))
            singles={}
            for cell in VERTICES:
                lesion=sorted(set(original)|{cell}); singles[cell]=maturity(run(lesion))
            pair_rows=[]; triple_rows=[]
            for a,b in UNIVERSAL:
                pair_lesion=sorted(set(original)|{a,b}); pair_rows.append({"pair":[a,b],"maturity_pass":maturity(run(pair_lesion)),
                    "symmetric_difference":sorted(set(original)^set(pair_lesion))})
                for c in VERTICES:
                    if c in (a,b): continue
                    lesion=sorted(set(original)|{a,b,c})
                    triple_rows.append({"pair":[a,b],"third":c,"triple":sorted([a,b,c]),"maturity_pass":maturity(run(lesion)),
                        "symmetric_difference":sorted(set(original)^set(lesion))})
            groups.append({"level":level,"single_rescuers":[c for c,v in singles.items() if v],
                           "pair_arms":pair_rows,"triple_arms":triple_rows})
    finally:
        c3.pressure_lesion=old_pressure; c16.parent.ALPHA=old_parent; c16.parent.g.ALPHA=old_runtime; c16.dose.ALPHAS=old_dose
    actual_single={c:[g["level"] for g in groups if c in g["single_rescuers"]] for c in VERTICES}
    pair_levels={f"{a},{b}":[g["level"] for g in groups for x in g["pair_arms"] if x["pair"]==[a,b] and x["maturity_pass"]] for a,b in UNIVERSAL}
    triple_levels={}
    for a,b in UNIVERSAL:
        for c in VERTICES:
            if c in (a,b): continue
            key=f"{a},{b}+{c}"
            triple_levels[key]=[g["level"] for g in groups for x in g["triple_arms"] if x["pair"]==[a,b] and x["third"]==c and x["maturity_pass"]]
    anchors=actual_single==EXPECTED_SINGLE and all(pair_levels[f"{a},{b}"]==LEVELS for a,b in UNIVERSAL)
    u1=all(triple_levels[f"40,41+{c}"]==LEVELS for c in VERTICES if c not in (40,41))
    u2=all(triple_levels[f"45,47+{c}"]==LEVELS for c in VERTICES if c not in (45,47))
    if not anchors: cat="ANCHOR_NOT_REPRODUCED"
    elif u1 and u2: cat="ROBUST_UNIVERSAL_PAIR_CLASS"
    elif u1: cat="U1_ONLY_ROBUST"
    elif u2: cat="U2_ONLY_ROBUST"
    else: cat="CONTEXT_SENSITIVE_UNIVERSALITY"
    return {"groups":groups,"actual_single_rescue_levels":actual_single,"pair_rescue_levels":pair_levels,
            "triple_rescue_levels":triple_levels,"anchors":anchors,"classification":cat,
            "runtime_alpha_restored":float(c16.parent.ALPHA)==old_parent and float(c16.parent.g.ALPHA)==old_runtime,
            "dose_allowlist_restored":tuple(c16.dose.ALPHAS)==old_dose,"pressure_lesion_restored":c3.pressure_lesion is old_pressure}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one_pass(); b=one_pass(); ba=canonical(a)
    triples=[x for g in a["groups"] for x in g["triple_arms"]]
    pairs=[x for g in a["groups"] for x in g["pair_arms"]]
    validity={
        "duplicate_analysis_byte_identical":ba==canonical(b),
        "levels_exact":[g["level"] for g in a["groups"]]==LEVELS,
        "alpha_exact":BELOW==c34.BELOW==0.134765625,
        "vertices_exact":list(VERTICES)==[2,10,40,41,45,47],
        "single_anchors_exact":a["actual_single_rescue_levels"]==EXPECTED_SINGLE,
        "two_universal_pair_anchors_exact":all(a["pair_rescue_levels"][f"{x[0]},{x[1]}"]==LEVELS for x in UNIVERSAL),
        "exact_eight_triples_each_level":all(len(g["triple_arms"])==8 for g in a["groups"]),
        "three_membership_changes_each_triple":all(len(x["symmetric_difference"])==3 and x["symmetric_difference"]==x["triple"] for x in triples),
        "two_membership_changes_each_pair":all(len(x["symmetric_difference"])==2 and x["symmetric_difference"]==x["pair"] for x in pairs),
        "runtime_alpha_restored":a["runtime_alpha_restored"],
        "dose_allowlist_restored":a["dose_allowlist_restored"],
        "pressure_lesion_restored":a["pressure_lesion_restored"],
    }
    cat=a["classification"]
    allowed={"ROBUST_UNIVERSAL_PAIR_CLASS","U1_ONLY_ROBUST","U2_ONLY_ROBUST","CONTEXT_SENSITIVE_UNIVERSALITY","GENERIC_THREE_ADDITION_RESCUE","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-C35","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_C35_UNIVERSAL_PAIR_THIRD_ADDITION_ROBUSTNESS":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
