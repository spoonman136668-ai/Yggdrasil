"""MH07 RETROSPECTIVE. Census bank-mix readouts on ORIGINAL sealed MH05 ZIPs.

No learner creation, training, action, source trial, bank mutation or protected use.
256 per-cell masks are evaluator-only: never claim the native model chose them.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import zipfile

from research import mh03_checkpoint_bank_readback as bank

PARENT = "778478247077b92611e099540ae320380832566f"
PREREG = "b1aa2e681b0a0d8f9dc5f5dcaa4bc84881449d98"
TRIAL = "MH05-SYNTH-HI-503-509-521-523-541-20261120"
EXPECTED = {
    "ubuntu": ("6a20b90954bdfac3e6154c9f58819f0a62d4c02b7c95de98bb29f5f44ddc5e32",
               14677697635),
    "windows": ("31bc7889bc94edbf259bbf5385e2e1593ada84b07b602fe86b3c2716fb147a4a",
                14676898689),
}
SEEDS = (503, 509, 521, 523, 541)
MAPS = {"H": (0, 2, 1, 0), "I": (2, 0, 0, 0)}
OLD = (0, 1, 2, 1)
EPS = 1e-10


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def load_archive(path: Path, platform: str) -> dict:
    if platform not in EXPECTED:
        raise ValueError("MH07_UNKNOWN_PLATFORM")
    data = path.read_bytes()
    if digest(data) != EXPECTED[platform][0]:
        raise ValueError("MH07_ORIGINAL_ARTIFACT_SHA_MISMATCH")
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if names != ["mh05-report.json"]:
            raise ValueError("MH07_ORIGINAL_ARTIFACT_LAYOUT")
        meta = archive.getinfo(names[0])
        if not 1000 <= meta.file_size <= 250000:
            raise ValueError("MH07_ORIGINAL_REPORT_SIZE")
        payload = json.loads(archive.read(names[0]))
    if (payload.get("trial_id") != TRIAL or payload.get("seed_set") != list(SEEDS)
            or payload.get("mappings") != {k: list(v) for k, v in MAPS.items()}
            or payload.get("scientific_gain_verified") is not False
            or payload.get("protected_original_source_first_use") is not False
            or payload.get("native_rust_changed") is not False
            or payload.get("summary", {}).get("storage_class") !=
                "MH05_DEV_STORAGE_RETAINED"
            or payload.get("summary", {}).get("cost_class") !=
                "MH05_DEV_COST_NO_GO"):
        raise ValueError("MH07_ORIGINAL_TRIAL_CONTRACT_DRIFT")
    if (payload.get("original_rust_source_sha256") !=
            digest(bank.SOURCE.read_bytes())
            or bank.SOURCE_BLOB != "85237dcc82905e05a273b11023b5be5db722726e"):
        raise ValueError("MH07_FROZEN_NATIVE_SOURCE_DRIFT")
    rows = payload.get("results")
    if not isinstance(rows, list) or len(rows) != 10:
        raise ValueError("MH07_ORIGINAL_COHORT_COUNT_DRIFT")
    expected_ids = {(k, s) for k in MAPS for s in SEEDS}
    actual_ids = {(x["mapping"], x["seed"]) for x in rows}
    if actual_ids != expected_ids:
        raise ValueError("MH07_ORIGINAL_COHORT_ID_DRIFT")
    return payload


def aligned_originals(left: dict, right: dict) -> None:
    """Stage scores differ in resource clocks; full original bytes must not."""
    a = {(x["mapping"], x["seed"]): x for x in left["results"]}
    b = {(x["mapping"], x["seed"]): x for x in right["results"]}
    if a.keys() != b.keys():
        raise ValueError("MH07_CROSS_OS_COHORT_DRIFT")
    for identity in sorted(a):
        p, q = a[identity], b[identity]
        if (p["full_original_checkpoint_hex"] !=
                q["full_original_checkpoint_hex"]):
            raise ValueError("MH07_CROSS_OS_ORIGINAL_BYTES_DRIFT")
        for stage in ("a240", "x240"):
            if p["stages"][stage]["native"] != q["stages"][stage]["native"]:
                raise ValueError("MH07_CROSS_OS_ORIGINAL_SCORE_DRIFT")


def select(scores3) -> int:
    if (len(scores3) != 3 or
            any(not math.isfinite(v) for v in scores3)):
        raise ValueError("MH07_MALFORMED_ACTION_SCORE")
    ordered = sorted(scores3)
    if ordered[2] - ordered[1] <= EPS:
        raise ValueError("MH07_UNIDENTIFIABLE_TIED_POLICY")
    winner = 0
    for i in (1, 2):
        if scores3[i] > scores3[winner] + EPS:
            winner = i
    return winner


def policy(state, bits: tuple[int, ...]):
    if (len(bits) != 8 or any(type(v) is not int or v not in (0, 1)
                              for v in bits)):
        raise ValueError("MH07_INVALID_OFFLINE_MASK")
    # Construct a detached evaluator-only copy of the decoded record; never
    # change source cell storage or write a serialized checkpoint.
    copied = {**state, "cells": tuple({**cell, "active": bit}
                     for cell, bit in zip(state["cells"], bits))}
    return tuple(select(bank.scores(copied, cue)) for cue in range(4))


def verify_stage(row: dict, stage: str) -> dict:
    if stage not in ("a240", "x240"):
        raise ValueError("MH07_UNKNOWN_FROZEN_STAGE")
    raw = bytes.fromhex(row["full_original_checkpoint_hex"][stage])
    state = bank.parse_checkpoint(raw)
    if len(raw) != bank.SIZE or state["sha256"] != digest(raw):
        raise ValueError("MH07_ORIGINAL_CHECKPOINT_IDENTITY")
    identity = row["stages"][stage]["native"]
    if state["sha256"] != identity["raw_sha256"]:
        raise ValueError("MH07_ORIGINAL_STAGE_RAW_HASH_DRIFT")
    full = bank.inspect_snapshot(raw)
    for mode in ("active", "forced_bank0", "forced_bank1"):
        scores = full["readouts"][mode]
        if digest(canonical(scores)) != identity[mode]["scores_sha256"]:
            raise ValueError("MH07_ORIGINAL_STAGE_SCORE_HASH_DRIFT")
        actions = tuple(select(r) for r in scores)
        if (sum(a == b for a, b in zip(actions, OLD)) / 4.0 !=
                identity[mode]["a"] or
                sum(a == b for a, b in zip(actions, MAPS[row["mapping"]])) / 4.0 !=
                identity[mode]["x"]):
            raise ValueError("MH07_ORIGINAL_STAGE_ACCURACY_DRIFT")
    if tuple(x["active"] for x in state["cells"]) != tuple(identity["active_banks"]):
        raise ValueError("MH07_ORIGINAL_ACTIVE_VECTOR_DRIFT")
    return state


def census_one(row: dict) -> dict:
    verify_stage(row, "a240")
    source = verify_stage(row, "x240")
    old, new = OLD, MAPS[row["mapping"]]
    if any(x["active"] != 1 for x in source["cells"]):
        raise ValueError("MH07_ORIGINAL_NEW_POLICY_ACTIVE_DRIFT")
    counts = Counter()
    ordered = []
    for mask in range(256):
        result = policy(source, tuple((mask >> cell) & 1 for cell in range(8)))
        counts[result] += 1
        ordered.append(list(result))
    if (sum(counts.values()) != 256 or
            policy(source, (0,) * 8) != old or
            policy(source, (1,) * 8) != new):
        raise ValueError("MH07_SOURCE_BANK_ENDPOINT_DRIFT")
    return {
        "mapping": row["mapping"], "seed": row["seed"],
        "original_checkpoint_x240_sha256": source["sha256"],
        "unique_offline_policies": len(counts),
        "masks_output_old": counts[old],
        "masks_output_new": counts[new],
        "masks_output_neither_trained_target":
            256 - counts[old] - counts[new],
        "other_untrained_policy_count":
            len([p for p in counts if p not in (old, new)]),
        "census_sha256": digest(canonical(ordered)),
        "actual_native_selected_mask": 255,
        "evaluator_masks_only": True,
    }


def evaluate(linux_zip: Path, windows_zip: Path) -> dict:
    linux = load_archive(linux_zip, "ubuntu")
    windows = load_archive(windows_zip, "windows")
    aligned_originals(linux, windows)
    results = [census_one(row) for row in linux["results"]]
    return {
        "schema": "yggdrasil.mh07.original_checkpoint_mixed_policy_retrospective.v1",
        "trial_id": TRIAL,
        "original_single_run_id": 44833674155,
        "original_artifact_zip_digest": {key: value[0] for key, value in EXPECTED.items()},
        "frozen_rust_git_blob": bank.SOURCE_BLOB,
        "source_origin": PARENT,
        "counts": {"original_cohorts": len(results),
                   "cross_os_original_checkpoints": len(results) * 2,
                   "masks_evaluated_per_cohort": 256},
        "cohorts": results,
        "scope": "retrospective_evaluator_oracle_only",
        "native_retrieval_gain_verified": False,
        "scientific_gain_verified": False,
        "protected_original_first_use": False,
        "native_learner_modified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ubuntu-zip", type=Path, required=True)
    parser.add_argument("--windows-zip", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    receipt = evaluate(args.ubuntu_zip, args.windows_zip)
    args.output.write_bytes(canonical(receipt) + b"\n")
    print("MH07_RETROSPECTIVE_CENSUS_VALIDATED", len(receipt["cohorts"]))
    print("MH07_DISTINCT_POLICIES", [x["unique_offline_policies"]
                                    for x in receipt["cohorts"]])
    print("MH07_NON_TARGET_MASKS", [x["masks_output_neither_trained_target"]
                                    for x in receipt["cohorts"]])
    print("MH07_NO_NATIVE_RETRIEVAL_OR_SCIENCE_GAIN")


if __name__ == "__main__":
    main()
