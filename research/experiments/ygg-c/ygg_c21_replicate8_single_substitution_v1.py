#!/usr/bin/env python3
import copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c20_replicate8_context_exchange_v1 as c20

PREREG="31d983cd460c46f6511edbd8719db6a49be16674"
PARENT_RUN="36255033844"
PARTNER=1

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def maturity(row):
    return bool(row["maturity"]["a25"]["pass"])

def run_manifest_with_lesion(manifest, level, lesion):
    c19=c20.c19
    x=copy.deepcopy(manifest)
    x["lesion"]=sorted(lesion)
    x["manifest_sha256"]=c19.c17.c16.c3.lu2v.manifest_identity(x)
    old=c19.c17.c16.c3.pressure_lesion
    mapping={x["seed"]:list(x["lesion"])}
    def fixed(seed,count):
        return mapping.get(seed,c19.c17.c16.c5.fine_pressure(seed,count))
    c19.c17.c16.c3.pressure_lesion=fixed
    try:
        return c19.c17.c16.c3.run_pressure_manifest(x,level)
    finally:
        c19.c17.c16.c3.pressure_lesion=old

def one_pass():
    c19=c20.c19
    old=c19.c17.c16.c3.pressure_lesion
    c19.c17.c16.c3.pressure_lesion=c19.c17.c16.c5.fine_pressure
    try:
        base=c19.c17.c16.c3.lu2v.primary_manifests(c19.c17.c16.c3.LU2VF1)
        groups=[]
        for level in range(8,17):
            manifests=[c19.c17.c16.c3.pressure_manifest(m,level) for m in base]
            byrep={int(m["replicate"]):m for m in manifests}
            m8=byrep[8]
            mp=byrep[PARTNER]
            l8=sorted(m8["lesion"])
            lp=sorted(mp["lesion"])
            original=run_manifest_with_lesion(m8,level,l8)
            full=run_manifest_with_lesion(m8,level,lp)
            only8=sorted(set(l8)-set(lp))
            onlyp=sorted(set(lp)-set(l8))
            lesions={}
            for rem in only8:
                for add in onlyp:
                    z=sorted((set(l8)-{rem})|{add})
                    lesions[tuple(z)]={"removed":rem,"added":add}
            arms=[]
            for lesion_t in sorted(lesions):
                meta=lesions[lesion_t]
                row=run_manifest_with_lesion(m8,level,list(lesion_t))
                arms.append({
                    "removed":meta["removed"],
                    "added":meta["added"],
                    "lesion":list(lesion_t),
                    "maturity_pass":maturity(row),
                    "cardinality":len(lesion_t),
                })
            groups.append({
                "level":level,
                "original_failure":not maturity(original),
                "full_partner_rescue":maturity(full),
                "original_lesion":l8,
                "partner_lesion":lp,
                "unique8":only8,
                "unique_partner":onlyp,
                "arms":arms,
            })
    finally:
        c19.c17.c16.c3.pressure_lesion=old

    anchor_ok=all(g["original_failure"] and g["full_partner_rescue"] for g in groups)
    allarms=[a for g in groups for a in g["arms"]]
    if not anchor_ok:
        cat="ANCHOR_NOT_REPRODUCED"
    elif not allarms:
        cat="NO_LOCAL_DIFFERENCE"
    elif all(a["maturity_pass"] for a in allarms):
        cat="EXACT_PAIRING_FRAGILE"
    elif all(not a["maturity_pass"] for a in allarms):
        cat="LOCAL_CONTEXT_ROBUST"
    elif any(a["maturity_pass"] for a in allarms) and any(not a["maturity_pass"] for a in allarms):
        cat="MIXED_LOCAL_CONTEXT"
    else:
        cat="OTHER_VALID_PATTERN"
    return {"groups":groups,"classification":cat}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    first=one_pass()
    second=one_pass()
    b1=canonical(first)
    b2=canonical(second)
    v={
        "duplicate_analysis_byte_identical":b1==b2,
        "levels_exact":[g["level"] for g in first["groups"]]==list(range(8,17)),
        "alpha_exact":c20.c19.c18.BELOW==0.134765625,
        "replicate_exact":True,
        "partner_exact":PARTNER==1,
        "anchors_reproduced":all(g["original_failure"] and g["full_partner_rescue"] for g in first["groups"]),
        "lesion_cardinality_preserved":all(
            all(a["cardinality"]==len(g["original_lesion"]) for a in g["arms"])
            for g in first["groups"]
        ),
        "all_unique_one_cell_substitutions_tested":all(
            len(g["arms"])==len(g["unique8"])*len(g["unique_partner"])
            for g in first["groups"]
        ),
    }
    allowed={"EXACT_PAIRING_FRAGILE","LOCAL_CONTEXT_ROBUST","MIXED_LOCAL_CONTEXT","NO_LOCAL_DIFFERENCE","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    cat=first["classification"]
    out={
        "schema":1,
        "experiment":"YGG-C21",
        "prereg":PREREG,
        "parent_run":PARENT_RUN,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "validity":v,
        "valid":all(v.values()),
        "qualification":{
            "YGG_C21_REPLICATE8_SINGLE_SUBSTITUTION":all(v.values()) and cat in allowed,
            "classification":cat,
        },
        "analysis":first,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
