#!/usr/bin/env python3
"""F07: one public model-card metadata GET; matrix inventory != transplantation."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.request

URL = "https://huggingface.co/api/models/neuronpedia/icalens-qwen3.6-27b"
REPO_ID = "neuronpedia/icalens-qwen3.6-27b"
LIMIT = 1_048_576
LAYER = 32
SHA40 = re.compile(r"^[0-9a-f]{40}$")
VECTORS = (".safetensors", ".pt", ".pth")


class InvalidMetadata(ValueError):
    pass


def read_public() -> bytes:
    request = urllib.request.Request(URL, headers={
        "User-Agent": "qtr01-f07-source-matrix-inventory/1.0",
        "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=20) as response:
        data = response.read(LIMIT + 1)
    if not data or len(data) > LIMIT:
        raise InvalidMetadata("PUBLIC_RESPONSE_SIZE")
    return data


def classify_metadata(data: bytes) -> dict:
    if not data or len(data) > LIMIT:
        raise InvalidMetadata("PUBLIC_RESPONSE_SIZE")
    try:
        obj = json.loads(data.decode("utf-8"))
    except (UnicodeError, ValueError) as err:
        raise InvalidMetadata("PUBLIC_RESPONSE_NOT_JSON") from err
    if not isinstance(obj, dict) or obj.get("id") != REPO_ID:
        raise InvalidMetadata("MODEL_REPO_IDENTITY_MISMATCH")
    revision = obj.get("sha")
    if not isinstance(revision, str) or not SHA40.fullmatch(revision):
        raise InvalidMetadata("NO_EXACT_SOURCE_REVISION")
    files = obj.get("siblings")
    if not isinstance(files, list) or len(files) > 3000:
        raise InvalidMetadata("SOURCE_FILE_LIST_INVALID")
    filenames = []
    for entry in files:
        if not isinstance(entry, dict) or not isinstance(entry.get("rfilename"), str):
            raise InvalidMetadata("INVALID_SOURCE_FILE_RECORD")
        name = entry["rfilename"]
        if len(name) > 512 or ".." in name or name.startswith("/"):
            raise InvalidMetadata("SOURCE_PATH_UNSAFE")
        filenames.append(name)
    card = obj.get("cardData")
    card = card if isinstance(card, dict) else {}
    license_declared = card.get("license")
    if not isinstance(license_declared, str) or not 1 <= len(license_declared) <= 100:
        license_declared = None

    # This checks only whether there is a plausible layer-specific numerical
    # matrix inventory. A filename does NOT verify any actual vector bytes.
    pattern = re.compile(r"(?:blocks[.]L[.]|blocks[.]|layers[.]|layer[_/-])32(?:[./_-]|$)", re.I)
    layer32 = [n for n in filenames if pattern.search(n) and n.endswith(VECTORS)]
    generic = [n for n in filenames if n.lower().endswith(VECTORS)]
    return {
        "schema": "yggdrasil.qtr01.f07.matrix-source-inventory.v1",
        "repository": REPO_ID, "hub_revision_sha": revision,
        "hub_response_sha256": hashlib.sha256(data).hexdigest(),
        "hub_response_bytes": len(data),
        "declared_license": license_declared or "UNVERIFIED",
        "repository_file_count": len(filenames),
        "numeric_artifact_file_count": len(generic),
        "explicit_layer32_matrix_candidates": len(layer32),
        "matrix_candidate_names": layer32[:8],
        "actual_matrix_bytes_fetched": False,
        "actual_matrix_sha256_verified": False,
        "analyzed_qwen_checkpoint_exact_sha_verified": False,
        "counterfactual_causal_semantics_verified": False,
        "independently_licensed_semantic_labels_verified": False,
        "paired_native_recipient_state_alignment_verified": False,
        "transplantation_eligible": False,
        "decision": "NO_GO_NUMERICAL_TRANSPLANT_WITH_NO_INFERENCE_METADATA",
        "next_executable_if_scope_changes": (
            "independently hash published fitted vectors and verify the exact "
            "source checkpoint, then preregister causal feature/recipient paired "
            "probes; do not use filenames as proof of knowledge transfer")
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--one-public-metadata-read", action="store_true", required=True)
    parser.parse_args()
    try:
        result = classify_metadata(read_public())
    except (InvalidMetadata, OSError, TimeoutError) as err:
        print("QTR01_F07_SOURCE_CUSTODY_BLOCKED: " + str(err), file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
