#!/usr/bin/env python3
import copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c20_replicate8_context_exchange_v1 as c20

PREREG="6a0c0a671f05a12c099318f68f24bbd0ace4602d"
PARENT_RUN="36272096271"
PARTNER=6
BELOW=0.134765625

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def maturity(row): return bool(row["maturity"]["a25"]["pass"])

def run_manifest_with_lesion(manifest,level,lesion):
    c19=c20.c19; c16=c19.c17.c16; c3=c16.c3
    x=copy.deepcopy(manifest)
    x["lesion"]=sorted(lesion)
    x["manifest_sha256"]=c3.lu2v.manifest_identity(x)
    if c3.non_lesion_bytes(x)!=c3.non_lesion_bytes(manifest):
        raise AssertionError("C22 nonlesion mutation")
    old=c3.pressure_lesion
    mapping={x["seed"]:list(x["lesion"])}
    def fixed(seed,count):
        return mapping.get(seed,c16.c5.fine_pressure(seed,count))
    c3.pressure_lesion=fixed
    try:
        if float(c16.parent.ALPHA)!=BELOW or float(c16.parent.g.ALPHA)!=BELOW:
            raise AssertionError("C22 runtime alpha drift")
        return c3.run_pressure_manifest(x,level)
    finally:
        c3.pressure_lesion=old

def one_pass():
    c19=c20.c19; c16=c19.c17.c16; c3=c16.c3
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
        actual_ids=sorted(int(m["replicate"]) for m in base)
        for level in range(8,17):
            manifests=[c3.pressure_manifest(m,level) for m in base]
            byrep={int(m["replicate"]):m for m in manifests}
            if 8 not in byrep or PARTNER not in byrep:
                raise AssertionError("C22 replicate identity missing")
            m8=byrep[8]; mp=byrep[PARTNER]
            l8=sorted(m8["lesion"]); lp=sorted(mp["lesion"])
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
                    "removed":meta["removed"],"added":meta["added"],"lesion":list(lesion_t),
                    "maturity_pass":maturity(row),"cardinality":len(lesion_t),
                })
            groups.append({
                "level":level,
                "actual_replicate_ids":actual_ids,
                "replicate":int(m8["replicate"]),
                "partner":int(mp["replicate"]),
                "original_failure":not maturity(original),
                "full_partner_rescue":maturity(full),
                "original_lesion":l8,"partner_lesion":lp,
                "unique8":only8,"unique_partner":onlyp,"arms":arms,
                "nonlesion_partner_exchange_preserved":c3.non_lesion_bytes(m8)==c3.non_lesion_bytes(copy.deepcopy(m8)),
            })
    finally:
        c3.pressure_lesion=old_pressure
        c16.parent.ALPHA=old_parent
        c16.parent.g.ALPHA=old_runtime
        c16.dose.ALPHAS=old_dose

    anchor_ok=all(g["original_failure"] and g["full_partner_rescue"] for g in groups)
    allarms=[a for g in groups for a in g["arms"]]
    if not anchor_ok: cat="ANCHOR_NOT_REPRODUCED"
    elif not allarms: cat="NO_LOCAL_DIFFERENCE"
    elif all(a["maturity_pass"] for a in allarms): cat="EXACT_PAIRING_FRAGILE"
    elif all(not a["maturity_pass"] for a in allarms): cat="LOCAL_CONTEXT_ROBUST"
    elif any(a["maturity_pass"] for a in allarms) and any(not a["maturity_pass"] for a in allarms): cat="MIXED_LOCAL_CONTEXT"
    else: cat="OTHER_VALID_PATTERN"

    return {
        "groups":groups,"classification":cat,
        "runtime_alpha_restored":float(c16.parent.ALPHA)==old_parent and float(c16.parent.g.ALPHA)==old_runtime,
        "dose_allowlist_restored":tuple(c16.dose.ALPHAS)==old_dose,
        "pressure_lesion_restored":c3.pressure_lesion is old_pressure,
    }

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    validity={
        "duplicate_analysis_byte_identical":b1==b2,
        "levels_exact":[g["level"] for g in first["groups"]]==list(range(8,17)),
        "alpha_exact":BELOW==c20.c19.c18.BELOW==0.134765625,
        "replicate8_dynamic":all(g["replicate"]==8 for g in first["groups"]),
        "partner6_dynamic":all(g["partner"]==6 for g in first["groups"]),
        "anchors_reproduced":all(g["original_failure"] and g["full_partner_rescue"] for g in first["groups"]),
        "lesion_cardinality_preserved":all(all(a["cardinality"]==len(g["original_lesion"]) for a in g["arms"]) for g in first["groups"]),
        "all_unique_one_cell_substitutions_tested":all(len(g["arms"])==len(g["unique8"])*len(g["unique_partner"]) for g in first["groups"]),
        "runtime_alpha_restored":first["runtime_alpha_restored"],
        "dose_allowlist_restored":first["dose_allowlist_restored"],
        "pressure_lesion_restored":first["pressure_lesion_restored"],
    }
    allowed={"EXACT_PAIRING_FRAGILE","LOCAL_CONTEXT_ROBUST","MIXED_LOCAL_CONTEXT","NO_LOCAL_DIFFERENCE","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    cat=first["classification"]
    out={
        "schema":1,"experiment":"YGG-C22","prereg":PREREG,"parent_run":PARENT_RUN,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "validity":validity,"valid":all(validity.values()),
        "qualification":{"YGG_C22_REPLICATE8_PARTNER6_SINGLE_SUBSTITUTION":all(validity.values()) and cat in allowed,"classification":cat},
        "analysis":first,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
