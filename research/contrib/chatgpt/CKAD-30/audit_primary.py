"""Read-only CKAD30 primary evidence auditor; no generator, no held B rescore."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEEDS = (707, 808, 909)
ARMS = ("native_original", "native_sparse_repair", "polynomial_logistic",
        "smoothed_frequency", "exact_2880_bayes", "uninformative_sham")


def require(ok, code):
    if not ok:
        raise ValueError("CKAD30_PRIMARY_AUDIT_"+code)


def audit_raw(raw):
    obj = json.loads(raw)
    lock_raw = (HERE/"source_lock.json").read_bytes()
    lock = json.loads(lock_raw)
    cert = json.loads((HERE/"pilot_certificate.json").read_bytes())
    screen = json.loads((HERE/"pilot_screen_report.json").read_bytes())
    lock_sha = hashlib.sha256(lock_raw).hexdigest()
    require(obj.get("schema")=="yggdrasil.ckad30.two-interaction-repair.v1"
            and obj.get("mode")=="primary" and obj.get("B_scored") is True
            and obj.get("source_lock")==lock, "SOURCE_ENVELOPE")
    require(cert["schema"]=="yggdrasil.ckad30.pilot-certificate.v1"
            and cert["source_lock_sha256"]==lock_sha
            and cert["pilot_seeds"]==[9101,9102]
            and cert["screen_go"] is True and cert["primary_scored"] is False
            and screen["screen_go"] is True
            and screen["primary_scored"] is False, "PILOT_GATE")
    cases=obj.get("cases")
    require(type(cases) is list and tuple(c["seed"] for c in cases)==SEEDS,
            "PRIMARY_SEEDS")
    for c in cases:
        require(c["source_rows"]==144 and c["held_composite_cases"]==48
                and c["old_primitive_retention_exact"] is True
                and c["cold_restore_exact"] is True
                and c["local_quarantine_exact"] is True, "BUDGET_OR_CUSTODY")
        require(set(c["metrics"])==set(ARMS)
                and all(x["cases"]==48 and 0<=x["brier"]<=1
                        and 0<=x["accuracy"]<=1 for x in c["metrics"].values()),
                "ARM_MISMATCH")
        require(c["candidate_repair_attempts"]==sum(
                s["attempted"] for s in c["solver"]) and
                c["candidate_repairs_eligible"]==sum(
                    s["attempted"] and s["eligible"] for s in c["solver"]) and
                len(c["solver"])==3 and len(c["posterior_law_counts"])==3
                and all(1<=n<=2880 for n in c["posterior_law_counts"]),
                "SOLVER_OR_EXACT_GRAMMAR")
        require(0 <= c["coverage"]["native_original"] <= 1 and
                0 <= c["coverage"]["native_sparse_repair"] <= 1,
                "COVERAGE")
        require(c["wall_seconds"]>=0 and c["cpu_seconds"]>=0,"TIMING")
        for key in ("old_checkpoint_sha256", "cold_checkpoint_sha256"):
            require(set(c[key])=={"native_original","native_sparse_repair"} and
                    all(type(x)==str and len(x)==64 and
                        all(d in "0123456789abcdef" for d in x)
                        for x in c[key].values()), "CHECKPOINT_CUSTODY")
    means={arm:sum(c["metrics"][arm]["brier"] for c in cases)/len(cases)
           for arm in ARMS}
    strongest=min(means["polynomial_logistic"],means["smoothed_frequency"])
    n=means["native_sparse_repair"]
    per_seed=sum(
        c["metrics"]["native_sparse_repair"]["brier"] <
        min(c["metrics"]["native_original"]["brier"],
            c["metrics"]["polynomial_logistic"]["brier"],
            c["metrics"]["smoothed_frequency"]["brier"]) for c in cases)
    gains=[c["coverage"]["native_sparse_repair"] -
           c["coverage"]["native_original"] for c in cases]
    gain=sum(gains)/len(gains)
    go=(n<=means["native_original"]-.05 and n<=strongest-.05
        and n<=means["exact_2880_bayes"]+.03 and per_seed>=2
        and gain>=.30)
    mixed=(not go and n<=means["native_original"]-.02)
    decision=("DEVELOPMENT_GO" if go else
              "DEVELOPMENT_MIXED" if mixed else "DEVELOPMENT_NO_GO")
    expected={"decision":decision,
              "mean_held_brier":{k:round(v,10) for k,v in means.items()},
              "strongest_conventional_brier":round(strongest,10),
              "mean_coverage_improvement":round(gain,10),
              "seeds_beat_native_and_fitted_controls":per_seed,
              "scientific_pass":False,"accepted_native":False,"deployment":"NONE"}
    require(obj["summary"]==expected, "FROZEN_GATE_ARITHMETIC")
    return {
        "schema":"yggdrasil.ckad30.primary-audit.v1",
        "status":"PASS","primary_first_use":True,
        "primary_rerun":False,
        "primary_seeds":list(SEEDS),
        "revealed_source_rows":sum(c["source_rows"] for c in cases),
        "held_composite_cases":sum(c["held_composite_cases"] for c in cases),
        "source_lock_sha256":lock_sha,
        "original_result_sha256":hashlib.sha256(raw).hexdigest(),
        "classification":decision,"mean_held_brier":expected["mean_held_brier"],
        "per_seed_native_and_fitted_wins":per_seed,
        "mean_coverage_improvement":expected["mean_coverage_improvement"],
        "scientific_pass":False,"accepted_native":False,"deployment":"NONE",
    }


def main():
    raw=(HERE/"primary_result.json").read_bytes()
    report=audit_raw(raw)
    sealed=json.loads((HERE/"primary_audit.json").read_bytes())
    require(sealed==report, "SEALED_AUDIT_IDENTITY")
    print(json.dumps(report,sort_keys=True))


if __name__=="__main__":
    main()
