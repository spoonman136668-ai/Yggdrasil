"""Check intervention cost semantics and the evidence gate."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

RESEARCH = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/CAUSAL-AMALGAM"
SPEC = spec_from_file_location("amalgam_outcome_probe_for_tests", RESEARCH / "outcome_probe.py")
PROBE = module_from_spec(SPEC)
SPEC.loader.exec_module(PROBE)


def predictor(context, action):
    return 0.85 if action else 0.15


class OutcomeProbeTests(unittest.TestCase):
    def test_propose_uses_outcome_entropy_and_keeps_one_in_four_support(self):
        probe = PROBE.OutcomeProbe(predictor, active=True)
        actions = []
        for _ in range(4):
            action, pair, _ = probe.choose(0)
            actions.append(action)
            probe.observe(0, action, pair, 0)
        self.assertEqual(actions, [1, 1, 1, 0])

    def test_posterior_cannot_declare_at_insufficient_sample_size(self):
        probe = PROBE.OutcomeProbe(predictor, active=True)
        for _ in range(5):
            action, pair, _ = probe.choose(0)
            probe.observe(0, action, pair, 0)
        self.assertGreater(probe.mass[1], 0.9)
        self.assertIsNone(probe.declaration(posterior=0.9, min_observations=8, max_bits_per_outcome=1))

    def test_calibration_rejects_both_poor_hypotheses(self):
        probe = PROBE.OutcomeProbe(predictor, active=True)
        for _ in range(12):
            action, pair, _ = probe.choose(0)
            probe.observe(0, action, pair, int(action == 0))
        self.assertGreater(probe.mass[1], 0.9)
        self.assertIsNone(probe.declaration(posterior=0.9, min_observations=8, max_bits_per_outcome=0.6))
