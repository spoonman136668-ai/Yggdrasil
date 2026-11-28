"""Independent third-action confirmation under adversarial two-label flips."""
import unittest
from evidence_gated_replay import EvidenceGatedReplay
from sequential_regimes import training_phase

class HardenedReplayTests(unittest.TestCase):
    def configured(self):
        agent = EvidenceGatedReplay(feature_positions=2, max_examples=8, min_probe_samples=3)
        training_phase(agent, "A")
        agent.archive()
        training_phase(agent, "B")
        agent.start_probe()
        return agent

    def probe(self, outcomes):
        agent = self.configured()
        for (frame, action), reward in zip(
            ((b"xB-train", 1), (b"yA-train", 1), (b"xB-train", 0)), outcomes
        ):
            agent.observe(frame, [0, 1])
            agent.learn(action, b"terminal", reward, True)
        decision = agent.restore_with_evidence()
        self.assertFalse(agent.probe_active)
        return decision

    def test_clean_three_action_return_restores(self):
        self.assertTrue(self.probe((0, 1, 1)))

    def test_two_flipped_feedback_observations_refused(self):
        # B continues: two manipulated rewards mimic A; third independent
        # action contradicts A. This must not restore the A archive.
        self.assertFalse(self.probe((0, 1, 0)))

    def test_three_action_continuing_regime_refused(self):
        self.assertFalse(self.probe((1, 0, 0)))

    def test_probe_cannot_repeat_same_action_as_confirmation(self):
        agent = self.configured()
        for _ in range(3):
            agent.observe(b"xB-train", [1])
            agent.learn(1, b"terminal", 0, True)
        self.assertFalse(agent.restore_with_evidence())

if __name__ == "__main__":
    unittest.main()
