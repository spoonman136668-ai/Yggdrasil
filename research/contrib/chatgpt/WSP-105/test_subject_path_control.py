"""WSP105 fabricated-graph path controls; never access original graph labels."""
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from subject_path_control import (
    MAX_JOIN_UPDATES, SUBJECT_NEIGHBORS, group_digest, heldout,
    parse_triple, selected_masked_groups_and_subject_paths,
)


def make_fixture(*, bridge=True, second_answer=True):
    masked = []
    for s in range(1, 300):
        d = group_digest(s, 7)
        if heldout(d):
            masked.append((int.from_bytes(d[8:16], "big"), s))
    masked.sort()
    a, b = (v for _, v in masked[:2])
    lines = [f"Q{a}\tP7\tQ200\n", f"Q{b}\tP7\tQ100\n"]
    if second_answer:
        lines.append(f"Q{a}\tP7\tQ201\n")

    # Factual frequency: Q100 is the most popular P7 object on retained edges.
    def retained_subjects(count, start):
        out = []
        for s in range(start, start + 1000):
            if not heldout(group_digest(s, 7)):
                out.append(s)
            if len(out) == count:
                return out
        raise AssertionError("not enough retained subject IDs")

    for s in retained_subjects(8, 1000):
        lines.append(f"Q{s}\tP7\tQ100\n")
    for s in retained_subjects(2, 3000):
        lines.append(f"Q{s}\tP7\tQ200\n")

    neighbor = 500000
    r1 = next(p for p in range(8, 100) if not heldout(group_digest(a, p)))
    r2 = next(p for p in range(8, 100) if not heldout(group_digest(neighbor, p)))
    lines.append(f"Q{a}\tP{r1}\tQ{neighbor}\n")
    if bridge:
        lines.append(f"Q{neighbor}\tP{r2}\tQ200\n")

    raw = "".join(lines).encode("ascii")
    relations = len({parse_triple(row)[1] for row in raw.splitlines(keepends=True)})
    return raw, relations


def run_fixture(raw, relations, *, expected_sha=None, **kwargs):
    return selected_masked_groups_and_subject_paths(
        lambda: BytesIO(raw),
        expected_rows=len(raw.splitlines()),
        expected_bytes=len(raw),
        expected_sha=(sha256(raw).hexdigest() if expected_sha is None else expected_sha),
        expected_relations=relations,
        expected_sample_sha=None,
        expected_frequency_sha=None,
        expected_frequency_scores=None,
        query_count=2,
        capacity=4,
        max_subject_neighbors=4,
        max_join_updates=500,
        max_wall_seconds=20,
        **kwargs,
    )


class SubjectPathControlTests(unittest.TestCase):
    def test_retained_path_can_rerank_wrong_relation_popularity(self):
        source, relations = make_fixture()
        result = run_fixture(source, relations)
        self.assertEqual(result["selected_query_groups"], 2)
        self.assertEqual(result["masked_training_rows"], 3)
        self.assertEqual(result["metrics"]["frequency"]["hits1"], 1)
        self.assertEqual(result["metrics"]["path_first"]["hits1"], 2)
        self.assertEqual(result["metrics"]["path_only"]["hits1"], 1)
        self.assertEqual(result["queries_with_any_two_hop_candidate"], 1)
        self.assertEqual(result["path_first_hits10_minus_frequency"], 0)
        self.assertFalse(result["official_validation_test_read"])
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["fully_trained_conventional_embedding_model"])

    def test_removed_bridge_forces_frozen_path_abstention(self):
        source, relations = make_fixture(bridge=False)
        result = run_fixture(source, relations)
        self.assertEqual(result["queries_with_any_two_hop_candidate"], 0)
        self.assertEqual(result["metrics"]["path_only"]["hits10"], 0)
        self.assertEqual(result["metrics"]["path_first"]["hits1"],
                         result["metrics"]["frequency"]["hits1"])
        self.assertEqual(result["metrics"]["path_first"]["hits10"],
                         result["metrics"]["frequency"]["hits10"])

    def test_exact_repeat_matches_all_scientific_receipts(self):
        source, relations = make_fixture()
        left = run_fixture(source, relations)
        right = run_fixture(source, relations)
        for key in (
            "source_sha256", "selected_query_answer_sha256",
            "frequency_score_receipt_sha256", "path_score_receipt_sha256",
            "path_join_updates", "metrics",
        ):
            self.assertEqual(left[key], right[key])

    def test_provenance_and_limits_fail_closed(self):
        source, relations = make_fixture()
        with self.assertRaises(ValueError):
            run_fixture(source, relations, expected_sha="0" * 64)
        with self.assertRaises(ValueError):
            run_fixture(source, relations + 1)
        with self.assertRaises(ValueError):
            selected_masked_groups_and_subject_paths(
                lambda: BytesIO(source), max_subject_neighbors=SUBJECT_NEIGHBORS + 1)
        with self.assertRaises(ValueError):
            selected_masked_groups_and_subject_paths(
                lambda: BytesIO(source), max_join_updates=MAX_JOIN_UPDATES + 1)

    def test_invalid_source_line_never_admitted(self):
        source, relations = make_fixture()
        first = source.splitlines(keepends=True)[0]
        for bad in (b"Q0\tP7\tQ200\n", b"Q01\tP7\tQ200\n",
                    b"Q1\tP0\tQ200\n", b"Q1\tP7\tQ0\n",
                    b"Q1\tP7\tQbad\n", b"Q1\tP7\tQ200"):
            with self.subTest(row=bad), self.assertRaises(ValueError):
                run_fixture(source.replace(first, bad, 1), relations)


if __name__ == "__main__":
    unittest.main()
