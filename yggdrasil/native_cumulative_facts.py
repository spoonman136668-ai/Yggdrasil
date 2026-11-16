"""NKR-08: non-destructive, source-pinned cumulative typed factual memory.

Isolated research-only wrapper around NKR-06's complete historical Q/P/Q
source. New direct observations are held in a *separate candidate ledger*,
never in accepted Yggdrasil memory, the historical facts image or causal cells.

A caller-supplied SHA pins exact bundle/checkpoint bytes. Neither a SHA nor
a 'direct observation' field authenticates an external source: the only
admissible input here is a synthetic engineering fixture.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re

from yggdrasil.native_knowledge_activation import (
    NativeKnowledgeSession, PINNED_MANIFEST_SHA, PINNED_TRAIN_SHA)
from yggdrasil.native_factual_weights import canonical, digest

BUNDLE_SCHEMA = "yggdrasil.nkr08.typed-public-observation-bundle.v1"
CHECKPOINT_SCHEMA = "yggdrasil.nkr08.cumulative-fact-checkpoint.v1"
MAX_BUNDLE_BYTES = 196608
MAX_CHECKPOINT_BYTES = 524288
MAX_EVIDENCE = 4096
MAX_BUNDLES = 64
MAX_RECORDS_PER_BUNDLE = 1024
MAX_QUERY = 256
REF = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9/_:.#-]{0,79}\Z")


def _pairs_unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("NKR08_DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def _doc(raw, *, limit, error):
    if type(raw) is not bytes or not raw or len(raw) > limit:
        raise ValueError(error + "_BYTES")
    try:
        obj = json.loads(raw.decode("ascii"), object_pairs_hook=_pairs_unique)
    except (UnicodeError, ValueError) as exc:
        raise ValueError(error + "_JSON") from exc
    if type(obj) is not dict or raw != canonical(obj):
        raise ValueError(error + "_NONCANONICAL")
    return obj


def _pinned(raw, expected, error):
    if (type(expected) is not str or not re.fullmatch(r"[0-9a-f]{64}", expected)
            or not hmac.compare_digest(digest(raw), expected)):
        raise ValueError(error + "_PIN_MISMATCH")


def _reference(x):
    if type(x) is not str or REF.fullmatch(x) is None:
        raise ValueError("NKR08_SOURCE_REFERENCE_INVALID")
    return x


def _triple(value):
    if (type(value) is not list or len(value) != 3
            or any(type(v) is not int or not 1 <= v <= 0xFFFFFFFF for v in value)):
        raise ValueError("NKR08_OBSERVATION_NOT_TYPED_QPQ")
    return tuple(value)


def empty_checkpoint():
    return canonical({
        "schema": CHECKPOINT_SCHEMA,
        "base_manifest_sha256": PINNED_MANIFEST_SHA,
        "base_train_sha256": PINNED_TRAIN_SHA,
        "evidence": [],
        "bundles": [],
        "source_authenticity": "ENGINEERING_FIXTURE_ONLY_NOT_CERTIFIED",
        "scientific_pass": False,
        "native_admission": False,
    })


def _parse_checkpoint(raw, expected):
    _pinned(raw, expected, "NKR08_CHECKPOINT")
    obj = _doc(raw, limit=MAX_CHECKPOINT_BYTES, error="NKR08_CHECKPOINT")
    if (set(obj) != {
            "schema", "base_manifest_sha256", "base_train_sha256", "evidence",
            "bundles", "source_authenticity", "scientific_pass", "native_admission"
        } or obj["schema"] != CHECKPOINT_SCHEMA
            or obj["base_manifest_sha256"] != PINNED_MANIFEST_SHA
            or obj["base_train_sha256"] != PINNED_TRAIN_SHA
            or obj["source_authenticity"] != "ENGINEERING_FIXTURE_ONLY_NOT_CERTIFIED"
            or obj["scientific_pass"] is not False
            or obj["native_admission"] is not False):
        raise ValueError("NKR08_CHECKPOINT_CONTRACT_INVALID")
    evidence = obj["evidence"]
    bundles = obj["bundles"]
    if (type(evidence) is not list or len(evidence) > MAX_EVIDENCE
            or type(bundles) is not list or len(bundles) > MAX_BUNDLES):
        raise ValueError("NKR08_CHECKPOINT_CAPACITY_INVALID")
    previous = None
    for item in evidence:
        if type(item) is not list or len(item) != 2:
            raise ValueError("NKR08_CHECKPOINT_EVIDENCE_INVALID")
        ref, triple = item
        _reference(ref)
        _triple(triple)
        if previous is not None and ref <= previous:
            raise ValueError("NKR08_CHECKPOINT_EVIDENCE_ORDER")
        previous = ref
    seen_ids = set()
    for record in bundles:
        if (type(record) is not list or len(record) != 2
                or type(record[1]) is not str
                or re.fullmatch(r"[0-9a-f]{64}", record[1]) is None):
            raise ValueError("NKR08_CHECKPOINT_BUNDLE_INVALID")
        ident = _reference(record[0])
        if ident in seen_ids:
            raise ValueError("NKR08_CHECKPOINT_BUNDLE_REUSED")
        seen_ids.add(ident)
    return obj


class CumulativeNativeFacts:
    """Read-only historical source + SHA-pinned developmental fact evidence."""

    __slots__ = ("base", "_checkpoint", "_index", "_facts", "_bundle_index")

    def __init__(self, base, checkpoint=None, *, checkpoint_sha256=None):
        if not isinstance(base, NativeKnowledgeSession):
            raise ValueError("NKR08_NATIVE_FACT_SESSION_REQUIRED")
        receipt = base.receipt
        if (type(receipt) is not dict
                or receipt.get("image_manifest_sha256") != PINNED_MANIFEST_SHA
                or receipt.get("source_train_sha256") != PINNED_TRAIN_SHA
                or receipt.get("native_accepted") is not False):
            raise ValueError("NKR08_HISTORICAL_BASE_PIN_DRIFT")
        raw = empty_checkpoint() if checkpoint is None else checkpoint
        expected = digest(raw) if checkpoint is None else checkpoint_sha256
        obj = _parse_checkpoint(raw, expected)
        self.base = base
        self._checkpoint = raw
        self._index = {ref: tuple(triple) for ref, triple in obj["evidence"]}
        self._facts = frozenset(self._index.values())
        self._bundle_index = {key: sha for key, sha in obj["bundles"]}

    def checkpoint(self):
        return self._checkpoint

    @property
    def checkpoint_sha256(self):
        return digest(self._checkpoint)

    def stage(self, raw, expected_source_sha256):
        """Return (new_candidate, receipt); never mutate this or base object."""
        _pinned(raw, expected_source_sha256, "NKR08_BUNDLE")
        data = _doc(raw, limit=MAX_BUNDLE_BYTES, error="NKR08_BUNDLE")
        if set(data) != {"schema", "source_id", "source_kind",
                          "source_mode", "records"}:
            raise ValueError("NKR08_BUNDLE_FIELDS_INVALID")
        if (data["schema"] != BUNDLE_SCHEMA
                or data["source_kind"] != "direct_public_observation"
                or data["source_mode"] != "engineering_fixture_only"):
            raise PermissionError("NKR08_NONOBSERVED_OR_UNQUALIFIED_SOURCE")
        source_id = _reference(data["source_id"])
        rows = data["records"]
        if type(rows) is not list or len(rows) > MAX_RECORDS_PER_BUNDLE:
            raise ValueError("NKR08_BUNDLE_CAPACITY")
        known = self._bundle_index.get(source_id)
        if known is not None:
            if not hmac.compare_digest(known, expected_source_sha256):
                raise ValueError("NKR08_SOURCE_ID_REBOUND")
            # Same source/version, second ingestion has no effects.
            return self, {
                "source_id": source_id, "bundle_sha256": expected_source_sha256,
                "records": len(rows), "new_unique_facts": 0,
                "already_in_historical": 0, "already_in_delta": 0,
                "duplicate_source_refs": len(rows),
                "total_candidate_delta_facts": len(self._facts),
                "checkpoint_sha256": self.checkpoint_sha256,
                "classification": "DUPLICATE_BUNDLE_NO_CHANGE",
                "scientific_pass": False, "native_accepted": False,
            }
        if len(self._bundle_index) >= MAX_BUNDLES:
            raise ValueError("NKR08_MAX_BUNDLES")
        state = dict(self._index)
        facts = set(self._facts)
        added = historical = prior = duplicate = 0
        last_ref = None
        for row in rows:
            if type(row) is not list or len(row) != 4:
                raise ValueError("NKR08_BUNDLE_RECORD_SHAPE")
            fact = _triple(row[:3])
            ref = _reference(row[3])
            if last_ref is not None and ref < last_ref:
                raise ValueError("NKR08_BUNDLE_REFERENCES_UNSORTED")
            last_ref = ref
            if ref in state:
                if state[ref] != fact:
                    raise ValueError("NKR08_EVIDENCE_REFERENCE_CONFLICT")
                duplicate += 1
                continue
            if len(state) == MAX_EVIDENCE:
                raise ValueError("NKR08_MAX_EVIDENCE")
            state[ref] = fact
            if self.base.fact(*fact)["witnessed"]:
                historical += 1
            elif fact in facts:
                prior += 1
            else:
                added += 1
            facts.add(fact)
        updated = _parse_checkpoint(self._checkpoint, self.checkpoint_sha256)
        updated["evidence"] = [[ref, list(fact)]
                               for ref, fact in sorted(state.items())]
        updated["bundles"].append([source_id, expected_source_sha256])
        checkpoint = canonical(updated)
        if len(checkpoint) > MAX_CHECKPOINT_BYTES:
            raise ValueError("NKR08_CHECKPOINT_SIZE_CAPACITY")
        candidate = CumulativeNativeFacts(
            self.base, checkpoint, checkpoint_sha256=digest(checkpoint))
        if candidate.checkpoint() != checkpoint:
            raise AssertionError("NKR08_COLD_CANDIDATE_DRIFT")
        return candidate, {
            "source_id": source_id,
            "bundle_sha256": expected_source_sha256,
            "records": len(rows),
            "new_unique_facts": added,
            "already_in_historical": historical,
            "already_in_delta": prior,
            "duplicate_source_refs": duplicate,
            "total_candidate_delta_facts": len(candidate._facts),
            "total_evidence_refs": len(candidate._index),
            "checkpoint_sha256": candidate.checkpoint_sha256,
            "classification": "CANDIDATE_FIXTURE_EVIDENCE_ONLY",
            "scientific_pass": False, "native_accepted": False,
        }

    def fact(self, subject, relation, obj):
        original = self.base.fact(subject, relation, obj)
        if original["witnessed"]:
            return original
        needle = _triple([subject, relation, obj])
        if needle in self._facts:
            return {
                "classification": "DEVELOPMENT_OBSERVED_FACT_NOT_ADMITTED",
                "witnessed": True, "subject_q": subject,
                "relation_p": relation, "object_q": obj,
                "source_mode": "engineering_fixture_only",
                "source_provenance": "SOURCE_SHA_PINNED_BYTES_NOT_AUTHENTICATED",
                "native_accepted": False, "verified_new_real_knowledge": False,
                "can_write_causal_consequence": False,
            }
        return original

    def objects(self, subject, relation, *, limit=64, after=0):
        if type(limit) is not int or not 1 <= limit <= MAX_QUERY:
            raise ValueError("NKR08_QUERY_LIMIT")
        if type(after) is not int or not 0 <= after <= 0xFFFFFFFF:
            raise ValueError("NKR08_QUERY_CURSOR")
        # Historical base already enforces subject, relation and positive IDs.
        original = self.base.objects(subject, relation, limit=limit, after=after)
        additions = (o for s, p, o in self._facts if
                     s == subject and p == relation and o > after)
        objects = sorted(set(original["objects"]).union(additions))[:limit]
        return {
            "classification": "HISTORICAL_PLUS_CANDIDATE_DEV_EVIDENCE",
            "objects": objects,
            "source_train_sha256": PINNED_TRAIN_SHA,
            "candidate_delta_sha256": self.checkpoint_sha256,
            "native_accepted": False,
            "can_write_causal_consequence": False,
        }

    def hypothesize(self, subject, first_relation, second_relation,
                    *, max_intermediates=16, max_candidates=64):
        if (type(max_intermediates) is not int
                or not 1 <= max_intermediates <= 64
                or type(max_candidates) is not int
                or not 1 <= max_candidates <= MAX_QUERY):
            raise ValueError("NKR08_HYPOTHESIS_BUDGET")
        mids = self.objects(subject, first_relation,
                            limit=max_intermediates)["objects"]
        results, seen = [], set()
        for mid in mids:
            for obj in self.objects(mid, second_relation,
                                    limit=max_candidates)["objects"]:
                if obj not in seen:
                    seen.add(obj)
                    results.append(obj)
                    if len(results) >= max_candidates:
                        break
            if len(results) >= max_candidates:
                break
        return {
            "classification": "UNVERIFIED_COMPOSED_PATH_HYPOTHESES",
            "objects": results,
            "source_train_sha256": PINNED_TRAIN_SHA,
            "candidate_delta_sha256": self.checkpoint_sha256,
            "native_accepted": False,
            "verified_new_real_knowledge": False,
            "can_write_causal_consequence": False,
        }
