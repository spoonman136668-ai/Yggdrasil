"""Metadata-only deterministic cohort split for Norman GSE133344.

Only usable after exact original source_admission.verify PASS. No expression
values, class labels, guide names, or cell identifiers appear in output.
Author format: guide_identity -> split('__')[0] -> split('_'); NegCtrlN
identifies the control gene. Source-free tests are engineering only.
"""
from __future__ import annotations

from collections import Counter
import csv
import gzip
import hashlib
import json
import re
from pathlib import Path

from source_admission import AdmissionError, verify, digest_file, FILE_SPEC

SCHEMA = "yggdrasil.wsp191.pair-metadata-split.v1"
SALT = b"WSP191-NORMAN-GSE133344-PAIR-SPLIT-v1"
GENE = re.compile(r"[A-Za-z0-9.\-]{1,64}\Z")
CONTROL = re.compile(r"NegCtrl[0-9]+\Z")
MIN_SPLIT = {"FIT": 40, "VALID": 8, "DEV": 8}


def parse_assignment(raw: str) -> tuple[str, tuple[str, ...]]:
    """Parse author-defined raw guide_identity, never infer from phenotype."""
    if not raw or raw == "*":
        return "UNASSIGNED", ()
    prefix = raw.split("__", 1)[0]
    parts = prefix.split("_")
    if len(parts) != 2 or any(not GENE.fullmatch(p) for p in parts):
        raise AdmissionError("UNSUPPORTED_GUIDE_IDENTITY_FORMAT")
    # An explicit correction in the original author GI_generate_populations notebook.
    parts = ["RHOXF2B" if x == "RHOXF2" else x for x in parts]
    active = tuple(sorted(p for p in parts if not CONTROL.fullmatch(p)))
    if len(active) == 2 and active[0] == active[1]:
        raise AdmissionError("SELF_PAIR_NOT_NEW_TARGET")
    kind = {0: "CONTROL", 1: "SINGLE", 2: "PAIR"}[len(active)]
    return kind, active


def split_pair(pair: tuple[str, str]) -> str:
    if len(pair) != 2 or tuple(sorted(pair)) != pair:
        raise AdmissionError("INVALID_CANONICAL_PAIR")
    h = hashlib.sha256(SALT + b"\x00" + pair[0].encode() + b"\x00" + pair[1].encode()).digest()
    v = int.from_bytes(h[:8], "big") % 100
    return "FIT" if v < 70 else "VALID" if v < 85 else "DEV"


def summarize_eligible(pairs: set[tuple[str, str]], singles: set[str]) -> dict:
    eligible = sorted(pair for pair in pairs if set(pair).issubset(singles))
    excluded = len(pairs) - len(eligible)
    buckets = Counter(split_pair(pair) for pair in eligible)
    for name, needed in MIN_SPLIT.items():
        if buckets[name] < needed:
            raise AdmissionError("INSUFFICIENT_DISJOINT_" + name + "_PAIRS")
    joined = "\n".join("\x00".join(p) for p in eligible).encode("utf-8")
    return {"eligible_pair_groups": len(eligible), "missing_single_parent_groups": excluded,
            "group_counts": {k: buckets[k] for k in ("FIT", "VALID", "DEV")},
            "canonical_pair_roster_sha256": hashlib.sha256(joined).hexdigest(),
            "raw_labels_emitted": False, "split_assignment_formula": "SHA256(salt,NUL,sorted_pair)[0:8] mod 100; <70 FIT; <85 VALID; else DEV"}


def analyze(root: Path) -> dict:
    custody = verify(root)
    if custody["byte_digest_and_metadata_shape_gate"] != "PASS" or not custody["identity_to_barcode_join_verified"]:
        raise AdmissionError("SOURCE_NOT_BYTE_ADMITTED")
    filename = root / "GSE133344_filtered_cell_identities.csv.gz"
    singles: set[str] = set()
    pairs: set[tuple[str, str]] = set()
    counts: Counter[str] = Counter()
    expected_rows = custody["files"][filename.name]["metadata_rows"]
    with gzip.open(filename, "rt", newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or "guide_identity" not in reader.fieldnames:
            raise AdmissionError("IDENTITY_GUIDE_KEY_MISSING")
        for row in reader:
            if sum(counts.values()) >= expected_rows or not row or None in row or any(v is None for v in row.values()):
                raise AdmissionError("IDENTITY_METADATA_DRIFT_OR_INVALID_ROW")
            kind, active = parse_assignment(row["guide_identity"])
            counts[kind] += 1
            if kind == "SINGLE":
                singles.add(active[0])
            if kind == "PAIR":
                pairs.add((active[0], active[1]))
    if sum(counts.values()) != expected_rows:
        raise AdmissionError("IDENTITY_METADATA_ROW_COUNT_DRIFT")
    recorded = custody["files"][filename.name]
    rechk = digest_file(filename, *FILE_SPEC[filename.name])
    if rechk["sha256"] != recorded["sha256"]:
        raise AdmissionError("IDENTITY_BYTES_DRIFT_AFTER_SOURCE_GATE")
    group = summarize_eligible(pairs, singles)
    return {"schema": SCHEMA, "source_gate": "PASS", "cohort_metadata_gate": "PASS",
            "pair_split": group, "observed_cell_count_by_kind": {k: counts[k] for k in ("CONTROL", "SINGLE", "PAIR", "UNASSIGNED")},
            "single_parent_groups": len(singles), "pair_groups": len(pairs),
            "source_fingerprint_sha256": hashlib.sha256(json.dumps(custody["files"], sort_keys=True).encode()).hexdigest(),
            "numeric_expression_values_read": False, "test_pair_labels_exposed": False,
            "protection_first_use_allowed": False, "scientific_pass": False,
            "experiment_executed": False}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(analyze(args.root), sort_keys=True))
    except (AdmissionError, OSError, EOFError, ValueError) as exc:
        print(json.dumps({"schema": SCHEMA, "cohort_metadata_gate": "FAIL", "reason": str(exc),
                          "experiment_executed": False}, sort_keys=True))
        raise SystemExit(2) from None
