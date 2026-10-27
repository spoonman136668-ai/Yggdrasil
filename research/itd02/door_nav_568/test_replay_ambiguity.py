"""Ambiguous archive evidence must not silently choose an arbitrary winner."""
import unittest
from evidence_gated_replay import EvidenceGatedReplay
from sequential_regimes import training_phase

class ReplayAmbiguityTests(unittest.TestCase):
    def test_equally_supported_archives_refuse_restoration(self):
        agent = EvidenceGatedReplay(feature_positions=2, max_examples=8, max_archives=2)
        training_phase(agent, "A")
        agent.archive()
        first = agent.archives[0]
        # Distinct legitimate history that agrees on both discriminating
        # feedback observations but differs on an unrelated public record.
        second = first[:-1] + ((b"qQ-train", 0, 1),)
        agent.archives.append(second)
        training_phase(agent, "B")
        agent.start_probe()
        for frame, action, reward in ((b"xB-train", 1, 0), (b"yA-train", 1, 1)):
            agent.observe(frame, [0, 1])
            agent.learn(action, b"terminal", reward, True)
        self.assertFalse(agent.restore_with_evidence(), "ambiguous archive winner")
        self.assertFalse(agent.probe_active)

if __name__ == "__main__":
    unittest.main()
