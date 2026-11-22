"""NKR-09: bounded endogenous two-hop relation rules with explicit microfeedback.

This is native non-token INTEGER evidence learning, on an isolated synthetic
candidate. No transformer, oracle, absent-edge negatives or real source
authentication. A matched exact symbolic control is expected to tie.
"""
from __future__ import annotations

from collections import defaultdict
import hmac
import re

from yggdrasil.native_cumulative_facts import (
    CumulativeNativeFacts, _parse_checkpoint, _pinned, _doc, _reference,
    _triple, PINNED_MANIFEST_SHA, canonical, digest,
)

CHECKPOINT_SCHEMA = "yggdrasil.nkr09.rule-hypothesis-checkpoint.v1"
FEEDBACK_SCHEMA = "yggdrasil.nkr09.public-feedback-bundle.v1"
MAX_PATHS = 250_000
MAX_RULES = 512
MAX_FEEDBACK = 32
MAX_RULES_PER_QUERY = 64
MAX_HYPOTHESES = 256
FEEDBACK_WEIGHT = 4
MIN_SUPPORT = 6


def _relation(value):
    if type(value) is not int or not 1 <= value <= 0xFFFFFFFF:
        raise ValueError("NKR09_INVALID_RELATION_ID")
    return value


def _subject(value):
    return _relation(value)


def _mine(evidence):
    """Induce template identities from *observed* Q/P/Q edges, not seeded rules.

    Every candidate requires explicit witnessed X-p3-Z and observed
    X-p1-Y, Y-p2-Z in the source-provided (synthetic) training evidence.
    Absence of any edge is not a negative label. Count unique subjects.
    """
    edges = set(evidence)
    outgoing = defaultdict(list)
    direct = defaultdict(set)
    for s, p, o in sorted(edges):
        outgoing[s].append((p, o))
        direct[(s, o)].add(p)
    subjects = defaultdict(set)
    paths = 0
    for s, p1, mid in sorted(edges):
        for p2, obj in outgoing.get(mid, ()):
            paths += 1
            if paths > MAX_PATHS:
                raise ValueError("NKR09_PATH_BUDGET_EXCEEDED")
            for p3 in direct.get((s, obj), ()):
                if p3 in (p1, p2):
                    continue
                subjects[(p3, p1, p2)].add(s)
                if len(subjects) > MAX_RULES:
                    raise ValueError("NKR09_RULE_BUDGET_EXCEEDED")
    return {key: len(vals) for key, vals in sorted(subjects.items())
            if len(vals) >= MIN_SUPPORT}


def _checkpoint(source_sha, rules):
    serial = [[*key, count] for key, count in sorted(rules.items())]
    return canonical({
        "schema": CHECKPOINT_SCHEMA,
        "evidence_checkpoint_sha256": source_sha,
        "rules": serial,
        "feedback": [],
        "feedback_sources": [],
        "mode": "engineering_fixture_only",
        "source_authenticity": "SHA_PINS_BYTES_NOT_REAL_PUBLIC_FEEDBACK",
        "scientific_pass": False,
        "native_admission": False,
    })


class NativeRelationDiscovery:
    """Induced rule pool + bounded immutable public-label microfeedback.

    All outputs are unverified hypotheses. No outcome is added to the
    underlying NKR08 fact ledger or actual Yggdrasil action counts.
    """
    __slots__ = ("facts", "_rules", "_feedback", "_sources", "_raw")

    def __init__(self, facts, checkpoint=None, *, checkpoint_sha256=None):
        if not isinstance(facts, CumulativeNativeFacts):
            raise ValueError("NKR09_CUMULATIVE_FACTS_REQUIRED")
        source = _parse_checkpoint(facts.checkpoint(), facts.checkpoint_sha256)
        evidence = {_triple(item[1]) for item in source["evidence"]}
        rules = _mine(evidence)
        raw = _checkpoint(facts.checkpoint_sha256, rules) if checkpoint is None else checkpoint
        expected = digest(raw) if checkpoint is None else checkpoint_sha256
        _pinned(raw, expected, "NKR09_CHECKPOINT")
        doc = _doc(raw, limit=131072, error="NKR09_CHECKPOINT")
        if (set(doc) != {"schema", "evidence_checkpoint_sha256", "rules",
                         "feedback", "feedback_sources", "mode",
                         "source_authenticity", "scientific_pass", "native_admission"}
                or doc["schema"] != CHECKPOINT_SCHEMA
                or doc["evidence_checkpoint_sha256"] != facts.checkpoint_sha256
                or doc["mode"] != "engineering_fixture_only"
                or doc["source_authenticity"] != "SHA_PINS_BYTES_NOT_REAL_PUBLIC_FEEDBACK"
                or doc["scientific_pass"] is not False
                or doc["native_admission"] is not False
                or doc["rules"] != [[*key, score] for key, score in sorted(rules.items())]):
            raise ValueError("NKR09_CHECKPOINT_SOURCE_OR_RULE_DRIFT")
        feedback = doc["feedback"]
        sources = doc["feedback_sources"]
        if (type(feedback) is not list or len(feedback) > MAX_FEEDBACK
                or type(sources) is not list or len(sources) > MAX_FEEDBACK):
            raise ValueError("NKR09_FEEDBACK_CAPACITY")
        seen_refs = set()
        seen_queries = set()
        for item in feedback:
            if type(item) is not list or len(item) != 4:
                raise ValueError("NKR09_FEEDBACK_ROW_FORMAT")
            s, p3, obj, ref = item
            _subject(s)
            _relation(p3)
            _subject(obj)
            _reference(ref)
            if ref in seen_refs or (s, p3) in seen_queries:
                raise ValueError("NKR09_DUPLICATE_FEEDBACK_OR_QUERY")
            seen_refs.add(ref)
            seen_queries.add((s, p3))
        if feedback != sorted(feedback, key=lambda x: x[3]):
            raise ValueError("NKR09_FEEDBACK_ORDER")
        source_ids = set()
        for entry in sources:
            if (type(entry) is not list or len(entry) != 2
                    or type(entry[1]) is not str
                    or re.fullmatch(r"[0-9a-f]{64}", entry[1]) is None):
                raise ValueError("NKR09_FEEDBACK_SOURCE_ENTRY")
            _reference(entry[0])
            if entry[0] in source_ids:
                raise ValueError("NKR09_FEEDBACK_SOURCE_REBOUND")
            source_ids.add(entry[0])
        if sources != sorted(sources):
            raise ValueError("NKR09_FEEDBACK_SOURCE_ORDER")
        self.facts = facts
        self._rules = rules
        self._feedback = tuple(tuple(item) for item in feedback)
        self._sources = {k: sha for k, sha in sources}
        self._raw = raw
        # Restored checkpoints must still contain only attainable, unverified
        # predictions. No concealed direct ground-truth edge may be present.
        for s, p, obj, ref in self._feedback:
            if self.facts.fact(s, p, obj)["witnessed"]:
                raise ValueError("NKR09_FEEDBACK_ALREADY_IN_FACTS")
            if obj not in self._candidates(s, p):
                raise ValueError("NKR09_FEEDBACK_NOT_PATH_SUPPORTED")

    @property
    def checkpoint_sha256(self):
        return digest(self._raw)

    def checkpoint(self):
        return self._raw

    def rules(self):
        return [
            {"target_relation": p3, "first_relation": p1,
             "second_relation": p2, "training_support": n,
             "classification": "TRAINING_COMPOSITION_SUPPORTED_NOT_CERTIFIED"}
            for (p3, p1, p2), n in sorted(self._rules.items())]

    def _candidates(self, subject, target_relation, *, max_intermediates=16,
                    max_candidates=64):
        _subject(subject)
        _relation(target_relation)
        applicable = [(key, score) for key, score in self._rules.items()
                      if key[0] == target_relation]
        if len(applicable) > MAX_RULES_PER_QUERY:
            raise ValueError("NKR09_QUERY_RULE_BUDGET")
        out = defaultdict(set)
        for (p3, p1, p2), _ in applicable:
            for obj in self.facts.hypothesize(
                    subject, p1, p2,
                    max_intermediates=max_intermediates,
                    max_candidates=max_candidates)["objects"]:
                out[obj].add((p3, p1, p2))
                if len(out) > MAX_HYPOTHESES:
                    raise ValueError("NKR09_HYPOTHESES_EXCEEDED")
        return out

    def _scores(self, subject, target_relation, *,
                max_intermediates=16, max_candidates=64):
        support = self._candidates(subject, target_relation,
                                   max_intermediates=max_intermediates,
                                   max_candidates=max_candidates)
        totals = defaultdict(lambda: [0, 0])
        for fb_s, fb_p, observed, _ in self._feedback:
            if fb_p != target_relation:
                continue
            for obj, keys in self._candidates(fb_s, fb_p).items():
                for key in keys:
                    totals[key][0 if observed == obj else 1] += 1
        scored = []
        for obj, keys in support.items():
            # Max rule strength, not a vote inflated by unrelated paths.
            rank = max(self._rules[key]
                       + FEEDBACK_WEIGHT * (totals[key][0]-totals[key][1])
                       for key in keys)
            scored.append((obj, rank, sorted(keys)))
        scored.sort(key=lambda entry: (-entry[1], entry[0]))
        return scored

    def predict(self, subject, target_relation):
        subject = _subject(subject)
        target_relation = _relation(target_relation)
        if self.facts.objects(subject, target_relation, limit=1)["objects"]:
            return {"classification": "ALREADY_OBSERVED_NOT_EVALUABLE",
                    "proposals": [], "verified_new_knowledge": False,
                    "native_accepted": False}
        hypotheses = self._scores(subject, target_relation)
        return {
            "classification": (
                "UNVERIFIED_ADAPTIVE_RELATION_HYPOTHESES" if hypotheses
                else "UNKNOWN_ABSTAIN"),
            "proposals": [
                {"object_q": obj, "integer_score": score,
                 "rule_templates": [list(k) for k in keys]}
                for obj, score, keys in hypotheses],
            "source_evidence_checkpoint_sha256": self.facts.checkpoint_sha256,
            "rule_checkpoint_sha256": self.checkpoint_sha256,
            "source_mode": "engineering_fixture_only",
            "verified_new_knowledge": False,
            "native_accepted": False,
            "can_write_causal_consequence": False,
        }

    def stage_feedback(self, raw, expected_sha256):
        """Immutable microfeedback update, never self-promote inferred claims."""
        _pinned(raw, expected_sha256, "NKR09_FEEDBACK_BUNDLE")
        data = _doc(raw, limit=32768, error="NKR09_FEEDBACK_BUNDLE")
        if (set(data) != {"schema", "source_id", "source_mode",
                          "source_kind", "records"}
                or data["schema"] != FEEDBACK_SCHEMA
                or data["source_kind"] != "public_target_outcome"
                or data["source_mode"] != "engineering_fixture_only"):
            raise PermissionError("NKR09_FEEDBACK_SOURCE_UNQUALIFIED")
        ident = _reference(data["source_id"])
        if ident in self._sources:
            if not hmac.compare_digest(self._sources[ident], expected_sha256):
                raise ValueError("NKR09_FEEDBACK_SOURCE_REBOUND")
            return self, {"classification": "DUPLICATE_FEEDBACK_BUNDLE_NO_EFFECT",
                           "checkpoint_sha256": self.checkpoint_sha256,
                           "new_feedback": 0, "scientific_pass": False}
        rows = data["records"]
        if type(rows) is not list or not 1 <= len(rows) <= MAX_FEEDBACK:
            raise ValueError("NKR09_FEEDBACK_RECORD_LIMIT")
        if len(rows) + len(self._feedback) > MAX_FEEDBACK:
            raise ValueError("NKR09_FEEDBACK_CAPACITY_EXCEEDED")
        old_refs = {rec[3] for rec in self._feedback}
        old_queries = {(rec[0], rec[1]) for rec in self._feedback}
        new = []
        for item in rows:
            if type(item) is not list or len(item) != 4:
                raise ValueError("NKR09_FEEDBACK_RECORD_SHAPE")
            s, p, obj = item[:3]
            s, p, obj = _subject(s), _relation(p), _subject(obj)
            ref = _reference(item[3])
            if ref in old_refs or (s, p) in old_queries:
                raise ValueError("NKR09_FEEDBACK_REF_OR_QUERY_REPLAY")
            if self.facts.fact(s, p, obj)["witnessed"]:
                raise ValueError("NKR09_FEEDBACK_ALREADY_OBSERVED")
            candidates = self._candidates(s, p)
            if obj not in candidates:
                raise ValueError("NKR09_FEEDBACK_UNSUPPORTED_TARGET")
            new.append([s, p, obj, ref])
            old_refs.add(ref)
            old_queries.add((s, p))
        if new != sorted(new, key=lambda item: item[3]):
            raise ValueError("NKR09_FEEDBACK_SOURCE_REF_ORDER")
        doc = _doc(self._raw, limit=131072, error="NKR09_CHECKPOINT")
        doc["feedback"] = sorted(doc["feedback"] + new, key=lambda item: item[3])
        doc["feedback_sources"] = sorted(
            doc["feedback_sources"] + [[ident, expected_sha256]])
        successor = canonical(doc)
        candidate = NativeRelationDiscovery(self.facts, successor,
                                           checkpoint_sha256=digest(successor))
        return candidate, {
            "classification": "FIXTURE_FEEDBACK_CANDIDATE_NOT_ADMITTED",
            "new_feedback": len(new),
            "rules": len(self._rules),
            "checkpoint_sha256": candidate.checkpoint_sha256,
            "scientific_pass": False,
            "native_accepted": False,
            "source_authenticity": "UNVERIFIED_FIXTURE",
        }
