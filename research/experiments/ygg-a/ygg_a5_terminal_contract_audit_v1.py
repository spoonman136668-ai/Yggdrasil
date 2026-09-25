#!/usr/bin/env python3
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a4_atomic_egress_integrity_v1 as a4

PREREG="1562ffb51dfde29ed80e6b6e87974fe6075caf7f"

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

def audit_world(row):
    maturity=row["maturity"]
    result=row["result"]
    repair=result["repair"]
    mismatch=bool(maturity["pass"] and not repair["repair_integrity"])
    terminal159=[r for r in maturity["rows"] if r.get("kind")=="TERMINAL_159"]
    all_rows_pass=all(r.get("pass") is True for r in maturity["rows"])
    exact_terminal=bool(terminal159) and all(terminal159_exact(r) for r in terminal159)
    count_balance=(
        repair["verification_detected"]
        == repair["repaired"] + len(terminal159)
    )
    integrity=(
        result["incorrect_done"]==0
        and result["matching_duplicate_cell"]==0
        and result["matching_duplicate_request"]==0
    )
    explained=bool(
        mismatch
        and all_rows_pass
        and exact_terminal
        and count_balance
        and integrity
    )
    return {
        "replicate":row["manifest"]["replicate"],
        "maturity_pass":maturity["pass"],
        "legacy_repair_integrity":repair["repair_integrity"],
        "mismatch":mismatch,
        "terminal159_count":len(terminal159),
        "terminal159_rows":terminal159,
        "verification_detected":repair["verification_detected"],
        "repaired":repair["repaired"],
        "incorrect_done":result["incorrect_done"],
        "matching_duplicate_cell":result["matching_duplicate_cell"],
        "matching_duplicate_request":result["matching_duplicate_request"],
        "terminal159_explained":explained,
    }

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    primary=a4.primary()
    rows=[audit_world(row) for row in primary["sweep"]]
    mismatches=[r for r in rows if r["mismatch"]]
    maturity_fail_repair_fail=[
        r for r in rows
        if (not r["maturity_pass"]) and (not r["legacy_repair_integrity"])
    ]
    checks={
        "source_duplicate_byte_identical":bool(primary["duplicate"]["byte_identical"]),
        "at_least_one_contract_mismatch":bool(mismatches),
        "all_mismatches_terminal159_explained":bool(mismatches) and all(r["terminal159_explained"] for r in mismatches),
        "no_maturity_fail_repair_fail_support":len(maturity_fail_repair_fail)==0,
    }
    checks["YGG_A5_TERMINAL_CONTRACT_DIVERGENCE"]=all(checks.values())
    out={
        "schema":1,
        "experiment":"YGG-A5",
        "stage":"contract_audit",
        "prereg":PREREG,
        "source_experiment":"YGG-A4",
        "source_duplicate":primary["duplicate"],
        "qualification":checks,
        "mismatch_replicates":[r["replicate"] for r in mismatches],
        "rows":rows,
    }
    Path(sys.argv[1]).write_text(json.dumps(out,sort_keys=True,separators=(",",":")),encoding="utf-8")

if __name__=="__main__":
    main()
