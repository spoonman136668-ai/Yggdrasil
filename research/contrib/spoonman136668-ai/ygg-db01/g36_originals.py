"""G36: verify original *receipt* bytes, never adjudicate science/custody.

Only reads bounded local metadata receipts (no withheld task labels). An
untrusted manifest cannot authenticate independent custody, even if its hashes
match. This module never executes inference, training or protected first-use.
"""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import re

SLOTS = (
    "task_manifest", "task_source_attestation", "evaluator_manifest",
    "fit_cohort_commitment", "transfer_cohort_commitment",
    "custodian_attestation", "frozen_thresholds_receipt",
    "prediction_seal_receipt", "label_release_receipt",
)
DIGEST = re.compile(r"[a-f0-9]{64}\Z")
PINNED_SOURCE = re.compile(
    r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/"
    r"(?:blob|commit)/[a-f0-9]{40}(?:/[^?#]*)?\Z"
)
MISSING_STATUS = "MISSING_ORIGINAL_RECEIPTS"
HASHED_STATUS = "HASHES_MATCH_AUTHENTICITY_UNVERIFIED"


def _reject(reason):
    raise ValueError("YGG_G36_FAIL_CLOSED: " + reason)


def _when(value):
    if type(value) is not str or not value.endswith("Z"):
        _reject("timestamp must be exact UTC string")
    try:
        result = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        _reject("invalid timestamp")
    if result.tzinfo != timezone.utc:
        _reject("non-UTC timestamp")
    return result


def inspect(index, root):
    """Inspect original metadata receipts only. Always deny primary execution."""
    if type(index) is not dict or set(index) != {
            "schema", "status", "g35_candidate_sha256",
            "authority", "records", "provenance_note"}:
        _reject("index schema")
    if (index["schema"] != "yggdrasil.db01.g36-original-receipts.v1" or
            index["status"] != "ORIGINALS_NOT_PROVIDED" or
            index["provenance_note"] !=
            "No original external receipts were supplied; no identity or independent custody accepted."):
        _reject("status/provenance")
    authority = index["authority"]
    if type(authority) is not dict or set(authority) != {
            "primary_execution_allowed", "scientific_acceptance_allowed",
            "protected_first_use_allowed", "accepted_ref_mutation"} or any(
            type(v) is not bool or v for v in authority.values()):
        _reject("authority cannot elevate")
    records = index["records"]
    if type(records) is not dict or set(records) != set(SLOTS):
        _reject("missing/extra receipt slot")
    project_root = Path(root).resolve()
    # The G35 plan must be the exact file under the same checked-out source.
    candidate = project_root / "g35_candidate.json"
    if not candidate.is_file() or candidate.is_symlink():
        _reject("G35 plan unavailable")
    plan_hash = hashlib.sha256(candidate.read_bytes()).hexdigest()
    pinned_plan = index["g35_candidate_sha256"]
    if pinned_plan is not None and (
            type(pinned_plan) is not str or not DIGEST.fullmatch(pinned_plan) or
            pinned_plan != plan_hash):
        _reject("G35 plan hash mismatch")
    if not isinstance(project_root, Path):
        _reject("root")
    missing = [name for name in SLOTS if records[name] is None]
    verified = []
    times = {}
    seen = set()
    for slot in SLOTS:
        record = records[slot]
        if record is None:
            continue
        if type(record) is not dict or set(record) != {
                "path", "sha256", "original_ref", "actor", "recorded_at_utc"}:
            _reject("receipt schema: " + slot)
        if (record["path"] != "originals/" + slot + ".json" or
                type(record["sha256"]) is not str or
                not DIGEST.fullmatch(record["sha256"]) or
                type(record["original_ref"]) is not str or
                not PINNED_SOURCE.fullmatch(record["original_ref"]) or
                type(record["actor"]) is not str or
                not 3 <= len(record["actor"]) <= 128 or
                record["actor"].strip() != record["actor"]):
            _reject("unbound original file/source reference: " + slot)
        observed = _when(record["recorded_at_utc"])
        file_path = project_root / record["path"]
        if (file_path in seen or file_path.is_symlink() or
                not file_path.is_file() or
                file_path.resolve().parent != (project_root / "originals").resolve()):
            _reject("missing, duplicate or escaping original file: " + slot)
        seen.add(file_path)
        if file_path.stat().st_size > 1024 * 1024:
            _reject("unbounded receipt file: " + slot)
        digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
        if digest != record["sha256"]:
            _reject("original byte hash mismatch: " + slot)
        verified.append(slot)
        times[slot] = observed
    if not missing:
        if pinned_plan is None:
            _reject("complete original receipts without pinned G35 plan")
        if not (max(times[s] for s in (
                "task_manifest", "task_source_attestation",
                "evaluator_manifest", "fit_cohort_commitment",
                "transfer_cohort_commitment", "custodian_attestation",
                "frozen_thresholds_receipt")) <
                times["prediction_seal_receipt"] <
                times["label_release_receipt"]):
            _reject("invalid claimed seal/release ordering")
    return {
        "status": MISSING_STATUS if missing else HASHED_STATUS,
        "missing_original_receipts": missing,
        "verified_receipt_byte_hashes": verified,
        "g35_plan_sha256": plan_hash,
        "original_source_authenticated": False,
        "independent_custody_authenticated": False,
        "receipt_actor_and_time_independently_verified": False,
        "primary_execution_allowed": False,
        "scientific_acceptance_allowed": False,
        "protected_first_use_allowed": False,
    }
