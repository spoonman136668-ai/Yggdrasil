#!/usr/bin/env python3
import copy,hashlib,json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c3_resource_pressure_retention_v1 as c3
import ygg_c5_fine_pressure_transition_v1 as c5

PREREG="bd9b7ee416868afb2cca7ec2804b1744b522fce8"
PARENT_CLOSURE="577676f3b5129a6c602d1a1ced66b515cdae80c7"
EXPECTED_PARENT_HASH="7b6ea7e6bea1d80f718c0581669ed23adbe95488db4f75d84637388c71010ae1"
CONDITIONS=("000","100","010","001","110","101","011","111")

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def transition_cells(seed):
    l10=set(c5.fine_pressure(seed,10))
    l11=set(c5.fine_pressure(seed,11))
    l12=set(c5.fine_pressure(seed,12))
    l13=set(c5.fine_pressure(seed,13))
    a=next(iter(l11-l10))
    b=next(iter(l12-l11))
    c=next(iter(l13-l12))
    return sorted(l10),a,b,c

def factorial_lesion(seed,bits):
    base,a,b,c=transition_cells(seed)
    cells=set(base)
    for bit,cell in zip(bits,(a,b,c)):
        if bit=="1":
            cells.add(cell)
    return sorted(cells)

def condition_manifests(base,bits):
    out=[]
    for m in base:
        x=copy.deepcopy(m)
        x["lesion"]=factorial_lesion(m["seed"],bits)
        x["manifest_sha256"]=c3.lu2v.manifest_identity(x)
        if c3.non_lesion_bytes(x)!=c3.non_lesion_bytes(m):
            raise AssertionError("non-lesion manifest mutation")
        out.append(x)
    return out

def run_condition(base,bits):
    manifests=condition_manifests(base,bits)
    count=10+bits.count("1")
    old=c3.pressure_lesion
    c3.pressure_lesion=lambda seed,n: factorial_lesion(seed,bits)
    try:
        rows=[c3.run_pressure_manifest(m,count) for m in manifests]
    finally:
        c3.pressure_lesion=old
    return manifests,rows

def one_pass():
    base=c3.lu2v.primary_manifests(c3.LU2VF1)
    parent=[c3.lu2v.run_pair(m) for m in base]
    groups=[]
    for bits in CONDITIONS:
        manifests,rows=run_condition(base,bits)
        count=10+bits.count("1")
        summary=c3.summarize_level(count,rows,parent)
        detail=[]
        for m,row in zip(manifests,rows):
            l10,a,b,c=transition_cells(m["seed"])
            detail.append({
                "replicate":m["replicate"],
                "lesion":m["lesion"],
                "l10":l10,
                "transition_cells":{"A":a,"B":b,"C":c},
                "a25_stream_phase":row["a25"]["stream_phase"],
                "a25_correct_done":row["a25"]["correct_done"],
                "a25_backlog":row["a25"]["backlog"],
                "a25_maturity_pass":row["maturity"]["a25"]["pass"],
            })
        groups.append({
            "condition":bits,
            "lesion_cells":count,
            "summary":summary,
            "manifests":manifests,
            "detail":detail,
        })
    return {"parent":parent,"base_manifests":base,"groups":groups}

def paired_effects(retained,slot):
    bit={"A":0,"B":1,"C":2}[slot]
    pairs=[]
    for bg in CONDITIONS:
        if bg[bit]!="0":
            continue
        after=bg[:bit]+"1"+bg[bit+1:]
        if after not in retained:
            continue
        effect=int(retained[after])-int(retained[bg])
        pairs.append({"background":bg,"after":after,"effect":effect})
    return pairs

def classify(groups):
    retained={g["condition"]:bool(g["summary"]["retained"]) for g in groups}
    path=bool(
        retained["000"]
        and not retained["100"]
        and not retained["110"]
        and retained["111"]
    )
    effects={}
    context=[]
    for slot in ("A","B","C"):
        rows=paired_effects(retained,slot)
        vals={r["effect"] for r in rows}
        effects[slot]=rows
        if len(vals)>1:
            context.append(slot)
    if not path:
        cls="PATH_NOT_REPRODUCED"
    elif context:
        cls="INTERACTION_DRIVEN"
    else:
        cls="SINGLE_DIRECTION_OR_ADDITIVE"
    return {
        "retained_by_condition":retained,
        "c5_path_reproduced":path,
        "paired_effects":effects,
        "context_dependent_slots":context,
        "classification":cls,
        "YGG_C6_TRANSITION_INTERACTION":bool(path and context),
    }

def validity(run1,run2):
    parent_hash=hashlib.sha256(canonical(run1["parent"])).hexdigest()
    exact=True
    lineage=True
    matching=True
    for g in run1["groups"]:
        bits=g["condition"]
        expected_count=10+bits.count("1")
        for base,m,row in zip(run1["base_manifests"],g["manifests"],g["detail"]):
            l10,a,b,c=transition_cells(base["seed"])
            expected=set(l10)
            for bit,cell in zip(bits,(a,b,c)):
                if bit=="1":
                    expected.add(cell)
            exact=exact and set(m["lesion"])==expected and len(m["lesion"])==expected_count
            lineage=lineage and c3.non_lesion_bytes(m)==c3.non_lesion_bytes(base)
        matching=matching and bool(g["summary"]["a25_matching_integrity"])
    checks={
        "duplicate_complete_execution_byte_identical":canonical(run1)==canonical(run2),
        "parent_reference_hash_exact":parent_hash==EXPECTED_PARENT_HASH,
        "factorial_lesion_sets_exact":exact,
        "nonlesion_manifest_fields_frozen":lineage,
        "all_matching_integrity":matching,
    }
    return checks,parent_hash

def compact_groups(run):
    return [{
        "condition":g["condition"],
        "lesion_cells":g["lesion_cells"],
        "summary":g["summary"],
        "detail":g["detail"],
    } for g in run["groups"]]

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    first=one_pass()
    second=one_pass()
    checks,parent_hash=validity(first,second)
    qual=classify(first["groups"])
    out={
        "schema":1,
        "experiment":"YGG-C6",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "parent_reference_sha256":parent_hash,
        "conditions":list(CONDITIONS),
        "validity":checks,
        "valid":all(checks.values()),
        "mechanistic_classification_valid":qual["c5_path_reproduced"],
        "duplicate_sha256":hashlib.sha256(canonical(first)).hexdigest(),
        "qualification":qual,
        "groups":compact_groups(first),
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
