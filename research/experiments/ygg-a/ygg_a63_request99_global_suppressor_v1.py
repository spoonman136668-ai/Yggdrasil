#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a62_suppressor_portability_v1 as a62

PREREG="a23620651391a22b2a71ff2043c9a83d46dc921f"
PARENT_RUN="36332265345"
MODES=("U_A0","U_A25")
PAIRS=((103,111),(105,111),(105,117),(106,111),(106,117),(117,123),(121,123))
SUPPRESSOR=99
CORRUPT=a62.CORRUPT
a44=a62.a44
a41=a62.a41
lu=a62.lu
flip_set=a62.flip_set
exact_change=a62.exact_change

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
    pair_rows=[]
    for i,j in PAIRS:
        si=run((i,)); sj=run((j,)); pair=run((i,j)); triple=run((i,j,SUPPRESSOR))
        pair_rows.append({
            "pair":[i,j],"single_i":si,"single_j":sj,"pair_arm":pair,"triple99":triple,
            "request99_restores_collapse":bool(triple["collapse"])
        })
    rescued=[x["pair"] for x in pair_rows if x["request99_restores_collapse"]]
    return {"mode":mode,"native":native_row,"pairs":pair_rows,"rescued_pairs":rescued}

def classify(rows):
    if not all(r["native"]["collapse"] and all(
        p["single_i"]["collapse"] and p["single_j"]["collapse"] and not p["pair_arm"]["collapse"]
        for p in r["pairs"]) for r in rows):
        return "ANCHOR_NOT_REPRODUCED"
    if rows[0]["rescued_pairs"]!=rows[1]["rescued_pairs"]:
        return "CROSS_MODE_99_DIFFERENCE"
    n=len(rows[0]["rescued_pairs"])
    if n==7: return "REQUEST99_GLOBAL_SUPPRESSOR"
    if 1<=n<=6: return "REQUEST99_PARTIAL_SUPPRESSOR"
    if n==0: return "REQUEST99_NO_PORTABLE_EFFECT"
    return "OTHER_VALID_PATTERN"

def one_pass():
    rows=[one_mode(m) for m in MODES]
    return {"rows":rows,"classification":classify(rows)}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    old_validate=lu.validate_manifest; old_lesion=a44.p.lesion_set; old_alpha=float(a44.g.ALPHA)
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    allrows=[]
    for r in first["rows"]:
        allrows.append(r["native"])
        for p in r["pairs"]: allrows.extend([p["single_i"],p["single_j"],p["pair_arm"],p["triple99"]])
    validity={
        "duplicate_complete_execution_byte_identical":b1==b2,
        "seven_pairs_exact":all([tuple(p["pair"]) for p in r["pairs"]]==list(PAIRS) for r in first["rows"]),
        "request99_not_pair_member":all(SUPPRESSOR not in pair for pair in PAIRS),
        "anchors_exact":all(r["native"]["collapse"] and all(
            p["single_i"]["collapse"] and p["single_j"]["collapse"] and not p["pair_arm"]["collapse"]
            for p in r["pairs"]) for r in first["rows"]),
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
    allowed={"REQUEST99_GLOBAL_SUPPRESSOR","REQUEST99_PARTIAL_SUPPRESSOR","REQUEST99_NO_PORTABLE_EFFECT","CROSS_MODE_99_DIFFERENCE","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-A63","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_A63_REQUEST99_GLOBAL_SUPPRESSOR":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
