"""Synthetic-only WSP107 unit controls; no historical protected data is read."""
from array import array
from hashlib import sha256
from io import BytesIO
import math
from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "WSP-106"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_distmult_dev import tiny_graph
from distmult_dev import (
    sample_groups, read_retained_and_candidates, exact_candidate_rankings,
    parse_triple,
)
from projected_transe import (
    project_rows, transe_batch, score_transe, fit_projected_transe,
    LR, MARGIN, SEED,
)


def fixture():
    raw, relations = tiny_graph()
    selected, hidden, _ = sample_groups(
        lambda: BytesIO(raw), rows=len(raw.splitlines()),
        byte_count=len(raw), sha=sha256(raw).hexdigest(), predicates=relations,
        query_count=2, wall=20)
    edges, heavy, witness = read_retained_and_candidates(
        lambda: BytesIO(raw), selected, hidden,
        expected_retained=len(raw.splitlines()) - hidden,
        expected_sample=None, capacity=4, wall=20)
    candidates, receipt, counts = exact_candidate_rankings(
        edges, heavy, selected, expected_recount=len(edges)//3,
        expected_receipt=None, expected_counts=None, wall=20)
    return raw, selected, edges, candidates, witness, receipt, counts


class TestIndependentProjectedTransE(unittest.TestCase):
    def test_synthetic_positive_margin_decreases_and_projection_is_bounded(self):
        E = np.array([[0.50, 0.20], [0.40, 0.10], [-0.80, -0.10]],
                     dtype=np.float32)
        P = np.array([[0.10, 0.10]], dtype=np.float32)
        s = np.array([0], dtype=np.int32)
        p = np.array([0], dtype=np.int32)
        o = np.array([1], dtype=np.int32)
        n = np.array([2], dtype=np.int32)
        losses = []
        for _ in range(25):
            loss, active = transe_batch(E, P, s, p, o, n, lr=np.float32(0.02))
            losses.append(loss)
            self.assertLessEqual(np.linalg.norm(E, axis=1).max(), 1.000001)
            self.assertLessEqual(np.linalg.norm(P, axis=1).max(), 1.000001)
        self.assertLess(losses[-1], losses[0])
        self.assertTrue(all(math.isfinite(v) for v in losses))

    def test_projection_checks_numerical_integrity(self):
        matrix = np.array([[3.0, 4.0], [0.0, 0.0], [0.5, 0.5]],
                          dtype=np.float32)
        project_rows(matrix)
        self.assertTrue(np.allclose(matrix[0], np.array([0.6, 0.8])))
        self.assertTrue(np.allclose(matrix[1], np.array([0.0, 0.0])))
        self.assertLessEqual(np.linalg.norm(matrix, axis=1).max(), 1.000001)
        matrix[1, 0] = np.nan
        with self.assertRaises(FloatingPointError):
            project_rows(matrix)

    def test_immutable_mask_and_candidate_provenance(self):
        raw, selected, edges, candidates, witness, receipt, counts = fixture()
        self.assertEqual(len(selected), 2)
        self.assertEqual(len(witness), 64)
        self.assertEqual(len(receipt), 64)
        self.assertEqual(len(edges), (len(raw.splitlines()) - 3) * 3)
        self.assertGreaterEqual(counts[1], counts[0])
        self.assertEqual(set(candidates[7]), {101, 200})

    def test_cold_seed_replay_and_complete_frozen_epochs(self):
        _, selected, edges, candidates, _, _, _ = fixture()
        left = fit_projected_transe(
            edges, selected, candidates, epochs=2, dimension=4,
            batch_size=8, seed=SEED, wall_seconds=20)
        right = fit_projected_transe(
            edges, selected, candidates, epochs=2, dimension=4,
            batch_size=8, seed=SEED, wall_seconds=20)
        for key in ("untrained", "trained", "training_epoch_receipts"):
            if key == "training_epoch_receipts":
                # Elapsed wall time is operational, not determinism criterion.
                L = [{k:v for k,v in x.items() if k!="epoch_wall_seconds"}
                     for x in left[key]]
                R = [{k:v for k,v in x.items() if k!="epoch_wall_seconds"}
                     for x in right[key]]
                self.assertEqual(L, R)
            else:
                self.assertEqual(left[key], right[key])
        self.assertEqual(left["retained_edges_trained_per_epoch"], len(edges)//3)
        self.assertEqual(left["training_epochs_completed"], 2)
        self.assertTrue(left["cold_copy_predictions_identical"])
        self.assertTrue(all(math.isfinite(x["mean_train_hinge_loss"])
                            for x in left["training_epoch_receipts"]))

    def test_translational_scoring_considers_subject_identity(self):
        E = np.array([[0.9,0.0], [0.9,0.0], [-0.9,0.0]],
                     dtype=np.float32)
        P = np.array([[0.0,0.0]], dtype=np.float32)
        ents = np.array([1,2,3],dtype=np.uint32)
        preds = np.array([7],dtype=np.uint32)
        selected = {(1,7):{2}, (3,7):{3}}
        candidates = {7:[2,3]}
        result = score_transe(E,P,ents,preds,selected,candidates)
        self.assertEqual(result["hits1"], 2)
        self.assertEqual(result["hits10"], 2)

    def test_invalid_training_budget_is_rejected(self):
        _, selected, edges, candidates, _, _, _ = fixture()
        with self.assertRaises(ValueError):
            fit_projected_transe(edges, selected, candidates, epochs=0)
        with self.assertRaises(ValueError):
            fit_projected_transe(edges, selected, candidates, dimension=0)
        with self.assertRaises(ValueError):
            fit_projected_transe(edges, selected, candidates, batch_size=0)

    def test_nonfinite_optimizer_input_is_rejected_not_silently_clipped(self):
        E = np.array([[0.0], [float("nan")], [0.2]], dtype=np.float32)
        P = np.array([[0.0]], dtype=np.float32)
        with self.assertRaises(FloatingPointError):
            transe_batch(E, P, np.array([0], np.int32),
                         np.array([0], np.int32),
                         np.array([1], np.int32),
                         np.array([2], np.int32))


if __name__ == "__main__":
    unittest.main()
