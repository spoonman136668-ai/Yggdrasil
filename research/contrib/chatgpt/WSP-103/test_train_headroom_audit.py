"""Frozen fake-source negative controls for WSP103 train-only headroom audit."""
from io import BytesIO
from hashlib import sha256
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from train_headroom_audit import (
    QUERY_COUNT, audit_streams, group_digest, heldout, parse_triple,
    load_custody_helpers
)


def fixture():
    eligible = []
    for subject in range(1, 300):
        digest = group_digest(subject, 7)
        if heldout(digest):
            eligible.append((int.from_bytes(digest[8:16], "big"), subject))
    eligible.sort()
    if len(eligible) < 3:
        raise AssertionError("fixture insufficient")
    a, b, c = [subject for _, subject in eligible[:3]]
    rows = [
        f"Q{a}\tP7\tQ100\n",
        f"Q{a}\tP7\tQ101\n",
        f"Q{b}\tP7\tQ200\n",
        f"Q{c}\tP7\tQ300\n",
    ]
    # Every supporting edge is retained rather than held out.
    for s in (a, b, c):
        predicate = next(p for p in range(8, 100) if not heldout(group_digest(s, p)))
        rows.append(f"Q{s}\tP{predicate}\tQ900\n")
    for o in (100, 101, 200, 300):
        subject = 400 + o
        predicate = next(p for p in range(8, 100) if not heldout(group_digest(subject, p)))
        rows.append(f"Q{subject}\tP{predicate}\tQ{o}\n")
    source = "".join(rows).encode("ascii")
    predicates = {parse_triple(row)[1] for row in source.splitlines(keepends=True)}
    return source, len(predicates)


def audit(source, relations, *, expected_sha=None):
    return audit_streams(
        lambda: BytesIO(source),
        expected_rows=len(source.splitlines()),
        expected_bytes=len(source),
        expected_sha=expected_sha or sha256(source).hexdigest(),
        expected_relations=relations,
        query_count=2,
        max_wall_seconds=20,
    )


class TrainOnlyHeadroomTests(unittest.TestCase):
    def test_holdout_keeps_all_values_in_one_query_group(self):
        data, relations = fixture()
        result = audit(data, relations)
        self.assertEqual(result["selected_distinct_query_groups"], 2)
        self.assertEqual(result["selected_group_answer_cardinality_histogram"], {1: 1, 2: 1})
        self.assertEqual(result["selected_group_leakage_count"], 0)
        self.assertEqual(result["with_both_endpoint_support"], 2)
        self.assertEqual(result["with_subject_train_support"], 2)
        self.assertEqual(result["with_any_object_train_support"], 2)
        self.assertEqual(result["heldout_source_rows"], 4)
        self.assertEqual(result["retained_train_rows"], len(data.splitlines()) - 4)
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["direct_weight_learner_trained"])
        self.assertFalse(result["trained_conventional_baseline"])

    def test_deterministic_cold_replay_identity(self):
        data, relations = fixture()
        one = audit(data, relations)
        two = audit(data, relations)
        for field in (
            "selected_query_answers_sha256", "source_train_sha256",
            "selected_group_answer_cardinality_histogram",
            "selected_distinct_objects", "heldout_source_rows",
            "with_both_endpoint_support",
        ):
            self.assertEqual(one[field], two[field])

    def test_source_integrity_and_budgets_fail_closed(self):
        data, relations = fixture()
        with self.assertRaises(ValueError):
            audit(data, relations, expected_sha="0" * 64)
        with self.assertRaises(ValueError):
            audit_streams(lambda: BytesIO(data), expected_rows=1,
                          expected_bytes=len(data), expected_sha=sha256(data).hexdigest(),
                          expected_relations=relations, query_count=2)
        with self.assertRaises(ValueError):
            audit_streams(lambda: BytesIO(data), expected_rows=len(data.splitlines()),
                          expected_bytes=len(data), expected_sha=sha256(data).hexdigest(),
                          expected_relations=relations + 1, query_count=2)
        with self.assertRaises(ValueError):
            audit_streams(lambda: BytesIO(data), expected_rows=len(data.splitlines()),
                          expected_bytes=len(data), expected_sha=sha256(data).hexdigest(),
                          expected_relations=relations, query_count=QUERY_COUNT + 1)

    def test_sealed_sibling_custody_import_works_without_network(self):
        download, inspect = load_custody_helpers()
        self.assertTrue(callable(download))
        self.assertTrue(callable(inspect))
        self.assertEqual(download.__module__, "wsp102_source_custody")

    def test_malformed_qids_never_enter_source(self):
        source, relations = fixture()
        for replacement in (b"Q0\tP7\tQ100\n", b"Q01\tP7\tQ100\n",
                            b"Q1\tP0\tQ100\n", b"Q1\tP7\tQ0\n",
                            b"Q1\tP7\tQ100", b"Q1\tP7\tQfoo\n"):
            original = source.splitlines(keepends=True)[0]
            malformed = source.replace(original, replacement, 1)
            with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                audit(malformed, relations)


if __name__ == "__main__":
    unittest.main()
