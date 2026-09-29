#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a70_compound_context_singleton_sufficiency_v1 as a70

PREREG="f2474b8955e4dcf8222d2b5bbca24bb40a1c611f"
PARENT_RUN="36509325957"
MODES=("U_A0","U_A25")
VERTICES=(99,103,105,106,107,111,117,121,123)
CORRUPT=a70.CORRUPT
a44=a70.a44
a41=a70.a41
lu=a70.lu
flip_set=a70.flip_set
exact_change=a70.exact_change

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def run_mode(mode):
    by=a41.bases(); r6=by[6]; programs=r6["programs"]; native=lu.make_arrivals(r6["seed"],programs)
    arms=[("EMPTY",())]+[(f"V{v}",(v,)) for v in VERTICES]
    rows=[]
    for name,subset in arms:
        arr=flip_set(native,subset)
        row=a44.pair(r6,programs,arr,CORRUPT,mode)
        rows.append({
            "arm":name,"subset":list(subset),"collapse":bool(row["collapse"]),
            "exact_registered_change":exact_change(native,arr,subset),
            "integrity":bool(row["integrity"]),
            "runtime_seed_exact":bool(row["runtime_seed_exact"]),
            "programs_exact":bool(row["programs_exact"]),
            "arrivals_exact":bool(row["arrivals_exact"]),
            "anchors_runtime_exact":bool(row["anchors_runtime_exact"]),
            "runtime_constants_frozen":bool(row["runtime_constants_frozen"]),
            "zero_lesion":row["zero_lesion"],"singleton_lesion":row["singleton_lesion"],
        })
    rescue=[x["subset"][0] for x in rows if x["subset"] and not x["collapse"]]
    return {"mode":mode,"rows":rows,"singleton_rescue_set":rescue}

def one_pass():
    parent=a70.one_pass()
    modes=[run_mode(m) for m in MODES]
    anchor_ok=(parent["classification"]=="EITHER_SINGLETON_SUFFICIENT" and
               all(next(x for x in m["rows"] if x["arm"]=="EMPTY")["collapse"] for m in modes) and
               all(not next(x for x in m["rows"] if x["arm"]=="V99")["collapse"] for m in modes) and
               all(not next(x for x in m["rows"] if x["arm"]=="V107")["collapse"] for m in modes))
    sets=[m["singleton_rescue_set"] for m in modes]
    if not anchor_ok:
        cat="ANCHOR_NOT_REPRODUCED"
    elif sets[0]!=sets[1]:
        cat="CROSS_MODE_SINGLETON_MAP"
    else:
        s=set(sets[0]); v=set(VERTICES); ctx={99,107}
        if s==ctx: cat="CONTEXT_ONLY_SINGLETON_RESCUE"
        elif s==v: cat="ALL_ROUTE_VERTICES_SINGLETON_RESCUE"
        elif ctx.issubset(s) and len(s)>2: cat="BROAD_ROUTE_SINGLETON_REDUNDANCY"
        else: cat="OTHER_VALID_PATTERN"
    return {"parent_classification":parent["classification"],"modes":modes,"classification":cat}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    old_validate=lu.validate_manifest; old_lesion=a44.p.lesion_set; old_alpha=float(a44.g.ALPHA)
    a=one_pass(); b=one_pass(); ba=canonical(a)
    rows=[x for m in a["modes"] for x in m["rows"]]
    validity={
        "prereg_commit_exact":PREREG=="f2474b8955e4dcf8222d2b5bbca24bb40a1c611f",
        "parent_a70_anchor_exact":a["parent_classification"]=="EITHER_SINGLETON_SUFFICIENT",
        "modes_exact":[m["mode"] for m in a["modes"]]==list(MODES),
        "vertices_exact":list(VERTICES)==[99,103,105,106,107,111,117,121,123],
        "ten_registered_arms_per_mode":all(len(m["rows"])==10 for m in a["modes"]),
        "singleton_only":all(len(x["subset"])<=1 for x in rows),
        "empty_and_context_anchors_exact":all(next(x for x in m["rows"] if x["arm"]=="EMPTY")["collapse"] and not next(x for x in m["rows"] if x["arm"]=="V99")["collapse"] and not next(x for x in m["rows"] if x["arm"]=="V107")["collapse"] for m in a["modes"]),
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
    allowed={"CONTEXT_ONLY_SINGLETON_RESCUE","ALL_ROUTE_VERTICES_SINGLETON_RESCUE","BROAD_ROUTE_SINGLETON_REDUNDANCY","CROSS_MODE_SINGLETON_MAP","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-A71","prereg":PREREG,"parent_run":PARENT_RUN,"duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),"qualification":{"YGG_A71_ROUTE_VERTEX_SINGLETON_SUFFICIENCY_MAP":all(validity.values()) and cat in allowed,"classification":cat},"analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__": main()
