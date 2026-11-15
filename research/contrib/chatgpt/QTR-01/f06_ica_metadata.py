#!/usr/bin/env python3
"""QTR-01 F06: bounded read-only public ICA feature metadata audit.

No Qwen execution, activation test, feature steering, paid APIs, raw texts,
model-weight reads, source mutation, or human/example semantic validation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request

MODEL = "qwen3.6-27b"
SOURCE = "32-icalens-res"
INDEX = "77"
URL = f"https://www.neuronpedia.org/api/feature/{MODEL}/{SOURCE}/{INDEX}"
BOUND = 1_000_000


class BadSource(ValueError):
    pass


def get_public():
    req = urllib.request.Request(URL, headers={
        "User-Agent": "qtr01-f06-metadata/1.0",
        "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        body = resp.read(BOUND + 1)
    if not 0 < len(body) <= BOUND:
        raise BadSource("BYTE_BOUND")
    return body


def profile(raw):
    if not 0 < len(raw) <= BOUND:
        raise BadSource("BYTE_BOUND")
    try:
        data = json.loads(raw.decode("utf-8"),
                          parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    except (ValueError, UnicodeError) as e:
        raise BadSource("INVALID_JSON") from e
    if not isinstance(data, dict):
        raise BadSource("NOT_DICT")
    ident = {key: data.get(key) for key in ("modelId", "sourceId", "source", "index")}
    seen_source = ident["sourceId"] if ident["sourceId"] is not None else ident["source"]
    if isinstance(seen_source, dict):
        seen_source = seen_source.get("id")
    if str(ident["modelId"]) != MODEL or str(seen_source) != SOURCE or str(ident["index"]) != INDEX:
        raise BadSource("IDENTITY_MISMATCH")
    explanations = data.get("explanations") or []
    activations = data.get("activations") or []
    if not isinstance(explanations, list) or not isinstance(activations, list):
        raise BadSource("INVALID_METADATA_SHAPE")
    return {
        "schema": "yggdrasil.qtr01.f06.public-ica-metadata.v1",
        "identifiable_record": True,
        "url": URL,
        "sha256_public_response": hashlib.sha256(raw).hexdigest(),
        "source_snapshot_immutable": False,
        "bytes": len(raw),
        "top_level_fields": sorted(str(k) for k in data),
        "explanation_objects": len(explanations),
        "activation_objects": len(activations),
        "provider_documents_inference_enabled": True,
        "inference_enabled_verified_by_call": False,
        "semantic_label_accurate": "UNVERIFIED",
        "causal_intervention_performed": False,
        "causal_concept_proven": False,
        "native_recipient_alignment_proven": False,
        "weight_edit_performed": False,
        "result": "SOURCE_RECORD_IDENTIFIABLE_ONLY"
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--one-fixed-public-read", action="store_true", required=True)
    p.parse_args()
    try:
        result = profile(get_public())
    except (BadSource, OSError, TimeoutError) as error:
        print("QTR01_F06_FAIL_CLOSED: " + str(error), file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
