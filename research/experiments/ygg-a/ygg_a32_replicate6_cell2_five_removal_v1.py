#!/usr/bin/env python3
import hashlib,itertools,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a28_replicate6_cell2_interaction_decomposition_v1 as a28

PREREG="3e648c56ab50197cc24903cf1dd713af3f1de5a3"
PARENT_RUN="36255027719"

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def one_mode(mode):
    base=a28.base6()
    l11=sorted(a28.a27.anchor_lesion(base["seed"]))
    anchor=a28.score(mode,l11)
    positive=a28.score(mode,sorted(l11+[a28.TARGET_CELL]))
    pc=a28.collapsed(anchor,positive)
    arms=[]
    for quint in itertools.combinations(l11,5):
        lesion=sorted([z for z in l11 if z not in quint]+[a28.TARGET_CELL])
        row=a28.score(mode,lesion)
        fs=a28.collapsed(anchor,row)
        arms.append({
            "removed_quint":list(quint),
            "collapse":bool(fs),
            "failures":fs,
            "maturity_pass":bool(row["maturity"]["pass"]),
            "incorrect_done":row["result"]["incorrect_done"],
            "matching_duplicate_cell":row["result"]["matching_duplicate_cell"],
            "matching_duplicate_request":row["result"]["matching_duplicate_request"],
            "branch_scheduled":row["branch"]["scheduled"],
            "branch_applied":row["branch"]["applied"],
            "branch_repaired":row["branch"]["repaired"],
        })
    return {
        "mode":mode,
        "replicate":int(base["replicate"]),
        "l11":l11,
        "positive_control_collapse":bool(pc),
        "arms":arms,
        "abolishing_quints":[a["removed_quint"] for a in arms if not a["collapse"]],
    }

def one_pass():
    rows=[one_mode(m) for m in a28.MODES]
    sets=[r["abolishing_quints"] for r in rows]
    if sets[0]!=sets[1]:
        cat="MODE_SPECIFIC_FIVE_INTERACTION"
    elif not sets[0]:
        cat="NO_FIVE_NECESSITY"
    elif sets[0]:
        cat="FIVE_NECESSITY_FOUND"
    else:
        cat="OTHER_VALID_PATTERN"
    return {"rows":rows,"classification":cat}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    first=one_pass()
    second=one_pass()
    b1=canonical(first)
    b2=canonical(second)
    validity={
        "duplicate_complete_execution_byte_identical":b1==b2,
        "actual_replicate6_verified":all(r["replicate"]==6 for r in first["rows"]),
        "l11_exact":all(r["l11"]==[7,15,23,29,31,32,39,47,52,55,63] for r in first["rows"]),
        "target_cell_exact":a28.TARGET_CELL==2,
        "alpha_exact":a28.a27.ALPHA==0.25,
        "positive_control_reproduced":all(r["positive_control_collapse"] for r in first["rows"]),
        "four_hundred_sixty_two_unique_five_arms":all(
            len(r["arms"])==462 and len({tuple(a["removed_quint"]) for a in r["arms"]})==462
            for r in first["rows"]
        ),
        "arm_integrity":all(
            all(
                a["maturity_pass"]
                and a["incorrect_done"]==0
                and a["matching_duplicate_cell"]==0
                and a["matching_duplicate_request"]==0
                and a["branch_scheduled"]==0
                and a["branch_applied"]==0
                and a["branch_repaired"]==0
                for a in r["arms"]
            )
            for r in first["rows"]
        ),
    }
    cat=first["classification"]
    allowed={"FIVE_NECESSITY_FOUND","MODE_SPECIFIC_FIVE_INTERACTION","NO_FIVE_NECESSITY","OTHER_VALID_PATTERN"}
    out={
        "schema":1,
        "experiment":"YGG-A32",
        "prereg":PREREG,
        "parent_run":PARENT_RUN,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "validity":validity,
        "valid":all(validity.values()),
        "qualification":{
            "YGG_A32_REPLICATE6_CELL2_FIVE_REMOVAL":all(validity.values()) and cat in allowed,
            "classification":cat,
        },
        "analysis":first,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
