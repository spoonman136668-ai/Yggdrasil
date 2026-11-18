"""Independent bounded pilot evidence sealer. Never reruns or reads primary cohort."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEEDS = (9101, 9102)
ARMS = ("native_original", "native_sparse_repair", "polynomial_logistic",
        "smoothed_frequency", "exact_2880_bayes", "uninformative_sham")


def verify_case(raw, seed, lock):
    obj = json.loads(raw)
    if obj.get("schema") != "yggdrasil.ckad30.two-interaction-repair.v1" or \
       obj.get("mode") != "pilot" or obj.get("B_scored") is not False or \
       obj.get("source_lock") != lock:
        raise ValueError("CKAD30_PILOT_ENVELOPE_INVALID")
    case = obj["case"]
    if case["seed"] != seed or case["source_rows"] != 144 or \
       case["held_composite_cases"] != 48:
        raise ValueError("CKAD30_PILOT_BUDGET_INVALID")
    if set(case["metrics"]) != set(ARMS):
        raise ValueError("CKAD30_PILOT_ARMS_INVALID")
    for key in ARMS:
        m = case["metrics"][key]
        if m["cases"] != 48 or not 0 <= m["brier"] <= 1 or \
           not 0 <= m["accuracy"] <= 1:
            raise ValueError("CKAD30_PILOT_METRICS_INVALID")
    cov = case["coverage"]
    if set(cov) != {"native_original", "native_sparse_repair"} or \
       any(not 0 <= x <= 1 for x in cov.values()):
        raise ValueError("CKAD30_PILOT_COVERAGE_INVALID")
    for name in ("old_primitive_retention_exact","cold_restore_exact",
                 "local_quarantine_exact"):
        if case[name] is not True:
            raise ValueError("CKAD30_PILOT_CUSTODY_FAILED")
    if len(case["solver"]) != 3 or \
       case["candidate_repair_attempts"] != sum(s["attempted"] for s in case["solver"]) or \
       case["candidate_repairs_eligible"] != sum(s["attempted"] and s["eligible"] for s in case["solver"]):
        raise ValueError("CKAD30_PILOT_SOLVER_ACCOUNTING")
    if len(case["posterior_law_counts"]) != 3 or \
       not all(1 <= count <= 2880 for count in case["posterior_law_counts"]):
        raise ValueError("CKAD30_PILOT_EXACT_CONTROL_INVALID")
    for group in ("old_checkpoint_sha256","cold_checkpoint_sha256"):
        if set(case[group]) != {"native_original", "native_sparse_repair"} or \
           not all(len(h)==64 and all(x in "0123456789abcdef" for x in h)
                   for h in case[group].values()):
            raise ValueError("CKAD30_PILOT_CHECKPOINT_PIN_INVALID")
    return case


def seal(root):
    lock_path = HERE / "source_lock.json"
    lock_raw = lock_path.read_bytes()
    lock = json.loads(lock_raw)
    pairs = []
    for seed in SEEDS:
        p = root / f"ckad30-pilot-{seed}" / "result.json"
        data = p.read_bytes()
        case = verify_case(data, seed, lock)
        pairs.append((seed, data, case))
    # Fixed gates copied from prereg, not delegated to experiment implementation.
    screen_go = any(
        c["metrics"]["native_original"]["brier"] -
        c["metrics"]["native_sparse_repair"]["brier"] >= .03
        and c["coverage"]["native_sparse_repair"] -
            c["coverage"]["native_original"] >= .20 for _,_,c in pairs)
    report = {
        "schema":"yggdrasil.ckad30.pilot-screen.v1",
        "source_lock_sha256":hashlib.sha256(lock_raw).hexdigest(),
        "pilot_seeds":list(SEEDS),
        "primary_seeds_untouched":[707,808,909],
        "primary_scored":False,
        "screen_go":screen_go,
        "classification":"PILOT_GO_TO_SEPARATE_B_GATE" if screen_go else "SCREEN_NO_GO",
        "receipts":{str(s):{"raw_sha256":hashlib.sha256(data).hexdigest(),
                             "native_brier":c["metrics"]["native_original"]["brier"],
                             "candidate_brier":c["metrics"]["native_sparse_repair"]["brier"],
                             "original_coverage":c["coverage"]["native_original"],
                             "candidate_coverage":c["coverage"]["native_sparse_repair"],
                             "solver_attempts":c["candidate_repair_attempts"],
                             "solver_eligible":c["candidate_repairs_eligible"]}
                   for s,data,c in pairs}
    }
    for seed, data, _ in pairs:
        (HERE/f"pilot-{seed}.json").write_bytes(data)
    (HERE/"pilot_screen_report.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    if screen_go:
        cert={
            "schema":"yggdrasil.ckad30.pilot-certificate.v1",
            "source_lock_sha256":hashlib.sha256(lock_raw).hexdigest(),
            "pilot_seeds":list(SEEDS),"screen_go":True,
            "pilot_receipt_sha256":{str(s):hashlib.sha256(data).hexdigest()
                                   for s,data,_ in pairs},
            "primary_scored":False
        }
        (HERE/"pilot_certificate.json").write_text(json.dumps(cert,sort_keys=True,indent=2)+"\n")
    print(json.dumps(report,sort_keys=True))
    return screen_go


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,required=True)
    a=ap.parse_args()
    seal(a.root)


if __name__=="__main__":
    main()
