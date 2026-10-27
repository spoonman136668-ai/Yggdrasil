"""Evidence-gated native replay tests: restoration versus no-evidence control."""
import unittest
from evidence_gated_replay import EvidenceGatedReplay
from sequential_regimes import training_phase, evaluate

class EvidenceReplayTests(unittest.TestCase):
    def test_reacquires_archived_regime_after_discriminating_feedback(self):
        agent = EvidenceGatedReplay(feature_positions=2, max_examples=8, max_archives=2)
        training_phase(agent, "A")
        agent.archive()
        training_phase(agent, "B")
        self.assertEqual(evaluate(agent, "B"), 4)
        self.assertEqual(evaluate(agent, "A"), 2)
        # Opposite rewards under A versus B at matched public state/actions.
        for frame, action, reward in ((b"xB-train", 1, 0), (b"yA-train", 1, 1)):
            agent.observe(frame, [0, 1])
            agent.learn(action, b"terminal", reward, True)
        self.assertTrue(agent.restore_with_evidence())
        self.assertEqual(evaluate(agent, "A"), 4)
        self.assertLessEqual(len(agent.active.examples), 8)

    def test_no_replay_without_sufficient_feedback(self):
        agent = EvidenceGatedReplay(feature_positions=2, max_examples=8)
        training_phase(agent, "A")
        agent.archive()
        training_phase(agent, "B")
        self.assertFalse(agent.restore_with_evidence())
        agent.observe(b"xB-train", [0, 1])
        agent.learn(1, b"terminal", 0, True)
        self.assertFalse(agent.restore_with_evidence())

    def test_archive_cap(self):
        agent = EvidenceGatedReplay(feature_positions=2, max_examples=8, max_archives=1)
        training_phase(agent, "A")
        agent.archive()
        training_phase(agent, "B")
        agent.archive()
        self.assertEqual(len(agent.archives), 1)

if __name__ == "__main__":
    unittest.main()
