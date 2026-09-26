#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a28_replicate6_cell2_interaction_decomposition_v1 as a28

PREREG="1ccaea85d53e6d2d0365ce320d21f21dd2c155a2"
PARENT_RUN="36273728981"
TARGET=2
L11=[7,15,23,29,31,32,39,47,52,55,63]

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def integrity(row):
    return {
        "maturity_pass":bool(row["maturity"]["pass"]),
        "incorrect_done":row["result"]["incorrect_done"],
        "matching_duplicate_cell":row["result"]["matching_duplicate_cell"],
        "matching_duplicate_request":row["result"]["matching_duplicate_request"],
        "branch_scheduled":row["branch"]["scheduled"],
        "branch_applied":row["branch"]["applied"],
        "branch_repaired":row["branch"]["repaired"],
    }

def one_mode(mode):
    base=a28.base6()
    zero=a28.score(mode,[])
    singleton=a28.score(mode,[TARGET])
    fs=a28.collapsed(zero,singleton)
    hist_anchor=a28.score(mode,L11)
    hist_positive=a28.score(mode,sorted(L11+[TARGET]))
    hist_pc=a28.collapsed(hist_anchor,hist_positive)
    return {
        "mode":mode,
        "replicate":int(base["replicate"]),
        "zero_lesion":[],
        "singleton_lesion":[TARGET],
        "singleton_collapse":bool(fs),
        "singleton_failures":fs,
        "zero_integrity":integrity(zero),
        "singleton_integrity":integrity(singleton),
        "historical_positive_control_collapse":bool(hist_pc),
        "historical_positive_control_failures":hist_pc,
    }

def one_pass():
    rows=[one_mode(m) for m in a28.MODES]
    vals=[r["singleton_collapse"] for r in rows]
    if vals==[True,True]: cat="CELL2_SINGLETON_SUFFICIENT"
    elif vals==[False,False]: cat="CELL2_SINGLETON_NOT_SUFFICIENT"
    elif vals[0]!=vals[1]: cat="MODE_SPECIFIC_SINGLETON"
    else: cat="OTHER_VALID_PATTERN"
    return {"rows":rows,"classification":cat}

def good_integrity(x):
    return x["maturity_pass"] and x["incorrect_done"]==0 and x["matching_duplicate_cell"]==0 and x["matching_duplicate_request"]==0 and x["branch_scheduled"]==0 and x["branch_applied"]==0 and x["branch_repaired"]==0

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    base=a28.base6()
    z=a28.make_manifest(base,[])
    s=a28.make_manifest(base,[TARGET])
    validity={
        "duplicate_complete_execution_byte_identical":b1==b2,
        "actual_replicate6_verified":all(r["replicate"]==6 for r in first["rows"]),
        "alpha_exact":a28.a27.ALPHA==0.25,
        "modes_exact":[r["mode"] for r in first["rows"]]==list(a28.MODES),
        "target_cell_exact":TARGET==a28.TARGET_CELL==2,
        "zero_lesion_exact":all(r["zero_lesion"]==[] for r in first["rows"]),
        "singleton_lesion_exact":all(r["singleton_lesion"]==[2] for r in first["rows"]),
        "historical_positive_control_reproduced":all(r["historical_positive_control_collapse"] for r in first["rows"]),
        "scientific_arm_integrity":all(good_integrity(r["zero_integrity"]) and good_integrity(r["singleton_integrity"]) for r in first["rows"]),
        "nonlesion_manifest_bytes_frozen":a28.a27.a19.nonlesion_bytes(z)==a28.a27.a19.nonlesion_bytes(base) and a28.a27.a19.nonlesion_bytes(s)==a28.a27.a19.nonlesion_bytes(base),
    }
    cat=first["classification"]
    allowed={"CELL2_SINGLETON_SUFFICIENT","CELL2_SINGLETON_NOT_SUFFICIENT","MODE_SPECIFIC_SINGLETON","OTHER_VALID_PATTERN"}
    out={
        "schema":1,"experiment":"YGG-A39","prereg":PREREG,"parent_run":PARENT_RUN,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "validity":validity,"valid":all(validity.values()),
        "qualification":{"YGG_A39_ZERO_LESION_CELL2_SUFFICIENCY":all(validity.values()) and cat in allowed,"classification":cat},
        "analysis":first,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
