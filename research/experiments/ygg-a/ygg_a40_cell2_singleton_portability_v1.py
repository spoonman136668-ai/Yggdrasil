#!/usr/bin/env python3
import copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a28_replicate6_cell2_interaction_decomposition_v1 as a28

PREREG="f5e4a95a16fa2a3276fd473374dbbfa635aa6d8b"
PARENT_RUN="36275113326"
TARGET=2
MODES=("U_A0","U_A25")

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def make_manifest(base,lesion):
    m=copy.deepcopy(base)
    m["lesion"]=sorted(lesion)
    m["manifest_sha256"]=a28.a27.t.manifest_identity(m)
    if a28.a27.a19.nonlesion_bytes(m)!=a28.a27.a19.nonlesion_bytes(base):
        raise AssertionError("A40 nonlesion mutation")
    return m

def score(base,mode,lesion):
    m=make_manifest(base,lesion)
    old_validate=a28.a27.t.validate_manifest
    old_lesion=a28.a27.p.lesion_set
    old_alpha=float(a28.a27.g.ALPHA)
    a28.a27.g.ALPHA=a28.a27.ALPHA
    a28.a27.t.validate_manifest=a28.a27.a22.pressure_validate
    try:
        a28.a27.p.lesion_set=lambda seed:set(lesion)
        row=a28.a27.a8.scored(m,mode,False)
    finally:
        a28.a27.t.validate_manifest=old_validate
        a28.a27.p.lesion_set=old_lesion
        a28.a27.g.ALPHA=old_alpha
    return row,m

def integrity(row):
    return (
        row["result"]["incorrect_done"]==0 and
        row["result"]["matching_duplicate_cell"]==0 and
        row["result"]["matching_duplicate_request"]==0 and
        bool(row["maturity"]["pass"]) and
        bool(row["horizon_aware_repair_integrity"]) and
        row["branch"]["scheduled"]==0 and
        row["branch"]["applied"]==0 and
        row["branch"]["repaired"]==0
    )

def one_mode(mode):
    bases=a28.a27.t.primary_manifests(a28.a27.a8.A1_PREREG)
    rows=[]
    for base in bases:
        rep=int(base["replicate"])
        zero,m0=score(base,mode,[])
        single,m1=score(base,mode,[TARGET])
        fs=a28.collapsed(zero,single)
        rows.append({
            "replicate":rep,
            "zero_lesion":[],
            "singleton_lesion":[TARGET],
            "collapse":bool(fs),
            "failures":fs,
            "zero_integrity":bool(integrity(zero)),
            "singleton_integrity":bool(integrity(single)),
            "zero_nonlesion_preserved":a28.a27.a19.nonlesion_bytes(m0)==a28.a27.a19.nonlesion_bytes(base),
            "singleton_nonlesion_preserved":a28.a27.a19.nonlesion_bytes(m1)==a28.a27.a19.nonlesion_bytes(base),
        })
    return {"mode":mode,"rows":rows,"replicate_ids":[r["replicate"] for r in rows],
            "collapsing_replicates":[r["replicate"] for r in rows if r["collapse"]]}

def classify(rows):
    sets=[r["collapsing_replicates"] for r in rows]
    ids=rows[0]["replicate_ids"]
    if sets[0]!=sets[1]: return "CROSS_MODE_SINGLETON_DIFFERENCE"
    s=sets[0]
    if not s: return "NO_SINGLETON_EFFECT"
    if s==ids: return "GLOBAL_SINGLETON_SENSITIVITY"
    if s==[6]: return "REPLICATE6_SPECIFIC"
    if len(s)>=2 and len(s)<len(ids): return "MULTIREPLICATE_SINGLETON_SENSITIVITY"
    return "OTHER_VALID_PATTERN"

def one_pass():
    rows=[one_mode(m) for m in MODES]
    return {"rows":rows,"classification":classify(rows)}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    old_alpha=float(a28.a27.g.ALPHA)
    old_validate=a28.a27.t.validate_manifest
    old_lesion=a28.a27.p.lesion_set
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    ids=[r["replicate_ids"] for r in first["rows"]]
    validity={
        "duplicate_complete_execution_byte_identical":b1==b2,
        "alpha_exact":a28.a27.ALPHA==0.25,
        "modes_exact":[r["mode"] for r in first["rows"]]==list(MODES),
        "target_cell_exact":TARGET==a28.TARGET_CELL==2,
        "full_primary_population_consistent":len(ids)==2 and ids[0]==ids[1] and len(ids[0])>0 and len(set(ids[0]))==len(ids[0]),
        "lesions_exact":all(all(x["zero_lesion"]==[] and x["singleton_lesion"]==[2] for x in r["rows"]) for r in first["rows"]),
        "scientific_arm_integrity":all(all(x["zero_integrity"] and x["singleton_integrity"] for x in r["rows"]) for r in first["rows"]),
        "nonlesion_manifest_bytes_frozen":all(all(x["zero_nonlesion_preserved"] and x["singleton_nonlesion_preserved"] for x in r["rows"]) for r in first["rows"]),
        "runtime_alpha_restored":float(a28.a27.g.ALPHA)==old_alpha,
        "validator_restored":a28.a27.t.validate_manifest is old_validate,
        "lesion_set_restored":a28.a27.p.lesion_set is old_lesion,
    }
    cat=first["classification"]
    allowed={"GLOBAL_SINGLETON_SENSITIVITY","REPLICATE6_SPECIFIC","MULTIREPLICATE_SINGLETON_SENSITIVITY","CROSS_MODE_SINGLETON_DIFFERENCE","NO_SINGLETON_EFFECT","OTHER_VALID_PATTERN"}
    out={
        "schema":1,"experiment":"YGG-A40","prereg":PREREG,"parent_run":PARENT_RUN,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "validity":validity,"valid":all(validity.values()),
        "qualification":{"YGG_A40_CELL2_SINGLETON_PORTABILITY":all(validity.values()) and cat in allowed,"classification":cat},
        "analysis":first,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
