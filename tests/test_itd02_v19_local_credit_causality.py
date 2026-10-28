"""Source-only V19 independent causal eligibility witness tests."""
import json
import unittest

from research.itd02_v19_local_credit_causality_audit import (
    FLAT, first, jacobian, reconstructed_prediction,
)
from yggdrasil.itd02_v18_intermediate_plasticity_dev import (
    ACTION_SITES, CHANNELS, INITIAL_GAIN, IntermediatePlasticRingDev,
)
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS


class V19CreditCausalityTests(unittest.TestCase):
    def test_zero_output_head_sensitivity_but_nonoutput_gain_mutates(self):
        for cue, actual_first, second in (
            ("LRV", "GoForward", "Backup"),
            ("docked_MRV", "Backup", "TurnAround"),
        ):
            model = IntermediatePlasticRingDev()
            first(model, cue, actual_first)
            initial_prediction, jac = jacobian(
                model, cue, actual_first, second)
            self.assertEqual(initial_prediction, 0.0)
            self.assertTrue(all(abs(x) < FLAT for row in jac for x in row))
            before = [list(row) for row in model.gains]
            model.accept_second(second, 2.0)
            self.assertTrue(any(
                abs(model.gains[i][j] - before[i][j]) > 1e-10
                for i in range(8) if i not in ACTION_SITES
                for j in range(CHANNELS)))
            self.assertEqual(model.learned_updates, 1)

    def test_actual_selected_identity_sensitivity_and_no_head_spoof(self):
        model = IntermediatePlasticRingDev()
        with self.assertRaises(ValueError):
            model.accept_first("Backup")
        model.start_observation("MRV")
        with self.assertRaises(ValueError):
            model.accept_first("Backup", reward=2)
        model.accept_first("TurnAround")
        before = model.checkpoint()
        with self.assertRaises(TypeError):
            model.accept_second("Backup", 1.0, hidden_law="private")
        self.assertEqual(before, model.checkpoint())
        with self.assertRaises(ValueError):
            model.accept_second("Backup", float("nan"))
        self.assertEqual(before, model.checkpoint())
        heads = [list(row) for row in model.heads]
        model.accept_second("GoForward", -1.0)
        self.assertEqual(model.heads[0], heads[0])
        self.assertEqual(model.heads[2], heads[2])
        self.assertNotEqual(model.heads[1], heads[1])
        raw = model.checkpoint()
        self.assertEqual(IntermediatePlasticRingDev.restore(raw).checkpoint(), raw)
        corrupted = json.loads(raw)
        corrupted["body"]["gains"][0][0] = 99
        with self.assertRaises(ValueError):
            IntermediatePlasticRingDev.restore(json.dumps(corrupted).encode())

    def test_source_exact_postfit_prediction_reconstruction(self):
        model = IntermediatePlasticRingDev()
        first(model, "LRV", "Backup")
        model.accept_second("GoForward", 1.5, learning=True)
        first(model, "MRV", "GoForward")
        expected, grad = jacobian(model, "MRV", "GoForward", "TurnAround")
        self.assertAlmostEqual(expected, model.scores()[0], places=12)
        self.assertEqual(len(grad), 8)
        self.assertTrue(all(len(row) == CHANNELS for row in grad))
        self.assertAlmostEqual(reconstructed_prediction(
            model, "MRV", "GoForward", "TurnAround", model.gains),
            model.scores()[ACTIONS.index("TurnAround")], places=12)


if __name__ == "__main__":
    unittest.main()
