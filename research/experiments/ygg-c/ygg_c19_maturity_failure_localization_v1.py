#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c17_interaction_onset_functional_pressure_v1 as c17
import ygg_c18_retention_predicate_decomposition_v1 as c18
PREREG="5eb5d2132e1217fbc502deba96a672c91c3e2df1"
PARENT_RUN="36228903415"
def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def detail(alpha):
    olda=tuple(c17.c16.ALPHAS); olde=tuple(c17.c16.EXTENDED_DOSE_ALPHAS)
    c17.c16.ALPHAS=c17.ALPHAS; c17.c16.EXTENDED_DOSE_ALPHAS=c17.EXTENDED
    try:
        old_parent=float(c17.c16.parent.ALPHA); old_runtime=float(c17.c16.parent.g.ALPHA)
        old_fine=c17.c16.c3.pressure_lesion; old_dose=tuple(c17.c16.dose.ALPHAS)
        c17.c16.dose.ALPHAS=c17.EXTENDED; c17.c16.parent.ALPHA=float(alpha); c17.c16.parent.g.ALPHA=float(alpha)
        c17.c16.c3.pressure_lesion=c17.c16.c5.fine_pressure
        try: raw=c17.c16.c5.one_pass()
        finally:
            c17.c16.c3.pressure_lesion=old_fine; c17.c16.parent.ALPHA=old_parent; c17.c16.parent.g.ALPHA=old_runtime; c17.c16.dose.ALPHAS=old_dose
    finally:
        c17.c16.ALPHAS=olda; c17.c16.EXTENDED_DOSE_ALPHAS=olde
    rows=[]
    for g in raw["groups"]:
        rows.append({"level":g["lesion_cells"],"failing_replicates":sorted(int(x["replicate"]) for x in g["detail"] if not x["a25_maturity_pass"])})
    return {"alpha":alpha,"levels":rows}
def one_pass():
    below=detail(c18.BELOW); above=detail(c18.ABOVE)
    bsets=[tuple(x["failing_replicates"]) for x in below["levels"]]
    asets=[tuple(x["failing_replicates"]) for x in above["levels"]]
    if any(asets): cat="ABOVE_ONSET_MATURITY_FAILURE"
    elif any(len(x)>1 for x in bsets): cat="MULTIPLE_REPLICATES"
    elif bsets and len(set(bsets))==1 and len(bsets[0])==1: cat="SINGLE_STABLE_REPLICATE"
    elif len(set(bsets))>1: cat="LEVEL_DEPENDENT_REPLICATE"
    else: cat="OTHER_VALID_PATTERN"
    return {"below":below,"above":above,"classification":cat}
def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    agg=c18.one_pass(); first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    validity={"duplicate_analysis_byte_identical":b1==b2,
      "below_aggregate_exact":agg["below"]["retained_by_level"]==c18.EXPECTED_BELOW,
      "above_aggregate_exact":agg["above"]["retained_by_level"]==c18.EXPECTED_ABOVE,
      "levels_exact": [x["level"] for x in first["below"]["levels"]]==list(range(8,17)) and [x["level"] for x in first["above"]["levels"]]==list(range(8,17))}
    cat=first["classification"]; allowed={"SINGLE_STABLE_REPLICATE","LEVEL_DEPENDENT_REPLICATE","MULTIPLE_REPLICATES","ABOVE_ONSET_MATURITY_FAILURE","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-C19","prereg":PREREG,"parent_run":PARENT_RUN,"duplicate_sha256":hashlib.sha256(b1).hexdigest(),
      "validity":validity,"valid":all(validity.values()),"qualification":{"YGG_C19_MATURITY_FAILURE_LOCALIZATION":bool(all(validity.values()) and cat in allowed),"classification":cat},"analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
