"""CKAD33 independent read-only pilot receipt audit, scientific and engineering gate.

Never imports or executes the frozen generator, native model, or hidden
evaluator. All original observations are preserved in Git, not regenerated.
"""
import argparse
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
SEEDS=(13531,13532)
INCLASS={"compiled_native","native_original","native_sparse","gf2_conventional",
         "exact_2880_bayes","polynomial_logistic","smoothed_frequency","sham"}
OOD={"compiled_native","uncalibrated_native","native_original","gf2_conventional",
     "gf2_degree3","sham"}
SHA_KEYS={"before_pressure_sha256","after_pressure_sha256"}


def check(value,name):
    if not value:
        raise ValueError("CKAD33_EVIDENCE_FAIL_CLOSED_"+name)


def audit_case(raw,seed,lock):
    obj=json.loads(raw)
    check(obj.get("schema")=="yggdrasil.ckad33.native-compilation.v1"
          and obj.get("mode")=="pilot" and obj.get("seed")==seed
          and obj.get("primary_scored") is False
          and obj.get("source_lock")==lock,"ENVELOPE")
    c=obj["case"]
    check(c["seed"]==seed and c["source_rows"]==216
          and c["inclass_source_rows"]==60
          and c["ood_source_rows"]==60
          and c["pressure_source_rows"]==96
          and c["held_cases_each_family"]==36,"SOURCE_BUDGET")
    fit,cal,held=(c["fit_input_indices"],c["calibration_input_indices"],
                  c["held_input_indices"])
    check(len(fit)==16 and len(cal)==4 and len(held)==12 and
          len(set(fit+cal+held))==32 and
          all(type(x) is int and 0<=x<32 for x in fit+cal+held),"SOURCE_DISJOINT")
    check(set(c["metrics"])=={"quadratic","cubic_shift"} and
          set(c["metrics"]["quadratic"])==INCLASS and
          set(c["metrics"]["cubic_shift"])==OOD and
          all(v["cases"]==36 and 0<=v["brier"]<=1
              for outcomes in c["metrics"].values()
              for v in outcomes.values()),"HELD_SCORES")
    check(set(c["calibration_pass"])=={str(i) for i in range(6)}
          and all(type(v) is bool for v in c["calibration_pass"].values()),
          "CALIBRATION_BOOLEAN")
    check(all(c["calibration_pass"][str(i)] for i in range(3)),
          "INCLASS_CALIBRATION_FAIL")
    check(set(c["coverage"])=={"quadratic","cubic_shift"}
          and all(0<=n<=1 for m in c["coverage"].values() for n in m.values()),
          "COVERAGE_BOUNDS")
    check(set(c["confident_wrong"])=={"quadratic","cubic_shift"}
          and all(type(n) is int and 0<=n<=36
                  for m in c["confident_wrong"].values() for n in m.values()),
          "CONFIDENT_BOUNDS")
    check(all(type(n) is int and 1<=n<=2880 for n in c["exact_bayes_rule_counts"])
          and len(c["exact_bayes_rule_counts"])==3,"EXACT_GRAMMAR")
    check(len(c["degree3_source_ranks"])==3
          and all(1<=n<=20 for n in c["degree3_source_ranks"]),"DEGREE3_CONTROL")
    model=c["native_compiler"]
    check(model["cold_restore_exact"] is True
          and model["retention_exact_all_32_inputs"] is True
          and model["conflict_rejection_atomic"] is True
          and model["pressure_slot_count"]==6
          and model["before_bytes"]>0 and model["after_bytes"]>0
          and len(model["slot_profiles"])==6,"NATIVE_MEMORY")
    check(all(p["degree"]==2 and p["rank"]==16 and p["source_records"]==16
              for p in model["slot_profiles"].values()),"NUMERIC_NATIVE_RANK")
    check(c["baseline_native"]["baseline_cold_and_retention_exact"] is True
          and len(c["sparse_solver"])==3,"MATCHED_NATIVE_CONTROL")
    for key in SHA_KEYS:
        h=model[key]
        check(type(h) is str and len(h)==64
              and all(ch in "0123456789abcdef" for ch in h),"NATIVE_PIN")
    check(c["wall_seconds"]>=0 and c["cpu_seconds"]>=0,"COST")
    # Mathematical parity is expected: both use declared degree-2 GF(2) class.
    check(c["metrics"]["quadratic"]["compiled_native"]["brier"]
          ==c["metrics"]["quadratic"]["gf2_conventional"]["brier"],
          "CONVENTIONAL_PARITY")
    check(c["metrics"]["cubic_shift"]["compiled_native"]["brier"]
          ==c["metrics"]["cubic_shift"]["gf2_conventional"]["brier"],
          "CONVENTIONAL_OOD_PARITY")
    return c


def qualify(cases):
    check(tuple(c["seed"] for c in cases)==SEEDS,"PILOT_ORDER")
    def eligible(c):
        q=c["metrics"]["quadratic"]
        o=c["metrics"]["cubic_shift"]
        m=q["compiled_native"]["brier"]
        return (
            m<=.01 and m<=q["native_original"]["brier"]-.10
            and m==q["gf2_conventional"]["brier"]
            and c["coverage"]["quadratic"]["compiled_native"]>=.95
            and o["compiled_native"]["brier"]<=o["uncalibrated_native"]["brier"]
            and c["confident_wrong"]["cubic_shift"]["compiled_native"]==0
            and sum(c["calibration_pass"][str(s)] is False for s in (3,4,5))>=2
        )
    good=all(eligible(c) for c in cases)
    return ("ENGINEERING_FEASIBLE" if good else "SCREEN_NO_GO"),good


def expected_report(pairs,lock_raw):
    decision,go=qualify([c for _,_,c in pairs])
    return {
        "schema":"yggdrasil.ckad33.pilot-screen.v1",
        "decision":decision,"engineering_feasible":go,
        "scientific_pass":False,
        "conventional_superiority":False,
        "pilot_seeds":list(SEEDS),
        "primary_seeds_untouched":[23531,23532,23533],
        "primary_scored":False,
        "source_lock_sha256":hashlib.sha256(lock_raw).hexdigest(),
        "pilot_receipt_sha256":{str(s):hashlib.sha256(raw).hexdigest()
                                for s,raw,_ in pairs},
        "metrics":{str(c["seed"]):{
            "native_compiled_brier":c["metrics"]["quadratic"]["compiled_native"]["brier"],
            "native_original_brier":c["metrics"]["quadratic"]["native_original"]["brier"],
            "conventional_gf2_brier":c["metrics"]["quadratic"]["gf2_conventional"]["brier"],
            "exact_bayes_brier":c["metrics"]["quadratic"]["exact_2880_bayes"]["brier"],
            "compiled_inclass_coverage":c["coverage"]["quadratic"]["compiled_native"],
            "ood_rejected_count":sum(c["calibration_pass"][str(i)] is False for i in (3,4,5)),
            "ood_gated_brier":c["metrics"]["cubic_shift"]["compiled_native"]["brier"],
            "ood_naive_brier":c["metrics"]["cubic_shift"]["uncalibrated_native"]["brier"],
            "ood_gated_wrong_confident":c["confident_wrong"]["cubic_shift"]["compiled_native"],
            "cpu_seconds":c["cpu_seconds"],"wall_seconds":c["wall_seconds"],
        } for _,_,c in pairs}
    }


def audit():
    lock_raw=(HERE/"source_lock.json").read_bytes()
    lock=json.loads(lock_raw)
    pair=[]
    for seed in SEEDS:
        raw=(HERE/f"pilot-{seed}.json").read_bytes()
        pair.append((seed,raw,audit_case(raw,seed,lock)))
    report=json.loads((HERE/"pilot_screen_report.json").read_bytes())
    check(report==expected_report(pair,lock_raw),"REPORT_IDENTITY")
    check(not (HERE/"pilot_certificate.json").exists(),"NO_PRIMARY_AUTOMATION")
    return report


def seal(root):
    lock_raw=(HERE/"source_lock.json").read_bytes()
    lock=json.loads(lock_raw)
    pair=[]
    for seed in SEEDS:
        raw=(root/f"ckad33-pilot-{seed}"/"result.json").read_bytes()
        pair.append((seed,raw,audit_case(raw,seed,lock)))
    report=expected_report(pair,lock_raw)
    for seed,raw,_ in pair:
        (HERE/f"pilot-{seed}.json").write_bytes(raw)
    (HERE/"pilot_screen_report.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    check(audit()==report,"INDEPENDENT_DISAGREEMENT")
    print(json.dumps(report,sort_keys=True))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path)
    args=ap.parse_args()
    if args.root is None:
        print(json.dumps(audit(),sort_keys=True))
    else:
        seal(args.root)


if __name__=="__main__":
    main()
