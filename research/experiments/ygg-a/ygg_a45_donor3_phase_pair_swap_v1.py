#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a44_corruption_phase_rotation_v1 as a44

PREREG="c0f23fa9118546038e02a37e86cbfb10e88dba4d"
PARENT_RUN="36283331102"
DONOR=3
PHASES=[0,1,2,3,4]
PAIRS=[(a,b) for a in PHASES for b in PHASES if a<b]
MODES=("U_A0","U_A25")

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def swap_phase_blocks(ids,a,b):
    out=[]
    for rid in ids:
        ph=rid//32; off=rid%32
        if ph==a: nr=b*32+off
        elif ph==b: nr=a*32+off
        else: nr=rid
        out.append(nr)
    if len(set(out))!=len(out):
        raise AssertionError("A45 non-bijective swap")
    return sorted(out)

def one_mode(mode):
    by=a44.a41.bases()
    r6=by[6]
    programs=r6["programs"]
    arrivals=a44.lu.make_arrivals(r6["seed"],programs)
    donor_seed=by[DONOR]["seed"]
    base=a44.base_corrupt(donor_seed,arrivals)
    anchor_base=a44.pair(r6,programs,arrivals,base,mode)
    rot1_ids=a44.rotate(base,1)
    anchor_rot1=a44.pair(r6,programs,arrivals,rot1_ids,mode)
    arms=[]
    for a,b in PAIRS:
        ids=swap_phase_blocks(base,a,b)
        row=a44.pair(r6,programs,arrivals,ids,mode)
        before_offsets=sorted([rid%32 for rid in base if rid//32 in (a,b)])
        after_offsets=sorted([rid%32 for rid in ids if rid//32 in (a,b)])
        arms.append({
            "phase_a":a,"phase_b":b,
            "collapse":bool(row["collapse"]),
            "failures":row["failures"],
            "corrupt_ids":ids,
            "count_preserved":len(ids)==len(base),
            "within_pair_offsets_preserved":before_offsets==after_offsets,
            "integrity":bool(row["integrity"]),
            "runtime_seed_exact":bool(row["runtime_seed_exact"]),
            "programs_exact":bool(row["programs_exact"]),
            "arrivals_exact":bool(row["arrivals_exact"]),
            "anchors_runtime_exact":bool(row["anchors_runtime_exact"]),
            "runtime_constants_frozen":bool(row["runtime_constants_frozen"]),
            "zero_lesion":row["zero_lesion"],"singleton_lesion":row["singleton_lesion"],
        })
    retained=[[x["phase_a"],x["phase_b"]] for x in arms if x["collapse"]]
    broken=[[x["phase_a"],x["phase_b"]] for x in arms if not x["collapse"]]
    return {
        "mode":mode,
        "donor":DONOR,
        "base_corrupt_ids":base,
        "base_anchor_collapse":bool(anchor_base["collapse"]),
        "rotation1_anchor_collapse":bool(anchor_rot1["collapse"]),
        "arms":arms,
        "retained_collapse_pairs":retained,
        "abolished_collapse_pairs":broken,
    }

def classify(rows):
    if any((not r["base_anchor_collapse"]) or r["rotation1_anchor_collapse"] for r in rows):
        return "ANCHOR_NOT_REPRODUCED"
    p0={(x["phase_a"],x["phase_b"]):x["collapse"] for x in rows[0]["arms"]}
    p1={(x["phase_a"],x["phase_b"]):x["collapse"] for x in rows[1]["arms"]}
    if p0!=p1: return "CROSS_MODE_PAIR_DIFFERENCE"
    vals=list(p0.values())
    if vals and all(not v for v in vals): return "ANY_PAIR_SWAP_BREAKS"
    if vals and all(v for v in vals): return "PAIR_SWAP_ROBUST"
    if any(vals) and any(not v for v in vals): return "MIXED_PHASE_PAIR_SENSITIVITY"
    return "OTHER_VALID_PATTERN"

def one_pass():
    rows=[one_mode(m) for m in MODES]
    return {"rows":rows,"classification":classify(rows)}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    old_validate=a44.lu.validate_manifest; old_lesion=a44.p.lesion_set; old_alpha=float(a44.g.ALPHA)
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    arms=[x for r in first["rows"] for x in r["arms"]]
    validity={
        "duplicate_complete_execution_byte_identical":b1==b2,
        "donor3_exact":all(r["donor"]==3 for r in first["rows"]),
        "modes_exact":[r["mode"] for r in first["rows"]]==list(MODES),
        "ten_phase_pairs_exact":all([(x["phase_a"],x["phase_b"]) for x in r["arms"]]==PAIRS for r in first["rows"]),
        "base_anchor_reproduced":all(r["base_anchor_collapse"] for r in first["rows"]),
        "rotation1_anchor_reproduced":all(not r["rotation1_anchor_collapse"] for r in first["rows"]),
        "count_preserved":all(x["count_preserved"] for x in arms),
        "within_pair_offsets_preserved":all(x["within_pair_offsets_preserved"] for x in arms),
        "runtime_seed_exact":all(x["runtime_seed_exact"] for x in arms),
        "programs_exact":all(x["programs_exact"] for x in arms),
        "arrivals_exact":all(x["arrivals_exact"] for x in arms),
        "anchors_runtime_exact":all(x["anchors_runtime_exact"] for x in arms),
        "runtime_constants_frozen":all(x["runtime_constants_frozen"] for x in arms),
        "lesions_exact":all(x["zero_lesion"]==[] and x["singleton_lesion"]==[2] for x in arms),
        "scientific_integrity":all(x["integrity"] for x in arms),
        "runtime_alpha_restored":float(a44.g.ALPHA)==old_alpha,
        "validator_restored":a44.lu.validate_manifest is old_validate,
        "lesion_set_restored":a44.p.lesion_set is old_lesion,
    }
    cat=first["classification"]
    allowed={"ANY_PAIR_SWAP_BREAKS","MIXED_PHASE_PAIR_SENSITIVITY","PAIR_SWAP_ROBUST","CROSS_MODE_PAIR_DIFFERENCE","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-A45","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_A45_DONOR3_PHASE_PAIR_SWAP":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
