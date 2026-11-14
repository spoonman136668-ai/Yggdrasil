"""WSP104 fake-data tests; no official test/validation or real archive reads."""
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from frequency_controls import train_candidates, group_digest, heldout, parse_triple


def fake_train(with_second_answer_retained=True):
    eligible = []
    for s in range(1, 250):
        digest = group_digest(s, 7)
        if heldout(digest):
            eligible.append((int.from_bytes(digest[8:16], "big"), s))
    eligible.sort()
    a, b = [s for _, s in eligible[:2]]
    lines = [
        f"Q{a}\tP7\tQ100\n",
        f"Q{a}\tP7\tQ101\n",
        f"Q{b}\tP7\tQ200\n",
    ]
    for obj, n in ((100, 5), (200, 3 if with_second_answer_retained else 0), (300, 1)):
        n_done = 0
        for s in range(500, 1500):
            if n_done >= n:
                break
            if heldout(group_digest(s, 7)):
                continue
            lines.append(f"Q{s}\tP7\tQ{obj}\n")
            n_done += 1
    for key in (a, b):
        p = next(p for p in range(8, 100) if not heldout(group_digest(key, p)))
        lines.append(f"Q{key}\tP{p}\tQ999\n")
    raw = "".join(lines).encode("ascii")
    relation_count = len({parse_triple(row)[1] for row in raw.splitlines(keepends=True)})
    return raw, relation_count


def run(raw, relations, **kw):
    return train_candidates(
        lambda: BytesIO(raw),
        expected_rows=len(raw.splitlines()),
        expected_bytes=len(raw),
        expected_sha=kw.get("source_sha", sha256(raw).hexdigest()),
        expected_relations=kw.get("relations", relations),
        expected_answers_sha=None,
        query_count=2,
        capacity=4,
        max_wall_seconds=20,
    )


class TestTrainOnlyFrequency(unittest.TestCase):
    def test_heldout_query_results_are_not_learning_features(self):
        raw, relations = fake_train()
        result = run(raw, relations)
        self.assertEqual(result["selected_query_groups"], 2)
        self.assertEqual(result["selected_group_direct_lookup_hits"], 0)
        self.assertEqual(result["masked_train_rows"], 3)
        self.assertEqual(result["retained_train_rows"], len(raw.splitlines()) - 3)
        self.assertEqual(result["metrics"]["frequency"]["hits1"], 1)
        self.assertEqual(result["metrics"]["frequency"]["hits10"], 2)
        self.assertEqual(result["metrics"]["reverse"]["hits1"], 0)
        self.assertEqual(result["metrics"]["reverse"]["hits10"], 2)
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["fully_trained_kg_neural_baseline"])
        self.assertFalse(result["official_validation_test_read"])

    def test_source_and_prediction_receipts_are_deterministic(self):
        raw, relations = fake_train()
        a = run(raw, relations)
        b = run(raw, relations)
        for field in ("frozen_query_answer_sha256", "source_train_sha256",
                      "score_receipt_sha256", "metrics", "retained_train_rows"):
            self.assertEqual(a[field], b[field])

    def test_heldout_answers_do_not_get_guaranteed_hits(self):
        full, rel = fake_train()
        no_second, rel2 = fake_train(with_second_answer_retained=False)
        full_result = run(full, rel)
        weak_result = run(no_second, rel2)
        self.assertLess(weak_result["metrics"]["frequency"]["hits10"],
                        full_result["metrics"]["frequency"]["hits10"])

    def test_integrity_and_capacity_bounds_fail_closed(self):
        raw, rel = fake_train()
        with self.assertRaises(ValueError):
            run(raw, rel, source_sha="0" * 64)
        with self.assertRaises(ValueError):
            run(raw, rel + 1)
        with self.assertRaises(ValueError):
            train_candidates(lambda: BytesIO(raw),
                             expected_rows=len(raw.splitlines()), expected_bytes=len(raw),
                             expected_sha=sha256(raw).hexdigest(), expected_relations=rel,
                             query_count=2, capacity=65, expected_answers_sha=None)

    def test_malformed_rows_are_not_admitted(self):
        raw, rel = fake_train()
        bad = raw.replace(raw.splitlines(keepends=True)[0], b"Q0\tP7\tQ100\n", 1)
        with self.assertRaises(ValueError):
            run(bad, rel)


if __name__ == "__main__":
    unittest.main()
