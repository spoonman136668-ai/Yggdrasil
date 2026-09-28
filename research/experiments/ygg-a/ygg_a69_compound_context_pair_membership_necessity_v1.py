#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a68_gap_route_exhaustion_v1 as a68

PREREG="ff96f4e0395103944c24a0fc2925faaff0105cad"
PARENT_RUN="36356248434"
MODES=("U_A0","U_A25")
PAIRS=((105,111),(105,117),(106,117),(117,123),(121,123))
CTX=(99,107)
CORRUPT=a68.CORRUPT
a44=a68.a44
a41=a68.a41
lu=a68.lu
flip_set=a68.flip_set
exact_change=a68.exact_change

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
    rows=[]
    for i,j in PAIRS:
        ctx=run(CTX)
        ia=run((i,)+CTX)
        ja=run((j,)+CTX)
        pair=run((i,j)+CTX)
        if not pair["collapse"]:
            if not ctx["collapse"]:
                pattern="COMPOUND_CONTEXT_ROUTE"
            elif (not ia["collapse"]) or (not ja["collapse"]):
                pattern="ONE_MEMBER_SUFFICIENT"
            else:
                pattern="ORIGINAL_PAIR_ESSENTIAL"
        else:
            pattern="ANCHOR_NOT_REPRODUCED"
        rows.append({"pair":[i,j],"context_only":ctx,"i_plus_context":ia,"j_plus_context":ja,
                     "pair_plus_context":pair,"dependency_pattern":pattern})
    return {"mode":mode,"rows":rows}

def classify(modes):
    if not all(all(not x["pair_plus_context"]["collapse"] for x in m["rows"]) for m in modes):
        return "ANCHOR_NOT_REPRODUCED"
    p0=[x["dependency_pattern"] for x in modes[0]["rows"]]
    p1=[x["dependency_pattern"] for x in modes[1]["rows"]]
    if p0!=p1: return "CROSS_MODE_DEPENDENCE_DIFFERENCE"
    uniq=set(p0)
    if uniq=={"ORIGINAL_PAIR_ESSENTIAL"}: return "ORIGINAL_PAIR_ESSENTIAL"
    if "COMPOUND_CONTEXT_ROUTE" in uniq: return "COMPOUND_CONTEXT_ROUTE" if len(uniq)==1 else "MIXED_PAIR_DEPENDENCE"
    if "ONE_MEMBER_SUFFICIENT" in uniq: return "ONE_MEMBER_SUFFICIENT" if len(uniq)==1 else "MIXED_PAIR_DEPENDENCE"
    return "MIXED_PAIR_DEPENDENCE" if len(uniq)>1 else "OTHER_VALID_PATTERN"

def one_pass():
    modes=[one_mode(m) for m in MODES]
    return {"modes":modes,"classification":classify(modes)}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    old_validate=lu.validate_manifest; old_lesion=a44.p.lesion_set; old_alpha=float(a44.g.ALPHA)
    a=one_pass(); b=one_pass(); ba=canonical(a)
    arms=[]
    for m in a["modes"]:
        for x in m["rows"]:
            arms.extend([x["context_only"],x["i_plus_context"],x["j_plus_context"],x["pair_plus_context"]])
    validity={
        "duplicate_complete_execution_byte_identical":ba==canonical(b),
        "five_reactivated_pairs_exact":all([tuple(x["pair"]) for x in m["rows"]]==list(PAIRS) for m in a["modes"]),
        "context_exact":CTX==(99,107),
        "four_registered_arms_per_pair":all(len([x["context_only"],x["i_plus_context"],x["j_plus_context"],x["pair_plus_context"]])==4 for m in a["modes"] for x in m["rows"]),
        "a68_pair_plus_context_anchors_exact":all(all(not x["pair_plus_context"]["collapse"] for x in m["rows"]) for m in a["modes"]),
        "only_registered_stream_changes":all(x["exact_registered_change"] for x in arms),
        "runtime_seed_exact":all(x["runtime_seed_exact"] for x in arms),
        "programs_exact":all(x["programs_exact"] for x in arms),
        "arrivals_exact":all(x["arrivals_exact"] for x in arms),
        "anchors_runtime_exact":all(x["anchors_runtime_exact"] for x in arms),
        "runtime_constants_frozen":all(x["runtime_constants_frozen"] for x in arms),
        "lesions_exact":all(x["zero_lesion"]==[] and x["singleton_lesion"]==[2] for x in arms),
        "scientific_integrity":all(x["integrity"] for x in arms),
        "runtime_alpha_restored":float(a44.g.ALPHA)==old_alpha,
        "validator_restored":lu.validate_manifest is old_validate,
        "lesion_set_restored":a44.p.lesion_set is old_lesion,
    }
    cat=a["classification"]
    allowed={"ORIGINAL_PAIR_ESSENTIAL","ONE_MEMBER_SUFFICIENT","COMPOUND_CONTEXT_ROUTE","MIXED_PAIR_DEPENDENCE","CROSS_MODE_DEPENDENCE_DIFFERENCE","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-A69","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_A69_COMPOUND_CONTEXT_PAIR_MEMBERSHIP_NECESSITY":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
