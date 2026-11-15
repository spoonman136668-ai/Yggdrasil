#!/usr/bin/env python3
"""F29 read-only, two-source JSON schema diagnostic; no knowledge admission."""
import argparse
import json
from pathlib import Path
import sys

from f26_semantic_association import NotAdmitted, safe_label
from f27_versioned_entitydata import LiveEntityData

SCHEMA = "yggdrasil.qtr01.f29.readonly-entitydata-schema-diagnostic.v1"
IDS = ("Q42", "Q5")
FROZEN = "d991dca367a8194c07b958d00c20637df8fe8622"
POLICY = Path(__file__).with_name("f29_prereg.json")


def preflight():
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    if (policy.get("schema") != SCHEMA
        or policy.get("status") != "FROZEN_BEFORE_CODE_OR_SOURCE"
        or policy.get("source_id_allowlist") != list(IDS)
        or policy.get("source_reader_file_sha") != "db561564c949ffe1a15c99dc460d18d0143588d1"
        or policy.get("source_request_limit") != 2
        or policy.get("source_per_response_bytes_max") != 4194304
        or policy.get("source_total_bytes_max") != 8388608
        or policy.get("source_timeout_seconds") != 15
        or policy.get("never_retry") is not True
        or policy.get("source_capture_no_admission") is not True
        or policy.get("no_native_project_code_or_model_weights") is not True):
        raise NotAdmitted("F29_PREREG_OR_SOURCE_CUSTODY_CHANGED")
    return policy


def typename(value):
    return type(value).__name__


def diagnose(qid, entity, receipt):
    if qid not in IDS or entity.get("id") != qid or receipt.get("entity") != qid:
        raise NotAdmitted("F29_NOT_FROZEN_ENTITY_OR_RECEIPT")
    for field in ("raw_sha256", "bytes", "revision"):
        if field not in receipt:
            raise NotAdmitted("F29_SOURCE_RECEIPT_FIELD_MISSING")
    if entity.get("lastrevid") != receipt["revision"]:
        raise NotAdmitted("F29_REVISION_RECEIPT_MISMATCH")
    labels = entity.get("labels")
    is_dict = type(labels) is dict
    en = labels.get("en") if is_dict else None
    en_is_dict = type(en) is dict
    label = en.get("value") if en_is_dict else None
    valid = False
    if en_is_dict and en.get("language") == "en" and type(label) is str:
        try:
            valid = bool(safe_label(label))
        except NotAdmitted:
            pass
    claims = entity.get("claims")
    return {
        "entity_id": qid,
        "raw_sha256": receipt["raw_sha256"],
        "response_bytes": receipt["bytes"],
        "lastrevid": receipt["revision"],
        "labels_field_type": typename(labels),
        "languages_present_count": len(labels) if is_dict else None,
        "en_present": "en" in labels if is_dict else False,
        "en_field_type": typename(en),
        "en_language_exact": en.get("language") == "en" if en_is_dict else False,
        "en_value_type": typename(label),
        "en_value_nonempty": bool(label.strip()) if type(label) is str else False,
        "en_value_safe_label": valid,
        "source_en_label_usable": valid,
        "claims_field_type": typename(claims),
        "claims_property_count": len(claims) if type(claims) is dict else None,
    }


def inspect(reader=None):
    preflight()
    reader = LiveEntityData() if reader is None else reader
    records = []
    for qid in IDS:
        entity, _ = reader.fetch(qid)
        records.append(diagnose(qid, entity, reader.receipts[-1]))
    if [r["entity_id"] for r in records] != list(IDS) or len(reader.receipts) != 2:
        raise NotAdmitted("F29_INCOMPLETE_SOURCE_DIAGNOSTIC")
    if reader.total_bytes > 8388608:
        raise NotAdmitted("F29_TOTAL_PROBE_BYTES_EXCEEDED")
    return {
        "schema": SCHEMA,
        "preregistration_commit": FROZEN,
        "source_metadata_only": True,
        "first_party": "Wikidata Special:EntityData JSON via existing F27 reader",
        "request_count": len(records),
        "source_bytes": reader.total_bytes,
        "records": records,
        "source_en_label_usable_count": sum(r["source_en_label_usable"] for r in records),
        "source_data_admitted": False,
        "model_weights_modified": False,
        "scientific_pass": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata-only", required=True, action="store_true")
    args = parser.parse_args()
    try:
        result = inspect()
    except (NotAdmitted, OSError, UnicodeError, TimeoutError, ValueError) as exc:
        print("F29_SOURCE_SCHEMA_BLOCKED=" + type(exc).__name__ + ":" + str(exc),
              file=sys.stderr)
        return 2
    print("F29_SCHEMA_DIAGNOSTIC=" + json.dumps(result, sort_keys=True, separators=(",", ":")))
    print("F29_NO_SOURCE_ADMISSION_OR_MODEL_WEIGHT_EDIT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
