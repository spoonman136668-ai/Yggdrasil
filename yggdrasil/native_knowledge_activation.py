"""NKR-06: explicit offline read-only activation of the pinned full factual image.

Nothing is injected into accepted DG-1 or NKR causal cells. This is an isolated,
locally installed research knowledge session; Q/P/Q statements are historical
source claims, and two-hop compositions are hypotheses rather than facts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import time

from yggdrasil.native_factual_weights import NativeFactualWeights, canonical, digest

SCHEMA = "yggdrasil.nkr06.offline-factual-activation.v1"
PINNED_MANIFEST_SHA = "aa2d56e72284a042aee72587028642110327307b483de667586f105f018ebe8f"
PINNED_PACKED_SHA = "6dd87ba5bbf5fd7ecaffa6d48f674e34ce2a7cc7fa748ec7698d2c0a4cdae3d1"
PINNED_TRAIN_SHA = "2ef1a279f6393a8edfbb2b44114a2c97944272e5fe2a1bd2a7cbe48f94742f1a"
PINNED_ARCHIVE_SHA = "ccda8bbcd3cf599b30dd3fd8979ac26e59b48fc53d23128882a044bfbb67f878"
PINNED_ROWS = 21_343_681
PINNED_RELATIONS = 828
PINNED_BYTES = 256_124_172
PINNED_SOURCE_RUN = 43856374741
PINNED_ARTIFACT_ID = 14220169461


class NativeKnowledgeSession:
    """Source-attributed *factual* read-only session, not a learned causal oracle."""
    __slots__ = ("_weights", "receipt")

    def __init__(self, weights, receipt):
        self._weights = weights
        self.receipt = receipt

    def close(self):
        self._weights.close()

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()

    def fact(self, subject, relation, obj):
        witnessed = self._weights.has_fact(subject, relation, obj)
        return {
            "classification": "HISTORICAL_TRAIN_FACT" if witnessed else "UNKNOWN_ABSTAIN",
            "witnessed": witnessed,
            "subject_q": subject,
            "relation_p": relation,
            "object_q": obj,
            "source_train_sha256": PINNED_TRAIN_SHA,
            "source_temporality": "HISTORICAL_NOT_CURRENT",
            "native_accepted": False,
            "can_write_causal_consequence": False,
        }

    def objects(self, subject, relation, *, limit=64, after=0):
        return {
            "classification": "SOURCE_BACKED_HISTORICAL_OBJECTS",
            "objects": self._weights.objects(subject, relation, limit=limit, after=after),
            "source_train_sha256": PINNED_TRAIN_SHA,
            "native_accepted": False,
            "can_write_causal_consequence": False,
        }

    def hypothesize(self, subject, relation1, relation2, *, max_intermediates=16,
                    max_candidates=64):
        result = self._weights.two_hop_candidates(
            subject, relation1, relation2,
            max_intermediates=max_intermediates, max_candidates=max_candidates)
        if result["classification"] != "UNVERIFIED_PATH_HYPOTHESES":
            raise AssertionError("NKR06_HYPOTHESES_NOT_LABELED")
        return {**result, "source_temporality": "HISTORICAL_NOT_CURRENT",
                "verified_new_knowledge": False, "native_accepted": False,
                "can_write_causal_consequence": False}


def _check_pinned(weights):
    meta = weights.manifest
    if (meta["packed_sha256"] != PINNED_PACKED_SHA
            or meta["source_train_sha256"] != PINNED_TRAIN_SHA
            or meta["source_archive_sha256"] != PINNED_ARCHIVE_SHA
            or meta["records"] != PINNED_ROWS
            or meta["numeric_bytes"] != PINNED_BYTES
            or meta["distinct_relation_types"] != PINNED_RELATIONS
            or len(weights) != PINNED_ROWS
            or meta["original_valid_test_read"] is not False
            or meta["historical_queries_previously_consumed"] is not True
            or meta["accepted_native"] is not False
            or meta["scientific_pass"] is not False):
        raise ValueError("NKR06_SOURCE_CONTRACT_DRIFT")


def _open_image(where):
    path = Path(where)
    for name in ("facts.uint32le", "manifest.json"):
        x = path / name
        if x.is_symlink() or not x.is_file():
            raise ValueError("NKR06_SOURCE_MISSING_OR_SYMLINK")
    weights = NativeFactualWeights(path / "facts.uint32le",
                                   path / "manifest.json", PINNED_MANIFEST_SHA)
    try:
        _check_pinned(weights)
    except BaseException:
        weights.close()
        raise
    return weights


def install_offline_image(source_directory, destination_parent, name):
    """Explicitly install a complete preverified image into a fresh local root.

    No network, accepted-state mutation, controller start, automatic installation
    or untrusted destination overwrite. The target is not usable through the
    session factory until activation.json exists and cold readback succeeds.
    """
    if type(name) is not str or re.fullmatch(r"[a-z][a-z0-9_-]{2,63}", name) is None:
        raise ValueError("NKR06_INSTALL_NAME_INVALID")
    parent = Path(destination_parent)
    if not parent.is_dir() or parent.is_symlink():
        raise ValueError("NKR06_PARENT_NOT_OWNED_DIRECTORY")
    target = parent / name
    if target.exists() or target.is_symlink():
        raise FileExistsError("NKR06_TARGET_EXISTS_NO_OVERWRITE")
    source = Path(source_directory)
    start = time.monotonic()
    with _open_image(source) as proof:
        if proof.row_at(0) != tuple(proof.manifest["first_triple"]):
            raise AssertionError("NKR06_SOURCE_FIRST_TRIPLE_DRIFT")
        if proof.row_at(PINNED_ROWS - 1) != tuple(proof.manifest["last_triple"]):
            raise AssertionError("NKR06_SOURCE_LAST_TRIPLE_DRIFT")
    # mkdir is an atomic no-clobber lease on the requested target path.
    target.mkdir(mode=0o700)
    try:
        for name_ in ("facts.uint32le", "manifest.json"):
            with open(source / name_, "rb") as reader, open(target / name_, "xb") as writer:
                shutil.copyfileobj(reader, writer, length=1 << 20)
        with _open_image(target) as cold:
            first = cold.row_at(0)
            last = cold.row_at(PINNED_ROWS - 1)
            if (first != tuple(cold.manifest["first_triple"])
                    or last != tuple(cold.manifest["last_triple"])
                    or not cold.has_fact(*first) or not cold.has_fact(*last)):
                raise AssertionError("NKR06_COLD_INSTALL_MISMATCH")
        activation = {
            "schema": SCHEMA,
            "source_kind": "previously-consumed-historical-TRAIN-only",
            "artifact_run_id": PINNED_SOURCE_RUN,
            "artifact_id": PINNED_ARTIFACT_ID,
            "image_manifest_sha256": PINNED_MANIFEST_SHA,
            "image_sha256": PINNED_PACKED_SHA,
            "source_train_sha256": PINNED_TRAIN_SHA,
            "source_rows": PINNED_ROWS,
            "source_predicates": PINNED_RELATIONS,
            "native_accepted": False,
            "original_scientific_first_use": False,
            "knowledge_kind": "typed-historical-facts-not-causal-events",
            "readonly_session_only": True,
        }
        marker = canonical(activation)
        with open(target / "activation.json", "xb") as stream:
            stream.write(marker)
        return {"classification": "OFFLINE_FULL_HISTORICAL_FACTUAL_IMAGE_INSTALLED",
                "artifact_id": PINNED_ARTIFACT_ID,
                "manifest_sha256": PINNED_MANIFEST_SHA,
                "image_sha256": PINNED_PACKED_SHA,
                "installed_source_rows": PINNED_ROWS,
                "installed_bytes": PINNED_BYTES,
                "install_wall_seconds": time.monotonic() - start,
                "local_owner_storage_persistence": "CALLER_RESPONSIBILITY",
                "accepted_native": False}
    except BaseException:
        # Only remove the new path created under our own no-overwrite lease.
        shutil.rmtree(target)
        raise


def open_installed_session(path):
    """Open *only* a complete locally installed matching pinned image."""
    root = Path(path)
    proof_path = root / "activation.json"
    if proof_path.is_symlink() or not proof_path.is_file():
        raise ValueError("NKR06_NO_ACTIVATION_RECEIPT")
    try:
        raw = proof_path.read_bytes()
        doc = json.loads(raw.decode("ascii"))
    except (UnicodeError, ValueError) as exc:
        raise ValueError("NKR06_ACTIVATION_INVALID") from exc
    if (not isinstance(doc, dict) or raw != canonical(doc)
            or doc.get("schema") != SCHEMA
            or doc.get("image_manifest_sha256") != PINNED_MANIFEST_SHA
            or doc.get("image_sha256") != PINNED_PACKED_SHA
            or doc.get("source_train_sha256") != PINNED_TRAIN_SHA
            or doc.get("source_rows") != PINNED_ROWS
            or doc.get("source_predicates") != PINNED_RELATIONS
            or doc.get("native_accepted") is not False
            or doc.get("readonly_session_only") is not True):
        raise ValueError("NKR06_ACTIVATION_PIN_MISMATCH")
    return NativeKnowledgeSession(_open_image(root), doc)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--destination-parent", required=True)
    parser.add_argument("--name", default="yggdrasil-historical-facts")
    args = parser.parse_args()
    receipt = install_offline_image(args.source, args.destination_parent, args.name)
    root = Path(args.destination_parent) / args.name
    with open_installed_session(root) as session:
        first = session._weights.row_at(0)
        last = session._weights.row_at(PINNED_ROWS - 1)
        if not session.fact(*first)["witnessed"] or not session.fact(*last)["witnessed"]:
            raise AssertionError("NKR06_REAL_INDEX_LOOKUP_FAILED")
        unknown = session.fact(4294967295, 4294967295, 4294967295)
        if unknown["classification"] != "UNKNOWN_ABSTAIN":
            raise AssertionError("NKR06_UNKNOWN_NOT_REFUSED")
    print("NKR06_OFFLINE_ACTIVATION=" + json.dumps({
        **receipt, "verified_first_triple": list(first),
        "verified_last_triple": list(last),
        "verified_unknown_abstention": True,
        "scientific_pass": False, "accepted_main_mutated": False,
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
