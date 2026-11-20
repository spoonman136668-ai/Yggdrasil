"""KNOW04: explicit, source-pinned *development-only* Q/P/Q -> public view seam.

A typed factual triple cannot prove a causal mechanism or define a binary
native state. A separate predeclared fixture mapping is required. Output is a
shadow-only planner readout; learned weights, causal history and model authority
are untouched. There is deliberately no native training/write API.
"""
from __future__ import annotations

import hashlib
import json
import re

from typed_readout_bridge import TypedFactualReadoutBridge

SCHEMA = "yggdrasil.know04.explicit-public-view-projection.v1"
SOURCE_MODE = "engineering_fixture_only"
SOURCE_KIND = "explicit-synthetic-qpq-to-native-view-mapping"
MAX_BYTES = 16 * 1024
MAX_ENTRIES = 8
HEX = re.compile(r"[0-9a-f]{64}\Z")


def _require(condition, reason):
    if not condition:
        raise ValueError("YGG_KNOW04_" + reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(doc):
    return json.dumps(doc, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def _unique(pairs):
    obj = {}
    for key, value in pairs:
        _require(key not in obj, "DUPLICATE_KEY")
        obj[key] = value
    return obj


def _triple(item):
    _require(type(item) is list and len(item) == 3 and
             all(type(n) is int and 0 < n <= 0xFFFFFFFF for n in item),
             "INVALID_QPQ")
    return tuple(item)


def _paired_views(raw):
    _require(type(raw) is list and len(raw) == 2 and
             all(type(view) is list and len(view) == 2 and
                 all(type(bit) is int and bit in (0, 1) for bit in view)
                 for view in raw), "INVALID_PUBLIC_VIEWS")
    _require(raw[0][0] == raw[1][0], "INCONSISTENT_PAIRED_STATE")
    return tuple(tuple(view) for view in raw)


def make_fixture_manifest(joint_sha, facts_sha, entries):
    """Synthetic-only helper; the emitted digest does not authenticate reality."""
    raw = canonical({
        "schema": SCHEMA, "source_mode": SOURCE_MODE,
        "source_kind": SOURCE_KIND,
        "amalgam_checkpoint_sha256": joint_sha,
        "factual_checkpoint_sha256": facts_sha,
        "bindings": entries, "native_accepted": False,
        "scientific_pass": False,
    })
    return raw, digest(raw)


class ExplicitPublicViewProjection:
    """No mapping guesses, no causal admission, no accepted-model mutation."""
    __slots__ = ("_bridge", "_raw", "_sha", "_bindings", "_ambiguous_plan_views")

    def __init__(self, bridge, raw, expected_sha256):
        _require(isinstance(bridge, TypedFactualReadoutBridge),
                 "ORIGINAL_TYPED_BRIDGE_REQUIRED")
        _require(type(raw) is bytes and 0 < len(raw) <= MAX_BYTES,
                 "MANIFEST_BYTES")
        _require(type(expected_sha256) is str and HEX.fullmatch(expected_sha256)
                 and digest(raw) == expected_sha256, "EXTERNAL_MANIFEST_PIN")
        try:
            doc = json.loads(raw.decode("ascii"), object_pairs_hook=_unique,
                             parse_constant=lambda _: _require(False, "NONFINITE"))
        except (ValueError, UnicodeError, TypeError) as exc:
            if isinstance(exc, ValueError) and str(exc).startswith("YGG_KNOW04_"):
                raise
            raise ValueError("YGG_KNOW04_INVALID_MANIFEST_JSON") from exc
        _require(type(doc) is dict and canonical(doc) == raw,
                 "NONCANONICAL_MANIFEST")
        _require(set(doc) == {
            "schema", "source_mode", "source_kind", "amalgam_checkpoint_sha256",
            "factual_checkpoint_sha256", "bindings", "native_accepted",
            "scientific_pass"} and doc["schema"] == SCHEMA and
            doc["source_mode"] == SOURCE_MODE and
            doc["source_kind"] == SOURCE_KIND and
            doc["native_accepted"] is False and
            doc["scientific_pass"] is False,
            "UNQUALIFIED_OR_UNSUPPORTED_MAPPING")
        _require(doc["amalgam_checkpoint_sha256"] == bridge._native_sha and
                 doc["factual_checkpoint_sha256"] == bridge._facts_sha,
                 "BOUND_CHECKPOINT_MISMATCH")
        rows = doc["bindings"]
        _require(type(rows) is list and 0 <= len(rows) <= MAX_ENTRIES,
                 "MAPPING_CAPACITY")
        mappings, previous = {}, None
        used_views = set()
        plan_view_counts = {}
        for entry in rows:
            _require(type(entry) is list and len(entry) == 2,
                     "INVALID_ENTRY")
            key = _triple(entry[0])
            views = _paired_views(entry[1])
            _require(previous is None or previous < key,
                     "NONUNIQUE_OR_UNSORTED_BINDINGS")
            _require(views not in used_views, "AMBIGUOUS_VIEW_ALIAS")
            mappings[key] = views
            used_views.add(views)
            plan_view_counts[views[0]] = plan_view_counts.get(views[0], 0) + 1
            previous = key
        bridge._check_snapshots()
        self._bridge = bridge
        self._raw = raw
        self._sha = expected_sha256
        self._bindings = mappings
        self._ambiguous_plan_views = frozenset(
            view for view, count in plan_view_counts.items() if count > 1)

    def checkpoint(self):
        """Return the immutable synthetic mapping only, not a learner checkpoint."""
        _require(digest(self._raw) == self._sha, "MANIFEST_PIN_DRIFT")
        self._bridge._check_snapshots()
        return self._raw

    def query(self, subject, predicate, obj):
        """Explicitly abstain when either stored fact or public mapping is absent."""
        self.checkpoint()
        key = _triple([subject, predicate, obj])
        observed = self._bridge.fact(*key)
        _require(observed.get("amalgam_checkpoint_sha256") ==
                 self._bridge._native_sha and
                 observed.get("factual_checkpoint_sha256") ==
                 self._bridge._facts_sha and
                 observed.get("causal_observation_admitted") is False and
                 observed.get("native_model_knowledge_updated") is False and
                 observed.get("scientific_pass") is False,
                 "FACTUAL_PROVENANCE_CONTRACT")
        kind = observed.get("evidence_kind")
        _require(kind in ("HISTORICAL_STORED_QPQ",
                          "SYNTHETIC_ENGINEERING_QPQ", "UNSUPPORTED_ABSTAIN"),
                 "INVALID_EVIDENCE_CLASS")
        pair = self._bindings.get(key)
        self.checkpoint()
        # Factual membership and usable shadow plan inputs are separate.
        # Pair-unique mappings can still alias the actual plan(view) input.
        # Never export an ambiguous mapped view to downstream readout clients.
        ambiguous = pair is not None and pair[0] in self._ambiguous_plan_views
        eligible = (pair is not None and kind != "UNSUPPORTED_ABSTAIN"
                    and not ambiguous)
        return {
            "schema": SCHEMA, "classification": (
                "SYNTHETIC_VIEW_PROPOSAL_ONLY" if eligible else
                "ABSTAIN_UNKNOWN_FACT" if kind == "UNSUPPORTED_ABSTAIN" else
                "ABSTAIN_AMBIGUOUS_NATIVE_PLAN_VIEW" if ambiguous else
                "ABSTAIN_NO_EXPLICIT_VIEW_MAP"),
            "source_fact_kind": kind,
            "qpq": list(key),
            "paired_public_views": [list(v) for v in pair] if eligible else None,
            "fact_checkpoint_sha256": self._bridge._facts_sha,
            "amalgam_checkpoint_sha256": self._bridge._native_sha,
            "mapping_sha256": self._sha,
            "real_semantic_grounding": False,
            "witnessed_causal_consequence": False,
            "native_training_performed": False,
            "scientific_pass": False,
            "native_accepted": False,
        }

    def shadow_plan(self, subject, predicate, obj):
        """Call the original native planner *only* through an explicit view.

        This is not an authorized policy change. No unverified Q/P/Q semantics
        are silently inferred, and absence of a mapping suppresses the call.
        """
        proposal = self.query(subject, predicate, obj)
        if proposal["paired_public_views"] is None:
            return {**proposal, "native_plan_called": False, "shadow_plan": None}
        public_view = tuple(proposal["paired_public_views"][0])
        if public_view in self._ambiguous_plan_views:
            self.checkpoint()
            return {**proposal, "classification": "ABSTAIN_AMBIGUOUS_NATIVE_PLAN_VIEW",
                    "native_plan_called": False, "shadow_plan": None,
                    "policy_activation": False, "causal_observation_admitted": False}
        result = self._bridge.independent_native_plan(public_view)
        self.checkpoint()
        return {**proposal, "native_plan_called": True, "shadow_plan": result,
                "policy_activation": False, "causal_observation_admitted": False}

    def observe_experience(self, *_a, **_k):
        raise PermissionError("YGG_KNOW04_NO_CAUSAL_WRITE_OR_TRAINING")

    def stage(self, *_a, **_k):
        raise PermissionError("YGG_KNOW04_NO_FACTUAL_WRITE_OR_TRAINING")
