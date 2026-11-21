"""KNOW02: inert typed-factual readout beside a research Amalgam checkpoint.

This is an *opt-in, read-only research seam* between two existing experimental
projects, not model integration or a new owner. No relation graph triple may
be converted to a native action/consequence witness; no causal feature mapping
is inferred. The supplied objects must be restored by their original owners
using original pinned source contracts before the bridge is constructed.
"""
from __future__ import annotations

import hashlib
import json
import re

AMALGAM_SCHEMA = "yggdrasil.ckad.native-causal-amalgam.v1"
NATIVE_SCHEMA = "yggdrasil.ckad.native-cumulative-learner.v5"
FACT_SCHEMA = "yggdrasil.nkr08.cumulative-fact-checkpoint.v1"
READOUT_SCHEMA = "yggdrasil.know02.typed-factual-readout.v1"
HISTORICAL_SHA = "2ef1a279f6393a8edfbb2b44114a2c97944272e5fe2a1bd2a7cbe48f94742f1a"
MANIFEST_SHA = "aa2d56e72284a042aee72587028642110327307b483de667586f105f018ebe8f"
MAX_NATIVE_BYTES = 32 * 1024 * 1024
MAX_FACT_BYTES = 524288
HEX = re.compile(r"[0-9a-f]{64}\Z")


def _require(ok, error):
    if not ok:
        raise ValueError("YGG_KNOW02_" + error)


def _digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _pin(s):
    return type(s) is str and HEX.fullmatch(s) is not None


def _unique(pairs):
    result = {}
    for name, value in pairs:
        _require(name not in result, "DUPLICATE_JSON_KEY")
        result[name] = value
    return result


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def _parse(raw, max_bytes):
    _require(type(raw) is bytes and 0 < len(raw) <= max_bytes, "CHECKPOINT_BYTES")
    try:
        obj = json.loads(raw.decode("ascii"), object_pairs_hook=_unique,
                         parse_constant=lambda _: _require(False, "NONFINITE"))
        normalized = _canonical(obj)
    except (ValueError, UnicodeError, OverflowError, TypeError) as exc:
        if isinstance(exc, ValueError) and str(exc).startswith("YGG_KNOW02_"):
            raise
        raise ValueError("YGG_KNOW02_INVALID_JSON") from exc
    _require(type(obj) is dict and normalized == raw, "NONCANONICAL_CHECKPOINT")
    return obj


def _read_checkpoint(instance, max_bytes, pin, label):
    method = getattr(instance, "checkpoint", None)
    _require(callable(method), label + "_CHECKPOINT_METHOD")
    raw = method()
    _require(type(raw) is bytes and 0 < len(raw) <= max_bytes,
             label + "_CHECKPOINT_BYTES")
    _require(_digest(raw) == pin, label + "_PIN_MISMATCH")
    return raw


def _qpq(*values):
    _require(all(type(x) is int and 1 <= x <= 0xFFFFFFFF for x in values),
             "INVALID_QPQ_IDENTIFIER")


class TypedFactualReadoutBridge:
    """Frozen, research-only paired readout; never changes native learning.

    ``native`` is an already restored NativeCausalAmalgam; ``facts`` is an
    already restored CumulativeNativeFacts using the NKR-06 historical image.
    Caller-supplied exact pins are mandatory but do not certify source truth.
    All operations recheck both checkpoint hashes *before and after* use.
    """
    __slots__ = ("_native", "_facts", "_native_sha", "_facts_sha")

    def __init__(self, native, facts, *, native_checkpoint_sha256,
                 facts_checkpoint_sha256):
        _require(_pin(native_checkpoint_sha256) and _pin(facts_checkpoint_sha256),
                 "EXPLICIT_TRUSTED_PINS_REQUIRED")
        self._native = native
        self._facts = facts
        self._native_sha = native_checkpoint_sha256
        self._facts_sha = facts_checkpoint_sha256
        self._verify_sources()

    def _check_snapshots(self):
        return (
            _read_checkpoint(self._native, MAX_NATIVE_BYTES, self._native_sha,
                             "NATIVE"),
            _read_checkpoint(self._facts, MAX_FACT_BYTES, self._facts_sha,
                             "FACTS"),
        )

    def _verify_sources(self):
        native_raw, facts_raw = self._check_snapshots()
        joint = _parse(native_raw, MAX_NATIVE_BYTES)
        _require(set(joint) == {
            "schema", "native_ascii", "native_parent_sha256",
            "specialist_parent_sha256", "action_heads", "temporal_heads"
        } and joint.get("schema") == AMALGAM_SCHEMA,
                 "RESEARCH_AMALGAM_ONLY")
        _require(_pin(joint["native_parent_sha256"]) and
                 _pin(joint["specialist_parent_sha256"]) and
                 type(joint["native_ascii"]) is str,
                 "AMALGAM_PARENTS")
        actual_native = _parse(joint["native_ascii"].encode("ascii"),
                               MAX_NATIVE_BYTES)
        _require(actual_native.get("schema") == NATIVE_SCHEMA and
                 actual_native.get("source_mode") == "engineering_fixture_only" and
                 actual_native.get("accepted_native") is False and
                 actual_native.get("scientific_pass") is False,
                 "UNACCEPTED_NATIVE_ONLY")
        _require(type(joint["action_heads"]) is list and
                 type(joint["temporal_heads"]) is list and
                 len(joint["action_heads"]) == 2 and
                 len(joint["temporal_heads"]) == 2,
                 "SPECIALIST_SHAPE")
        factual = _parse(facts_raw, MAX_FACT_BYTES)
        _require(set(factual) == {
            "schema", "base_manifest_sha256", "base_train_sha256",
            "evidence", "bundles", "source_authenticity",
            "scientific_pass", "native_admission"
        } and factual.get("schema") == FACT_SCHEMA and
                 factual.get("base_manifest_sha256") == MANIFEST_SHA and
                 factual.get("base_train_sha256") == HISTORICAL_SHA and
                 factual.get("source_authenticity") ==
                 "ENGINEERING_FIXTURE_ONLY_NOT_CERTIFIED" and
                 factual.get("scientific_pass") is False and
                 factual.get("native_admission") is False,
                 "UNACCEPTED_FACTUAL_ONLY")
        base = getattr(self._facts, "base", None)
        receipt = getattr(base, "receipt", None)
        _require(type(receipt) is dict and
                 receipt.get("image_manifest_sha256") == MANIFEST_SHA and
                 receipt.get("source_train_sha256") == HISTORICAL_SHA and
                 receipt.get("native_accepted") is False,
                 "PINNED_HISTORICAL_SOURCE_REQUIRED")
        # Do not trust a reported checkpoint_sha256 without rehashing bytes.
        self._check_snapshots()

    def _call(self, target, name, *args, **kwargs):
        self._check_snapshots()
        method = getattr(target, name, None)
        _require(callable(method), "MISSING_READOUT_METHOD")
        try:
            result = method(*args, **kwargs)
        finally:
            self._check_snapshots()
        return result

    def fact(self, subject, predicate, obj):
        _qpq(subject, predicate, obj)
        row = self._call(self._facts, "fact", subject, predicate, obj)
        _require(type(row) is dict and
                 (row.get("subject_q"), row.get("relation_p"), row.get("object_q")) ==
                 (subject, predicate, obj) and
                 row.get("native_accepted") is False and
                 row.get("can_write_causal_consequence") is False and
                 type(row.get("witnessed")) is bool,
                 "FACTUAL_READOUT_CONTRACT")
        classification = row.get("classification")
        if classification == "HISTORICAL_TRAIN_FACT":
            _require(row["witnessed"] is True and
                     row.get("source_train_sha256") == HISTORICAL_SHA and
                     row.get("source_temporality") == "HISTORICAL_NOT_CURRENT",
                     "HISTORICAL_FACT_PROVENANCE")
            kind = "HISTORICAL_STORED_QPQ"
        elif classification == "DEVELOPMENT_OBSERVED_FACT_NOT_ADMITTED":
            _require(row["witnessed"] is True and
                     row.get("source_mode") == "engineering_fixture_only" and
                     row.get("source_provenance") ==
                     "SOURCE_SHA_PINNED_BYTES_NOT_AUTHENTICATED" and
                     row.get("verified_new_real_knowledge") is False,
                     "UNQUALIFIED_DELTA")
            kind = "SYNTHETIC_ENGINEERING_QPQ"
        elif classification == "UNKNOWN_ABSTAIN":
            _require(row["witnessed"] is False and
                     row.get("source_train_sha256") == HISTORICAL_SHA,
                     "UNKNOWN_MUST_ABSTAIN")
            kind = "UNSUPPORTED_ABSTAIN"
        else:
            raise ValueError("YGG_KNOW02_UNRECOGNIZED_FACT_CLASS")
        return {
            "schema": READOUT_SCHEMA,
            "query_kind": "DIRECT_QPQ_MEMBERSHIP",
            "identifiers": [subject, predicate, obj],
            "evidence_kind": kind,
            "source_claim": classification,
            "stored_witness": row["witnessed"],
            "historical_source_sha256": HISTORICAL_SHA,
            "amalgam_checkpoint_sha256": self._native_sha,
            "factual_checkpoint_sha256": self._facts_sha,
            "native_model_consulted_for_fact": False,
            "native_model_knowledge_updated": False,
            "causal_observation_admitted": False,
            "scientific_pass": False,
            "accepted_native": False,
        }

    def hypotheses(self, subject, relation1, relation2, *,
                   max_intermediates=16, max_candidates=64):
        _qpq(subject, relation1, relation2)
        _require(type(max_intermediates) is int and
                 1 <= max_intermediates <= 64 and
                 type(max_candidates) is int and 1 <= max_candidates <= 256,
                 "HYPOTHESIS_BUDGET")
        result = self._call(self._facts, "hypothesize", subject, relation1,
                            relation2, max_intermediates=max_intermediates,
                            max_candidates=max_candidates)
        _require(type(result) is dict and
                 result.get("classification") ==
                 "UNVERIFIED_COMPOSED_PATH_HYPOTHESES" and
                 result.get("source_train_sha256") == HISTORICAL_SHA and
                 result.get("candidate_delta_sha256") == self._facts_sha and
                 result.get("native_accepted") is False and
                 result.get("verified_new_real_knowledge") is False and
                 result.get("can_write_causal_consequence") is False,
                 "HYPOTHESES_ARE_NOT_FACTS")
        objects = result.get("objects")
        _require(type(objects) is list and len(objects) <= max_candidates and
                 all(type(x) is int and 1 <= x <= 0xFFFFFFFF for x in objects) and
                 len(set(objects)) == len(objects),
                 "HYPOTHESES_OUTPUT_SHAPE")
        return {
            "schema": READOUT_SCHEMA,
            "query_kind": "TWO_HOP_CANDIDATES",
            "input_identifiers": [subject, relation1, relation2],
            "unverified_objects": list(objects),
            "classification": "UNVERIFIED_COMPOSED_PATH_HYPOTHESES",
            "factual_checkpoint_sha256": self._facts_sha,
            "amalgam_checkpoint_sha256": self._native_sha,
            "native_model_knowledge_updated": False,
            "causal_observation_admitted": False,
            "scientific_pass": False,
            "accepted_native": False,
        }

    def independent_native_plan(self, public_view):
        """Native planner readout is intentionally independent of fact lookup.

        It receives ONLY the explicit public numeric view, never a QPQ triple.
        Caller remains responsible for the original view/feature source contract.
        """
        return self._call(self._native, "plan", public_view)

    def stage(self, *_args, **_kwargs):
        raise PermissionError("YGG_KNOW02_NO_FACTUAL_WRITE_OR_CAUSAL_TRAINING")

    def observe_experience(self, *_args, **_kwargs):
        raise PermissionError("YGG_KNOW02_NO_FACTUAL_WRITE_OR_CAUSAL_TRAINING")
