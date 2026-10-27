"""Regression: rejected evidence cannot be recycled into a later replay."""
import unittest
from evidence_gated_replay import EvidenceGatedReplay
from sequential_regimes import training_phase

class ReplayProbeFreshness(unittest.TestCase):
    def test_rejected_probe_requires_two_new_observations(self):
        agent = EvidenceGatedReplay(feature_positions=2, max_examples=8)
        training_phase(agent, "A")
        agent.archive()
        training_phase(agent, "B")
        self.assertFalse(agent.restore_with_evidence())
        self.assertEqual(len(agent.feedback), 0)
        agent.observe(b"xB-train", [0, 1])
        agent.learn(1, b"terminal", 0, True)
        self.assertFalse(agent.restore_with_evidence())
        agent.observe(b"yA-train", [0, 1])
        agent.learn(1, b"terminal", 1, True)
        self.assertTrue(agent.restore_with_evidence() is False)
        self.assertEqual(len(agent.feedback), 0)

if __name__ == "__main__":
    unittest.main()
