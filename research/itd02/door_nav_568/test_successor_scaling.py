"""Verify held-out state refusal and bounded public successor observations."""
import unittest
from successor_corroborated_replay import SuccessorCorroboratedReplay
from test_successor_corroborated_replay import fit

class SuccessorScalingTests(unittest.TestCase):
    def test_held_out_successor_cannot_claim_known_causal_effect(self):
        agent = SuccessorCorroboratedReplay()
        fit(agent, "A")
        agent.archive()
        fit(agent, "B")
        agent.start_probe()
        for frame in (b"zA-unseen", b"zB-unseen"):
            agent.observe(frame, [0])
            agent.learn(0, b"A:"+frame, 1, True)
        self.assertFalse(agent.restore_with_corrob())
        self.assertFalse(agent.learner.probe_active)

    def test_capacity_rejects_new_state_without_partial_update(self):
        agent = SuccessorCorroboratedReplay(max_successors=8)
        for i in range(8):
            agent.observe(b"state"+bytes([i]), [0])
            agent.learn(0, b"next", 0, True)
        agent.observe(b"unknown-state", [0])
        with self.assertRaises(ValueError):
            agent.learn(0, b"next", 1, True)
        self.assertEqual(len(agent.current_successors), 8)
        self.assertEqual(len(agent.learner.active.examples), 8)

    def test_memory_across_regimes_and_probe_is_bounded(self):
        agent = SuccessorCorroboratedReplay(max_successors=8)
        for regime in (b"A", b"B"):
            for i in range(8):
                agent.observe(regime+bytes([i]), [0])
                agent.learn(0, regime+b"next", 0, True)
            if regime == b"A":
                agent.archive()
        self.assertEqual(len(agent.archived_successors), 8)
        self.assertEqual(len(agent.current_successors), 8)
        agent.start_probe()
        for i in range(8):
            agent.observe(b"probe"+bytes([i]), [0])
            agent.learn(0, b"next", 0, True)
        agent.observe(b"over-cap", [0])
        with self.assertRaises(ValueError):
            agent.learn(0, b"next", 0, True)
        self.assertEqual(len(agent.probe_successors), 8)

if __name__ == "__main__":
    unittest.main()
