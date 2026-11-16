"""NKR-04: stage exact-source public consequences into opt-in native weights.

Research-only compiler. Source SHA256 authenticates bytes against a caller-owned
pin, NOT the source's authority or correctness. Only public engineering fixtures
are enabled here. Real-world native admission requires separate independent
source custody and owner acceptance, intentionally absent from this module.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import json

from yggdrasil.native_relation_memory import NativeRelationMemory
from yggdrasil.public_causal_cells import PublicCausalCells

SCHEMA = "yggdrasil.native-evidence-bundle.v1"
RECEIPT_SCHEMA = "yggdrasil.native-evidence-candidate.v1"
MAX_BUNDLE_BYTES = 131072
MAX_SOURCE_RECORDS = NativeRelationMemory.MAX_UNIQUE_OBSERVATIONS
ALLOWED_KEYS = frozenset(("schema", "source_id", "source_mode",
                           "source_kind", "license", "records"))
ALLOWED_SOURCE_MODE = "engineering_fixture_only"
ALLOWED_SOURCE_KIND = "observed_public_intervention"
ALLOWED_LICENSE = "synthetic-fixture"


def canonical_json(value):
    """Canonical ASCII bytes for reproducible source and result identities."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def digest(value):
    return hashlib.sha256(value).hexdigest()


def _unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("NKR04_DUPLICATED_JSON_FIELD")
        result[key] = value
    return result


def _valid_ascii_source(value):
    return (type(value) is str and 1 <= len(value) <= 96
            and value.isascii()
            and all(33 <= ord(char) <= 126 for char in value))


@dataclass(frozen=True)
class StagedNativeWeights:
    """Candidate only, never accepted-model admission or source certification."""
    checkpoint: bytes
    receipt: dict


def stage_native_bundle(raw, expected_source_sha256, *,
                        prior_checkpoint=None):
    """Compile without modifying an external object or accepted Yggdrasil state.

    Input is an immutable, externally pinned canonical development source.
    Its public observations are staged in a temporary NKR03 NativeRelationMemory.
    A candidate native checkpoint is returned, never installed or promoted.
    """
    if (type(raw) is not bytes or len(raw) > MAX_BUNDLE_BYTES or not raw):
        raise ValueError("NKR04_SOURCE_BYTES_INVALID")
    if (type(expected_source_sha256) is not str
            or len(expected_source_sha256) != 64
            or any(x not in "0123456789abcdef" for x in expected_source_sha256)
            or not hmac.compare_digest(digest(raw), expected_source_sha256)):
        raise ValueError("NKR04_SOURCE_PIN_MISMATCH")
    try:
        doc = json.loads(raw.decode("ascii"), object_pairs_hook=_unique_keys)
    except (ValueError, UnicodeError) as exc:
        raise ValueError("NKR04_SOURCE_DOCUMENT_INVALID") from exc
    if type(doc) is not dict or set(doc) != ALLOWED_KEYS:
        raise ValueError("NKR04_SOURCE_SCHEMA_INVALID")
    if (doc["schema"] != SCHEMA
            or doc["source_mode"] != ALLOWED_SOURCE_MODE
            or doc["source_kind"] != ALLOWED_SOURCE_KIND
            or doc["license"] != ALLOWED_LICENSE):
        # In particular, no graph triple, inferred counterfactual, model output,
        # hidden answer, or self-asserted "qualified" real source is accepted.
        raise PermissionError("NKR04_UNQUALIFIED_SOURCE_KIND")
    if not _valid_ascii_source(doc["source_id"]):
        raise ValueError("NKR04_SOURCE_ID_INVALID")
    if raw != canonical_json(doc):
        raise ValueError("NKR04_NONCANONICAL_SOURCE")
    rows = doc["records"]
    if type(rows) is not list or len(rows) > MAX_SOURCE_RECORDS:
        raise ValueError("NKR04_SOURCE_CAPACITY")
    # Validate the entire input before any candidate is changed.
    previous_key = None
    for row in rows:
        if (type(row) is not list or len(row) != 5
                or any(type(n) is not int for n in row[:4])
                or not 0 <= row[0] < NativeRelationMemory.ADDRESSES
                or not 0 <= row[1] < (1 << NativeRelationMemory.CONTEXT_BITS)
                or row[2] not in (0, 1) or row[3] not in (0, 1)
                or not _valid_ascii_source(row[4])):
            raise ValueError("NKR04_BAD_OBSERVATION")
        key = (row[0], row[1], row[2])
        if previous_key is not None and key < previous_key:
            raise ValueError("NKR04_SOURCE_ORDER_NONCANONICAL")
        previous_key = key
    if prior_checkpoint is not None and type(prior_checkpoint) is not bytes:
        raise ValueError("NKR04_PRIOR_CHECKPOINT_TYPE")
    bank = (NativeRelationMemory.restore(prior_checkpoint)
            if prior_checkpoint is not None else NativeRelationMemory())
    baseline = bank.checkpoint()
    new, duplicate = 0, 0
    for slot, context, action, outcome, source_ref in rows:
        retained = slot >= PublicCausalCells.ACTIVE_SLOTS
        local = slot - PublicCausalCells.ACTIVE_SLOTS if retained else slot
        if bank.observe_public_verified(local, context, action, outcome,
                                        source_ref, retained=retained):
            new += 1
        else:
            duplicate += 1
    checkpoint = bank.checkpoint()
    if NativeRelationMemory.restore(checkpoint).checkpoint() != checkpoint:
        raise AssertionError("NKR04_COLD_REPLAY_MISMATCH")
    report = {
        "schema": RECEIPT_SCHEMA,
        "source_sha256": expected_source_sha256,
        "source_id": doc["source_id"],
        "source_kind": doc["source_kind"],
        "source_authenticity": "UNVERIFIED_EXACT_BYTES_ONLY",
        "source_records": len(rows),
        "unique_added": new,
        "duplicates_ignored": duplicate,
        "total_native_observations": bank.unique_observations,
        "populated_native_slots": sum(
            bool(bank._events[slot] or bank._exceptions[slot])
            for slot in range(bank.ADDRESSES)),
        "distinct_numeric_profiles": bank.unique_programmed_profiles,
        "verified_exception_records": bank.verified_exception_count,
        "previous_checkpoint_sha256": digest(baseline),
        "candidate_checkpoint_sha256": digest(checkpoint),
        "candidate_checkpoint_bytes": len(checkpoint),
        "scientific_pass": False,
        "native_admission": False,
        "accepted_main_mutated": False,
        "source_first_use": False,
    }
    return StagedNativeWeights(checkpoint, report)
