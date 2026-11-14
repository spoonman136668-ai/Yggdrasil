#!/usr/bin/env python3
"""QTR-01 F05: bounded Neuronpedia source metadata feasibility, no model inference.

This makes two fixed public GETs. It deliberately does not print or store
automatically-generated explanation text, excerpts, token examples or logits.
Those are NOT licensed or validated native-model training data.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
import urllib.request

MODEL = "qwen3-32b"
SOURCE = "32-resid-batchtopk-65k"
INDICES = ("37427", "51972")
MAX_BYTES = 2_000_000
URL_PREFIX = "https://www.neuronpedia.org/api/feature/"


class InvalidInput(ValueError):
    pass


def bounded_get(index: str) -> bytes:
    if index not in INDICES:
        raise InvalidInput("NON_PREREGISTERED_FEATURE")
    url = f"{URL_PREFIX}{MODEL}/{SOURCE}/{index}"
    req = urllib.request.Request(url, headers={"User-Agent": "qtr01-f05-source-audit/1.0",
                                              "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as response:
        raw = response.read(MAX_BYTES + 1)
    if not 0 < len(raw) <= MAX_BYTES:
        raise InvalidInput("RESPONSE_BYTE_BOUND")
    return raw


def summarize(index: str, raw: bytes) -> dict:
    if index not in INDICES or not 0 < len(raw) <= MAX_BYTES:
        raise InvalidInput("INVALID_INDEX_OR_BOUND")
    try:
        obj = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise InvalidInput("BAD_JSON") from exc
    if not isinstance(obj, dict):
        raise InvalidInput("NOT_OBJECT")
    # Providers can expose index either as a JSON integer or string.
    def observed(k):
        v = obj.get(k)
        return None if v is None else str(v)
    # Neuronpedia's public feature API may use source instead of sourceId.
    raw_source = obj.get("sourceId", obj.get("source"))
    if isinstance(raw_source, dict):
        raw_source = raw_source.get("id")
    reported = {"modelId": observed("modelId"), "sourceId": None if raw_source is None else str(raw_source), "index": observed("index")}
    expected = {"modelId": MODEL, "sourceId": SOURCE, "index": index}
    if any(reported[k] != value for k, value in expected.items()):
        raise InvalidInput("SOURCE_IDENTITY_NOT_VERIFIED")
    interpretations = obj.get("explanations")
    activations = obj.get("activations")
    if interpretations is not None and not isinstance(interpretations, list):
        raise InvalidInput("EXPLANATIONS_SHAPE_INVALID")
    if activations is not None and not isinstance(activations, list):
        raise InvalidInput("ACTIVATIONS_SHAPE_INVALID")
    n_expl = len(interpretations or [])
    n_act = len(activations or [])
    # No claims about accuracy or copyright status from any provider scores.
    n_scores = sum(bool(isinstance(x, dict) and x.get("scores"))
                   for x in (interpretations or []))
    return {
        "feature_id": index, "source_id": SOURCE, "model_id": MODEL,
        "byte_count": len(raw), "response_sha256": hashlib.sha256(raw).hexdigest(),
        "explanation_objects": n_expl, "activation_objects": n_act,
        "explanations_with_reported_scores": n_scores,
        "availability": ("EXPLANATION_CANDIDATE_ONLY" if n_expl else "INSUFFICIENT_EXPLANATION_EVIDENCE"),
        "independent_semantic_validation": False,
        "causal_intervention_validation": False,
        "recipient_alignment_validation": False,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--two-preregistered-reads", action="store_true", required=True)
    p.parse_args()
    out = []
    try:
        for index in INDICES:
            out.append(summarize(index, bounded_get(index)))
    except (InvalidInput, OSError, TimeoutError) as e:
        print("QTR01_F05_FAIL_CLOSED: " + str(e), file=sys.stderr)
        return 2
    print(json.dumps({
        "schema": "yggdrasil.qtr01.f05.public-feature-metadata.v1",
        "recorded_features": out, "donor_model_executed": False,
        "model_weights_modified": False, "scientific_transplant_performed": False,
        "provider_rights_for_model_training": "UNVERIFIED; DO_NOT_USE_AS_TRAINING_DATA",
        "next_gate": "independently licensed causal probe and recipient-native interface, not reuse of unvalidated automated labels",
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
