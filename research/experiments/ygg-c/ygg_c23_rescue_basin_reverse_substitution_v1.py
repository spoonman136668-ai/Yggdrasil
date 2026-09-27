#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c22_replicate8_partner6_single_substitution_v1 as c22

PREREG="08e879863996f18432bbeff1703cae3af4cd0a5b"
PARENT_RUN="36276037967"
BELOW=0.134765625
PARTNER=6

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def maturity(row): return bool(row["maturity"]["a25"]["pass"])

def one_pass():
    c20=c22.c20; c19=c20.c19; c16=c19.c17.c16; c3=c16.c3
    old_pressure=c3.pressure_lesion; old_parent=float(c16.parent.ALPHA); old_runtime=float(c16.parent.g.ALPHA); old_dose=tuple(c16.dose.ALPHAS)
    c16.parent.ALPHA=BELOW; c16.parent.g.ALPHA=BELOW; c16.dose.ALPHAS=c19.c17.EXTENDED; c3.pressure_lesion=c16.c5.fine_pressure
    groups=[]
    try:
        base=c3.lu2v.primary_manifests(c3.LU2VF1)
        for level in range(8,17):
            manifests=[c3.pressure_manifest(m,level) for m in base]
            byrep={int(m["replicate"]):m for m in manifests}
            m8=byrep[8]; mp=byrep[PARTNER]
            l8=sorted(m8["lesion"]); lp=sorted(mp["lesion"])
            original=c22.run_manifest_with_lesion(m8,level,l8)
            full=c22.run_manifest_with_lesion(m8,level,lp)
            only8=sorted(set(l8)-set(lp)); onlyp=sorted(set(lp)-set(l8))
            lesions={}
            for rem in onlyp:
                for add in only8:
                    z=sorted((set(lp)-{rem})|{add})
                    lesions[tuple(z)]={"removed_partner":rem,"added_r8":add}
            arms=[]
            for lt in sorted(lesions):
                meta=lesions[lt]
                row=c22.run_manifest_with_lesion(m8,level,list(lt))
                arms.append({"removed_partner":meta["removed_partner"],"added_r8":meta["added_r8"],
                             "lesion":list(lt),"maturity_pass":maturity(row),"cardinality":len(lt)})
            edge=next((a for a in arms if a["removed_partner"]==42 and a["added_r8"]==38),None)
            groups.append({"level":level,"replicate":int(m8["replicate"]),"partner":int(mp["replicate"]),
                           "original_failure":not maturity(original),"full_partner_rescue":maturity(full),
                           "original_lesion":l8,"partner_lesion":lp,"unique8":only8,"unique_partner":onlyp,
                           "arms":arms,"reverse_42_to_38":edge})
    finally:
        c3.pressure_lesion=old_pressure; c16.parent.ALPHA=old_parent; c16.parent.g.ALPHA=old_runtime; c16.dose.ALPHAS=old_dose

    anchor=all(g["original_failure"] and g["full_partner_rescue"] for g in groups)
    allarms=[a for g in groups for a in g["arms"]]
    pairs={}
    for g in groups:
        for a in g["arms"]:
            k=(a["removed_partner"],a["added_r8"])
            pairs.setdefault(k,[]).append(a["maturity_pass"])
    universal_fail=[list(k) for k,v in pairs.items() if len(v)==9 and all(not x for x in v)]
    if not anchor: cat="ANCHOR_NOT_REPRODUCED"
    elif not allarms: cat="NO_REVERSE_DIFFERENCE"
    elif all(a["maturity_pass"] for a in allarms): cat="RESCUE_BASIN_ROBUST"
    elif universal_fail: cat="SINGLE_REVERSION_FRAGILE"
    elif any(a["maturity_pass"] for a in allarms) and any(not a["maturity_pass"] for a in allarms): cat="MIXED_RESCUE_BASIN"
    else: cat="OTHER_VALID_PATTERN"
    return {"groups":groups,"universal_failing_reverse_pairs":universal_fail,"classification":cat,
            "runtime_alpha_restored":float(c16.parent.ALPHA)==old_parent and float(c16.parent.g.ALPHA)==old_runtime,
            "dose_allowlist_restored":tuple(c16.dose.ALPHAS)==old_dose,"pressure_lesion_restored":c3.pressure_lesion is old_pressure}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one_pass(); b=one_pass(); ba=canonical(a)
    validity={
      "duplicate_analysis_byte_identical":ba==canonical(b),
      "levels_exact":[g["level"] for g in a["groups"]]==list(range(8,17)),
      "alpha_exact":BELOW==c22.BELOW==0.134765625,
      "replicate8_dynamic":all(g["replicate"]==8 for g in a["groups"]),
      "partner6_dynamic":all(g["partner"]==6 for g in a["groups"]),
      "anchors_reproduced":all(g["original_failure"] and g["full_partner_rescue"] for g in a["groups"]),
      "cardinality_preserved":all(all(x["cardinality"]==len(g["partner_lesion"]) for x in g["arms"]) for g in a["groups"]),
      "all_unique_reverse_substitutions_tested":all(len(g["arms"])==len(g["unique8"])*len(g["unique_partner"]) for g in a["groups"]),
      "reverse_42_to_38_present_all_levels":all(g["reverse_42_to_38"] is not None for g in a["groups"]),
      "runtime_alpha_restored":a["runtime_alpha_restored"],"dose_allowlist_restored":a["dose_allowlist_restored"],"pressure_lesion_restored":a["pressure_lesion_restored"],
    }
    cat=a["classification"]; allowed={"RESCUE_BASIN_ROBUST","SINGLE_REVERSION_FRAGILE","MIXED_RESCUE_BASIN","NO_REVERSE_DIFFERENCE","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-C23","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_C23_RESCUE_BASIN_REVERSE_SUBSTITUTION":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
