"""Small focused negative/identity tests (full source regression NOT run here)."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('r15', Path(__file__).with_name('r15_evidence_switch_replay.py'))
r15 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r15)

class TestEvidenceSwitch(unittest.TestCase):
    def test_identical_experts_are_identity_control(self):
        preds, post = r15.step(0.25, (300_000, 400_000), (300_000, 400_000), 1, 0)
        self.assertEqual(preds, (300_000, 400_000))
        self.assertAlmostEqual(post, 0.25 * (31 / 32) + 1 / 64)

    def test_reward_is_conditioned_on_observed_transition(self):
        # State=1 selects the first expert with likelihood 0.8 over 0.2.
        preds, posterior = r15.step(0.5, (800_000, 900_000),
                                     (200_000, 100_000), 1, 1)
        self.assertEqual(preds, (500_000, 740_000))
        self.assertGreater(posterior, .8)

    def test_invalid_evidence_rejected(self):
        with self.assertRaisesRegex(ValueError, 'NONBINARY'):
            r15.step(0.5, (200_000, 500_000), (500_000, 500_000), 0, 2)
        with self.assertRaisesRegex(ValueError, 'BAD_FORECAST'):
            r15.step(0.5, (-1, 500_000), (500_000, 500_000), 0, 1)
        with self.assertRaisesRegex(ValueError, 'IMPOSSIBLE'):
            r15.step(1.0, (0, 500_000), (0, 500_000), 1, 0)

    def test_order_gate(self):
        with self.assertRaisesRegex(ValueError, 'TRACE_ORDER'):
            r15.evaluate_trace([{'stage': 1}] * 72, 0, 'sha',
                                     hazard=1/32, margin=.005, return_bound=.02)

if __name__ == '__main__':
    unittest.main()
