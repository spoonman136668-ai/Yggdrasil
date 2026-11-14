"""WSP106 tests: synthetic source only, not protected or historical source."""
from array import array
from hashlib import sha256
from io import BytesIO
import math
from pathlib import Path
import sys
import time
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from distmult_dev import (
    BATCH, DIM, EPOCHS, WSP104_COUNTS,
    batch_update, check_budget, exact_candidate_rankings,
    id_maps, model_trial, rank_score, read_retained_and_candidates,
    sample_groups, group_digest, heldout, parse_triple,
)


def tiny_graph():
    masked = []
    for subject in range(1, 200):
        d = group_digest(subject, 7)
        if heldout(d):
            masked.append((int.from_bytes(d[8:16], "big"), subject))
    masked.sort()
    a, b = [v for _, v in masked[:2]]
    lines = [
        f"Q{a}\tP7\tQ101\n",
        f"Q{a}\tP7\tQ102\n",
        f"Q{b}\tP7\tQ200\n",
    ]
    # Non-hidden facts; exact WSP103 grouping prevents answer leakage.
    for i in range(1000, 1040):
        if not heldout(group_digest(i, 7)):
            lines.append(f"Q{i}\tP7\tQ101\n")
    for i in range(2000, 2030):
        if not heldout(group_digest(i, 7)):
            lines.append(f"Q{i}\tP7\tQ200\n")
    for subject in (a, b):
        p = next(p for p in range(8, 64) if not heldout(group_digest(subject, p)))
        lines.append(f"Q{subject}\tP{p}\tQ999\n")
    raw = "".join(lines).encode("ascii")
    relations = len({parse_triple(r)[1] for r in raw.splitlines(keepends=True)})
    return raw, relations


class TestDistMultDev(unittest.TestCase):
    def test_full_entity_mapping_unhashed_and_deterministic(self):
        triples = array("I", [7, 3, 11, 7, 4, 17, 31, 3, 11])
        entities, relations, subjects, rp, objects = id_maps(triples)
        self.assertEqual(entities.tolist(), [7, 11, 17, 31])
        self.assertEqual(relations.tolist(), [3, 4])
        self.assertEqual(subjects.tolist(), [0, 0, 3])
        self.assertEqual(objects.tolist(), [1, 2, 1])
        self.assertEqual(rp.tolist(), [0, 1, 0])

    def test_sgd_negative_logistic_step_learns_synthetic_relation(self):
        E = np.array([[0.8, 0.2], [0.7, 0.4], [-0.6, -0.4]],
                     dtype=np.float32)
        R = np.array([[1.0, 1.0]], dtype=np.float32)
        s = np.array([0], dtype=np.int32)
        p = np.array([0], dtype=np.int32)
        o = np.array([1], dtype=np.int32)
        neg = np.array([2], dtype=np.int32)
        initial = float((E[0] * R[0] * (E[1] - E[2])).sum())
        losses = [batch_update(E, R, s, p, o, neg, lr=np.float32(0.05))
                  for _ in range(24)]
        final = float((E[0] * R[0] * (E[1] - E[2])).sum())
        self.assertGreater(final, initial)
        self.assertLess(losses[-1], losses[0])
        self.assertTrue(all(math.isfinite(v) for v in losses))

    def test_query_group_mask_witness_and_baseline_replay(self):
        data, relations = tiny_graph()
        start = time.monotonic()
        kwargs = dict(rows=len(data.splitlines()),
                      byte_count=len(data), sha=sha256(data).hexdigest(),
                      predicates=relations, query_count=2,
                      start=start, wall=20)
        selected, hidden, _ = sample_groups(lambda: BytesIO(data), **kwargs)
        self.assertEqual(len(selected), 2)
        self.assertEqual(hidden, 3)
        edges, heavy, witness = read_retained_and_candidates(
            lambda: BytesIO(data), selected, hidden, expected_retained=len(data.splitlines())-3,
            expected_sample=None, capacity=4, start=start, wall=20)
        self.assertEqual(len(edges)//3, len(data.splitlines())-3)
        self.assertEqual(len(witness), 64)
        baseline, receipt, counts = exact_candidate_rankings(
            edges, heavy, selected,
            expected_receipt=None, expected_counts=None,
            expected_recount=len(edges)//3, start=start, wall=20)
        self.assertEqual(len(receipt), 64)
        self.assertGreaterEqual(counts[1], counts[0])
        self.assertGreaterEqual(counts[3], counts[2])
        self.assertEqual(len(baseline[7]), 2)

    def test_synthetic_trial_replays_identically_and_trains_all_facts(self):
        data, relations = tiny_graph()
        selected, hidden, _ = sample_groups(lambda: BytesIO(data),
            rows=len(data.splitlines()), byte_count=len(data),
            sha=sha256(data).hexdigest(), predicates=relations,
            query_count=2, wall=20)
        edges, heavy, _ = read_retained_and_candidates(
            lambda: BytesIO(data), selected, hidden,
            expected_retained=len(data.splitlines()) - 3,
            expected_sample=None, capacity=4, wall=20)
        base, _, _ = exact_candidate_rankings(
            edges, heavy, selected, expected_receipt=None,
            expected_counts=None, expected_recount=len(edges)//3, wall=20)
        a = model_trial(edges, selected, base,
                        epochs=2, batch=8, dimension=4, seed=41061, wall=20)
        b = model_trial(edges, selected, base,
                        epochs=2, batch=8, dimension=4, seed=41061, wall=20)
        self.assertEqual(a["retained_edges_trained_per_epoch"], len(edges)//3)
        self.assertEqual(a["epochs_completed"], 2)
        self.assertEqual(a["mean_train_logistic_loss_each_epoch"],
                         b["mean_train_logistic_loss_each_epoch"])
        self.assertEqual(a["trained"], b["trained"])
        self.assertTrue(all(math.isfinite(v)
                            for v in a["mean_train_logistic_loss_each_epoch"]))

    def test_source_drift_and_hidden_leakage_fail_closed(self):
        data, relations = tiny_graph()
        with self.assertRaises(ValueError):
            sample_groups(lambda: BytesIO(data),
                rows=len(data.splitlines()),
                byte_count=len(data), sha="0"*64,
                predicates=relations, query_count=2)
        with self.assertRaises(ValueError):
            sample_groups(lambda: BytesIO(data),
                rows=len(data.splitlines()), byte_count=len(data),
                sha=sha256(data).hexdigest(),
                predicates=relations+1, query_count=2)
        with self.assertRaises(ValueError):
            sample_groups(lambda: BytesIO(data),
                rows=1, byte_count=len(data),
                sha=sha256(data).hexdigest(),
                predicates=relations, query_count=2)
        selected, hidden, _ = sample_groups(lambda: BytesIO(data),
            rows=len(data.splitlines()), byte_count=len(data),
            sha=sha256(data).hexdigest(), predicates=relations, query_count=2)
        with self.assertRaises(ValueError):
            read_retained_and_candidates(
                lambda: BytesIO(data), selected, hidden,
                expected_retained=len(data.splitlines()) - 3,
                expected_sample="0"*64, capacity=4)

    def test_out_of_vocabulary_candidate_never_receives_positive_embedding(self):
        E = np.array([[1, 0], [1, 0]], dtype=np.float32)
        R = np.array([[1, 1]], dtype=np.float32)
        one = rank_score(E, R, np.array([1, 2], dtype=np.uint32),
                         np.array([7], dtype=np.uint32),
                         {(1, 7): {99}},
                         {7: [2, 99]})
        self.assertEqual(one["hits1"], 0)
        self.assertEqual(one["hits10"], 1)
        self.assertEqual(one["unknown_candidate_occurrences"], 1)

    def test_budget_is_enforced(self):
        with self.assertRaises(TimeoutError):
            check_budget(time.monotonic()-4, 1)
        with self.assertRaises(MemoryError):
            check_budget(time.monotonic(), 50, rss_limit=-1)


if __name__ == "__main__":
    unittest.main()
