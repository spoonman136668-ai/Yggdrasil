"""NKR-10: source-masked real historical P31/P279 relationship transfer.

Engineering / historical-TRAIN development diagnostic ONLY. Full immutable
native factual source is read twice; a deterministic held-out P31 subset is
NEVER supplied to the rule miner or direct-memory query path. This does not
claim an externally independent scientific cohort or a new causal law.

Any proposed source-absent relationship remains an UNVERIFIED HYPOTHESIS.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import struct
import time

from yggdrasil.native_knowledge_activation import (
    PINNED_ROWS, PINNED_PACKED_SHA, PINNED_MANIFEST_SHA,
)
from yggdrasil.native_factual_weights import NativeFactualWeights

P_INSTANCE = 31
P_SUBCLASS = 279
COHORT_MOD = 32
COHORT_BUCKET = 7
HOLDOUT_MOD = 4
TARGET_SALT = 0x9E3779B97F4A7C15
MASK64 = (1 << 64) - 1
MAX_ROWS = 25_000_000
MAX_COHORT = 2_000_000
MAX_CLASSES = 1_000_000
MAX_SUBCLASSES = 4_000_000
MAX_QUERIES = 4096
MAX_SECONDS = 900
MIN_RULE_SUBJECTS = 4
MIN_POSITIVE_QUERIES = 64
TOP_K = 4


def mix64(value):
    """Exact cross-platform SplitMix finalizer, not Python's salted hash()."""
    if type(value) is not int or value < 0:
        raise ValueError("NKR10_HASH_INPUT")
    z = (value + TARGET_SALT) & MASK64
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK64
    return (z ^ (z >> 31)) & MASK64


def subject_selected(subject, *, cohort_mod=COHORT_MOD, bucket=COHORT_BUCKET):
    return mix64(subject) % cohort_mod == bucket


def heldout_fact(subject, obj):
    """Same original triple gets same partition regardless of duplicates."""
    return mix64(subject ^ (obj << 1) ^ TARGET_SALT) % HOLDOUT_MOD == 0


class MaskedTrainingView:
    """Visible P31 statements and permitted P279 edges only.

    Its constructor never accepts held-out labels. No original graph/session
    or raw source handle is retained; unfrozen tests cannot bypass this view.
    """
    __slots__ = ("instances", "subclasses")

    def __init__(self, instances, subclasses):
        self.instances = {s: frozenset(obs) for s, obs in instances.items()}
        self.subclasses = {c: frozenset(obs) for c, obs in subclasses.items()}

    def candidate_counts(self, subject, target_relation=P_INSTANCE):
        if type(subject) is not int or subject <= 0:
            raise ValueError("NKR10_SUBJECT_INVALID")
        if type(target_relation) is not int or target_relation <= 0:
            raise ValueError("NKR10_RELATION_INVALID")
        if target_relation != P_INSTANCE:
            return {}
        result = Counter()
        for cls in self.instances.get(subject, ()):
            for parent in self.subclasses.get(cls, ()):
                result[parent] += 1
        return dict(result)

    def rank(self, subject, *, enabled, target_relation=P_INSTANCE):
        if not enabled:
            return ()
        votes = self.candidate_counts(subject, target_relation)
        return tuple(obj for obj, _ in sorted(
            votes.items(), key=lambda it: (-it[1], it[0]))[:TOP_K])


def _symbolic_top4(instances, subclasses, subject):
    """Independently coded, fully fitted exact symbolic two-hop control."""
    totals = {}
    for cls in sorted(instances.get(subject, ())):
        for parent in sorted(subclasses.get(cls, ())):
            totals[parent] = totals.get(parent, 0) + 1
    if not totals:
        return ()
    order = sorted(totals, key=lambda obj: (-totals[obj], obj))
    return tuple(order[:TOP_K])


def _validate_source(source, *, fixture):
    if fixture:
        if not hasattr(source, "row_at") or not hasattr(source, "__len__"):
            raise ValueError("NKR10_FIXTURE_INTERFACE_INVALID")
    else:
        if not isinstance(source, NativeFactualWeights):
            raise ValueError("NKR10_ORIGINAL_NATIVE_WEIGHTS_REQUIRED")
        meta = source.manifest
        if (len(source) != PINNED_ROWS
                or meta.get("packed_sha256") != PINNED_PACKED_SHA
                or meta.get("records") != PINNED_ROWS
                or meta.get("original_valid_test_read") is not False
                or meta.get("scientific_pass") is not False):
            raise ValueError("NKR10_ORIGINAL_HISTORICAL_SOURCE_DRIFT")
    if not 1 <= len(source) <= MAX_ROWS:
        raise ValueError("NKR10_SOURCE_BUDGET")


def _time_guard(start, rows):
    if rows % 16384 == 0 and time.monotonic() - start > MAX_SECONDS:
        raise TimeoutError("NKR10_FULL_SOURCE_TIME_BUDGET")


def frozen_split(source, *, fixture=False, cohort_mod=COHORT_MOD,
                 bucket=COHORT_BUCKET):
    """Two deterministic source-only passes, with sealed holdouts separate."""
    _validate_source(source, fixture=fixture)
    if (type(cohort_mod) is not int or not 1 <= cohort_mod <= 64
            or type(bucket) is not int or not 0 <= bucket < cohort_mod
            or (not fixture and (cohort_mod, bucket) !=
                (COHORT_MOD, COHORT_BUCKET))):
        raise ValueError("NKR10_SPLIT_NOT_FROZEN")
    start = time.monotonic()
    visible = defaultdict(set)
    sealed = defaultdict(set)
    visible_rows = heldout_rows = selected_rows = 0
    for i in range(len(source)):
        _time_guard(start, i)
        s, p, obj = source.row_at(i)
        if p == P_INSTANCE and subject_selected(
                s, cohort_mod=cohort_mod, bucket=bucket):
            selected_rows += 1
            if selected_rows > MAX_COHORT:
                raise MemoryError("NKR10_COHORT_ROWS_EXCEEDED")
            if heldout_fact(s, obj):
                sealed[s].add(obj)
                heldout_rows += 1
            else:
                visible[s].add(obj)
                visible_rows += 1
    classes = {obj for subjects in visible.values() for obj in subjects}
    if len(classes) > MAX_CLASSES:
        raise MemoryError("NKR10_CLASS_IDS_EXCEEDED")
    subclass = defaultdict(set)
    subclass_rows = 0
    for i in range(len(source)):
        _time_guard(start, len(source) + i)
        s, p, obj = source.row_at(i)
        if p == P_SUBCLASS and s in classes:
            subclass_rows += 1
            if subclass_rows > MAX_SUBCLASSES:
                raise MemoryError("NKR10_SUBCLASS_ROWS_EXCEEDED")
            subclass[s].add(obj)
    # Keep sealed targets physically out of the only object available to the
    # learner. Hidden source labels are handed exclusively to scoring.
    training = MaskedTrainingView(visible, subclass)
    return training, {s: frozenset(obs) for s, obs in sealed.items()}, {
        "original_rows_scanned_per_pass": len(source),
        "source_passes": 2,
        "selected_p31_rows": selected_rows,
        "visible_p31_rows": visible_rows,
        "masked_p31_rows": heldout_rows,
        "visible_p31_subjects": len(visible),
        "source_p31_class_ids": len(classes),
        "visible_p279_rows": subclass_rows,
        "visible_p279_class_ids": len(subclass),
        "source_processing_seconds": time.monotonic() - start,
    }


def evaluate_split(training, sealed, diagnostics, *, fixture=False):
    """Sealed positive labels used ONLY here, after the model is constructed."""
    if not isinstance(training, MaskedTrainingView):
        raise ValueError("NKR10_TRAINING_VIEW_INVALID")
    # Training support is explicit source-visible X-p31-Y, Y-p279-Z,
    # X-p31-Z. Missing direct edges never count as negatives.
    supported_subjects = 0
    for s, objects in training.instances.items():
        if objects and any(x in objects
                           for x in training.candidate_counts(s)):
            supported_subjects += 1
    enabled = supported_subjects >= MIN_RULE_SUBJECTS
    # Frozen first 4096 *eligible* lexicographic masked positives, no
    # selecting solely those that the candidate can recover.
    test_queries = []
    for s in sorted(sealed):
        if s in training.instances:
            for obj in sorted(sealed[s]):
                test_queries.append((s, obj))
                if len(test_queries) >= MAX_QUERIES:
                    break
        if len(test_queries) >= MAX_QUERIES:
            break
    frequency = Counter()
    for objects in training.instances.values():
        frequency.update(objects)
    top_prior = tuple(obj for obj, _ in sorted(
        frequency.items(), key=lambda x: (-x[1], x[0]))[:TOP_K])
    native_hits = symbolic_hits = prior_hits = covered = 0
    for s, hidden_obj in test_queries:
        native = training.rank(s, enabled=enabled)
        symbolic = (_symbolic_top4(training.instances, training.subclasses, s)
                    if enabled else ())
        if native != symbolic:
            raise AssertionError("NKR10_INDEPENDENT_SYMBOLIC_PARITY_FAIL")
        if hidden_obj in training.instances[s]:
            raise AssertionError("NKR10_HELDOUT_FACT_LEAKED_INTO_TRAIN")
        covered += bool(native)
        native_hits += hidden_obj in native
        symbolic_hits += hidden_obj in symbolic
        prior_hits += hidden_obj in top_prior
    n = len(test_queries)
    classification = "HISTORICAL_TRAIN_NO_SIGNAL"
    lift = ((native_hits-prior_hits)/n) if n else 0.0
    if n < MIN_POSITIVE_QUERIES:
        classification = "INSUFFICIENT_ELIGIBLE_MASKED_HISTORICAL_LABELS"
    elif not enabled:
        classification = "INSUFFICIENT_HISTORICAL_COMPOSITION_SUPPORT"
    elif native_hits / n >= 0.10 and lift >= 0.05:
        classification = "HISTORICAL_TRAIN_MASKED_RECOVERY_DEV_POSITIVE"
    else:
        classification = "HISTORICAL_TRAIN_MASKED_RECOVERY_NULL"
    return {
        "schema": "yggdrasil.nkr10.historical-real-fact-masked-transfer-result.v1",
        "classification": classification,
        "development_historical_train_only": not fixture,
        "fixture": fixture,
        "target_relation_p": P_INSTANCE,
        "prespecified_path": [P_INSTANCE, P_SUBCLASS, P_INSTANCE],
        "cohort_mod": COHORT_MOD if not fixture else None,
        "cohort_bucket": COHORT_BUCKET if not fixture else None,
        "holdout_mod": HOLDOUT_MOD,
        "eligible_masked_positive_queries": n,
        "real_training_motif_support_subjects": supported_subjects,
        "rule_activated": enabled,
        "queries_with_nonempty_inference": covered,
        "native_positive_recall_hits_at4": native_hits,
        "symbolic_positive_recall_hits_at4": symbolic_hits,
        "frequency_prior_positive_hits_at4": prior_hits,
        "native_positive_recall_at4": native_hits/n if n else 0.0,
        "symbolic_positive_recall_at4": symbolic_hits/n if n else 0.0,
        "frequency_prior_positive_recall_at4": prior_hits/n if n else 0.0,
        "absolute_lift_over_prior_at4": lift,
        "exact_equal_information_symbolic_parity": True,
        "new_true_world_relations_certified": 0,
        "novel_relation_types_created": 0,
        "scientific_pass": False,
        "native_accepted": False,
        "original_scientific_first_use": False,
        "inferred_facts_admitted": 0,
        "source": diagnostics,
    }
