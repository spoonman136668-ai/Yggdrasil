"""One-shot CKAD40 two-seed DEV screen; no pilot or primary first use."""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ckad40_diagnostic", HERE / "diagnostic.py")
D = importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)


def main():
    cases = [D.case(seed) for seed in D.DEV]  # each disjoint DEV seed once
    decision = D.classify(cases)
    if decision == "INVALID_SOURCE":
        raise AssertionError("CKAD40_NATIVE_SOURCE_INTEGRITY_FAILURE")
    result = {
        "schema":"yggdrasil.ckad40.dev-screen.v1",
        "prereg_commit":D.PREREG,
        "source_parent":"feef03a15ec68a8e3da073e9d78d197acf656ea8",
        "decision":decision,
        "science_pass":False,
        "pilot_scored":False,
        "primary_scored":False,
        "consumed_dev_seeds":list(D.DEV),
        "reserved_untouched":list(D.RESERVED),
        "source_integrity":True,
        "cases":cases,
        "interpretation":{
            "ARCHIVE_COVERAGE_GAP":"No sufficient distinct old/new native source blocks were available by prediction time",
            "IDENTIFICATION_GAP":"Both archived source classes exist, but recent observed evidence does not classify the hidden phases reliably",
            "REPRESENTATION_GAP":"Evaluator-only correct source labels do not make native archive forecasts sufficiently strong against fitted controls",
            "DIAGNOSTIC_POTENTIAL":"Necessary development ceiling conditions met; not a deployable retrieval mechanism or scientific pass"
        }[decision],
        "frozen_thresholds":{
            "min_coverage_fraction_per_seed":.50,
            "min_late_covered_per_seed":64,
            "min_prior_evidence_accuracy_per_seed":.65,
            "min_oracle_gain_vs_native_brier":.015,
            "min_oracle_gain_vs_strongest_conventional_brier":.015
        },
        "limits":"Read-only development diagnostic only. Phase grouping and oracle ceiling use private evaluator labels; cannot be served to a real native learner. No held or unfamiliar-world scientific qualification."
    }
    print("CKAD40_DEV_REPORT=" + json.dumps(result, sort_keys=True, separators=(",",":")))
    return result


if __name__ == "__main__":
    main()
