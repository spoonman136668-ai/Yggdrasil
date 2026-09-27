#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a61_causal_pair_context_sweep_v1 as a61

PREREG="994aa8361a7e131e8aee1dc260dcfc300c640e0b"
PARENT_RUN="36331200003"
MODES=("U_A0","U_A25")
PAIR=(105,111)
CONTEXTS=tuple(r for r in range(96,128) if r not in PAIR)
S1={96,97,99,103,111,112,113,116,121}
S1_COMMON={96,97,99,103,112,113,116,121}
CORRUPT=a61.CORRUPT
a44=a61.a44
a41=a61.a41
lu=a61.lu
flip_set=a61.flip_set
exact_change=a61.exact_change

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def one_mode(mode):
    by=a41.bases(); r6=by[6]; programs=r6["programs"]
    native=lu.make_arrivals(r6["seed"],programs)
    def run(subset):
        arr=flip_set(native,subset)
        row=a44.pair(r6,programs,arr,CORRUPT,mode)
        return {
            "subset":list(subset),"collapse":bool(row["collapse"]),
            "exact_registered_change":exact_change(native,arr,subset),
            "integrity":bool(row["integrity"]),
            "runtime_seed_exact":bool(row["runtime_seed_exact"]),
            "programs_exact":bool(row["programs_exact"]),
            "arrivals_exact":bool(row["arrivals_exact"]),
            "anchors_runtime_exact":bool(row["anchors_runtime_exact"]),
            "runtime_constants_frozen":bool(row["runtime_constants_frozen"]),
            "zero_lesion":row["zero_lesion"],"singleton_lesion":row["singleton_lesion"],
        }
    native_row=run(())
    s105=run((105,))
    s111=run((111,))
    pair=run(PAIR)
    contexts=[]
    for k in CONTEXTS:
        x=run((105,111,k))
        contexts.append({"context_rid":k,**x})
    s2=[x["context_rid"] for x in contexts if x["collapse"]]
    return {
        "mode":mode,"native":native_row,"single105":s105,"single111":s111,"pair":pair,
        "contexts":contexts,"suppressor_rids":s2,
        "shared_common":sorted(set(s2)&S1_COMMON),
        "lost_common":sorted(S1_COMMON-set(s2)),
        "new_suppressors":sorted(set(s2)-S1_COMMON),
    }

def classify(rows):
    if not all(r["native"]["collapse"] and r["single105"]["collapse"] and r["single111"]["collapse"] and not r["pair"]["collapse"] for r in rows):
        return "ANCHOR_NOT_REPRODUCED"
    if rows[0]["suppressor_rids"]!=rows[1]["suppressor_rids"]:
        return "CROSS_MODE_PORTABILITY_DIFFERENCE"
    s2=set(rows[0]["suppressor_rids"])
    shared=s2&S1_COMMON
    if S1_COMMON.issubset(s2) and not (s2-S1_COMMON):
        return "PORTABLE_SUPPRESSOR_FIELD"
    if shared:
        return "PARTIAL_SUPPRESSOR_PORTABILITY"
    if s2:
        return "PAIR_SPECIFIC_SUPPRESSION"
    return "NO_SUPPRESSION_FOR_SECOND_PAIR"

def one_pass():
    rows=[one_mode(m) for m in MODES]
    return {"s1":sorted(S1),"s1_common":sorted(S1_COMMON),"rows":rows,"classification":classify(rows)}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    old_validate=lu.validate_manifest; old_lesion=a44.p.lesion_set; old_alpha=float(a44.g.ALPHA)
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    allrows=[]
    for r in first["rows"]:
        allrows.extend([r["native"],r["single105"],r["single111"],r["pair"]]); allrows.extend(r["contexts"])
    validity={
        "duplicate_complete_execution_byte_identical":b1==b2,
        "anchors_exact":all(r["native"]["collapse"] and r["single105"]["collapse"] and r["single111"]["collapse"] and not r["pair"]["collapse"] for r in first["rows"]),
        "exact_30_contexts_per_mode":all([x["context_rid"] for x in r["contexts"]]==list(CONTEXTS) for r in first["rows"]),
        "s1_exact":first["s1"]==sorted(S1) and first["s1_common"]==sorted(S1_COMMON),
        "only_registered_stream_changes":all(x["exact_registered_change"] for x in allrows),
        "runtime_seed_exact":all(x["runtime_seed_exact"] for x in allrows),
        "programs_exact":all(x["programs_exact"] for x in allrows),
        "arrivals_exact":all(x["arrivals_exact"] for x in allrows),
        "anchors_runtime_exact":all(x["anchors_runtime_exact"] for x in allrows),
        "runtime_constants_frozen":all(x["runtime_constants_frozen"] for x in allrows),
        "lesions_exact":all(x["zero_lesion"]==[] and x["singleton_lesion"]==[2] for x in allrows),
        "scientific_integrity":all(x["integrity"] for x in allrows),
        "runtime_alpha_restored":float(a44.g.ALPHA)==old_alpha,
        "validator_restored":lu.validate_manifest is old_validate,
        "lesion_set_restored":a44.p.lesion_set is old_lesion,
    }
    cat=first["classification"]
    allowed={"PORTABLE_SUPPRESSOR_FIELD","PARTIAL_SUPPRESSOR_PORTABILITY","PAIR_SPECIFIC_SUPPRESSION","NO_SUPPRESSION_FOR_SECOND_PAIR","CROSS_MODE_PORTABILITY_DIFFERENCE","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-A62","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_A62_SUPPRESSOR_PORTABILITY":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
