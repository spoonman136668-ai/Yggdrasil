#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a4_atomic_egress_integrity_v1 as a4

PREREG="762fddfbb72bee9bff824917a7f24bbe2f5e0fb7"
PARENT_A5_CLOSURE="fb9ba4904e799c96b0a2b5a71d655d9a01262749"

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def terminal159_exact(row):
    return (
        row.get("kind")=="TERMINAL_159"
        and row.get("pass") is True
        and row.get("detection_epoch")==159
        and row.get("repair_epoch") is None
        and row.get("verified_epoch") is None
        and row.get("done_epoch") is None
        and row.get("terminal_state")=="REPAIR_PENDING"
    )

def summarize_world(row):
    result=row["result"]
    repair=result["repair"]
    maturity=row["maturity"]
    terminal=[r for r in maturity["rows"] if r.get("kind")=="TERMINAL_159"]
    exact_terminal=all(terminal159_exact(r) for r in terminal)
    horizon_aware=bool(
        result["incorrect_done"]==0
        and result["matching_duplicate_cell"]==0
        and result["matching_duplicate_request"]==0
        and maturity["pass"]
        and repair["verification_detected"]==repair["corruptions_reaching_egress"]
        and exact_terminal
        and repair["verification_detected"]==repair["repaired"]+len(terminal)
    )
    target=row.get("target_141",{})
    return {
        "replicate":row["manifest"]["replicate"],
        "baseline_feasible":a4.t.baseline_feasible(row),
        "legacy_repair_integrity":repair["repair_integrity"],
        "horizon_aware_repair_integrity":horizon_aware,
        "corruptions_reaching_egress":repair["corruptions_reaching_egress"],
        "verification_detected":repair["verification_detected"],
        "repaired":repair["repaired"],
        "terminal159_count":len(terminal),
        "terminal159_rows":terminal,
        "maturity_pass":maturity["pass"],
        "incorrect_done":result["incorrect_done"],
        "matching_duplicate_cell":result["matching_duplicate_cell"],
        "matching_duplicate_request":result["matching_duplicate_request"],
        "target_141":target,
    }

def one_pass():
    source=a4.primary()
    rows=[summarize_world(r) for r in source["sweep"]]
    srcq=source["qualification"]
    r10=next(r for r in rows if r["replicate"]==10)
    target=r10["target_141"]
    target_valid=bool(
        target.get("present")
        and target.get("detected")
        and target.get("first_egress_epoch")==159
        and (
            (
                target.get("stage")=="REPAIR_PENDING"
                and r10["terminal159_count"]>=1
                and any(x.get("rid")==141 and terminal159_exact(x) for x in r10["terminal159_rows"])
            )
            or (
                target.get("stage") in ("VERIFIED","DONE")
                and r10["incorrect_done"]==0
            )
        )
    )
    q={
        "baseline_feasible_count":srcq["baseline_feasible_count"],
        "evidence_coverage_pass":srcq["baseline_feasible_count"]>=8,
        "all_zero_incorrect_done":all(r["incorrect_done"]==0 for r in rows),
        "all_matching_integrity":all(r["matching_duplicate_cell"]==0 and r["matching_duplicate_request"]==0 for r in rows),
        "both_sibling_orders_exercised":srcq["both_sibling_orders_exercised"],
        "d_never_before_join":srcq["d_never_before_join"],
        "fork_dependencies_exact":srcq["fork_dependencies_exact"],
        "all_maturity_pass":all(r["maturity_pass"] for r in rows),
        "all_horizon_aware_repair_integrity":all(r["horizon_aware_repair_integrity"] for r in rows),
        "repair_reverify_fixture":srcq["repair_reverify_fixture"],
        "source_a4_duplicate_byte_identical":source["duplicate"]["byte_identical"],
        "replicate10_target141_terminal_valid":target_valid,
    }
    return {
        "schema":1,
        "experiment":"YGG-A6",
        "prereg":PREREG,
        "parent_a5_closure":PARENT_A5_CLOSURE,
        "source_a4_duplicate":source["duplicate"],
        "legacy_a4_verdict":srcq["YGG_A4_ATOMIC_EGRESS_INTEGRITY_HANDOFF"],
        "rows":rows,
        "qualification":q,
    }

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    first=one_pass()
    second=one_pass()
    b1=canonical(first)
    b2=canonical(second)
    duplicate=b1==b2
    q=first["qualification"]
    q["duplicate_complete_execution_byte_identical"]=duplicate
    q["YGG_A6_HORIZON_AWARE_ATOMIC_EGRESS_CONFIRMATION"]=all(q.values())
    out={
        "schema":1,
        "experiment":"YGG-A6",
        "prereg":PREREG,
        "parent_a5_closure":PARENT_A5_CLOSURE,
        "duplicate_byte_identical":duplicate,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "primary":first,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
