"""Read-only CKAD30 two-pilot custody verification. Does not invoke world generator or scorer."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
def check(ok, name):
    if not ok:
        raise ValueError("CKAD30_AUDIT_FAIL_CLOSED_"+name)


def main():
    lock_raw=(HERE/"source_lock.json").read_bytes()
    lock=json.loads(lock_raw)
    screen_raw=(HERE/"pilot_screen_report.json").read_bytes()
    report=json.loads(screen_raw)
    check(report.get("schema")=="yggdrasil.ckad30.pilot-screen.v1", "SCREEN_SCHEMA")
    check(report["source_lock_sha256"]==hashlib.sha256(lock_raw).hexdigest(), "LOCK")
    check(report["pilot_seeds"]==[9101,9102] and
          report["primary_seeds_untouched"]==[707,808,909] and
          report["primary_scored"] is False, "SEED_CUSTODY")
    cases=[]
    for seed in (9101,9102):
        raw=(HERE/f"pilot-{seed}.json").read_bytes()
        v=json.loads(raw)
        check(v.get("mode")=="pilot" and v.get("B_scored") is False and
              v.get("source_lock")==lock and v["case"]["seed"]==seed,"PILOT_ENVELOPE")
        c=v["case"]
        check(c["source_rows"]==144 and c["held_composite_cases"]==48 and
              c["old_primitive_retention_exact"] is True and
              c["cold_restore_exact"] is True and
              c["local_quarantine_exact"] is True, "WITNESS_RETENTION")
        check(set(c["metrics"])=={
            "native_original","native_sparse_repair","polynomial_logistic",
            "smoothed_frequency","exact_2880_bayes","uninformative_sham"
        } and all(x["cases"]==48 for x in c["metrics"].values()), "ARM_BUDGET")
        got=report["receipts"][str(seed)]
        expected={
            "raw_sha256":hashlib.sha256(raw).hexdigest(),
            "native_brier":c["metrics"]["native_original"]["brier"],
            "candidate_brier":c["metrics"]["native_sparse_repair"]["brier"],
            "original_coverage":c["coverage"]["native_original"],
            "candidate_coverage":c["coverage"]["native_sparse_repair"],
            "solver_attempts":c["candidate_repair_attempts"],
            "solver_eligible":c["candidate_repairs_eligible"],
        }
        check(got==expected, "RECEIPT_MATCH")
        cases.append(c)
    progress=any(
        c["metrics"]["native_original"]["brier"] -
        c["metrics"]["native_sparse_repair"]["brier"] >= .03
        and c["coverage"]["native_sparse_repair"] -
        c["coverage"]["native_original"] >= .20
        for c in cases)
    check(report["screen_go"] is progress, "FROZEN_THRESHOLDS")
    check(report["classification"]==("PILOT_GO_TO_SEPARATE_B_GATE" if progress
                                   else "SCREEN_NO_GO"), "CLASSIFICATION")
    cert=HERE/"pilot_certificate.json"
    if progress:
        check(cert.is_file(), "CERT_MISSING")
        d=json.loads(cert.read_bytes())
        check(d["schema"]=="yggdrasil.ckad30.pilot-certificate.v1" and
              d["pilot_seeds"]==[9101,9102] and
              d["source_lock_sha256"]==hashlib.sha256(lock_raw).hexdigest() and
              d["screen_go"] is True and d["primary_scored"] is False and
              d["pilot_receipt_sha256"]=={
                str(s):hashlib.sha256((HERE/f"pilot-{s}.json").read_bytes()).hexdigest()
                for s in (9101,9102)}, "CERT_VALIDITY")
    else:
        check(not cert.exists(), "CERT_FORBIDDEN_ON_NEGATIVE")
    print(json.dumps({"schema":"yggdrasil.ckad30.pilot-audit.v1",
                      "status":"PASS","primary_scored":False,
                      "screen_go":progress,"seeds":2,"source_rows":288,
                      "held_pilot_cases":96},sort_keys=True))


if __name__=="__main__":
    main()
