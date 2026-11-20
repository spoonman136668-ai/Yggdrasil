"""MH-01 source-only deterministic guardrails; science threshold is a separate report."""
import json
import sys
import pathlib
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from study import (CHECKPOINTS, FIT, HELD, VALID, Genome, MetaColony,
                   LogisticControl, assess, data, genomes, lesion, run)


class MH01Tests(unittest.TestCase):
    def test_frozen_grid_32_and_disjoint_cohorts(self):
        self.assertEqual(len(genomes()), 32)
        self.assertEqual(len(set(FIT + VALID + HELD)), 7)
        self.assertEqual(CHECKPOINTS, (0, 8, 32, 64, 96))
        self.assertEqual(genomes()[0], Genome(.5, 0., .005, 0.))

    def test_feedback_is_validated_before_any_mutation(self):
        model = MetaColony(Genome(1., 0., .02, .03))
        original = model.checkpoint()
        sensors = (True, False, True, False)
        for feedback in [(True, 1), (1, 2), (True, True)]:
            with self.assertRaises(ValueError):
                model.learn_completed_public_feedback("A", sensors, *feedback)
        with self.assertRaises(ValueError):
            model.learn_completed_public_feedback("A", (True, 0, True, False), True, 2)
        self.assertEqual(original, model.checkpoint())
        model.learn_completed_public_feedback("A", sensors, True, 2)
        self.assertNotEqual(original, model.checkpoint())
        self.assertEqual(model.feedback_updates, 1)
        self.assertEqual(sum(c.updates for c in model.cells["A"]), 4)
        self.assertEqual(sum(c.updates for c in model.cells["B"]), 0)

    def test_damage_actually_removes_three_pairs(self):
        model = MetaColony(Genome(1., 0., .02, .03))
        for _ in range(9):
            model.learn_completed_public_feedback("A", (True,) * 4, True, 2)
            model.learn_completed_public_feedback("B", (True,) * 4, True, 2)
        before = [(c.fast, c.slow) for side in ("A", "B") for c in model.cells[side]]
        self.assertTrue(all(x[0] for x in before))
        lesion(model)
        for side, i in (("A", 0), ("A", 2), ("B", 1)):
            self.assertEqual((model.cells[side][i].fast, model.cells[side][i].slow), (0, 0.0))
        self.assertEqual(sum(c.fast != 0 for side in ("A", "B")
                             for c in model.cells[side]), 5)

    def test_genome_checkpoint_exact_and_tamper_rejected(self):
        model = MetaColony(Genome(2., .01, .005, 0.))
        for i in range(20):
            model.learn_completed_public_feedback("B",
                (bool(i & 1), bool(i & 2), bool(i & 4), bool(i & 8)),
                bool(i & 2), 2)
        saved = model.checkpoint()
        cold = MetaColony.restore(saved)
        self.assertEqual(cold.genome, model.genome)
        self.assertEqual(cold.checkpoint(), saved)
        self.assertLessEqual(len(saved), 32768)
        for i in range(16):
            xs = tuple(bool(i & 1 << j) for j in range(4))
            self.assertEqual(model.predict("B", xs), cold.predict("B", xs))
        corrupted = json.loads(saved)
        corrupted["payload"]["genome"]["fast_gain"] = 4.0
        with self.assertRaises(ValueError):
            MetaColony.restore(json.dumps(corrupted).encode())

    def test_conventional_control_matches_public_update_rights(self):
        p = LogisticControl()
        x = (True, False, False, True)
        with self.assertRaises(ValueError):
            p.learn_completed_public_feedback("A", x, True, 1)
        self.assertEqual(p.feedback_updates, 0)
        p.learn_completed_public_feedback("A", x, True, 2)
        self.assertEqual(p.feedback_updates, 1)
        self.assertEqual(p.weights["B"], [0.0] * 4)

    def test_deterministic_fresh_dev_fixture(self):
        g = Genome(1., 0., .02, .03)
        self.assertEqual(assess(MetaColony(g), data(211)),
                         assess(MetaColony(g), data(211)))

    def test_report_preserves_controls_and_negative_outcomes(self):
        r = run()
        self.assertEqual(r["genome_count"], 32)
        self.assertEqual(len(r["fit_search"]), 32)
        self.assertEqual(len(r["held"]["evolved"]), 3)
        self.assertEqual(len(r["held"]["r7_original"]), 3)
        self.assertEqual(len(r["held"]["online_logistic"]), 3)
        self.assertEqual(len(r["held"]["flipped_outcome_negative"]), 3)
        self.assertFalse(r["scientific_first_use"])
        self.assertFalse(r["reward_free_lifetime_hebbian"])
        self.assertIn(r["development_mechanism"],
                      ("DEV_MECHANISM_GO_PENDING_COST", "SCIENTIFIC_DEV_NO_GO"))
        self.assertEqual([a["feedback_updates"] for a in r["held"]["evolved"]],
                         [672] * 3)
        self.assertEqual(run()["winner"], r["winner"])


if __name__ == "__main__":
    unittest.main()
