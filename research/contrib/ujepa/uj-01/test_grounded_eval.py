"""Fabricated DEV fixtures only; no protected dataset."""
import hashlib
import json
import unittest

from grounded_eval import load_corpus, evaluate, probabilities, training_pairs


def fixture():
    return [dict(id=str(i), group=str(i), domain=d, split=s,
                 context="context " + str(i), options=["a", "b"], answer=i % 2)
            for i, (s, d) in enumerate(
                [("train", "language"), ("train", "math"),
                 ("validation", "language"), ("test", "math")])]


def load(rows):
    raw = ("\n".join(json.dumps(r) for r in rows) + "\n").encode()
    return load_corpus(raw, hashlib.sha256(raw).hexdigest())


class GroundedTests(unittest.TestCase):
    def test_partitions_and_training_only(self):
        p = load(fixture())
        self.assertEqual([len(p[s]) for s in ("train", "validation", "test")], [2, 1, 1])
        self.assertEqual(training_pairs(p), ((b"context 0", b"a"), (b"context 1", b"b")))

    def test_digest_failure(self):
        with self.assertRaises(ValueError):
            load_corpus(b"not json", "0" * 64)

    def test_leakage_rejected(self):
        for key in ("group", "context", "id"):
            rows = fixture()
            rows[-1][key] = rows[0][key]
            with self.assertRaises(ValueError):
                load(rows)

    def test_bad_records(self):
        for key, value in (("answer", True), ("answer", 2), ("options", ["a", "a"]),
                           ("context", "x"*257), ("split", "unknown")):
            rows = fixture()
            rows[0][key] = value
            with self.assertRaises(ValueError):
                load(rows)

    def test_scoring_and_blind_interface(self):
        rows = load(fixture())["test"]
        seen = []
        def score(ctx, opts):
            seen.append((ctx, opts))
            return [0, 0]
        m = evaluate(rows, score)
        self.assertEqual(seen, [(b"context 3", (b"a", b"b"))])
        self.assertEqual(m["all"], {"n": 1, "accuracy": 0.5, "brier": 0.25})
        self.assertEqual(m["math"], m["all"])
        self.assertEqual(evaluate(rows, lambda c,o: [-1000, 1000])["all"]["accuracy"], 1)
        self.assertEqual(evaluate(rows, lambda c,o: [1000, -1000])["all"]["brier"], 1)

    def test_invalid_scores(self):
        for values in ([0], [0, float("nan")], [float("inf"), 0]):
            with self.assertRaises(ValueError):
                probabilities(values)
        with self.assertRaises(ValueError):
            evaluate(load(fixture())["test"], lambda c,o: [0, 0, 0])


if __name__ == "__main__":
    unittest.main()
