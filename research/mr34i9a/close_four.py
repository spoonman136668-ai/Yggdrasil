"""MR34I9B independent all-four-worker evidence retention and closure.

Never filter unfavorable workers. A negative result is a valid scientific
engineering-kernel closure, not a reason to rerun or alter frozen thresholds.
"""
import json
import os
from pathlib import Path
import sys

COHORT_COUNTS = {
    "canonical_frozen_boundaries": 42,
    "canonical_seeded_binary64_inputs": 128,
    "FaramaMiniGridDoorKey8": 160,
    "DeepMindPycolabApprehend": 160,
}
LABELS = ["ubuntu-latest-1", "ubuntu-latest-2",
          "windows-latest-1", "windows-latest-2"]
PINS = {
    "s4c1": "8e1561eb1a542e21307bac669c42435cf48e59bd",
    "farama": "7f5853792ea7f04f75614661006d87fcf949f26d",
    "pycolab": "6504c8065dd5322438f23a2a9026649904f3322a",
    "cr_exp_mirror": "196e71ff8f00ab9df0802f3661cbe845ff8e118c",
}


def close(folder, out):
    receipts = {}
    for label in LABELS:
        path = Path(folder) / ("mr34i9b-" + label) / "receipt.json"
        if not path.is_file():
            raise ValueError("MR34I9B_FOUR_WORKER_EVIDENCE_INCOMPLETE")
        item = json.loads(path.read_text(encoding="utf-8"))
        if (item["schema"] != "yggdrasil.mr34i9b.compiled_eightwide_development_only.v1"
            or item["original_source_pins"] != PINS
            or item["source_sha"] !=
                os.environ["GITHUB_SHA"]
            or item["scientific_first_use"] is not False
            or item["training_performed"] is not False
            or item["original_learner_modified"] is not False
            or item["cognitive_transfer"] != "NOT_TESTED"
            or {name: row["n"] for name, row in item["cohorts"].items()} != COHORT_COUNTS
            or len(item["measurements"]["paired_abba_rounds"]) != 5
            or item["G29_project_regression"] != "NOT_RUN"):
            raise ValueError("MR34I9B_FROZEN_RECEIPT_IDENTITY_OR_SCOPE_DRIFT")
        receipts[label] = item
    first = receipts[LABELS[0]]["cohorts"]
    input_match = all(
        all(item["cohorts"][k]["original_frozen_training_input_sha256"] ==
            first[k]["original_frozen_training_input_sha256"] for k in COHORT_COUNTS)
        for item in receipts.values())
    cross_os = all(
        all(item["cohorts"][k]["candidate_binary64_sha256"] ==
            first[k]["candidate_binary64_sha256"] for k in COHORT_COUNTS)
        for item in receipts.values())
    # A checksum is a gate on equal bytes within the frozen data; it is
    # not a substitute for genuine independent first-use provenance.
    no_cpu_regression = all(
        item["measurements"]["cpu_nonregression"] is True
        for item in receipts.values())
    no_rss_regression = all(
        item["measurements"]["rss_nonregression"] is True
        for item in receipts.values())
    within_1ulp = all(
        item["numeric_precision_pass"] is True
        for item in receipts.values())
    if not input_match:
        raise ValueError("MR34I9B_HISTORICAL_TRAINING_INPUT_IDENTITY_DRIFT")
    if not cross_os:
        decision = "NUMERIC_CROSS_OS_NO_GO"
    elif not within_1ulp:
        decision = "NUMERIC_PRECISION_NO_GO"
    elif not no_cpu_regression or not no_rss_regression:
        decision = "RESOURCE_NO_GO"
    else:
        decision = "ENGINEERING_KERNEL_GO_ONLY"
    report = {
        "schema": "yggdrasil.mr34i9b.four_worker_frozen_closure.v1",
        "verdict": decision,
        "all_four_workers_retained": LABELS,
        "independent_source_input_identity_pass": input_match,
        "candidate_binary64_cross_os_equal": cross_os,
        "candidate_max_ulp_lte_one_all": within_1ulp,
        "cpu_nonregression_all": no_cpu_regression,
        "memory_nonregression_all": no_rss_regression,
        "per_worker_verdict": {k: v["verdict"] for k, v in receipts.items()},
        "per_worker_cpu_ns_per_call": {k: v["measurements"]["median_cpu_ns_per_eightwide"]
                                      for k, v in receipts.items()},
        "per_worker_peak_resident_bytes": {k: v["measurements"]["peak_rss_bytes"]
                                           for k, v in receipts.items()},
        "full_learner_training": "NOT_RUN",
        "transfer_claim": "PROHIBITED",
        "independent_first_use": "NOT_CONSUMED",
        "G29_project_regression": "NOT_RUN",
        "next_gate": ("SEPARATE_MR34I10_PREREG_REQUIRED" if decision ==
                      "ENGINEERING_KERNEL_GO_ONLY" else
                      "CLOSE_HIGH_PRECISION_KERNEL_SEARCH_PRESERVE_NEGATIVE"),
    }
    Path(out).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                         encoding="utf-8")
    print("MR34I9B_FROZEN_FOUR_WORKER_DISPOSITION=" + decision)
    print("MR34I9B_FOUR_INDEPENDENT_RECEIPTS_RETAINED=TRUE")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: close_four.py ALL_ARTIFACTS REPORT")
    close(sys.argv[1], sys.argv[2])
