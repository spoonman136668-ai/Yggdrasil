#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a28_replicate6_cell2_interaction_decomposition_v1 as a28

PREREG="d3ed549be2e901ea0ebf75cb02080683b6d0e944"
PARENT_RUN="36272092354"
L11=[7,15,23,29,31,32,39,47,52,55,63]
TARGET=2

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def one_mode(mode):
    base=a28.base6()
    l11=sorted(a28.a27.anchor_lesion(base["seed"]))
    anchor=a28.score(mode,l11)
    positive=a28.score(mode,sorted(l11+[TARGET]))
    pc=a28.collapsed(anchor,positive)
    row=a28.score(mode,[TARGET])
    fs=a28.collapsed(anchor,row)
    return {
        "mode":mode,
        "replicate":int(base["replicate"]),
        "l11":l11,
        "positive_control_collapse":bool(pc),
        "zero_support_lesion":[TARGET],
        "zero_support_collapse":bool(fs),
        "failures":fs,
        "maturity_pass":bool(row["maturity"]["pass"]),
        "incorrect_done":row["result"]["incorrect_done"],
        "matching_duplicate_cell":row["result"]["matching_duplicate_cell"],
        "matching_duplicate_request":row["result"]["matching_duplicate_request"],
        "branch_scheduled":row["branch"]["scheduled"],
        "branch_applied":row["branch"]["applied"],
        "branch_repaired":row["branch"]["repaired"],
    }

def one_pass():
    rows=[one_mode(m) for m in a28.MODES]
    vals=[r["zero_support_collapse"] for r in rows]
    if vals==[True,True]: cat="ZERO_SUPPORT_COLLAPSE"
    elif vals==[False,False]: cat="L11_SUPPORT_REQUIRED"
    elif vals[0]!=vals[1]: cat="MODE_SPECIFIC_ZERO_SUPPORT"
    else: cat="OTHER_VALID_PATTERN"
    return {"rows":rows,"classification":cat}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    validity={
        "duplicate_complete_execution_byte_identical":b1==b2,
        "actual_replicate6_verified":all(r["replicate"]==6 for r in first["rows"]),
        "l11_exact":all(r["l11"]==L11 for r in first["rows"]),
        "target_cell_exact":TARGET==a28.TARGET_CELL==2,
        "alpha_exact":a28.a27.ALPHA==0.25,
        "modes_exact":[r["mode"] for r in first["rows"]]==list(a28.MODES),
        "positive_control_reproduced":all(r["positive_control_collapse"] for r in first["rows"]),
        "zero_support_lesion_exact":all(r["zero_support_lesion"]==[2] for r in first["rows"]),
        "arm_integrity":all(
            r["maturity_pass"] and r["incorrect_done"]==0 and
            r["matching_duplicate_cell"]==0 and r["matching_duplicate_request"]==0 and
            r["branch_scheduled"]==0 and r["branch_applied"]==0 and r["branch_repaired"]==0
            for r in first["rows"]
        ),
    }
    cat=first["classification"]
    allowed={"ZERO_SUPPORT_COLLAPSE","L11_SUPPORT_REQUIRED","MODE_SPECIFIC_ZERO_SUPPORT","OTHER_VALID_PATTERN"}
    out={
        "schema":1,"experiment":"YGG-A38","prereg":PREREG,"parent_run":PARENT_RUN,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "validity":validity,"valid":all(validity.values()),
        "qualification":{"YGG_A38_REPLICATE6_CELL2_ZERO_SUPPORT":all(validity.values()) and cat in allowed,"classification":cat},
        "analysis":first,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
