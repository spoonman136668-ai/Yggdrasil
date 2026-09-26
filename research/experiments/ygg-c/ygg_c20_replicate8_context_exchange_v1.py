#!/usr/bin/env python3
import copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c19_maturity_failure_localization_v1 as c19

PREREG="cab30efad5378a84d0f0b4eb0e057843f352263c"
PARENT_RUN="36236452372"
BELOW=0.134765625

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def maturity(row): return bool(row["maturity"]["a25"]["pass"])

def one_pass():
    parent=c19.detail(c19.c18.BELOW)
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

    execution_alpha_exact=True
    groups=[]
    try:
        base=c3.lu2v.primary_manifests(c3.LU2VF1)
        for level in range(8,17):
            manifests=[c3.pressure_manifest(m,level) for m in base]
            byrep={int(m["replicate"]):m for m in manifests}
            m8=byrep[8]
            arms=[]
            for partner in sorted(r for r in byrep if r!=8):
                mp=byrep[partner]
                x8=copy.deepcopy(m8); xp=copy.deepcopy(mp)
                x8["lesion"]=list(mp["lesion"]); xp["lesion"]=list(m8["lesion"])
                x8["manifest_sha256"]=c3.lu2v.manifest_identity(x8)
                xp["manifest_sha256"]=c3.lu2v.manifest_identity(xp)
                mapping={x8["seed"]:list(x8["lesion"]),xp["seed"]:list(xp["lesion"])}
                def swapped(seed,count):
                    return mapping.get(seed,c16.c5.fine_pressure(seed,count))
                c3.pressure_lesion=swapped
                try:
                    execution_alpha_exact=execution_alpha_exact and float(c16.parent.ALPHA)==BELOW and float(c16.parent.g.ALPHA)==BELOW
                    r8=c3.run_pressure_manifest(x8,level)
                    rp=c3.run_pressure_manifest(xp,level)
                finally:
                    c3.pressure_lesion=c16.c5.fine_pressure
                arms.append({
                    "partner":partner,
                    "replicate8_maturity_pass":maturity(r8),
                    "partner_maturity_pass":maturity(rp),
                    "replicate8_nonlesion_preserved":c3.non_lesion_bytes(m8)==c3.non_lesion_bytes(x8),
                    "partner_nonlesion_preserved":c3.non_lesion_bytes(mp)==c3.non_lesion_bytes(xp),
                    "runtime_alpha":float(c16.parent.ALPHA),
                    "runtime_g_alpha":float(c16.parent.g.ALPHA),
                })
            groups.append({"level":level,"arms":arms})
    finally:
        c3.pressure_lesion=old_pressure
        c16.parent.ALPHA=old_parent
        c16.parent.g.ALPHA=old_runtime
        c16.dose.ALPHAS=old_dose

    parent_ok=all(x["failing_replicates"]==[8] for x in parent["levels"])
    allarms=[a for g in groups for a in g["arms"]]
    if not parent_ok: cat="NO_REPRODUCED_FAILURE"
    elif all((not a["replicate8_maturity_pass"]) and a["partner_maturity_pass"] for a in allarms): cat="IDENTITY_BOUND"
    elif all(a["replicate8_maturity_pass"] and (not a["partner_maturity_pass"]) for a in allarms): cat="LESION_CONTEXT_BOUND"
    elif allarms: cat="MIXED_IDENTITY_CONTEXT"
    else: cat="OTHER_VALID_PATTERN"
    return {
        "parent":parent,
        "groups":groups,
        "classification":cat,
        "execution_alpha_exact":bool(execution_alpha_exact),
        "runtime_alpha_restored":float(c16.parent.ALPHA)==old_parent and float(c16.parent.g.ALPHA)==old_runtime,
        "dose_allowlist_restored":tuple(c16.dose.ALPHAS)==old_dose,
        "pressure_lesion_restored":c3.pressure_lesion is old_pressure,
    }

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    partners=[len(g["arms"]) for g in first["groups"]]
    validity={
        "duplicate_analysis_byte_identical":b1==b2,
        "parent_failure_reproduced":all(x["failing_replicates"]==[8] for x in first["parent"]["levels"]),
        "alpha_exact":first["parent"]["alpha"]==BELOW,
        "exchange_runtime_alpha_exact":first["execution_alpha_exact"],
        "levels_exact":[g["level"] for g in first["groups"]]==list(range(8,17)),
        "all_non8_partners_tested":len(set(partners))==1 and partners[0]>0,
        "nonlesion_bytes_preserved":all(a["replicate8_nonlesion_preserved"] and a["partner_nonlesion_preserved"] for g in first["groups"] for a in g["arms"]),
        "runtime_alpha_restored":first["runtime_alpha_restored"],
        "dose_allowlist_restored":first["dose_allowlist_restored"],
        "pressure_lesion_restored":first["pressure_lesion_restored"],
    }
    cat=first["classification"]
    allowed={"IDENTITY_BOUND","LESION_CONTEXT_BOUND","MIXED_IDENTITY_CONTEXT","NO_REPRODUCED_FAILURE","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-C20","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_C20_REPLICATE8_CONTEXT_EXCHANGE":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
