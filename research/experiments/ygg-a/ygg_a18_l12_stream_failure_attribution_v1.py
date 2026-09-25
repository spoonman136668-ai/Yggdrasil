#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a17_l12_topology_failure_rescue_v1 as a17

PREREG="71f1297570076cad1dd7fb20bdbabc79dabae602"
PARENT_CLOSURE="f5906290375b5dfac8415e5cb2b612deb74ac17a"
TARGET_ALPHA=1.0

a13=a17.a13
g=a17.g

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def stream_failures(anchor_rows,current_rows,field):
    base={int(r["replicate"]):r[field] for r in anchor_rows}
    failures=[]
    for row in current_rows:
        rep=int(row["replicate"])
        br=base[rep]["result"]["stream_phase"]
        cr=row[field]["result"]["stream_phase"]
        for ph in range(5):
            ps=str(ph)
            for stream in ("C","S"):
                base_n=br[ps][stream]
                cur_n=cr[ps][stream]
                if base_n>=4 and cur_n<0.75*base_n:
                    failures.append({
                        "replicate":rep,
                        "phase":ph,
                        "stream":stream,
                        "l8":base_n,
                        "l12":cur_n,
                        "ratio":cur_n/base_n if base_n else None,
                    })
    return failures

def category(off_fail,on_fail):
    if not off_fail and not on_fail:
        return "BOTH_PASS"
    if not off_fail and on_fail:
        return "REPAIR_INDUCED"
    if off_fail and not on_fail:
        return "REPAIR_RESCUES"
    if off_fail==on_fail:
        return "TOPOLOGY_ONLY_IDENTICAL"
    return "TOPOLOGY_DOMINANT_DIFFERENT"

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")

    original_alpha=float(g.ALPHA)
    g.ALPHA=TARGET_ALPHA
    try:
        anchor=a13.one_pass()
    finally:
        g.ALPHA=original_alpha

    first=a17.l12_one_pass(anchor["rows"])
    second=a17.l12_one_pass(anchor["rows"])

    b1=canonical(first)
    b2=canonical(second)

    off_fail=stream_failures(anchor["rows"],first["rows"],"a25_off")
    on_fail=stream_failures(anchor["rows"],first["rows"],"a25_on")
    cat=category(off_fail,on_fail)

    off_zero_damage=all(
        r["a25_off"]["branch"]["scheduled"]==0
        and r["a25_off"]["branch"]["applied"]==0
        and r["a25_off"]["branch"]["repaired"]==0
        for r in first["rows"]
    )
    on_exact=all(
        r["a25_on"]["branch"]["scheduled"]==58
        and r["a25_on"]["branch"]["scheduled_b"]==29
        and r["a25_on"]["branch"]["scheduled_c"]==29
        and r["a25_on"]["branch"]["applied"]==58
        and r["a25_on"]["branch"]["repaired"]==58
        for r in first["rows"]
    )
    common_integrity=all(
        r["a25_off"]["result"]["matching_duplicate_cell"]==0
        and r["a25_off"]["result"]["matching_duplicate_request"]==0
        and r["a25_off"]["maturity"]["pass"]
        and r["a25_off"]["horizon_aware_repair_integrity"]
        and r["a25_on"]["result"]["matching_duplicate_cell"]==0
        and r["a25_on"]["result"]["matching_duplicate_request"]==0
        and r["a25_on"]["maturity"]["pass"]
        and r["a25_on"]["horizon_aware_repair_integrity"]
        for r in first["rows"]
    )
    exact_l12=bool(first["qualification"]["l12_exact_c3_nested_construction"])
    duplicate=b1==b2
    alpha_restored=float(g.ALPHA)==original_alpha

    allowed={
        "TOPOLOGY_ONLY_IDENTICAL",
        "TOPOLOGY_DOMINANT_DIFFERENT",
        "REPAIR_INDUCED",
        "REPAIR_RESCUES",
        "BOTH_PASS",
    }
    validity={
        "exact_a17_l12_topology":exact_l12,
        "a15_l8_alpha100_anchor_exact":hashlib.sha256(canonical(anchor)).hexdigest()==a17.A15_ALPHA100_HASH,
        "damage_off_zero_scheduled_branch_damage":off_zero_damage,
        "damage_on_exact_58_repairs":on_exact,
        "matching_maturity_terminal_integrity_exact":common_integrity,
        "duplicate_execution_byte_identical":duplicate,
        "runtime_alpha_restored":alpha_restored,
    }
    qualification={
        "YGG_A18_L12_STREAM_FAILURE_ATTRIBUTION":bool(all(validity.values()) and cat in allowed),
        "attribution_category":cat,
        "damage_off_stream_noncollapse":len(off_fail)==0,
        "damage_on_stream_noncollapse":len(on_fail)==0,
    }
    out={
        "schema":1,
        "experiment":"YGG-A18",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "validity":validity,
        "valid":all(validity.values()),
        "qualification":qualification,
        "damage_off_failures":off_fail,
        "damage_on_failures":on_fail,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
