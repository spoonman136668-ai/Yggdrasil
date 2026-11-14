#!/usr/bin/env python3
"""QTR-01/F04: prospective source-only identifiability screen; never run Qwen."""
import argparse
from collections import Counter
import hashlib
import json
import sys
import urllib.request

REV = "0f965454ffedb93e826546a7dc11b51a4622188e"
URL = f"https://huggingface.co/LeonInverse/qwen3.8-27b-scope-code/resolve/{REV}/interface/feature_list_1x.json"
MAX = 500_000
DESCRIPTORS = {"description", "explanation", "concept", "semantic_label", "meaning"}
PROBES = {"positive_examples", "negative_examples", "counterfactual", "test_cases"}
FEATURE_IDS = {"feat", "feature", "feature_id", "feature_idx", "index"}


class InvalidInput(ValueError):
    pass


def bounded_public_get() -> bytes:
    request = urllib.request.Request(URL, headers={"User-Agent": "qtr01-f04/1.0"})
    with urllib.request.urlopen(request, timeout=25) as response:
        data = response.read(MAX + 1)
    if not 0 < len(data) <= MAX:
        raise InvalidInput("BYTE_BOUND")
    return data


def screen(payload: bytes) -> dict:
    if not 0 < len(payload) <= MAX:
        raise InvalidInput("BYTE_BOUND")
    try:
        root = json.loads(payload.decode("utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise InvalidInput("INVALID_JSON") from exc
    if type(root) not in (dict, list):
        raise InvalidInput("INVALID_ROOT")
    counts, depth_limit = Counter(), 18
    descriptions = paired = nodes = 0

    def walk(v, depth=0):
        nonlocal descriptions, paired, nodes
        nodes += 1
        if depth > depth_limit or nodes > 300_000:
            raise InvalidInput("COMPLEXITY_LIMIT")
        if type(v) is dict:
            keys = {str(k).lower(): value for k, value in v.items()}
            counts.update(keys)
            has_description = any(k in DESCRIPTORS and isinstance(value, str) and len(value.split()) >= 4
                                  for k, value in keys.items())
            if has_description:
                descriptions += 1
                if FEATURE_IDS.intersection(keys) and PROBES.intersection(keys):
                    paired += 1
            for value in v.values():
                walk(value, depth + 1)
        elif type(v) is list:
            for value in v:
                walk(value, depth + 1)
    walk(root)
    # Even annotations in publisher metadata do not establish independent causal validity.
    return {
        "schema": "yggdrasil.qtr01.semantic-admission.v1",
        "pinned_revision": REV, "source": URL, "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload), "json_root": type(root).__name__, "nodes_examined": nodes,
        "field_names": sorted(counts), "natural_language_descriptor_records": descriptions,
        "descriptors_with_id_and_probe_fields": paired,
        "outcome": ("NO_GO_UNLABELLED_INTERFACE_FOR_SEMANTIC_TRANSPLANT"
                    if descriptions == 0 else "DESCRIPTION_HINTS_ONLY_INDEPENDENT_CAUSAL_PROOF_REQUIRED"),
        "source_feature_semantics_proven": False, "recipient_alignment_proven": False,
        "transplant_performed": False
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pinned-source-readonly", action="store_true", required=True)
    parser.parse_args()
    try:
        print(json.dumps(screen(bounded_public_get()), indent=2, sort_keys=True))
    except (InvalidInput, OSError, TimeoutError) as exc:
        print("QTR01_F04_FAIL_CLOSED: " + str(exc), file=sys.stderr)
        raise SystemExit(2)
