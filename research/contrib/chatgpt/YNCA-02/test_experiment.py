"""YNCA-02 focused, synthetic-only tests; no protected data or model owner calls."""
import unittest
import experiment as e


class FailureDetectorTests(unittest.TestCase):
    def test_disjoint_seeds(self):
        spans = [set(range(*v)) for v in e.RANGES.values()]
        self.assertTrue(all(spans[i].isdisjoint(spans[j]) for i in range(3) for j in range(i + 1, 3)))

    def test_deterministic_world(self):
        self.assertEqual(e.world(100001, 'train'), e.world(100001, 'train'))

    def test_interventions_are_separate(self):
        _, observed, interventions = e.world(100001, 'train')
        self.assertIn(len(observed), (90, 110, 120, 140))
        self.assertIn(len(interventions), (20, 24, 28, 48))
        self.assertEqual(set(x for x, y in interventions), {0, 1})

    def test_expert_scores_bounded(self):
        _, observed, interventions = e.world(100002, 'train')
        scores = e.experts(observed, interventions)
        self.assertEqual(len(scores), 3)
        self.assertTrue(all(0 <= p <= 1 for p in scores))

    def test_risk_does_not_read_label(self):
        rows = list(e.cases('train'))[:64]
        model = e.fit(rows)
        seed, _, key, confidence, features = rows[0]
        p0 = e.risk(model, (seed, 0, key, confidence, features))
        p1 = e.risk(model, (seed, 1, key, confidence, features))
        self.assertEqual(p0, p1)

    def test_failure_scores_bounded(self):
        rows = list(e.cases('train'))[:64]
        model = e.fit(rows)
        for name, prob in e.risk(model, rows[0]).items():
            self.assertLessEqual(prob, 1, name)
            self.assertGreaterEqual(prob, 0, name)

    def test_selection_risk(self):
        self.assertEqual(e.selection_risk([0, 0, 1, 1, 1], [0, .1, .2, .3, .4]), .5)

    def test_auc_orientation(self):
        self.assertEqual(e.auc([0, 1, 0, 1], [.1, .9, .2, .8]), 1)
        self.assertEqual(e.auc([0, 1, 0, 1], [.9, .1, .8, .2]), 0)


if __name__ == '__main__':
    unittest.main()
