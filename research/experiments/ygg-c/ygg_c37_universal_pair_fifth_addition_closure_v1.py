#!/usr/bin/env python3
import hashlib,itertools,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c36_universal_pair_fourth_addition_closure_v1 as c36

PREREG="30c93cd023a75b512f4702f8e2109f61f2a985c3"
PARENT_RUN="36508983931"
BELOW=c36.BELOW
LEVELS=list(c36.LEVELS)
VERTICES=tuple(c36.VERTICES)
UNIVERSAL=tuple(c36.UNIVERSAL)

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def maturity(row): return bool(row["maturity"]["a25"]["pass"])

def one_pass():
    parent=c36.one_pass()
    c35=c36.c35; c34=c35.c34; c33=c34.c33; c32=c33.c32; c31=c32.c31; c30=c31.c30; c29=c30.c29
    c28=c29.c28; c27=c28.c27; c26=c27.c26; c25=c26.c25; c24=c25.c24
    c23=c24.c23; c22=c23.c22; c20=c22.c20; c19=c20.c19; c16=c19.c17.c16; c3=c16.c3
    old_pressure=c3.pressure_lesion
    old_parent=float(c16.parent.ALPHA)
    old_runtime=float(c16.parent.g.ALPHA)
    old_dose=tuple(c16.dose.ALPHAS)
    groups=[]
    try:
        c16.parent.ALPHA=BELOW
        c16.parent.g.ALPHA=BELOW
        c16.dose.ALPHAS=c19.c17.EXTENDED
        c3.pressure_lesion=c16.c5.fine_pressure
        base=c3.lu2v.primary_manifests(c3.LU2VF1)
        for level in LEVELS:
            manifests=[c3.pressure_manifest(m,level) for m in base]
            m8={int(m["replicate"]):m for m in manifests}[8]
            original=sorted(m8["lesion"])
            def run(lesion): return c22.run_manifest_with_lesion(m8,level,sorted(lesion))
            arms=[]
            for a,b in UNIVERSAL:
                remaining=[x for x in VERTICES if x not in (a,b)]
                for c,d,e in itertools.combinations(remaining,3):
                    lesion=sorted(set(original)|{a,b,c,d,e})
                    arms.append({
                        "pair":[a,b],
                        "additions":[c,d,e],
                        "quintuple":sorted([a,b,c,d,e]),
                        "arm_key":f"{a},{b}+{c},{d},{e}",
                        "maturity_pass":maturity(run(lesion)),
                        "symmetric_difference":sorted(set(original)^set(lesion)),
                    })
            groups.append({"level":level,"arms":arms})
    finally:
        c3.pressure_lesion=old_pressure
        c16.parent.ALPHA=old_parent
        c16.parent.g.ALPHA=old_runtime
        c16.dose.ALPHAS=old_dose
    rescue_levels={}
    for a,b in UNIVERSAL:
        remaining=[x for x in VERTICES if x not in (a,b)]
        for c,d,e in itertools.combinations(remaining,3):
            key=f"{a},{b}+{c},{d},{e}"
            rescue_levels[key]=[
                g["level"] for g in groups
                for x in g["arms"]
                if x["arm_key"]==key and x["maturity_pass"]
            ]
    u1=all(rescue_levels[k]==LEVELS for k in rescue_levels if k.startswith("40,41+"))
    u2=all(rescue_levels[k]==LEVELS for k in rescue_levels if k.startswith("45,47+"))
    parent_ok=bool(parent["parent_anchors"]) and parent["classification"]=="CONTEXT_SENSITIVE_HIGHER_ORDER"
    if not parent_ok: cat="ANCHOR_NOT_REPRODUCED"
    elif u1 and u2: cat="ROBUST_FIVE_ADDITION_CLOSURE"
    elif u1: cat="U1_ONLY_FIVE_CLOSURE"
    elif u2: cat="U2_ONLY_FIVE_CLOSURE"
    else: cat="CONTEXT_SENSITIVE_FIFTH_ORDER"
    return {
        "parent_classification":parent["classification"],
        "parent_anchors":bool(parent["parent_anchors"]),
        "groups":groups,"rescue_levels":rescue_levels,"classification":cat,
        "runtime_alpha_restored":float(c16.parent.ALPHA)==old_parent and float(c16.parent.g.ALPHA)==old_runtime,
        "dose_allowlist_restored":tuple(c16.dose.ALPHAS)==old_dose,
        "pressure_lesion_restored":c3.pressure_lesion is old_pressure,
    }

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one_pass(); b=one_pass(); ba=canonical(a)
    arms=[x for g in a["groups"] for x in g["arms"]]
    keys=[x["arm_key"] for x in a["groups"][0]["arms"]]
    validity={
        "prereg_commit_exact":PREREG=="30c93cd023a75b512f4702f8e2109f61f2a985c3",
        "parent_c36_classification_exact":a["parent_classification"]=="CONTEXT_SENSITIVE_HIGHER_ORDER",
        "parent_c36_anchor_exact":bool(a["parent_anchors"]),
        "levels_exact":[g["level"] for g in a["groups"]]==LEVELS,
        "alpha_exact":BELOW==0.134765625,
        "vertices_exact":list(VERTICES)==[2,10,40,41,45,47],
        "exact_eight_quintuple_arms_each_level":all(len(g["arms"])==8 for g in a["groups"]),
        "exact_eight_unique_arm_keys":len(keys)==8 and len(set(keys))==8,
        "five_membership_changes_each_arm":all(len(x["symmetric_difference"])==5 and x["symmetric_difference"]==x["quintuple"] for x in arms),
        "runtime_alpha_restored":a["runtime_alpha_restored"],
        "dose_allowlist_restored":a["dose_allowlist_restored"],
        "pressure_lesion_restored":a["pressure_lesion_restored"],
        "duplicate_analysis_byte_identical":ba==canonical(b),
    }
    cat=a["classification"]
    allowed={"ROBUST_FIVE_ADDITION_CLOSURE","U1_ONLY_FIVE_CLOSURE","U2_ONLY_FIVE_CLOSURE","CONTEXT_SENSITIVE_FIFTH_ORDER","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-C37","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_C37_UNIVERSAL_PAIR_FIFTH_ADDITION_CLOSURE":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
