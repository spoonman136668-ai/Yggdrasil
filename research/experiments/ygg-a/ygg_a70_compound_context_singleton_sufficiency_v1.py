#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a69_compound_context_pair_membership_necessity_v1 as a69

PREREG="c08ec3e6cda89452322ddeebfc80e40c38cd1a40"
PARENT_RUN="36482937563"
MODES=("U_A0","U_A25")
ARMS=(("EMPTY",()),("CTX99",(99,)),("CTX107",(107,)),("CTX99_107",(99,107)))
CORRUPT=a69.CORRUPT
a44=a69.a44
a41=a69.a41
lu=a69.lu
flip_set=a69.flip_set
exact_change=a69.exact_change

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def run_mode(mode):
    by=a41.bases(); r6=by[6]; programs=r6["programs"]
    native=lu.make_arrivals(r6["seed"],programs)
    rows=[]
    for name,subset in ARMS:
        arr=flip_set(native,subset)
        row=a44.pair(r6,programs,arr,CORRUPT,mode)
        rows.append({
            "arm":name,
            "subset":list(subset),
            "collapse":bool(row["collapse"]),
            "exact_registered_change":exact_change(native,arr,subset),
            "integrity":bool(row["integrity"]),
            "runtime_seed_exact":bool(row["runtime_seed_exact"]),
            "programs_exact":bool(row["programs_exact"]),
            "arrivals_exact":bool(row["arrivals_exact"]),
            "anchors_runtime_exact":bool(row["anchors_runtime_exact"]),
            "runtime_constants_frozen":bool(row["runtime_constants_frozen"]),
            "zero_lesion":row["zero_lesion"],
            "singleton_lesion":row["singleton_lesion"],
        })
    d={x["arm"]:x for x in rows}
    if d["CTX99_107"]["collapse"]:
        cat="ANCHOR_NOT_REPRODUCED"
    elif not d["EMPTY"]["collapse"]:
        cat="BASELINE_ALREADY_RESCUED"
    elif (not d["CTX99"]["collapse"]) and (not d["CTX107"]["collapse"]):
        cat="EITHER_SINGLETON_SUFFICIENT"
    elif not d["CTX99"]["collapse"]:
        cat="CTX99_SINGLETON_SUFFICIENT"
    elif not d["CTX107"]["collapse"]:
        cat="CTX107_SINGLETON_SUFFICIENT"
    elif d["EMPTY"]["collapse"] and d["CTX99"]["collapse"] and d["CTX107"]["collapse"]:
        cat="BOTH_CONTEXT_MEMBERS_REQUIRED"
    else:
        cat="OTHER_VALID_PATTERN"
    return {"mode":mode,"classification":cat,"rows":rows}

def one_pass():
    modes=[run_mode(m) for m in MODES]
    if any(m["classification"]=="ANCHOR_NOT_REPRODUCED" for m in modes):
        cat="ANCHOR_NOT_REPRODUCED"
    elif modes[0]["classification"]!=modes[1]["classification"]:
        cat="CROSS_MODE_CONTEXT_DIFFERENCE"
    else:
        cat=modes[0]["classification"]
    return {"modes":modes,"classification":cat}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    old_validate=lu.validate_manifest
    old_lesion=a44.p.lesion_set
    old_alpha=float(a44.g.ALPHA)
    a=one_pass(); b=one_pass(); ba=canonical(a)
    rows=[x for m in a["modes"] for x in m["rows"]]
    pair_anchor=all(next(x for x in m["rows"] if x["arm"]=="CTX99_107")["collapse"] is False for m in a["modes"])
    validity={
        "prereg_commit_exact":PREREG=="c08ec3e6cda89452322ddeebfc80e40c38cd1a40",
        "modes_exact":[m["mode"] for m in a["modes"]]==list(MODES),
        "four_registered_arms_per_mode":all([x["arm"] for x in m["rows"]]==[x[0] for x in ARMS] for m in a["modes"]),
        "subsets_exact":all([x["subset"] for x in m["rows"]]==[list(x[1]) for x in ARMS] for m in a["modes"]),
        "no_original_pair_members":all(not any(v in {103,105,106,111,117,121,123} for v in x["subset"]) for x in rows),
        "a69_compound_context_anchor_exact":pair_anchor,
        "only_registered_stream_changes":all(x["exact_registered_change"] for x in rows),
        "runtime_seed_exact":all(x["runtime_seed_exact"] for x in rows),
        "programs_exact":all(x["programs_exact"] for x in rows),
        "arrivals_exact":all(x["arrivals_exact"] for x in rows),
        "anchors_runtime_exact":all(x["anchors_runtime_exact"] for x in rows),
        "runtime_constants_frozen":all(x["runtime_constants_frozen"] for x in rows),
        "lesions_exact":all(x["zero_lesion"]==[] and x["singleton_lesion"]==[2] for x in rows),
        "scientific_integrity":all(x["integrity"] for x in rows),
        "runtime_alpha_restored":float(a44.g.ALPHA)==old_alpha,
        "validator_restored":lu.validate_manifest is old_validate,
        "lesion_set_restored":a44.p.lesion_set is old_lesion,
        "duplicate_complete_execution_byte_identical":ba==canonical(b),
    }
    cat=a["classification"]
    allowed={"BOTH_CONTEXT_MEMBERS_REQUIRED","CTX99_SINGLETON_SUFFICIENT","CTX107_SINGLETON_SUFFICIENT","EITHER_SINGLETON_SUFFICIENT","BASELINE_ALREADY_RESCUED","CROSS_MODE_CONTEXT_DIFFERENCE","OTHER_VALID_PATTERN"}
    out={
        "schema":1,
        "experiment":"YGG-A70",
        "prereg":PREREG,
        "parent_run":PARENT_RUN,
        "duplicate_sha256":hashlib.sha256(ba).hexdigest(),
        "validity":validity,
        "valid":all(validity.values()),
        "qualification":{
            "YGG_A70_COMPOUND_CONTEXT_SINGLETON_SUFFICIENCY":all(validity.values()) and cat in allowed,
            "classification":cat,
        },
        "analysis":a,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__": main()
