#!/usr/bin/env python3
"""GKD-06 — corrected published ZIP member names; no changes to GKD-05 control science.

Preregistration FIRST: 35cc14449fc1acd28ebb7bc16f8638cb9b7477d3.
Existing GKD-05 prereg, original attempt and code remain immutable.
Run --selftest (offline) or --score-public (one-shot exact commit Linux only).
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import sys
import time

DIR = pathlib.Path(__file__).resolve().parent
GKD05 = DIR.parent / "GKD-05"
assert GKD05.is_dir()

# Lock upstream source model/control implementations, not just the copied numeric claims.
# Verify bytes in a cross-platform-safe way (GitHub Windows may check out CRLF).
SOURCE_BLOBS = {
    "admit.py": "7f95b1ad1244b43884cdfa5b473d979456843016",
    "score.py": "b5cae9715859b9406b65d889e640686378581573",
}
def guard(ok: bool, why: str):
    if not ok:
        raise ValueError("GKD06_FAIL_CLOSED:" + why)

def git_blob_sha(path: pathlib.Path) -> str:
    b = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()

for n,sha in SOURCE_BLOBS.items():
    guard(git_blob_sha(GKD05 / n) == sha, "UPSTREAM_GKD05_DRIFT:" + n)

sys.path.insert(0, str(GKD05))
import admit as a
guard(a.SOURCE_MD5 == "d50ccd7f88bb3705bcf6eda3978bcc41",
      "PINNED_ARCHIVE_MD5")
guard(a.FIT == ("cd3cd28.csv", "cd3cd28icam2.csv", "cd3cd28_g0076.csv",
                "cd3cd28_psitect.csv", "pma.csv")
      and a.REQUIRED[-1] == "Ground_Truth.csv",
      "UPSTREAM_ORIGINAL_MANIFEST")

# Prospectively frozen *only* corrections from the public Zenodo ZIP's own
# metadata preview; no numerical values or model rules consulted.
a.FIT = ("cd3cd28.csv", "cd3cd28_icam2.csv", "cd3cd28_g0076.csv",
         "cd3cd28_psitect.csv", "pma.csv")
a.REQUIRED = a.FIT + a.VALID + a.DEV + a.SIM + ("GroundTruth.csv",)

import score as s
guard(s.FIT == a.FIT and s.VALID == a.VALID and s.DEV == a.DEV
      and s.PARENTS == {"Erk": ("Raf", "Mek"),
                        "Akt": ("PIP3", "Erk"),
                        "P38": ("PKC", "Plcg"),
                        "Jnk": ("PKC", "Plcg")}
      and s.ALPHAS == (.001, .1, 1., 10., 100., 1000.),
      "UPSTREAM_FROZEN_EXPERIMENT")

def selftest():
    a.selftest()
    s.selftest()
    guard(len(a.FIT) == 5 and len(a.VALID) == 2 and len(a.DEV) == 2
          and a.REQUIRED[-1] == "GroundTruth.csv"
          and "cd3cd28_icam2.csv" in a.REQUIRED
          and "cd3cd28icam2.csv" not in a.REQUIRED,
          "CORRECTED_SOURCE_MANIFEST")
    print("GKD06_SOURCE_ONLY_FROZEN_CONTROLS_PASS")

def score_public():
    started = time.perf_counter()
    raw = a.fetch_bounded()
    # Admission opens only CSV headers and counts, not numerical measurements.
    admission = a.admit_archive(raw)
    guard(admission["original_published_experiment_count"] == 9
          and admission["simulated_experiment_count_excluded"] == 5
          and admission["archive_md5"] == a.SOURCE_MD5,
          "PINNED_PUBLISHED_SOURCE")
    # First and only numeric source scoring under the GKD-06 prereg.
    source = s.read_source(raw)
    result = s.evaluate(source)
    guard(result["experiment_id"] == "GKD-05"
          and result["preregistration_commit"] ==
          "aafab21d6b8997ffafd355de528c9eb1cd7dfa0a",
          "FROZEN_COMPARATOR_REUSE")
    result["experiment_id"] = "GKD-06"
    result["schema"] = "yggdrasil.gkd06.public-real-condition-dev.v1"
    result["preregistration_commit"] = "35cc14449fc1acd28ebb7bc16f8638cb9b7477d3"
    result["previous_experiment"] = {
        "id": "GKD-05", "status": "SOURCE_PACKAGING_NO_GO",
        "numeric_labels_read": False, "dev_score": None,
        "original_run": 44825472870
    }
    result["source_manifest_correction"] = {
        "fit_filename": "cd3cd28_icam2.csv",
        "ground_truth_filename_excluded": "GroundTruth.csv",
        "original_protocol_unchanged": True
    }
    result["scientific_gain_verified"] = False
    result["scientific_pass"] = False
    result["elapsed_s"] = round(time.perf_counter() - started, 6)
    print("GKD06_PUBLIC_DEV_RESULT=" + json.dumps(result, sort_keys=True,
          separators=(",", ":"), allow_nan=False))
    print("GKD06_PUBLIC_SCORE_CONSUMED_NO_REPLAY")

def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--selftest", action="store_true")
    mode.add_argument("--score-public", action="store_true")
    options = parser.parse_args()
    if options.selftest:
        selftest()
    else:
        score_public()

if __name__ == "__main__":
    main()
